# ---- setup: data, windows, event metric, models, training + logging helpers (run this first) ----
import re, time, datetime
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch
import torch.nn as nn

dev = torch.device("cpu")     # these models are tiny: on this machine the CPU is ~4x faster than MPS (checked)
DATA = Path("original")
LOG_CSV = "experiments_anomaly.csv"     # every trained model appends rows here (in this repo)
IMU = ["ACC_x_RMS", "ACC_y_RMS", "ACC_z_RMS", "MAG_x_RMS", "MAG_y_RMS", "MAG_z_RMS"]
PAPER11 = ["GPS_alt", "GPS_speed", "GPS_num_sats", "ACC_x_RMS", "ACC_y_RMS", "ACC_z_RMS", "ACC_samples",
           "MAG_x_RMS", "MAG_y_RMS", "MAG_z_RMS", "MAG_samples"]        # everything except time, lat, lon (the paper's NO-GPS set)
FEATURES = {"imu6": IMU, "paper11": PAPER11}

def parse_ts(s):
    """The files mix 'YYYY-MM-DD hh:mm:ss', 'DD-MM-YY hh:mm' and '20DD-03-21 hh:mm:ss' (= DD March 2021)."""
    s = s.strip()
    if m := re.fullmatch(r"(\d\d)-(\d\d)-(\d\d) (\d{1,2}:\d\d(?::\d\d)?)", s):
        return pd.Timestamp(f"20{m[3]}-{m[2]}-{m[1]} {m[4]}")
    if m := re.fullmatch(r"20(\d\d)-03-21 (.*)", s):
        return pd.Timestamp(f"2021-03-{m[1]} {m[2]}")
    return pd.Timestamp(s)

def load(name):
    d = pd.read_csv(DATA / name)
    d["t"] = d.timestamp.map(parse_ts)
    # rows the authors' loader refuses to use: no GPS fix (lat = lon = 0), negative altitude, oversampled interval
    d["bad"] = ((d.GPS_lat == 0) & (d.GPS_lon == 0)) | (d.GPS_alt < 0) | (d.MAG_samples > 10000)
    return d

train, test = load("training.csv"), load("test.csv")
ANOM = pd.DatetimeIndex([parse_ts(l) for l in (DATA / "anomalies.timestamps").read_text().splitlines() if l.strip()])
print(f"train {len(train)} rows ({train.bad.sum()} unusable) | test {len(test)} rows ({test.bad.sum()} unusable) | {len(ANOM)} labelled anomalies")

def make_windows(d, cols, L):
    """All windows of L consecutive file rows, exactly as the authors' SWDataset: dropped if one row is unusable
    or if the window spans more than 1 hour (or time goes backwards). Returns X (n, L, F), start times, end times."""
    X, t, bad = d[cols].to_numpy(float), d.t.to_numpy(), d.bad.to_numpy()
    i = np.arange(len(d) - L + 1)
    nbad = np.concatenate([[0], np.cumsum(bad)])
    span = (t[i + L - 1] - t[i]) / np.timedelta64(1, "s")
    ok = (nbad[i + L] - nbad[i] == 0) & (span >= 0) & (span <= 3600)
    i = i[ok]
    W = np.lib.stride_tricks.sliding_window_view(X, (L, X.shape[1]))[:, 0][i]
    return W, t[i], t[i + L - 1]

def match_index(st, et):
    """Index of the labelled anomaly inside [start - 1 min, end + 1 min], like the authors' verify.py (-1 if none)."""
    s = st.floor("min"); s = s - pd.Timedelta("1min") if s.minute > 0 else s
    e = et.floor("min") + pd.Timedelta("59s"); e = e + pd.Timedelta("1min") if et.minute < 59 else e
    hit = np.flatnonzero((ANOM >= s) & (ANOM <= e))
    return int(hit[0]) if len(hit) else -1

def event_scores(flags, st, et):
    """Authors' precision/recall: TP = labelled anomalies hit, FP = flagged windows that hit nothing
    (a run of consecutive flagged windows counts once), recall = TP / number of labelled anomalies."""
    hit = np.zeros(len(ANOM), bool); fp, prev = 0, False
    for f, s, e in zip(flags, st, et):
        if f:
            k = match_index(pd.Timestamp(s), pd.Timestamp(e))
            if k >= 0: hit[k] = True
            elif not prev: fp += 1
        prev = f
    tp = int(hit.sum())
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / len(ANOM)
    return dict(precision=p, recall=r, f1=2 * p * r / (p + r) if p + r else 0.0, tp=tp, fp=fp)

# ---- models (hand-written) ----
class DenseAE(nn.Module):
    """The paper's autoencoder: 1, 3 or 5 hidden ReLU layers (n/2 | n/2,n/4,n/2 | 2n/3,n/2,n/4,n/2,2n/3), Glorot init."""
    def __init__(self, n, hidden_layers=1):
        super().__init__()
        h = {1: [n // 2], 3: [n // 2, n // 4, n // 2], 5: [2 * n // 3, n // 2, n // 4, n // 2, 2 * n // 3]}[hidden_layers]
        sizes, layers = [n] + h, []
        for a, b in zip(sizes[:-1], sizes[1:]):
            layers += [nn.Linear(a, b), nn.ReLU()]
        self.net = nn.Sequential(*layers, nn.Linear(sizes[-1], n))
        for m in self.net:
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight); nn.init.zeros_(m.bias)
    def forward(self, x):
        return self.net(x)

class SeqAE(nn.Module):
    """Sequence autoencoder: encoder RNN -> latent vector -> decoder RNN rebuilds the whole window. cell = 'gru' or 'lstm'."""
    def __init__(self, n, hidden=16, latent=8, cell="gru"):
        super().__init__()
        rnn = {"gru": nn.GRU, "lstm": nn.LSTM}[cell]
        self.cell = cell
        self.enc, self.to_z = rnn(n, hidden, batch_first=True), nn.Linear(hidden, latent)
        self.from_z, self.dec, self.out = nn.Linear(latent, hidden), rnn(hidden, hidden, batch_first=True), nn.Linear(hidden, n)
    def forward(self, x):
        _, h = self.enc(x)
        h = h[0] if self.cell == "lstm" else h                       # LSTM returns (h, c)
        z = self.to_z(h[-1])                                          # the window squeezed into `latent` numbers
        y, _ = self.dec(self.from_z(z).unsqueeze(1).repeat(1, x.shape[1], 1))
        return self.out(y)

def fit(model, X, epochs=100, batch_size=16, lr=1e-3, patience=10, seed=0):
    """Adam on MSE, early stopping on the training loss (patience 10) like the authors' Keras code. Returns (history, seconds)."""
    X = torch.as_tensor(X, dtype=torch.float32, device=dev)
    opt, hist, best, wait, t0 = torch.optim.Adam(model.parameters(), lr=lr), [], np.inf, 0, time.time()
    g = torch.Generator().manual_seed(seed)
    for ep in range(epochs):
        model.train(); total = 0.0
        for b in torch.randperm(len(X), generator=g).split(batch_size):
            loss = ((model(X[b]) - X[b]) ** 2).mean()
            opt.zero_grad(); loss.backward(); opt.step()
            total += loss.item() * len(b)
        hist.append(total / len(X))
        if hist[-1] < best: best, wait = hist[-1], 0
        else:
            wait += 1
            if wait >= patience: break
    return hist, time.time() - t0

@torch.no_grad()
def window_scores(model, X):
    """Reconstruction error (mean squared error over the whole window) of every window."""
    model.eval(); X = torch.as_tensor(X, dtype=torch.float32, device=dev)
    return torch.cat([((model(b) - b) ** 2).mean(dim=tuple(range(1, X.ndim))) for b in X.split(2048)]).cpu().numpy()

# the paper's text says "maximum training error", but the authors' code (BaseAD.compute_training_scores, mse_thr=0.05) takes the 95th percentile
THRESHOLDS = {"q95": lambda s: np.quantile(s, 0.95), "q99": lambda s: np.quantile(s, 0.99), "max": lambda s: s.max()}
SCORES = {}      # name -> (test window end times, test errors, {threshold name: value}) kept for the plots

def run(name, model_kind, features="imu6", L=1, seed=0, thresholds=("q95", "q99", "max"), **kw):
    """Train one model on the training windows, score the test windows, log one CSV row per (threshold, matching)."""
    torch.manual_seed(seed); np.random.seed(seed)
    cols = FEATURES[features]
    Wtr, _, _ = make_windows(train, cols, L)
    mu, sd = Wtr.reshape(-1, len(cols)).mean(0), Wtr.reshape(-1, len(cols)).std(0)      # z-score with the TRAINING statistics
    Wtr = (Wtr - mu) / sd
    Wte, st, et = make_windows(test, cols, L); Wte = (Wte - mu) / sd
    if model_kind == "dense":
        model, Wtr, Wte = DenseAE(len(cols), kw.get("hidden_layers", 1)).to(dev), Wtr[:, 0], Wte[:, 0]       # L = 1: one row per sample
    else:
        model = SeqAE(len(cols), kw.get("hidden", 16), kw.get("latent", 8), model_kind).to(dev)
    hist, sec = fit(model, Wtr, epochs=kw.get("epochs", 100), batch_size=kw.get("batch_size", 16), lr=kw.get("lr", 1e-3), seed=seed)
    s_tr, s_te = window_scores(model, Wtr), window_scores(model, Wte)
    thr = {k: THRESHOLDS[k](s_tr) for k in thresholds}
    SCORES[name] = (et, s_te, thr)
    params = sum(p.numel() for p in model.parameters())
    for tname, tval in thr.items():
        for match in (["window", "end"] if L > 1 else ["window"]):           # 'end' = only the last row of the window counts
            res = event_scores(s_te > tval, st if match == "window" else et, et)
            log_run(name, model_kind, features, L, tname, match, seed, params, len(hist), hist[-1], sec, res, kw)
    return model, hist

def log_run(name, kind, features, L, tname, match, seed, params, epochs, train_loss, sec, res, kw):
    row = dict(time=f"{datetime.datetime.now():%Y-%m-%d %H:%M}", name=name, model=kind, features=features, window=L,
               hidden_layers=kw.get("hidden_layers") if kind == "dense" else None,
               hidden=kw.get("hidden", 16) if kind != "dense" else None, latent=kw.get("latent", 8) if kind != "dense" else None,
               threshold=tname, match=match, seed=seed, batch_size=kw.get("batch_size", 16), lr=kw.get("lr", 1e-3),
               params=params, epochs=epochs, train_loss=round(train_loss, 4), precision=round(res["precision"], 3),
               recall=round(res["recall"], 3), f1=round(res["f1"], 3), tp=res["tp"], fp=res["fp"], sec=round(sec, 1), notes="")
    pd.DataFrame([row]).to_csv(LOG_CSV, mode="a", header=not Path(LOG_CSV).exists(), index=False)
    print(f"{name:34s} thr={tname:4s} match={match:6s}  P={res['precision']:.3f} R={res['recall']:.3f} F1={res['f1']:.3f} (TP {res['tp']}, FP {res['fp']})")

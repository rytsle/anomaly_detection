# Two checks that answer "do we need windows / a recurrent model?" and "does the dirty training data hurt?"
#  A) same rows, same labels: single-row AE vs dense AE on a flattened window vs GRU AE (AUROC / AP on row labels)
#  B) retrain the GRU AE without training windows that contain a gravity-axis switch and compare
# Run from anomaly_detection/:  uv run python deep_dive/context_check.py | tee deep_dive/context_check_output.txt
from sklearn.metrics import roc_auc_score, average_precision_score
exec(open("slides/_setup_cell_copy.py").read())
SEEDS = (0, 1, 2)

def windows_idx(d, cols, L):
    """Like make_windows but also returns the file index of the last row of every window."""
    W, st, et = make_windows(d, cols, L)
    X, t, bad = d[cols].to_numpy(float), d.t.to_numpy(), d.bad.to_numpy()
    i = np.arange(len(d) - L + 1); nbad = np.concatenate([[0], np.cumsum(bad)])
    span = (t[i + L - 1] - t[i]) / np.timedelta64(1, "s")
    ok = (nbad[i + L] - nbad[i] == 0) & (span >= 0) & (span <= 3600)
    return W, i[ok] + L - 1, i[ok]

def train_score(kind, feats, L, seed, drop_flip_windows=False):
    torch.manual_seed(seed); np.random.seed(seed)
    cols = FEATURES[feats]
    Wtr, end_tr, start_tr = windows_idx(train, cols, L)
    if drop_flip_windows:      # drop training windows in which the gravity axis (largest ACC RMS) changes between consecutive rows
        g = train[["ACC_x_RMS", "ACC_y_RMS", "ACC_z_RMS"]].to_numpy().argmax(1); chg = np.concatenate([[0], (np.diff(g) != 0).astype(int)])
        cs = np.concatenate([[0], np.cumsum(chg)])
        keep = (cs[end_tr + 1] - cs[start_tr + 1]) == 0
        Wtr = Wtr[keep]
    Wte, end_te, _ = windows_idx(test, cols, L)
    mu, sd = Wtr.reshape(-1, len(cols)).mean(0), Wtr.reshape(-1, len(cols)).std(0)
    Wtr, Wte = (Wtr - mu) / sd, (Wte - mu) / sd
    if kind == "dense":                       # L = 1: the row itself; L > 1: the window flattened into one long vector
        Wtr, Wte = Wtr.reshape(len(Wtr), -1), Wte.reshape(len(Wte), -1)
        model = DenseAE(Wtr.shape[1], 1 if L == 1 else 3).to(dev); kw = dict(epochs=100, batch_size=16)
    else:
        model = SeqAE(len(cols), 16, 8, kind).to(dev); kw = dict(epochs=60, batch_size=64)
    fit(model, Wtr, seed=seed, **kw)
    return end_te, window_scores(model, Wte), window_scores(model, Wtr), len(Wtr)

row_label = lambda idx: np.array([match_index(test.t.iloc[i], test.t.iloc[i]) >= 0 for i in idx])    # row within +-1 min of a labelled anomaly

# ---- A ----
common = windows_idx(test, FEATURES["imu6"], 20)[1]; y = row_label(common)
print(f"A) {len(common)} test rows scored by every model (rows that end a valid 20-row window); {y.mean():.0%} of them are within +-1 min of an anomaly\n")
cfg = [("single row, dense AE, 11 cols (paper's EDGE)", "dense", "paper11", 1), ("single row, dense AE, 6 IMU", "dense", "imu6", 1),
       ("window 5 flattened, dense AE", "dense", "imu6", 5), ("window 10 flattened, dense AE", "dense", "imu6", 10), ("window 20 flattened, dense AE", "dense", "imu6", 20),
       ("window 5, GRU AE", "gru", "imu6", 5), ("window 10, GRU AE", "gru", "imu6", 10), ("window 20, GRU AE", "gru", "imu6", 20)]
print(f"{'model':48s} {'AUROC mean+-sd':>16s} {'AUPRC mean+-sd':>16s}   (chance AUROC 0.5, chance AUPRC {y.mean():.2f})")
for name, kind, feats, L in cfg:
    au, ap = [], []
    for s in SEEDS:
        end_te, err, _, _ = train_score(kind, feats, L, s)
        e = dict(zip(end_te, err)); sc = np.array([e[i] for i in common])
        au.append(roc_auc_score(y, sc)); ap.append(average_precision_score(y, sc))
    print(f"{name:48s} {np.mean(au):7.3f} +-{np.std(au):.3f}   {np.mean(ap):7.3f} +-{np.std(ap):.3f}")

# ---- B ----
print("\nB) GRU AE, window 10, 6 IMU: training windows with a gravity-axis switch removed or not (same test rows/labels as A)")
y10 = row_label(windows_idx(test, FEATURES["imu6"], 10)[1])
for drop in (False, True):
    au, ap, n = [], [], []
    for s in SEEDS:
        end_te, err, _, ntr = train_score("gru", "imu6", 10, s, drop_flip_windows=drop)
        sc = np.array([dict(zip(end_te, err))[i] for i in common]) 
        au.append(roc_auc_score(y, sc)); ap.append(average_precision_score(y, sc)); n.append(ntr)
    print(f"{'clean training' if drop else 'all training windows':24s} train windows {n[0]:6d}  AUROC {np.mean(au):.3f} +-{np.std(au):.3f}  AUPRC {np.mean(ap):.3f} +-{np.std(ap):.3f}")

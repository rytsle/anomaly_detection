# Retrains the main GRU autoencoder (seed 0, same settings as baseline_gru.ipynb) and exports what the explainer's threshold widget needs.
# Run from anomaly_detection/:  uv run python deep_dive/make_data.py
import json
exec(open("slides/_setup_cell_copy.py").read())
LOG_CSV = "/dev/null"
run("GRU-AE imu6 L=10 s0", "gru", "imu6", 10, 0, batch_size=64, epochs=60)
et, err, thr = SCORES["GRU-AE imu6 L=10 s0"]
_, st, _ = make_windows(test, FEATURES["imu6"], 10)
mw = [match_index(pd.Timestamp(a), pd.Timestamp(b)) for a, b in zip(st, et)]            # match by the whole window (the authors' way)
me = [match_index(pd.Timestamp(b), pd.Timestamp(b)) for b in et]                          # match by the last row only
pos = np.searchsorted(et, ANOM.to_numpy()).tolist()
data = dict(err=[float(f"{v:.5g}") for v in err], mw=mw, me=me, pos=pos, n_anom=len(ANOM),
            thr={k: float(f"{v:.5g}") for k, v in thr.items()}, times=[str(pd.Timestamp(t))[:16] for t in et])
json.dump(data, open("deep_dive/data.json", "w"))
print("windows", len(err), "thresholds", data["thr"])
for k, v in thr.items():
    print(k, {m: event_scores(err > v, st if m == "window" else et, et) for m in ("window", "end")})

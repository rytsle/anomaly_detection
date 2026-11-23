# Reference points for reading the event F1: what trivial detectors score, and threshold-free ranking quality (AUROC / AUPRC).
# Run from anomaly_detection/:  uv run python deep_dive/metric_check.py | tee deep_dive/metric_check_output.txt
import json
from sklearn.metrics import roc_auc_score, average_precision_score
exec(open("slides/_setup_cell_copy.py").read())
LOG_CSV = "/dev/null"            # nothing is logged to the experiment CSV here (these are reference points, not new models)
rng = np.random.default_rng(0)

cfgs = [("dense-1HL paper11", "dense", "paper11", 1, {}), ("dense-1HL imu6", "dense", "imu6", 1, {}),
        ("GRU-AE imu6 L=5", "gru", "imu6", 5, dict(batch_size=64, epochs=60)), ("GRU-AE imu6 L=10", "gru", "imu6", 10, dict(batch_size=64, epochs=60)),
        ("GRU-AE imu6 L=20", "gru", "imu6", 20, dict(batch_size=64, epochs=60)), ("LSTM-AE imu6 L=10", "lstm", "imu6", 10, dict(batch_size=64, epochs=60)),
        ("GRU-AE paper11 L=10", "gru", "paper11", 10, dict(batch_size=64, epochs=60))]
print("Seed 0 of each configuration, q95 threshold. 'flag all' and 'random' use the paper's event metric.\n")
print(f"{'model':22s} {'windows':>7s} {'near-anomaly':>12s} {'AUROC':>6s} {'AUPRC':>6s} | {'flagged@q95':>11s} {'event F1':>8s} | {'flag-all F1':>11s} {'random(same count) F1':>21s}")
for name, kind, feat, L, kw in cfgs:
    run(name, kind, feat, L, 0, thresholds=("q95",), **kw)
    _, err, thr = SCORES[name]
    _, st, et = make_windows(test, FEATURES[feat], L)
    y = np.array([match_index(pd.Timestamp(a), pd.Timestamp(b)) >= 0 for a, b in zip(st, et)])      # window lies within +-1 min of a labelled anomaly
    f = err > thr["q95"]
    ev = event_scores(f, st, et)
    allf = event_scores(np.ones(len(err), bool), st, et)
    k = int(f.sum())
    rnd = np.mean([event_scores(np.isin(np.arange(len(err)), rng.choice(len(err), k, replace=False)), st, et)["f1"] for _ in range(300)])
    print(f"{name:22s} {len(y):7d} {y.mean():12.2f} {roc_auc_score(y, err):6.3f} {average_precision_score(y, err):6.3f} | {f.mean():11.2f} {ev['f1']:8.3f} | {allf['f1']:11.3f} {rnd:21.2f}")

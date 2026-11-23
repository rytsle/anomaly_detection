import sys
exec(open("slides/_setup_cell_copy.py").read())
LOG_CSV = "/dev/null"
OUT = "slides/"
INK, TEAL, ORANGE, GREY = "#1F2933", "#1B998B", "#E4572E", "#6B7280"
plt.rcParams.update({"font.size": 12, "axes.edgecolor": GREY, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#E5E7EB", "grid.linewidth": 0.8})

# ---- 1) close-up of a few anomalies: acceleration + magnetic field per axis ----
w = test[(test.t >= "2021-01-21 15:00") & (test.t <= "2021-01-21 15:20")]
a = ANOM[(ANOM >= w.t.min()) & (ANOM <= w.t.max())]
fig, ax = plt.subplots(2, 1, figsize=(6.3, 4.2), sharex=True)
cols = {"x": "#374151", "y": "#9CA3AF", "z": TEAL}
for axis, c in cols.items():
    ax[0].plot(w.t, w[f"ACC_{axis}_RMS"], color=c, lw=1.8, label=f"{axis} ašis")
    ax[1].plot(w.t, w[f"MAG_{axis}_RMS"], color=c, lw=1.8)
for x in ax:
    for t_ in a: x.axvline(t_, color=ORANGE, lw=1.6)
ax[0].set_ylabel("pagreitis (m/s²)"); ax[1].set_ylabel("magnetinis laukas (µT)")
h_, l_ = ax[0].get_legend_handles_labels(); fig.legend(h_, l_, ncol=3, loc="upper center", frameon=False, fontsize=11)
ax[1].xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%H:%M")); ax[1].set_xlabel("laikas, 2021-01-21")
plt.tight_layout(rect=(0, 0, 1, 0.95)); plt.savefig(OUT + "fig_anomaly.png", dpi=200); plt.close()

# ---- 2) magnetic field level per session ----
d = pd.concat([train.assign(split="train"), test.assign(split="test")], ignore_index=True)
d["mag"] = np.sqrt(d.MAG_x_RMS**2 + d.MAG_y_RMS**2 + d.MAG_z_RMS**2)
d["sess"] = d.groupby("split").t.transform(lambda s: ((s.diff().abs() > pd.Timedelta("5min"))).cumsum())
g = d.groupby(["split", "sess"]).filter(lambda x: len(x) >= 30)
keys = g.groupby(["split", "sess"]).mag.median().sort_values().index
fig, ax = plt.subplots(figsize=(5.5, 3.0))
for i, k in enumerate(keys):
    v = g[(g.split == k[0]) & (g.sess == k[1])].mag
    b = ax.boxplot(v, positions=[i], widths=0.7, showfliers=False, patch_artist=True,
                   medianprops=dict(color=INK, lw=1), whiskerprops=dict(color=GREY), capprops=dict(color=GREY),
                   boxprops=dict(facecolor=TEAL if k[0] == "test" else "#9CA3AF", edgecolor=GREY))
ax.set_xticks([]); ax.set_xlabel("sesijos (nuo mažiausio iki didžiausio lauko)"); ax.set_ylabel("|B| (µT)")
ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color="#9CA3AF"), plt.Rectangle((0, 0), 1, 1, color=TEAL)], labels=["mokymo", "testo"], frameon=False, loc="upper left")
plt.tight_layout(); plt.savefig(OUT + "fig_sessions.png", dpi=200); plt.close()
s = g.groupby(["split", "sess"]).mag.agg(["mean", "std"])
print("between-session std of means %.1f, median within-session std %.1f, n sessions %d" % (s["mean"].std(), s["std"].median(), len(s)))

# ---- 3) error timeline of the main GRU model (retrained with the notebook's seed 0; not logged) ----
model, hist = run("GRU-AE imu6 L=10 s0", "gru", "imu6", 10, 0, batch_size=64, epochs=60)
et, err, thr = SCORES["GRU-AE imu6 L=10 s0"]
res = event_scores(err > thr["q95"], et, et) 
pos = np.searchsorted(et, ANOM.to_numpy()); x = np.arange(len(err))
fig, ax = plt.subplots(figsize=(12.13, 3.93))
ax.scatter(x, err, s=7, c=np.where(err > thr["q95"], ORANGE, TEAL), zorder=3)
for p in pos: ax.axvline(p, color=ORANGE, alpha=0.30, lw=1)
ax.axhline(thr["q95"], color=INK, ls="--", lw=1.2); ax.text(330, thr["q95"] * 1.7, "slenkstis (95 % mokymo klaidų)", fontsize=12, color=INK)
ax.set_yscale("log"); ax.set_ylabel("atkūrimo klaida"); ax.set_xlabel("testo langai laiko tvarka (tarpai tarp sesijų išmesti)")
plt.tight_layout(); plt.savefig(OUT + "fig_timeline.png", dpi=200); plt.close()
print("end-match F1 of this retrain at q95:", {k: round(v, 3) for k, v in res.items()})

# ---- 4) first look: |a| is almost constant, |B| is not, which axis carries gravity (train vs test) ----
norm = lambda d, p: np.sqrt(d[f"{p}_x_RMS"]**2 + d[f"{p}_y_RMS"]**2 + d[f"{p}_z_RMS"]**2)
GREY_T = "#9CA3AF"
fig, ax = plt.subplots(1, 3, figsize=(12.13, 3.6))
for d, c, lab in [(train, GREY_T, "mokymo"), (test, TEAL, "testo")]:
    ax[0].hist(norm(d, "ACC"), bins=np.linspace(9, 11, 61), density=True, alpha=0.75, color=c, label=lab)
    ax[1].hist(norm(d, "MAG"), bins=np.linspace(0, 175, 61), density=True, alpha=0.75, color=c, label=lab)
ax[0].axvline(9.81, color=INK, ls="--", lw=1.4); ax[0].text(9.84, ax[0].get_ylim()[1] * 0.9, "g = 9,81", fontsize=12)
ax[0].set_xlabel("|a| (m/s²)"); ax[0].set_title("Pagreičio ilgis", fontsize=13); ax[0].set_ylabel("tankis")
ax[1].set_xlabel("|B| (µT)"); ax[1].set_title("Magnetinio lauko ilgis", fontsize=13); ax[1].legend(frameon=False, loc="upper right")
share = lambda d: [(d[["ACC_x_RMS", "ACC_y_RMS", "ACC_z_RMS"]].to_numpy().argmax(1) == i).mean() * 100 for i in range(3)]
w = 0.38
ax[2].bar(np.arange(3) - w / 2, share(train), w, color=GREY_T, label="mokymo"); ax[2].bar(np.arange(3) + w / 2, share(test), w, color=TEAL, label="testo")
ax[2].set_xticks(range(3)); ax[2].set_xticklabels(["x", "y", "z"]); ax[2].set_xlabel("ašis, kurioje didžiausias pagreitis"); ax[2].set_ylabel("eilučių dalis (%)")
ax[2].set_title("Kur krenta gravitacija", fontsize=13)
for a_ in ax: a_.grid(axis="x", visible=False)
plt.tight_layout(); plt.savefig(OUT + "fig_overview.png", dpi=200); plt.close()
print("overview figure done")

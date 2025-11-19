import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

# ============================================================
# CONFIG
# ============================================================

INPUT = "phase2_processed.csv"
OUTDIR = "figures"

os.makedirs(OUTDIR, exist_ok=True)

# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(INPUT)

# Normalize workload names (IMPORTANT FIX)
df["workload"] = df["workload"].replace({
    "parallel_sort": "parallel_sort",
    "producer_consumer": "producer_consumer",
    "matrix_multiplication": "matrix_multiplication"
})

df_best = df[df["config_type"] == "p_best"].copy()

workloads = ["matrix_multiplication", "parallel_sort", "producer_consumer"]
languages = ["go", "java", "python", "rust"]

# nice labels
WL_LABEL = {
    "matrix_multiplication": "Matrix Multiplication",
    "parallel_sort": "Parallel Sort",
    "producer_consumer": "Producer–Consumer"
}

LANG_LABEL = {
    "go": "Go",
    "java": "Java",
    "python": "Python",
    "rust": "Rust"
}

# ============================================================
#  FUNCTION: save_graph()
# ============================================================

def save_graph(fig, name):
    path = os.path.join(OUTDIR, name)
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] saved {path}")

# ============================================================
#  GRAPH 1–6: per workload (speedup & efficiency)
# ============================================================

for wl in workloads:
    sub = df_best[df_best["workload"] == wl].copy()

    if sub.empty:
        print(f"[WARN] No data for workload {wl}, skipping")
        continue

    # sort by language for consistent graphs
    sub = sub.sort_values("language")

    # -------- SPEEDUP GRAPH --------
    fig = plt.figure(figsize=(8,5))
    plt.bar(
        [LANG_LABEL[l] for l in sub["language"]],
        sub["speedup"],
        color="skyblue",
        edgecolor="black"
    )
    plt.ylabel("Speedup (T1 / Tp_best)")
    plt.title(f"Speedup Comparison — {WL_LABEL[wl]}")
    save_graph(fig, f"speedup_{wl}.png")

    # -------- EFFICIENCY GRAPH --------
    fig = plt.figure(figsize=(8,5))
    plt.bar(
        [LANG_LABEL[l] for l in sub["language"]],
        sub["efficiency"],
        color="lightgreen",
        edgecolor="black"
    )
    plt.ylabel("Efficiency = Speedup / p_best")
    plt.title(f"Efficiency Comparison — {WL_LABEL[wl]}")
    save_graph(fig, f"efficiency_{wl}.png")

# ============================================================
#  GRAPH 7: Radar Chart — Overall parallel strength
# ============================================================

categories = [
    "Matrix Mul",
    "Parallel Sort",
    "Prod-Cons"
]
num_cat = len(categories)

# build radar data
radar_data = []

for lang in languages:
    vals = []
    for wl in workloads:
        row = df_best[(df_best["language"] == lang) & (df_best["workload"] == wl)]
        if len(row) == 0:
            vals.append(0)
        else:
            vals.append(float(row["speedup"].iloc[0]))
    radar_data.append(vals)

angles = np.linspace(0, 2 * np.pi, num_cat, endpoint=False).tolist()
angles += angles[:1]

fig = plt.figure(figsize=(8, 8))
ax = plt.subplot(111, polar=True)

for i, lang in enumerate(languages):
    vals = radar_data[i]
    vals += vals[:1]

    ax.plot(angles, vals, label=LANG_LABEL[lang])
    ax.fill(angles, vals, alpha=0.1)

ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories)
plt.title("Overall Parallel Strength (Speedup at p_best)")
plt.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))

save_graph(fig, "radar_parallel_strength.png")
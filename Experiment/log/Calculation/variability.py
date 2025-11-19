import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# =====================================================
# LOAD RAW PHASE 2 DATA (NOT THE MEDIAN/PROCESSED ONE)
# =====================================================
df = pd.read_csv("phase2.csv")

required = ["language", "workload", "config_type", "threads", "wall_time_s", "repeat"]
for col in required:
    if col not in df.columns:
        raise ValueError(f"Missing column: {col}")

# =====================================================
# 4.5.1 — Boxplot Wall-Time Variability per Language
# =====================================================
plt.figure(figsize=(16,6))
sns.boxplot(data=df, x="language", y="wall_time_s")
plt.title("Grafik 4.5.1 — Boxplot of Wall-Time Variability per Language", fontsize=16)
plt.xlabel("Language", fontsize=14)
plt.ylabel("Wall Time (s)", fontsize=14)
plt.tight_layout()
plt.show()

# =====================================================
# 4.5.2 — CV Comparison p=1 vs p=p_best
# =====================================================
cv_df = (
    df.groupby(["language", "workload", "config_type"])
      .agg(mean_time=("wall_time_s", "mean"),
           std_time=("wall_time_s", "std"))
      .reset_index()
)

cv_df["cv"] = cv_df["std_time"] / cv_df["mean_time"]

pivot = cv_df.pivot_table(
    index=["language", "workload"], 
    columns="config_type", 
    values="cv"
).reset_index()

pivot_melt = pivot.melt(
    id_vars=["language", "workload"],
    value_vars=["p_base", "p_best"],
    var_name="config",
    value_name="cv"
)

plt.figure(figsize=(16,6))
sns.barplot(data=pivot_melt, x="language", y="cv", hue="config")
plt.title("Grafik 4.5.2 — CV Comparison for p=1 and p=p_best Across Workloads", fontsize=16)
plt.xlabel("Language", fontsize=14)
plt.ylabel("Coefficient of Variation (CV)", fontsize=14)
plt.tight_layout()
plt.show()

# =====================================================
# 4.5.3 — Delta-CV (Parallel - Sequential)
# =====================================================
pivot["delta_cv"] = pivot["p_best"] - pivot["p_base"]

plt.figure(figsize=(16,6))
sns.barplot(data=pivot, x="language", y="delta_cv", hue="workload")
plt.title("Grafik 4.5.3 — Delta-CV Between Sequential and Parallel Configurations", fontsize=16)
plt.xlabel("Language", fontsize=14)
plt.ylabel("Δ CV (Parallel - Sequential)", fontsize=14)
plt.axhline(0, color="black", linewidth=1)
plt.tight_layout()
plt.show()

print("[OK] Semua grafik 4.5 berhasil ditampilkan!")
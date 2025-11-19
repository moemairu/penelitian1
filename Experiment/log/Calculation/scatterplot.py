import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("phase2_processed_full.csv")

def scatter(x, y, title):
    plt.figure(figsize=(7,5))
    for lang in df["language"].unique():
        sub = df[df["language"] == lang]
        plt.scatter(sub[x], sub[y], label=lang, s=80)
    plt.xlabel(x)
    plt.ylabel(y)
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()

scatter("cpu_pct", "speedup", "CPU Usage vs Speedup")
scatter("peak_rss_kb", "speedup", "Memory Usage vs Speedup")
scatter("cpu_pct", "efficiency", "CPU Usage vs Efficiency")
scatter("peak_rss_kb", "efficiency", "Memory Usage vs Efficiency")
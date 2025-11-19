import json
import pandas as pd

INPUT = "phase2.jsonl"
OUTPUT = "phase2_processed_full.csv"

# ==========================
# 1. LOAD JSONL
# ==========================
rows = []
buffer = ""

with open(INPUT) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        buffer += line
        if buffer.startswith("{") and buffer.endswith("}"):
            try:
                rows.append(json.loads(buffer))
            except:
                pass
            buffer = ""

df = pd.DataFrame(rows)

# ==========================
# 2. CLEAN & TYPECAST
# ==========================

for col in ["threads", "wall_time_s", "cpu_pct", "peak_rss_kb"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df[df.wall_time_s.notna()]

# ==========================
# 3. GROUP BY MEDIAN
# ==========================
agg = (
    df.groupby(["language", "workload", "config_type", "threads"])
      .agg({
          "wall_time_s": "median",
          "cpu_pct": "median",
          "peak_rss_kb": "median"
      })
      .reset_index()
)

# ==========================
# 4. COMPUTE SPEEDUP & EFFICIENCY
# ==========================

results = []

for (lang, wl), sub in agg.groupby(["language", "workload"]):
    base_row = sub[sub["config_type"] == "p_base"]
    best_row = sub[sub["config_type"] == "p_best"]

    if base_row.empty:
        continue

    T1 = base_row.iloc[0]["wall_time_s"]
    pbest_threads = int(best_row.iloc[0]["threads"]) if not best_row.empty else 1

    sub["speedup"] = T1 / sub["wall_time_s"]
    sub["efficiency"] = sub["speedup"] / sub["threads"]

    results.append(sub)

final = pd.concat(results)

# ==========================
# 5. EXPORT
# ==========================

final.to_csv(OUTPUT, index=False)
print("[OK] Saved:", OUTPUT)
print(final)
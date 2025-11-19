import json
import pandas as pd

INPUT = "phase2.jsonl"
OUTPUT_CSV = "phase2_processed.csv"

# ============================================================
# 1) LOAD phase2.jsonl (multi-line JSON parser)
# ============================================================

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
                obj = json.loads(buffer)
                rows.append(obj)
            except Exception as e:
                print("ERROR parsing:", buffer[:80], "->", e)
            buffer = ""

print(f"[INFO] Loaded {len(rows)} Phase 2 records")

df = pd.DataFrame(rows)

# ============================================================
# 2) CLEAN DATA
# ============================================================

numeric_cols = ["threads", "wall_time_s", "cpu_pct", "peak_rss_kb", "repeat"]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

df = df[df.wall_time_s.notna()]

print(f"[INFO] Cleaned records: {len(df)}")


# ============================================================
# 3) MEDIAN per (language, workload, config_type, threads)
# ============================================================

agg = (
    df.groupby(["language", "workload", "config_type", "threads"])
      .wall_time_s.median()
      .reset_index()
)

print("\n=== MEDIAN WALL TIME (Phase 2) ===")
print(agg)


# ============================================================
# 4) COMPUTE SPEEDUP & EFFICIENCY
# ============================================================

results = []

for (lang, wl), sub in agg.groupby(["language", "workload"]):
    
    # find T1 from p_base (threads = 1)
    base_row = sub[(sub.config_type == "p_base") & (sub.threads == 1)]
    
    if base_row.empty:
        print(f"[WARN] Missing p_base for {lang}-{wl}, skip")
        continue
    
    T1 = base_row.wall_time_s.values[0]

    sub = sub.sort_values("threads")
    sub["speedup"] = T1 / sub.wall_time_s
    sub["efficiency"] = sub["speedup"] / sub["threads"]

    results.append(sub)

final = pd.concat(results).sort_values(["language", "workload", "config_type"])

print("\n=== FINAL RESULTS (Phase 2) ===")
print(final)

# ============================================================
# 5) EXPORT
# ============================================================

final.to_csv(OUTPUT_CSV, index=False)
print(f"\n[OK] Saved → {OUTPUT_CSV}")
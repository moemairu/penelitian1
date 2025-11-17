import json
import pandas as pd

# ================================
# CONFIG
# ================================
PHASE1 = "phase1.jsonl"
PHASE2 = "phase2.jsonl"
OUT1 = "phase1_median.csv"
OUT2 = "phase2_median.csv"

# ================================
# FUNCTION: LOAD JSONL MULTILINE
# ================================
def load_jsonl_multiline(path):
    rows = []
    buf = ""

    with open(path, "r") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            buf += line

            if buf.startswith("{") and buf.endswith("}"):
                try:
                    obj = json.loads(buf)
                    rows.append(obj)
                except Exception as e:
                    print("parse error:", e, buf[:80])
                buf = ""

    return pd.DataFrame(rows)

# ================================
# FUNCTION: CLEAN + MEDIAN
# ================================
def compute_median(df, phase_label):
    # Convert numerics
    numeric_cols = ["threads", "wall_time_s", "cpu_pct", "peak_rss_kb", "repeat"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Filter only valid rows
    df = df[df.wall_time_s.notna()]

    group_cols = ["language", "workload", "threads"]
    if "config_type" in df.columns:  # phase 2
        group_cols.append("config_type")

    # Median aggregation
    agg = (
        df.groupby(group_cols)
          .wall_time_s.median()
          .reset_index()
          .sort_values(group_cols)
    )

    print(f"\n=== {phase_label} MEDIAN ===")
    print(agg)

    return agg

# ================================
# MAIN PROCESS
# ================================
print("Loading Phase 1...")
df1 = load_jsonl_multiline(PHASE1)
print("Phase 1 rows:", len(df1))

print("Loading Phase 2...")
df2 = load_jsonl_multiline(PHASE2)
print("Phase 2 rows:", len(df2))

print("\nProcessing Phase 1...")
median1 = compute_median(df1, "PHASE 1")
median1.to_csv(OUT1, index=False)
print(f"[OK] Saved → {OUT1}")

print("\nProcessing Phase 2...")
median2 = compute_median(df2, "PHASE 2")
median2.to_csv(OUT2, index=False)
print(f"[OK] Saved → {OUT2}")
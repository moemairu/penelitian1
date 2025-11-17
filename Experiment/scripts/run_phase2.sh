#!/bin/bash
set -eo pipefail

# Phase 2 Benchmark Runner — p_base vs p_best comparison
ROOT_DIR="/home/mole/penelitian1/Experiment"
BENCH_DIR="$ROOT_DIR/benchmark"
LOG_DIR="$ROOT_DIR/log"
RAW_LOG="$LOG_DIR/phase2.jsonl"

mkdir -p "$LOG_DIR"
: > "$RAW_LOG"

timestamp() { date +"%Y-%m-%dT%H:%M:%S%z"; }

echo "=== Phase 2 Benchmark Started at $(timestamp) ==="
echo "Logs → $RAW_LOG"
echo ""

# quick deps check
if ! command -v jq >/dev/null 2>&1; then
  echo "error: jq not found. install 'jq' first" >&2
  exit 1
fi
if [[ ! -x "/usr/bin/time" ]]; then
  echo "error: /usr/bin/time not found or not executable" >&2
  exit 1
fi

# check cpu governor
echo "[INIT] check cpu governor..."
if [[ -r /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor ]]; then
  gov=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)
  echo "  → governor = $gov"
  [[ "$gov" != "performance" ]] && echo "  WARNING: governor is not performance!"
fi
echo ""

# cleanup function
cleanup_all() {
  echo "[CLEAN] cleaning workspace..."
  find "$BENCH_DIR/src_java" -name "*.class" -delete 2>/dev/null || true
  if [[ -d "$BENCH_DIR/src_rust" ]]; then
    (cd "$BENCH_DIR/src_rust" && cargo clean >/dev/null 2>&1) || true
  fi
  if [[ -d "$BENCH_DIR/src_go" ]]; then
    (cd "$BENCH_DIR/src_go" && go clean -cache >/dev/null 2>&1) || true
  fi
  echo "[CLEAN] done."
  echo ""
}

cleanup_all

# Java warm-up for Phase 2
echo "=== java warm-up (5x each workload) ==="
JAVA_DIR="$BENCH_DIR/src_java"
if [[ -d "$JAVA_DIR" ]]; then
  cd "$JAVA_DIR"
  javac *.java >/dev/null 2>&1 || true
  
  echo "[WARM-UP] Matmul (5x)"
  for i in {1..5}; do
    THREADS=4 taskset -c 0-3 java Matmul >/dev/null 2>&1 || true
  done
  
  echo "[WARM-UP] ParallelSort (5x)"
  for i in {1..5}; do
    THREADS=4 taskset -c 0-3 java ParallelSort >/dev/null 2>&1 || true
  done
  
  echo "[WARM-UP] ProdCons (5x)"
  for i in {1..5}; do
    THREADS=4 taskset -c 0-3 java ProdCons >/dev/null 2>&1 || true
  done
  
  echo ""
fi

# file mappings
declare -A PY_FILES=(
  ["matmul"]="matmul.py"
  ["sort"]="parallel_sort.py"
  ["prod-cons"]="prodcons.py"
)

declare -A RS_FILES=(
  ["matmul"]="matmul"
  ["sort"]="parallel_sort"
  ["prod-cons"]="prod_cons"
)

declare -A GO_FILES=(
  ["matmul"]="matmul.go"
  ["sort"]="parallel_sort.go"
  ["prod-cons"]="prod_cons.go"
)

declare -A JV_FILES=(
  ["matmul"]="Matmul"
  ["sort"]="ParallelSort"
  ["prod-cons"]="ProdCons"
)

# Phase 2 config: p_base=1 for all, p_best from table
P_BASE=1
REPEATS=10

# p_best configuration table
declare -A P_BEST
P_BEST["go,matmul"]=8
P_BEST["go,sort"]=8
P_BEST["go,prod-cons"]=8
P_BEST["java,matmul"]=8
P_BEST["java,sort"]=4
P_BEST["java,prod-cons"]=4
P_BEST["python,matmul"]=8
P_BEST["python,sort"]=4
P_BEST["python,prod-cons"]=2
P_BEST["rust,matmul"]=8
P_BEST["rust,sort"]=8
P_BEST["rust,prod-cons"]=1

coremask() { local p=$1; echo "0-$((p-1))"; }

# parse elapsed time to seconds
to_seconds() {
  s="$1"
  s="$(echo "$s" | tr -d '[:space:]')"
  if [[ "$s" == *:* ]]; then
    IFS=':' read -ra parts <<< "$s"
    if (( ${#parts[@]} == 2 )); then
      min=${parts[0]}; sec=${parts[1]}
      awk -v m="$min" -v s="$sec" 'BEGIN{printf "%.6f", m*60 + s}'
    else
      hh=${parts[0]}; mm=${parts[1]}; ss=${parts[2]}
      awk -v h="$hh" -v m="$mm" -v s="$ss" 'BEGIN{printf "%.6f", h*3600 + m*60 + s}'
    fi
  else
    awk -v s="$s" 'BEGIN{printf "%.6f", s}'
  fi
}

# run single benchmark
run_one() {
  local lang="$1"
  local workload="$2"
  local p="$3"
  local config_type="$4"  # "p_base" or "p_best"

  for ((r=1; r<=REPEATS; r++)); do
    echo "[RUN] $lang | $workload | $config_type (p=$p) | repeat $r"
    cleanup_all
    mask=$(coremask $p)

    # prepare command based on language
    case $lang in
      python)
        cd "$BENCH_DIR/src_python"
        progfile="${PY_FILES[$workload]}"
        cmd="python3 $progfile"
        ;;
      rust)
        cd "$BENCH_DIR/src_rust"
        cargo build --release >/dev/null 2>&1
        bin="${RS_FILES[$workload]}"
        cmd="./target/release/${bin}"
        ;;
      go)
        cd "$BENCH_DIR/src_go"
        progfile="${GO_FILES[$workload]}"
        cmd="go run $progfile"
        ;;
      java)
        cd "$BENCH_DIR/src_java"
        javac *.java >/dev/null 2>&1 || true
        cls="${JV_FILES[$workload]}"
        cmd="java $cls"
        ;;
      *)
        echo "unknown lang $lang" >&2
        return 1
        ;;
    esac

    # create temp files
    TIMEFILE="$(mktemp "$LOG_DIR/time.XXXXXX")"
    PROGOUT="$(mktemp "$LOG_DIR/prog.XXXXXX.json")"

    # execute with timing
    set +e
    /usr/bin/time -v -o "$TIMEFILE" env THREADS="$p" taskset -c "$mask" $cmd > "$PROGOUT" 2>&1
    EXIT_CODE=$?
    set -e

    # if no output, create minimal JSON
    if [[ ! -s "$PROGOUT" ]]; then
      echo "{\"language\":\"$lang\",\"workload\":\"$workload\",\"threads\":$p,\"note\":\"no_program_output\",\"exit_code\":$EXIT_CODE}" > "$PROGOUT"
    fi

    # parse time metrics
    wall_line=$(grep -i "Elapsed (wall clock) time" "$TIMEFILE" || true)
    if [[ -n "$wall_line" ]]; then
      wall_raw=$(echo "$wall_line" | awk '{print $NF}')
      wall_s=$(to_seconds "$wall_raw")
    else
      user_s=$(grep -i "User time" "$TIMEFILE" | awk -F: '{print $2}' | tr -d ' ' || echo "0")
      sys_s=$(grep -i "System time" "$TIMEFILE" | awk -F: '{print $2}' | tr -d ' ' || echo "0")
      wall_s=$(awk -v u="${user_s:-0}" -v s="${sys_s:-0}" 'BEGIN{printf "%.6f", u+s}')
    fi

    # parse CPU percentage
    cpu_pct_raw=$(grep -iE "Percent of (the )?CPU this job got" "$TIMEFILE" || true)
    if [[ -n "$cpu_pct_raw" ]]; then
      cpu_pct=$(echo "$cpu_pct_raw" | awk -F: '{print $2}' | tr -d ' %' | xargs)
    else
      cpu_pct="0"
    fi
    cpu_pct=${cpu_pct:-0}

    # parse memory
    rss_raw=$(grep -i "Maximum resident set size" "$TIMEFILE" | awk -F: '{print $2}' | tr -d ' ' | xargs || true)
    peak_rss_kb=${rss_raw:-0}

    # create run_id
    run_id="${lang}_phase2_${workload}_${config_type}_p${p}_r${r}"

    # merge with program output
    if jq -e . "$PROGOUT" >/dev/null 2>&1; then
      merged=$(jq --arg runid "$run_id" \
                  --arg cfg_type "$config_type" \
                  --argjson wall "$(printf '%s' "$wall_s")" \
                  --argjson cpu "$(printf '%s' "$cpu_pct")" \
                  --argjson rss "$(printf '%s' "$peak_rss_kb")" \
                  --argjson repeat "$r" \
                  '. + {run_id:$runid, config_type:$cfg_type, wall_time_s:$wall, cpu_pct:$cpu, peak_rss_kb:$rss, phase:2, repeat:$repeat}' "$PROGOUT" 2>/dev/null || true)
    else
      prog_txt=$(cat "$PROGOUT" | sed 's/"/\\"/g' | tr '\n' ' ')
      merged=$(jq -n --arg runid "$run_id" \
                     --arg lang "$lang" \
                     --arg wl "$workload" \
                     --argjson pval "$p" \
                     --arg cfg_type "$config_type" \
                     --arg prog "$prog_txt" \
                     --argjson wall "$(printf '%s' "$wall_s")" \
                     --argjson cpu "$(printf '%s' "$cpu_pct")" \
                     --argjson rss "$(printf '%s' "$peak_rss_kb")" \
                     --argjson repeat "$r" \
                     '{language:$lang, workload:$wl, threads:$pval, config_type:$cfg_type, program_output:$prog, run_id:$runid, wall_time_s:$wall, cpu_pct:$cpu, peak_rss_kb:$rss, phase:2, repeat:$repeat}')
    fi

    # append to log
    echo "$merged" >> "$RAW_LOG"

    # cleanup temp files
    rm -f "$TIMEFILE" "$PROGOUT"
  done
}

# Main loop: test p_base and p_best for each language+workload
LANGS=("go" "java" "python" "rust")
WORKLOADS=("matmul" "sort" "prod-cons")

for lang in "${LANGS[@]}"; do
  for workload in "${WORKLOADS[@]}"; do
    echo ""
    echo "=========================================="
    echo "Testing: $lang - $workload"
    echo "=========================================="
    
    # Get p_best for this combination
    key="${lang},${workload}"
    p_best=${P_BEST[$key]}
    
    if [[ -z "$p_best" ]]; then
      echo "WARNING: no p_best defined for $key, skipping"
      continue
    fi
    
    echo "  p_base=$P_BASE, p_best=$p_best"
    echo ""
    
    # Run p_base
    echo "--- Running p_base (p=$P_BASE) ---"
    run_one "$lang" "$workload" "$P_BASE" "p_base"
    
    # Run p_best (skip if same as p_base)
    if [[ "$p_best" != "$P_BASE" ]]; then
      echo ""
      echo "--- Running p_best (p=$p_best) ---"
      run_one "$lang" "$workload" "$p_best" "p_best"
    else
      echo "  (p_best == p_base, skipping duplicate)"
    fi
  done
done

# final cleanup
echo ""
echo "[FINAL CLEAN] resetting..."
cleanup_all

echo ""
echo "=== Phase 2 Completed at $(timestamp) ==="
echo "Total runs: $(($(wc -l < "$RAW_LOG"))) records"
echo "Output saved to: $RAW_LOG"
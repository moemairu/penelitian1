#!/bin/bash
set -eo pipefail

# Phase 1 Benchmark Runner — external timing (time -v) + merge JSON
ROOT_DIR="/home/mole/penelitian1/Experiment"
BENCH_DIR="$ROOT_DIR/benchmark"
LOG_DIR="$ROOT_DIR/log"
RAW_LOG="$LOG_DIR/phase1.jsonl"

mkdir -p "$LOG_DIR"
: > "$RAW_LOG"

timestamp() { date +"%Y-%m-%dT%H:%M:%S%z"; }

echo "=== Phase 1 Benchmark Started at $(timestamp) ==="
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

# 1) init / warm-up (java)
echo "[INIT] check cpu governor..."
if [[ -r /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor ]]; then
  gov=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)
  echo "  → governor = $gov"
  [[ "$gov" != "performance" ]] && echo "  WARNING: governor is not performance!"
fi
echo ""

echo "=== java warm-up (5x each workload) ==="
JAVA_DIR="$BENCH_DIR/src_java"
if [[ -d "$JAVA_DIR" ]]; then
  cd "$JAVA_DIR"
  javac *.java >/dev/null 2>&1 || true
  WJ=("Matmul" "ParallelSort" "ProdCons")
  for W in "${WJ[@]}"; do
    echo "[WARM-UP] $W (5x)"
    for i in {1..5}; do
      THREADS=4 taskset -c 0-3 java "$W" >/dev/null 2>&1 || true
    done
    echo ""
  done
fi

# cleanup function (before each run)
cleanup_all() {
  echo "[CLEAN] cleaning workspace..."
  # java .class
  find "$BENCH_DIR/src_java" -name "*.class" -delete 2>/dev/null || true
  # rust
  if [[ -d "$BENCH_DIR/src_rust" ]]; then
    (cd "$BENCH_DIR/src_rust" && cargo clean >/dev/null 2>&1) || true
  fi
  # go
  if [[ -d "$BENCH_DIR/src_go" ]]; then
    (cd "$BENCH_DIR/src_go" && go clean -cache >/dev/null 2>&1) || true
  fi
  echo "[CLEAN] done."
  echo ""
}

cleanup_all

# mappings + config
PY_map_matrix_multiplication="matmul.py"
PY_map_parallel_sort="parallel_sort.py"
PY_map_producer_consumer="prodcons.py"

RS_map_matrix_multiplication="matmul"
RS_map_parallel_sort="parallel_sort"
RS_map_producer_consumer="prod_cons"

GO_map_matrix_multiplication="matmul.go"
GO_map_parallel_sort="parallel_sort.go"
GO_map_producer_consumer="prod_cons.go"

JV_map_matrix_multiplication="Matmul"
JV_map_parallel_sort="ParallelSort"
JV_map_producer_consumer="ProdCons"

LANGS=("python" "rust" "go" "java")
WORKLOADS=("matrix_multiplication" "parallel_sort" "producer_consumer")
THREADS_LIST=(1 2 4 8)
REPEATS=5

coremask() { local p=$1; echo "0-$((p-1))"; }

# parse elapsed mm:ss / hh:mm:ss formats to seconds (supports 0:00.123 or 0:00:01)
to_seconds() {
  s="$1"
  # trim
  s="$(echo "$s" | tr -d '[:space:]')"
  # if contains ':', split
  if [[ "$s" == *:* ]]; then
    IFS=':' read -ra parts <<< "$s"
    # parts could be [MM SS.ms] or [HH MM SS.ms]
    if (( ${#parts[@]} == 2 )); then
      min=${parts[0]}; sec=${parts[1]}
      awk -v m="$min" -v s="$sec" 'BEGIN{printf "%.6f", m*60 + s}'
    else
      # assume HH:MM:SS.ms
      hh=${parts[0]}; mm=${parts[1]}; ss=${parts[2]}
      awk -v h="$hh" -v m="$mm" -v s="$ss" 'BEGIN{printf "%.6f", h*3600 + m*60 + s}'
    fi
  else
    # plain seconds
    awk -v s="$s" 'BEGIN{printf "%.6f", s}'
  fi
}

# run helper: build/run, capture stdout(program) and time-stderr -> merge JSON
run_one() {
  local lang="$1"; local workload="$2"; local p="$3"

  for ((r=1; r<=REPEATS; r++)); do
    echo "[RUN] $lang | $workload | p=$p | repeat $r"
    cleanup_all
    mask=$(coremask $p)

    # prepare command
    case $lang in
      python)
        cd "$BENCH_DIR/src_python"
        progfile=$(eval echo "\$PY_map_${workload}")
        cmd="python3 $progfile"
        ;;
      rust)
        cd "$BENCH_DIR/src_rust"
        cargo build --release >/dev/null 2>&1
        bin=$(eval echo "\$RS_map_${workload}")
        cmd="./target/release/${bin}"
        ;;
      go)
        cd "$BENCH_DIR/src_go"
        progfile=$(eval echo "\$GO_map_${workload}")
        cmd="go run $progfile"
        ;;
      java)
        cd "$BENCH_DIR/src_java"
        javac *.java >/dev/null 2>&1 || true
        cls=$(eval echo "\$JV_map_${workload}")
        cmd="java $cls"
        ;;
      *)
        echo "unknown lang $lang" >&2; return 1
        ;;
    esac

    # create temp files
    TIMEFILE="$(mktemp "$LOG_DIR/time.XXXXXX")"
    PROGOUT="$(mktemp "$LOG_DIR/prog.XXXXXX.json")"

    # run with time -v writing verbose to TIMEFILE; program stdout -> PROGOUT
    # note: set THREADS env for program
    set +e
    /usr/bin/time -v -o "$TIMEFILE" env THREADS="$p" taskset -c "$mask" $cmd > "$PROGOUT" 2>&1
    EXIT_CODE=$?
    set -e

    # if program produced no JSON, create minimal JSON with error note
    if [[ ! -s "$PROGOUT" ]]; then
      echo "{\"language\":\"$lang\",\"workload\":\"$workload\",\"threads\":$p,\"note\":\"no_program_output\",\"exit_code\":$EXIT_CODE}" > "$PROGOUT"
    fi

    # parse timefile - FIX: support both "Percent of CPU" and "Percent of the CPU"
    wall_line=$(grep -i "Elapsed (wall clock) time" "$TIMEFILE" | tr -d '\r' || true)

    if [[ -n "$wall_line" ]]; then
      # Extract everything after the last ": " (handle timestamps with colons)
      wall_raw=$(echo "$wall_line" | sed -E 's/^.*:[[:space:]]*([0-9]+:[0-9]+\.[0-9]+)$/\1/' || true)
      if [[ -z "$wall_raw" || "$wall_raw" == "$wall_line" ]]; then
        # Fallback: simple cut after ": "
        wall_raw=$(echo "$wall_line" | awk -F': ' '{print $2}' | tr -d ' ')
      fi
      wall_s=$(to_seconds "$wall_raw")
    else
      # Fallback: use User + System time
      user_s=$(grep -i "User time (seconds)" "$TIMEFILE" | awk -F: '{print $2}' | tr -d ' ' || echo "0")
      sys_s=$(grep -i "System time (seconds)" "$TIMEFILE" | awk -F: '{print $2}' | tr -d ' ' || echo "0")
      user_s=${user_s:-0}; sys_s=${sys_s:-0}
      wall_s=$(awk -v u="$user_s" -v s="$sys_s" 'BEGIN{printf "%.6f", u+s}')
    fi

    # FIX: Flexible regex to match both formats
    cpu_pct_raw=$(grep -iE "Percent of (the )?CPU this job got" "$TIMEFILE" || true)
    if [[ -n "$cpu_pct_raw" ]]; then
      cpu_pct=$(echo "$cpu_pct_raw" | awk -F: '{print $2}' | tr -d ' %' | xargs)
    else
      cpu_pct="0"
    fi
    cpu_pct=${cpu_pct:-0}

    rss_raw=$(grep -i "Maximum resident set size" "$TIMEFILE" | awk -F: '{print $2}' | tr -d ' ' | xargs || true)
    peak_rss_kb=${rss_raw:-0}

    # merge program JSON + external metrics
    run_id="${lang}_phase1_${workload}_p${p}_r${r}"
    # ensure PROGOUT is valid JSON; if not, wrap as message
    if jq -e . "$PROGOUT" >/dev/null 2>&1; then
      merged=$(jq --arg runid "$run_id" \
                  --argjson wall "$(printf '%s' "$wall_s")" \
                  --argjson cpu "$(printf '%s' "$cpu_pct")" \
                  --argjson rss "$(printf '%s' "$peak_rss_kb")" \
                  --argjson repeat "$r" \
                  '. + {run_id:$runid, wall_time_s:$wall, cpu_pct:$cpu, peak_rss_kb:$rss, phase:1, repeat:$repeat}' "$PROGOUT" 2>/dev/null || true)
    else
      # not valid JSON, wrap
      prog_txt=$(cat "$PROGOUT" | sed 's/"/\\"/g' | tr '\n' ' ')
      merged=$(jq -n --arg runid "$run_id" \
                     --arg lang "$lang" \
                     --arg wl "$workload" \
                     --argjson pval "$p" \
                     --arg prog "$prog_txt" \
                     --argjson wall "$(printf '%s' "$wall_s")" \
                     --argjson cpu "$(printf '%s' "$cpu_pct")" \
                     --argjson rss "$(printf '%s' "$peak_rss_kb")" \
                     --argjson repeat "$r" \
                     '{language:$lang, workload:$wl, threads:$pval, program_output:$prog, run_id:$runid, wall_time_s:$wall, cpu_pct:$cpu, peak_rss_kb:$rss, phase:1, repeat:$repeat}')
    fi

    # append to global logfile
    echo "$merged" >> "$RAW_LOG"

    # cleanup temp files
    rm -f "$TIMEFILE" "$PROGOUT"

  done
}

# phase 1 loop (all configs × repeats)
for L in "${LANGS[@]}"; do
  for W in "${WORKLOADS[@]}"; do
    for P in "${THREADS_LIST[@]}"; do
      run_one "$L" "$W" "$P"
    done
  done
done

# final cleanup
echo "[FINAL CLEAN] resetting..."
cleanup_all

echo "=== Phase 1 Completed at $(timestamp) ==="
echo "output saved to: $RAW_LOG"
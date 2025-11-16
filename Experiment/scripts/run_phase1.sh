#!/bin/bash

# ===========================================================
# Phase 1 Runner — Matching EXACT folder + filenames you use
# ===========================================================

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BENCH_DIR="$ROOT_DIR/benchmark"
RAW_LOG="$ROOT_DIR/log/phase1.jsonl"

mkdir -p "$ROOT_DIR/log"
echo "" > "$RAW_LOG"

timestamp() { date +"%Y-%m-%dT%H:%M:%S%z"; }

LANGS=("python" "rust" "go" "java")
WORKLOADS=("matrix_multiplication" "parallel_sort" "producer_consumer")
THREADS_LIST=(1 2 4 8)

echo "=== Phase 1 Benchmark Started at $(timestamp) ==="
echo "Logs → $RAW_LOG"
echo ""

# ===========================================================
# WORKLOAD → FILENAME MAPPING (BASED ON YOUR FOLDER)
# ===========================================================

# Python
PY_MAP_matrix_multiplication="matmul.py"
PY_MAP_parallel_sort="parallel_sort.py"
PY_MAP_producer_consumer="prodcons.py"

# Rust
RS_MAP_matrix_multiplication="matmul"
RS_MAP_parallel_sort="parallel_sort"
RS_MAP_producer_consumer="prod_cons"

# Go
GO_MAP_matrix_multiplication="matmul.go"
GO_MAP_parallel_sort="parallel_sort.go"
GO_MAP_producer_consumer="prod_cons.go"

# Java class names
JV_MAP_matrix_multiplication="Matmul"
JV_MAP_parallel_sort="ParallelSort"
JV_MAP_producer_consumer="ProdCons"

# ===========================================================
# RUNNER
# ===========================================================
run_cmd () {
    local lang=$1
    local workload=$2
    local threads=$3

    echo "[RUN] $lang | $workload | p=$threads"

    if [[ "$lang" == "python" ]]; then
        cd "$BENCH_DIR/src_python"
        file=$(eval echo "\$PY_MAP_${workload}")
        THREADS=$threads python3 "$file" >> "$RAW_LOG"

    elif [[ "$lang" == "rust" ]]; then
        cd "$BENCH_DIR/src_rust"
        cargo build --release >/dev/null 2>&1
        bin=$(eval echo "\$RS_MAP_${workload}")
        THREADS=$threads "./target/release/${bin}" >> "$RAW_LOG"

    elif [[ "$lang" == "go" ]]; then
        cd "$BENCH_DIR/src_go"
        file=$(eval echo "\$GO_MAP_${workload}")
        THREADS=$threads go run "$file" >> "$RAW_LOG"

    elif [[ "$lang" == "java" ]]; then
        cd "$BENCH_DIR/src_java"
        javac *.java >/dev/null 2>&1
        class=$(eval echo "\$JV_MAP_${workload}")
        THREADS=$threads java "$class" >> "$RAW_LOG"
    fi
}

# ===========================================================
# MAIN LOOP — 48 CONFIGS
# ===========================================================
for lang in "${LANGS[@]}"; do
    for workload in "${WORKLOADS[@]}"; do
        for threads in "${THREADS_LIST[@]}"; do
            run_cmd "$lang" "$workload" "$threads"
        done
    done
done

echo ""
echo "=== Phase 1 Completed at $(timestamp) ==="
echo "Output saved to $RAW_LOG"
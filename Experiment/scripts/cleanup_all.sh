#!/bin/bash

ROOT_DIR="/home/mole/penelitian1/Experiment"
BENCH_DIR="$ROOT_DIR/benchmark"

cleanup_all() {
    echo "[CLEAN] Full environment cleanup..."

    # Java
    find "$BENCH_DIR/src_java" -name "*.class" -delete

    # Rust
    cd "$BENCH_DIR/src_rust"
    cargo clean >/dev/null 2>&1

    # Go
    go clean -cache >/dev/null 2>&1

    echo "[CLEAN] Done."
    echo ""
}

cleanup_all

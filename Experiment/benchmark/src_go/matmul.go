package main

import (
    "encoding/json"
    "fmt"
    "os"
    "time"
)

const N = 1024

func worker(A, B, C [][]int, sr, er int, done chan bool) {
    for i := sr; i < er; i++ {
        for j := 0; j < N; j++ {
            s := 0
            for k := 0; k < N; k++ {
                s += A[i][k] * B[k][j]
            }
            C[i][j] = s
        }
    }
    done <- true
}

func main() {
    threads := 1
    fmt.Sscanf(os.Getenv("THREADS"), "%d", &threads)

    A := make([][]int, N)
    B := make([][]int, N)
    C := make([][]int, N)
    for i := 0; i < N; i++ {
        A[i] = make([]int, N)
        B[i] = make([]int, N)
        C[i] = make([]int, N)
        for j := 0; j < N; j++ {
            A[i][j] = 1
            B[i][j] = 1
        }
    }

    start := time.Now()
    chunk := N / threads
    done := make(chan bool)

    for t := 0; t < threads; t++ {
        sr := t * chunk
        er := (t + 1) * chunk
        go worker(A, B, C, sr, er, done)
    }
    for t := 0; t < threads; t++ { <-done }

    elapsed := time.Since(start).Seconds()

    out := map[string]interface{}{
        "language":    "go",
        "workload":    "matrix_multiplication",
        "threads":     threads,
        "run":         1,
        "elapsed_s":   elapsed,
        "peak_rss_kb": 0,
        "cpu_pct":     0.0,
    }
    b, _ := json.Marshal(out)
    fmt.Println(string(b))
}
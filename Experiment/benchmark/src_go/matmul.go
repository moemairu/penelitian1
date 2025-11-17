package main

import (
    "encoding/json"
    "fmt"
    "os"
    "strconv"
    "runtime"
)

const N = 1024

func getThreads() int {
    s := os.Getenv("THREADS")
    n, err := strconv.Atoi(s)
    if err != nil || n < 1 {
        return 1
    }
    return n
}

func worker(A, B, C [][]int, sr, er int, done chan bool) {
    for i := sr; i < er; i++ {
        row := A[i]
        for j := 0; j < N; j++ {
            s := 0
            for k := 0; k < N; k++ {
                s += row[k] * B[k][j]
            }
            C[i][j] = s
        }
    }
    done <- true
}

func main() {
    threads := getThreads()
    runtime.GOMAXPROCS(threads)

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

    chunk := N / threads
    done := make(chan bool, threads)

    for t := 0; t < threads; t++ {
        sr := t * chunk
        er := (t + 1) * chunk
        go worker(A, B, C, sr, er, done)
    }
    for t := 0; t < threads; t++ { <-done }

    out := map[string]interface{}{
        "language": "go",
        "workload": "matrix_multiplication",
        "threads":  threads,
    }
    b, _ := json.Marshal(out)
    fmt.Println(string(b))
}
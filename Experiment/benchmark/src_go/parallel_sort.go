package main

import (
    "encoding/json"
    "fmt"
    "os"
    "time"
)

func merge(a, b []int) []int {
    out := make([]int, 0, len(a)+len(b))
    i, j := 0, 0
    for i < len(a) && j < len(b) {
        if a[i] <= b[j] {
            out = append(out, a[i]); i++
        } else {
            out = append(out, b[j]); j++
        }
    }
    out = append(out, a[i:]...)
    out = append(out, b[j:]...)
    return out
}

func mergeSort(arr []int) []int {
    if len(arr) <= 1 { return arr }
    mid := len(arr)/2
    left := mergeSort(arr[:mid])
    right := mergeSort(arr[mid:])
    return merge(left,right)
}

func parallelMerge(arr []int, depth int) []int {
    if depth == 0 || len(arr)<=1 {
        return mergeSort(arr)
    }
    mid := len(arr)/2
    left := arr[:mid]
    right := arr[mid:]

    ch := make(chan []int)
    go func() { ch <- parallelMerge(left, depth-1) }()
    rightS := parallelMerge(right, depth-1)
    leftS := <-ch

    return merge(leftS,rightS)
}

func main() {
    threads := 1
    fmt.Sscanf(os.Getenv("THREADS"), "%d", &threads)
    depth := 0
    for (1<<depth) < threads { depth++ }

    arr := make([]int,1_000_000)
    for i:=0;i<1_000_000;i++ { arr[i] = 1_000_000-i }

    start := time.Now()
    _ = parallelMerge(arr, depth)
    elapsed := time.Since(start).Seconds()

    out := map[string]interface{}{
        "language": "go",
        "workload": "parallel_sort",
        "threads": threads,
        "run": 1,
        "elapsed_s": elapsed,
        "peak_rss_kb": 0,
        "cpu_pct": 0.0,
    }
    b,_ := json.Marshal(out)
    fmt.Println(string(b))
}
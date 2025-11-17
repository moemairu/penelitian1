package main

import (
    "encoding/json"
    "fmt"
    "os"
    "strconv"
    "runtime"
)

func getThreads() int {
    s := os.Getenv("THREADS")
    n, err := strconv.Atoi(s)
    if err != nil || n < 1 {
        return 1
    }
    return n
}

func producer(ch chan<- int, count int) {
    for i := 0; i < count; i++ {
        ch <- 1
    }
}

func consumer(ch <-chan int, count int, done chan bool) {
    for i := 0; i < count; i++ {
        <-ch
    }
    done <- true
}

func main() {
    threads := getThreads()
    runtime.GOMAXPROCS(threads)

    // FIXED to match Rust/Java/Python
    producers := 4
    consumers := 4
    total := 1_000_000
    perProd := total / producers
    perCons := total / consumers

    ch := make(chan int, 1024)
    done := make(chan bool, consumers)

    for i := 0; i < producers; i++ {
        go producer(ch, perProd)
    }

    for i := 0; i < consumers; i++ {
        go consumer(ch, perCons, done)
    }

    for i := 0; i < consumers; i++ { <-done }

    out := map[string]interface{}{
        "language": "go",
        "workload": "producer_consumer",
        "threads":  threads,
    }
    b, _ := json.Marshal(out)
    fmt.Println(string(b))
}
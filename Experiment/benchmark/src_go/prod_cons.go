package main

import (
    "encoding/json"
    "fmt"
    "os"
    "time"
)

func producer(ch chan<- int, count int) {
    for i := 0; i < count; i++ { ch <- 1 }
}

func consumer(ch <-chan int, count int, done chan bool) {
    processed := 0
    for processed < count {
        <-ch
        processed++
    }
    done <- true
}

func main() {
    producers := 4
    consumers := 4
    perProd := 250000
    total := producers * perProd
    threads := producers+consumers

    ch := make(chan int,1024)
    done := make(chan bool)

    start := time.Now()

    for i := 0; i < producers; i++ {
        go producer(ch, perProd)
    }
    for i := 0; i < consumers; i++ {
        go consumer(ch, total/consumers, done)
    }

    for i := 0; i < consumers; i++ { <-done }

    elapsed := time.Since(start).Seconds()

    out := map[string]interface{}{
        "language":"go",
        "workload":"producer_consumer",
        "threads":threads,
        "run":1,
        "elapsed_s":elapsed,
        "peak_rss_kb":0,
        "cpu_pct":0.0,
    }
    b,_ := json.Marshal(out)
    fmt.Println(string(b))
}
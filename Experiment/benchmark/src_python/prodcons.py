import time, json, os, multiprocessing as mp

def producer(q, count):
    for _ in range(count):
        q.put(1)

def consumer(q, count):
    processed = 0
    while processed < count:
        q.get()
        processed += 1

def main():
    threads = int(os.environ.get("THREADS", "1"))
    language = "python"
    workload = "producer_consumer"

    producers = 4
    consumers = 4
    per_prod = 250_000
    total = producers * per_prod

    q = mp.Queue(maxsize=1024)
    processes = []

    start = time.time()

    for _ in range(producers):
        processes.append(mp.Process(target=producer, args=(q,per_prod)))
    for _ in range(consumers):
        processes.append(mp.Process(target=consumer, args=(q,total//consumers)))

    for p in processes: p.start()
    for p in processes: p.join()

    elapsed = time.time()-start

    print(json.dumps({
        "language": language,
        "workload": workload,
        "threads": threads,
        "run": 1,
        "elapsed_s": elapsed,
        "peak_rss_kb": 0,
        "cpu_pct": 0.0
    }))

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# prodcons.py
# producer-consumer using multiprocessing.Queue
# prints only minimal json at end

import os
import time
import json
import multiprocessing as mp

def get_threads():
    try:
        t = int(os.getenv("THREADS", "1"))
        return max(1, t)
    except:
        return 1

def producer(q, count):
    for _ in range(count):
        q.put(1)

def consumer(q, count):
    processed = 0
    while processed < count:
        _ = q.get()
        processed += 1

def main():
    threads = get_threads()

    # split threads between producers and consumers fairly
    producers = max(1, threads // 2)
    consumers = max(1, threads - producers)
    total_msgs = 1_000_000
    per_prod = total_msgs // producers
    per_cons = total_msgs // consumers

    q = mp.Queue(maxsize=1024)
    procs = []

    start = time.time()
    for _ in range(producers):
        p = mp.Process(target=producer, args=(q, per_prod))
        p.start()
        procs.append(p)
    for _ in range(consumers):
        p = mp.Process(target=consumer, args=(q, per_cons))
        p.start()
        procs.append(p)

    for p in procs:
        p.join()
    elapsed = time.time() - start

    out = {"language": "python", "workload": "producer_consumer", "threads": threads}
    print(json.dumps(out))

if __name__ == "__main__":
    # try to use fork on linux to reduce startup cost if possible
    try:
        mp.set_start_method("fork")
    except Exception:
        pass
    main()
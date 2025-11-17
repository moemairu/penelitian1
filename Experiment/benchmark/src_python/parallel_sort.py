#!/usr/bin/env python3
# parallel_sort.py
# parallel merge sort using ProcessPoolExecutor
# prints only minimal json at end

import os
import math
import json
import time
from concurrent.futures import ProcessPoolExecutor

def get_threads():
    try:
        t = int(os.getenv("THREADS", "1"))
        return max(1, t)
    except:
        return 1

def seq_merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = seq_merge_sort(arr[:mid])
    right = seq_merge_sort(arr[mid:])
    return merge(left, right)

def merge(a, b):
    out = []
    i = j = 0
    la, lb = len(a), len(b)
    while i < la and j < lb:
        if a[i] <= b[j]:
            out.append(a[i]); i += 1
        else:
            out.append(b[j]); j += 1
    if i < la:
        out.extend(a[i:])
    if j < lb:
        out.extend(b[j:])
    return out

def parallel_merge_sort(arr, depth, max_workers):
    # base
    if depth <= 0 or len(arr) <= 1:
        return seq_merge_sort(arr)

    mid = len(arr) // 2
    left = arr[:mid]
    right = arr[mid:]

    # spawn left in separate process, compute right here
    with ProcessPoolExecutor(max_workers=max_workers) as ex:
        left_future = ex.submit(parallel_merge_sort, left, depth - 1, max_workers)
        right_sorted = parallel_merge_sort(right, depth - 1, max_workers)
        left_sorted = left_future.result()
    return merge(left_sorted, right_sorted)

def main():
    threads = get_threads()
    # depth chosen so that 2^depth <= threads (tree parallelism)
    depth = 0
    while (1 << depth) <= max(1, threads):
        depth += 1
    depth = max(0, depth - 1)

    # prepare descending data (worst-case)
    n = 1_000_000
    arr = list(range(n, 0, -1))

    start = time.time()
    _ = parallel_merge_sort(arr, depth, max(1, threads))
    elapsed = time.time() - start

    out = {"language": "python", "workload": "parallel_sort", "threads": threads}
    print(json.dumps(out))

if __name__ == "__main__":
    main()
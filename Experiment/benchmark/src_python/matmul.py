#!/usr/bin/env python3
# matmul.py
# dense matrix multiplication using multiprocessing + shared memory
# prints only minimal json at end

import os
import time
import json
import multiprocessing as mp
from ctypes import c_int

N = 1024

def get_threads():
    try:
        t = int(os.getenv("THREADS", "1"))
        return max(1, t)
    except:
        return 1

def worker(a_arr, b_arr, c_arr, sr, er, n):
    # a_arr, b_arr, c_arr are multiprocessing.Array('i', n*n) flattened row-major
    for i in range(sr, er):
        for j in range(n):
            s = 0
            base_i = i * n
            for k in range(n):
                s += a_arr[base_i + k] * b_arr[k * n + j]
            c_arr[base_i + j] = s

def main():
    threads = get_threads()

    # create shared flat arrays (C int)
    size = N * N
    a_sh = mp.Array(c_int, size, lock=False)
    b_sh = mp.Array(c_int, size, lock=False)
    c_sh = mp.Array(c_int, size, lock=False)

    # initialize
    for i in range(N):
        base = i * N
        for j in range(N):
            a_sh[base + j] = 1
            b_sh[base + j] = 1
            c_sh[base + j] = 0

    chunk = N // threads
    procs = []

    start = time.time()
    for t in range(threads):
        sr = t * chunk
        er = (t + 1) * chunk if t != threads - 1 else N
        p = mp.Process(target=worker, args=(a_sh, b_sh, c_sh, sr, er, N))
        p.start()
        procs.append(p)

    for p in procs:
        p.join()
    elapsed = time.time() - start

    # only minimal json (no timings or memory)
    out = {"language": "python", "workload": "matrix_multiplication", "threads": threads}
    print(json.dumps(out))

if __name__ == "__main__":
    # prefer fork on linux for efficiency if available
    try:
        mp.set_start_method("fork")
    except Exception:
        pass
    main()
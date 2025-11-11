import argparse
import multiprocessing as mp
import numpy as np
import time
import os

def sort_chunk(chunk):
    return np.sort(chunk)

def merge_sorted_arrays(arrays):
    """Merge sorted arrays into one (simple merge step)"""
    return np.concatenate(arrays)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=1000000, help="array size")
    parser.add_argument("--threads", type=int, default=os.cpu_count(), help="number of processes")
    args = parser.parse_args()

    n = args.n
    p = args.threads

    np.random.seed(42)
    data = np.random.randint(0, 10**6, size=n)

    chunks = np.array_split(data, p)

    start = time.perf_counter()
    with mp.Pool(processes=p) as pool:
        sorted_chunks = pool.map(sort_chunk, chunks)
    merged = merge_sorted_arrays(sorted_chunks)
    end = time.perf_counter()

    elapsed = end - start
    checksum = int(np.sum(merged[:100]))  # buat validasi kecil aja

    print(f"Array size: {n}")
    print(f"Processes: {p}")
    print(f"Elapsed time (s): {elapsed:.6f}")
    print(f"Checksum: {checksum}")

if __name__ == "__main__":
    mp.set_start_method("spawn")
    main()

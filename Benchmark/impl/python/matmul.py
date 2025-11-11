import argparse
import multiprocessing as mp
import time
import numpy as np
import os

def worker(task):
    """Worker function: perform partial matrix multiplication"""
    A_slice, B = task
    return np.dot(A_slice, B)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=512, help="matrix size NxN")
    parser.add_argument("--threads", type=int, default=os.cpu_count(), help="number of processes")
    args = parser.parse_args()

    n = args.n
    p = args.threads

    # --- Generate matrices ---
    np.random.seed(42)
    A = np.random.rand(n, n).astype(np.float64)
    B = np.random.rand(n, n).astype(np.float64)

    # --- Split A into p chunks by rows ---
    chunks = np.array_split(A, p, axis=0)

    start = time.perf_counter()

    with mp.Pool(processes=p) as pool:
        results = pool.map(worker, [(chunk, B) for chunk in chunks])

    C = np.vstack(results)

    end = time.perf_counter()

    # --- Output benchmark metrics ---
    elapsed = end - start
    checksum = np.sum(C)

    print(f"Matrix size: {n}x{n}")
    print(f"Processes: {p}")
    print(f"Elapsed time (s): {elapsed:.6f}")
    print(f"Checksum: {checksum:.6f}")

if __name__ == "__main__":
    mp.set_start_method("spawn")
    main()

import time, json, os, multiprocessing as mp

N = 1024

def worker_matmul(args):
    A, B, start_r, end_r = args
    C_part = []
    for i in range(start_r, end_r):
        row = [0] * N
        for j in range(N):
            s = 0
            for k in range(N):
                s += A[i][k] * B[k][j]
            row[j] = s
        C_part.append((i, row))
    return C_part

def main():
    threads = int(os.environ.get("THREADS", "1"))
    language = "python"
    workload = "matrix_multiplication"

    # init matrices
    A = [[1 for _ in range(N)] for _ in range(N)]
    B = [[1 for _ in range(N)] for _ in range(N)]

    start = time.time()
    chunk = N // threads

    args = []
    for t in range(threads):
        sr = t * chunk
        er = (t+1) * chunk
        args.append((A, B, sr, er))

    with mp.Pool(threads) as p:
        parts = p.map(worker_matmul, args)

    elapsed = time.time() - start

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
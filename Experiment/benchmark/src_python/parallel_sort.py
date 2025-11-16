import time, json, os, multiprocessing as mp

def merge(left, right):
    out = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i]); i+=1
        else:
            out.append(right[j]); j+=1
    out.extend(left[i:])
    out.extend(right[j:])
    return out

def seq_merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr)//2
    left = seq_merge_sort(arr[:mid])
    right = seq_merge_sort(arr[mid:])
    return merge(left,right)

def parallel_merge_sort(arr, depth):
    if depth == 0 or len(arr) <= 1:
        return seq_merge_sort(arr)

    mid = len(arr)//2
    left = arr[:mid]
    right = arr[mid:]

    with mp.Pool(2) as p:
        left_s, right_s = p.map(seq_merge_sort, [left, right])

    return merge(left_s, right_s)

def main():
    threads = int(os.environ.get("THREADS", "1"))
    language = "python"
    workload = "parallel_sort"

    depth = max(0, threads.bit_length()-1)

    arr = list(range(1000000,0,-1))  # descending

    start = time.time()
    sorted_arr = parallel_merge_sort(arr, depth)
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
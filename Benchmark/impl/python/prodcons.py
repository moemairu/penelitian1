import argparse
import multiprocessing as mp
import queue
import time
import os

def producer(q, count):
    for i in range(count):
        q.put(i)
    q.put(None)  # tanda selesai

def consumer(q, result_queue):
    total = 0
    while True:
        item = q.get()
        if item is None:
            break
        total += item
    result_queue.put(total)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--messages", type=int, default=100000, help="jumlah pesan total")
    parser.add_argument("--producers", type=int, default=2, help="jumlah producer")
    parser.add_argument("--consumers", type=int, default=2, help="jumlah consumer")
    args = parser.parse_args()

    msg_per_prod = args.messages // args.producers
    q = mp.Queue(maxsize=1000)
    result_q = mp.Queue()

    producers = [mp.Process(target=producer, args=(q, msg_per_prod)) for _ in range(args.producers)]
    consumers = [mp.Process(target=consumer, args=(q, result_q)) for _ in range(args.consumers)]

    start = time.perf_counter()
    for p in producers + consumers:
        p.start()
    for p in producers + consumers:
        p.join()
    end = time.perf_counter()

    # ambil hasil
    total_sum = 0
    while not result_q.empty():
        total_sum += result_q.get()

    elapsed = end - start
    print(f"Producers: {args.producers}, Consumers: {args.consumers}")
    print(f"Messages: {args.messages}")
    print(f"Elapsed time (s): {elapsed:.6f}")
    print(f"Checksum: {total_sum}")

if __name__ == "__main__":
    mp.set_start_method("spawn")
    main()

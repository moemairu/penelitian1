# Penelitian Benchmark Modern Programming Language
Judul Penelitian:
## An Experimental Performance Evaluation of Concurrency and Parallelism in Modern Programming Languages

> Penelitian ini mengevaluasi performa concurrency (eksekusi bersamaan) dan parallelism (pemrosesan paralel) pada empat bahasa pemrograman modern: Go, Rust, Java, dan Python. Menggunakan benchmark standar seperti matrix multiplication dan parallel sorting, kami mengukur metrik seperti waktu eksekusi, penggunaan CPU, konsumsi memori, dan skalabilitas pada multi-core processor.

### Abstract:
> The primary objective of this study is to evaluate and compare the concurrency performance of four modern programming languages—Go, Rust, Java, and Python—under a unified and reproducible experimental setting. As multicore hardware becomes ubiquitous, understanding how different runtime models utilize parallel resources is essential for selecting efficient tools for concurrent system development. The research employs a controlled two-phase benchmarking design. Phase 1 performs a full scalability sweep using representative compute-bound, memory-bound, and synchronization-bound workloads, executed with multiple worker configurations to identify each language’s most effective parallel operating point. Phase 2 conducts deep replication on the sequential baseline and the selected optimal configuration, enabling high-confidence estimation of execution time, speedup, efficiency, CPU utilization, memory footprint, and runtime stability. The results reveal clear distinctions in parallel performance. Rust achieves the highest speedup, efficiency, and stability across workloads, driven by its deterministic concurrency model and low overhead. Java performs strongly in compute-heavy scenarios but experiences degradation under memory and synchronization load. Go provides balanced and predictable performance, scaling well across workload types with moderate overhead. Python shows limited scalability due to multiprocessing and inter-process communication overhead, though it benefits modestly in compute-intensive tasks. Overall, the study concludes that language runtime design strongly influences parallel scalability. Rust is most suitable for high-performance parallel tasks; Go offers general-purpose concurrency with stable behavior; Java is effective for compute-bound workloads; and Python is least efficient for fine-grained parallelism.

Penulis:
Ismail Faruqy

Start:
September 2025

Finish:
November 2025

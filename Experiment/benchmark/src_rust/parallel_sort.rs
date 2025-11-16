use std::thread;
use std::time::Instant;

fn merge(left: Vec<i32>, right: Vec<i32>) -> Vec<i32> {
    let mut out = Vec::with_capacity(left.len() + right.len());
    let (mut i, mut j) = (0, 0);

    while i < left.len() && j < right.len() {
        if left[i] <= right[j] {
            out.push(left[i]);
            i += 1;
        } else {
            out.push(right[j]);
            j += 1;
        }
    }
    out.extend_from_slice(&left[i..]);
    out.extend_from_slice(&right[j..]);
    out
}

fn seq_merge_sort(mut arr: Vec<i32>) -> Vec<i32> {
    if arr.len() <= 1 { return arr; }
    let mid = arr.len() / 2;
    let left = seq_merge_sort(arr[..mid].to_vec());
    let right = seq_merge_sort(arr[mid..].to_vec());
    merge(left, right)
}

fn parallel_merge_sort(arr: Vec<i32>, depth: usize) -> Vec<i32> {
    if depth == 0 || arr.len() <= 1 {
        return seq_merge_sort(arr);
    }

    let mid = arr.len() / 2;
    let left = arr[..mid].to_vec();
    let right = arr[mid..].to_vec();

    // ---------- PARALLEL BRANCH ----------
    let handle = thread::spawn(move || parallel_merge_sort(left, depth - 1));
    let right_sorted = parallel_merge_sort(right, depth - 1);
    let left_sorted = handle.join().unwrap();

    merge(left_sorted, right_sorted)
}

fn main() {
    let threads: usize = std::env::var("THREADS").unwrap().parse().unwrap();
    let depth = (threads as f64).log2().floor() as usize;

    let mut arr = Vec::new();
    for i in (0..1_000_000).rev() {
        arr.push(i);
    }

    let start = Instant::now();
    let _ = parallel_merge_sort(arr, depth);
    let elapsed = start.elapsed().as_secs_f64();

    println!(
        "{{\"language\":\"rust\",\"workload\":\"parallel_sort\",\"threads\":{},\
         \"run\":1,\"elapsed_s\":{},\"peak_rss_kb\":0,\"cpu_pct\":0.0}}",
        threads, elapsed
    );
}
use std::sync::Arc;
use std::thread;
use std::time::Instant;

fn merge(a: &[i32], b: &[i32]) -> Vec<i32> {
    let mut out = Vec::with_capacity(a.len() + b.len());
    let (mut i, mut j) = (0, 0);

    while i < a.len() && j < b.len() {
        if a[i] <= b[j] {
            out.push(a[i]);
            i += 1;
        } else {
            out.push(b[j]);
            j += 1;
        }
    }
    out.extend_from_slice(&a[i..]);
    out.extend_from_slice(&b[j..]);
    out
}

fn seq_sort(v: &[i32]) -> Vec<i32> {
    if v.len() <= 1 {
        return v.to_vec();
    }
    let mid = v.len() / 2;
    let left = seq_sort(&v[..mid]);
    let right = seq_sort(&v[mid..]);
    merge(&left, &right)
}

fn parallel_sort(data: Arc<[i32]>, depth: usize) -> Vec<i32> {
    if depth == 0 || data.len() <= 1 {
        return seq_sort(&data);
    }

    let mid = data.len() / 2;
    let left_arc: Arc<[i32]> = Arc::from(&data[..mid]);
    let right_arc: Arc<[i32]> = Arc::from(&data[mid..]);

    // parallel branch
    let handle = thread::spawn(move || parallel_sort(left_arc, depth - 1));
    let right_sorted = parallel_sort(right_arc, depth - 1);
    let left_sorted = handle.join().unwrap();

    merge(&left_sorted, &right_sorted)
}

fn main() {
    let threads: usize = std::env::var("THREADS")
        .unwrap_or("1".to_string())
        .parse()
        .unwrap_or(1);

    // depth = floor(log2(threads))
    let mut depth: usize = 0;
    while (1 << depth) < threads {
        depth += 1;
    }
    if depth > 0 {
        depth -= 1;
    }

    // generate array
    let mut tmp = Vec::with_capacity(1_000_000);
    for i in (0..1_000_000).rev() {
        tmp.push(i);
    }

    let arr = Arc::from(tmp.into_boxed_slice());

    let start = Instant::now();
    let _sorted = parallel_sort(arr, depth);
    let _elapsed = start.elapsed().as_secs_f64();

    println!(
        "{{\"language\":\"rust\",\"workload\":\"parallel_sort\",\"threads\":{}}}",
        threads
    );
}
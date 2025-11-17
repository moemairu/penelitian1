use std::env;
use std::sync::Arc;
use std::thread;

const N: usize = 1024;

fn main() {
    let threads: usize = env::var("THREADS")
        .unwrap_or("1".to_string())
        .parse()
        .unwrap_or(1);

    let a = Arc::new(vec![vec![1_i32; N]; N]);
    let b = Arc::new(vec![vec![1_i32; N]; N]);

    let chunk = N / threads;

    let mut handles = Vec::new();

    // allocate final matrix C (will be filled after join)
    let mut c = vec![vec![0_i32; N]; N];

    for t in 0..threads {
        let a_cl = Arc::clone(&a);
        let b_cl = Arc::clone(&b);

        let sr = t * chunk;
        let er = if t == threads - 1 { N } else { (t + 1) * chunk };

        // each thread computes its own partial C
        handles.push(thread::spawn(move || {
            let mut local_c = vec![vec![0_i32; N]; er - sr];

            for (local_i, i) in (sr..er).enumerate() {
                for j in 0..N {
                    let mut sum = 0;
                    for k in 0..N {
                        sum += a_cl[i][k] * b_cl[k][j];
                    }
                    local_c[local_i][j] = sum;
                }
            }
            (sr, er, local_c)
        }));
    }

    // merge results back
    for h in handles {
        let (sr, er, partial) = h.join().unwrap();
        for (local_i, i) in (sr..er).enumerate() {
            c[i] = partial[local_i].clone();
        }
    }

    println!(
        "{{\"language\":\"rust\",\"workload\":\"matrix_multiplication\",\"threads\":{}}}",
        threads
    );
}
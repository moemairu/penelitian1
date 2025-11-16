use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Instant;

const N: usize = 1024;

fn main() {
    let threads: usize = std::env::var("THREADS").unwrap().parse().unwrap();

    // init matrices
    let mut A = vec![vec![1_i32; N]; N];
    let mut B = vec![vec![1_i32; N]; N];
    let C = Arc::new(Mutex::new(vec![vec![0_i32; N]; N]));

    let chunk = N / threads;

    let start = Instant::now();

    let mut handles = vec![];

    for t in 0..threads {
        let A_cl = A.clone();
        let B_cl = B.clone();
        let C_cl = Arc::clone(&C);

        let sr = t * chunk;
        let er = (t + 1) * chunk;

        let handle = thread::spawn(move || {
            for i in sr..er {
                for j in 0..N {
                    let mut s = 0;
                    for k in 0..N {
                        s += A_cl[i][k] * B_cl[k][j];
                    }
                    C_cl.lock().unwrap()[i][j] = s;
                }
            }
        });
        handles.push(handle);
    }

    for h in handles {
        h.join().unwrap();
    }

    let elapsed = start.elapsed().as_secs_f64();

    println!(
        "{{\"language\":\"rust\",\"workload\":\"matrix_multiplication\",\"threads\":{},\
         \"run\":1,\"elapsed_s\":{},\"peak_rss_kb\":0,\"cpu_pct\":0.0}}",
        threads, elapsed
    );
}
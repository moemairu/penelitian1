use std::env;
use std::sync::{Arc, Mutex, mpsc};
use std::thread;

fn producer(tx: mpsc::SyncSender<i32>, count: usize) {
    for _ in 0..count {
        tx.send(1).unwrap();
    }
}

fn consumer(rx: Arc<Mutex<mpsc::Receiver<i32>>>, count: usize) {
    for _ in 0..count {
        let _ = rx.lock().unwrap().recv().unwrap();
    }
}

fn main() {
    let threads: usize = env::var("THREADS")
        .unwrap_or("1".to_string())
        .parse()
        .unwrap_or(1);

    let producers = std::cmp::max(1, threads / 2);
    let consumers = std::cmp::max(1, threads - producers);

    let total = 1_000_000usize;
    let per_prod = total / producers;
    let per_cons = total / consumers;

    let (tx, rx) = mpsc::sync_channel::<i32>(1024);
    let rx = Arc::new(Mutex::new(rx));

    let mut handles = vec![];

    for _ in 0..producers {
        let txc = tx.clone();
        handles.push(thread::spawn(move || producer(txc, per_prod)));
    }

    for _ in 0..consumers {
        let rc = Arc::clone(&rx);
        handles.push(thread::spawn(move || consumer(rc, per_cons)));
    }

    for h in handles {
        h.join().unwrap();
    }

    println!(
        "{{\"language\":\"rust\",\"workload\":\"producer_consumer\",\"threads\":{}}}",
        threads
    );
}
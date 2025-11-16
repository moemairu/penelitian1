use std::sync::{Arc, mpsc};
use std::thread;
use std::time::Instant;

fn producer(tx: mpsc::SyncSender<i32>, count: usize) {
    for _ in 0..count {
        tx.send(1).unwrap();
    }
}

fn consumer(rx: Arc<mpsc::Receiver<i32>>, count: usize) {
    let mut processed = 0;
    while processed < count {
        let _ = rx.recv().unwrap();
        processed += 1;
    }
}

fn main() {
    let producers = 4;
    let consumers = 4;
    let per_prod = 250_000usize;
    let total = producers * per_prod;

    let (tx, rx) = mpsc::sync_channel::<i32>(1024);
    let rx = Arc::new(rx);

    let mut handles = vec![];

    let start = Instant::now();

    // producers
    for _ in 0..producers {
        let txc = tx.clone();
        handles.push(thread::spawn(move || producer(txc, per_prod)));
    }

    // consumers
    for _ in 0..consumers {
        let rc = Arc::clone(&rx);
        handles.push(thread::spawn(move || consumer(rc, total / consumers)));
    }

    for h in handles { h.join().unwrap(); }

    let elapsed = start.elapsed().as_secs_f64();

    println!(
        "{{\"language\":\"rust\",\"workload\":\"producer_consumer\",\"threads\":{},\
         \"run\":1,\"elapsed_s\":{},\"peak_rss_kb\":0,\"cpu_pct\":0.0}}",
        producers + consumers,
        elapsed
    );
}
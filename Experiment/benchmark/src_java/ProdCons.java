import java.util.concurrent.*;

public class ProdCons {
    public static void main(String[] args) throws Exception {

        int threads = Integer.parseInt(System.getenv().getOrDefault("THREADS", "1"));

        int producers = threads / 2;
        int consumers = threads - producers;
        if (producers < 1) producers = 1;
        if (consumers < 1) consumers = 1;

        int totalMsgs = 1_000_000;
        int perProd = totalMsgs / producers;
        int perCons = totalMsgs / consumers;

        // FIX: pool must have >= producers + consumers
        int poolSize = Math.max(threads, 2);
        ExecutorService pool = Executors.newFixedThreadPool(poolSize);

        BlockingQueue<Integer> q = new ArrayBlockingQueue<>(1024);

        for (int i = 0; i < producers; i++) {
            pool.submit(() -> {
                try {
                    for (int n = 0; n < perProd; n++) q.put(1);
                } catch (Exception e) {}
            });
        }

        for (int i = 0; i < consumers; i++) {
            pool.submit(() -> {
                int processed = 0;
                try {
                    while (processed < perCons) {
                        q.take();
                        processed++;
                    }
                } catch (Exception e) {}
            });
        }

        pool.shutdown();
        pool.awaitTermination(5, TimeUnit.HOURS);

        System.out.println(
            "{\"language\":\"java\",\"workload\":\"producer_consumer\",\"threads\":"+threads+"}"
        );
    }
}
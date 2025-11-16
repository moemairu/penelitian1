import java.util.concurrent.*;

public class ProdCons {
    public static void main(String[] args) throws Exception {

        int producers = 4;
        int consumers = 4;
        int perProd = 250_000;
        int total = producers*perProd;

        BlockingQueue<Integer> q = new ArrayBlockingQueue<>(1024);
        ExecutorService pool = Executors.newFixedThreadPool(producers+consumers);

        long start = System.nanoTime();

        // producers
        for(int i=0;i<producers;i++){
            pool.submit(() -> {
                for(int n=0;n<perProd;n++){
                    try { q.put(1);} catch(Exception e){}
                }
            });
        }

        // consumers
        for(int i=0;i<consumers;i++){
            pool.submit(() -> {
                int processed=0;
                while(processed < total/consumers){
                    try{ q.take(); } catch(Exception e){}
                    processed++;
                }
            });
        }

        pool.shutdown();
        pool.awaitTermination(5,TimeUnit.HOURS);

        double elapsed = (System.nanoTime()-start)/1e9;

        System.out.println("{\"language\":\"java\",\"workload\":\"producer_consumer\",\"threads\":"+
            (producers+consumers)+",\"run\":1,\"elapsed_s\":"+elapsed+
            ",\"peak_rss_kb\":0,\"cpu_pct\":0.0}");
    }
}
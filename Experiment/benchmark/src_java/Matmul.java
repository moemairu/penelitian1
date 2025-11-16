import java.util.*;
import java.util.concurrent.*;

public class Matmul {
    static final int N = 1024;

    public static void main(String[] args) throws Exception {
        int threads = Integer.parseInt(System.getenv("THREADS"));
        ExecutorService pool = Executors.newFixedThreadPool(threads);

        int[][] A = new int[N][N];
        int[][] B = new int[N][N];
        int[][] C = new int[N][N];

        for (int i=0;i<N;i++){
            for(int j=0;j<N;j++){
                A[i][j]=1; B[i][j]=1;
            }
        }

        int chunk = N / threads;

        long start = System.nanoTime();

        List<Future<?>> tasks = new ArrayList<>();

        for (int t=0; t<threads; t++){
            int sr = t*chunk;
            int er = (t+1)*chunk;

            tasks.add(pool.submit(() -> {
                for(int i=sr;i<er;i++){
                    for(int j=0;j<N;j++){
                        int s=0;
                        for(int k=0;k<N;k++)
                            s+=A[i][k]*B[k][j];
                        C[i][j]=s;
                    }
                }
            }));
        }

        for(Future<?> f: tasks) f.get();
        pool.shutdown();

        double elapsed = (System.nanoTime()-start)/1e9;

        System.out.println(
            "{\"language\":\"java\",\"workload\":\"matrix_multiplication\",\"threads\":"+threads+
            ",\"run\":1,\"elapsed_s\":"+elapsed+",\"peak_rss_kb\":0,\"cpu_pct\":0.0}"
        );
    }
}
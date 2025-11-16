import java.util.*;
import java.util.concurrent.*;

public class ParallelSort {

    static int[] merge(int[] a, int[] b) {
        int[] out = new int[a.length + b.length];
        int i=0,j=0,k=0;
        while (i<a.length && j<b.length) {
            if (a[i] <= b[j]) out[k++] = a[i++];
            else out[k++] = b[j++];
        }
        while(i<a.length) out[k++] = a[i++];
        while(j<b.length) out[k++] = b[j++];
        return out;
    }

    static int[] seqMergeSort(int[] arr){
        if(arr.length <= 1) return arr;
        int mid = arr.length/2;
        int[] left = seqMergeSort(Arrays.copyOfRange(arr,0,mid));
        int[] right = seqMergeSort(Arrays.copyOfRange(arr,mid,arr.length));
        return merge(left,right);
    }

    static int[] parallelMergeSort(int[] arr, int depth, ExecutorService pool) throws Exception {
        if (depth==0 || arr.length<=1) return seqMergeSort(arr);

        int mid=arr.length/2;
        int[] left = Arrays.copyOfRange(arr,0,mid);
        int[] right = Arrays.copyOfRange(arr,mid,arr.length);

        Future<int[]> leftF = pool.submit(() -> parallelMergeSort(left, depth-1, pool));
        int[] rightSorted = parallelMergeSort(right,depth-1,pool);
        int[] leftSorted = leftF.get();

        return merge(leftSorted,rightSorted);
    }

    public static void main(String[] args) throws Exception {
        int threads = Integer.parseInt(System.getenv("THREADS"));
        ExecutorService pool = Executors.newFixedThreadPool(threads);

        int[] arr = new int[1_000_000];
        for (int i=0;i<1_000_000;i++) arr[i] = 1_000_000 - i;

        int depth = (int)(Math.log(threads)/Math.log(2));

        long start = System.nanoTime();
        int[] sorted = parallelMergeSort(arr, depth, pool);
        double elapsed = (System.nanoTime()-start)/1e9;

        pool.shutdown();

        System.out.println("{\"language\":\"java\",\"workload\":\"parallel_sort\",\"threads\":"+threads+
            ",\"run\":1,\"elapsed_s\":"+elapsed+",\"peak_rss_kb\":0,\"cpu_pct\":0.0}");
    }
}
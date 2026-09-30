// Name: Ali Ghaffari
// Student number: S5270064

import java.util.ArrayList;
import java.util.Random;

class QueueAssigner {

    //a private ArrayList<Integer> field called free, created empty
    
    //a private Random field called rng, created

    public QueueAssigner(int numQueues) {
        //add the numbers 0 up to numQueues - 1 into free
        for (int i = 0; i < numQueues; i++) {
            free.add(i);
        }
        rng = new Random();
    }

    public synchronized int claim() {
        // pick a random position in free, store it in an int called pick
        int pick = rng.nextInt(free.size());
        // remove the number at that position from free, store it in an int called chosen
        int chosen = free.remove(pick);
        // wake all waiting threads
        notifyAll();
        // return chosen
        return chosen;
    }

    public synchronized void waitForAll() throws InterruptedException {
        // while free is not empty, wait
        while (!free.isEmpty()) {
            wait();
        }
    }
}
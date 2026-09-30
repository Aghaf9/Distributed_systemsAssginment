// Name: Ali Ghaffari
// Student number: S5270064

/**
 * A counting semaphore built from a Java monitor.
 */
class Semaphore {

    //declaring a private whole-number field called count
    private int count;

    public Semaphore(int initial) {
        //set count to initial
        this.count = initial;
    }

    public synchronized void acquire() throws InterruptedException {
        //while there are no tokens, wait
        while (this.count == 0) {
            wait();
        }
        //take a token
        this.count--;
    }

    public synchronized void release() {
        //add a token
        this.count++;
        //wake all waiting threads
        notifyAll();
    }

    public synchronized boolean tryAcquire() {
        //if there are no tokens, return false
        if (this.count == 0) {
            return false;
        }
        //otherwise take a token and return true
        this.count--;
        return true;
    }
}
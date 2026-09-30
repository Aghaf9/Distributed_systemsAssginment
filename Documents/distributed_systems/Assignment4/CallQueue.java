//Name: Ali Ghaffari
//Student number: S5270064

/**
 * One call queue, stored as a circular buffer and used as a deque:
 * callers add at the front (in), the owner takes from the back (out),
 * and thieves take from the front (in - 1).
 */
class CallQueue {

    //this is aprivate constant called SIZE, equal to 5
    private static final int SIZE = 5;

    //a private int array called buffer, with SIZE slots
    private int[] buffer = new int[SIZE];

    //private int fields in and out, both starting at 0
    private int in = 0;
    private int out = 0;

    //three private Semaphore fields, notEmpty, notFull, mutexFront
    private Semaphore notEmpty;
    private Semaphore notFull;
    private Semaphore mutexFront;

    //a private int field called id which queue this is 0, 1 or 2
    private int id;

    public CallQueue(int id) {
        //storing the id that was passed in
        this.id = id;

        //creating the three semaphores with their starting counts
        notEmpty = new Semaphore(0);
        notFull = new Semaphore(SIZE);
        mutexFront = new Semaphore(1);
    }
       

    public void addCall(int call) throws InterruptedException {
        //wait until there's a free slot              
        // (p2)
        notFull.acquire();
        //get permission to touch the front           
        // (p3)
        mutexFront.acquire();
        //put call into the buffer at position in     
        // (p4)
        buffer[in] = call;
        //move in forward by one, wrapping around     
        // (p5)
        in = (in + 1) % SIZE;

        //give back the front permission              
        // (p6)
        mutexFront.release();

        //signal that a call is now waiting           
        // (p7)
        notEmpty.release();
    }
        public int tryTakeOldest() {
        //takeing a call waiting token without waiting   
        // (q1)
        //if that fails, returning -1
        if (!notEmpty.tryAcquire()) {
            return -1;
        }


        //read the call pos out q2
        int call = buffer[out];
        //move out forward by one, wrapping around q3
        out = (out + 1) % SIZE;
        //signal that a slot is now free q4
        notFull.release();
        //return the call
        return call;
    }



    public int tryStealNewest() throws InterruptedException {
        //try to take a "call waiting" token without waiting;   
        // (r1)
        //if that fails, return -1
        if (!notEmpty.tryAcquire()) {
            return -1;
        }
        //get permission to touch the front                     
        // (r2)
        mutexFront.acquire();
        //move in BACK by one, wrapping around                  
        // (r3)
        in = (in - 1 + SIZE) % SIZE;
        //read the call at position in into a new int variable  
        // (r4)
        int call = buffer[in];
        //give back the front permission                        
        // (r5)
        mutexFront.release();
        //signal that a slot is now free                        
        // (r6)
        notFull.release();
        //return the call
        return call;
    }
}
class AcquireTest {
    public static void main(String[] args) throws InterruptedException {
        //creating a Semaphore with 0 tokens, called s
        Semaphore s = new Semaphore(0);         


        Thread waiter = new Thread(() -> {
            try {
                //printing waiter: trying to acquire
                System.out.println("waiter: trying to acquire");
                //acquiring a token from s
                s.acquire();
                //printing waiter: got the token
                System.out.println("waiter: got the token");
            } catch (InterruptedException e) {
                System.out.println("waiter was interrupted");
            }
        });

        //starting the waiter thread
        waiter.start();
        //making main sleep for 2000ms
        Thread.sleep(2000);
        //printing main: releasing
        System.out.println("main: releasing");
        //releasing a token
        s.release();
        //printing main: waiting for waiter to finish
        System.out.println("main: waiting for waiter to finish");
        //waiting for the waiter thread to finish
        waiter.join();
    }
}


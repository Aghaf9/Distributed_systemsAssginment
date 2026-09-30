class SemaphoreTest {
    public static void main(String[] args) {

        //createing a Semaphore with 2 tokens, stored in a variable called s
        Semaphore s = new Semaphore(2);

        //printing the result of s.tryAcquire(), three times
        System.out.println(s.tryAcquire());
        System.out.println(s.tryAcquire());
        System.out.println(s.tryAcquire());

        //releaseing one token
        s.release();

        //printing the result of s.tryAcquire() once more
        System.out.println(s.tryAcquire());
    }
}

 
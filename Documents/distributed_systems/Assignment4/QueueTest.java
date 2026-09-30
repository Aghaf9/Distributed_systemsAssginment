class QueueTest {
    public static void main(String[] args) throws InterruptedException {
        CallQueue q = new CallQueue(0);

        q.addCall(10);
        q.addCall(20);
        q.addCall(30);

        System.out.println(q.tryStealNewest());
        System.out.println(q.tryTakeOldest());

        q.addCall(40);
        q.addCall(50);
        q.addCall(60);
        q.addCall(70);

        System.out.println(q.tryStealNewest());
        System.out.println(q.tryStealNewest());
        System.out.println(q.tryTakeOldest());
        System.out.println(q.tryTakeOldest());
        System.out.println(q.tryTakeOldest());
        System.out.println(q.tryTakeOldest());
    }
}
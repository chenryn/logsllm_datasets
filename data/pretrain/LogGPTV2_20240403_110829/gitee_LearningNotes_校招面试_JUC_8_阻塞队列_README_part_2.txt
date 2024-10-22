            condition.signalAll();
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            lock.unlock();
        }
    }
    public void decrement() throws Exception{
        // 同步代码块，加锁
        lock.lock();
        try {
            // 判断
            while(number == 0) {
                // 等待不能消费
                condition.await();
            }
            // 干活
            number--;
            System.out.println(Thread.currentThread().getName() + "\t " + number);
            // 通知 唤醒
            condition.signalAll();
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            lock.unlock();
        }
    }
}
```
里面有一个number变量，同时提供了increment 和 decrement的方法，分别让number 加1和减1
但是我们在进行判断的时候，为了防止出现虚假唤醒机制，不能使用if来进行判断，而应该使用while
```
// 判断
while(number != 0) {
    // 等待不能生产
    condition.await();
}
```
不能使用 if判断
```
// 判断
if(number != 0) {
    // 等待不能生产
    condition.await();
}
```
完整代码
```
/**
 * 生产者消费者 传统版
 * 题目：一个初始值为0的变量，两个线程对其交替操作，一个加1，一个减1，来5轮
 * @author: 陌溪
 * @create: 2020-03-16-21:38
 */
/**
 * 线程 操作 资源类
 * 判断 干活 通知
 * 防止虚假唤醒机制
 */
/**
 * 资源类
 */
class ShareData {
    private int number = 0;
    private Lock lock = new ReentrantLock();
    private Condition condition = lock.newCondition();
    public void increment() throws Exception{
        // 同步代码块，加锁
        lock.lock();
        try {
            // 判断
            while(number != 0) {
                // 等待不能生产
                condition.await();
            }
            // 干活
            number++;
            System.out.println(Thread.currentThread().getName() + "\t " + number);
            // 通知 唤醒
            condition.signalAll();
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            lock.unlock();
        }
    }
    public void decrement() throws Exception{
        // 同步代码块，加锁
        lock.lock();
        try {
            // 判断
            while(number == 0) {
                // 等待不能消费
                condition.await();
            }
            // 干活
            number--;
            System.out.println(Thread.currentThread().getName() + "\t " + number);
            // 通知 唤醒
            condition.signalAll();
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            lock.unlock();
        }
    }
}
public class ProdConsumerTraditionDemo {
    public static void main(String[] args) {
        // 高内聚，低耦合    内聚指的是，一个空调，自身带有调节温度高低的方法
        ShareData shareData = new ShareData();
        // t1线程，生产
        new Thread(() -> {
            for (int i = 0; i  {
            for (int i = 0; i  blockingQueue = null;
    // 而应该采用依赖注入里面的，构造注入方法传入
    public MyResource(BlockingQueue blockingQueue) {
        this.blockingQueue = blockingQueue;
        // 查询出传入的class是什么
        System.out.println(blockingQueue.getClass().getName());
    }
    /**
     * 生产
     * @throws Exception
     */
    public void myProd() throws Exception{
        String data = null;
        boolean retValue;
        // 多线程环境的判断，一定要使用while进行，防止出现虚假唤醒
        // 当FLAG为true的时候，开始生产
        while(FLAG) {
            data = atomicInteger.incrementAndGet() + "";
            // 2秒存入1个data
            retValue = blockingQueue.offer(data, 2L, TimeUnit.SECONDS);
            if(retValue) {
                System.out.println(Thread.currentThread().getName() + "\t 插入队列:" + data  + "成功" );
            } else {
                System.out.println(Thread.currentThread().getName() + "\t 插入队列:" + data  + "失败" );
            }
            try {
                TimeUnit.SECONDS.sleep(1);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        System.out.println(Thread.currentThread().getName() + "\t 停止生产，表示FLAG=false，生产介绍");
    }
    /**
     * 消费
     * @throws Exception
     */
    public void myConsumer() throws Exception{
        String retValue;
        // 多线程环境的判断，一定要使用while进行，防止出现虚假唤醒
        // 当FLAG为true的时候，开始生产
        while(FLAG) {
            // 2秒存入1个data
            retValue = blockingQueue.poll(2L, TimeUnit.SECONDS);
            if(retValue != null && retValue != "") {
                System.out.println(Thread.currentThread().getName() + "\t 消费队列:" + retValue  + "成功" );
            } else {
                FLAG = false;
                System.out.println(Thread.currentThread().getName() + "\t 消费失败，队列中已为空，退出" );
                // 退出消费队列
                return;
            }
        }
    }
    /**
     * 停止生产的判断
     */
    public void stop() {
        this.FLAG = false;
    }
}
public class ProdConsumerBlockingQueueDemo {
    public static void main(String[] args) {
        // 传入具体的实现类， ArrayBlockingQueue
        MyResource myResource = new MyResource(new ArrayBlockingQueue(10));
        new Thread(() -> {
            System.out.println(Thread.currentThread().getName() + "\t 生产线程启动");
            System.out.println("");
            System.out.println("");
            try {
                myResource.myProd();
                System.out.println("");
                System.out.println("");
            } catch (Exception e) {
                e.printStackTrace();
            }
        }, "prod").start();
        new Thread(() -> {
            System.out.println(Thread.currentThread().getName() + "\t 消费线程启动");
            try {
                myResource.myConsumer();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }, "consumer").start();
        // 5秒后，停止生产和消费
        try {
            TimeUnit.SECONDS.sleep(5);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        System.out.println("");
        System.out.println("");
        System.out.println("5秒中后，生产和消费线程停止，线程结束");
        myResource.stop();
    }
}
```
最后运行结果
```
java.util.concurrent.ArrayBlockingQueue
prod	 生产线程启动
consumer	 消费线程启动
prod	 插入队列:1成功
consumer	 消费队列:1成功
prod	 插入队列:2成功
consumer	 消费队列:2成功
prod	 插入队列:3成功
consumer	 消费队列:3成功
prod	 插入队列:4成功
consumer	 消费队列:4成功
prod	 插入队列:5成功
consumer	 消费队列:5成功
5秒中后，生产和消费线程停止，线程结束
prod	 停止生产，表示FLAG=false，生产介绍
```
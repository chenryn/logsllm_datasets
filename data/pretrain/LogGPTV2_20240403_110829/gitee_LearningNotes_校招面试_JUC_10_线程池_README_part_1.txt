# 线程池（Java中有哪些方法获取多线程）
## 前言
获取多线程的方法，我们都知道有三种，还有一种是实现Callable接口
- 实现Runnable接口
- 实现Callable接口
- 实例化Thread类
- 使用线程池获取
## Callable接口
Callable接口，是一种让线程执行完成后，能够返回结果的
在说到Callable接口的时候，我们不得不提到Runnable接口
```
/**
 * 实现Runnable接口
 */
class MyThread implements Runnable {
    @Override
    public void run() {
    }
}
```
我们知道，实现Runnable接口的时候，需要重写run方法，也就是线程在启动的时候，会自动调用的方法
同理，我们实现Callable接口，也需要实现call方法，但是这个时候我们还需要有返回值，这个Callable接口的应用场景一般就在于批处理业务，比如转账的时候，需要给一会返回结果的状态码回来，代表本次操作成功还是失败
```
/**
 * Callable有返回值
 * 批量处理的时候，需要带返回值的接口（例如支付失败的时候，需要返回错误状态）
 *
 */
class MyThread2 implements Callable {
    @Override
    public Integer call() throws Exception {
        System.out.println("come in Callable");
        return 1024;
    }
}
```
最后我们需要做的就是通过Thread线程， 将MyThread2实现Callable接口的类包装起来
这里需要用到的是FutureTask类，他实现了Runnable接口，并且还需要传递一个实现Callable接口的类作为构造函数
```
// FutureTask：实现了Runnable接口，构造函数又需要传入 Callable接口
// 这里通过了FutureTask接触了Callable接口
FutureTask futureTask = new FutureTask<>(new MyThread2());
```
然后在用Thread进行实例化，传入实现Runnabnle接口的FutureTask的类
```
Thread t1 = new Thread(futureTask, "aaa");
t1.start();
```
最后通过 futureTask.get() 获取到返回值
```
// 输出FutureTask的返回值
System.out.println("result FutureTask " + futureTask.get());
```
这就相当于原来我们的方式是main方法一条龙之心，后面在引入Callable后，对于执行比较久的线程，可以单独新开一个线程进行执行，最后在进行汇总输出
最后需要注意的是 要求获得Callable线程的计算结果，如果没有计算完成就要去强求，会导致阻塞，直到计算完成
![image-20200317152541284](images/image-20200317152541284.png)
也就是说 futureTask.get() 需要放在最后执行，这样不会导致主线程阻塞
也可以使用下面算法，使用类似于自旋锁的方式来进行判断是否运行完毕
```
// 判断futureTask是否计算完成
while(!futureTask.isDone()) {
}
```
### 注意
多个线程执行 一个FutureTask的时候，只会计算一次
```
FutureTask futureTask = new FutureTask<>(new MyThread2());
// 开启两个线程计算futureTask
new Thread(futureTask, "AAA").start();
new Thread(futureTask, "BBB").start();
```
如果我们要两个线程同时计算任务的话，那么需要这样写，需要定义两个futureTask
```
FutureTask futureTask = new FutureTask<>(new MyThread2());
FutureTask futureTask2 = new FutureTask<>(new MyThread2());
// 开启两个线程计算futureTask
new Thread(futureTask, "AAA").start();
new Thread(futureTask2, "BBB").start();
```
## ThreadPoolExecutor
### 为什么用线程池
线程池做的主要工作就是控制运行的线程的数量，处理过程中，将任务放入到队列中，然后线程创建后，启动这些任务，如果线程数量超过了最大数量的线程排队等候，等其它线程执行完毕，再从队列中取出任务来执行。
它的主要特点为：线程复用、控制最大并发数、管理线程
线程池中的任务是放入到阻塞队列中的
### 线程池的好处
多核处理的好处是：省略的上下文的切换开销
原来我们实例化对象的时候，是使用 new关键字进行创建，到了Spring后，我们学了IOC依赖注入，发现Spring帮我们将对象已经加载到了Spring容器中，只需要通过@Autowrite注解，就能够自动注入，从而使用
因此使用多线程有下列的好处
- 降低资源消耗。通过重复利用已创建的线程，降低线程创建和销毁造成的消耗
- 提高响应速度。当任务到达时，任务可以不需要等到线程创建就立即执行
- 提高线程的可管理性。线程是稀缺资源，如果无线创建，不仅会消耗系统资源，还会降低系统的稳定性，使用线程池可以进行统一的分配，调优和监控
### 架构说明
Java中线程池是通过Executor框架实现的，该框架中用到了Executor，Executors（代表工具类），ExecutorService，ThreadPoolExecutor这几个类。
![image-20200317175202647](images/image-20200317175202647.png)
![image-20200317175241007](images/image-20200317175241007.png)
### 创建线程池
- Executors.newFixedThreadPool(int i) ：创建一个拥有 i 个线程的线程池
  - 执行长期的任务，性能好很多
  - 创建一个定长线程池，可控制线程数最大并发数，超出的线程会在队列中等待
- Executors.newSingleThreadExecutor：创建一个只有1个线程的 单线程池
  - 一个任务一个任务执行的场景
  - 创建一个单线程化的线程池，它只会用唯一的工作线程来执行任务，保证所有任务按照指定顺序执行
- Executors.newCacheThreadPool();  创建一个可扩容的线程池
  - 执行很多短期异步的小程序或者负载教轻的服务器
  - 创建一个可缓存线程池，如果线程长度超过处理需要，可灵活回收空闲线程，如无可回收，则新建新线程
- Executors.newScheduledThreadPool(int corePoolSize)：线程池支持定时以及周期性执行任务，创建一个corePoolSize为传入参数，最大线程数为整形的最大数的线程池
具体使用，首先我们需要使用Executors工具类，进行创建线程池，这里创建了一个拥有5个线程的线程池
```
// 一池5个处理线程（用池化技术，一定要记得关闭）
ExecutorService threadPool = Executors.newFixedThreadPool(5);
// 创建一个只有一个线程的线程池
ExecutorService threadPool = Executors.newSingleThreadExecutor();
// 创建一个拥有N个线程的线程池，根据调度创建合适的线程
ExecutorService threadPool = Executors.newCacheThreadPool();
```
然后我们执行下面的的应用场景
```
模拟10个用户来办理业务，每个用户就是一个来自外部请求线程
```
我们需要使用 threadPool.execute执行业务，execute需要传入一个实现了Runnable接口的线程
```
threadPool.execute(() -> {
	System.out.println(Thread.currentThread().getName() + "\t 给用户办理业务");
});
```
然后我们使用完毕后关闭线程池
```
threadPool.shutdown();
```
完整代码为：
```
/**
 * 第四种获取 / 使用 Java多线程的方式，通过线程池
 * @author: 陌溪
 * @create: 2020-03-17-15:59
 */
public class MyThreadPoolDemo {
    public static void main(String[] args) {
        // Array  Arrays(辅助工具类)
        // Collection Collections(辅助工具类)
        // Executor Executors(辅助工具类)
        // 一池5个处理线程（用池化技术，一定要记得关闭）
        ExecutorService threadPool = Executors.newFixedThreadPool(5);
        // 模拟10个用户来办理业务，每个用户就是一个来自外部请求线程
        try {
            // 循环十次，模拟业务办理，让5个线程处理这10个请求
            for (int i = 0; i  {
                    System.out.println(Thread.currentThread().getName() + "\t 给用户:" + tempInt + " 办理业务");
                });
            }
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            threadPool.shutdown();
        }
    }
}
```
最后结果：
```
pool-1-thread-1	 给用户:0 办理业务
pool-1-thread-5	 给用户:4 办理业务
pool-1-thread-1	 给用户:5 办理业务
pool-1-thread-4	 给用户:3 办理业务
pool-1-thread-2	 给用户:1 办理业务
pool-1-thread-3	 给用户:2 办理业务
pool-1-thread-2	 给用户:9 办理业务
pool-1-thread-4	 给用户:8 办理业务
pool-1-thread-1	 给用户:7 办理业务
pool-1-thread-5	 给用户:6 办理业务
```
我们能够看到，一共有5个线程，在给10个用户办理业务
### 创建周期性执行任务的线程池
Executors.newScheduledThreadPool(int corePoolSize)：
**线程池支持定时以及周期性执行任务，创建一个corePoolSize为传入参数，最大线程数为整形的最大数的线程池**
底层使用 ScheduledThreadPoolExecutor 来实现 ScheduledThreadPoolExecutor 为ThreadPoolExecutor子类
```java
public ScheduledThreadPoolExecutor(int corePoolSize) {
        super(corePoolSize, Integer.MAX_VALUE, 0, NANOSECONDS,
              new DelayedWorkQueue());
}
```
#### 执行方法
```java
    /**
     * @throws RejectedExecutionException {@inheritDoc}
     * @throws NullPointerException       {@inheritDoc}
     * command：执行的任务 Callable或Runnable接口实现类
	 * delay：延时执行任务的时间
	 * unit：延迟时间单位
     */
    public ScheduledFuture schedule(Runnable command,
                                       long delay,
                                       TimeUnit unit)
```
```java
    /**
     * @throws RejectedExecutionException {@inheritDoc}
     * @throws NullPointerException       {@inheritDoc}
     * @throws IllegalArgumentException   {@inheritDoc}
     * command：执行的任务 Callable或Runnable接口实现类
	 * initialDelay 第一次执行任务延迟时间
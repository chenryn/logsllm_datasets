- 声明线程池后立即调用 **prestartAllCoreThreads** 方法，来启动所有核心线程；
- 传入 **true** 给 **allowCoreThreadTimeOut** 方法，来让线程池在空闲的时候同样回收核心线程。
不知道你有没有想过：**Java** 线程池是先用工作队列来存放来不及处理的任务，满了之后再扩容线程池。当我们的工作队列设置得很大时，最大线程数这个参数显得没有意义，因为队列很难满，或者到满的时候再去扩容线程池已经于事无补了。
那么，我们有没有办法让线程池更激进一点，优先开启更多的线程，而把队列当成一个后备方案呢？比如我们这个例子，任务执行得很慢，需要10秒，如果线程池可以优先扩容到 **5** 个最大线程，那么这些任务最终都可以完成，而不会因为线程池扩容过晚导致慢任务来不及处理。
限于篇幅，这里我只给你一个大致思路：
- 由于线程池在工作队列满了无法入队的情况下会扩容线程池，那么我们是否可以重写队列的offer方法，造成这个队列已满的假象呢？
- 由于我们 **Hack** 了队列，在达到了最大线程后势必会触发拒绝策略，那么能否实现一个自定义的拒绝策略处理程序，这个时候再把任务真正插入队列呢？
  接下来，就请你动手试试看如何实现这样一个“弹性”线程池吧。**Tomcat** 线程池也实现了类似的效果，可供你借鉴。
## 务必确认清楚线程池本身是不是复用的
不久之前我遇到了这样一个事故：某项目生产环境时不时有报警提示线程数过多，超过 **2000** 个，收到报警后查看监控发现，瞬时线程数比较多但过一会儿又会降下来，线程数抖动很厉害，而应用的访问量变化不大。
为了定位问题，我们在线程数比较高的时候进行线程栈抓取，抓取后发现内存中有 **1000** 多个自定义线程池。一般而言，线程池肯定是复用的，有5个以内的线程池都可以认为正常，而 **1000** 多个线程池肯定不正常。
在项目代码里，我们没有搜到声明线程池的地方，搜索execute关键字后定位到，原来是业务代码调用了一个类库来获得线程池，类似如下的业务代码：调用**ThreadPoolHelper** 的 **getThreadPool** 方法来获得线程池，然后提交数个任务到线程池处理，看不出什么异常。
```java
@GetMapping("wrong")
public String wrong() throws InterruptedException {
    ThreadPoolExecutor threadPool = ThreadPoolHelper.getThreadPool();
    IntStream.rangeClosed(1, 10).forEach(i -> {
        threadPool.execute(() -> {
            ...
            try {
                TimeUnit.SECONDS.sleep(1);
            } catch (InterruptedException e) {
            }
        });
    });
    return "OK";
}
```
但是，来到 **ThreadPoolHelper** 的实现让人大跌眼镜，**getThreadPool** 方法居然是每次都使用 **Executors.newCachedThreadPool** 来创建一个线程池。
```java
class ThreadPoolHelper {
    public static ThreadPoolExecutor getThreadPool() {
        //线程池没有复用
        return (ThreadPoolExecutor) Executors.newCachedThreadPool();
    }
}
```
通过上一小节的学习，我们可以想到 **newCachedThreadPool** 会在需要时创建必要多的线程，业务代码的一次业务操作会向线程池提交多个慢任务，这样执行一次业务操作就会开启多个线程。如果业务操作并发量较大的话，的确有可能一下子开启几千个线程。
那，为什么我们能在监控中看到线程数量会下降，而不会撑爆内存呢？
回到 **newCachedThreadPool** 的定义就会发现，它的核心线程数是0，而 **keepAliveTime** 是60秒，也就是在 **60** 秒之后所有的线程都是可以回收的。好吧，就因为这个特性，我们的业务程序死得没太难看。
要修复这个Bug也很简单，使用一个静态字段来存放线程池的引用，返回线程池的代码直接返回这个静态字段即可。这里一定要记得我们的最佳实践，手动创建线程池。修复后的 **ThreadPoolHelper** 类如下：
```java
class ThreadPoolHelper {
  private static ThreadPoolExecutor threadPoolExecutor = new ThreadPoolExecutor(
    10, 50,
    2, TimeUnit.SECONDS,
    new ArrayBlockingQueue<>(1000),
    new ThreadFactoryBuilder().setNameFormat("demo-threadpool-%d").get());
    public static ThreadPoolExecutor getRightThreadPool() {
   	  return threadPoolExecutor;
  	}
}
```
## 需要仔细斟酌线程池的混用策略
线程池的意义在于复用，那这是不是意味着程序应该始终使用一个线程池呢？
当然不是。通过第一小节的学习我们知道，要根据任务的“轻重缓急”来指定线程池的核心参数，包括线程数、回收策略和任务队列：
对于执行比较慢、数量不大的IO任务，或许要考虑更多的线程数，而不需要太大的队列。
而对于吞吐量较大的计算型任务，线程数量不宜过多，可以是CPU核数或核数*2（理由是，线程一定调度到某个CPU进行执行，如果任务本身是CPU绑定的任务，那么过多的线程只会增加线程切换的开销，并不能提升吞吐量），但可能需要较长的队列来做缓冲。
之前我也遇到过这么一个问题，业务代码使用了线程池异步处理一些内存中的数据，但通过监控发现处理得非常慢，整个处理过程都是内存中的计算不涉及IO操作，也需要数秒的处理时间，应用程序CPU占用也不是特别高，有点不可思议。
经排查发现，业务代码使用的线程池，还被一个后台的文件批处理任务用到了。
或许是够用就好的原则，这个线程池只有 **2** 个核心线程，最大线程也是 **2** ，使用了容量为 **100** 的 **ArrayBlockingQueue** 作为工作队列，使用了 **CallerRunsPolicy** 拒绝策略：
```java
private static ThreadPoolExecutor threadPool = new ThreadPoolExecutor(
        2, 2,
        1, TimeUnit.HOURS,
        new ArrayBlockingQueue<>(100),
        new ThreadFactoryBuilder().setNameFormat("batchfileprocess-threadpool-%d").get(),
        new ThreadPoolExecutor.CallerRunsPolicy());
```
这里，我们模拟一下文件批处理的代码，在程序启动后通过一个线程开启死循环逻辑，不断向线程池提交任务，任务的逻辑是向一个文件中写入大量的数据：
```java
@PostConstruct
public void init() {
    printStats(threadPool);
new Thread(() -> {
    //模拟需要写入的大量数据
    String payload = IntStream.rangeClosed(1, 1_000_000)
            .mapToObj(__ -> "a")
            .collect(Collectors.joining(""));
    while (true) {
        threadPool.execute(() -> {
            try {
                //每次都是创建并写入相同的数据到相同的文件
                Files.write(Paths.get("demo.txt"), Collections.singletonList(LocalTime.now().toString() + ":" + payload), UTF_8, CREATE, TRUNCATE_EXISTING);
            } catch (IOException e) {
                e.printStackTrace();
            }
            log.info("batch file processing done");
        });
    }
}).start();
}
```
可以想象到，这个线程池中的2个线程任务是相当重的。通过printStats方法打印出的日志，我们观察下线程池的负担：
![image-20220517083249217](images/image-20220517083249217.png)
可以看到，线程池的2个线程始终处于活跃状态，队列也基本处于打满状态。因为开启了CallerRunsPolicy拒绝处理策略，所以当线程满载队列也满的情况下，任务会在提交任务的线程，或者说调用execute方法的线程执行，也就是说不能认为提交到线程池的任务就一定是异步处理的。如果使用了CallerRunsPolicy策略，那么有可能异步任务变为同步执行。从日志的第四行也可以看到这点。这也是这个拒绝策略比较特别的原因。
不知道写代码的同学为什么设置这个策略，或许是测试时发现线程池因为任务处理不过来出现了异常，而又不希望线程池丢弃任务，所以最终选择了这样的拒绝策略。不管怎样，这些日志足以说明线程池是饱和状态。
可以想象到，业务代码复用这样的线程池来做内存计算，命运一定是悲惨的。我们写一段代码测试下，向线程池提交一个简单的任务，这个任务只是休眠10毫秒没有其他逻辑：
```java
private Callable calcTask() {
    return () -> {
        TimeUnit.MILLISECONDS.sleep(10);
        return 1;
    };
}
@GetMapping("wrong")
public int wrong() throws ExecutionException, InterruptedException {
    return threadPool.submit(calcTask()).get();
}
```
我们使用 **wrk** 工具对这个接口进行一个简单的压测，可以看到 **TPS** 为 75，性能的确非常差。
![image-20220517083339012](images/image-20220517083339012.png)
细想一下，问题其实没有这么简单。因为原来执行IO任务的线程池使用的是CallerRunsPolicy策略，所以直接使用这个线程池进行异步计算的话，当线程池饱和的时候，计算任务会在执行Web请求的Tomcat线程执行，这时就会进一步影响到其他同步处理的线程，甚至造成整个应用程序崩溃。
解决方案很简单，使用独立的线程池来做这样的“计算任务”即可。计算任务打了双引号，是因为我们的模拟代码执行的是休眠操作，并不属于CPU绑定的操作，更类似IO绑定的操作，如果线程池线程数设置太小会限制吞吐能力：
```java
private static ThreadPoolExecutor asyncCalcThreadPool = new ThreadPoolExecutor(
	200, 200,
	1, TimeUnit.HOURS,
	new ArrayBlockingQueue<>(1000),
	new ThreadFactoryBuilder().setNameFormat("asynccalc-threadpool-%d").get());
@GetMapping("right")
public int right() throws ExecutionException, InterruptedException {
	return asyncCalcThreadPool.submit(calcTask()).get();
}
```
使用单独的线程池改造代码后再来测试一下性能，TPS提高到了1727：
![image-20220517083402523](images/image-20220517083402523.png)
可以看到，盲目复用线程池混用线程的问题在于，别人定义的线程池属性不一定适合你的任务，而且混用会相互干扰。这就好比，我们往往会用虚拟化技术来实现资源的隔离，而不是让所有应用程序都直接使用物理机。
就线程池混用问题，我想再和你补充一个坑：Java 8的parallel stream功能，可以让我们很方便地并行处理集合中的元素，其背后是共享同一个ForkJoinPool，默认并行度是CPU核数-1。对于CPU绑定的任务来说，使用这样的配置比较合适，但如果集合操作涉及同步IO操作的话（比如数据库操作、外部服务调用等），建议自定义一个ForkJoinPool（或普通线程池）。你可以参考第一讲的相关Demo。
## 重点回顾
线程池管理着线程，线程又属于宝贵的资源，有许多应用程序的性能问题都来自线程池的配置和使用不当。在今天的学习中，我通过三个和线程池相关的生产事故，和你分享了使用线程池的几个最佳实践。
第一，Executors 类提供的一些快捷声明线程池的方法虽然简单，但隐藏了线程池的参数细节。因此，使用线程池时，我们一定要根据场景和需求配置合理的线程数、任务队列、拒绝策略、线程回收策略，并对线程进行明确的命名方便排查问题。
第二，既然使用了线程池就需要确保线程池是在复用的，每次 new 一个线程池出来可能比不用线程池还糟糕。如果你没有直接声明线程池而是使用其他同学提供的类库来获得一个线程池，请务必查看源码，以确认线程池的实例化方式和配置是符合预期的。
第三，复用线程池不代表应用程序始终使用同一个线程池，我们应该根据任务的性质来选用不同的线程池。特别注意 IO 绑定的任务和 CPU 绑定的任务对于线程池属性的偏好，如果希望减少任务间的相互干扰，考虑按需使用隔离的线程池。
最后我想强调的是，线程池作为应用程序内部的核心组件往往缺乏监控（如果你使用类似 RabbitMQ 这样的 MQ 中间件，运维同学一般会帮我们做好中间件监控），往往到程序崩溃后才发现线程池的问题，很被动。在设计篇中我们会重新谈及这个问题及其解决方案。
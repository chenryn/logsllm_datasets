今天，我们来看看解决线程安全问题的另一种重要手段—**锁**，在使用上比较容易犯哪些错。
我先和你分享一个有趣的案例吧。有一天，一位同学在群里说“见鬼了，疑似遇到了一个 **JVM** 的 **Bug**”，我们都很好奇是什么 **Bug**。
于是，他贴出了这样一段代码：在一个类里有两个 **int** 类型的字段 a 和 **b**，有一个 add 方法循环 **1** 万次对 a 和 **b** 进行 ++ 操作，有另一个 compare 方法，同样循环 1 万次判断 a 是否小于 b，条件成立就打印 a 和 b 的值，并判断 a>b 是否成立。
```
@Slf4j
public class Interesting {
    volatile int a = 1;
    volatile int b = 1;
    public void add() {
        log.info("add start");
        for (int i = 0; i  b);
                //最后的a>b应该始终是false吗？
            }
        }
        log.info("compare done");
    }
}
```
他起了两个线程来分别执行 add 和 compare 方法：
```
Interesting interesting = new Interesting();
new Thread(() -> interesting.add()).start();
new Thread(() -> interesting.compare()).start();
```
按道理，a 和 b 同样进行累加操作，应该始终相等，compare 中的第一次判断应该始终不会成立，不会输出任何日志。但，执行代码后发现不但输出了日志，而且更诡异的是，compare 方法在判断 ab 也成立：
![img](images/9ec61aada64ac6d38681dd199c0ee61d.png)
群里一位同学看到这个问题笑了，说：“这哪是 JVM 的 Bug，分明是线程安全问题嘛。很明显，你这是在操作两个字段 a 和 b，有线程安全问题，应该为 add 方法加上锁，确保 a 和 b 的 ++ 是原子性的，就不会错乱了。”随后，他为 add 方法加上了锁：
```
public synchronized void add()
```
但，加锁后问题并没有解决。
我们来仔细想一下，为什么锁可以解决线程安全问题呢。因为只有一个线程可以拿到锁，所以加锁后的代码中的资源操作是线程安全的。但是，这个案例中的 add 方法始终只有一个线程在操作，显然只为 add 方法加锁是没用的。
之所以出现这种错乱，是因为两个线程是交错执行 add 和 compare 方法中的业务逻辑，而且这些业务逻辑不是原子性的：a++ 和 b++ 操作中可以穿插在 compare 方法的比较代码中；更需要注意的是，a new Data().wrong());
    return Data.getCounter();
}
```
因为默认运行 100 万次，所以执行后应该输出 100 万，但页面输出的是 639242：
![img](images/777f520e9d0be89b66e814d3e7c1a30b.png)
我们来分析下为什么会出现这个问题吧。
在非静态的 wrong 方法上加锁，只能确保多个线程无法执行同一个实例的 wrong 方法，却不能保证不会执行不同实例的 wrong 方法。而静态的 counter 在多个实例中共享，所以必然会出现线程安全问题。
理清思路后，修正方法就很清晰了：同样在类中定义一个 Object 类型的静态字段，在操作 counter 之前对这个字段加锁。
```
class Data {
    @Getter
    private static int counter = 0;
    private static Object locker = new Object();
    public void right() {
        synchronized (locker) {
            counter++;
        }
    }
}
```
你可能要问了，把 wrong 方法定义为静态不就可以了，这个时候锁是类级别的。可以是可以，但我们不可能为了解决线程安全问题改变代码结构，把实例方法改为静态方法。
感兴趣的同学还可以从字节码以及 JVM 的层面继续探索一下，代码块级别的 synchronized 和方法上标记 synchronized 关键字，在实现上有什么区别。
## 加锁要考虑锁的粒度和场景问题
在方法上加 synchronized 关键字实现加锁确实简单，也因此我曾看到一些业务代码中几乎所有方法都加了 synchronized，但这种滥用 synchronized 的做法：
一是，没必要。通常情况下 60% 的业务代码是三层架构，数据经过无状态的 Controller、Service、Repository 流转到数据库，没必要使用 synchronized 来保护什么数据。
二是，可能会极大地降低性能。使用 Spring 框架时，默认情况下 Controller、Service、Repository 是单例的，加上 synchronized 会导致整个程序几乎就只能支持单线程，造成极大的性能问题。
即使我们确实有一些共享资源需要保护，也要尽可能降低锁的粒度，仅对必要的代码块甚至是需要保护的资源本身加锁。
比如，在业务代码中，有一个 ArrayList 因为会被多个线程操作而需要保护，又有一段比较耗时的操作（代码中的 slow 方法）不涉及线程安全问题，应该如何加锁呢？
错误的做法是，给整段业务逻辑加锁，把 slow 方法和操作 ArrayList 的代码同时纳入 synchronized 代码块；更合适的做法是，把加锁的粒度降到最低，只在操作 ArrayList 的时候给这个 ArrayList 加锁。
```
private List data = new ArrayList<>();
//不涉及共享资源的慢方法
private void slow() {
    try {
        TimeUnit.MILLISECONDS.sleep(10);
    } catch (InterruptedException e) {
    }
}
//错误的加锁方法
@GetMapping("wrong")
public int wrong() {
    long begin = System.currentTimeMillis();
    IntStream.rangeClosed(1, 1000).parallel().forEach(i -> {
        //加锁粒度太粗了
        synchronized (this) {
            slow();
            data.add(i);
        }
    });
    log.info("took:{}", System.currentTimeMillis() - begin);
    return data.size();
}
//正确的加锁方法
@GetMapping("right")
public int right() {
    long begin = System.currentTimeMillis();
    IntStream.rangeClosed(1, 1000).parallel().forEach(i -> {
privatestaticintITEM_COUNT=1000;
privateMapnormaluse()throwsInterruptedException{
    ConcurrentHashMapfreqs=newConcurrentHashMap<>(ITEM_COUNT)ForkJoinPoolforkJoinPool=newForkJoinPool(THREAD_COUNT);
    forkJoinPool.execute(()->IntStream.rangeClosed(1,LOOP_COUNT).parallel()
        //获得一个随机的Key
        Stringkey="item"+ThreadLocalRandom.current().nextint(ITEM_COUNT);
        synchronized(freqs){
            if(freqs.containsKey(key)){
                //Key存在则+1
                freqs.put(key,freqs.get(key)+1);
            } else{
                //Key不存在则初始化为1
                freqs.put(key,1L);
            }
        }
    }
    ));
    forkJoinPool.shutdown();
    forkJoinPool.awaitTermination(1,TimeUnit.HOURS);
    returnfreqs;
}
```
我们吸取之前的教训，直接通过锁的方式锁住 Map，然后做判断、读取现在的累计值、加1、保存累加后值的逻辑。这段代码在功能上没有问题，但无法充分发挥ConcurrentHashMap 的威力，改进后的代码如下：
```java
privateMapgooduse()throwsInterruptedException{
    ConcurrentHashMapfreqs=newConcurrentHashMap<>(ITEM_CForkJoinPoolforkJoinPool=newForkJoinPool(THREAD_COUNT);
    forkJoinPool.execute(()->IntStream.rangeClosed(1,LOOP_COUNT).parallel()
        Stringkey="item"+ThreadLocalRandom.current().nextint(ITEM_COUNT);
            //利用computeIfAbsent()方法来实例化LongAdder，然后利用LongAdder来进行
            freqs.computeIfAbsent(key,k->newLongAdder()).increment();
        }
    ));
    forkJoinPool.shutdown();
    forkJoinPool.awaitTermination(1,TimeUnit.HOURS);
    //因为我们的Value是LongAdder而不是Long，所以需要做一次转换才能返回
    returnfreqs.entrySet().stream()
        .collect(Collectors.toMap(
            e->e.getKey(),
            e->e.getValue().longValue())
        );
}
```
在这段改进后的代码中，我们巧妙利用了下面两点：
使用 ConcurrentHashMap 的原子性方法 computeIfAbsent 来做复合逻辑操作，判断Key 是否存在 Value，如果不存在则把 Lambda 表达式运行后的结果放入 Map 作为Value，也就是新创建一个 LongAdder 对象，最后返回 Value。
由于 computeIfAbsent 方法返回的 Value 是 LongAdder，是一个线程安全的累加器，因此可以直接调用其 increment 方法进行累加。
这样在确保线程安全的情况下达到极致性能，把之前 7 行代码替换为了 1 行。
我们通过一个简单的测试比较一下修改前后两段代码的性能：
```java
@GetMapping("good")
publicStringgood()throwsInterruptedException{
    StopWatchstopWatch=newStopWatch();
    stopWatch.start("normaluse");
    Mapnormaluse=normaluse();
    stopWatch.stop();
    //校验元素数量
    Assert.isTrue(normaluse.size()==ITEM_COUNT,"normalusesizeerror");
    //校验累计总数
    Assert.isTrue(normaluse.entrySet().stream()
            .mapToLong(item->item.getValue()).reduce(0,Long::sum)==
        ,"normalusecounterror");
    stopWatch.start("gooduse");
    Mapgooduse=gooduse();
    stopWatch.stop();
    Assert.isTrue(gooduse.size()==ITEM_COUNT,"goodusesizeerror");
    Assert.isTrue(gooduse.entrySet().stream()
            .mapToLong(item->item.getValue())
            .reduce(0,Long::sum)==LOOP_COUNT
        ,"goodusecounterror");
    log.info(stopWatch.prettyPrint());
    return"OK";
}
```
这段测试代码并无特殊之处，使用 StopWatch 来测试两段代码的性能，最后跟了一个断言判断 Map 中元素的个数以及所有 Value 的和，是否符合预期来校验代码的正确性。测试结果如下：
![image-20220514220157751](images/image-20220514220157751.png)
可以看到，优化后的代码，相比使用锁来操作 ConcurrentHashMap 的方式，性能提升了 10 倍。
你可能会问，computeIfAbsent 为什么如此高效呢？
答案就在源码最核心的部分，也就是 Java 自带的 Unsafe 实现的 CAS。它在虚拟机层面确保了写入数据的原子性，比加锁的效率高得多：
```java
staticfinalbooleancasTabAt(Node[]tab,inti,
        Nodec,Nodev){
    returnU.compareAndSetObject(tab,((long)icopyOnWriteArrayList=newCopyOnWriteArrayList<>();ListsynchronizedList=Collections.synchronizedList(newArrayListStopWatchstopWatch=newStopWatch();
    intloopCount=100000;
    stopWatch.start("Write:copyOnWriteArrayList");
    //循环100000次并发往CopyOnWriteArrayList写入随机元素
    IntStream.rangeClosed(1,loopCount).parallel().forEach(__->copyOnWriteAr
    stopWatch.stop();
    stopWatch.start("Write:synchronizedList");
    //循环100000次并发往加锁的ArrayList写入随机元素
    IntStream.rangeClosed(1,loopCount).parallel().forEach(__->synchronizedListopWatch.stop();
    log.info(stopWatch.prettyPrint());
    Mapresult=newHashMap();
    result.put("copyOnWriteArrayList",copyOnWriteArrayList.size());
    result.put("synchronizedList",synchronizedList.size());
    returnresult;
}
//帮助方法用来填充List
privatevoidaddAll(Listlist){
    list.addAll(IntStream.rangeClosed(1,1000000).boxed().collect(Collectors.to
}
//测试并发读的性能
@GetMapping("read")
publicMaptestRead(){
    //创建两个测试对象
    ListcopyOnWriteArrayList=newCopyOnWriteArrayList<>();ListsynchronizedList=Collections.synchronizedList(newArrayList//填充数据
    addAll(copyOnWriteArrayList);
    addAll(synchronizedList);
    StopWatchstopWatch=newStopWatch();
    intloopCount=1000000;
    intcount=copyOnWriteArrayList.size();
    stopWatch.start("Read:copyOnWriteArrayList");
    //循环1000000次并发从CopyOnWriteArrayList随机查询元素
    IntStream.rangeClosed(1,loopCount).parallel().forEach(__->copyOnWriteArstopWatch.stop();
    stopWatch.start("Read:synchronizedList");
    //循环1000000次并发从加锁的ArrayList随机查询元素
    IntStream.range(0,loopCount).parallel().forEach(__->synchronizedList.getstopWatch.stop();
    log.info(stopWatch.prettyPrint());
    Mapresult=newHashMap();
    result.put("copyOnWriteArrayList",copyOnWriteArrayList.size());
    result.put("synchronizedList",synchronizedList.size());
    returnresult;
}
```
运行程序可以看到，**大量写的场景（10 万次 add 操作），CopyOnWriteArray 几乎比同步的 ArrayList 慢一百倍**：
![image-20220514220243945](images/image-20220514220243945.png)
而在大量读的场景下（100 万次 get 操作），CopyOnWriteArray 又比同步的 ArrayList快五倍以上：
![image-20220514220304455](images/image-20220514220304455.png)
你可能会问，为何在大量写的场景下，CopyOnWriteArrayList 会这么慢呢？
答案就在源码中。以 add 方法为例，每次 add 时，都会用 Arrays.copyOf 创建一个新数组，频繁 add 时内存的申请释放消耗会很大：
```java
/**
*Appendsthespecifiedelementtotheendofthislist.
*
*@parameelementtobeappendedtothislist
*@return{@codetrue}(asspecifiedby{@linkCollection#add})
*/
publicbooleanadd(Ee){
    synchronized(lock){
        Object[]elements=getArray();
        intlen=elements.length;
        Object[]newElements=Arrays.copyOf(elements,len+1);newElements[len]=e;
        setArray(newElements);
        returntrue;
    }
}
```
## 总结
本文主要分享了开发人员使用并发工具来解决线程安全问题时容易犯的四类错。
- 一是，只知道使用并发工具，但并不清楚当前线程的来龙去脉，解决多线程问题却不了解线程。比如，使用 ThreadLocal 来缓存数据，以为 ThreadLocal 在线程之间做了隔离不会有线程安全问题，没想到线程重用导致数据串了。请务必记得，在业务逻辑结束之前清理ThreadLocal 中的数据。
- 二是，误以为使用了并发工具就可以解决一切线程安全问题，期望通过把线程不安全的类替换为线程安全的类来一键解决问题。比如，认为使用了 ConcurrentHashMap 就可以解决线程安全问题，没对复合逻辑加锁导致业务逻辑错误。如果你希望在一整段业务逻辑中，对容器的操作都保持整体一致性的话，需要加锁处理。
- 三是，没有充分了解并发工具的特性，还是按照老方式使用新工具导致无法发挥其性能。比如，使用了 ConcurrentHashMap，但没有充分利用其提供的基于 CAS 安全的方法，还是使用锁的方式来实现逻辑。
  四是，没有了解清楚工具的适用场景，在不合适的场景下使用了错误的工具导致性能更差。比如，没有理解 CopyOnWriteArrayList 的适用场景，把它用在了读写均衡或者大量写操作的场景下，导致性能问题。对于这种场景，你可以考虑是用普通的 List。
  其实，这四类坑之所以容易踩到，原因可以归结为，我们在使用并发工具的时候，并没有充分理解其可能存在的问题、适用场景等。所以最后，我还要和你分享两点建议：
一定要认真阅读官方文档（比如 Oracle JDK 文档）。充分阅读官方文档，理解工具的适用场景及其 API 的用法，并做一些小实验。了解之后再去使用，就可以避免大部分坑。
如果你的代码运行在多线程环境下，那么就会有并发问题，并发问题不那么容易重现，可能需要使用压力测试模拟并发场景，来发现其中的 Bug 或性能问题。
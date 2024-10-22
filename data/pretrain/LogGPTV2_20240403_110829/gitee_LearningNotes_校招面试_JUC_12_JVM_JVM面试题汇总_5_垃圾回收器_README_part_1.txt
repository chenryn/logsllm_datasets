# 垃圾收集器
## GC垃圾回收算法和垃圾收集器关系
> 天上飞的理念，要有落地的实现（垃圾收集器就是GC垃圾回收算法的实现）
>
> GC算法是内存回收的方法论，垃圾收集器就是算法的落地实现
GC算法主要有以下几种
- 引用计数（几乎不用，无法解决循环引用的问题）
- 复制拷贝（用于新生代）
- 标记清除（用于老年代）
- 标记整理（用于老年代）
因为目前为止还没有完美的收集器出现，更没有万能的收集器，只是针对具体应用最合适的收集器，进行分代收集（那个代用什么收集器）
## 四种主要的垃圾收集器
- Serial：串行回收  `-XX:+UseSeriallGC`
- Parallel：并行回收  `-XX:+UseParallelGC`
- CMS：并发标记清除
- G1
- ZGC：（java 11 出现的）
![image-20200325084453631](images/image-20200325084453631.png)
### Serial
串行垃圾回收器，它为单线程环境设计且值使用一个线程进行垃圾收集，会暂停所有的用户线程，只有当垃圾回收完成时，才会重新唤醒主线程继续执行。所以不适合服务器环境
![image-20200325085320683](images/image-20200325085320683.png)
### Parallel
并行垃圾收集器，多个垃圾收集线程并行工作，此时用户线程也是阻塞的，适用于科学计算 / 大数据处理等弱交互场景，也就是说Serial 和 Parallel其实是类似的，不过是多了几个线程进行垃圾收集，但是主线程都会被暂停，但是并行垃圾收集器处理时间，肯定比串行的垃圾收集器要更短
![image-20200325085729428](images/image-20200325085729428.png)
### CMS
并发标记清除，用户线程和垃圾收集线程同时执行（不一定是并行，可能是交替执行），不需要停顿用户线程，互联网公司都在使用，适用于响应时间有要求的场景。并发是可以有交互的，也就是说可以一边进行收集，一边执行应用程序。
![image-20200325090858921](images/image-20200325090858921.png)
### G1
G1垃圾回收器将堆内存分割成不同区域，然后并发的进行垃圾回收
![image-20200325093222711](images/image-20200325093222711.png)
## 垃圾收集器总结
注意：并行垃圾回收在单核CPU下可能会更慢
![image-20200325091619082](images/image-20200325091619082.png)
## 查看默认垃圾收集器
使用下面JVM命令，查看配置的初始参数
```
-XX:+PrintCommandLineFlags
```
然后运行一个程序后，能够看到它的一些初始配置信息
```
-XX:InitialHeapSize=266376000 -XX:MaxHeapSize=4262016000 -XX:+PrintCommandLineFlags -XX:+UseCompressedClassPointers -XX:+UseCompressedOops -XX:-UseLargePagesIndividualAllocation -XX:+UseParallelGC
```
移动到最后一句，就能看到 `-XX:+UseParallelGC` 说明使用的是并行垃圾回收
```
-XX:+UseParallelGC
```
## 默认垃圾收集器有哪些
Java中一共有7大垃圾收集器
- UserSerialGC：串行垃圾收集器
- UserParallelGC：并行垃圾收集器
- UseConcMarkSweepGC：（CMS）并发标记清除
- UseParNewGC：年轻代的并行垃圾回收器
- UseParallelOldGC：老年代的并行垃圾回收器
- UseG1GC：G1垃圾收集器
- UserSerialOldGC：串行老年代垃圾收集器（已经被移除）
底层源码
![image-20200325100653829](images/image-20200325100653829.png)
## 各垃圾收集器的使用范围
![image-20200325101451849](images/image-20200325101451849.png)
新生代使用的：
- Serial Copying： UserSerialGC，串行垃圾回收器
- Parallel Scavenge：UserParallelGC，并行垃圾收集器
- ParNew：UserParNewGC，新生代并行垃圾收集器
老年区使用的：
- Serial Old：UseSerialOldGC，老年代串行垃圾收集器
- Parallel Compacting（Parallel Old）：UseParallelOldGC，老年代并行垃圾收集器
- CMS：UseConcMarkSwepp，并行标记清除垃圾收集器
各区都能使用的：
G1：UseG1GC，G1垃圾收集器
垃圾收集器就来具体实现这些GC算法并实现内存回收，不同厂商，不同版本的虚拟机实现差别很大，HotSpot中包含的收集器如下图所示：
![image-20200325102329216](images/image-20200325102329216.png)
## 部分参数说明
- DefNew：Default New Generation
- Tenured：Old
- ParNew：Parallel New Generation
- PSYoungGen：Parallel Scavenge
- ParOldGen：Parallel Old Generation
## Java中的Server和Client模式
使用范围：一般使用Server模式，Client模式基本不会使用
操作系统
- 32位的Window操作系统，不论硬件如何都默认使用Client的JVM模式
- 32位的其它操作系统，2G内存同时有2个cpu以上用Server模式，低于该配置还是Client模式
- 64位只有Server模式
![image-20200325175208231](images/image-20200325175208231.png)
## 新生代下的垃圾收集器
### 串行GC(Serial)
串行GC（Serial）（Serial Copying）
是一个单线程单线程的收集器，在进行垃圾收集时候，必须暂停其他所有的工作线程直到它收集结束。
![image-20200325175704604](images/image-20200325175704604.png)
串行收集器是最古老，最稳定以及效率高的收集器，只使用一个线程去回收但其在垃圾收集过程中可能会产生较长的停顿(Stop-The-World 状态)。 虽然在收集垃圾过程中需要暂停所有其它的工作线程，但是它简单高效，对于限定单个CPU环境来说，没有线程交互的开销可以获得最高的单线程垃圾收集效率，因此Serial垃圾收集器依然是Java虚拟机运行在Client模式下默认的新生代垃圾收集器
对应JVM参数是：-XX:+UseSerialGC
开启后会使用：Serial(Young区用) + Serial Old(Old区用) 的收集器组合
表示：新生代、老年代都会使用串行回收收集器，新生代使用复制算法，老年代使用标记-整理算法
```
-Xms10m -Xmx10m -XX:PrintGCDetails -XX:+PrintConmandLineFlags -XX:+UseSerialGC
```
### 并行GC(ParNew)
并行收集器，使用多线程进行垃圾回收，在垃圾收集，会Stop-the-World暂停其他所有的工作线程直到它收集结束
![image-20200325191328733](images/image-20200325191328733.png)
ParNew收集器其实就是Serial收集器新生代的并行多线程版本，最常见的应用场景时配合老年代的CMS GC工作，其余的行为和Serial收集器完全一样，ParNew垃圾收集器在垃圾收集过程中同样也要暂停所有其他的工作线程。它是很多Java虚拟机运行在Server模式下新生代的默认垃圾收集器。
常见对应JVM参数：-XX:+UseParNewGC     启动ParNew收集器，只影响新生代的收集，不影响老年代
开启上述参数后，会使用：ParNew（Young区用） + Serial Old的收集器组合，新生代使用复制算法，老年代采用标记-整理算法
```
-Xms10m -Xmx10m -XX:PrintGCDetails -XX:+PrintConmandLineFlags -XX:+UseParNewGC
```
但是会出现警告，即 ParNew 和 Serial Old 这样搭配，Java8已经不再被推荐
![image-20200325194316660](images/image-20200325194316660.png)
备注： -XX:ParallelGCThreads   限制线程数量，默认开启和CPU数目相同的线程数
### 并行回收GC（Parallel）/ （Parallel Scavenge）
因为Serial 和 ParNew都不推荐使用了，因此现在新生代默认使用的是Parallel Scavenge，也就是新生代和老年代都是使用并行
![image-20200325204437678](images/image-20200325204437678.png)
Parallel Scavenge收集器类似ParNew也是一个新生代垃圾收集器，使用复制算法，也是一个并行的多线程的垃圾收集器，俗称吞吐量优先收集器。一句话：串行收集器在新生代和老年代的并行化
它关注的重点是：
可控制的吞吐量（Thoughput = 运行用户代码时间 / (运行用户代码时间 + 垃圾收集时间) ），也即比如程序运行100分钟，垃圾收集时间1分钟，吞吐量就是99%。高吞吐量意味着高效利用CPU时间，它多用于在后台运算而不需要太多交互的任务。
自适应调节策略也是ParallelScavenge收集器与ParNew收集器的一个重要区别。（自适应调节策略：虚拟机会根据当前系统的运行情况收集性能监控信息，动态调整这些参数以提供最合适的停顿时间( -XX:MaxGCPauseMills)）或最大的吞吐量。
常用JVM参数：-XX:+UseParallelGC 或 -XX:+UseParallelOldGC（可互相激活）使用Parallel Scanvenge收集器
开启该参数后：新生代使用复制算法，老年代使用标记-整理算法
```
-Xms10m -Xmx10m -XX:PrintGCDetails -XX:+PrintConmandLineFlags -XX:+UseParallelGC
```
## 老年代下的垃圾收集器
### 串行GC（Serial Old） / (Serial MSC)
Serial Old是Serial垃圾收集器老年代版本，它同样是一个单线程的收集器，使用标记-整理算法，这个收集器也主要是运行在Client默认的Java虚拟机中默认的老年代垃圾收集器
在Server模式下，主要有两个用途（了解，版本已经到8及以后）
- 在JDK1.5之前版本中与新生代的Parallel Scavenge收集器搭配使用（Parallel Scavenge + Serial Old）
- 作为老年代版中使用CMS收集器的后备垃圾收集方案。
配置方法：
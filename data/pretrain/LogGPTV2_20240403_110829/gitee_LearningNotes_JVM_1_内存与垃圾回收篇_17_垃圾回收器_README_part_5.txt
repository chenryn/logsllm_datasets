![image-20200714081622526](images/image-20200714081622526.png)
### PrintGCDetails
打开GC日志
```bash
-verbose:gc -XX:+PrintGCDetails
```
输入信息如下
![image-20200714081909309](images/image-20200714081909309.png)
参数解析
![image-20200714081925767](images/image-20200714081925767.png)
### 补充
- [GC"和"[Fu11GC"说明了这次垃圾收集的停顿类型，如果有"Fu11"则说明GC发生了"stop The World"
- 使用Seria1收集器在新生代的名字是Default New Generation，因此显示的是"[DefNew"
- 使用ParNew收集器在新生代的名字会变成"[ParNew"，意思是"Parallel New Generation"
- 使用Paralle1 scavenge收集器在新生代的名字是”[PSYoungGen"
- 老年代的收集和新生代道理一样，名字也是收集器决定的
- 使用G1收集器的话，会显示为"garbage-first heap"
Allocation Failure表明本次引起GC的原因是因为在年轻代中没有足够的空间能够存储新的数据了。
[PSYoungGen：5986K->696K（8704K）]5986K->704K（9216K）中括号内：GC回收前年轻代大小，回收后大小，（年轻代总大小）括号外：GC回收前年轻代和老年代大小，回收后大小，（年轻代和老年代总大小）
user代表用户态回收耗时，sys内核态回收耗时，rea实际耗时。由于多核的原因，时间总和可能会超过rea1时间
### Young GC图片
![image-20200714082555688](images/image-20200714082555688.png)
### FullGC图片、
![image-20200714082714690](images/image-20200714082714690.png)
### GC回收举例
我们编写一个程序，用来说明GC收集的过程
```java
/**
 * GC垃圾收集过程
 * @author: 陌溪
 * @create: 2020-07-14-8:35
 */
public class GCUseTest {
    static final Integer _1MB = 1024 * 1024;
    public static void main(String[] args) {
        byte [] allocation1, allocation2, allocation3, allocation4;
        allocation1 = new byte[2 *_1MB];
        allocation2 = new byte[2 *_1MB];
        allocation3 = new byte[2 *_1MB];
        allocation4 = new byte[4 *_1MB];
    }
}
```
我们设置JVM启动参数
```bash
-Xms10m -Xmx10m -XX:+PrintGCDetails
```
首先我们会将3个2M的数组存放到Eden区，然后后面4M的数组来了后，将无法存储，因为Eden区只剩下2M的剩余空间了，那么将会进行一次Young GC操作，将原来Eden区的内容，存放到Survivor区，但是Survivor区也存放不下，那么就会直接晋级存入Old 区
![image-20200714083332238](images/image-20200714083332238.png)
然后我们将4M对象存入到Eden区中
![image-20200714083526790](images/image-20200714083526790.png)
可以用一些工具去分析这些GC日志
常用的日志分析工具有：GCViewer、GCEasy、GCHisto、GCLogViewer、Hpjmeter、garbagecat等
**GCViewer**
![image-20200714084921184](images/image-20200714084921184.png)
**GC easy**
![image-20200714084726824](images/image-20200714084726824.png)
## 垃圾回收器的新发展
GC仍然处于飞速发展之中，目前的默认选项G1GC在不断的进行改进，很多我们原来认为的缺点，例如串行的Fu11GC、Card Table扫描的低效等，都已经被大幅改进，例如，JDK10以后，Fu11GC已经是并行运行，在很多场景下，其表现还略优于ParallelGC的并行Ful1GC实现。
即使是SerialGC，虽然比较古老，但是简单的设计和实现未必就是过时的，它本身的开销，不管是GC相关数据结构的开销，还是线程的开销，都是非常小的，所以随着云计算的兴起，在serverless等新的应用场景下，Serial Gc找到了新的舞台。
比较不幸的是CMSGC，因为其算法的理论缺陷等原因，虽然现在还有非常大的用户群体，但在JDK9中已经被标记为废弃，并在JDK14版本中移除
Epsilon:A No-Op GarbageCollector（Epsilon垃圾回收器，"No-Op（无操作）"回收器）http://openidk.iava.net/iep s/318
ZGC:A Scalable Low-Latency Garbage Collector（Experimental）（ZGC：可伸缩的低延迟垃圾回收器，处于实验性阶段）
现在G1回收器已成为默认回收器好几年了。我们还看到了引入了两个新的收集器：ZGC（JDK11出现）和Shenandoah（Open JDK12）
>主打特点：低停顿时间
### Open JDK12的Shenandoash GC
Open JDK12的shenandoash GC：低停顿时间的GC（实验性）
Shenandoah，无疑是众多GC中最孤独的一个。是第一款不由oracle公司团队领导开发的Hotspot垃圾收集器。不可避免的受到官方的排挤。比如号称openJDK和OracleJDk没有区别的Oracle公司仍拒绝在oracleJDK12中支持Shenandoah。
Shenandoah垃圾回收器最初由RedHat进行的一项垃圾收集器研究项目Pauseless GC的实现，旨在针对JVM上的内存回收实现低停顿的需求。在2014年贡献给OpenJDK。
Red Hat研发Shenandoah团队对外宣称，Shenandoah垃圾回收器的暂停时间与堆大小无关，这意味着无论将堆设置为200MB还是200GB，99.9%的目标都可以把垃圾收集的停顿时间限制在十毫秒以内。不过实际使用性能将取决于实际工作堆的大小和工作负载。
![image-20200714090608807](images/image-20200714090608807.png)
这是RedHat在2016年发表的论文数据，测试内容是使用Es对200GB的维基百科数据进行索引。从结果看：
>停顿时间比其他几款收集器确实有了质的飞跃，但也未实现最大停顿时间控制在十毫秒以内的目标。
>而吞吐量方面出现了明显的下降，总运行时间是所有测试收集器里最长的。
总结
- shenandoah Gc的弱项：高运行负担下的吞吐量下降。
- shenandoah GC的强项：低延迟时间。
### 革命性的ZGC
zGC与shenandoah目标高度相似，在尽可能对吞吐量影响不大的前提下，实现在任意堆内存大小下都可以把垃圾收集的停颇时间限制在十毫秒以内的低延迟。
《深入理解Java虚拟机》一书中这样定义zGC：2GC收集器是一款基于Region内存布局的，（暂时）不设分代的，使用了读屏障、染色指针和内存多重映射等技术来实现可并发的标记-压缩算法的，以低延迟为首要目标的一款垃圾收集器。
ZGC的工作过程可以分为4个阶段：**并发标记 - 并发预备重分配 - 并发重分配 - 并发重映射** 等。
ZGC几乎在所有地方并发执行的，除了初始标记的是STw的。所以停顿时间几乎就耗费在初始标记上，这部分的实际时间是非常少的。
![image-20200714091201073](images/image-20200714091201073.png)
停顿时间对比
![image-20200714091401511](images/image-20200714091401511.png)
虽然ZGC还在试验状态，没有完成所有特性，但此时性能已经相当亮眼，用“令人震惊、革命性”来形容，不为过。
未来将在服务端、大内存、低延迟应用的首选垃圾收集器。
![image-20200714093243028](images/image-20200714093243028.png)
JDK14之前，2GC仅Linux才支持。
尽管许多使用zGc的用户都使用类Linux的环境，但在Windows和macos上，人们也需要zGC进行开发部署和测试。许多桌面应用也可以从ZGC中受益。因此，2GC特性被移植到了Windows和macos上。
现在mac或Windows上也能使用zGC了，示例如下：
```bash
-XX:+UnlockExperimentalVMOptions-XX：+UseZGC
```
### AliGC 
AliGC是阿里巴巴JVM团队基于G1算法，面向大堆（LargeHeap）应用场景。指定场景下的对比：
![image-20200714093604012](images/image-20200714093604012.png)
当然，其它厂商也提供了各种别具一格的GC实现，例如比较有名的低延迟GC Zing
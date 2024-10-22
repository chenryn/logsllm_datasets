基于上面给出的前提，大家通常想到的解决方法
- 从 **service** 层将 **connection** 对象向 **dao** 层传递
- 加锁
### 常规解决方法的弊端
- 提高代码的耦合度（因为我们需要从 **service** 层 传入 **connection** 参数）
- 降低程序的性能（加了同步代码块，失去了并发性）
这个时候就可以通过 **ThreadLocal** 和当前线程进行绑定，来降低代码之间的耦合
![image-20200710212423494](images/image-20200710212423494.png)
### 使用ThreadLocal解决
针对上面出现的情况，我们需要对原来的JDBC连接池对象进行更改
- 将原来从连接池中获取对象，改成直接获取当前线程绑定的连接对象
- 如果连接对象是空的
  - 再去连接池中获取连接
  - 将此连接对象跟当前线程进行绑定
```java
ThreadLocal tl = new ThreadLocal();
public static Connection getConnection() {
    Connection conn = tl.get();
    if(conn == null) {
        conn = ds.getConnection();
        tl.set(conn);
    }
    return conn;
}
```
### ThreadLocal实现的好处
从上述的案例中我们可以看到，在一些特定场景下，ThreadLocal方案有两个突出的优势：
- 传递数据：保存每个线程绑定的数据，在需要的地方可以直接获取，避免参数直接传递带来的代码耦合问题
- 线程隔离：各线程之间的数据相互隔离却又具备并发性，避免同步方式带来的性能损失
## ThreadLocal的内部结构
通过以上的学习，我们对 **ThreadLocal** 的作用有了一定的认识。现在我们一起来看一下 **ThreadLocal** 的内部结构，探究它能够实现线程数据隔离的原理。
### 常见误解
如果我们不去看源代码的话，可能会猜测 **ThreadLocal** 是这样子设计的：每个 **ThreadLocal** 都创建一个 **Map**，然后用线程作为 **Map** 的 **key**，要存储的局部变量作为 **Map** 的 **value**，这样就能达到各个线程的局部变量隔离的效果。这是最简单的设计方法，JDK最早期的 **ThreadLocal** 确实是这样设计的，但现在早已不是了。
![image-20200710214857638](images/image-20200710214857638.png)
### 现在的设计
但是，**JDK** 后面优化了设计方案，在 **JDK8** 中 **ThreadLocal** 的设计是：每个 **Thread** 维护一个**ThreadLocalMap**，这个 **Map** 的 **key** 是 **ThreadLocal** 实例本身，**value** 才是真正要存储的值 **object**。具体的过程是这样的：
- 每个 **Thread** 线程内部都有一个 **Map**（**ThreadLocalMap**）
- **Map** 里面存储 **ThreadLocal** 对象**key** 和线程的变量副本 **value**
- **Thread** 内部的 **Map** 是由 **ThreadLocal** 维护的，由 **ThreadLocal** 负责向 **map** 获取和设置线程的变量值。
- 对于不同的线程，每次获取副本值时，别的线程并不能获取到当前线程的副本值，形成了副本的隔离，互不干扰。
![image-20200710215038748](images/image-20200710215038748.png)
### 对比
![image-20200710215128743](images/image-20200710215128743.png)
从上面变成 **JDK8** 的设计有什么好处？
- 每个 **Map** 存储的 **Entry** 数量变少，因为原来的 **Entry** 数量是由 **Thread** 决定，而现在是由 **ThreadLocal** 决定的。真实开发中，**Thread** 的数量远远大于 **ThreadLocal** 的数量
- 当 **Thread** 销毁的时候，**ThreadLocalMap** 也会随之销毁，因为 **ThreadLocal** 是存放在 **Thread** 中的，随着 **Thread** 销毁而消失，能降低开销。
## ThreadLocalMap源码分析
在分析 **ThreadLocal** 方法的时候，我们了解到 **ThreadLocal** 的操作实际上是围绕 **ThreadLocalMap** 展开的。
**ThreadLocalMap** 的源码相对比较复杂，我们从以下三个方面进行讨论。
### 基本结构
**ThreadLocalMap** 是 **ThreadLocal** 的内部类，没有实现 **Map** 接口，用独立的方式实现了 **Map** 的功能，其内部的 **Entry** 也是独立实现。
![image-20200710220856315](images/image-20200710220856315.png)
#### 成员变量
```java
/**
* 初始容量 - 必须是2的整次幂
**/
private static final int INITIAL_CAPACITY = 16;
/**
*存放数据的table ，Entry类的定义在下面分析，同样，数组的长度必须是2的整次幂
**/
private Entry[] table;
/**
*数组里面entrys的个数，可以用于判断table当前使用量是否超过阈值
**/
private int size = 0;
/**
*进行扩容的阈值，表使用量大于它的时候进行扩容
**/
private int threshold; // Default to 0
```
跟 **HashMap** 类似，**INITIAL_CAPACITY** 代表这个 **Map** 的初始容量；**table** 是一个 **Entry** 类型的数组，用于存储数据；**size** 代表表中的存储数目；**threshold** 代表需要扩容时对应的 **size** 的阈值。
### 存储结构 - Entry
```java
/*
*Entry继承WeakRefefence，并且用ThreadLocal作为key.
如果key为nu11（entry.get（）==nu11），意味着key不再被引用，
*因此这时候entry也可以从table中清除。
*/
static class Entry extends weakReference>{
object value；Entry（ThreadLocalk，object v）{
    super(k);
    value = v;
}}
```
在 **ThreadLocalMap** 中，也是用 **Entry** 来保存 **K-V** 结构数据的。不过 **Entry** 中的 **key** 只能是 **ThreadLocal** 对象，这点在构造方法中已经限定死了。
另外，**Entry** 继承 **WeakReference**，也就是 **key（ThreadLocal）**是弱引用，其目的是将 **ThreadLocal** 对象的生命周期和线程生命周期解绑。
## 弱引用和内存泄漏
有些程序员在使用 **ThreadLocal** 的过程中会发现有内存泄漏的情况发生，就猜测这个内存泄漏跟Entry中使用了弱引用的 **key** 有关系。这个理解其实是不对的。
我们先来回顾这个问题中涉及的几个名词概念，再来分析问题。
### 内存泄漏相关概念
**Memory overflow**：内存溢出，没有足够的内存提供申请者使用。
**Memory leak**：内存泄漏是指程序中己动态分配的堆内存由于某种原因程序未释放或无法释放，造成系统内存的浪费，导致程序运行速度减慢甚至系统溃等严重后果。I内存泄漏的堆积终将导致内存溢出。
### 弱引用相关概念
Java中的引用有4种类型：强、软、弱、虚。当前这个问题主要涉及到强引用和弱引用：
**强引用**：就是我们最常见的普通对象引用，只要还有强引用指向一个对象，就能表明对象还“活着”，垃圾回收器就不会回收这种对象。
**弱引用**：垃圾回收器一旦发现了只具有弱引用的对象，不管当前内存空间足够与否，都会回收它的内存。
### 如果key使用强引用，那么会出现内存泄漏？
假设 **ThreadLocalMap** 中的 **key** 使用了强引用，那么会出现内存泄漏吗？
此时 **ThreadLocal** 的内存图（实线表示强引用）如下：
![image-20200710222559109](images/image-20200710222559109.png)
- 假设在业务代码中使用完 **ThreadLocal**，**threadLocal Ref**被回收了
- 但是因为 **threadLocalMap** 的 **Entry** 强引用了 **threadLocal**，造成 **threadLocal** 无法被回收。
- 在没有手动删除这个 **Entry** 以及 **CurrentThread** 依然运行的前提下，始终有强引用链 **threadRef->currentThread->threadLocalMap->entry**，**Entry** 就不会被回收（ **Entry** 中包括了ThreadLocal实例和value），导致Entry内存泄漏。
也就是说，**ThreadLocalMap** 中的 **key** 使用了强引用，是无法完全避免内存泄漏的。
### 如果key使用弱引用，那么会出现内存泄漏？
![image-20200710222847567](images/image-20200710222847567.png)
- 同样假设在业务代码中使用完 **ThreadLocal** ，**threadLocal Ref** 被回收了。
- 由于 **ThreadLocalMap** 只持有 **ThreadLocal** 的弱引用，没有任何强引用指向 **threadlocal** 实例，所以**threadlocal** 就可以顺利被 **gc** 回收，此时 **Entry** 中的 **key=null** 。
- 但是在没有手动删除这个 **Entry** 以及 **CurrentThread** 依然运行的前提下，也存在有强引用链 **threadRef->currentThread->threadLocalMap->entry-> value**，**value** 不会被回收，而这块 **value** 永远不会被访问到了，导致 **value** 内存泄漏。
也就是说，**ThreadLocalMap** 中的 **key** 使用了弱引用，也有可能内存泄漏。
### 出现内存泄漏的真实原因
比较以上两种情况，我们就会发现，内存泄漏的发生跟 **ThreadLocalMap** 中的 **key** 是否使用弱引用是没有关系的。那么内存泄漏的的真正原因是什么呢？
细心的同学会发现，在以上两种内存泄漏的情况中，都有两个前提：
- 没有手动删除这个 **Entry**
- **CurrentThread** 依然运行
第一点很好理解，只要在使用完 **ThreadLocal**，调用其 **remove** 方法删除对应的 **Entry**，就能避免内存泄漏。
第二点稍微复杂一点，由于 **ThreadLocalMap** 是 **Thread** 的一个属性，被当前线程所引用，所以它的生命周期跟 **Thread** 一样长。那么在使用完 **ThreadLocal** 的使用，如果当前 **Thread** 也随之执行结束，**ThreadLocalMap** 自然也会被 **gc** 回收，从根源上避免了内存泄漏。
综上，**ThreadLocal** 内存泄漏的根源是：由于 **ThreadLocalMap** 的生命周期跟 **Thread** 一样长，如果没有手动删除对应 **key** 就会导致内存泄漏。
### 为什么要使用弱引用？
根据刚才的分析，我们知道了：无论 **ThreadLocalMap** 中的 **key** 使用哪种类型引用都无法完全避免内存泄漏，跟使用弱引用没有关系。
要避免内存泄漏有两种方式：
- 使用完 **ThreadLocal**，调用其 **remove** 方法删除对应的 **Entry**
- 使用完 **ThreadLocal**，当前 **Thread** 也随之运行结束
相对第一种方式，第二种方式显然更不好控制，特别是使用线程池的时候，线程结束是不会销毁的，而是接着放入了线程池中。
也就是说，只要记得在使用完 **ThreadLocal** 及时的调用 **remove**，无论 **key** 是强引用还是弱引用都不会有问题。
那么为什么 **key** 要用弱引用呢？
事实上，在 **ThreadLocalMap** 中的 **set / getEntry** 方法中，会对 **key** 为 **null**（也即是 **ThreadLocal** 为**null**）进行判断，如果为 **null** 的话，那么是会对 **value** 置为 **null** 的。
这就意味着使用完 **ThreadLocal**，**CurrentThread** 依然运行的前提下，就算忘记调用 **remove** 方法，弱引用比强引用可以多一层保障：弱引用 的**ThreadLocal 会**被回收，对应的 **value** 在下一次 **ThreadLocalMap** 调用**set，get，remove** 中的任一方法的时候会被清除，从而避免内存泄漏。
## 往期推荐
- [蘑菇博客从0到2000Star，分享我的Java自学路线图](https://mp.weixin.qq.com/s/3u6OOYkpj4_ecMzfMqKJRw)
- [从三本院校到斩获字节跳动后端研发Offer-讲述我的故事](https://mp.weixin.qq.com/s/c4rR_aWpmNNFGn-mZBLWYg)
- [陌溪在公众号摸滚翻爬半个月，整理的入门指南](https://mp.weixin.qq.com/s/Jj1i-mD9Tw0vUEFXi5y54g)
- [读者问:有没有高效的记视频笔记方法？](https://mp.weixin.qq.com/s/QcQnV1yretxmDQr4ELW7_g)
- [万字长文带你学习ElasticSearch](https://mp.weixin.qq.com/s/9eh6rK2aZHRiBpf5bRae9g)
## 结语
应各位小伙伴们的需求，陌溪已经把 **学习笔记** 已经整理成 **PDF** 版本啦，方便大家在手机或者电脑上阅读。以下笔记仓库的部分 **PDF** 文件 ~
![周阳老师大厂面试第二季](images/image-20210523171559176.png)
![中华石杉老师Java面试突击](images/image-20210523171833579.png)
![宋红康老师JVM笔记](images/image-20210523172056549.png)
如果有需要离线阅读的小伙伴可以到公众号回复 **PDF** ，即可获取下载地址~
![img](https://gitee.com/moxi159753/LearningNotes/raw/master/doc/images/qq/%E8%8E%B7%E5%8F%96PDF.jpg)
同时本公众号**申请较晚**，暂时没有开通**留言**功能，欢迎小伙伴们添加我的私人微信【备注：**加群**】，我将邀请你加入到**蘑菇博客交流群**中，欢迎小伙伴们找陌溪一块聊天唠嗑，共同学习进步，如果你觉得本文对你有所帮助，麻烦小伙伴们动动手指给文章点个“**赞**”和“**在看**”。
![快来找陌溪唠嗑吧](https://gitee.com/moxi159753/LearningNotes/raw/master/doc/images/qq/%E6%B7%BB%E5%8A%A0%E9%99%8C%E6%BA%AA.png)
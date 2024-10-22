| void rollbakc()           | 回滚事务                         |
开启事务的注意点
为了保证所有操作在一个事务中，案例中使用的连接必须是同一个；service层开启事务的connection需要跟dao层访问数据库的connection保持一致
线程并发情况下，每个线程只能操作各自的connection，也就是线程隔离
### 常规解决方法
基于上面给出的前提，大家通常想到的解决方法
- 从service层将connection对象向dao层传递
- 加锁
### 常规解决方法的弊端
- 提高代码的耦合度（因为我们需要从service 层 传入 connection参数）
- 降低程序的性能（加了同步代码块，失去了并发性）
这个时候就可以通过ThreadLocal和当前线程进行绑定，来降低代码之间的耦合
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
通过以上的学习，我们对ThreadLocal的作用有了一定的认识。现在我们一起来看一下ThreadLocal的内部结构，探究它能够实现线程数据隔离的原理。
### 常见误解
如果我们不去看源代码的话，可能会猜测 ThreadLocal 是这样子设计的：每个ThreadLocal都创建一个Map，然后用线程作为Map的key，要存储的局部变量作为Map的value，这样就能达到各个线程的局部变量隔离的效果。这是最简单的设计方法，JDK最早期的ThreadLocal确实是这样设计的，但现在早已不是了。
![image-20200710214857638](images/image-20200710214857638.png)
### 现在的设计
但是，JDK后面优化了设计方案，在JDK8中 ThreadLocal的设计是：每个Thread维护一个ThreadLocalMap，这个Map的key是ThreadLocal实例本身，value 才是真正要存储的值object。具体的过程是这样的：
- 每个Thread线程内部都有一个Map（ThreadLocalMap）
- Map里面存储ThreadLocal对象（key）和线程的变量副本（value）
- Thread内部的Map是由ThreadLocal维护的，由ThreadLocal负责向map获取和设置线程的变量值。
- 对于不同的线程，每次获取副本值时，别的线程并不能获取到当前线程的副本值，形成了副本的隔离，互不干扰。
![image-20200710215038748](images/image-20200710215038748.png)
### 对比
![image-20200710215128743](images/image-20200710215128743.png)
从上面变成JDK8的设计有什么好处？
- 每个Map存储的Entry数量变少，因为原来的Entry数量是由Thread决定，而现在是由ThreadLocal决定的
  - 真实开发中，Thread的数量远远大于ThreadLocal的数量
- 当Thread销毁的时候，ThreadLocalMap也会随之销毁，因为ThreadLocal是存放在Thread中的，随着Thread销毁而消失，能降低开销。
## ThreadLocal核心方法源码
基于ThreadLocal的内部结构，我们继续分析它的核心方法源码，更深入的了解其操作原理。
除了构造方法之外，ThreadLocal对外暴露的方法有以下4个
| 方法声明                   | 描述                         |
| -------------------------- | ---------------------------- |
| protected T initialValue() | 返回当前线程局部变量的初始值 |
| public void set(T value)   | 返回当前线程绑定的局部变量   |
| public T get()             | 获取当前线程绑定的局部变量   |
| public void remove()       | 移除当前线程绑定的局部变量   |
以下是这4个方法的详细源码分析（为了保证思路清晰，ThreadLocalMap部分暂时不展开，下一个知识点详解）
### set方法
![image-20200710215706026](images/image-20200710215706026.png)
![image-20200710215827494](images/image-20200710215827494.png)
代码流程
- 首先获取当前线程，并根据当前线程获取一个Map
- 如果获取的Map不为空，则将参数设置到Map中（当前ThreadLocal的引用作为key）
- 如果Map为空，则给该线程创建Map，并设置初始化值
### get方法
![image-20200710220037887](images/image-20200710220037887.png)
![image-20200710220201472](images/image-20200710220201472.png)
代码执行流程
- 首先获取当前线程，根据当前线程获取一个Map 
- 如果获取的Map不为空，则在Map中以ThreadLocal的引用作为key来在Map中获取对应的Entrye，否则转到第四步
-  如果e不为null，则返回e.value，否则转到第四步
- Map为空或者e为空，则通过initialValue函数获取初始值value，然后用ThreadLocal的引用和value作为firstKey和firstValue创建一个新的Map
总结：先获取当前线程的ThreadLocal变量，如果存在则返回值，不存在则创建并返回初始值
### remove方法
![image-20200710220519229](images/image-20200710220519229.png)
代码执行流程
- 首先获取当前线程，并根据当前线程获取一个Map
- 如果获取的Map不为空，则移除当前ThreadLocal对象对应的Entry
### initialValue方法
![image-20200710220639455](images/image-20200710220639455.png)
此方法的作用是返回该线程局部变量的初始值。
- 这个方法是一个延迟调用方法，从上面的代码我们得知，在set方法还未调用而先调用了get方法时才执行，并且仅执行1次。
- 这个方法缺省实现直接返回一个null。
- 如果想要一个除null之外的初始值，可以重写此方法。（备注：该方法是一个protected的方法，显然是为了让子类覆盖而设计的）
## ThreadLocalMap源码分析
在分析ThreadLocal方法的时候，我们了解到ThreadLocal的操作实际上是围绕ThreadLocalMap展开的。
ThreadLocalMap的源码相对比较复杂，我们从以下三个方面进行讨论。
### 基本结构
ThreadLocalMap是ThreadLocal的内部类，没有实现Map接口，用独立的方式实现了Map的功能，其内部的Entry也是独立实现。
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
跟HashMap类似，INITIAL_CAPACITY代表这个Map的初始容量；table是一个Entry类型的数组，用于存储数据；size代表表中的存储数目；threshold代表需要扩容时对应的size的阈值。
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
在ThreadLocalMap中，也是用Entry来保存K-V结构数据的。不过Entry中的key只能是ThreadLocal对象，这点在构造方法中已经限定死了。
另外，Entry继承WeakReference，也就是key（ThreadLocal）是弱引用，其目的是将ThreadLocal对象的生命周期和线程生命周期解绑。
## 弱引用和内存泄漏
有些程序员在使用ThreadLocal的过程中会发现有内存泄漏的情况发生，就猜测这个内存泄漏跟Entry中使用了弱引用的key有关系。这个理解其实是不对的。
我们先来回顾这个问题中涉及的几个名词概念，再来分析问题。
### 内存泄漏相关概念
Memory overflow：内存溢出，没有足够的内存提供申请者使用。
Memory leak：内存泄漏是指程序中己动态分配的堆内存由于某种原因程序未释放或无法释放，造成系统内存的浪费，导致程序运行速度减慢甚至系统溃等严重后果。I内存泄漏的堆积终将导致内存溢出。
### 弱引用相关概念
Java中的引用有4种类型：强、软、弱、虚。当前这个问题主要涉及到强引用和弱引用：
强引用（"Strong"Reference），就是我们最常见的普通对象引用，只要还有强引用指向一个对象，就能表明对象还“活着”，垃圾回收器就不会回收这种对象。
弱引用（WeakReference），垃圾回收器一旦发现了只具有弱引用的对象，不管当前内存空间足够与否，都会回收它的内存。
### 如果key使用强引用，那么会出现内存泄漏？
# 堆
## 堆的核心概念
堆针对一个JVM进程来说是唯一的，也就是一个进程只有一个JVM，但是进程包含多个线程，他们是共享同一堆空间的。
![image-20200706195127740](images/image-20200706195127740.png)
一个JVM实例只存在一个堆内存，堆也是Java内存管理的核心区域。
Java堆区在JVM启动的时候即被创建，其空间大小也就确定了。是JVM管理的最大一块内存空间。
- 堆内存的大小是可以调节的。
《Java虚拟机规范》规定，堆可以处于物理上不连续的内存空间中，但在逻辑上它应该被视为连续的。
所有的线程共享Java堆，在这里还可以划分线程私有的缓冲区（Thread Local Allocation Buffer，TLAB）。
> -Xms10m：最小堆内存
>
> -Xmx10m：最大堆内存
下图就是使用：Java VisualVM查看堆空间的内容，通过 jdk bin提供的插件
![image-20200706200739392](images/image-20200706200739392.png)
《Java虚拟机规范》中对Java堆的描述是：所有的对象实例以及数组都应当在运行时分配在堆上。（The heap is the run-time data area from which memory for all class instances and arrays is allocated）
我要说的是：“几乎”所有的对象实例都在这里分配内存。—从实际使用角度看的。
- 因为还有一些对象是在栈上分配的
数组和对象可能永远不会存储在栈上，因为栈帧中保存引用，这个引用指向对象或者数组在堆中的位置。
在方法结束后，堆中的对象不会马上被移除，仅仅在垃圾收集的时候才会被移除。
- 也就是触发了GC的时候，才会进行回收
- 如果堆中对象马上被回收，那么用户线程就会收到影响，因为有stop the word
堆，是GC（Garbage Collection，垃圾收集器）执行垃圾回收的重点区域。
![image-20200706201904057](images/image-20200706201904057.png)
### 堆内存细分
Java 7及之前堆内存逻辑上分为三部分：新生区+养老区+永久区
- Young Generation Space 新生区  Young/New   又被划分为Eden区和Survivor区
- Tenure generation space 养老区 Old/Tenure
- Permanent Space永久区   Perm
Java 8及之后堆内存逻辑上分为三部分：新生区养老区+元空间
- Young Generation Space新生区  Young/New  又被划分为Eden区和Survivor区
- Tenure generation space 养老区  Old/Tenure
- Meta Space  元空间   Meta
约定：新生区 -> 新生代 -> 年轻代   、  养老区 -> 老年区 -> 老年代、 永久区 -> 永久代
![image-20200706203419496](images/image-20200706203419496.png)
堆空间内部结构，JDK1.8之前从永久代  替换成 元空间
![image-20200706203835403](images/image-20200706203835403.png)
## 设置堆内存大小与OOM
Java堆区用于存储Java对象实例，那么堆的大小在JVM启动时就已经设定好了，大家可以通过选项"-Xmx"和"-Xms"来进行设置。
- “-Xms"用于表示堆区的起始内存，等价于-xx:InitialHeapSize
- “-Xmx"则用于表示堆区的最大内存，等价于-XX:MaxHeapSize
一旦堆区中的内存大小超过“-xmx"所指定的最大内存时，将会抛出outofMemoryError异常。
通常会将-Xms和-Xmx两个参数配置相同的值，其目的是**为了能够在ava垃圾回收机制清理完堆区后不需要重新分隔计算堆区的大小，从而提高性能**。
默认情况下
- 初始内存大小：物理电脑内存大小/64
- 最大内存大小：物理电脑内存大小/4
```java
/**
 * -Xms 用来设置堆空间（年轻代+老年代）的初始内存大小
 *  -X：是jvm运行参数
 *  ms：memory start
 * -Xmx：用来设置堆空间（年轻代+老年代）的最大内存大小
 *
 * @author: 陌溪
 * @create: 2020-07-06-20:44
 */
public class HeapSpaceInitial {
    public static void main(String[] args) {
        // 返回Java虚拟机中的堆内存总量
        long initialMemory = Runtime.getRuntime().totalMemory() / 1024 / 1024;
        // 返回Java虚拟机试图使用的最大堆内存
        long maxMemory = Runtime.getRuntime().maxMemory() / 1024 / 1024;
        System.out.println("-Xms:" + initialMemory + "M");
        System.out.println("-Xmx:" + maxMemory + "M");
    }
}
```
输出结果
```
-Xms:245M
-Xmx:3614M
```
如何查看堆内存的内存分配情况
```
jps  ->  jstat -gc 进程id
```
![image-20200706205756045](images/image-20200706205756045.png)
```
-XX:+PrintGCDetails
```
![image-20200706205821919](images/image-20200706205821919.png)
### OutOfMemory举例
![image-20200706205947535](images/image-20200706205947535.png)
![image-20200706210000461](images/image-20200706210000461.png)
我们简单的写一个OOM例子
```java
/**
 * OOM测试
 *
 * @author: 陌溪
 * @create: 2020-07-06-21:11
 */
public class OOMTest {
    public static void main(String[] args) {
        List list = new ArrayList<>();
        while(true) {
            list.add(999999999);
        }
    }
}
```
然后设置启动参数
```
-Xms10m -Xmx:10m
```
运行后，就出现OOM了，那么我们可以通过 VisualVM这个工具查看具体是什么参数造成的OOM
![image-20200706211652779](images/image-20200706211652779.png)
## 年轻代与老年代
存储在JVM中的Java对象可以被划分为两类：
- 一类是生命周期较短的瞬时对象，这类对象的创建和消亡都非常迅速
  - 生命周期短的，及时回收即可
- 另外一类对象的生命周期却非常长，在某些极端的情况下还能够与JVM的生命周期保持一致
Java堆区进一步细分的话，可以划分为年轻代（YoungGen）和老年代（oldGen）
其中年轻代又可以划分为Eden空间、Survivor0空间和Survivor1空间（有时也叫做from区、to区）
![image-20200707075847954](images/image-20200707075847954.png)
下面这参数开发中一般不会调：
![image-20200707080154039](images/image-20200707080154039.png)
- Eden：From：to ->  8:1:1
- 新生代：老年代  - >  1 : 2
配置新生代与老年代在堆结构的占比。
- 默认-XX:NewRatio=2，表示新生代占1，老年代占2，新生代占整个堆的1/3
- 可以修改-XX:NewRatio=4，表示新生代占1，老年代占4，新生代占整个堆的1/5
> 当发现在整个项目中，生命周期长的对象偏多，那么就可以通过调整 老年代的大小，来进行调优
在HotSpot中，Eden空间和另外两个survivor空间缺省所占的比例是8：1：1当然开发人员可以通过选项“-xx:SurvivorRatio”调整这个空间比例。比如-xx:SurvivorRatio=8
几乎所有的Java对象都是在Eden区被new出来的。绝大部分的Java对象的销毁都在新生代进行了。（有些大的对象在Eden区无法存储时候，将直接进入老年代）
>IBM公司的专门研究表明，新生代中80%的对象都是“朝生夕死”的。
>
>可以使用选项"-Xmn"设置新生代最大内存大小
>
>这个参数一般使用默认值就可以了。
![image-20200707084208115](images/image-20200707084208115.png)
## 图解对象分配过程
### 概念
为新对象分配内存是一件非常严谨和复杂的任务，JM的设计者们不仅需要考虑内存如何分配、在哪里分配等问题，并且由于内存分配算法与内存回收算法密切相关，所以还需要考虑GC执行完内存回收后是否会在内存空间中产生内存碎片。
# Java中的引用
## 前言
在原来的时候，我们谈到一个类的实例化
```
Person p = new Person()
```
在等号的左边，就是一个对象的引用，存储在栈中
而等号右边，就是实例化的对象，存储在堆中
其实这样的一个引用关系，就被称为强引用
## 整体架构
![image-20200323155120778](images/image-20200323155120778.png)
## 强引用
当内存不足的时候，JVM开始垃圾回收，对于强引用的对象，就算是出现了OOM也不会对该对象进行回收，打死也不回收~！
强引用是我们最常见的普通对象引用，只要还有一个强引用指向一个对象，就能表明对象还“活着”，垃圾收集器不会碰这种对象。在Java中最常见的就是强引用，把一个对象赋给一个引用变量，这个引用变量就是一个强引用。当一个对象被强引用变量引用时，它处于可达状态，它是不可能被垃圾回收机制回收的，即使该对象以后永远都不会被用到，JVM也不会回收，因此强引用是造成Java内存泄漏的主要原因之一。
对于一个普通的对象，如果没有其它的引用关系，只要超过了引用的作用于或者显示地将相应（强）引用赋值为null，一般可以认为就是可以被垃圾收集的了（当然具体回收时机还是要看垃圾回收策略）
强引用小例子：
```
/**
 * 强引用
 * @author: 陌溪
 * @create: 2020-03-23-16:25
 */
public class StrongReferenceDemo {
    public static void main(String[] args) {
        // 这样定义的默认就是强应用
        Object obj1 = new Object();
        // 使用第二个引用，指向刚刚创建的Object对象
        Object obj2 = obj1;
        // 置空
        obj1 = null;
        // 垃圾回收
        System.gc();
        System.out.println(obj1);
        System.out.println(obj2);
    }
}
```
输出结果我们能够发现，即使 obj1 被设置成了null，然后调用gc进行回收，但是也没有回收实例出来的对象，obj2还是能够指向该地址，也就是说垃圾回收器，并没有将该对象进行垃圾回收
```
null
java.lang.Object@14ae5a5
```
## 软引用
软引用是一种相对弱化了一些的引用，需要用Java.lang.ref.SoftReference类来实现，可以让对象豁免一些垃圾收集，对于只有软引用的对象来讲：
- 当系统内存充足时，它不会被回收
- 当系统内存不足时，它会被回收
软引用通常在对内存敏感的程序中，比如高速缓存就用到了软引用，内存够用 的时候就保留，不够用就回收
具体使用
```
/**
 * 软引用
 *
 * @author: 陌溪
 * @create: 2020-03-23-16:39
 */
public class SoftReferenceDemo {
    /**
     * 内存够用的时候
     */
    public static void softRefMemoryEnough() {
        // 创建一个强应用
        Object o1 = new Object();
        // 创建一个软引用
        SoftReference softReference = new SoftReference<>(o1);
        System.out.println(o1);
        System.out.println(softReference.get());
        o1 = null;
        // 手动GC
        System.gc();
        System.out.println(o1);
        System.out.println(softReference.get());
    }
    /**
     * JVM配置，故意产生大对象并配置小的内存，让它的内存不够用了导致OOM，看软引用的回收情况
     * -Xms5m -Xmx5m -XX:+PrintGCDetails
     */
    public static void softRefMemoryNoEnough() {
        System.out.println("========================");
        // 创建一个强应用
        Object o1 = new Object();
        // 创建一个软引用
        SoftReference softReference = new SoftReference<>(o1);
        System.out.println(o1);
        System.out.println(softReference.get());
        o1 = null;
        // 模拟OOM自动GC
        try {
            // 创建30M的大对象
            byte[] bytes = new byte[30 * 1024 * 1024];
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            System.out.println(o1);
            System.out.println(softReference.get());
        }
    }
    public static void main(String[] args) {
        softRefMemoryEnough();
        softRefMemoryNoEnough();
    }
}
```
我们写了两个方法，一个是内存够用的时候，一个是内存不够用的时候
我们首先查看内存够用的时候，首先输出的是 o1 和 软引用的 softReference，我们都能够看到值
然后我们把o1设置为null，执行手动GC后，我们发现softReference的值还存在，说明内存充足的时候，软引用的对象不会被回收
```
java.lang.Object@14ae5a5
java.lang.Object@14ae5a5
[GC (System.gc()) [PSYoungGen: 1396K->504K(1536K)] 1504K->732K(5632K), 0.0007842 secs] [Times: user=0.00 sys=0.00, real=0.00 secs] 
[Full GC (System.gc()) [PSYoungGen: 504K->0K(1536K)] [ParOldGen: 228K->651K(4096K)] 732K->651K(5632K), [Metaspace: 3480K->3480K(1056768K)], 0.0058450 secs] [Times: user=0.00 sys=0.00, real=0.01 secs] 
null
java.lang.Object@14ae5a5
```
下面我们看当内存不够的时候，我们使用了JVM启动参数配置，给初始化堆内存为5M
```
-Xms5m -Xmx5m -XX:+PrintGCDetails
```
但是在创建对象的时候，我们创建了一个30M的大对象
```
// 创建30M的大对象
byte[] bytes = new byte[30 * 1024 * 1024];
```
这就必然会触发垃圾回收机制，这也是中间出现的垃圾回收过程，最后看结果我们发现，o1 和 softReference都被回收了，因此说明，软引用在内存不足的时候，会自动回收
```
java.lang.Object@7f31245a
java.lang.Object@7f31245a
[GC (Allocation Failure) [PSYoungGen: 31K->160K(1536K)] 682K->811K(5632K), 0.0003603 secs] [Times: user=0.00 sys=0.00, real=0.00 secs] 
[GC (Allocation Failure) [PSYoungGen: 160K->96K(1536K)] 811K->747K(5632K), 0.0006385 secs] [Times: user=0.00 sys=0.00, real=0.00 secs] 
[Full GC (Allocation Failure) [PSYoungGen: 96K->0K(1536K)] [ParOldGen: 651K->646K(4096K)] 747K->646K(5632K), [Metaspace: 3488K->3488K(1056768K)], 0.0067976 secs] [Times: user=0.02 sys=0.00, real=0.01 secs] 
[GC (Allocation Failure) [PSYoungGen: 0K->0K(1536K)] 646K->646K(5632K), 0.0004024 secs] [Times: user=0.00 sys=0.00, real=0.00 secs] 
[Full GC (Allocation Failure) [PSYoungGen: 0K->0K(1536K)] [ParOldGen: 646K->627K(4096K)] 646K->627K(5632K), [Metaspace: 3488K->3488K(1056768K)], 0.0065506 secs] [Times: user=0.00 sys=0.00, real=0.01 secs] 
null
null
```
## 弱引用
不管内存是否够，只要有GC操作就会进行回收
弱引用需要用 `java.lang.ref.WeakReference` 类来实现，它比软引用生存期更短
对于只有弱引用的对象来说，只要垃圾回收机制一运行，不管JVM的内存空间是否足够，都会回收该对象占用的空间。
```
/**
 * 弱引用
 *
 * @author: 陌溪
 * @create: 2020-03-24-10:18
 */
public class WeakReferenceDemo {
    public static void main(String[] args) {
        Object o1 = new Object();
        WeakReference weakReference = new WeakReference<>(o1);
        System.out.println(o1);
        System.out.println(weakReference.get());
        o1 = null;
        System.gc();
        System.out.println(o1);
        System.out.println(weakReference.get());
    }
}
```
我们看结果，能够发现，我们并没有制造出OOM内存溢出，而只是调用了一下GC操作，垃圾回收就把它给收集了
```
java.lang.Object@14ae5a5
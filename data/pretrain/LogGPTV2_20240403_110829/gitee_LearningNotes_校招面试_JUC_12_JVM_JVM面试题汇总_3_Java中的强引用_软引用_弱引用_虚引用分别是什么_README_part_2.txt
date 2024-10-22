java.lang.Object@14ae5a5
[GC (System.gc()) [PSYoungGen: 5246K->808K(76288K)] 5246K->816K(251392K), 0.0008236 secs] [Times: user=0.00 sys=0.00, real=0.00 secs] 
[Full GC (System.gc()) [PSYoungGen: 808K->0K(76288K)] [ParOldGen: 8K->675K(175104K)] 816K->675K(251392K), [Metaspace: 3494K->3494K(1056768K)], 0.0035953 secs] [Times: user=0.00 sys=0.00, real=0.00 secs] 
null
null
```
## 软引用和弱引用的使用场景
场景：假如有一个应用需要读取大量的本地图片
- 如果每次读取图片都从硬盘读取则会严重影响性能
- 如果一次性全部加载到内存中，又可能造成内存溢出
此时使用软引用可以解决这个问题
设计思路：使用HashMap来保存图片的路径和相应图片对象关联的软引用之间的映射关系，在内存不足时，JVM会自动回收这些缓存图片对象所占的空间，从而有效地避免了OOM的问题
```
Map> imageCache = new HashMap>();
```
### WeakHashMap是什么？
比如一些常常和底层打交道的，mybatis等，底层都应用到了WeakHashMap
WeakHashMap和HashMap类似，只不过它的Key是使用了弱引用的，也就是说，当执行GC的时候，HashMap中的key会进行回收，下面我们使用例子来测试一下
我们使用了两个方法，一个是普通的HashMap方法
我们输入一个Key-Value键值对，然后让它的key置空，然后在查看结果
```
    private static void myHashMap() {
        Map map = new HashMap<>();
        Integer key = new Integer(1);
        String value = "HashMap";
        map.put(key, value);
        System.out.println(map);
        key = null;
        System.gc();
        System.out.println(map);
    }
```
第二个是使用了WeakHashMap，完整代码如下
```
/**
 * WeakHashMap
 * @author: 陌溪
 * @create: 2020-03-24-11:33
 */
public class WeakHashMapDemo {
    public static void main(String[] args) {
        myHashMap();
        System.out.println("==========");
        myWeakHashMap();
    }
    private static void myHashMap() {
        Map map = new HashMap<>();
        Integer key = new Integer(1);
        String value = "HashMap";
        map.put(key, value);
        System.out.println(map);
        key = null;
        System.gc();
        System.out.println(map);
    }
    private static void myWeakHashMap() {
        Map map = new WeakHashMap<>();
        Integer key = new Integer(1);
        String value = "WeakHashMap";
        map.put(key, value);
        System.out.println(map);
        key = null;
        System.gc();
        System.out.println(map);
    }
}
```
最后输出结果为：
```
{1=HashMap}
{1=HashMap}
==========
{1=WeakHashMap}
{}
```
从这里我们看到，对于普通的HashMap来说，key置空并不会影响，HashMap的键值对，因为这个属于强引用，不会被垃圾回收。
但是WeakHashMap，在进行GC操作后，弱引用的就会被回收
## 虚引用
### 概念
虚引用又称为幽灵引用，需要`java.lang.ref.PhantomReference` 类来实现
顾名思义，就是形同虚设，与其他几种引用都不同，虚引用并不会决定对象的生命周期。
如果一个对象持有虚引用，那么它就和没有任何引用一样，在任何时候都可能被垃圾回收器回收，它不能单独使用也不能通过它访问对象，虚引用必须和引用队列ReferenceQueue联合使用。
虚引用的主要作用和跟踪对象被垃圾回收的状态，仅仅是提供一种确保对象被finalize以后，做某些事情的机制。
PhantomReference的get方法总是返回null，因此无法访问对象的引用对象。其意义在于说明一个对象已经进入finalization阶段，可以被gc回收，用来实现比finalization机制更灵活的回收操作
换句话说，设置虚引用关联的唯一目的，就是在这个对象被收集器回收的时候，收到一个系统通知或者后续添加进一步的处理，Java技术允许使用finalize()方法在垃圾收集器将对象从内存中清除出去之前，做必要的清理工作
这个就相当于Spring AOP里面的后置通知
### 场景
一般用于在回收时候做通知相关操作
## 引用队列 ReferenceQueue
软引用，弱引用，虚引用在回收之前，需要在引用队列保存一下
我们在初始化的弱引用或者虚引用的时候，可以传入一个引用队列
```
Object o1 = new Object();
// 创建引用队列
ReferenceQueue referenceQueue = new ReferenceQueue<>();
// 创建一个弱引用
WeakReference weakReference = new WeakReference<>(o1, referenceQueue);
```
那么在进行GC回收的时候，弱引用和虚引用的对象都会被回收，但是在回收之前，它会被送至引用队列中
完整代码如下：
```
/**
 * 虚引用
 *
 * @author: 陌溪
 * @create: 2020-03-24-12:09
 */
public class PhantomReferenceDemo {
    public static void main(String[] args) {
        Object o1 = new Object();
        // 创建引用队列
        ReferenceQueue referenceQueue = new ReferenceQueue<>();
        // 创建一个弱引用
        WeakReference weakReference = new WeakReference<>(o1, referenceQueue);
        // 创建一个弱引用
//        PhantomReference weakReference = new PhantomReference<>(o1, referenceQueue);
        System.out.println(o1);
        System.out.println(weakReference.get());
        // 取队列中的内容
        System.out.println(referenceQueue.poll());
        o1 = null;
        System.gc();
        System.out.println("执行GC操作");
        try {
            TimeUnit.SECONDS.sleep(2);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        System.out.println(o1);
        System.out.println(weakReference.get());
        // 取队列中的内容
        System.out.println(referenceQueue.poll());
    }
}
```
运行结果
```
java.lang.Object@14ae5a5
java.lang.Object@14ae5a5
null
执行GC操作
null
null
java.lang.ref.WeakReference@7f3124
```
从这里我们能看到，在进行垃圾回收后，我们弱引用对象，也被设置成null，但是在队列中还能够导出该引用的实例，这就说明在回收之前，该弱引用的实例被放置引用队列中了，我们可以通过引用队列进行一些后置操作
## GCRoots和四大引用小总结
- 红色部分在垃圾回收之外，也就是强引用的
- 蓝色部分：属于软引用，在内存不够的时候，才回收
- 虚引用和弱引用：每次垃圾回收的时候，都会被干掉，但是它在干掉之前还会存在引用队列中，我们可以通过引用队列进行一些通知机制
![image-20200324123829937](images/image-20200324123829937.png)
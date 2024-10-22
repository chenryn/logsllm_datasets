安全区域是指在一段代码片段中，对象的引用关系不会发生变化，在这个区域中的任何位置开始Gc都是安全的。我们也可以把Safe Region看做是被扩展了的Safepoint。
**执行流程：**
- 当线程运行到Safe Region的代码时，首先标识已经进入了Safe Relgion，如果这段时间内发生GC，JVM会忽略标识为Safe Region状态的线程
- 当线程即将离开Safe Region时，会检查JVM是否已经完成GC，如果完成了，则继续运行，否则线程必须等待直到收到可以安全离开Safe Region的信号为止；
## 再谈引用
我们希望能描述这样一类对象：当内存空间还足够时，则能保留在内存中；如果内存空间在进行垃圾收集后还是很紧张，则可以抛弃这些对象。
【既偏门又非常高频的面试题】强引用、软引用、弱引用、虚引用有什么区别？具体使用场景是什么？
在JDK1.2版之后，Java对引用的概念进行了扩充，将引用分为：
- 强引用（Strong Reference）
- 软引用（Soft Reference）
- 弱引用（Weak Reference）
- 虚引用（Phantom Reference）
这4种引用强度依次逐渐减弱。除强引用外，其他3种引用均可以在java.1ang.ref包中找到它们的身影。如下图，显示了这3种引用类型对应的类，开发人员可以在应用程序中直接使用它们。
.![image-20200712205813321](images/image-20200712205813321.png)
Reference子类中只有终结器引用是包内可见的，其他3种引用类型均为public，可以在应用程序中直接使用
- 强引用（StrongReference）：最传统的“引用”的定义，是指在程序代码之中普遍存在的引用赋值，即类似“object obj=new Object（）”这种引用关系。无论任何情况下，==只要强引用关系还存在，垃圾收集器就永远不会回收掉被引用的对象==。
- 软引用（SoftReference）：在系统将要发生内存溢出之前，将会把这些对象列入回收范围之中进行第二次回收。如果这次回收后还没有足够的内存，才会抛出内存流出异常。
- 弱引用（WeakReference）：被弱引用关联的对象只能生存到下一次垃圾收集之前。当垃圾收集器工作时，无论内存空间是否足够，都会回收掉被弱引用关联的对象。
- 虚引用（PhantomReference）：一个对象是否有虚引用的存在，完全不会对其生存时间构成影响，也无法通过虚引用来获得一个对象的实例。==为一个对象设置虚引用关联的唯一目的就是能在这个对象被收集器回收时收到一个系统通知==。
## 再谈引用：强引用
在Java程序中，最常见的引用类型是强引用（普通系统99%以上都是强引用），也就是我们最常见的普通对象引用，也是默认的引用类型。
当在Java语言中使用new操作符创建一个新的对象，并将其赋值给一个变量的时候，这个变量就成为指向该对象的一个强引用。
强引用的对象是可触及的，垃圾收集器就永远不会回收掉被引用的对象。
对于一个普通的对象，如果没有其他的引用关系，只要超过了引用的作用域或者显式地将相应（强）引用赋值为nu11，就是可以当做垃圾被收集了，当然具体回收时机还是要看垃圾收集策略。
相对的，软引用、弱引用和虚引用的对象是软可触及、弱可触及和虚可触及的，在一定条件下，都是可以被回收的。所以，强引用是造成Java内存泄漏的主要原因之一。
### 举例
强引用的案例说明
```java
StringBuffer str = new StringBuffer("hello mogublog");
```
局部变量str指向stringBuffer实例所在堆空间，通过str可以操作该实例，那么str就是stringBuffer实例的强引用对应内存结构：
![image-20200712211501377](images/image-20200712211501377.png)
如果此时，在运行一个赋值语句
```java
StringBuffer str = new StringBuffer("hello mogublog");
StringBuffer str1 = str;
```
对应的内存结构为:
![image-20200712211732976](images/image-20200712211732976.png)
那么我们将 str = null; 则 原来堆中的对象也不会被回收，因为还有其它对象指向该区域
### 总结
本例中的两个引用，都是强引用，强引用具备以下特点：
- 强引用可以直接访问目标对象。
- 强引用所指向的对象在任何时候都不会被系统回收，虚拟机宁愿抛出OOM异常，也不会回收强引用所指向对象。
- 强引用可能导致内存泄漏。
## 再谈引用： 软引用
软引用是用来描述一些还有用，但非必需的对象。只被软引用关联着的对象，在系统将要发生内存溢出异常前，会把这些对象列进回收范围之中进行第二次回收，如果这次回收还没有足够的内存，才会抛出内存溢出异常。
> 注意，这里的第一次回收是不可达的对象
软引用通常用来实现内存敏感的缓存。比如：高速缓存就有用到软引用。如果还有空闲内存，就可以暂时保留缓存，当内存不足时清理掉，这样就保证了使用缓存的同时，不会耗尽内存。
垃圾回收器在某个时刻决定回收软可达的对象的时候，会清理软引用，并可选地把引用存放到一个引用队列（Reference Queue）。
类似弱引用，只不过Java虚拟机会尽量让软引用的存活时间长一些，迫不得已才清理。
> 一句话概括：当内存足够时，不会回收软引用可达的对象。内存不够时，会回收软引用的可达对象
在JDK1.2版之后提供了SoftReference类来实现软引用
```java
// 声明强引用
Object obj = new Object();
// 创建一个软引用
SoftReference sf = new SoftReference<>(obj);
obj = null; //销毁强引用，这是必须的，不然会存在强引用和软引用
```
## 再谈引用：弱引用
> 发现即回收
弱引用也是用来描述那些非必需对象，被弱引用关联的对象只能生存到下一次垃圾收集发生为止。在系统GC时，只要发现弱引用，不管系统堆空间使用是否充足，都会回收掉只被弱引用关联的对象。
但是，由于垃圾回收器的线程通常优先级很低，因此，并不一定能很快地发现持有弱引用的对象。在这种情况下，弱引用对象可以存在较长的时间。
弱引用和软引用一样，在构造弱引用时，也可以指定一个引用队列，当弱引用对象被回收时，就会加入指定的引用队列，通过这个队列可以跟踪对象的回收情况。
软引用、弱引用都非常适合来保存那些可有可无的缓存数据。如果这么做，当系统内存不足时，这些缓存数据会被回收，不会导致内存溢出。而当内存资源充足时，这些缓存数据又可以存在相当长的时间，从而起到加速系统的作用。
在JDK1.2版之后提供了WeakReference类来实现弱引用
```java
// 声明强引用
Object obj = new Object();
// 创建一个弱引用
WeakReference sf = new WeakReference<>(obj);
obj = null; //销毁强引用，这是必须的，不然会存在强引用和弱引用
```
弱引用对象与软引用对象的最大不同就在于，当GC在进行回收时，需要通过算法检查是否回收软引用对象，而对于弱引用对象，GC总是进行回收。弱引用对象更容易、更快被GC回收。
面试题：你开发中使用过WeakHashMap吗？
WeakHashMap用来存储图片信息，可以在内存不足的时候，及时回收，避免了OOM
## 再谈引用：虚引用
也称为“幽灵引用”或者“幻影引用”，是所有引用类型中最弱的一个
一个对象是否有虚引用的存在，完全不会决定对象的生命周期。如果一个对象仅持有虚引用，那么它和没有引用几乎是一样的，随时都可能被垃圾回收器回收。
它不能单独使用，也无法通过虚引用来获取被引用的对象。当试图通过虚引用的get（）方法取得对象时，总是null
为一个对象设置虚引用关联的唯一目的在于跟踪垃圾回收过程。比如：能在这个对象被收集器回收时收到一个系统通知。
虚引用必须和引用队列一起使用。虚引用在创建时必须提供一个引用队列作为参数。当垃圾回收器准备回收一个对象时，如果发现它还有虚引用，就会在回收对象后，将这个虚引用加入引用队列，以通知应用程序对象的回收情况。
由于虚引用可以跟踪对象的回收时间，因此，也可以将一些资源释放操作放置在虚引用中执行和记录。
> 虚引用无法获取到我们的数据
在JDK1.2版之后提供了PhantomReference类来实现虚引用。
```java
// 声明强引用
Object obj = new Object();
// 声明引用队列
ReferenceQueue phantomQueue = new ReferenceQueue();
// 声明虚引用（还需要传入引用队列）
PhantomReference sf = new PhantomReference<>(obj, phantomQueue);
obj = null; 
```
### 案例
我们使用一个案例，来结合虚引用，引用队列，finalize进行讲解
```java
/**
 * @author: 陌溪
 * @create: 2020-07-12-21:42
 */
public class PhantomReferenceTest {
    // 当前类对象的声明
    public static PhantomReferenceTest obj;
    // 引用队列
    static ReferenceQueue phantomQueue = null;
    @Override
    protected void finalize() throws Throwable {
        super.finalize();
        System.out.println("调用当前类的finalize方法");
        obj = this;
    }
    public static void main(String[] args) {
        Thread thread = new Thread(() -> {
            while(true) {
                if (phantomQueue != null) {
                    PhantomReference objt = null;
                    try {
                        objt = (PhantomReference) phantomQueue.remove();
                    } catch (Exception e) {
                        e.getStackTrace();
                    }
                    if (objt != null) {
                        System.out.println("追踪垃圾回收过程：PhantomReferenceTest实例被GC了");
                    }
                }
            }
        }, "t1");
        thread.setDaemon(true);
        thread.start();
        phantomQueue = new ReferenceQueue<>();
        obj = new PhantomReferenceTest();
        // 构造了PhantomReferenceTest对象的虚引用，并指定了引用队列
        PhantomReference phantomReference = new PhantomReference<>(obj, phantomQueue);
        try {
            System.out.println(phantomReference.get());
            // 去除强引用
            obj = null;
            // 第一次进行GC，由于对象可复活，GC无法回收该对象
            System.out.println("第一次GC操作");
            System.gc();
            Thread.sleep(1000);
            if (obj == null) {
                System.out.println("obj 是 null");
            } else {
                System.out.println("obj 不是 null");
            }
            System.out.println("第二次GC操作");
            obj = null;
            System.gc();
            Thread.sleep(1000);
            if (obj == null) {
                System.out.println("obj 是 null");
            } else {
                System.out.println("obj 不是 null");
            }
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
        }
    }
}
```
最后运行结果
```java
null
第一次GC操作
调用当前类的finalize方法
obj 不是 null
第二次GC操作
追踪垃圾回收过程：PhantomReferenceTest实例被GC了
obj 是 null
```
从上述运行结果我们知道，第一次尝试获取虚引用的值，发现无法获取的，这是因为虚引用是无法直接获取对象的值，然后进行第一次gc，因为会调用finalize方法，将对象复活了，所以对象没有被回收，但是调用第二次gc操作的时候，因为finalize方法只能执行一次，所以就触发了GC操作，将对象回收了，同时将会触发第二个操作就是 将回收的值存入到引用队列中。
## 终结器引用
它用于实现对象的finalize() 方法，也可以称为终结器引用
无需手动编码，其内部配合引用队列使用
在GC时，终结器引用入队。由Finalizer线程通过终结器引用找到被引用对象调用它的finalize()方法，第二次GC时才回收被引用的对象
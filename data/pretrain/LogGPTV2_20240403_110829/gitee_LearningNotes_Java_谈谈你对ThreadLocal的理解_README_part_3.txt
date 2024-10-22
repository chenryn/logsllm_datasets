假设ThreadLocalMap中的key使用了强引用，那么会出现内存泄漏吗？
此时ThreadLocal的内存图（实线表示强引用）如下：
![image-20200710222559109](images/image-20200710222559109.png)
- 假设在业务代码中使用完ThreadLocal，threadLocal Ref被回收了
- 但是因为threadLocalMap的Entry强引用了threadLocal，造成threadLocal无法被回收。
- 在没有手动删除这个Entry以及CurrentThread依然运行的前提下，始终有强引用链 threadRef->currentThread->threadLocalMap->entry，Entry就不会被回收（Entry中包括了ThreadLocal实例和value），导致Entry内存泄漏。
也就是说，ThreadLocalMap中的key使用了强引用，是无法完全避免内存泄漏的。
### 如果key使用弱引用，那么会出现内存泄漏？
![image-20200710222847567](images/image-20200710222847567.png)
- 同样假设在业务代码中使用完ThreadLocal，threadLocal Ref被回收了。
- 由于ThreadLocalMap只持有ThreadLocal的弱引用，没有任何强引用指向threadlocal实例，所以threadloca就可以顺利被gc回收，此时Entry中的key=null。
- 但是在没有手动删除这个Entry以及CurrentThread依然运行的前提下，也存在有强引用链 threadRef->currentThread->threadLocalMap->entry-> value，value不会被回收，而这块value永远不会被访问到了，导致value内存泄漏。
也就是说，ThreadLocalMap中的key使用了弱引用，也有可能内存泄漏。
### 出现内存泄漏的真实原因
比较以上两种情况，我们就会发现，内存泄漏的发生跟ThreadLocalMap中的key是否使用弱引用是没有关系的。那么内存泄漏的的真正原因是什么呢？
细心的同学会发现，在以上两种内存泄漏的情况中，都有两个前提：
- 没有手动删除这个Entry
- CurrentThread依然运行
第一点很好理解，只要在使用完ThreadLocal，调用其remove方法删除对应的Entry，就能避免内存泄漏。
第二点稍微复杂一点，由于ThreadLocalMap是Thread的一个属性，被当前线程所引用，所以它的生命周期跟Thread一样长。那么在使用完ThreadLocal的使用，如果当前Thread也随之执行结束，ThreadLocalMap自然也会被gc回收，从根源上避免了内存泄漏。
综上，ThreadLocal内存泄漏的根源是：由于ThreadLocalMap的生命周期跟Thread-样长，如果没有手动删除对应key就会导致内存泄漏。
### 为什么要使用弱引用？
根据刚才的分析，我们知道了：无论ThreadLocalMap中的key使用哪种类型引用都无法完全避免内存泄漏，跟使用弱引用没有关系。
要避免内存泄漏有两种方式：
- 使用完ThreadLocal，调用其remove方法删除对应的Entry
- 使用完ThreadLocal，当前Thread也随之运行结束
相对第一种方式，第二种方式显然更不好控制，特别是使用线程池的时候，线程结束是不会销毁的，而是接着放入了线程池中。
也就是说，只要记得在使用完ThreadLocal及时的调用remove，无论key是强引用还是弱引用都不会有问题。
那么为什么key要用弱引用呢？
事实上，在ThreadLocalMap中的 set / getEntry方法中，会对key为null（也即是ThreadLocal为null）进行判断，如果为null的话，那么是会对value置为nul的。
这就意味着使用完ThreadLocal，CurrentThread依然运行的前提下，就算忘记调用remove方法，弱引用比强引用可以多一层保障：弱引用的ThreadLocal会被回收，对应的value在下一次ThreadLocalMap调用set，get，remove中的任一方法的时候会被清除，从而避免内存泄漏。
## Hash冲突的解决
hash冲突的解决是Map中的一个重要内容。我们以hash冲突的解决为线索，来研究一下ThreadLocalMap的核心源码。
首先从ThreadLocal的set方法入手
```java
public void set（T value）{
	Threadt=Thread.currentThread();
    ThreadLoca1.ThreadLocalMap map=getMap(t);
    if（mapl @= nu11）
//调用了ThreadLocalMap的set方法I 
        map.set(this，value);
    else 
        createMap（t，value);
}
ThreadLocal.ThreadLocalMap getMap（Thread t）{
	return t.threadLocals；
}
void createMap（Thread t，T firstValue）{
//调用了ThreadLocalMap的构造方法
t.threadlocals=new ThreadLocal.ThreadtocalMap(this，firstValue);
```
这个方法我们刚才分析过，其作用是设置当前线程绑定的局部变量
- 首先获取当前线程，并根据当前线程获取一个Map 
- 如果获取的Map不为空，则将参数设置到Map中（当前ThreadLocal的引用作为key)（这里调用了ThreadLocalMap的set方法）
- 如果Map为空，则给该线程创建Map，并设置初始值（这里调用了ThreadLocalMap的构造方法）
这段代码有两个地方分别涉及到ThreadLocalMap的两个方法，我们接着分析这两个方法
### 构造方法
ThreadLocalMap(ThreadLocal firstKey, Object firstValue)
![image-20200710224030132](images/image-20200710224030132.png)
构造函数首先创建一个长度为16的Entry数组，然后计算出firstKey对应的索引，然后存储到table中，并设置size和threshold。
重点分析：int i = firstKey.threadLocalHashCode & ( INITIAL_CAPACITY - 1)
**关于：threadLocalHashCode** 
![image-20200710224257493](images/image-20200710224257493.png)
这里定义了一个Atomiclnteger类型，每次获取当前值并加上HASHINCREMENT，HASH_INCREMENT =
0x61c88647，这个值跟斐波那契数列（黄金分割数）有关，其主要目的就是为了让哈希码能均匀的分布在2的n次方的数组里，也就是EntryI table中，这样做可以尽量避免hash冲突。
**关于&（INITIAL_CAPACITY-1）**
计算hash的时候里面采用了hashCode&（size-1）的算法，这相当于取模运算hashCode%size的一个更高效的实现。正是因为这种算法，我们要求size必须是2的整次幂，这也能保证保证在索引不越界的前提下，使得hash发生冲突的次数减小。
### Get方法
![image-20200710224609317](images/image-20200710224609317.png)
![image-20200710224724127](images/image-20200710224724127.png)
代码执行流程
- 首先还是根据key计算出索引i，然后查找位置上的Entry，
- 若是Entry已经存在并且key等于传入的key，那么这时候直接给这个Entry赋新的value值，
- 若是Entry存在，但是key为null，则调用replaceStaleEntry来更换这个key为空的Entry，
- 不断循环检测，直到遇到为null的地方，这时候要是还没在循环过程中return，那么就在这个null的位置新建一个Entry，并且插入，同时size增加1。
最后调用cleanSomeSlots，清理key为null的Entry，最后返回是否清理了Entry，接下来再判断sz是否>=
thresgold达到了rehash的条件，达到的话就会调用rehash函数执行一次全表的扫描清理。
### 线性探测法解决Hash冲突
该方法一次探测下一个地址，直到有空的地址后插入，若整个空间都找不到空余的地址，则产生溢出。
举个例子，假设当前table长度为16，也就是说如果计算出来key的hash值为14，如果table[14]上已经有值，并且其key与当前key不一致，那么就发生了hash冲突，这个时候将1401得到15，取table[15]进行判断，这个时候如果还是冲突会回到0，取table[0]，以此类推，直到可以插入。
按照上面的描述，可以把Entry table看成一个环形数组。
## ThreadLocal使用场景
### 源码使用场景
ThreadLocal的作用主要是做数据隔离，填充的数据只属于当前线程，变量的数据对别的线程而言是相对隔离的，在多线程环境下，如何防止自己的变量被其它线程篡改。
例如，用于 Spring实现事务隔离级别的源码
Spring采用Threadlocal的方式，来保证单个线程中的数据库操作使用的是同一个数据库连接，同时，采用这种方式可以使业务层使用事务时不需要感知并管理connection对象，通过传播级别，巧妙地管理多个事务配置之间的切换，挂起和恢复。
Spring框架里面就是用的ThreadLocal来实现这种隔离，主要是在`TransactionSynchronizationManager`这个类里面，代码如下所示:
```java
private static final Log logger = LogFactory.getLog(TransactionSynchronizationManager.class);
	private static final ThreadLocal> resources =
			new NamedThreadLocal<>("Transactional resources");
	private static final ThreadLocal> synchronizations =
			new NamedThreadLocal<>("Transaction synchronizations");
	private static final ThreadLocal currentTransactionName =
			new NamedThreadLocal<>("Current transaction name");
```
Spring的事务主要是ThreadLocal和AOP去做实现的，我这里提一下，大家知道每个线程自己的链接是靠ThreadLocal保存的就好了
### 用户使用场景1
 除了源码里面使用到ThreadLocal的场景，你自己有使用他的场景么？
之前我们上线后发现部分用户的日期居然不对了，排查下来是SimpleDataFormat的锅，当时我们使用SimpleDataFormat的parse()方法，内部有一个Calendar对象，调用SimpleDataFormat的parse()方法会先调用Calendar.clear（），然后调用Calendar.add()，如果一个线程先调用了add()然后另一个线程又调用了clear()，这时候parse()方法解析的时间就不对了。
其实要解决这个问题很简单，让每个线程都new 一个自己的 SimpleDataFormat就好了，但是1000个线程难道new1000个SimpleDataFormat？
所以当时我们使用了线程池加上ThreadLocal包装SimpleDataFormat，再调用initialValue让每个线程有一个SimpleDataFormat的副本，从而解决了线程安全的问题，也提高了性能。
### 用户使用场景2
我在项目中存在一个线程经常遇到横跨若干方法调用，需要传递的对象，也就是上下文（Context），它是一种状态，经常就是是用户身份、任务信息等，就会存在过渡传参的问题。
使用到类似责任链模式，给每个方法增加一个context参数非常麻烦，而且有些时候，如果调用链有无法修改源码的第三方库，对象参数就传不进去了，所以我使用到了ThreadLocal去做了一下改造，这样只需要在调用前在ThreadLocal中设置参数，其他地方get一下就好了。
```java
before
void work(User user) {
    getInfo(user);
    checkInfo(user);
    setSomeThing(user);
    log(user);
}
then
void work(User user) {
try{
	  threadLocalUser.set(user);
	  // 他们内部  User u = threadLocalUser.get(); 就好了
    getInfo();
    checkInfo();
    setSomeThing();
    log();
    } finally {
     threadLocalUser.remove();
    }
}
```
我看了一下很多场景的cookie，session等数据隔离都是通过ThreadLocal去做实现的
在Android中，Looper类就是利用了ThreadLocal的特性，保证每个线程只存在一个Looper对象。
```java
static final ThreadLocal sThreadLocal = new ThreadLocal();
private static void prepare(boolean quitAllowed) {
    if (sThreadLocal.get() != null) {
        throw new RuntimeException("Only one Looper may be created per thread");
    }
    sThreadLocal.set(new Looper(quitAllowed));
}
```
## 参考
https://blog.csdn.net/qq_35190492/article/details/107599875
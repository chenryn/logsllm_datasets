HashMap的容量为什么是2的n次幂，和这个(n - 1) & hash的计算方法有着千丝万缕的关系，符号&是按位与的计算，这是位运算，计算机能直接运算，特别高效，按位与&的计算方法是，只有当对应位置的数据都为1时，运算结果也为1，当HashMap的容量是2的n次幂时，(n-1)的2进制也就是1111111***111这样形式的，这样与添加元素的hash值进行位运算时，能够充分的散列，使得添加的元素均匀分布在HashMap的每个位置上，减少hash碰撞，下面举例进行说明。
当HashMap的容量是16时，它的二进制是10000，(n-1)的二进制是01111，与hash值得计算结果如下:
![image-20200405105533985](images/image-20200405105533985.png)
上面四种情况我们可以看出，不同的hash值，和(n-1)进行位运算后，能够得出不同的值，使得添加的元素能够均匀分布在集合中不同的位置上，避免hash碰撞，下面就来看一下HashMap的容量不是2的n次幂的情况，当容量为10时，二进制为01010，(n-1)的二进制是01001，向里面添加同样的元素，结果为：
![image-20200405105704798](images/image-20200405105704798.png)
可以看出，有三个不同的元素进过&运算得出了同样的结果，严重的hash碰撞了。
终上所述，HashMap计算添加元素的位置时，使用的位运算，这是特别高效的运算；另外，HashMap的初始容量是2的n次幂，扩容也是2倍的形式进行扩容，是因为容量是2的n次幂，可以使得添加的元素均匀分布在HashMap中的数组上，减少hash碰撞，避免形成链表的结构，使得查询效率降低
## JDK1.8结构变化
由JDK1.7的，数组 + 链表 
JDK1.8变为：数组 + 链表 + 红黑树
具体触发条件为：某个链表连接的个数大于8，并且总的容量大于64的时候，那么会把原来的链表转换成红黑树
这么做的好处是什么：除了添加元素外，查询和删除效率比链表快
红黑树查询、增加和删除的时间复杂度：O(log2n) 
链表的查询和删除的时间复杂度： O(n)，插入为：O(1)
## 为什么HashMap使用红黑树而不是AVL树
在JDK1.8版本后，Java对HashMap做了改进，在链表长度大于8的时候，将后面的数据由链表改成了红黑树，以加快检索的速度
但是为什么使用的红黑树，而不是AVL树或者其它树呢？
> 最主要的原因：在CurrentHashMap中加锁了，实际上就是读写锁，如果写冲突就会等待，如果插入的时间过长，必然会导致等待的时间变长，而红黑树相比于AVL树，它的插入更快。
红黑树和AVL树都是常见的平衡二叉树，它们的查找，删除，修改的时间复杂度都是 O(log n)
AVL树和红黑树相比有以下的区别
- AVL树是更加严格的平衡，因此可以提供更快的查找速度，一般读取查找密集型任务，适用AVL树
- 红黑树更适合插入修改密集型任务
- 通常，AVL树的旋转比红黑树的旋转更加难以平衡和调试
### 总结
- AVL以及红黑树都是高度平衡的树形结构，它们非常的相似，真正的区别在于任何添加、删除操作时完成的旋转操作次数
- 两种时间复杂度都是O(logN)，其中N是叶子的数量，但实际上AVL树在查找密集型任务上更快，利用更好的平衡，树遍历平均更短，另一方面，插入和删除上，AVL树较慢，因为需要更高的旋转次数才能在修改时正确地重新平衡数据结构
- 在AVL树中，从根到任何叶子节点的最短路径和最长路径之间的差异最多为1，在红黑树中，差异可以是2倍
- 两个都是O(logN)查找，但是平衡二叉树可能需要 O(logN)旋转，而红黑树需要最多两次旋转使其达到平衡（尽可能需要检查O(logN)节点以确定旋转的位置），旋转本身是O(1)操作，因为你只需要移动指针。
## ConcurrentHashMap变化
### 为何JDK8要放弃分段锁？
由原来的分段锁，变成了CAS，也就是通过无锁化设计替代了阻塞同步的加锁操作，性能得到了提高。
- 通过使用Synchronized + CAS的方式实现并发访问
通过分段锁的方式提高了并发度。分段是一开始就确定的了，后期不能再进行扩容的，其中的段Segment继承了重入锁ReentrantLock，有了锁的功能，同时含有类似HashMap中的数组加链表结构（这里没有使用红黑树），虽然Segment的个数是不能扩容的，但是单个Segment里面的数组是可以扩容的。
JDK1.8的ConcurrentHashMap摒弃了1.7的segment设计，而是JDK1.8版本的HashMap的基础上实现了线程安全的版本，即也是采用**数组+链表+红黑树**的形式，虽然ConcurrentHashMap的读不需要锁，但是需要保证能读到最新数据，所以必须加volatile。即数组的引用需要加volatile，同时一个Node节点中的val和next属性也必须要加volatile。
至于为什么抛弃Segment的设计，是因为分段锁的这个段不太好评定，如果我们的Segment设置的过大，那么隔离级别也就过高，那么就有很多空间被浪费了，也就是会让某些段里面没有元素，如果太小容易造成冲突
### 弃用的原因
通过上述描述以及查看官方文档，弃用分段锁的原因主要有以下几点
- 加入多个分段锁 浪费了内存空间
- 生产环境中，map在放入时 竞争同一个锁的概率非常小，分段锁反而会造成更新等操作的长时间等待
- 为了提高GC的效率
### 新的同步方案
既然弃用了分段锁，那么一定有新的线程安全方案，我们来看看源码是怎么解决线程安全的呢？
> 源码保留segment代码，但是并没有使用
首先通过hash找到对应链表后，查看是否第一个object，如果是直接用CAS原则插入，无需加锁
```java
Node f; int n, i, fh; K fk; V fv;
if (tab == null || (n = tab.length) == 0)
    // 这里在整个map第一次操作时，初始化hash桶， 也就是一个table
    tab = initTable(); 
else if ((f = tabAt(tab, i = (n - 1) & hash)) == null) {
    //如果是第一个object， 则直接cas放入， 不用锁
    if (casTabAt(tab, i, null, new Node(hash, key, value)))
        break;                   
}
```
然后， 如果不是链表第一个object， 则直接用链表第一个object加锁，这里加的锁是Synchronized，虽然效率不如 ReentrantLock， 但节约了空间，这里会一直用第一个object为锁， 直到重新计算map大小， 比如扩容或者操作了第一个object为止。
```java
// 这里的f即为第一个链表的object
synchronized (f) {
    if (tabAt(tab, i) == f) {
        if (fh >= 0) {
            binCount = 1;
            for (Node e = f;; ++binCount) {
                K ek;
                if (e.hash == hash &&
                    ((ek = e.key) == key ||
                     (ek != null && key.equals(ek)))) {
                    oldVal = e.val;
                    if (!onlyIfAbsent)
                        e.val = value;
                    break;
                }
                Node pred = e;
                if ((e = e.next) == null) {
                    pred.next = new Node(hash, key, value);
                    break;
                }
            }
        }
        else if (f instanceof TreeBin) { // 太长会用红黑树
            Node p;
            binCount = 2;
            if ((p = ((TreeBin)f).putTreeVal(hash, key,
                                           value)) != null) {
                oldVal = p.val;
                if (!onlyIfAbsent)
                    p.val = value;
            }
        }
        else if (f instanceof ReservationNode)
            throw new IllegalStateException("Recursive update");
    }
}
```
分段锁技术是在java8以前使用的，在java8已经弃用了，更新为synchronized+cas
## ConcurrentHashMap为什么要使用synchronized而不是如ReentranLock这样的可重入锁？
这个问题我们将要从几个角度来讨论
- 锁的粒度
  - 首先锁的粒度没有变粗，甚至变得更细了。每次扩容一次，ConcurrentHashMap的并发度就扩大
- Hash冲突
  - 在JDK1.7中，ConcurrentHashMap从二次hash方式（Segment - > HashEntry）能够快速的找到查找的元素，在JDK1.8中，通过链表+红黑树的形式，弥补了put、get时的性能差距。
- 扩容
  - JDK1.8中，在ConcurrentHashMap进行扩容时，其他线程可以通过检测数组中的节点决定是否对这条链表进行扩容，减少了扩容的粒度，提高了扩容的效率。
**为什么是用Synchronized 而不是 ReentrantLock？**
- 减少内存开销
  - 假设使用可重入锁来获得同步支持，那么每个节点都需要通过继承AQS来获得同步支持。但并不是每个节点都需要同步支持，只有链表的头结点（红黑树的根节点）需要同步，这无疑带来了巨大的浪费
- 获得JVM支持
  - 可重入锁毕竟是API这个级别的，后续的性能优化空间 很小
  - Synchronized则是由JVM直接支持，JVM能够在运行时做出对应的优化措施：锁粗化，锁消除，锁自旋等。这就是使得Synchronized能够随着JDK版本的升级而无需改动代码的前提下获得性能上的提升。
## 内存结构优化
取消永久区，把方法区 放在 元空间中
> 方法区主要用于存储一些类模板
![image-20200405115011067](images/image-20200405115011067.png)
OOM错误发生概率降低
同时相关JVM调优命令变为：
> MetaspaceSize
>
> MaxMetaspaceSize
## 参考
- https://blog.csdn.net/zhangvalue/article/details/101483736
- https://blog.csdn.net/apeopl/article/details/88935422
- https://blog.csdn.net/chenyiminnanjing/article/details/82706942
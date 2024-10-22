# Java8新特性
## 主要特性
- Lambda表达式
- 函数式接口
- 方法引用与构造器引用
- Stream API
- 接口中默认方法与静态方法
- 新时间日期API
- 最大化减少空指针异常（Optional）
- 。。。。
## HashMap1.7
在JDK1.7 到 JDK1.8的时候，对HashMap做了优化
首先JDK1.7的HashMap当出现Hash碰撞的时候，最后插入的元素会放在前面，这个称为 “头插法”
>JDK7用头插是考虑到了一个所谓的热点数据的点(新插入的数据可能会更早用到)，但这其实是个伪命题,因为JDK7中rehash的时候，旧链表迁移新链表的时候，如果在新表的数组索引位置相同，则链表元素会倒置(就是因为头插) 所以最后的结果 还是打乱了插入的顺序 所以总的来看支撑JDK7使用头插的这点原因也不足以支撑下去了 所以就干脆换成尾插 一举多得
![image-20200405101639700](images/image-20200405101639700.png)
## HashMap1.7存在死链问题
参考：[hashmap扩容时死循环问题](https://blog.csdn.net/chenyiminnanjing/article/details/82706942)
在JDK1.8以后，由头插法改成了尾插法，因为头插法还存在一个死链的问题
在说死链问题时，我们先从Hashmap存储数据说起，下面这个是HashMap的put方法
```
public V put(K key, V value)
{
    ......
    //计算Hash值
    int hash = hash(key.hashCode());
    int i = indexFor(hash, table.length);
    //各种校验吧
    for (Entry e = table[i]; e != null; e = e.next) {
        Object k;
        if (e.hash == hash && ((k = e.key) == key || key.equals(k))) {
            V oldValue = e.value;
            e.value = value;
            e.recordAccess(this);
            return oldValue;
        }
    }
    modCount++;
    //该key不存在，需要增加一个结点
    addEntry(hash, key, value, i);
    return null;
}
```
这里添加一个节点需要检查是否超出容量，出现一个负载因子
```
void addEntry(int hash, K key, V value, int bucketIndex)
{
    Entry e = table[bucketIndex];
    table[bucketIndex] = new Entry(hash, key, value, e);
    //查看当前的size是否超过了我们设定的阈值threshold，如果超过，需要resize
    if (size++ >= threshold)
        resize(2 * table.length);//扩容都是2倍2倍的来的，
}
```
> HashMap有 负载因子：0.75，以及 初始容量：16，扩容阈值：16*0.75 = 12，当HashMap达到扩容的条件时候，会把HashMap中的每个元素，重新进行运算Hash值，打入到扩容后的数组中。
既然新建了一个更大尺寸的hash表，然后把数据从老的Hash表中迁移到新的Hash表中。
```
void resize(int newCapacity)
{
    Entry[] oldTable = table;
    int oldCapacity = oldTable.length;
    ......
    //创建一个新的Hash Table
    Entry[] newTable = new Entry[newCapacity];
    //将Old Hash Table上的数据迁移到New Hash Table上
    transfer(newTable);
    table = newTable;
    threshold = (int)(newCapacity * loadFactor);
}
```
重点在这个transfer()方法
```
void transfer(Entry[] newTable)
{
    Entry[] src = table;
    int newCapacity = newTable.length;
    //下面这段代码的意思是：
    //  从OldTable里摘一个元素出来，然后放到NewTable中
    for (int j = 0; j  e = src[j];
        if (e != null) {
            src[j] = null;
            do {
                Entry next = e.next;
                int i = indexFor(e.hash, newCapacity);
                e.next = newTable[i];
                newTable[i] = e;
                e = next;
            } while (e != null);
        }
    }
}
```
do循环里面的是最能说明问题的，当只有一个线程的时候：
![image-20200405110723887](images/image-20200405110723887.png)
最上面的是old hash 表，其中的Hash表的size=2, 所以key = 3, 7, 5，在mod 2以后都冲突在table[1]这里了。接下来的三个步骤是Hash表 扩容变成4，然后在把所有的元素放入新表
```
do {
    Entry next = e.next; // 3这个顺序。
然后线程一被调度回来执行：
先是执行 newTalbe[i] = e;
然后是e = next，导致了e指向了key(7)，
而下一次循环的next = e.next导致了next指向了key(3)
注意看图里面的线，线程1指向线程2里面的key3.
![image-20200405111205298](images/image-20200405111205298.png)
线程一接着工作。把key(7)摘下来，放到newTable[i]的第一个，然后把e和next往下移。
![image-20200405111254924](images/image-20200405111254924.png)
这时候，原来的线程2里面的key7的e和key3的next没了，e=key3,next=null。
当继续执行，需要将key3加回到key7的前面。
e.next = newTable[i] 导致 key(3).next 指向了 key(7)
注意：此时的key(7).next 已经指向了key(3)， 环形链表就这样出现了。
![image-20200405111319072](images/image-20200405111319072.png)
线程2生成的e和next的关系影响到了线程1里面的情况。从而打乱了正常的e和next的链。于是，当我们的线程一调用到，HashTable.get(11)时，即又到了3这个位置，需要插入新的，那这会就e 和next就乱了
## HashMap每次扩容为什么是2倍
参考：[HashMap初始容量为什么是2的n次幂](https://blog.csdn.net/apeopl/article/details/88935422)
首先看向HashMap中添加元素是怎么存放的
![image-20200405105335235](images/image-20200405105335235.png)
![image-20200405105401674](images/image-20200405105401674.png)
 第一个截图是向HashMap中添加元素putVal()方法的部分源码，可以看出，向集合中添加元素时，会使用(n - 1) & hash的计算方法来得出该元素在集合中的位置；而第二个截图是HashMap扩容时调用resize()方法中的部分源码，可以看出会新建一个tab，然后遍历旧的tab，将旧的元素进过e.hash & (newCap - 1)的计算添加进新的tab中，也就是(n - 1) & hash的计算方法，其中n是集合的容量，hash是添加的元素进过hash函数计算出来的hash值
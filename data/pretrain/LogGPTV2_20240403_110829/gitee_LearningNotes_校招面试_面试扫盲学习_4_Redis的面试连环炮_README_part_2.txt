- RDB每次在fork子进程来执行RDB快照数据生成的时候，如果数据文件特别大，可能会导致对客户端提供的服务暂停数毫秒，或者甚至数秒
  - 一般不要让RDB的间隔太长，否则每次生成的RDB文件太长，会对Redis本身的性能会有影响
### AOF持久化的优点
- AOF可以更好的保护数据不丢失，一般AOF会间隔一秒，通过一个后台线程执行一次fsync操作，最多丢失1秒
- AOF日志文件以append-only模式写入，所有没有任何磁盘寻址开销，写入性能非常高，而且文件不容易破损，即使文件尾部破损，也很容易快速修复。
- AOF日志文件及时过大的时候，出现后台的重写操作，也不会影响客户端的读写，因为rewrite log 的时候，会对其中的数据进行压缩，创建出一份需要恢复数据的最小日志出来，再创建新日志文件的时候，老的日志文件还是照常写入，当新的merge后的日志文件ready的时候，再交换新老日志文件即可。
- AOF日志文件的命令通过非常可读的方式进行记录，这个特性非常适合做灾难性的误删除的紧急恢复，比如某人不小心用了 flushall命令，清空了整个Redis数据，只要这个时候后台rewrite还没有发生，那么就可以立即拷贝AOF文件，将最后一条flushall命令删除了，然后再将该AOF文件放回去，就可以通过恢复机制，自动回复所有的数据。
### AOF持久化机制的缺点
- 对于同一份数据来说，AOF日志通常比RDB数据快照文件更大
- AOF开启后，支持写QPS会比RDB支持的写QPS低，因为AOF一般会配置成每秒fsync一次日志文件，因此这也就造成了性能不是很高。
  - 如果你要保证一条数据都不丢，也可以的，AOF的fsync设置成每次写入一条数据，fsync一次，这样Redis的QPS会大降。
- AOF这种较为复杂的基于命令日志/merge/回放的方式，比基于RDB每次持久化一份完整的数据快照的方式，更加脆弱一些，容易有BUG，不过AOF就是为了避免rewrite过程导致的BUG，因此每次rewrite并不是基于旧的指令来进行merge的，而是基于当时内存中数据进行指令的重新构建，这与健壮性会好一些。
- 唯一的缺点：就是做数据恢复的时候，会比较慢，还有做冷备，定期的被封，不太方便，可能要自己手动写复杂的脚本去做。
### RDB和AOF的选择
- 不要仅仅使用RDB，因为那样会导致你丢失很多的数据
- 也不要仅仅使用AOF，因为这样有两个问题
  - AOF做冷备，没有RDB冷备恢复快
  - RDB每次简单粗暴的生成数据快照，更加健壮，可以避免AOF这种复杂的被封和恢复机制的BUG
- 综合使用AOF和RDB两种持久化机制，用AOF来保证数据不丢失，作为数据恢复的第一选择，用RDB来做不同程度的冷备，在AOF文件都丢失或者损坏不可用的时候，可以使用RDB来进行快速的数据恢复。
## Redis的线程模型
### 文件事件处理器
Redis基于reactor模式开发了网络事件处理器，这个处理器叫做文件事件处理器，file event handler，这个文件事件处理器是单线程的，因此Redis才叫做单线程的模型，采用IO多路复用机制同时监听多个socket，根据socket上的事件来选择相应的事件处理器来处理这个事件。
文件事件处理器是单线程模式下运行的，但是通过IO多路复用机制监听了多个socket，可以实现高性能的网络通信模型，又可以跟内部的其它单线程的模块进行对接，保证了Redis内部的线程模型的简单性。
文件事件处理器的结构包含4个部分：多个socket，IO多路复用程序，文件事件分派器，事件处理器等。
多个socket可能并发的产生不同的操作，每个操作对应不同的文件事件，但是IO多路复用程序会监听多个socket，但是会把socket放入到一个队列中排队，每次从队列中取出一个socket给事件分派器，事件分派器把socket给对应的时间处理器。
![image-20200421185741787](images/image-20200421185741787.png)
![image-20200421185725418](images/image-20200421185725418.png)
每次我们一个socket请求过来 和 redis中的 server socket建立连接后，通过IO多路复用程序，就会往队列中插入一个socket，文件事件分派器就是将队列中的socket取出来，分派到对应的处理器，在处理器处理完成后，才会从队列中在取出一个。
这里也就是用一个线程，监听了客户端的所有请求，被称为Redis的单线程模型。
## 为什么Redis单线程模型效率这么高？
- 纯内存操作
- 核心是非阻塞的IO多路复用机制
- 单线程反而避免了多线程频繁上下文切换的问题
## Redis的过期策略
### Redis中的数据为什么会丢失
之前有同学问过我，说我们生产环境的redis怎么经常会丢掉一些数据？写进去了，过一会儿可能就没了。我的天，同学，你问这个问题就说明redis你就没用对啊。redis是缓存，你给当存储了是吧？
啥叫缓存？用内存当缓存。内存是无限的吗，内存是很宝贵而且是有限的，磁盘是廉价而且是大量的。可能一台机器就几十个G的内存，但是可以有几个T的硬盘空间。redis主要是基于内存来进行高性能、高并发的读写操作的。
那既然内存是有限的，比如redis就只能用10个G，你要是往里面写了20个G的数据，会咋办？当然会干掉10个G的数据，然后就保留10个G的数据了。那干掉哪些数据？保留哪些数据？当然是干掉不常用的数据，保留常用的数据了。所以说，这是缓存的一个最基本的概念，数据是会过期的，要么是你自己设置个过期时间，要么是redis自己给干掉。
```
set key value 过期时间（1小时）
set进去的key，1小时之后就没了，就失效了
```
### 数据明明都过期了，怎么还占用着内存啊？
还有一种就是如果你设置好了一个过期时间，你知道redis是怎么给你弄成过期的吗？什么时候删除掉？如果你不知道，之前有个学员就问了，为啥好多数据明明应该过期了，结果发现redis内存占用还是很高？那是因为你不知道redis是怎么删除那些过期key的。
redis 内存一共是10g，你现在往里面写了5g的数据，结果这些数据明明你都设置了过期时间，要求这些数据1小时之后都会过期，结果1小时之后，你回来一看，redis机器，怎么内存占用还是50%呢？5g数据过期了，我从redis里查，是查不到了，结果过期的数据还占用着redis的内存。
### 定期删除和惰性删除
我们Redis设置了过期时间，其实内部是 定期删除 + 惰性删除两个再起作用的。
所谓定期删除，指的是redis默认是每隔100ms就随机抽取一些设置了过期时间的key，检查其是否过期，如果过期就删除。假设redis里放了10万个key，都设置了过期时间，你每隔几百毫秒，就检查10万个key，那redis基本上就死了，cpu负载会很高的，消耗在你的检查过期key上了。注意，这里可不是每隔100ms就遍历所有的设置过期时间的key，那样就是一场性能上的灾难。实际上redis是每隔100ms随机抽取一些key来检查和删除的。
但是问题是，定期删除可能会导致很多过期key到了时间并没有被删除掉，那咋整呢？所以就是惰性删除了。这就是说，在你获取某个key的时候，redis会检查一下 ，这个key如果设置了过期时间那么是否过期了？如果过期了此时就会删除，不会给你返回任何东西。
并不是key到时间就被删除掉，而是你查询这个key的时候，redis再懒惰的检查一下
通过上述两种手段结合起来，保证过期的key一定会被干掉。
很简单，就是说，你的过期key，靠定期删除没有被删除掉，还停留在内存里，占用着你的内存呢，除非你的系统去查一下那个key，才会被redis给删除掉。
但是实际上这还是有问题的，如果定期删除漏掉了很多过期key，然后你也没及时去查，也就没走惰性删除，此时会怎么样？如果大量过期key堆积在内存里，导致redis内存块耗尽了，咋整？
答案是：走内存淘汰机制。
### Redis内存淘汰机制
如果redis的内存占用过多的时候，此时会进行内存淘汰，有如下一些策略：
```
redis 10个key，现在已经满了，redis需要删除掉5个key
1个key，最近1分钟被查询了100次
1个key，最近10分钟被查询了50次
1个key，最近1个小时倍查询了1次
```
1）noeviction：当内存不足以容纳新写入数据时，新写入操作会报错，这个一般没人用吧，实在是太恶心了
2）allkeys-lru：当内存不足以容纳新写入数据时，在键空间中，移除最近最少使用的key（这个是最常用的）
3）allkeys-random：当内存不足以容纳新写入数据时，在键空间中，随机移除某个key，这个一般没人用吧，为啥要随机，肯定是把最近最少使用的key给干掉啊
4）volatile-lru：当内存不足以容纳新写入数据时，在设置了过期时间的键空间中，移除最近最少使用的key（这个一般不太合适）
5）volatile-random：当内存不足以容纳新写入数据时，在设置了过期时间的键空间中，随机移除某个key
6）volatile-ttl：当内存不足以容纳新写入数据时，在设置了过期时间的键空间中，有更早过期时间的key优先移除
很简单，你写的数据太多，内存满了，或者触发了什么条件，redis lru，自动给你清理掉了一些最近很少使用的数据
## Redis中的LRU算法
Java版本的LRU
```
public class LRUCache extends LinkedHashMap {
private final int CACHE_SIZE;
    // 这里就是传递进来最多能缓存多少数据
    public LRUCache(int cacheSize) {
        super((int) Math.ceil(cacheSize / 0.75) + 1, 0.75f, true); // 这块就是设置一个hashmap的初始大小，同时最后一个true指的是让linkedhashmap按照访问顺序来进行排序，最近访问的放在头，最老访问的就在尾
        CACHE_SIZE = cacheSize;
    }
    @Override
    protected boolean removeEldestEntry(Map.Entry eldest) {
        return size() > CACHE_SIZE; // 这个意思就是说当map中的数据量大于指定的缓存个数的时候，就自动删除最老的数据
    }
```
## 如何保证Redis的高并发及高可用？
如何保证Redis的高并发和高可用？
redis的主从复制原理能介绍一下么？
redis的哨兵原理能介绍一下么？
### 剖析
就是如果你用redis缓存技术的话，肯定要考虑如何用redis来加多台机器，保证redis是高并发的，还有就是如何让Redis保证自己不是挂掉以后就直接死掉了，redis高可用
我这里会选用我之前讲解过这一块内容，redis高并发、高可用、缓存一致性
redis高并发：主从架构，一主多从，一般来说，很多项目其实就足够了，单主用来写入数据，单机几万QPS，多从用来查询数据，多个从实例可以提供每秒10万的QPS。
redis高并发的同时，还需要容纳大量的数据：一主多从，每个实例都容纳了完整的数据，比如redis主就10G的内存量，其实你就最对只能容纳10g的数据量。如果你的缓存要容纳的数据量很大，达到了几十g，甚至几百g，或者是几t，那你就需要redis集群，而且用redis集群之后，可以提供可能每秒几十万的读写并发。
redis高可用：如果你做主从架构部署，其实就是加上哨兵就可以了，就可以实现，任何一个实例宕机，自动会进行主备切换。
##  Redis如何通过读写分离来承受百万的QPS
### redis高并发跟整个系统的高并发之间的关系
redis，你要搞高并发的话，不可避免，要把底层的缓存搞得很好
mysql，高并发，做到了，那么也是通过一系列复杂的分库分表，订单系统，事务要求的，QPS到几万，比较高了
要做一些电商的商品详情页，真正的超高并发，QPS上十万，甚至是百万，一秒钟百万的请求量
光是redis是不够的，但是redis是整个大型的缓存架构中，支撑高并发的架构里面，非常重要的一个环节
#### 总结
Redis实现高并发：一主多从，一般来说，很多项目其实就足够了，单主用来写数据，单机几万QPS，多从用来查询数据，多个从实例可以提供每秒10万QPS
Redis高并发的同时，还需要容纳大量的数据：一主多从，每个实例都容纳了完整的数据，比如Redis主就10G内存量，其实你就可以对只能容纳10G的数据量。如果你的缓存要容纳的数据量很大，达到了几十G，甚至几百G，那就需要使用到Redis集群，而且用Redis集群之后，提供可能每秒几十万的读写并发。
Redis高可用：如果用主从架构部署，在加上哨兵就可以实现任何一个实例宕机，就会自动进行主备切换。
## Redis哨兵架构
### 哨兵介绍
sentinal，中文名是哨兵
哨兵是redis集群架构中非常重要的一个组件，主要功能如下
- 集群监控，负责监控redis master和slave进程是否正常工作
- 消息通知，如果某个redis实例有故障，那么哨兵负责发送消息作为报警通知给管理员
- 故障转移，如果master node挂掉了，会自动转移到slave node上
- 配置中心，如果故障转移发生了，通知client客户端新的master地址
哨兵本身也是分布式的，作为一个哨兵集群去运行，互相协同工作
- 故障转移时，判断一个master node是宕机了，需要大部分的哨兵都同意才行，涉及到了分布式选举的问题
- 即使部分哨兵节点挂掉了，哨兵集群还是能正常工作的，因为如果一个作为高可用机制重要组成部分的故障转移系统本身是单点的，那就很坑爹了
目前采用的是sentinal 2版本，sentinal 2相对于sentinal 1来说，重写了很多代码，主要是让故障转移的机制和算法变得更加健壮和简单
### 哨兵的核心知识
- 哨兵至少需要3个实例，来保证自己的健壮性
- 哨兵 + redis主从的部署架构，是不会保证数据零丢失的，只能保证redis集群的高可用性
- 对于哨兵 + redis主从这种复杂的部署架构，尽量在测试环境和生产环境，都进行充足的测试和演练
### 为什么Redis的哨兵集群只有2个节点无法正常工作？
哨兵集群必须部署2个以上节点
如果哨兵集群仅仅部署了个2个哨兵实例，s1 和 s2，quorum=1
```
+----+         +----+
| M1 |---------| R1 |
| S1 |         | S2 |
+----+         +----+
```
Configuration: quorum = 1
master宕机，s1和s2中只要有1个哨兵认为master宕机就可以还行切换，同时s1和s2中会选举出一个哨兵来执行故障转移同时这个时候，需要majority，也就是大多数哨兵都是运行的，2个哨兵的majority就是2（2的majority=2，3的majority=2，5的majority=3，4的majority=2），2个哨兵都运行着，就可以允许执行故障转移但是如果整个M1和S1运行的机器宕机了，那么哨兵只有1个了，此时就没有majority来允许执行故障转移，虽然另外一台机器还有一个R1，但是故障转移不会执行
### 经典的3节点哨兵集群
```
       +----+
       | M1 |
       | S1 |
       +----+
          |
+----+    |    +----+
| R2 |----+----| R3 |
| S2 |         | S3 |
+----+         +----+
```
Configuration: quorum = 2，majority
如果M1所在机器宕机了，那么三个哨兵还剩下2个，S2和S3可以一致认为master宕机，然后选举出一个来执行故障转移，同时3个哨兵的majority是2，所以还剩下的2个哨兵运行着，就可以允许执行故障转移
### Redis主备切换的数据丢失问题：异步复制、集群脑裂
主备切换的过程，可能会导致数据丢失
#### 异步复制导致的数据丢失
因为master -> slave的复制是异步的，所以可能有部分数据还没复制到slave，master就宕机了，此时这些部分数据就丢失了。
![异步复制导致的数据丢失问题](images/异步复制导致的数据丢失问题.png)
#### 脑裂导致的数据丢失
脑裂，也就是说，某个master所在机器突然脱离了正常的网络，跟其他slave机器不能连接，但是实际上master还运行着，此时哨兵可能就会认为master宕机了，然后开启选举，将其他slave切换成了master
这个时候，集群里就会有两个master，也就是所谓的脑裂。此时虽然某个slave被切换成了master，但是可能client还没来得及切换到新的master，还继续写向旧master的数据可能也丢失了
因此旧master再次恢复的时候，会被作为一个slave挂到新的master上去，自己的数据会清空，重新从新的master复制数据
![集群脑裂导致的数据丢失问题](images/集群脑裂导致的数据丢失问题.png)
同时原来的master节点上的，client像 旧的 master中写入数据，当网络分区恢复正常后，client写的数据就会因为复制，导致数据的丢失。
#### 解决异步复制和脑裂导致数据丢失
```
min-slaves-to-write 1
min-slaves-max-lag 10
```
要求至少有1个slave，数据复制和同步的延迟不能超过10秒
如果说一旦所有的slave，数据复制和同步的延迟都超过了10秒钟，那么这个时候，master就不会再接收任何请求了，上面两个配置可以减少异步复制和脑裂导致的数据丢失
- 减少异步复制的数据丢失
有了min-slaves-max-lag这个配置，就可以确保说，一旦slave复制数据和ack延时太长，就认为可能master宕机后损失的数据太多了，那么就拒绝写请求，这样可以把master宕机时由于部分数据未同步到slave导致的数据丢失降低的可控范围内
![异步复制导致数据丢失如何降低损失](images/异步复制导致数据丢失如何降低损失.png)
- 减少脑裂的数据丢失
如果一个master出现了脑裂，跟其他slave丢了连接，那么上面两个配置可以确保说，如果不能继续给指定数量的slave发送数据，而且slave超过10秒没有给自己ack消息，那么就直接拒绝客户端的写请求，这样脑裂后的旧master就不会接受client的新数据，也就避免了数据丢失，上面的配置就确保了，如果跟任何一个slave丢了连接，在10秒后发现没有slave给自己ack，那么就拒绝新的写请求，因此在脑裂场景下，最多就丢失10秒的数据![脑裂导致数据丢失的问题如何降低损失](images/脑裂导致数据丢失的问题如何降低损失.png)
### Redis哨兵的底层原理
#### sdown和odown转换机制
sdown和odown两种失败状态
sdown是主观宕机，就一个哨兵如果自己觉得一个master宕机了，那么就是主观宕机
odown是客观宕机，如果quorum数量的哨兵都觉得一个master宕机了，那么就是客观宕机
sdown达成的条件很简单，如果一个哨兵ping一个master，超过了is-master-down-after-milliseconds指定的毫秒数之后，就主观认为master宕机
sdown到odown转换的条件很简单，如果一个哨兵在指定时间内，收到了quorum指定数量的其他哨兵也认为那个master是sdown了，那么就认为是odown了，客观认为master宕机
#### 哨兵集群的自动发现机制
哨兵互相之间的发现，是通过redis的pub/sub系统实现的，每个哨兵都会往__sentinel__:hello这个channel里发送一个消息，这时候所有其他哨兵都可以消费到这个消息，并感知到其他的哨兵的存在
每隔两秒钟，每个哨兵都会往自己监控的某个master+slaves对应的__sentinel__:hello channel里发送一个消息，内容是自己的host、ip和runid还有对这个master的监控配置
每个哨兵也会去监听自己监控的每个master+slaves对应的__sentinel__:hello channel，然后去感知到同样在监听这个master+slaves的其他哨兵的存在
每个哨兵还会跟其他哨兵交换对master的监控配置，互相进行监控配置的同步
#### slave配置的自动纠正
哨兵会负责自动纠正slave的一些配置，比如slave如果要成为潜在的master候选人，哨兵会确保slave在复制现有master的数据; 如果slave连接到了一个错误的master上，比如故障转移之后，那么哨兵会确保它们连接到正确的master上
#### slave->master选举算法
如果一个master被认为odown了，而且majority哨兵都允许了主备切换，那么某个哨兵就会执行主备切换操作，此时首先要选举一个slave来，会考虑slave的一些信息
- 跟master断开连接的时长
- slave优先级
- 复制offset
- run id
如果一个slave跟master断开连接已经超过了down-after-milliseconds的10倍，外加master宕机的时长，那么slave就被认为不适合选举为master
```
(down-after-milliseconds * 10) + milliseconds_since_master_is_in_SDOWN_state
```
接下来会对slave进行排序
- 按照slave优先级进行排序，slave priority越低，优先级就越高
- 如果slave priority相同，那么看replica offset，哪个slave复制了越多的数据，offset越靠后，优先级就越高
- 如果上面两个条件都相同，那么选择一个run id比较小的那个slave
#### quorum和majority
每次一个哨兵要做主备切换，首先需要quorum数量的哨兵认为odown，然后选举出一个哨兵来做切换，这个哨兵还得得到majority哨兵的授权，才能正式执行切换
如果quorum = majority，那么必须quorum数量的哨兵都授权，比如5个哨兵，quorum是5，那么必须5个哨兵都同意授权，才能执行切换
#### configuration epoch
哨兵会对一套redis master+slave进行监控，有相应的监控的配置
执行切换的那个哨兵，会从要切换到的新master（salve->master）那里得到一个configuration epoch，这就是一个version号，每次切换的version号都必须是唯一的
如果第一个选举出的哨兵切换失败了，那么其他哨兵，会等待failover-timeout时间，然后接替继续执行切换，此时会重新获取一个新的configuration epoch，作为新的version号
#### configuraiton传播
哨兵完成切换之后，会在自己本地更新生成最新的master配置，然后同步给其他的哨兵，就是通过之前说的pub/sub消息机制，这里之前的version号就很重要了，因为各种消息都是通过一个channel去发布和监听的，所以一个哨兵完成一次新的切换之后，新的master配置是跟着新的version号的，其他的哨兵都是根据版本号的大小来更新自己的master配置的
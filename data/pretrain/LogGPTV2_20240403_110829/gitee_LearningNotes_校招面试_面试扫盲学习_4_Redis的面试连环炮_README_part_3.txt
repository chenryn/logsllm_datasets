首先，你的底层的缓存中间件，缓存系统，必须能够支撑的起我们说的那种高并发，其次，再经过良好的整体的缓存架构的设计（多级缓存架构、热点缓存），支撑真正的上十万，甚至上百万的高并发
### redis不能支撑高并发的瓶颈在哪里？
因为单机的Redis，QPS只能在上万左右，成为了支撑高并发的瓶颈。
### ![redis单机的瓶颈](images/redis单机的瓶颈.png)如果redis要支撑超过10万+的并发，那应该怎么做？
单机的redis几乎不太可能说QPS超过10万+，除非一些特殊情况，比如你的机器性能特别好，配置特别高，物理机，维护做的特别好，而且你的整体的操作不是太复杂，单机在几万。
读写分离，一般来说，对缓存，一般都是用来支撑读高并发的，写的请求是比较少的，可能写请求也就一秒钟几千，一两千。大量的请求都是读，一秒钟二十万次读
读写分离：主从架构 -> 读写分离 -> 支撑10万+读QPS的架构
![redis主从实现读写分离支撑10万+的高并发](images/redis主从实现读写分离支撑10万+的高并发.png)
架构做成主从架构，一主多从，主服务器负责写，并且将数据同步到其它的slave节点，从节点负责读，所有的读请求全部走节点。
同时这样的架构，支持碎片扩容，就是说如果QPS在增加，也很简单，只需要增加  Redis Slave节点即可。
### Redis主从架构
redis主从架构 -> 读写分离架构 -> 可支持水平扩展的读高并发架构
#### 基本原理
- redis采用异步方式复制数据到slave节点，不过redis 2.8开始，slave node会周期性地确认自己每次复制的数据量
- 一个master node是可以配置多个slave node的
- slave node也可以连接其他的slave node
- slave node做复制的时候，是不会block master node的正常工作的
- slave node在做复制的时候，也不会block对自己的查询操作，它会用旧的数据集来提供服务; 但是复制完成的时候，需要删除旧数据集，加载新数据集，这个时候就会暂停对外服务了
- slave node主要用来进行横向扩容，做读写分离，扩容的slave node可以提高读的吞吐量
![image-20200422073720488](images/image-20200422073720488.png)
写操作存放在master node，同时在异步把master上的信息，同步到每个slave node上。
#### master持久化对于主从架构的安全保障的意义
如果采用了主从架构，那么建议必须开启master node的持久化！不建议用slave node作为master node的数据热备，因为那样的话，如果你关掉master的持久化，可能在master宕机重启的时候数据是空的，然后可能一经过复制，salve node数据也丢了
master -> RDB和AOF都关闭了 -> 全部在内存中
master宕机，重启，是没有本地数据可以恢复的，然后就会直接认为自己IDE数据是空的
master就会将空的数据集同步到slave上去，所有slave的数据全部清空
100%的数据丢失
master节点，必须要使用持久化机制
第二个，master的各种备份方案，要不要做，万一说本地的所有文件丢失了; 从备份中挑选一份rdb去恢复master; 这样才能确保master启动的时候，是有数据的
即使采用了后续讲解的高可用机制，slave node可以自动接管master node，但是也可能sentinal还没有检测到master failure，master node就自动重启了，还是可能导致上面的所有slave node数据清空故障
#### Redis主从复制原理
当启动一个slave node的时候，它会发送一个PSYNC命令给master node，如果这是slave node重新连接master node，那么master node仅仅会复制给slave部分缺少的数据; 否则如果是slave node第一次连接master node，那么会触发一次full resynchronization
开始full resynchronization的时候，master会启动一个后台线程，开始生成一份RDB快照文件，同时还会将从客户端收到的所有写命令缓存在内存中。RDB文件生成完毕之后，master会将这个RDB发送给slave，slave会先写入本地磁盘，然后再从本地磁盘加载到内存中。然后master会将内存中缓存的写命令发送给slave，slave也会同步这些数据。
slave node如果跟master node有网络故障，断开了连接，会自动重连。master如果发现有多个slave node都来重新连接，仅仅会启动一个rdb save操作，用一份数据服务所有slave node。![redis主从复制的原理](images/redis主从复制的原理.png)
### 主从复制的断点续传
从redis 2.8开始，就支持主从复制的断点续传，如果主从复制过程中，网络连接断掉了，那么可以接着上次复制的地方，继续复制下去，而不是从头开始复制一份
master node会在内存中常见一个backlog，master和slave都会保存一个replica offset还有一个master id，offset就是保存在backlog中的。如果master和slave网络连接断掉了，slave会让master从上次的replica offset开始继续复制，但是如果没有找到对应的offset，那么就会执行一次resynchronization
### 无磁盘化复制
master在内存中直接创建rdb，然后发送给slave，不会在自己本地落地磁盘了
```
repl-diskless-sync
# 等待一定时长再开始复制，因为要等更多slave重新连接过来
repl-diskless-sync-delay
```
### Redis主从复制的完整复制流程
#### 主从复制流程图
- slave node启动，仅仅保存master node的信息，包括master node的host和ip，但是复制流程没开始master host和ip是从哪儿来的，redis.conf里面的slaveof配置的
- slave node内部有个定时任务，每秒检查是否有新的master node要连接和复制，如果发现，就跟master node建立socket网络连接
- slave node发送ping命令给master node
- 口令认证，如果master设置了requirepass，那么salve node必须发送masterauth的口令过去进行认证
- master node第一次执行全量复制，将所有数据发给slave node
- master node后续持续将写命令，异步复制给slave node
![复制的完整的基本流程](images/复制的完整的基本流程.png)
#### 数据同步相关核心机制
指的就是第一次slave连接msater的时候，执行的全量复制，那个过程里面你的一些细节的机制
- master和slave都会维护一个offset
master会在自身不断累加offset，slave也会在自身不断累加offset
slave每秒都会上报自己的offset给master，同时master也会保存每个slave的offset
这个倒不是说特定就用在全量复制的，主要是master和slave都要知道各自的数据的offset，才能知道互相之间的数据不一致的情况
- backlog
master node有一个backlog，默认是1MB大小
master node给slave node复制数据时，也会将数据在backlog中同步写一份
backlog主要是用来做全量复制中断候的增量复制的
- master run id
info server，可以看到master run id
如果根据host+ip定位master node，是不靠谱的，如果master node重启或者数据出现了变化，那么slave node应该根据不同的run id区分，run id不同就做全量复制
如果需要不更改run id重启redis，可以使用redis-cli debug reload命令
- psync
从节点使用psync从master node进行复制，psync runid offset master node会根据自身的情况返回响应信息，可能是FULLRESYNC runid offset触发全量复制，可能是CONTINUE触发增量复制![maste run id的作用](images/maste run id的作用.png)
#### 全量复制
- master执行bgsave，在本地生成一份rdb快照文件
- master node将rdb快照文件发送给salve node，如果rdb复制时间超过60秒（repl-timeout），那么slave node就会认为复制失败，可以适当调节大这个参数
- 对于千兆网卡的机器，一般每秒传输100MB，6G文件，很可能超过60s
- master node在生成rdb时，会将所有新的写命令缓存在内存中，在salve node保存了rdb之后，再将新的写命令复制给salve node
- client-output-buffer-limit slave 256MB 64MB 60，如果在复制期间，内存缓冲区持续消耗超过64MB，或者一次性超过256MB，那么停止复制，复制失败
- slave node接收到rdb之后，清空自己的旧数据，然后重新加载rdb到自己的内存中，同时基于旧的数据版本对外提供服务
rdb生成、rdb通过网络拷贝、slave旧数据的清理、slave aof rewrite，很耗费时间
如果slave node开启了AOF，那么会立即执行BGREWRITEAOF，重写AOF
#### 增量复制
- 如果全量复制过程中，master-slave网络连接断掉，那么salve重新连接master时，会触发增量复制
- master直接从自己的backlog中获取部分丢失的数据，发送给slave node，默认backlog就是1MB
- msater就是根据slave发送的psync中的offset来从backlog中获取数据的
#### 异步复制
master每次接收到写命令之后，现在内部写入数据，然后异步发送给slave node
#### 心跳机制
master默认每隔10秒发送一次心跳，salve node每隔1秒发送一个心跳
### Redis主从架构如何才能做到99.99%的高可用性？
架构上，高可用性，99.99%的高可用性
99.99%，公式，系统可用的时间 / 系统故障的时间，365天，在365天 * 99.99%的时间内，你的系统都是可以哗哗对外提供服务的，那就是高可用性，99.99%
系统可用的时间 / 总的时间 = 高可用性，然后会对各种时间的概念，说一大堆解释
#### 系统可用性
![什么是99.99%高可用性](images/什么是99.99%高可用性.png)
#### 系统处于不可用
![系统处于不可用是什么意思](images/系统处于不可用是什么意思.png)
#### Redis的不可用
一个slave宕机后，不会影响系统的可用性，还有其它slave在提供相同数据的情况下对外提供查询服务。
![redis的不可用](images/redis的不可用.png)
master宕机后，相当于系统不可用了。
#### Redis高可用的方案
当Redis的master节点宕机后，redis的高可用架构中，有一个故障转移，叫failover，也可以做主备切换。
![redis基于哨兵的高可用性](images/redis基于哨兵的高可用性.png)
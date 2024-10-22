- RPOP 产生一个rpop事件。如果键由于最后一个元素被从列表中弹出而导致删除，会又产生一个del事件。
- LPOP 产生一个lpop事件。如果键由于最后一个元素被从列表中弹出而导致删除，会又产生一个del事件。
- LINSERT 产生一个linsert事件。
- LSET 产生一个lset事件。
- LREM 产生一个lrem事件。如果结果列表为空并且键被删除，会又产生一个del事件。
- LTRIM 产生一个ltrim事件。如果结果列表为空并且键被删除，会又产生一个del事件。
- RPOPLPUSH和BRPOPLPUSH 产生一个rpop事件和一个lpush事件。两种情况下顺序都能保证 (lpush事件总是在rpop事件之后被传递) 如果结果列表长度为零并且键被删除，会又产生一个del事件。
- HSET, HSETNX和HMSET 都产生单个hset事件。
- HINCRBY 产生一个hincrby事件。
- HINCRBYFLOAT 产生一个hincrbyfloat事件。
- HDEL 产生单个hdel事件。如果结果哈希为空并且键被删除，会又产生一个del事件。
- SADD 产生单个sadd事件，即使在可变情况下(even in the variadic case)。
- SREM 产生单个srem事件。如果结果集合为空并且键被删除，会又产生一个del事件。
- SMOVE 为源键产生一个srem事件为目标键产生一个sadd事件。
- SPOP 产生一个spop事件。如果结果集合为空并且键被删除，会又产生一个del事件。
- SINTERSTORE, SUNIONSTORE, SDIFFSTORE 分别产生sinterstore，sunionostore，sdiffstore事件。在特殊情况下，集合为空，且存储结果的键已经存在，由于键被删除，会产生一个del事件。
- ZINCR 产生一个zincr事件。
- ZADD产生单个zadd事件，即使添加了多个元素。.
- ZREM 产生单个zrem事件，即使删除了多个元素。当结果有序集合为空，并且键被生成时，会产生一个额外的del事件。
- ZREMBYSCORE 产生单个zrembyscore事件。当结果有序集合为空，并且键被生成时，会产生一个额外的del事件。
- ZREMBYRANK 产生单个zrembyrank事件。当结果有序集合为空，并且键被生成时，会产生一个额外的del事件。
- ZINTERSTORE和ZUNIONSTORE 分别产生zinterstore和zunionstore事件。在特殊情况下，集合为空，且存储结果的键已经存在，由于键被删除，会产生一个del事件。
- 每当一个关联有生存事件的键由于过期而被从数据集中删除时会产生一个expired事件。
- 每当一个键由于maxmemory策略而从数据集中被淘汰以节省内存时会产生一个evicted事件。
## 开启远程登录连接
使用 netstat 来查看端口占用情况，6379为默认Redis端口。
```bash
netstat -nlt|grep 6379
```
- -t：指明显示 TCP 端口
- -u：指明显示 UDP 端口
- -l：仅显示监听套接字
- -p：显示进程标识符和程序名称，每一个套接字/端口都属于一个程序。
- -n：不进行 DNS 轮询，显示 IP （可以加速操作）
### 修改防火墙配置
修改防火墙配置 sudo vi /etc/sysconfig/iptables
```bash
-A INPUT -m state --state NEW -m tcp -p tcp --dport 6379 -j ACCEPT
```
###  修改配置文件
Redis protected-mode 是3.2 之后加入的新特性，在Redis.conf的注释中，我们可以了解到，他的具体作用和启用条件。可以在 sudo vi /etc/redis.conf 中编辑，修改配置文件。
```bash
# Protected mode is a layer of security protection, in order to avoid that
# Redis instances left open on the internet are accessed and exploited.
#
# When protected mode is on and if:
#
# 1) The server is not binding explicitly to a set of addresses using the
#    "bind" directive.
# 2) No password is configured.
#
# The server only accepts connections from clients connecting from the
# IPv4 and IPv6 loopback addresses 127.0.0.1 and ::1, and from Unix domain
# sockets.
#
# By default protected mode is enabled. You should disable it only if
# you are sure you want clients from other hosts to connect to Redis
# even if no authentication is configured, nor a specific set of interfaces
# are explicitly listed using the "bind" directive.
protected-mode yes
```
它启用的条件，有两个：
1. 没有bind IP
2. 没有设置访问密码
如果启用了，则只能够通过lookback ip（127.0.0.1）访问Redis cache，如果从外网访问，则会返回相应的错误信息：
```bash
(error) DENIED Redis is running in protected mode because protected mode is enabled, no bind address was specified, no authentication password is requested to clients. In this mode connections are only accepted from the lookback interface. If you want to connect from external computers to Redis you may adopt one of the following solutions: 1) Just disable protected mode sending the command 'CONFIG SET protected-mode no' from the loopback interface by connecting to Redis from the same host the server is running, however MAKE SURE Redis is not publicly accessible from internet if you do so. Use CONFIG REWRITE to make this change permanent. 2) Alternatively you can just disable the protected mode by editing the Redis configuration file, and setting the protected mode option to 'no', and then restarting the server. 3) If you started the server manually just for testing, restart it with the --portected-mode no option. 4) Setup a bind address or an authentication password. NOTE: You only need to do one of the above things in order for the server to start accepting connections from the outside.
```
## 提供的原生监控
### 当前链接的客户端数和连接数
`redis-cli --stat`查看当前连接的客户端数，连接数等
```bash
------- data ------ --------------------- load -------------------- - child -
keys       mem      clients blocked requests            connections
4          1.27M    6       0       17340 (+0)          111
4          1.27M    6       0       17341 (+1)          111
4          1.27M    6       0       17342 (+1)          111
4          1.27M    6       0       17343 (+1)          111
```
### 内存最大的键值和平均的键值数据
`redis-cli --bigkeys` 对当前占用内存最大的键值和平均的键值数据，也可以通过指定`-i`参数定时查看当前的视图情况。
```bash
# Scanning the entire keyspace to find biggest keys as well as
# average sizes per key type.  You can use -i 0.1 to sleep 0.1 sec
# per 100 SCAN commands (not usually needed).
[00.00%] Biggest string found so far 'asdf.js' with 3 bytes
[00.00%] Biggest string found so far 'wabg-tokeneyJhbGciOiJIUzI1NiJ9.NA.UGGRiB2I42rP-33cIMrcoPub7AzHgDlqHacAKFw1pfE' with 328 bytes
[00.00%] Biggest string found so far 'wabg-token-province' with 231042 bytes
-------- summary -------
Sampled 4 keys in the keyspace!
Total key length in bytes is 180 (avg len 45.00)
Biggest string found 'wabg-token-province' has 231042 bytes
4 strings with 231819 bytes (100.00% of keys, avg size 57954.75)
0 lists with 0 items (00.00% of keys, avg size 0.00)
0 sets with 0 members (00.00% of keys, avg size 0.00)
0 hashs with 0 fields (00.00% of keys, avg size 0.00)
0 zsets with 0 members (00.00% of keys, avg size 0.00)
```
### 查看当前的键值情况
`redis-cli --scan`提供和`keys *`相似的功能，查看当前的键值情况，可以通过正则表达
```bash 
$ redis-cli --scan
sess:K4xh-bxOBrcXpy9kEW87oiy-u7I2sAA5
asdf.js
sess:1tGNZSXW8GyoEQsbtpqkA5tMmSFp_ZIn
wabg-tokeneyJhbGciOiJIUzI1NiJ9.NA.UGGRiB2I42rP-33cIMrcoPub7AzHgDlqHacAKFw1pfE
sess:3e4NGIJd0wf1-RONeTt-FsXQj4EaVNjk
wabg-token-province
sess:UuCLAX2sWZ50fiIO1qvDgulf0XIZRd98
wabg-tokeneyJhbGciOiJIUzI1NiJ9.MQ.6z44GClzAsUED1M_UyxqdREdDKcYFnL9tSqd5ZhLhsY
sess:2HEchaRLYUoaa44IF1bB6mpik7lZjBb4
```
### 原生的Monitor监控
redis-cli monitor打印出所有sever接收到的命令以及其对应的客户端地址
```bash
$ redis-cli monitor
OK
1472626566.218175 [0 127.0.0.1:62862] "info"
1472626571.220948 [0 127.0.0.1:62862] "exists" "aaa"
1472626571.223174 [0 127.0.0.1:62862] "set" "aaa" ""
1472626571.232126 [0 127.0.0.1:62862] "type" "aaa"
1472626571.243697 [0 127.0.0.1:62862] "pttl" "aaa"
1472626571.243717 [0 127.0.0.1:62862] "object" "ENCODING" "aaa"
1472626571.243726 [0 127.0.0.1:62862] "strlen" "aaa"
```
## 配置说明
```bash
#redis.conf
# Redis configuration file example.
# ./redis-server /path/to/redis.conf
################################## INCLUDES ###################################
#这在你有标准配置模板但是每个redis服务器又需要个性设置的时候很有用。
# include /path/to/local.conf
# include /path/to/other.conf
################################ GENERAL #####################################
# 是否在后台执行，yes：后台运行；no：不是后台运行（老版本默认）
daemonize yes
# 3.2里的参数，是否开启保护模式，默认开启。要是配置里没有指定bind和密码。
# 开启该参数后，redis只会本地进行访问，拒绝外部访问。
# 要是开启了密码   和bind，可以开启。否   则最好关闭，设置为no。
protected-mode yes
# redis的进程文件
pidfile /var/run/redis/redis-server.pid
# redis监听的端口号。
port 6379
# 此参数确定了TCP连接中已完成队列(完成三次握手之后)的长度， 
# 当然此值必须不大于Linux系统定义的/proc/sys/net/core/somaxconn值，默认是511，
# 而Linux的默认参数值是128。当系统并发量大并且客户端速度缓慢的时候，
# 可以将这二个参数一起参考设定。该内核参数默认值一般是128，对于负载很大的服务程序来说大大的不够。
# 一般会将它修改为2048或者更大。在/etc/sysctl.conf中添加:net.core.somaxconn = 2048，然后在终端中执行sysctl -p。
tcp-backlog 511
#指定 redis 只接收来自于该 IP 地址的请求，如果不进行设置，那么将处理所有请求
bind 127.0.0.1
# 配置unix socket来让redis支持监听本地连接。
# unixsocket /var/run/redis/redis.sock
# 配置unix socket使用文件的权限
# unixsocketperm 700
# 此参数为设置客户端空闲超过timeout，服务端会断开连接，为0则服务端不会主动断开连接，不能小于0。
timeout 0
# tcp keepalive参数。如果设置不为0，就使用配置tcp的SO_KEEPALIVE值，
# 使用keepalive有两个好处:检测挂掉的对端。降低中间设备出问题而导致网络看似连接却已经与对端端口的问题。
# 在Linux内核中，设置了keepalive，redis会定时给对端发送ack。检测到对端关闭需要两倍的设置值。
tcp-keepalive 0
# 指定了服务端日志的级别。级别包括：debug（很多信息，方便开发、测试），
# verbose（许多有用的信息，但是没有debug级别信息多），notice（适当的日志级别，适合生产环境），warn（只有非常重要的信息）
loglevel notice
#指定了记录日志的文件。空字符串的话，日志会打印到标准输出设备。后台运行的redis标准输出是/dev/null。
logfile /var/log/redis/redis-server.log
# 是否打开记录syslog功能
# syslog-enabled no
# syslog的标识符。
# syslog-ident redis
# 日志的来源、设备
# syslog-facility local0
# 数据库的数量，默认使用的数据库是DB 0。可以通过”SELECT “命令选择一个db
databases 16
################################ SNAPSHOTTING ################################
# 快照配置
# 注释掉“save”这一行配置项就可以让保存数据库功能失效
# 设置sedis进行数据库镜像的频率。
# 900秒（15分钟）内至少1个key值改变（则进行数据库保存--持久化） 
# 300秒（5分钟）内至少10个key值改变（则进行数据库保存--持久化） 
# 60秒（1分钟）内至少10000个key值改变（则进行数据库保存--持久化）
save 900 1
save 300 10
save 60 10000
# 当RDB持久化出现错误后，是否依然进行继续进行工作，yes：不能进行工作，no：可以继续进行工作，
# 可以通过info中的rdb_last_bgsave_status了解RDB持久化是否有错误
stop-writes-on-bgsave-error yes
# 使用压缩rdb文件，rdb文件压缩使用LZF压缩算法，yes：压缩，但是需要一些cpu的消耗。no：不压缩，需要更多的磁盘空间
rdbcompression yes
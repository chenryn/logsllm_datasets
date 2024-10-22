10 分钟快速入门 Redis
===
目录
===
- [Redis安装](#redis安装)
  - [官方编译安装](#官方编译安装)
  - [通过EPEL源安装](#通过epel源安装)
  - [Redis升级](#redis升级)
- [服务管理](#服务管理)
  - [基本服务操作](#基本服务操作)
  - [查看版本](#查看版本)
  - [开机启动](#开机启动)
- [更改配置](#更改配置)
- [设置请求密码](#设置请求密码)
- [主从架构配置](#主从架构配置)
- [基本操作](#基本操作)
- [支持的数据类型](#支持的数据类型)
  - [字符串](#字符串)
  - [Hashes - 哈希值](#hashes---哈希值)
  - [Lists - 列表](#lists---列表)
  - [有序集合](#有序集合)
- [开启通知](#开启通知)
- [开启远程登录连接](#开启远程登录连接)
  - [修改防火墙配置](#修改防火墙配置)
  - [修改配置文件](#修改配置文件)
- [提供的原生监控](#提供的原生监控)
  - [当前链接的客户端数和连接数](#当前链接的客户端数和连接数)
  - [内存最大的键值和平均的键值数据](#内存最大的键值和平均的键值数据)
  - [查看当前的键值情况](#查看当前的键值情况)
  - [原生的Monitor监控](#原生的monitor监控)
- [配置说明](#配置说明)
- [精品文章](#精品文章)
## Redis安装
### 官方编译安装
```bash
$ wget http://download.redis.io/releases/redis-4.0.0.tar.gz
$ tar xzvf redis-4.0.0.tar.gz -C /usr/local/
$ cd /usr/local/redis-4.0.0
$ make
$ make test
$ make install 
# 程序会自动执行:
# mkdir -p /usr/local/bin
# cp -pf redis-server /usr/local/bin
# cp -pf redis-benchmark /usr/local/bin
# cp -pf redis-cli /usr/local/bin
# cp -pf redis-check-dump /usr/local/bin
# cp -pf redis-check-aof /usr/local/bin
```
测试`make test`报错
```
$ make test
You need tcl 8.5 or newer in order to run the Redis test
make: *** [test] Error 1
```
这个是需要安装`tcl`
```
wget http://downloads.sourceforge.net/tcl/tcl8.6.1-src.tar.gz  
sudo tar xzvf tcl8.6.1-src.tar.gz  -C /usr/local/  
cd  /usr/local/tcl8.6.1/unix/  
sudo ./configure  
sudo make  
sudo make install   
```
### 通过EPEL源安装
源安装问题在于不能安装最新，或者指定Redis版本。
```bash
yum --enablerepo=epel -y install redis
```
如果没有安装源，通过下面方式安装源。
```bash
cd /etc/yum.repos.d/
rpm -Uvh http://download.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
```
### Redis升级
首先，确保安装了以下repos，EPEL和REMI：
```bash
sudo rpm -Uvh http://download.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
sudo rpm -Uvh http://rpms.remirepo.net/enterprise/remi-release-6.rpm
```
通过`--enablerepo=epel`参数查看指定源Redis版本，检查REMI repo中的Redis版本：
```bash
yum --enablerepo=epel info redis
# Loaded plugins: fastestmirror
# Loading mirror speeds from cached hostfile
#  * base: centos.ustc.edu.cn
#  * epel: mirrors.tuna.tsinghua.edu.cn
#  * extras: centos.ustc.edu.cn
#  * updates: mirrors.zju.edu.cn
# Available Packages
# Name        : redis
# Arch        : x86_64
# Version     : 2.4.10
# Release     : 1.el6
# Size        : 213 k
# Repo        : epel/x86_64
# Summary     : A persistent key-value database
# URL         : http://redis.io
# License     : BSD
# Description : Redis is an advanced key-value store. It is similar to memcached but the data
#             : set is not volatile, and values can be strings, exactly like in memcached, but
#             : also lists, sets, and ordered sets. All this data types can be manipulated with
#             : atomic operations to push/pop elements, add/remove elements, perform server
#             : side union, intersection, difference between sets, and so forth. Redis supports
#             : different kind of sorting abilities.
```
然后从EPEL repo安装相关的依赖关系（jemalloc）：
```bash
yum --enablerepo=epel install jemalloc
```
在安装之前，您应该停止旧的Redis守护进程：
```bash
service redis stop
```
然后安装更新版本的Redis：
```bash
sudo yum --enablerepo=remi install redis
```
## 服务管理
重新启动Redis守护程序，并使其重新启动时自动启动：
```bash
sudo service redis start
sudo chkconfig redis on
```
### 基本服务操作
```bash
## 启动并后台运行
$ redis-server & nohup
## 查是否启动
$ redis-cli ping
## 关闭命令
$ redis-cli shutdown
# 命令行客户端启动
$ redis-cli start
# 启动
$ service redis start
# 停止
$ service redis stop
# 命令行客户端启动
$ redis-cli -p 6380
# 指定端口后台启动
$ redis-server --port 6380 &
```
### 查看版本
检查当前安装的Redis版本：
```bash
# 查看 Redis 版本
$ redis-cli info | grep redis_version
# 查看端口号
$ redis-cli info | grep tcp_port
```
### 服务管理
```bash
systemctl status redis # 查看服务状态
systemctl start redis # 启动 Redis
systemctl stop redis # 启动 Redis
```
### 开机启动
如果你是通过yum安装，可以使用下面方式开机启动。
```bash
systemctl enable redis.service
chkconfig redis on
```
如果你是编译安装可通过下面方式设置开机启动
我们将在 Redis 安装目录找到`/usr/local/redis-4.0.0/utils`这个目录，在这个目录中有个有个脚本 `redis_init_script`，将此脚本拷贝到`/etc/init.d`目录下，命名为`redis`: 
```bash
cp /usr/local/redis-4.0.0/utils/redis_init_script /etc/init.d/redis
```
拷贝一下`redis.conf` 文件到`/etc/redis`目录下
```bash
cp /usr/local/redis-4.0.0/redis.conf /etc/redis/6380.conf
```
配置文件`6380.conf`需要更改几个地方
```bash
# 是否在后台执行，yes：后台运行；no：不是后台运行（老版本默认）
daemonize yes
```
更改权限，通过 [chkconfig](https://jaywcjlove.github.io/linux-command/c/chkconfig.html) 命令检查、设置系统redis服务开启
```bash
chmod +x /etc/init.d/redis
chkconfig redis on
```
必须把下面两行注释放在 `/etc/init.d/redis` 文件头部，不设置会报不支持的提示 `service redis does not support chkconfig`
```bash
# chkconfig:   2345 90 10
# description:  redis is a persistent key-value database
```
上面的注释的意思是，redis服务必须在运行级2，3，4，5下被启动或关闭，启动的优先级是90，关闭的优先级是10。
**Redis 启动警告错误解决**
1. WARNING overcommit_memory is set to 0! Background save may fail under low memory condition. To fix this issue add 'vm.overcommit_memory = 1' to /etc/sysctl.conf and then reboot or run the command 'sysctl vm.overcommit_memory=1' for this to take effect.
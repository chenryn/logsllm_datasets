# Windows+VMware一键搭建蘑菇博客本地开发环境
## 前言
大家好，我是**陌溪**
这阵子很多新手小伙伴打算入坑蘑菇博客的开发，但是被博客所依赖的软件的安装和配置所劝退，导致最终无法顺利的完成蘑菇博客本地环境的搭建。鉴于此，我打算使用**VMware**快速搭建蘑菇博客所依赖的中间件，帮助小伙伴减轻痛苦。
注意：本博客使用的是 **Nacos/master** 分支代码 ，**Eureka** 分支环境搭建请参考 [本篇教程](http://moguit.cn/#/info?blogOid=14)
如何想把所有软件安装到 **Windows** 中，参考博客：[Windows环境下配置蘑菇博客环境](http://moguit.cn/#/info?blogOid=14)
**IDEA** 开发环境需要提前安装 **lombok** 插件：[IDEA中引入Lombok](http://moguit.cn/#/info?blogUid=4ccb7df5d537f52d954eb15f094c90a3) 
参考：[蘑菇博客切换搜索模式](http://moguit.cn/#/info?blogUid=4042b4f4088e4e37e95d9fc75d97298b)，完成蘑菇博客的搜索引擎切换，目前支持 **Solr**、**ElasticSearch**、**MySQL** 的方式，选择一种搜索方式即可。
## VMware中安装CentOS
首先需要在 **VMware** 中安装 **CentOS** 环境，推荐硬盘大小设置为 **40GB**，内存大小为 **4GB**。
同时为了以后搭建更加方便，最好能够给 **CentOS** 服务器设置固定 **IP**
参考博客：[VMWare中CentOS如何配置固定IP](http://moguit.cn/#/info?blogOid=126)
此教程不仅仅适用于 VMWare中的CentOS，如果本地配置不行的话，也可以购买云服务器完成下面的部署
最低配置：1核2G 【[需开启虚拟内存](http://moguit.cn/#/info?blogOid=96)】
推荐配置：2核4G 【双十二特惠】
> 【阿里云】云服务器双12狂欢特惠，1核2G 5M轻量级应用服务器114元/年【博主使用】 [点我传送](https://www.aliyun.com/minisite/goods?userCode=w7aungxw) 
>
> 【腾讯云】云产品限时秒杀，爆款1核2G云服务器，首年99元（老用户重新用微信QQ注册即可） [点我进入](https://curl.qcloud.com/zry6xub9)
### 安装Docker
因为我们需要拉取镜像，所以需要在服务器提前安装好Docker，首先配置一下Docker的阿里yum源
```bash
cat >/etc/yum.repos.d/docker.repo> /etc/docker/daemon.json  CentOS IP：192.168.177.150 【配置的固定CentOS IP】
>
> MySQL用户名：root
>
> MySQL密码：mogu2018
![image-20210103171327116](images/image-20210103171327116.png)
连接后，即可看到我们安装好的蘑菇博客业务数据库
![image-20210103171603686](images/image-20210103171603686.png)
### Nacos
Nacos服务注册和配置中心，如果想更加详细的了解Nacos的使用
参考 [【SpringCloud】使用Nacos实现服务注册发现和配置中心等功能](http://moguit.cn/#/info?blogUid=e6e619349d31dded928c9265c5a9c672)
访问下面 **URL** 进行测试
```bash
# Nacos后台配置页面，默认账号和密码：nacos  nacos
http://192.168.177.150:8848/nacos
```
打开后，我们在配置列表即可看到我们的配置文件
![image-20210104084259827](images/image-20210104084259827.png)
### Redis
Redis使用 **RedisDesktopManager** 进行连接
> Host：192.168.177.150 
>
> Redis密码：mogu2018
开始连接
![image-20210103171808589](images/image-20210103171808589.png)
因为目前 **Redis** 还没有缓存数据，所以为空，以后有数据的话，将会使用 **db0** 数据库
![image-20210103171911067](images/image-20210103171911067.png)
### RabbitMQ
RabbitMQ是消息队列，我们可以访问其图形化界面
```bash
# 图形化地址
192.168.177.150:15672
# 默认账号和密码为：admin  mogu2018
```
然后即可进入到RabbitMQ的可视化页面
![image-20210103194818204](images/image-20210103194818204.png)
## 部署非核心组件
除了核心组件之外，还有一些组件可以**根据自己的情况选择是否启动**，如果**本地内存不允许**的话，也可以直接**跳过**本节的非核心组件的部署~
### Zipkin
Zipkin是一个开源的分布式的链路追踪系统，每个微服务都会向zipkin报告计时数据，聚合各业务系统调用延迟数据，达到链路调用监控跟踪，深入了解可参考博客：[使用Zipkin搭建蘑菇博客链路追踪](http://www.moguit.cn/#/info?blogUid=35bd93cabc08611c7f74ce4564753ef9)
链路追踪服务可以选择安装，不过如果没有安装的话，在启动的时候会出现这样一个错误，不过该错误不会影响正常使用，可以忽略
```bash
I/O error on POSt request for "http://localhost:9411/api/v2/span" ：connect timeout
```
到 **docker-compose/bin** 目录下，执行下面脚本安装 **zipkin**
```bash
docker-compose -f zipkin.yml up -d
```
脚本将会给我们拉取zipkin镜像，并进行启动
![image-20210103195652668](images/image-20210103195652668.png)
启动完成后，我们访问下面 **URL** 进行测试
```bash
http://192.168.177.150:9411/zipkin/
```
启动后的页面如下所示
![image-20210103195830492](images/image-20210103195830492.png)
### Sentinel
随着微服务的流行，服务和服务之间的稳定性变得越来越重要。**Sentinel** 以流量为切入点，从流量控制、熔断降级、系统负载保护等多个维度保护服务的稳定性。
参考[【SpringCloud】使用Sentinel实现熔断和限流](http://moguit.cn/#/info?blogUid=408e9c889ebf96a66af2adfdc258ba5f) ，了解Sentinel以及使用
到 **docker-compose/bin** 目录下，执行下面脚本安装 **Sentinel**
```bash
docker-compose -f sentinel.yml up -d
```
脚本将会给我们拉取 sentinel 镜像，并进行启动
![image-20210103201427604](images/image-20210103201427604.png)
启动完成后，我们访问下面 **URL** 进行测试
```bash
# 访问Sentinel登录页面，输入账号密码： sentinel  sentinel
http://192.168.177.150:8070
```
即可进入到sentinel后台管理，因为我们的微服务还没有启动，所以暂时还看不到任何东西
![image-20210103201751979](images/image-20210103201751979.png)
### 搜索模块
目前蘑菇博客支持三种搜索模式的配置，分别是 **Solr**、**ElasticSearch** 和 **SQL**，小伙伴可以按照自己的服务器配置进行相应的部署，默认是 **SQL** 搜索，即无需启动 **mogu-search** 也能正常运行。
参考：[蘑菇博客切换搜索模式](http://moguit.cn/#/info?blogUid=4042b4f4088e4e37e95d9fc75d97298b) ，进行三种模式的切换（三种方式选择一种，默认是 **SQL** 搜索，可以配置**ElasticSearch** 或者 **Solr** 作为全文检索 ）
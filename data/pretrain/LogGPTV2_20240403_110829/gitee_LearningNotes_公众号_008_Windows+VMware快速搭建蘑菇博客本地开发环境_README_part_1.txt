# Windows+VMware一键搭建蘑菇博客本地开发环境
## 前言
大家好，我是**陌溪**
这阵子很多新手小伙伴打算入坑蘑菇博客的开发，但是被博客所依赖的软件的安装和配置所劝退，导致最终无法顺利的完成蘑菇博客本地环境的搭建。鉴于此，我打算使用**VMware**快速搭建蘑菇博客所依赖的中间件，帮助小伙伴减轻痛苦。
注意：本博客使用的是 **Nacos/master** 分支代码 
**Eureka** 分支的或者是想把所有软件安装到 **Windows** 中的小伙伴，参考下面这篇博客
> Windows环境下配置蘑菇博客环境：
>
> http://moguit.cn/#/info?blogOid=14
**IDEA** 开发环境需要提前安装 **lombok** 插件，参考下面这篇博客
> IDEA中引入Lombok : 
>
> http://moguit.cn/#/info?blogOid=138
目前蘑菇博客的搜索引擎切换，目前支持 **Solr**、**ElasticSearch**、**MySQL** 的方式，选择一种搜索方式即可。
> 蘑菇博客切换搜索模式：
>
> http://moguit.cn/#/info?blogOid=119
## VMware中安装CentOS
首先需要在 **VMware** 中安装 **CentOS** 环境，推荐硬盘大小设置为 **40GB**，内存大小为 **4GB**。
同时为了以后搭建更加方便，最好能够给 **CentOS** 服务器设置固定 **IP**
> VMWare中CentOS如何配置固定IP：
>
> http://moguit.cn/#/info?blogOid=126
此教程不仅仅适用于 VMWare中的CentOS，如果本地配置不行的话，也可以购买云服务器完成下面的部署
### 安装Docker
因为我们需要拉取镜像，所以需要在服务器提前安装好Docker，首先配置一下Docker的阿里yum源
```bash
cat >/etc/yum.repos.d/docker.repo> /etc/docker/daemon.json  下载地址：https://wws.lanzous.com/iTHoIiuilvi
把下载到的文件使用Xftp工具，拷贝到 `/usr/local/bin/` 目录下
```bash
# 重命名
mv docker-compose-Linux-x86_64  docker-compose
# 加入执行权限
sudo chmod +x /usr/local/bin/docker-compose
# 查看docker-compose版本
docker-compose -v
```
### 关闭防火墙
然后关闭CentOS的防火墙
```bash
systemctl stop firewalld.service    
```
## 下载源码
下载蘑菇博客的源码
```bash
https://gitee.com/moxi159753/mogu_blog_v2
```
然后找到，docker-compose 目录
![docker-compose脚本所在目录](images/3eebbd04b6594f1098530b44142cb76c)
首先我们来查看一下docker-compose的目录结构
![docker-compose脚本目录结构](images/93219faa15224ea581f3b365e3cb2d5e)
- bin：相关一键启动脚本的目录
- config：存放配置文件
- data：存放数据文件
- log：存放日志文件
- yaml：存放docker compose的yaml文件
下面我们开始，将docker-compose文件夹，拷贝服务器目录位置随意，我是拷贝到 `/root/docker-compose` 目录，然后给命令设置执行权限
```bash
# 进入目录
cd docker-compose
# 添加执行权限
chmod +x bin/middleware.sh
chmod +x bin/kernShutdown.sh
chmod +x bin/wait-for-it.sh
```
可能是因为windows与Unix文本编辑器默认格式不同，引起脚本无法执行的情况，因此需要进行转换
```bash
# 安装 dos2unix
yum -y install dos2unix*
# 转换脚本
dos2unix bin/middleware.sh
dos2unix bin/kernShutdown.sh
dos2unix bin/wait-for-it.sh
```
## 部署核心组件
下面我们将部署蘑菇博客所依赖的核心中间件，例如：**Nacos**、**MySQL**、**Redis**、**RabbitMQ**、**Nginx** 等
首先到  **docker-compose/bin** 目录下，执行脚本
```bash
# 开始部署核心组件
sh middleware.sh
# 以后打算关闭的话，执行 ./kernShutdown.sh
```
下面是安装过程，需要耐心等待
![安装核心组件](images/image-20210103171207594.png)
在部署完中间件后，我们需要进行测试中间件安装是否成功。
### MySQL
首先测试 **MySQL** 数据库，可以使用图形化工具如：**SQLyog**
> CentOS IP：192.168.177.150 【配置的固定CentOS IP】
>
> MySQL用户名：root
>
> MySQL密码：mogu2018
![SQLyog连接界面](images/image-20210103171327116.png)
连接后，即可看到我们安装好的蘑菇博客业务数据库
![蘑菇博客业务数据库](images/image-20210103171603686.png)
### Nacos
Nacos服务注册和配置中心，如果想更加详细的了解Nacos的使用
> 【SpringCloud】使用Nacos实现服务注册发现和配置中心等功能：
>
> http://moguit.cn/#/info?blogUid=e6e619349d31dded928c9265c5a9c672
访问下面 **URL** 进行测试
```bash
# Nacos后台配置页面，默认账号和密码：nacos  nacos
http://192.168.177.150:8848/nacos
```
打开后，我们在配置列表即可看到我们的配置文件
![配置文件所在地](images/image-20210104084259827.png)
### Redis
Redis使用 **RedisDesktopManager** 进行连接
> Host：192.168.177.150 
>
> Redis密码：mogu2018
开始连接
![RDM连接界面](images/image-20210103171808589.png)
因为目前 **Redis** 还没有缓存数据，所以为空，以后有数据的话，将会使用 **db0** 数据库
![Redis中的16个db](images/image-20210103171911067.png)
### RabbitMQ
RabbitMQ是消息队列，我们可以访问其图形化界面
```bash
# 图形化地址
192.168.177.150:15672
# 默认账号和密码为：admin  mogu2018
```
然后即可进入到RabbitMQ的可视化页面
![RabbitMQ可视化页面](images/image-20210103194818204.png)
## 部署非核心组件
除了核心组件之外，还有一些组件可以**根据自己的情况选择是否启动**，如果**本地内存不允许**的话，也可以直接**跳过**本节的非核心组件的部署~
### Zipkin
Zipkin是一个开源的分布式的链路追踪系统，每个微服务都会向zipkin报告计时数据，聚合各业务系统调用延迟数据，达到链路调用监控跟踪，深入了解可参考博客：
> 使用Zipkin搭建蘑菇博客链路追踪：
>
> http://moguit.cn/#/info?blogOid=95
链路追踪服务可以选择安装，不过如果没有安装的话，在启动的时候会出现这样一个错误，不过该错误不会影响正常使用，可以忽略
```bash
I/O error on POSt request for "http://localhost:9411/api/v2/span" ：connect timeout
```
到 **docker-compose/bin** 目录下，执行下面脚本安装 **zipkin**
```bash
docker-compose -f zipkin.yml up -d
```
脚本将会给我们拉取zipkin镜像，并进行启动
![拉取Zipkin镜像](images/image-20210103195652668.png)
启动完成后，我们访问下面 **URL** 进行测试
```bash
http://192.168.177.150:9411/zipkin/
```
启动后的页面如下所示
![Zipkin可视化页面](images/image-20210103195830492.png)
### Sentinel
随着微服务的流行，服务和服务之间的稳定性变得越来越重要。**Sentinel** 以流量为切入点，从流量控制、熔断降级、系统负载保护等多个维度保护服务的稳定性。
> 【SpringCloud】使用Sentinel实现熔断和限流：
>
> http://moguit.cn/#/info?blogOid=121
到 **docker-compose/bin** 目录下，执行下面脚本安装 **Sentinel**
```bash
docker-compose -f sentinel.yml up -d
```
脚本将会给我们拉取 sentinel 镜像，并进行启动
![拉取Sentinel镜像](images/image-20210103201427604.png)
启动完成后，我们访问下面 **URL** 进行测试
```bash
# 访问Sentinel登录页面，输入账号密码： sentinel  sentinel
http://192.168.177.150:8070
```
即可进入到sentinel后台管理，因为我们的微服务还没有启动，所以暂时还看不到任何东西
![Sentinel后台页面](images/image-20210103201751979.png)
### 搜索模块
目前蘑菇博客支持三种搜索模式的配置，分别是 **Solr**、**ElasticSearch** 和 **SQL**，小伙伴可以按照自己的服务器配置进行相应的部署，默认是 **SQL** 搜索，即无需启动 **mogu-search** 也能正常运行。
蘑菇博客可以进行三种模式的切换(默认是 **SQL** 搜索，可以配置**ElasticSearch** 或者 **Solr** 作为全文检索 )
> 蘑菇博客切换搜索模式：
>
> http://moguit.cn/#/info?blogOid=119
####  Solr
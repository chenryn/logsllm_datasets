# DockerCompose一键部署蘑菇博客(Nacos版)
## 前言
首先，特别感谢群里小伙伴 [@你钉钉响了](https://gitee.com/it00021hot) 和 [@touch fish](https://gitee.com/chengccn1)， 一块完成了蘑菇博客的镜像制作。
原来的部署方式是采用单个Docker镜像来进行部署的，每次拉取一个超大型的镜像【大概5G】，如果在拉取镜像的时候，遇到网络卡顿等外界影响，很容易导致拉取失败，同时因为这种部署方式不太符合微服务架构的思想。
因此后面我们将所有的服务制作成单个的镜像，然后通过docker compose 进行容器编排，来协调每个容器同时对外提供服务，同时提供了Docker容器的可视化管理工具Portainer进行管理，同时达到对服务容器化的目的，也为以后使用K8S集群管理蘑菇博客做了很好的铺垫~。
本文不再讲蘑菇博客如何制作镜像，Docker Compose的使用，以及将镜像推送到阿里云容器镜像服务和DockerHub，如果感兴趣的小伙伴可以参考另外的几篇博客。
- [Docker Compose入门学习](http://www.moguit.cn/#/info?blogOid=568)
- [使用GithubAction构建蘑菇博客镜像提交DockerHub](http://www.moguit.cn/#/info?blogOid=567)
- [Docker图形化工具Portainer介绍与安装](http://www.moguit.cn/#/info?blogOid=569)
- [使用DockerCompose制作蘑菇博客YAML镜像文件](http://www.moguit.cn/#/info?blogOid=567)
本文主要讲解使用Docker Compose 一键部署蘑菇项目，如果想尝试其他方式【通过发布 **jar** 包部署】，可以参考 [使用Docker快速搭建蘑菇博客（Nacos分支）](http://www.moguit.cn/#/info?blogUid=8100dcb585fff77e3fa25eed50e3708e)
如果你也拥有域名并且备案了的话，可以给蘑菇博客配置域名的方式访问：[DockerCompose部署的博客配置域名访问](http://moguit.cn/#/info?blogOid=582)
如果你的服务器带宽只有1M，可以使用免费的百度云加速，加快页面渲染速度：[如何使用百度云加速提升网站访问速度](http://www.moguit.cn/#/info?blogUid=af053959672343f8a139ec27fd534c6c)
## 虚拟内存
如果你的服务器内存也是2G的话，请务必先配置一下交换内存【推荐虚拟内存4G】：[CentOS如何增加虚拟内存](http://www.moguit.cn/#/info?blogUid=36ee5efa56314807a9b6f1c1db508871)
## 安装Docker
因为我们需要拉取镜像，所以需要在服务器提前安装好Docker，首先配置一下Docker的阿里yum源
```bash
cat >/etc/yum.repos.d/docker.repo> /etc/docker/daemon.json  如果Github下载过于缓慢，备用地址【下载后解压zip】：[点我传送](https://wws.lanzous.com/iTHoIiuilvi)
然后选择Linux版本下载
![image-20201127211547030](images/image-20201127211547030.png)
把下载到的文件使用Xftp工具，拷贝到 `/usr/local/bin/` 目录下
```bash
# 重命名
mv docker-compose-Linux-x86_64  docker-compose
# 加入执行权限
sudo chmod +x /usr/local/bin/docker-compose
# 查看docker-compose版本
docker-compose -v
```
## 开放安全组
下面我们需要将一些端口暴露到外网能够访问，所以需要开放的安全组，如果是使用阿里云的小伙伴，必须在 阿里云的官网，配置相应的安全组，不然外面是没办法访问的。关于安全组的配置，在云服务器ECS的管理页面
![image-20201128205607264](images/image-20201128205607264.png)
在点击配置规则
![image-20201128205621790](images/image-20201128205621790.png)
然后点击右上角按钮，把需要用到的端口号都填写进去
![image-20201128205731724](images/image-20201128205731724.png)
【此处为了测试暴露了全部需要用到端口，后期小伙伴可以根据自己的需要进行端口的开放】
按照下面的规则，把每一个添加进去即可, 需要添加的端口号有
```bash
RabbitMQ消息队列：15672
Zipkin链路追踪: 9411
发Email端口：465   
图片资源：8600   
前端Web页面:9527    
后端Admin页面：9528  
Redis:6379   
Mysql:3306   
Tomcat[里面部署的solr]:8080
HTTP端口：80
Kibana端口：5601
mogu_admin端口：8601
mogu_picture端口：8602
mogu_web端口：8603
mogu_sms端口：8604
mogu_search端口：8605
mogu_monitor端口：8606
mogu_gateway端口：8607
nacos端口: 8848
sentinel端口: 8070
portainer端口：9000
```
![image-20200209125938397](images/f9632cf3b2b9452194eaa5c7e0a3c0de)
## 一键部署博客
### 创建网络
因为Docker容器之间，需要互相通信访问，所以我们需要创建我们的Docker网络
```bash
docker network create mogu
```
### 拷贝到服务器
下面将源码中的 `docker-compose` 文件夹拷贝到我们的服务器中
![image-20201128215644896](images/image-20201128215644896.png)
首先我们来查看一下docker-compose的目录结构
![image-20201212095110226](images/image-20201212095110226.png)
- bin：相关一键启动脚本的目录
  - completeStartup.sh：完整版启动脚本
  - completeShutdown.sh：完整版关闭脚本
  - kernStartup.sh：核心版启动脚本【只包含必要的组件】
  - kernShutdown.sh：核心版关闭脚本
  - update.sh：用于更新镜像【同步最新代码时使用】
- config：存放配置文件
- data：存放数据文件
- log：存放日志文件
- yaml：存放docker compose的yaml文件
下面我们开始，将docker-compose文件夹，拷贝服务器目录位置随意，我是拷贝到  `/root/docker-compose` 目录，然后给命令设置执行权限
```bash
# 进入目录
cd docker-compose
# 添加执行权限
chmod +x bin/kernStartup.sh
chmod +x bin/kernShutdown.sh
chmod +x bin/update.sh
chmod +x bin/wait-for-it.sh
```
### 修改前端配置
关于前端配置的修改，提供了两种方式
- 自动修改：通过python脚本获取外网地址，然后一键替换【虚拟机部署的无效】
- 手动修改：如果在虚拟机中部署，必须使用手动修改的方式
### 自动修改
首先需要进入 **docker-compose/bin** 文件夹，里面提供了自动替换ip的python脚本
```bash
# 进入到bin目录
cd bin
# 执行脚本
python2 replaceIp.py
```
执行完后，将会修改我们配置文件中的ip地址
![image-20210103150812306](images/image-20210103150812306.png)
tip：该脚本只能在云服务器上，才能获取到精确的外网地址，如果采用NAT网络模式的虚拟机，获取的IP会有问题，需要自己手动进行ip地址的修改~
### 手动修改
针对虚拟机中部署，我们需要手动修改配置
```bash
# 修改vue_mogu_admin项目配置
vim config/vue_mogu_admin.env
# 修改vue_mogu_web项目配置
vim config/vue_mogu_web.env
```
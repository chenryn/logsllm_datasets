# 使用Docker快速搭建蘑菇博客(Eureka版)
最近几天一直在研究怎么样才能够快速搭建蘑菇博客项目，对了，我的服务器是阿里云购买的云服务器ECS，配置是 1核2G ，学生优惠价，100多一年。。。 嗯，这应该是搭建蘑菇博客的最低配置了，内存少于2G的话，可能会启动不起来，本来2G也是不够用的，我是把所有的微服务和solr都放到一个tomcat中，才勉强跑起来的。 目前为了更加方便大家的部署，我已经修改成jar包的方式进行部署启动了，tomcat仅用于作为solr启动的web容器。
如果你的服务器内存也是2G的话，请务必先配置一下交换内存：[CentOS如何增加虚拟内存](http://www.moguit.cn/#/info?blogUid=36ee5efa56314807a9b6f1c1db508871)
如果你也拥有对应的域名并且备案了的话，可以给蘑菇博客配置域名的方式访问：[蘑菇博客配置域名解析](http://moguit.cn/#/info?blogUid=06565868c0e86fe8125a9d55430cd266)
如果你的服务器带宽只有1M，可以使用免费的百度云加速，加快页面渲染速度：[如何使用百度云加速提升网站访问速度](http://www.moguit.cn/#/info?blogUid=af053959672343f8a139ec27fd534c6c)
> tip：特别注意，因为镜像中的代码可能不是最新版本，因此推荐在按照本篇博客，安装好docker环境后，需要在参考 [蘑菇博客部署阿里云(Eureka版)](http://www.moguit.cn/#/info?blogUid=ab8377106a0d4b9f8d66131e4312c69e) 这篇博客，重新将前后端代码都重新部署一遍，同时也记得把doc中的两个SQL文件也重新导入，确保服务器为最新代码
如果你之前安装好了蘑菇博客的docker环境，修改的博客的源码，想要重新发布到自己服务器上：[蘑菇博客如何部署到阿里云服务器(Eureka版)](http://www.moguit.cn/#/info?blogUid=ab8377106a0d4b9f8d66131e4312c69e)
因为配置那些环境比较麻烦，（主要包括Nginx，Solr，Redis，Tomcat，Mysql，RabbitMQ）当然如果小伙伴喜欢自己配置的话，也可以不使用我搭建好的镜像，可以参考下面几篇博客哦，希望你也能够配置成功的~！（想直接通过Docker部署的，可以忽略下面几步..）
1、[CentOS下如何安装Nginx](http://www.moguit.cn/#/info?blogUid=e8d3e38ba35b4765ae128256eb44e341)
2、[CentOS下Rdeis的安装和部署](http://www.moguit.cn/#/info?blogUid=d0e2c4337d7a4a85b176834c8c674fdf)
3、[CentOS下Solr的安装和部署](http://www.moguit.cn/#/info?blogUid=7c7404c456904be5b7736238f28d2515)
4、[CentOS下Mariadb的安装和部署](http://www.moguit.cn/#/info?blogUid=d5b6dff48e5d42b1afcbf6ab591bdab1)
5、[CentOS下RabbitMQ的安装和部署](http://www.moguit.cn/#/info?blogUid=2af543cdbd4342e1812e72687aac4580)
6、[CentOS下ElasticSearch的安装和部署](http://moguit.cn/#/info?blogUid=ee342088a5d0f5b96bcb4582d9b563aa)
好了。下面我介绍的是用Docker快速搭建蘑菇博客。话不多说，下面我就直接进入正题。
## 注册Docker账号
首先大家先去DockerHub注册账号，用于拉取Docker镜像和存储镜像
注意：注册DockerHub的目的，是为了能够方便以后大家把自己的镜像上传上去，如果DockerHub无法访问，或者不想上传镜像的话，可以忽略这一步，同时在3步 也忽略 docker login，直接进行Docker pull 拉取我的镜像即可
DockerHub官网：[点我传送](https://hub.docker.com/)
关于更多docker命令和介绍，可以看这篇博客：[Docker常用命令](http://www.moguit.cn/#/info?blogUid=8974a6ce5bae4bf68f1aa37f07c96d0f)
## Docker安装和启动
注册成功后，进入我们的CentOS系统中（如果是Ubuntu的话，可能安装docker的方式不同，请自行百度安装）
下面介绍的是使用yum方式安装docker
### 配置docker的阿里云yum源
```
cat >>/etc/yum.repos.d/docker.repo<<EOF
[docker-ce-edge]
name=Docker CE Edge - \$basearch
baseurl=https://mirrors.aliyun.com/docker-ce/linux/centos/7/\$basearch/edge
enabled=1
gpgcheck=1
gpgkey=https://mirrors.aliyun.com/docker-ce/linux/centos/gpg
EOF
```
###  安装docker
```
# yum安装
yum -y install docker-ce
#查看docker版本
docker --version  
# 设置开机自启
systemctl enable docker
# 启动docker
systemctl start docker
```
## Docker login登录
使用Docker login命令登录，需要输入刚刚注册的账号和密码（ps：如果不想发布镜像到dockerhub，可以忽略）
```
# 登录dockerhub
docker login
```
## 拉取蘑菇博客的镜像
```
docker pull moxi/mogu_blog
```
因为镜像有点大，所以拉取的话，可能会有点慢，所以耐下等待下
![image-20200209122416398](images/image-20200209122416398.png)
如果拉取失败，或者出现超时的情况、或者拉取过慢，可以尝试使用下面的方法： [CentOS7中Docker拉取镜像失败的解决方法](http://www.moguit.cn/#/info?blogUid=5296cfe28b35caa808a5387ff95734c7)
如果还是拉取速度很慢的话，推荐在早上的时候拉取镜像，因为DockerHub是国外的网站，早上的时候，他们美国这边都已经到了晚间了，基本不占用太多带宽，拉取速度会更快一些~
## 查看镜像
拉取成功后，使用命令查看已经拉取的镜像
```
docker images
```
![image-20200209122441971](images/image-20200209122441971.png)
好了，能看到刚刚拉取的镜像，大概有4.75G大（ps.. 现在因为装了很多东西..已经10多G了），因为这里面包含了需要图片资源和项目的一些安装包。
## 制作蘑菇博客docker容器
```
docker run --privileged -d -it -h mogu_blog_2 --name mogu_blog_2 -v /etc/localtime:/etc/localtime:ro -p 11122:22 -p 15672:15672 -p 8600:8600 -p 9527:9527 -p 9528:9528 -p 6379:6379 -p 3306:3306 -p 80:80 -p 8080:8080 -p 8601:8601 -p 8602:8602 -p 8603:8603 -p 8604:8604 -p 8605:8605 -p 8606:8606 -p 8607:8607 -p 8761:8761 -p 5601:5601 -p 9411:9411 -p 465:465 moxi/mogu_blog /usr/sbin/init
```
使用下面的命令，就能够制作成一个docker容器了，他会将上面写的一些端口号都映射到宿主机中，所以宿主机那些端口号不能别占用了哦。
当然同时，宿主机的那些端口号也必须开放，如果是使用阿里云的小伙伴，必须在 阿里云的官网，配置相应的安全组，不然外面是没办法访问的。
关于安全组的配置，在云服务器ECS的管理页面
![image-20200209125847329](images/image-20200209125847329.png)
在点击配置规则
![image-20200209125905430](images/image-20200209125905430.png)
然后点击右上角按钮，把需要用到的端口号都导入进去
![image-20200209125919324](images/image-20200209125919324.png)
安装下面的规则，把每一个添加进去即可, 需要添加的端口号有：
```bash
蘑菇Docker内部容器SSH连接：11122
RabbitMQ消息队列：15672
Zipkin链路追踪: 9411
发Email端口：465   
图片资源：8600   
前端Web页面:9527    
后端Admin页面：9528  
Redis:6379   
Mysql:3306   
Tomcat(里面部署的solr):8080
HTTP端口：80
Kibana端口：5601
mogu_admin端口：8601
mogu_picture端口：8602
mogu_web端口：8603
mogu_sms端口：8604
mogu_search端口：8605
mogu_monitor端口：8606
mogu_gateway端口：8607
mogu_eureka端口：8761
```
![image-20200209125938397](images/image-20200209125938397.png)
## 查看容器状态
好了，回到刚刚的内容，我们在执行第六步的时候，已经制作好了容器了，使用下面的命令，查看容器状态
```
# 查看容器状态
docker ps -a
```
![image-20200209125953803](images/image-20200209125953803.png)
## 打开XShell，连接
![image-20200209130011043](images/image-20200209130011043.png)
输入用户名： root
![image-20200209130023427](images/image-20200209130023427.png)
输入密码：mogu2018
![image-20200209130036402](images/image-20200209130036402.png)
成功进入系统，下面我们就需要把对应的服务都开启
注意：该密码是docker镜像的初始密码，如果需要更改的话，可以使用下列命令更改密码
```
passwd
```
## 启动对应的服务
### 启动Nginx
```
# 进入nginx的安装目录下
cd /soft/nginx/sbin/
# 启动nginx
./nginx
```
好吧，启动报错
![image-20200209130104979](images/image-20200209130104979.png)
看问题需要创建一个目录，那么就开始创建吧
```
mkdir -p /var/run/nginx
```
再次使用启动命令，启动成功
![image-20200209130124155](images/image-20200209130124155.png)
我们在使用命令 ，查看已经启动的端口号
```
netstat -tunlp
```
我们已经看到了，现在已经开机自启了 RabbitMQ的 5672 15672 ， mysql的 3306， 其他的一些就是项目的端口，现在我们还需要启动 redis的 6379 和 tomcat的 8080
![image-20200209130139403](images/image-20200209130139403.png)
注意：如果我们查看端口号没有RabbitMQ，我们需要手动启动对应的服务
新开一个xshell连接，启动rabbitmq：
```
# 后台启动RabbitMQ
rabbitmq-server -detached
```
### 启动redis
```
# 进入redis的安装目录
cd /soft/redis/bin/
# 后台启动redis
./redis-server redis.conf
# 查看启动端口号
netstat -tunlp
```
 我们看到redis已经正常启动了
![image-20200209130156442](images/image-20200209130156442.png)
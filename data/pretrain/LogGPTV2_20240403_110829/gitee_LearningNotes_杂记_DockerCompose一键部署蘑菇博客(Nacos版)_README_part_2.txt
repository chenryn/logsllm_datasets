可以直接拷贝在本地，使用记事本进行修改，或者通过vim的全局替换命令
```bash
:%s/120.78.126.96/192.168.177.150/g
```
### 开始部署
首先到**bin**目录，执行 `kernStartup.sh` 开始一键部署，该脚本将安装蘑菇博客所需的核心服务
```bash
# 进入到bin目录
cd bin
# 启动一键部署脚本 【核心版脚本】
sh kernStartup.sh
# 一键关闭【需要关闭时使用】
sh kernShutdown.sh
```
> 注意：如果执行一键部署脚本 kernStartup.sh 的时候，出现  $'\r': command not found  文件
>
> 可能是因为windows与Unix文本编辑器默认格式不同引起的，因此需要进行转换
>
> ```bash
> # 安装 dos2unix
> yum -y install dos2unix*
> # 转换脚本
> dos2unix kernStartup.sh
> dos2unix kernShutdown.sh
> dos2unix update.sh
> dos2unix wait-for-it.sh
> ```
执行完成后，就会在我们的镜像仓库中拉取对应的镜像【如果本地没有的话】
![image-20201128173111688](images/image-20201128173111688.png)
我们在一边拉取镜像的时候，我们可以看看镜像的拉取情况
```bash
docker images;
```
![image-20201128173252314](images/image-20201128173252314.png)
能够看到我们的镜像已经成功拉取下来了，接着我们看启动的情况
```bash
docker ps -a
```
![image-20201128173343556](images/image-20201128173343556.png)
注意：如果我们通过命令查看，发现某个容器没有正常运行，如下图所示 【没有出错的，可以直接跳过】
![image-20201212095820865](images/image-20201212095820865.png)
是 portainer 容器运行失败，我们就需要对该容器进行重启，可以使用下面命令【找到该容器的 yml脚本】
```bash
docker-compose -f yaml/portainer.yml up -d
```
## 运行测试
### 运行容器查看 【默认未启动】
我们安装了Portainer容器可视化工具，主要进行Docker容器的状态监控，以及镜像和容器的安装，如果需要开启的话，那么执行下面的脚本，进行启动
```bash
docker-compose -f yaml/portainer.yml up -d
```
关于具体Portainer可视化工具的使用，参考博客：[Docker图形化工具Portainer介绍与安装](http://moguit.cn/#/info?blogOid=570)
```bash
# 访问portainer可视化界面【首次需要创建密码，选择local环境】
http://ip:9000
```
![image-20201128210555720](images/image-20201128210555720.png)
### 后台测试
首先我们需要登录Nacos查看后台服务是否成功注册
```bash
# Nacos管理页【默认账号密码：nacos nacos】
http://ip:8848/nacos
```
![image-20201212152323674](images/image-20201212152323674.png)
> 如果还存在某些服务没有注册上来，那么就需要等待一会【因为后台启动需要时间】
我们在通过访问下列swagger接口，测试接口是否正常
```bash
# admin端
http://your_ip:8601/swagger-ui/index.html
# web端
http://your_ip:8603/swagger-ui/index.html
```
如果能够进入下面页面的话，说明后台是没有问题的了，下面我们可以验证一下接口
![img](images/f7aac7c1d46e41fb88cce5918318f509)
验证登录
![img](images/84ed060923214f7cb8df77f0b6bc512a)
在swagger页面的右上角，有一个authorize的按钮，点击后，将token粘贴进去，即可操作全部接口进行测试了~
![img](images/03c6697dfd3148888215e2f38e99b775)
### 前台测试
接着访问前端和后端页面进行测试即可
```bash
# 前端页面
http://ip:9527
# 后端页面
http://ip:9528
```
前端页面【没有图片，需要自己修改配置后手动上传，关于配置如何修改往下看~】
![image-20201128211416521](images/image-20201128211416521.png)
后端页面【没有图片，需要自己修改配置后手动上传，关于配置如何修改往下看~】
![image-20201128211427634](images/image-20201128211427634.png)
## 修改项目配置
最后在项目成功启动后，我们还需要修改一些配置
### mogu_web配置
我们进入到nacos配置文件管理界面，找到的 mogu_web_prod.yaml文件
![image-20200903164514073](images/95308e71b99846a5998efc4983fa2a9f)
我们需要将下面的域名，改成自己的
```bash
data:
  # 门户页面
  webSite:
    url: http://101.132.122.175/:9527/#/
    # 有域名可以改成如下
    # url: http://www.moguit.cn/#/
  # mogu_web网址，用于第三方登录回调
  web:
    url: http://101.132.122.175/:8603
```
同时在配置文件的最下面，还需要修改第三方注册需要的 clientId 和 ClientSecret：如果不清楚如何获取的小伙伴，可以查看我的这篇博客，在后面部分对ID的获取有相关介绍：
- [SpringBoot+Vue如何集成第三方登录JustAuth](http://moguit.cn/#/info?blogUid=8cbadb54967257f12d6cc7eb1a58a361)
-  [使用JustAuth集成QQ登录](http://www.moguit.cn/#/info?blogUid=fe9e352eb95205a08288f21ec3cc69e0)
```bash
# 第三方登录
justAuth:
  clientId:
    gitee: XXXXXXXXXXXXXXXXXXXXXX
    github: XXXXXXXXXXXXXXXXXXXXXX
    qq: XXXXXXXXXXXXXXXX # APP ID 
  clientSecret:
    gitee: XXXXXXXXXXXXXXXXXXXXXX
    github: XXXXXXXXXXXXXXXXXXXXXX
    qq: XXXXXXXXXXXXXXXXXX # APP Key
```
### mogu_sms配置
我们进入到nacos配置文件管理界面，找到的 mogu_sms_prod.yaml文件
![image-20200903164316451](images/4f8f8ad92d3b47f1b28768f02167a334)
在mogu_sms中，主要修改的就是邮箱的配置，我们将发送邮件的信息改成自己的
```bash
#mail
mail:
    username: PI:EMAIL
    password: XXXXXXX #授权码开启SMTP服务里设置
```
注意，上面的password是授权码，授权码不是密码，以163邮箱为例，我们需要开启SMTP服务，然后设置授权码
![image-20200722090457339](images/c1f29c98397442c385cfb151ae5a76fc)
### 修改图片配置
图片默认使用的是本地图片上传，如果想使用其它的存储方式，可以参考另外的博客
- [蘑菇博客配置七牛云存储](http://www.moguit.cn/#/info?blogUid=735ed389c4ad1efd321fed9ac58e646b)
- [使用Minio搭建对象存储服务](http://www.moguit.cn/#/info?blogUid=a1058b2d030310e2c5d7b0584e514f1f)
本文主要以本地文件存储为例，我们到系统配置，首先修改图片显示的本地域名
![image-20201128212328950](images/image-20201128212328950.png)
修改完成后，进行保存，然后在图片管理上传新的图片
![image-20201128212826334](images/image-20201128212826334.png)
>  要是图片无法正常显示，可以F12看看图片路径是否是修改后的IP，同时对应的 8600端口的 安全组是否开放
最后到博客管理页面，编辑博客，然后选择图片插入即可~
![image-20201128213307577](images/image-20201128213307577.png)
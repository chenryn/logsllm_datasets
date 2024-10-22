# 蘑菇博客部署到阿里云服务器（Eureka分支）
## 前言
最近很多小伙伴问我如何把蘑菇博客部署在自己的云服务器中，今天花费了一些时间整理一下博客部署的过程，希望能够对大家有所帮助，好了话不多说，下面开始进入正式的部署过程。
如果还没有安装好对应的环境话，需要按这篇博客搭建好环境：[使用Docker快速搭建蘑菇博客（Eureka分支）](http://moguit.cn/#/info?blogUid=ab8377106a0d4b9f8d66131e4312c69e)
如果已经拥有域名的小伙伴，并且想给蘑菇博客配置域名解析：可以参考这篇博客：[蘑菇博客配置域名解析](http://moguit.cn/#/info?blogUid=06565868c0e86fe8125a9d55430cd266)
如果本博客教程在搭建的时候存在疑惑，那么可以参考我录制的视频教程：[利用阿里云免费服务器搭建个人博客](https://www.bilibili.com/video/BV1c5411b7EZ?t=117)
本文不再重复叙述 nginx、rabbitmq、mysql、solr以及redis的安装和启动，如果了解，请移步至上一篇博客~
## 查看当前Git分支
首先我们需要将项目拉取下来，然后进入到mogu_blog_v2目录
```bash
# 拉取项目
git clone https://gitee.com/moxi159753/mogu_blog_v2.git
```
首先判断当前分支是否是Eureka分支，使用下面命令查看
```bash
git branch
```
这里显示的是目前在Nacos分支，所以我们需要切换到Eureka分支
![image-20201110090336834](images/image-20201110090336834.png)
使用下面命令切换分支
```bash
# 切换Eureka分支
git checkout Eureka
```
![image-20201110090632776](images/image-20201110090632776.png)
切换好分支后，后面我们就可以进行 maven依赖安装了
## 重新导入数据库脚本
因为之前部署的docker环境中的数据库脚本可能不是最新的，因此在配置好docker环境后，我们需要远程连接上我们docker服务器中的Mysql，我们进入doc文件夹
```
mogu_blog.sql：代表mogu_blog数据库的文件
mogu_blog_update.sql：代表mogu_blog在后续开发时候更新的字段）
mogu_picture.sql：代表mogu_picture数据库文件
mogu_picture_update.sql：代表mogu_picture在后续开发时候更新的字段）
nacos_config.sql：表示Nacos配置脚本【仅用于Nacos分支】
```
首次导入数据库文件的时候，我们只需要执行mogu_blog.sql 、 mogu_picture.sql文件即可，如果你在之前已经部署了本项目，那么你需要在对应的update.sql文件中，打开后，从中找到没有的字段，复制上执行即可，里面每个字段的添加，都会有对应的日期提示，如果有些字段是你clone项目后添加的，那么你就需要执行它们一遍
【举例】假设我在2020.10.15号部署了项目，那会只需要通过导入 mogu_blog.sql 、mogu_picture.sql 和 nacos_config.sql 导入到数据库即可成功运行。但是后面在 2020.11.17号，又重新拉取了蘑菇博客的源码，想要更新最新的代码，那么这个时候就有两种情况
- 如果你系统里面没有任何数据【也就是没有添加自己的博客】，那么再次 导入 mogu_blog.sql 、mogu_picture.sql 即可
- 如果你系统已经上线【已经添加了自己的一些内容】，那么就需要查看 mogu_picture_update.sql 和 mogu_picture_update.sql，然后查看在 2020.10.15 - 2020.11.17 这一段时间内，是否更新了新的字段，如果有更新，那么为了不破坏原有的数据库，那么你需要把里面的字段插入到执行的数据库表中
每次更新的时间，在mogu_*_update.sql 表里都有体现，只需要进去查看即可 ，然后找到对应访问内的，增量更新即可
![img](images/caa45bc804224c9c9441f270c36d6f75)
## SpringBoot项目打包
下面我们进行 maven依赖安装了
```bash
# 拉取项目
git clone https://gitee.com/moxi159753/mogu_blog_v2.git
# 进入mogu_blog_v2目录
cd mogu_blog_v2
# 执行mvn打包命令
mvn clean install
```
完成上面操作后，能看到下面的图，说明已经成功打包了
![image-20200101130036478](images/image-20200101130036478.png)
下面我们需要进入下列的目录，把对应的jar上传到我们之前制作的docker容器中
```
# 进入 mogu_eureka目录
cd mogu_eureka\target
```
我们把下面的jar包复制
![image-20200101131008048](images/image-20200101131008048.png)
然后通过xftp工具，把jar复制到Docker容器的/home/mogu_blog/mogu_eureka目录，替换里面的jar包
```bash
cd /home/mogu_blog/mogu_eureka
```
![image-20200101131046409](images/image-20200101131046409.png)
里面的结构有：
```
./startup.sh  #启动脚本
./shutdown.sh #关闭脚本
mogu_eureka***.jar #springboot打包的可执行jar包
/config #外部配置文件
catalina.out #启动脚本后，生成的日志文件
```
然后我们执行里面的start.sh脚本启动jar包
```
./startup.sh
```
startup.sh脚本其实比较简单，代码如下
```
#!/bin/bash     
nohup java  -Xms256m -Xmx512m -jar  mogu_eureka-0.0.1-SNAPSHOT.jar  > catalina.out  2>&1 &
tail -f ./catalina.out
```
就是通过nohup命令，进行后台启动 java jar包，同时里面-Xms256m -Xmx512m 是指定最大堆和最小堆内存，这个命令就是为了防止tomcat请求太多内存，而造成其它项目无法启动。
shutdown.sh脚本如下所示：
```
#!/bin/bash
PID=$(ps -ef | grep mogu_eureka-0.0.1-SNAPSHOT.jar  | grep -v grep | awk '{ print $2 }')
if [ -z "$PID" ]
then
    echo Application is already stopped
else
    echo kill $PID
    kill $PID
fi
```
大概意思就是，我们找到jar启动的PID，然后使用kill命令杀死即可。
启动mogu_eureka后，我们重复上面的操作，分别把 mogu_picture、mogu_sms、mogu_web、mogu_admin分别执行上述操作，即可完成蘑菇博客后台项目的部署
需要注意的是：mogu_picture项目和mogu_web项目，除了替换对应的jar包外，我们还需要修改对应的配置文件，然后在启动项目
### mogu_picture修改配置
首先我们在启动startup.sh脚本前，先修改对应目录下 config文件夹的application.yml配置文件，直接修改可能会里面是乱码，可以先把它取出来，到window下修改，然后在放入
```
# 进入picture目录下
cd /home/mogu_blog/mogu_picture/config
# 编辑配置
vim application.yml
```
然后找到下面的内容
```yaml
#Data image url
data:
  image:
    url: http://your_ip:8600/
file:
  upload:
    path: /home/mogu_blog/mogu_data/
```
特别注意的是：如果有的小伙伴自己有域名的话，并且已经配置了域名解析，即可换成对应的域名
例如：我的 picture.moguit.cn域名，映射到服务器的8600端口，那么我的配置就可以改成如下所示
```yaml
#Data image url
data:
  image:
    url: http://picture.moguit.cn/
file:
  upload:
    path: /home/mogu_blog/mogu_data/
```
修改完成后，我们启动picture项目
### 修改mogu_web配置文件
同理，找到mogu_web下的config文件，我们需要将下面的域名，改成自己的IP地址
```yaml
#Data image url
data:
  # 门户页面
  webSite:
    url: http://101.132.122.175:9527/#/
  # mogu_web网址，用于第三方登录回调
  web:
    url: http://101.132.122.175:8603
```
如果拥有域名的小伙伴，可以将配置改成如下形式
```yaml
#Data image url
data:
  # 门户页面
  webSite:
    url: http://www.moguit.cn:9527/#/
  # mogu_web网址，用于第三方登录回调
  web:
    url: http://101.132.122.175:8603
```
同时在配置文件的最下面，还需要修改第三方注册需要的 clientId 和 ClientSecret：如果不清楚如何获取的小伙伴，可以查看我的这篇博客，在后面部分对ID的获取有相关介绍：[SpringBoot+Vue如何集成第三方登录JustAuth](http://moguit.cn/#/info?blogUid=8cbadb54967257f12d6cc7eb1a58a361)
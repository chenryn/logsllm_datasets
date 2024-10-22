### 启动tomcat中的solr
tip：如果配置了Solr作为全文检索，那么需要启动Solr，否则可以忽略这一步
```
# 进入tomcat目录
cd /soft/tomcat/bin
# 启动
./startup.sh
# 查看启动信息
tail -f ../logs/catalina.out
```
### 启动微服务
启动 mogu_eureka & mogu_picture & mogu_sms & mogu_admin & mogu_web
```
#进入到项目目录
cd /home/mogu_blog
```
我们查看项目结构，有以下几个文件夹
![image-20200209130210835](images/image-20200209130210835.png)
下面说明每个文件夹的作用
```
mogu_admin：admin端API接口服务
mogu_data：存在蘑菇博客的图片资源
mogu_eureka：服务发现
mogu_picture: 图片服务器，用于图片上传和下载
mogu_sms: 消息发送服务器，用于邮件和短信发送
mogu_web：web端API接口服务
mogu_monitor：监控模块
mogu_zipkin：链路追踪模块
vue_mogu_admin：VUE的后台管理页面
vue_mogu_web：VUE的门户网站
```
首先进入mogu_eureka目录下
我们查看一下目录结构
![image-20200209130224724](images/image-20200209130224724.png)
```
./startup.sh  #启动脚本
./shutdown.sh #关闭脚本
mogu_admin***.jar #springboot打包的可执行jar包
/config #外部配置文件
catalina.out #启动脚本后，生成的日志文件
```
然后我们使用下面的命令进行启动
```
# 进入mogu_eureka目录
cd mogu_eureka
# 启动项目
./startup.sh
```
不过需要注意的是：mogu_picture 、 mogu_web、mogu_sms 我们还需要修改一些配置，才能够启动成功
> tip：因为镜像中的代码可能不是最新版本，因此推荐在按照本篇博客，安装好docker环境后，需要在参考下面蘑菇博客部署阿里云这篇博客，重新将前后端代码都重新部署一遍，同时也记得把doc中的两个SQL文件也重新导入，确保服务器为最新代码~
### mogu_picture修改配置
首先我们在启动startup.sh脚本前，先修改对应目录下 config文件夹的application.yml配置文件，直接修改可能会里面是乱码，可以先把它取出来，到window下修改，然后在放入
```
# 进入picture目录下
cd /home/mogu_blog/mogu_picture/config
# 编辑配置
vim application.yml
```
然后找到下面的内容，把对应的ip地址改成自己云服务器的即可
```
#Data image url
file:
  upload:
    path: /home/mogu_blog/mogu_data/
```
修改完成后，我们回到上级目录，执行启动脚本
```
# 返回上一级
cd ..
# 启动项目
./startup.sh
```
### mogu_web修改配置
同理，找到mogu_web下的config文件，我们需要将下面的域名，改成自己的IP地址
```
#Data image url
data:
  # 门户页面
  webSite:
    url: http://101.132.122.175:9527/#/
  # mogu_web网址，用于第三方登录回调
  web:
    url: http://101.132.122.175:8603
  # 静态资源映射，通过nginx
  image:
    url: http://101.132.122.175:8600/
```
同时在配置文件的最下面，还需要修改第三方注册需要的 clientId 和 ClientSecret：如果不清楚如何获取的小伙伴，可以查看我的这篇博客，在后面部分对ID的获取有相关介绍：[SpringBoot+Vue如何集成第三方登录JustAuth](http://moguit.cn/#/info?blogUid=8cbadb54967257f12d6cc7eb1a58a361)
```yml
# 第三方登录
justAuth:
  clientId:
    gitee: XXXXXXXXXXXXXXXXXXXXXX
    github: XXXXXXXXXXXXXXXXXXXXXX
  clientSecret:
    gitee: XXXXXXXXXXXXXXXXXXXXXX
    github: XXXXXXXXXXXXXXXXXXXXXX
```
###  mogu_sms修改配置
在mogu_sms中，主要修改的就是邮箱的配置，我们将发送邮件的信息改成自己的
```yml
#mail
mail:
    username: PI:EMAIL
    password: XXXXXXX #授权码开启SMTP服务里设置
```
注意，上面的password是授权码，授权码不是密码，以163邮箱为例，我们需要开启SMTP服务，然后设置授权码
![image-20200722090457339](images/image-20200722090457339.png)
修改完成后，我们启动对应的项目即可，最终我们需要启动的项目有： mogu_eureka，mogu_picture, mogu_sms, mogu_admin, mogu_web
**tip:（用于以后使用图形化客户端进行连接）**
mysql的账号和密码是 root  mogu2018
redis的密码是 mogu2018
## 验证是否后台是否启动成功
等服务器都启动完成后，下面我们验证一下后台是否正常启动，访问下列的地址：
```
http://your_ip:8761
```
首次登录会出现登录框：用户名：user  密码：password123
如果我们看到下面四个服务都注册到eureka中，那说明启动成功
![image-20200209130259959](images/image-20200209130259959.png)
我们在通过访问下列swagger接口，测试接口是否正常
```
http://your_ip:8601/swagger-ui.html
http://your_ip:8603/swagger-ui.html
```
如果能够进入下面页面的话，说明后台是没有问题的了，下面我们可以验证一下接口
![image-20200209130313977](images/image-20200209130313977.png)
验证登录
![image-20200209130324333](images/image-20200209130324333.png)
登录功能正常使用，我们把token复制到来，然后在swagger页面的右上角，有一个authorize的按钮，点击后，将token粘贴进去，即可操作全部接口进行测试了~
![image-20200209130336478](images/image-20200209130336478.png)
## 修改前端项目配置
我们现在需要修改两个地方的配置，分别是：vue_mogu_admin 和 vue_mogu_web
下面我们到 vue_mogu_web/config/目录下，修改prod.env.js文件
![image-20200209130347971](images/image-20200209130347971.png)
把里面的ip地址换成你主机的地址即可
```
WEB_API: '"http://your_ip:8603"',
PICTURE_HOST: '"http://your_ip:8600"',
```
同理，在修改 vue_mogu_admin下的地址，把里面的ip地址，换成你服务器的ip即可
![image-20200209130403916](images/image-20200209130403916.png)
修改完成后，需要进行重新编译~ 打包~ 部署~
我们首先在 vue_mogu_admin 目录下，执行下列命令进行打包（打包过程中.....可能会遇到一些语法规范错误，请无视~）
```
# 安装依赖
npm install --registry=https://registry.npm.taobao.org
# 打包
npm run build
```
打包完成后，会生成一个dist目录，我们将整个dist目录，压缩成 zip格式
![image-20200209130425874](images/image-20200209130425874.png)
然后使用xftp工具，丢入到我们的前端目录下，目录在 /home/mogu_blog/vue_mogu_admin
![image-20200209130438506](images/image-20200209130438506.png)
注意：如果该文件夹下存在 dist文件夹，我们需要将其删除，然后在解压
然后使用下面命令进行解压
```
unzip dist.zip
```
同理的操作，在执行一下上述操作，将vue_mogu_web项目也进行打包，部署到 /home/mogu_blog/vue_mogu_web目录下即可
## 访问蘑菇博客项目
### 访问前端项目
例如： 192.168.1.101:9527 
![image-20200209130524162](images/image-20200209130524162.png)
### 访问后端项目
 ip地址:9528  用户名和密码是： admin mogu2018
![image-20200209130547785](images/image-20200209130547785.png)
## 总结：
好了，到目前为止，蘑菇博客已经搭建完成。当然小伙伴并不是拉取来就能直接用的， 如果ip地址不一样的话，是不能直接使用的，后面的话，需要拉取源码后，修改对应的配置信息后，然后在打包部署，才能够使用的。
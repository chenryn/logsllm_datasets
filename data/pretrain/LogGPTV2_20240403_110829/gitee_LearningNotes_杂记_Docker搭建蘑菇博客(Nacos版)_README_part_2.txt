```
启动后，会有如下提示
![image-20200903161239748](images/image-20200903161239748.png)
我们可以通过查看日志进行判断nacos是否启动成功
![image-20200903161406977](images/image-20200903161406977.png)
如果没有报错信息，说明Nacos已经启动成功了，下面我们可以进入到Nacos的图形化管理页面
```bash
http://your_ip:8848/nacos
```
打开后，输入默认账号密码：nacos  nacos，即可进入系统，查看到项目的配置
![image-20200903161619843](images/image-20200903161619843.png)
如果需要更改配置，以后到这里完成就可以了，修改配置后，重启服务即可生效
### 启动Sentinel（可选）
Sentinel是用来做服务的熔断、雪崩、限流，相当于原来的Hystrix，但是提供了更加强大的功能，如果想要了解Sentinel的更多操作，可以参考这两篇博客
- [【SpringCloud】使用Sentinel实现熔断和限流](http://moguit.cn/#/info?blogUid=408e9c889ebf96a66af2adfdc258ba5f)
- [CentOS下安装Sentinel](http://moguit.cn/#/info?blogUid=b100fde21ac0b61414dbaa74d2db7192)
首先进入到Sentinel的启动目录下进行启动
```bash
# 进入到sentinel目录
cd /soft/sentinel
# 启动Sentinel
./startup.sh
# 查看日志
```
然后进入到Sentinel的图形化界面
```bash
http://your_ip:8070
```
输入默认账号密码：sentinel  sentinel，进入到管理界面，更多关于Sentinel的操作，可以查看[这篇博客](http://moguit.cn/#/info?blogUid=408e9c889ebf96a66af2adfdc258ba5f)
![image-20200903162631281](images/image-20200903162631281.png)
### 启动微服务
启动 mogu_picture & mogu_sms & mogu_admin & mogu_web
```
#进入到项目目录
cd /home/mogu_blog
```
我们查看项目结构，有以下几个文件夹
![image-20200903163514966](images/image-20200903163514966-1599124136538.png)
下面说明每个文件夹的作用
```
mogu_admin：admin端API接口服务
mogu_data：存在蘑菇博客的图片资源
mogu_monitor：服务监控
mogu_picture: 图片服务器，用于图片上传和下载
mogu_sms: 消息发送服务器，用于邮件和短信发送
mogu_web：web端API接口服务
mogu_zipkin：链路追踪模块
vue_mogu_admin：VUE的后台管理页面
vue_mogu_web：VUE的门户网站
```
#### 启动Admin后台服务
首先进入mogu_admin目录下
我们查看一下目录结构
![image-20200209130224724](images/image-20200209130224724-1599124105899.png)
```
./startup.sh  #启动脚本
./shutdown.sh #关闭脚本
mogu_admin***.jar #springboot打包的可执行jar包
/config #外部配置文件
catalina.out #启动脚本后，生成的日志文件
```
然后我们使用下面的命令进行启动
```
# 进入mogu_admin目录
cd mogu_admin
# 启动项目
./startup.sh
```
> tip：因为镜像中的代码可能不是最新版本，因此推荐在按照本篇博客，安装好docker环境后，需要在参考下面蘑菇博客部署阿里云这篇博客，重新将前后端代码都重新部署一遍，同时也记得把doc中的三个SQL文件也重新导入，确保服务器为最新代码~
### mogu_web修改配置
我们进入到nacos配置文件管理界面，找到的 mogu_web_prod.yaml文件
![image-20200903164514073](images/image-20200903164514073-1599124105900.png)
我们需要将下面的域名，改成自己的
```
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
修改完成后，启动项目
```bash
# 进入mogu_web目录
cd mogu_web
# 启动项目
./startup.sh
```
###  mogu_sms修改配置
我们进入到nacos配置文件管理界面，找到的 mogu_sms_prod.yaml文件
![image-20200903164316451](images/image-20200903164316451-1599124105900.png)
在mogu_sms中，主要修改的就是邮箱的配置，我们将发送邮件的信息改成自己的
```yml
#mail
mail:
    username: PI:EMAIL
    password: XXXXXXX #授权码开启SMTP服务里设置
```
注意，上面的password是授权码，授权码不是密码，以163邮箱为例，我们需要开启SMTP服务，然后设置授权码
![image-20200722090457339](images/image-20200722090457339-1599124105900.png)
修改完成后，我们启动对应的项目即可，最终我们需要启动的项目有： mogu_picture, mogu_sms, mogu_admin, mogu_web、mogu_gateway
**tip:（用于以后使用图形化客户端进行连接）**
mysql的账号和密码是 root  mogu2018
redis的密码是 mogu2018
## 验证是否后台是否启动成功
等服务器都启动完成后，下面我们验证一下后台是否正常启动，回到我们的Nacos管理界面
```
http://your_ip:8848/nacos
```
如果我们看到下面五个服务都注册到Nacos中，那说明启动成功
- mogu_picture
- mogu_sms
- mogu_admin
- mogu_web
- mogu_gateway
如下图所示
![image-20201212144805069](images/image-20201212144805069.png)
我们在通过访问下列swagger接口，测试接口是否正常
```
http://your_ip:8601/swagger-ui/index.html
http://your_ip:8603/swagger-ui/index.html
```
如果能够进入下面页面的话，说明后台是没有问题的了，下面我们可以验证一下接口
![img](images/f7aac7c1d46e41fb88cce5918318f509)
验证登录
![img](images/84ed060923214f7cb8df77f0b6bc512a)
然后执行完成后，复制到token
![img](images/ec60e235b7264864a404abc8cd24248f)
然后在swagger页面的右上角，有一个authorize的按钮，点击后，将token粘贴进去，即可操作全部接口进行测试了~
![img](images/03c6697dfd3148888215e2f38e99b775)
## 修改前端项目配置
下面我们需要修改前端地址，如果不修改的话，默认是请求的是蘑菇演示环境的后台接口【！！所以这里切记】
![image-20201130110943750](images/image-20201130110943750.png)
我们现在需要修改两个地方的配置，分别是：vue_mogu_admin 和 vue_mogu_web 目录下
### 修改vue_mogu_admin配置
```bash
# 进入dist目录
cd vue_mogu_admin/dist
# 找到index.html【为了方便，可以复制到windows下面修改】
vim index.html
```
然后把里面的ip地址，改成自己的 ip 即可
> 文件是被压缩的，可以使用在线格式化工具：[html在线格式化](https://tool.oschina.net/codeformat/html/)，优化后在进行编辑
![image-20201130105850074](images/image-20201130105850074.png)
注意，上面 `BLOG_WEB_URL` 地址的修改的时候，如果你拥有域名的话，就不要使用IP了
```bash
// 有域名
"BLOG_WEB_URL":"http://demoweb.moguit.cn"
// 没有域名
"BLOG_WEB_URL":"http://120.78.126.96:9527"
```
修改完成后，在把修改后的文件，替换服务器上的 index.html 即可
### 修改vue_mogu_web配置
修改 vue_mogu_web的过程和上面一致
```bash
# 进入dist目录
cd vue_mogu_web/dist
# 找到index.html【为了方便，可以复制到windows下面修改】
vim index.html
```
然后把里面的ip地址，改成自己的 ip 即可
![image-20201130110112326](images/image-20201130110112326.png)
注意，上面 `VUE_MOGU_WEB` 地址的修改的时候，如果你拥有域名的话，就不要使用IP了
```bash
// 有域名
"BLOG_WEB_URL":"http://demoweb.moguit.cn"
// 没有域名
"BLOG_WEB_URL":"http://120.78.126.96:9527"
```
修改完成后，在把修改后的文件，替换服务器上的 index.html 即可
## 访问蘑菇博客项目
### 访问前端项目
例如： http://youip:9527 
![image-20201110155005003](images/image-20201110155005003.png)
tip：需要注意的是，如果图片无法正常显示，请先登录后台管理页面，然后修改对应的域名
关于具体的配置，参考这篇博客：[蘑菇博客配置七牛云存储](http://www.moguit.cn/#/info?blogUid=735ed389c4ad1efd321fed9ac58e646b)
![image-20200903170244575](images/image-20200903170244575-1599124105901.png)
### 访问后端项目
120.78.126.96:9528       用户名和密码是： admin mogu2018 【如果登录不进去，请F12检查，请求的IP地址是否是自己的服务器，如果不是，那么参考前面修改前端项目配置，改成自己的服务器IP】
![image-20200209130547785](images/image-20200209130547785-1599124105901.png)
## 总结
好了，到目前为止，蘑菇博客已经搭建完成。当然小伙伴并不是拉取来就能直接用的， 如果ip地址不一样的话，是不能直接使用的，后面的话，需要拉取源码后，修改对应的配置信息后，然后在打包部署，才能够使用的。
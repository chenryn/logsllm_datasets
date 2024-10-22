# Windows环境下搭建蘑菇博客
## 前言
码云上最近有些小伙伴们问到了蘑菇博客的详细配置信息，突然想想之前本来打算写来着，但是因为各种各样的问题搁置了，现在就在win10环境下对博客的配置进行详细的说明了。
> Tip: 如遇到启动失败的,请先maven clean install 后再尝试启动
IDE得装lombok插件：[IDEA中引入Lombok](http://moguit.cn/#/info?blogUid=4ccb7df5d537f52d954eb15f094c90a3) 
参考：[蘑菇博客如何部署到阿里云服务器](http://www.moguit.cn/#/info?blogUid=89defe3f4a3f317cba9aa0cdb9ff879e) ，在你修改蘑菇博客源码后，将项目打包部署到云服务器
参考：[蘑菇博客切换搜索模式](http://moguit.cn/#/info?blogUid=4042b4f4088e4e37e95d9fc75d97298b)，完成蘑菇博客的搜索引擎切换，目前支持Solr、ElasticSearch、mysql的方式，一般因为服务器配置文件，选择一种搜索方式即可
参考：[蘑菇博客切换七牛云存储](http://moguit.cn/#/info?blogUid=735ed389c4ad1efd321fed9ac58e646b)，配置文件的七牛云对象存储，及本地文件存储
注意！在Windows进行项目启动时，有很多组件可以根据自己的系统配置进行启动，在标题上标注【非必须】的字样，说明该模块可以根据自身配置进行安装。
同时在下载源码后，需要区分当前属于Eureka分支还是Nacos分支，不同的分支安装过程有所差异，在下文均会标记出来~
## 视频教程
特别感谢 [俺是程序狮](https://space.bilibili.com/277038643) 在B站上给蘑菇博客录制的视频教程，里面介绍了windows环境下配置蘑菇博客，如果参考文档遇到了问题的话，可以参考视频进行部署（ps：视频教程基于Eureka版）
- [项目介绍](https://www.bilibili.com/video/BV1Si4y1u7H4)
- [结构介绍与本地Nginx本地图片服务器启动](https://www.bilibili.com/video/BV1AA411e7W5)
- [mysql脚本准备](https://www.bilibili.com/video/BV1kv411v7ND)
- [后台服务启动](https://www.bilibili.com/video/BV1Nv411i7wu)
- [RabbitMQ启动](https://www.bilibili.com/video/BV1mD4y1U7GT)
- [前端项目启动](https://www.bilibili.com/video/BV1B541187Ez)
## 配置JDK
略
## 配置Maven
maven安装成功后，记得添加阿里源，不然有些东西下载会非常慢的
## 配置nginx
nginx的下载直接到nginx官网下载即可
下载完成后，我们需要修改nginx.conf配置文件，加入下面的内容
```bash
#蘑菇博客图片资源
server {
 listen       8600;
 server_name  localhost;
 add_header Access-Control-Allow-Origin *;
 add_header Access-Control-Allow-Methods *;
 add_header Access-Control-Allow-Headers *;
 if ($request_method = 'OPTIONS') {
   return 204;
 }	
 location / {
	root   D:\mogu_blog\data;
	index  index.html index.htm;
 }
}
```
就是将8600端口的请求映射到 D:\mogu_blog\data的目录下，如果没有这个目录的，可以提前创建好，当然不一定在D盘，可以在任意位置，其它位置修改成对应的即可。
不过如果需要修改的话，需要到mogu_picture项目的yml文件里也一起修改对应的配置文件，如下图的 file.upload.path 修改成自定义的即可 【如果是nacos分支，需要在nacos中进行修改】
```bash
#Data image url
file:
  upload:
    path: D:/mogu_blog/data
```
## 配置redis
去redis官网，进行下载：https://redis.io/
然后双击启动即可
![image-20200209121341204](images/image-20200209121341204.png)
> 注意，如果使用docker的方法安装的蘑菇博客镜像，里面设置了默认的密码mogu2018，如果直接复制的本地配置，还需要修改一下默认密码
## 配置RabbitMq
RabbitMQ是一款比较优秀的消息中间件，在这里主要用于同步solr索引和ElasticSearch索引，redis缓存更新，以及邮件和验证码发送等功能。
关于配置，参考这篇博客：[蘑菇博客配置RabbitMQ](http://www.moguit.cn/#/info?blogUid=995e0fccd2b240aabd56a10a688e42d4)
## 配置搜索模块【非必须】
目前蘑菇博客支持三种搜索模式的配置，分别是Solr、ElasticSearch和SQL，小伙伴可以按照自己的服务器配置进行相应的部署。
参考：[蘑菇博客切换搜索模式](http://moguit.cn/#/info?blogUid=4042b4f4088e4e37e95d9fc75d97298b) ，进行三种模式的切换（三种方式选择一种，默认是SQL搜索，可以配置ElasticSearch或者Solr作为全文检索）
### 配置Solr【非必须】
关于window下配置蘑菇博客的solr，其实和我之前写的一篇博客大同小异，在这里我就不多叙述了，详情参考：[CentOS下Solr的安装和部署](http://www.moguit.cn/#/info?blogUid=7c7404c456904be5b7736238f28d2515)
> 注意：需要修改schema.xml文件
最近很多小伙伴说solr不好配置，所以我特意把solr的上传到百度云和七牛云了，小伙伴只需要下载后，放到tomcat的webapps目录下，然后修改一下solrhome的配置，即可完成Solr的部署
蓝奏云：
```bash
https://wws.lanzous.com/i3drtj8l8ja
```
百度云：
```
链接：https://pan.baidu.com/s/1gpKs7oixT8RBn8zuDSiEGQ 
提取码：ditj 
```
下载完成后，解压
![image-20200209121359910](images/image-20200209121359910.png)
然后找到 web.xml文件
![image-20200209121416395](images/image-20200209121416395.png)
修改里面的地址，把路径改成你的目录即可
```
       solr/home
       E:\Software\xampp\tomcat\webapps\solr\solr_home
       java.lang.String
```
然后查看solr admin页面：http://localhost:8080/solr/#/
如果能正常显示，说明已经安装成功
### **配置ElasticSearch（选择性安装）**
关于ElasticSearch的配置和相关介绍，可以参考这篇博客：[Elasticsearch介绍和安装](http://moguit.cn/#/info?blogUid=ee342088a5d0f5b96bcb4582d9b563aa)
Window也可自行百度进行安装，或者直接下载我上传的压缩包完成快速搭建
```
链接：https://pan.baidu.com/s/1X1z47Osm_MBjwSBckhUmTQ 
提取码：pnfp
```
下载完后，解压能看到这个目录
![image-20200209121433345](images/image-20200209121433345.png)
我们首先进入elasticsearch下的config目录，修改elasticsearch.yml文件，把下面两个路径，改成你对应的目录即可
![image-20200209121450887](images/image-20200209121450887.png)
**然后启动ElasticSearch：**
![image-20200209121502904](images/image-20200209121502904.png)
**启动Kibana：**
![image-20200209121514369](images/image-20200209121514369.png)
启动完成后：我们输入网址 
```
http://localhost:5601/
```
如果能出现下面的页面，说明已经成功安装了 ElasticSearch 和 Kibana，在这里kibana只是作为ElasticSearch的图形化显示工具，相当于原来的SolrAdmin页面一样，在生产环境中，可以不部署也行
![image-20200209121540189](images/image-20200209121540189.png)
## 配置Mysql
```bash
# 使用命令把项目clone下来
git clone https://gitee.com/moxi159753/mogu_blog_v2.git
```
然后找到目录下的doc文件夹，里面有个数据库脚本，里面有两个数据库，我们需要提前创建好 mogu_blog 、mogu_picture 、nacos_config这里三个数据库，然后把备份脚本导入即可。
![image-20200908083757671](images/image-20200908083757671.png)
- mogu_blog.sql：代表mogu_blog数据库的文件
- mogu_blog_update.sql：代表mogu_blog在后续开发时候更新的字段（首次无需导入）
- mogu_picture.sql：代表mogu_picture数据库文件
- mogu_picture_update.sql：代表mogu_picture在后续开发时候更新的字段（首次不需要导入）
- nacos_config.sql：代表nacos的配置信息，用来存放每个模块的配置信息 【nacos分支需要导入】
首次导入数据库文件的时候，我们只需要执行mogu_blog.sql 、 mogu_picture.sql、nacos_config即可！！
如果你在之前已经部署了本项目，那么你需要在对应的update.sql文件中，打开后，从中找到没有的字段，复制上执行即可，里面每个字段的添加，都会有对应的日期提示，如果有些字段是你clone项目后添加的，那么你就需要执行它们一遍即可
![image-20200908084447425](images/image-20200908084447425.png)
同时设置数据库访问账户和密码为： admin  admin
当然不设置也没关系，就是后面修改yml文件里面的配置即可
## 配置zipkin链路追踪【非必须】
Zipkin是一个开源的分布式的链路追踪系统，每个微服务都会向zipkin报告计时数据，聚合各业务系统调用延迟数据，达到链路调用监控跟踪。
参考博客：[使用Zipkin搭建蘑菇博客链路追踪](http://www.moguit.cn/#/info?blogUid=35bd93cabc08611c7f74ce4564753ef9)
链路追踪服务可以选择安装，不过如果没有安装的话，在启动的时候会出现这样一个错误，不过该错误不会影响正常使用，可以忽略
```bash
I/O error on POSt request for "http://localhost:9411/api/v2/span" ：connect timeout
```
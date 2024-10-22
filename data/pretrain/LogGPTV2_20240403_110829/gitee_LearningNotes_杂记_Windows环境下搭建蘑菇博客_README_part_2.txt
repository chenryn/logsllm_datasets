## 配置Nacos【Nacos分支】
Nacos是服务注册和配置中心，如果使用的使用的是Eureka作为服务注册中心，那么直接跳过Nacos和Sentinel的安装过程。
参考 [【SpringCloud】使用Nacos实现服务注册发现和配置中心等功能](http://moguit.cn/#/info?blogUid=e6e619349d31dded928c9265c5a9c672)，了解Nacos的使用
参考 [蘑菇博客Nacos部署指南](http://moxi159753.gitee.io/learningnotes/#/./杂记/蘑菇博客Nacos安装指南/README?id=蘑菇博客nacos部署指南)，完成蘑菇博客中Nacos的安装和配置
## 配置Sentinel流量控制【非必须】
Sentinel存在于Nacos分支下，如果你的注册中心是Eureka，那么不需要配置
随着微服务的流行，服务和服务之间的稳定性变得越来越重要。Sentinel 以流量为切入点，从流量控制、熔断降级、系统负载保护等多个维度保护服务的稳定性。
参考[【SpringCloud】使用Sentinel实现熔断和限流](http://moguit.cn/#/info?blogUid=408e9c889ebf96a66af2adfdc258ba5f) ，了解Sentinel以及使用
参考 [蘑菇博客Sentinel安装指南](http://moxi159753.gitee.io/learningnotes/#/./杂记/蘑菇博客Sentinel安装指南/README?id=蘑菇博客sentinel安装指南)，完成蘑菇博客中Sentinel的配置
## 配置zipkin链路追踪【非必须】
Zipkin是一个开源的分布式的链路追踪系统，每个微服务都会向zipkin报告计时数据，聚合各业务系统调用延迟数据，达到链路调用监控跟踪。
链路追踪服务可以选择安装，不过如果没有安装的话，在启动的时候会出现这样一个错误，不过该错误不会影响正常使用，可以忽略。
参考博客：[使用Zipkin搭建蘑菇博客链路追踪](http://www.moguit.cn/#/info?blogUid=35bd93cabc08611c7f74ce4564753ef9)
## 启动后端项目
在全部配置完成后，就可以开始启动项目了，这里我用的编辑器是sts。目前有热心的码云朋友说IDEA不能正常启动项目，后面我经过排查，确实是存在这个文件，最近正在研究是哪块出错导致的。目前蘑菇博客的开发已经迁移到 IDEA中了，感谢[Jetbrains全家桶](https://www.jetbrains.com/?from=mogu_blog_v2)对开源的支持~。
首先进入项目根目录文件夹，执行下面命令
```
# 下载依赖
mvn clean install
```
如果下面都是success，那就说明依赖下载成功了
![image-20200209121557593](images/image-20200209121557593.png)
下面就把项目导入到sts中
![image-20200209121611995](images/image-20200209121611995.png)
关于项目的介绍
```bash
MoguBlog 是一款基于最新技术开发的多人在线、简洁的博客系统。
mogu_admin: 提供admin端API接口服务；
mogu_web：提供web端API接口服务；
mogu_eureka： 服务发现和注册
mogu_picture： 图片服务，用于图片上传和下载；
mogu_sms：消息服务，用于更新ElasticSearch、Solr索引、邮件和短信发送
mogu_monitor：监控服务，集成SpringBootAdmin用于管理和监控SpringBoot应用程序
mogu_spider：爬虫服务（目前还未完善）
mogu_spider：网关服务（目前还未完善）
mogu_zipkin：链路追踪服务，目前使用java -jar的方式启动
mogu_search：搜索服务，ElasticSearch和Solr作为全文检索工具，支持可插拔配置，默认使用SQL搜索
mogu_commons：公共模块，主要用于存放Entity实体类、Feign远程调用接口、以及公共config配置
mogu_utils: 是常用工具类；
mogu_xo: 是存放 VO、Service，Dao层的
mogu_base: 是一些Base基类
doc: 是蘑菇博客的一些文档和数据库文件
vue_mogu_admin：VUE的后台管理页面
vue_mogu_web：VUE的门户网站
uniapp_mogu_web：基于uniapp 和 colorUi 的蘑菇博客移动端门户页面（Nacos分支）
nuxt_mogu_web：Nuxt的门户网站，主要用于支持SEO搜索引擎优化（目前还未完善）
```
 下面进行项目启动
mogu_eureka -> mogu_picture -> mogu_sms -> mogu_admin -> mogu_web（上述模块是必须启动的）
如果是Nacos版本：需要启动  mogu_gateway -> mogu_picture -> mogu_sms -> mogu_admin -> mogu_web
其它一些模块可以根据自己配置进行启动：如 mogu_monitor、SearchApplication、Zipkin等
下面是启动成功的图片 【该图是Eureka版本】
![image-20200209121636765](images/image-20200209121636765.png) 
启动成功后，我们应该能够查看到对应的Swagger接口文档
> tip：需要注意，swagger-ui在nacos版本和eureka版本使用的不一致
>
> eureka版本：swagger-ui使用的是2.X，访问的页面是  http://localhost:8601/swagger-ui.html
>
> nacos版本：swagger-ui使用的是3.X，访问的页面是 http://localhost:8601/swagger-ui/index.html
```
############ admin端swagger ##################
# Eureka分支
http://localhost:8601/swagger-ui.html
# Nacos分支
http://localhost:8601/swagger-ui/index.html
############ picture端swagger ##################
# Eureka分支
http://localhost:8602/swagger-ui.html
# Nacos分支
http://localhost:8602/swagger-ui/index.html
############ web端swagger ##################
# Eureka分支
http://localhost:8603/swagger-ui.html
# Nacos分支
http://localhost:8603/swagger-ui/index.html
```
 Admin端接口文档：
![image-20200209121651260](images/image-20200209121651260.png)
Picture端接口文档
![image-20200209121712009](images/image-20200209121712009.png)
web端接口文档
![image-20200209121727626](images/image-20200209121727626.png)
因为Nacos分支引入了 mogu_gateway作为 微服务的网关入口，以后部署项目后，很多内部的服务端口可能就不会暴露出来了，因此以后测试，就需要我们通过 mogu_gateway提供的Knife4j 接口聚合
```bash
http://localhost:8607/doc.html
```
我们可以通过左上角的下拉框选择我们的微服务接口，使用方法和swagger一致
![image-20201210204040689](images/image-20201210204040689.png)
## 启动前端项目
前端项目使用的是Vue编写的，所以在这之前，需要下载好nodejs，因为nodejs里的npm模块是用于管理vue项目中的依赖，就类似于maven一样
node官网：https://nodejs.org/en/
在安装的时候，记得选择好加入到环境变量中，这样我们就能在任何使用了。
查看是否安装成功： npm -v
![image-20200209121742980](images/image-20200209121742980.png)
1) 安装 vue_mogu_admin 项目的依赖
进入vue_mogu_admin 文件夹内，使用下面命令进行安装
```bash
# 指定node-sass的国内镜像源
npm i node-sass --sass_binary_site=https://npm.taobao.org/mirrors/node-sass
# 使用淘宝镜像源进行依赖安装，解决国内下载缓慢的问题(出现警告可以忽略)
npm install --registry=https://registry.npm.taobao.org
# 启动项目
npm run dev
#打包项目（在部署的时候才需要使用）
npm run build
```
强烈建议不要用直接使用 cnpm 安装，会有各种诡异的 bug，可以通过重新指定 registry 来解决 npm 安装速度慢的问题。若还是不行，可使用 [yarn](https://github.com/yarnpkg/yarn) 替代 `npm`。
Windows 用户若安装不成功，很大概率是`node-sass`安装失败，[解决方案](https://github.com/PanJiaChen/vue-element-admin/issues/24)。
另外因为 `node-sass` 是依赖 `python`环境的，如果你之前没有安装和配置过的话，需要自行查看一下相关安装教程。
在启动项目成功后，会跳转到：localhost:9528 ，我们输入账号密码： admin, mogu2018 访问即可
![image-20200209121800363](images/image-20200209121800363.png)
2) 安装 vue_mogu_web 项目的依赖,
这个步骤其实和admin端的安装时一致的，这里就不做过多的叙述
```bash
# 指定node-sass的国内镜像源
npm i node-sass --sass_binary_site=https://npm.taobao.org/mirrors/node-sass
# 使用淘宝镜像源进行依赖安装，解决国内下载缓慢的问题(出现警告可以忽略)
npm install --registry=https://registry.npm.taobao.org
# 启动项目
npm run dev
#打包项目（在部署的时候才需要使用）
npm run build
```
 下面是启动成功的界面，跳转到： localhost:9527
![image-20200209121819581](images/image-20200209121819581.png)
tip：特别注意！！！！！首次部署完成，如果图片无法显示，那是因为本地没有对应的图片，需要做的事是查看nginx是否启动，然后就是在后台添加图片进行上传
![image-20200908085423131](images/image-20200908085423131.png)
然后进行图片上传
![image-20200908085438033](images/image-20200908085438033.png)
上传完毕后，再到博客管理页面，修改博客标题图，然后保存即可
![image-20200908085522052](images/image-20200908085522052.png)
## 写在后面的话
关于我本机的配置，是使用的8G内存，项目所需的全部软件开启后，占用率大概到达了95%，所以微服务还是挺吃内存的。
关于服务器的配置，使用的是[1核2G的学生价格服务器](https://promotion.aliyun.com/ntms/act/campus2018.html?spm=5176.10695662.1244717.1.641e5a06KpmU4A&accounttraceid=3ac1b990a4f445859080d2555566af8fiirr?userCode=w7aungxw&tag=share_component&share_source=copy_link?userCode=w7aungxw&tag=share_component&share_source=copy_link?userCode=w7aungxw&tag=share_component&share_source=copy_link&userCode=w7aungxw&tag=share_component&share_source=copy_link&share_source=copy_link)，目前来说，在增加虚拟内存后，能够正常的运行项目，内存不够的小伙伴，可以参考这篇博客。[CentOS如何增加虚拟内存？](http://www.moguit.cn/#/info?blogUid=36ee5efa56314807a9b6f1c1db508871)
好了，关于博客的配置就到这里了，如果有问题的话，欢迎提出~
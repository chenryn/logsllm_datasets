> 学习笔记Gitee地址：https://gitee.com/moxi159753/LearningNotes
## 关于博客
蘑菇博客( **MoguBlog** )，一个基于微服务架构的前后端分离博客系统。**Web**端使用 **Vue** + **Element** , 移动端使用**Uniapp** 和 **ColorUI** 。后端使用 **Spring Cloud** + **Spring boot** + **Mybatis-plus** 进行开发，使用 **Jwt** + **Spring Security** 做登录验证和权限校验，使用 **ElasticSearch** 和 **Solr** 作为全文检索服务，使用 **Github Actions** 完成博客的持续集成，使用ELK收集博客日志，文件支持上传 **七牛云** 和 **Minio**。
欢迎大家能 **Star** 支持一下下哦，同时也可以参与到蘑菇博客的开源贡献中，如果想要体验完整的内容，欢迎关注Gitee中的演示环境，直接登录进行体验~
> 蘑菇博客Gitee地址：https://gitee.com/moxi159753/mogu_blog_v2
>
> 蘑菇博客Github地址：https://github.com/moxi624/mogu_blog_v2
### 摘要
蘑菇博客( **MoguBlog** )，一个基于微服务架构的前后端分离博客系统。**Web**端使用 **Vue** + **Element** , 移动端使用**Uniapp** 和 **ColorUI** 。后端使用 **Spring Cloud** + **Spring boot** + **Mybatis-plus** 进行开发，使用 **Jwt** + **Spring Security** 做登录验证和权限校验，使用 **ElasticSearch** 和 **Solr** 作为全文检索服务，使用 **Github Actions** 完成博客的持续集成，使用ELK收集博客日志，文件支持上传 **七牛云** 和 **Minio**
### 项目起源
蘑菇博客大部分功能是我个人进行开发的，因能力有限，其中很多技术都是一边学习一边使用的，可以说蘑菇博客也是一个我用来熟悉技术的项目，所以很多地方可能考虑不周，故有能改正的地方，还请各位老哥能够指出~
现在挺多是 **SSM** 或者 **SSH** 的博客管理系统，想用 **Spring boot** + **Spring Cloud** + **Vue** 的微服务架构进行尝试项目的构建，里面很多功能可能只是为了满足自己的学习需求而引入的，大家可以根据自己服务器配置来选择启动的服务，因此本博客也是一个非常好的 **SpringBoot** 、**SpringCloud** 以及 **Vue** 技术的入门学习项目。
原来做过 **Vue** + **Element-Ui** 做过管理系统，所以现在打算做一套自己的、基于当前最新技术栈、前后端分离的微服务博客系统。
### 项目特点
- 友好的代码结构及注释，便于阅读及二次开发
- 实现前后端分离，通过 **Json** 进行数据交互，前端再也不用关注后端技术
- 页面交互使用 **Vue2.x**，极大的提高了开发效率。
- 引入**Swagger** 文档支持，方便编写API接口文档。
- 引入 **RabbitMQ** 消息队列，用于邮件发送、更新 **Redis** 、**Solr** 和 **ElasticSearch**
- 引入 **JustAuth** 第三方登录开源库，支持 **Gitee**、**Github** 账号登录。
- 引入**ElasticSearch** 和 **Solr** 作为全文检索服务，并支持可插拔配置
- 引入**Github Actions** 工作流，完成蘑菇博客的持续集成、持续部署。
- 引入 **七牛云** 和 **Minio** 对象存储，同时支持本地文件存储
- 引入**RBAC** 权限管理设计，灵活的权限控制，按钮级别的细粒度权限控制，满足绝大部分的权限需求
- 引入 **Zipkin** 链路追踪，聚合各业务系统调用延迟数据，可以一眼看出延迟高的服务
- 采用自定义参数校验注解，轻松实现后端参数校验
- 采用 **AOP** + **自定义注解** + **Redis** 实现限制IP接口访问次数
- 采用自研的评论模块，实现评论邮件通知
- 采用 **Nacos** 作为服务发现和配置中心，轻松完成项目的配置的维护
- 采用 **Sentinel** 流量控制框架，通过配置轻松实现网站限流
- 采用 **uniapp** 和 **ColorUi** 完成蘑菇博客的移动端门户页面搭建
- 支持多种文本编辑器，**Markdown** 编辑器([Vditor](https://github.com/Vanessa219/vditor))和富文本编辑器([CKEditor](https://github.com/ckeditor/ckeditor4))随心切换
- 采用 **ElasticStack**【ElasticSearch+Beats+Kibana+Logstash】搭建蘑菇博客日志收集
- 采用 **Docker Compose** 完成容器编排，**Portainer** 实现容器可视化，支持一键部署线上环境
### 后端技术
|      技术      |           说明            |
| :------------: | :-----------------------: |
|   SpringBoot   |           MVC框           |
|  SpringCloud   |        微服务框架         |
| SpringSecurity |      认证和授权框架       |
|  MyBatis-Plus  |          ORM框架          |
|   Swagger-UI   |       文档生产工具        |
|     Kibana     |     分析和可视化平台      |
| Elasticsearch  |         搜索引擎          |
|     Beats      |     轻量型数据采集器      |
|    Logstash    | 用于接收Beats的数据并处理 |
|      Solr      |         搜索引擎          |
|    RabbitMQ    |         消息队列          |
|     Redis      |        分布式缓存         |
|     Docker     |        容器化部署         |
|     Druid      |       数据库连接池        |
|     七牛云     |     七牛云 - 对象储存     |
|      JWT       |        JWT登录支持        |
|     SLF4J      |         日志框架          |
|     Lombok     |     简化对象封装工具      |
|     Nginx      |  HTTP和反向代理web服务器  |
|    JustAuth    |     第三方登录的工具      |
|     Hutool     |      Java工具包类库       |
|    阿里大于    |       短信发送平台        |
| Github Actions |        自动化部署         |
|     Zipkin     |         链路追踪          |
| Flexmark-java  |     Markdown转换Html      |
|   Ip2region    |     离线IP地址定位库      |
|     Minio      |     本地对象存储服务      |
| Docker Compose |      Docker容器编排       |
|   Portainer    |     Docker可视化管理      |
### 前端技术
|         技术          |                  说明                   |
| :-------------------: | :-------------------------------------: |
|        Vue.js         |                前端框架                 |
|      Vue-router       |                路由框架                 |
|         Vuex          |            全局状态管理框架             |
|        Nuxt.js        |        创建服务端渲染 (SSR) 应用        |
|        Element        |               前端ui框架                |
|         Axios         |              前端HTTP框架               |
|        Echarts        |                图表框架                 |
|       CKEditor        |              富文本编辑器               |
|     Highlight.js      |            代码语法高亮插件             |
|        Vditor         |             Markdown编辑器              |
|      vue-cropper      |              图片裁剪组件               |
| vue-image-crop-upload |           vue图片剪裁上传组件           |
|   vue-emoji-comment   |          Vue Emoji表情评论组件          |
|     clipboard.js      |            现代化的拷贝文字             |
|      js-beautify      |           美化JavaScript代码            |
|     FileSaver.js      |            保存文件在客户端             |
|      SortableJS       |       功能强大的JavaScript 拖拽库       |
|   vue-side-catalog    |               目录导航栏                |
|        uniapp         |            移动端跨平台语言             |
|        colorUi        |         专注视觉的小程序组件库          |
|       showdown        | 用Javascript编写的Markdown 到Html转换器 |
|       turndown        | 用JavaScript编写的HTML到Markdown转换器  |
### 项目架构图
![项目架构图](./images/server.jpg)
### 部分截图
此处只是列举了部分截图，如果想要体验完整的内容，欢迎关注Gitee中的演示环境，直接登录进行体验~
![门户页面](./images/index.png)
![关于我](./images/image-20201218202417475.png)
![归档页面](./images/image-20201218202438433.png)
![后台仪表盘](./images/image-20201218202536293.png)
![博客管理](./images/image-20201218202618987.png)
![编辑文章](./images/image-20201218202641551.png)
### 关于开源
从开源的过程中，不仅自己的能力能得到提升，同时也能认识非常多志同相合的小伙伴，包括在群里的小伙伴们，也有一些一块参与到项目的维护和开发中，也有一些给我们提供 **issue** 和 **idea** ，同时能够和一些参加多年工作经验的老哥交流，也是受益匪浅的。
通过开源，我也获得了很多工作机会。就本次秋招来讲，其实很多面试官对我做的开源项目比较感兴趣，所以面试上其实很多时间都在聊这个开源项目。同时，我也收到过猎头通过 **Github** 上的邮箱给我发的邮件，期望我去参加他们推荐的工作 ( 哈哈哈，后面因为知道我还没有毕业的事情，就放弃了，因为他们招的是5年工作经验的。就因为这个原因错过了**阿里P6-P7**的岗位了，简直太亏了啊)
![图片](images/640-1609070992911.png)
## 举目远望
研究生的生涯，基本上在看论文、做实验、写博客中度过...，**2020** 年因为疫情的原因，整个寒假都是在家里度过的，直到 **2020** 年 **5** 月份才开学。在2月份的时候，我就听到有的小伙伴在准备寻找实习了，后面我想了想，正式的秋招大约是在8月份左右，有些公司如果有提前批的话，可能从6月底就开始了(今年字节跳动6月底就开始提前批)。所以从2月到7月，有5个月的时间进行学习，在加上疫情原因，无法正常返校，所以就刚刚好可以开始为面试而学习的阶段。
首先明确自己需要找哪方面的工作，因为我平时都是学习 **Java** 相关的，所以以后打算找后端开发，因此我的投递的岗位基本上都是顶着后台岗位的要求来的，加上我之前编程技术也算可以，所以就没有从头开始学习 **Java**，而是主要关注于java进阶方面的内容。
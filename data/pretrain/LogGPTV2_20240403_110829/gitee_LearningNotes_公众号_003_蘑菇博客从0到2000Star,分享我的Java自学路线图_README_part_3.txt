**ElasticStack** = **ElasticSearch** + **Logstash** + **Kibana** + **Beats**
![ElasticStack技术栈](https://gitee.com/moxi159753/LearningNotes/raw/master/ElasticStack/1_ElasticSearch%E4%BB%8B%E7%BB%8D%E4%B8%8E%E5%AE%89%E8%A3%85/images/image-20200922092403279.png)
在本章节，我们将学习到 **ElasticStack** 技术栈，主要包括如下内容：
**Elasticsearch** 基于 **Java**，是个开源分布式搜索引擎，它的特点有：分布式，零配置，自动发现，索引自动分片，索引副本机制，**Restful** 风格接口，多数据源，自动搜索负载等。
**Logstash** 基于 **Java**，是一个开源的用于收集,分析和存储日志的工具。
**Kibana** 基于**nodejs**，也是一个开源和免费的工具，**Kibana** 可以为 **Logstash** 和 **ElasticSearch** 提供的日志分析友好的 **Web** 界面，可以汇总、分析和搜索重要数据日志。
**Beats** 是 **Elastic** 公司开源的一款采集系统监控数据的代理 **agent**，是在被监控服务器上以客户端形式运行的数据收集器的统称，可以直接把数据发送给 **Elasticsearch** 或者通过 **Logstash** 发送给 **Elasticsearch**，然后进行后续的数据分析活动。
如果细心观察的小伙伴，可以看到蘑菇博客的架构图中，日志收集模块，其实就是使用 **ElasticStack** 实现的，同时全文检索也使用到了 **ElasticSearch**
![蘑菇博客日志收集模块](images/image-20201222204511571.png)
> Bilibili 黑马程序员 Elastic Stack（ELK）从入门到实践：
>
> https://www.bilibili.com/video/BV1iJ411c7Az
## SpringCloud
**微服务** 是一种用于构建应用程序的架构方案。微服务架构与传统架构的区别在于，微服务可以将应用拆分成多个核心功能。每个功能都被称为一项服务，可以单独部署，这也意味着各项微服务在工作(出现故障时，不会相互影响)，关于微服务的更多理解，可以参考 **martinfowler** 的论文
> https://martinfowler.com/articles/microservices.html
![martinfowler关于微服务的论文](images/sketch.png)
蘑菇博客最开始的架构是基于 **SpringCloud** 进行搭建，但是后面随着 **SpringCloud** 各种组件停止更新，进入维护阶段，后续技术组件的升级和替换策略方案选型，最终将 **SpringCloud** 升级为 现在的 **SpringCloud Alibaba** 架构。
在本章节中，学习 **SpringCloud** 各个组件，例如：Eureka、Feign、Hystrix、Ribbo、Config、Zuul、Zipkin 等。同时顺应时代变化，加入了 **SpringCloud Alibaba** 相关组件的，例如：Nacos、Sentinel、Seata 等技术。同时对微服务中的服务降级、服务熔断、服务限流、hotkey控制、分布式统一配置管理、分布式全局事务控制、RabbitMQ与Stream整合、Nacos和Nginx配置高可用集群等技术进行学习。
> Bilibili尚硅谷2020最新版SpringCloud教程：
>
> https://www.bilibili.com/video/BV18E411x7eT
## 实战演练
在我们把上面这些技术都学习完成后，我们就可以开始进行项目的训练了，这里我推荐尚硅谷的**谷粒商城项目**。
谷粒商城是一个完整大型分布式架构电商平台，技术涵盖：微服务架构、分布式、全栈、集群、部署、自动化运维、可视化CICD。
项目由业务集群系统+后台管理系统构成，打通了分布式开发及全栈开发技能，包含前后分离全栈开发、Restful接口、数据校验、网关、注册发现、配置中心、熔断、限流、降级、链路追踪、性能监控、压力测试、系统预警、集群部署、持续集成、持续部署等等。
同时视频教程也分为了三部分：分布式基础（全栈开发篇）、分布式高级（微服务架构篇）、高可用集群（架构师提升篇。小伙伴们可以由浅入深，逐步了解到一个大型的分布式项目是如何进行开发的，再本视频教程中，我们将会将前面学习到的所有知识点都进行实践，保证小伙伴们做到学以致用。
> Bilibili尚硅谷全网最强电商教程《谷粒商城》：
>
> https://www.bilibili.com/video/BV1np4y1C7Yf
## 结语
俗话说，**师傅领进门，修行看个人**。在看完上面这些老师的视频后，我们对 **Java** 的学习将会上升到新的高度，但是编码技术的功底也并非一下就能突飞猛进，还需要我们**多多练习**。在编码中遇到问题，并且解决问题，不断的提升自己问题解决能力。其实我在群里经常会遇到一些小伙伴的提问，有些问题可能只需要**百度一下就能马上解决**。因此在未来的自学过程中，我们肯定也会遇到各种各种的问题，我们遇到问题的时候，**首先自己先尝试着解决，同时做好笔记的习惯，防止自己再次掉坑**。
以上就是我的 **Java** 学习路线图，学完这些基本上找一份工作是没有问题的了，但是如果想要找一份比较好的工作的话，可能还需要**在面试这块好好下功夫**了，后面我将会写一份 **Java** 面试相关的学习指南，专门针对于**面试的自学之路**，那我们下期再见咯 ~ 
**陌溪**是一个从三本院校一路摸滚翻爬上来的互联网大厂程序员。独立做过几个开源项目，其中**蘑菇博客**在码云上有 **2K Star** 了。目前就职于**字节跳动的Data广告部门**，是字节跳动全线产品的商业变现研发团队。同时本公众号将会持续性的输出很多原创小知识以及学习资源。欢迎各位小伙伴关注陌溪，让我们一起成长~
![和陌溪一起学编程](images/1608514024370.jpg)
## 参考
**Bilibili 宋红康老师 尚硅谷IDEA教程**：
https://www.bilibili.com/video/BV1PW411X75p
**Bilibili 毕向东老师Java基础**：
https://www.bilibili.com/video/BV1Rt411f7F5
**Bilibili 宋红康老师 尚硅谷 Java零基础教程**：
https://www.bilibili.com/video/BV1Kb411W75N
**Bilibili尚硅谷 MySQL入门**：
https://www.bilibili.com/video/BV12b411K7Zu
**Bilibili尚硅谷JDBC核心技术**：
https://www.bilibili.com/video/BV1eJ411c7rf
**Bilibili 尚硅谷 王振国老师 JavaWeb全套教程**：
https://www.bilibili.com/video/BV1Y7411K7zz
**Bilibili尚硅谷Maven视频教程**：
https://www.bilibili.com/video/BV1TW411g7hP
**Bilibili尚硅谷Spring5框架**：
https://www.bilibili.com/video/BV1Vf4y127N5
**Bilibili 尚硅谷 SpringMVC**：
https://www.bilibili.com/video/BV1PE411W7BW
**Bilibili尚硅谷MyBatis实战教程**：
https://www.bilibili.com/video/BV1mW411M737
**Mybatis-Plus开源地址**：
https://gitee.com/baomidou/mybatis-plus
**Bilibili尚硅谷Mybatis-Plus教程**：
https://www.bilibili.com/video/BV1Ds411E76Y
**Bilibili狂神说 Git最新教程通俗易懂**：
https://www.bilibili.com/video/BV1FE411P7B3
**Bilibili尚硅谷雷丰阳老师2021最新版SpringBoot2全套完整版**：
https://www.bilibili.com/video/BV19K4y1L7MT
**Bilibili秦疆老师Linux最通俗易懂的教程阿里云真实环境学习**：
https://www.bilibili.com/video/BV1Sv411r7vd
**Bilibili狂神说 Docker最新超详细版教程**：
https://www.bilibili.com/video/BV1og4y1q7M4
**Bilibili 秦疆老师 Docker进阶篇超详细版教程通俗易懂**：
https://www.bilibili.com/video/BV1kv411q7Qc
**Bilibili狂神说 Redis最新超详细版教程**：
https://www.bilibili.com/video/BV1S54y1R7SB
**Bilibili最适合小白入门的RabbitMQ教程**：
https://www.bilibili.com/video/BV14A411q7pF
**Bilibili 黑马程序员 Elastic Stack（ELK）从入门到实践**：
https://www.bilibili.com/video/BV1iJ411c7Az
**martinfowler关于微服务的论文**：
https://martinfowler.com/articles/microservices.html
**Bilibili尚硅谷2020最新版SpringCloud教程**:
https://www.bilibili.com/video/BV18E411x7eT
**Bilibili尚硅谷全网最强电商教程《谷粒商城》**：
https://www.bilibili.com/video/BV1np4y1C7Yf
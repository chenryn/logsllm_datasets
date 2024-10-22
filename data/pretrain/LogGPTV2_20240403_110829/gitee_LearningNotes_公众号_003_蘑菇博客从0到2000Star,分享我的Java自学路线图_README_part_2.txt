> https://www.bilibili.com/video/BV1PE411W7BW
### Mybatis
**MyBatis** 是一款优秀的持久层框架，它支持自定义 **SQL**、存储过程以及高级映射。**MyBatis** 免除了几乎所有的 **JDBC** 代码以及设置参数和获取结果集的工作。**MyBatis** 可以通过简单的 XML 或注解来配置和映射原始类型、接口和 **Java POJO**（Plain Old Java Objects，普通老式 Java 对象）为数据库中的记录。
![Mybatis-图片来源网络](images/mybatis-superbird-small.png)
在这节，我们将学习如何编写 **Mybatis** 配置文件、配置动态 **SQL**、**缓存机制**、整合 **SSM** 以及 **Mybatis逆向工程**
想当初陌溪在开发**蘑菇博客**第一版本的时候，就是使用的**SSM**框架。那会在整合SSM框架的时候，足足花费了 **2** 周的时间，那会视频教程没有这么多，我在遇到问题只能通过**百度**和 **Google**来检索，还好最后终于成功了~
同时通过学习 **Mybatis逆向工程**，可以自动生成基础的代码，让我们更加专注于业务的开发。
> Bilibili尚硅谷MyBatis实战教程：
>
> https://www.bilibili.com/video/BV1mW411M737
### MybatisPlus
MyBatisPlus是一款非常强大的MyBatis增强工具包，**只做增强不做改变**。
![MybatisPlus-图片来源网络](images/image-20201222112155139.png)
陌溪最早接触 **Mybatis-Plus** 的时候，是在逛**码云**的时候看到的，那会它已经是年度最受欢迎的开源项目了，然后我为了学习 **Mybatis-Plus** 的使用，在蘑菇博客技术选型的时候，就把 **Mybatis-Plus** 作为了蘑菇博客的ORM框架。
> Mybatis-Plus开源地址：
>
> https://gitee.com/baomidou/mybatis-plus
**Mybatis-Plus** 在不用编写任何 **SQL语句** 的情况下即可以方便的实现单一、批量、分页等操作。
在这节，我们将学习，如何集成 **MyBatisPlus**、通用 **CRUD**、**EntityWrapper** 条件构造器、**ActiveRecord** 等基本操作，更有**代码生成器**、**插件扩展**、**自定义全局操作**、**公共字段填充**、**Idea** 快速开发插件等高阶技术.。
同时会涉及到 **MyBatis** 框架相关的原理，需要我们提前对 **Mybatis** 有一定的了解。
> Bilibili尚硅谷Mybatis-Plus教程：
>
> https://www.bilibili.com/video/BV1Ds411E76Y
## Git
我们把上面的内容学习完之后，其实就已经可以开始上手写项目了。
但是以后工作肯定不会是一个人**单打独斗**，而是需要和大家一块**协同开发**，但是协同开发不可避免的就会遇到**代码冲突**，就是两个人同时修改某一块区域，最终以谁的代码为准？
![Git-来源网络](images/image-20201223091907489.png)
这个时候 **Git** 就出现了，**Git** 一个最重要的功能就是 **版本控制**，让我们在开发过程中管理我们对文件、目录或工程等内容的修改历史。方便我们查看更改历史记录和备份，以便恢复以前的版本。
本节主要讲解：Git安装过程，本地库基本操作、远程基本操作、码云的注册和使用、IDEA中集成Git操作以及GIt分支管理
> Bilibili狂神说 Git最新教程通俗易懂：
>
> https://www.bilibili.com/video/BV1FE411P7B3
## SpringBoot
其实谈到 **SpringBoot** 的时候，我们不得不说它和 **SpringMVC** 的关系。**SpringMVC** 相当于一辆自动挡的汽车，而 **SpringBoot** 相当于把手动挡变成了自动挡，同时加入了无人驾驶等功能，让你开车更加省心。但是车的主体功能还是不变的，你还是需要使用到 **SpringMVC**。
**SpringBoot** 因为遵循**约定大于配置**，大量减少了配置文件的使用，让开发人员不需要定义样板化的配置。从而使得开发变得更加简便，提高了我们的编码效率。
![SpringBoot-来源网络](images/image-20201222165200251.png)
**SpringBoot** 本身并不提供 **Spring** 框架的核心特性以及扩展功能，只是用于快速、敏捷地开发新一代基于 **Spring**框架的应用程序。同时 **SpringBoot** 并不能替代 **SpringMVC**，它只是简化了 **SpringMVC** 相关配置。
虽然说，小伙伴们直接上手 **SpringBoot** 也未尝不可，但是如果在不了解 **SpringMVC** 原理的情况下就使用其进行开发，这叫知其然不知所以然，不是正确的学习方式。
在本节，将介绍 SpringBoot的使用和内部原理，其中包括 微服务概念、配置文件、日志框架的使用、Web开发、Thymeleaf模板引擎、Docker容器技术教程等。
> Bilibili尚硅谷雷丰阳老师2021最新版SpringBoot2全套完整版：
>
> https://www.bilibili.com/video/BV19K4y1L7MT
## Linux
在我们学习完 **SpringBoot** 后，其实就可以打包成 **Jar** 包然后部署到Linux服务器上了，虽然说在服务器上部署可能就是一条指令：**java -jar** 。但是以后我们难免需要在上面进行调试和错误定位。因此，为了以后能够了解运维相关的内容，所以我们也有必要去系统学习一波 **Linux** 的使用。
![Linux-来源网络](images/image-20201223092003694.png)
本章节，主要从Linux历史、基本命令、项目实战发布上线、等方面来讲解，告诉我们一个项目是如何打包并且部署在阿里云服务器中的。
> Bilibili秦疆老师Linux最通俗易懂的教程阿里云真实环境学习：
>
> https://www.bilibili.com/video/BV1Sv411r7vd
## Docker
**Docker** 是一个开源的应用容器引擎，可以让开发者打包他们的应用以及依赖包到一个轻量级、可移植的容器中，然后发布到任何流行的 **Linux** 机器上。同时容器是完全使用沙箱机制，相互之间不会有任何接口(类似于 iphone的 app )，更重要的是容器的性能开销非常低。
![Docker-来源网络](images/image-20201223092035311.png)
蘑菇博客也是使用了Docker进行部署的，最开始的时候，是通过拉取一个 **CentOS** 的镜像，然后制作成容器，最后在上面安装博客所需的环境：Nginx、Redis、Rabbitmq、MySQL 等。最后将容器再次打包成镜像，发布到 **DockerHub** 上，其它小伙伴只需要拉取该镜像，即可快速完成环境的搭建。
本章节中，将从 Docker概念、镜像、容器、部署、Portainer可视化、容器数据卷、DockerFile、Docker网络 等方面镜像讲解。
> Bilibili狂神说 Docker最新超详细版教程：
>
> https://www.bilibili.com/video/BV1og4y1q7M4
## Docker Compose
**Docker Compose** 属于 **Docker** 的高阶部分。在我们之前使用 **Docker** 的时候，需要定义 **DockerFile** 文件，然后使用 docker build 、 docker run 等命令操作容器。然而微服务架构的应用系统一般包含若干个微服务，每个微服务一般都会部署多个实例，如果每个微服务都要手动开启和关闭，那么效率是非常低的，耗费运维的成本。
![Docker Compose-来源网络](images/image-20201223092104895.png)
这个时候 **Docker Compose** 就运营而生，它可以非常轻松、高效的管理容器，同时它也是一个用于定义和运行多个容器的 **Docker** 管理工具。
在本章节中，主要讲解 Docker Compose概念、Compose配置编写规则、使用Docker Compose一键部署 WordPress博客、编写微服务实战、Swarm集群搭建、Raft一致性协议。
>Bilibili 秦疆老师 Docker进阶篇超详细版教程通俗易懂：
>
>https://www.bilibili.com/video/BV1kv411q7Qc
## Redis
我们都知道大量查询 **MySQL** 是比较耗时的，目前蘑菇博客其实有很多场景都使用到了 **Redis** 作为缓存数据库。例如：首页内容的显示，热门的文章，数据字典，用户的令牌信息 等等，都是存储在 **Redis** 中的，就目前企业级开发来说， **Redis** 也是使用的非常多，一些需要通过计算得到的数据，并且未来将会再次使用，都可以将其存储在 **Redis** 中，来加快接口访问的效率。
![Redis图片-来源网络](images/image-20201222170345727.png)
在本章节，将从 **NoSQL**谈起，深入讲解 **Redis** 的基本数据类型、扩展特殊类型、**Java** 操作 **Redis**、SpringBoot集成 Redis、Redis的事务、配置文件的详解。同时在原理层面，将讲解 Redis的发布订阅模型、持久化机制、主从复制、哨兵模式、缓存穿透 和 缓存雪崩的处理。
> Bilibili狂神说 Redis最新超详细版教程：
>
> https://www.bilibili.com/video/BV1S54y1R7SB
## RabbitMQ
MQ(Message Queue)，即消息队列。谈到队列我们都知道，就是一个 **先进先出**的数据结构。而消息队列，就是将消息存储在队列里，先存入的队列就将会提前被消费。**MQ** 引入到系统中，就是有三个目的：**异步**、**削峰**、**解耦**
目前主流的消息队列主要有：**Kafka**、**ActiveMQ**、**RabbitMQ**、**RocketMQ**，关于各自的特点，请看下图
![image-20201222171358114](images/image-20201222171358114.png)
**RabbitMQ** 只是目前消息队列中的一种，因为最开始我被**小兔子**(RabbitMQ) 的控制面板吸引，所以在搭建蘑菇博客的时候，选择了 **RabbitMQ**。当然，小伙伴们在学习的时候，也可以结合自己喜欢的 **MQ**。
![RabbitMQ图片-来源网络](images/image-20201222171915742.png)
蘑菇博客使用 **RabbitMQ** 的场景，主要是在 更新 **Solr** 和 **ElasticSearch** 索引(**用于全文检索**)，以及发送邮件和短信。因为这些过程都是可以异步执行的，所以就使用了 **RabbitMQ** 的异步特性。
在本节，主要讲解：MQ的概念、主流的MQ、RabbitMQ的安装及配置、RabbitMQ的工作模式、队列和交换机、SpringBoot项目整合RabbitMQ。
> Bilibili最适合小白入门的RabbitMQ教程：
>
> https://www.bilibili.com/video/BV14A411q7pF
## ElasticStack
如果你没有听说过 **Elastic Stack**，那你一定听说过 **ELK** ，实际上 **ELK** 是三款软件的简称
**ELK** = **ElasticSearch** + **Logstash** + **Kibana**
随着 **Beats** 的加入，原来的 **ELK** 体系变成了 **ElasticStack** ，即
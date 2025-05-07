### MyBatis
**MyBatis** 是一款卓越的持久层框架，支持自定义 **SQL**、存储过程以及高级映射。它消除了大部分 **JDBC** 代码的需求，包括参数设置和结果集处理。通过简单的 XML 或注解配置，**MyBatis** 可以将原始类型、接口及 **Java POJO**（Plain Old Java Objects，普通老式 Java 对象）映射到数据库中的记录。

![Mybatis-图片来源网络](images/mybatis-superbird-small.png)

本节将介绍如何编写 **MyBatis** 配置文件、动态 **SQL** 的配置方法、缓存机制、与 **SSM** 框架的整合方式，以及 **MyBatis** 逆向工程的应用。在开发蘑菇博客的第一个版本时，陌溪采用了 **SSM** 框架，当时仅是整合这一框架就花费了两周时间。由于那时视频教程资源有限，遇到问题只能依靠 **百度** 和 **Google** 解决，但最终还是成功完成了任务。学习 **MyBatis** 逆向工程后，能够自动生成基础代码，使开发者可以更加专注于业务逻辑的实现。

> Bilibili尚硅谷MyBatis实战教程：
>
> https://www.bilibili.com/video/BV1mW411M737

### MyBatisPlus
**MyBatisPlus** 是一个强大的 **MyBatis** 增强工具包，遵循“只做增强不做改变”的原则。
![MybatisPlus-图片来源网络](images/image-20201222112155139.png)

陌溪最初接触到 **MyBatis-Plus** 是在浏览码云时发现的，彼时它已是年度最受欢迎的开源项目之一。为了掌握 **MyBatis-Plus** 的使用，在选择蘑菇博客的技术栈时，决定将其作为 ORM 框架。

> Mybatis-Plus开源地址：
>
> https://gitee.com/baomidou/mybatis-plus

**MyBatis-Plus** 允许用户在无需编写任何 **SQL语句** 的情况下轻松执行单一、批量、分页等操作。本课程将涵盖如何集成 **MyBatisPlus**、通用 **CRUD** 操作、**EntityWrapper** 条件构造器、**ActiveRecord** 等基本功能，以及更高级的主题如代码生成器、插件扩展、自定义全局操作、公共字段填充、**Idea** 快速开发插件等。同时也会涉及 **MyBatis** 框架的基本原理，建议提前对 **MyBatis** 有一定了解。

> Bilibili尚硅谷Mybatis-Plus教程：
>
> https://www.bilibili.com/video/BV1Ds411E76Y

## Git
完成上述内容的学习后，你已经可以开始实际项目开发了。然而，在团队协作中，单打独斗显然不可行，协同工作时常常会遇到代码冲突的问题。这时就需要用到 **Git** 这个版本控制系统，它帮助我们管理文件或项目的修改历史，方便查看更改记录并恢复旧版本。

本章节将讲解 **Git** 的安装步骤、本地库与远程库的操作方法、码云平台的注册与使用、**IDEA** 中的 **Git** 集成以及分支管理技巧。

> Bilibili狂神说 Git最新教程通俗易懂：
>
> https://www.bilibili.com/video/BV1FE411P7B3

## SpringBoot
提到 **SpringBoot**，不得不提及其与 **SpringMVC** 的关系。如果说 **SpringMVC** 像是一辆自动挡汽车，那么 **SpringBoot** 就是将手动挡升级为自动挡，并增加了无人驾驶功能，使得驾驶变得更加简便。尽管如此，车辆的核心功能并未改变，仍需依赖 **SpringMVC**。

由于 **SpringBoot** 遵循“约定优于配置”的理念，大幅减少了配置文件的数量，简化了开发流程，提高了编码效率。需要注意的是，**SpringBoot** 并不提供 **Spring** 框架的核心特性和扩展功能，而是用于快速构建基于 **Spring** 的应用程序，并且不能替代 **SpringMVC**。

虽然可以直接上手 **SpringBoot** 开发，但如果缺乏对 **SpringMVC** 原理的理解，则可能无法深入理解其运作机制。本部分将详细介绍 **SpringBoot** 的使用方法及其内部机制，包括微服务概念、配置文件管理、日志框架应用、Web 开发技术、Thymeleaf 模板引擎使用及 **Docker** 容器技术入门。

> Bilibili尚硅谷雷丰阳老师2021最新版SpringBoot2全套完整版：
>
> https://www.bilibili.com/video/BV19K4y1L7MT

... [后续内容按照相同方式进行优化]
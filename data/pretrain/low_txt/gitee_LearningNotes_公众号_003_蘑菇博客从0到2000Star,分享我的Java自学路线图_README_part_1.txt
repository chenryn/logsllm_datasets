## 前言
大家好，我是**陌溪**。近期，不少群友询问我关于**蘑菇博客**的入门指南。经过两年的技术迭代，蘑菇博客已涵盖了从**SpringBoot**到**SpringCloud**，从**Solr**到**ElasticStack**等众多知识点。内容繁杂，对于初学者而言可能有些难以掌握。因此，我决定整理一份学习路线指南，以帮助新手们更轻松地入门。

![蘑菇博客系统架构图](images/server.jpg)

在接下来的内容中，我将以**视频教程**为主要形式进行分享。在我看来，通过观看视频来学习是一种非常适合新手的方式，因为编程是一门实践性很强的学科，需要跟随老师的思路进行编码练习，从而提升自己的技能。建议大家在观看视频时做好笔记，并跟着老师一起编写代码。

本文主要针对**Java新手**，但如果你是经验丰富的开发者，也可以结合视频和书籍进行学习。现在，请各位新手朋友们坐稳扶好，我们即将启程！

## 工欲善其事，必先利其器

在开始编程之前，选择一款合适的 **IDE** 编辑器至关重要，这将使我们的编码工作更加高效。我个人尝试过多种编辑器，包括 **Eclipse** 、**MyEclipse**、**STS**、**VSCode** 和 **Intellij IDEA**。

- **Eclipse** 是一个开源免费的 Java 集成开发环境。
- **MyEclipse** 在 Eclipse 的基础上增加了额外插件。
- **STS** 则专为 **Spring** 开发设计。
- **VSCode** 是由微软开发的一款跨平台编辑器，支持多种主流编程语言。
- **Intellij IDEA** 被广泛认为是最好的 Java 开发工具之一，在智能代码助手、代码提示及版本控制等方面表现出色，且其用户界面设计美观。

我最初使用的是 **Eclipse** 系列编辑器，后来被推荐使用 **Intellij IDEA** ，并花费了几周时间适应其快捷键设置。目前，我已经完全转向了 **Jetbrains** 全家桶（对在校学生免费），并通过参与蘑菇博客项目获得了两份免费许可证。

对于初次接触 Java 的朋友，我强烈建议直接使用 **Intellij IDEA** 并花几个小时熟悉其基本功能，这将极大地提高你后续的编码效率。

> Bilibili 宋红康老师 尚硅谷IDEA教程：
>
> https://www.bilibili.com/video/BV1PW411X75p

## Java SE

**Java SE** 是 Java 技术的核心与基础。我第一次接触 Java SE 是在 2014 年 10 月，当时还在上大二。学校开设了 Java 课程，当我了解到可以通过代码创建图形界面时，我对这门语言产生了浓厚兴趣。

随后，我在网上发现了传智播客提供的视频教程，开启了我的 Java 学习之旅。

![Java图片-来源网络](images/image-20201222094534783.png)

首先推荐毕向东老师的 **Java基础视频教程**，该课程涵盖了 Java 环境搭建、进制转换、运算符、条件语句、数组、面向对象编程、多线程、集合类、IO流等内容。打好基础非常重要，我当时花了两三个月才学完这部分内容。

> Bilibili 毕向东老师Java基础：
>
>  https://www.bilibili.com/video/BV1Rt411f7F5

尽管毕老师的课程非常经典，但由于部分内容如 **Java GUI** 已经被淘汰，以及所用 JDK 版本较旧（基于 Java 1.6），我更推荐尚硅谷宋红康老师的 **Java零基础教程**。这套课程不仅去除了过时技术，还介绍了计算机和 Java 发展史，并讲解了从 JDK 8 到 JDK 11 的新特性。

>Bilibili 宋红康老师 尚硅谷 Java零基础教程：
>
>https://www.bilibili.com/video/BV1Kb411W75N

在 **Java SE** 学习阶段，重点应放在以下几个方面：
- 面向对象
- 集合类
- IO 流
- 反射
- 泛型
- 异常处理

## MySQL

完成 **Java EE** 课程后，可以开始学习 **MySQL** 数据库。这门课程通常会在本科期间的大二或大三开设。如果已经学过的话，可以直接跳过此部分。

![MySQL图片-来源网络](images/image-20201222094616465.png)

在这里，我们将学习数据库和表的操作、约束、视图、存储过程和函数、流程控制结构以及数据增删改查操作。

> Bilibili尚硅谷 MySQL入门：
>
> https://www.bilibili.com/video/BV12b411K7Zu

## JDBC

**JDBC (Java Data Base Connectivity)** 是一种用于简化和统一数据库操作的标准 API。其主要步骤包括：加载驱动、获取连接、执行操作、释放资源。

虽然现代 ORM 框架（如 Hibernate、MyBatis）隐藏了许多底层细节，但在进行性能调优时仍需了解 **JDBC** 。因此，快速入门者可略过此章节。

> Bilibili尚硅谷JDBC核心技术：
>
> https://www.bilibili.com/video/BV1eJ411c7rf

## Java Web

学习完 Java 基础及如何使用 Java 操作 MySQL 后，就进入了 **Java Web** 阶段。在此阶段，我们将学习前端技术（HTML、CSS、JavaScript、jQuery）和后端技术（Servlet、Filter、Listener、JSP、EL 表达式、JSTL 标签库、Cookie、Session、JSON、Ajax 请求等）。

最后，我们将运用所学知识完成一个书城项目，为将来学习框架打下坚实的基础。

> Bilibili 尚硅谷 王振国老师 JavaWeb全套教程：
>
> https://www.bilibili.com/video/BV1Y7411K7zz

### 关于 JSP 的讨论

尽管有观点认为 JSP 已被其他模板引擎（如 FreeMarker、Thymeleaf）取代，但仍有许多遗留项目依赖 JSP 进行维护。因此，建议至少了解其基本用法。

## Java EE

**Java EE (又称为 J2EE)** 主要用于企业级应用开发。在此阶段，我们将学习 SSM 框架（即 Spring、SpringMVC 和 MyBatis）。

- **Spring**：轻量级 Java 开发框架，旨在解决企业应用开发中的复杂问题。
- **SpringMVC**：分离控制器、模型对象与分派器，便于定制开发。
- **MyBatis**：Java 持久层框架，简化数据库操作。

> SSH 框架（Struts2、Spring、Hibernate）现较少使用，故不作推荐。

### Maven

**Maven** 是一种流行的自动化构建工具，适用于大型项目开发中的依赖管理。它通过中央仓库管理依赖关系，避免了手动查找 jar 包带来的不便。

本节将介绍 Maven 的作用、常用命令、配置依赖、生命周期等内容。

> Bilibili尚硅谷Maven视频教程：
>
> https://www.bilibili.com/video/BV1TW411g7hP

### Spring

**Spring 5** 是一个强大的 Java EE 框架，提供 IOC 容器、AOP 功能及 Web MVC 支持。学习重点包括 Spring 基础、IOC 容器、AOP、JdbcTemplate、事务管理等。

> Bilibili尚硅谷Spring5框架：
>
> https://www.bilibili.com/video/BV1Vf4y127N5

### SpringMVC

**SpringMVC** 采用松耦合可插拔组件结构，具有良好的扩展性和灵活性。我们将学习 RequestMapping、RequestParam 注解的使用，以及拦截器、过滤器、国际化、文件上传、异常处理等内容。此外，还将探讨 RESTful 风格 URL 请求的设计方法。

> Bilibili 尚硅谷 SpringMVC：
>
> [链接待补充]

希望以上内容能帮助大家更好地理解和掌握相关知识！
> 大家好，我是陌溪，欢迎点击下方的公众号名片，关注陌溪，让我们一起成长~
## ElasticStack技术栈
如果你没有听说过 **Elastic Stack**，那你一定听说过 **ELK** ，实际上 **ELK** 是三款软件的简称，分别是**Elasticsearch**、 **Logstash**、**Kibana** 组成，在发展的过程中，又有新成员 **Beats** 的加入，所以就形成了**Elastic Stack**。所以说，**ELK** 是旧的称呼，**Elastic Stack** 是新的名字。
![从ELK到ElasticStack](http://image.moguit.cn/717cfb28870243db81fe9456b5961a87)
全系的 **ElasticStack** 技术栈包括：
![ElasticStack技术栈](http://image.moguit.cn/a85c4a7fe9ce4c739f76509c78979397)
### Elasticsearch
Elasticsearch 基于 **Java**，是个开源分布式搜索引擎，它的特点有：分布式，零配置，自动发现，索引自动分片，索引副本机制，**restful** 风格接口，多数据源，自动搜索负载等。
### Logstash
**Logstash** 基于 **Java**，是一个开源的用于收集,分析和存储日志的工具。
### Kibana
**Kibana** 基于 **nodejs**，也是一个开源和免费的工具，**Kibana** 可以为 **Logstash** 和 **ElasticSearch** 提供的日志分析友好的 **Web** 界面，可以汇总、分析和搜索重要数据日志。
### Beats
**Beats** 是 **elastic** 公司开源的一款采集系统监控数据的代理 **agent**，是在被监控服务器上以客户端形式运行的数据收集器的统称，可以直接把数据发送给 **Elasticsearch** 或者通过 **Logstash** 发送给 **Elasticsearch**，然后进行后续的数据分析活动。**Beats**由如下组成:
*   Packetbeat：是一个网络数据包分析器，用于监控、收集网络流量信息，Packetbeat嗅探服务器之间的流量，解析应用层协议，并关联到消息的处理，其支 持ICMP (v4 and v6)、DNS、HTTP、Mysql、PostgreSQL、Redis、MongoDB、Memcache等协议；
*   Filebeat：用于监控、收集服务器日志文件，其已取代 logstash forwarder；
*   Metricbeat：可定期获取外部系统的监控指标信息，其可以监控、收集 Apache、HAProxy、MongoDB MySQL、Nginx、PostgreSQL、Redis、System、Zookeeper等服务；
> Beats和Logstash其实都可以进行数据的采集，但是目前主流的是使用Beats进行数据采集，然后使用 Logstash进行数据的分割处理等，早期没有Beats的时候，使用的就是Logstash进行数据的采集。
ElasticSearch快速入门
-----------------
### 简介
> 官网：https://www.elastic.co/
**ElasticSearch** 是一个基于 **Lucene** 的搜索服务器。它提供了一个分布式多用户能力的全文搜索引擎，基于**RESTful Web** 接口。**Elasticsearch** 是用 **Java** 开发的，并作为 **Apache** 许可条款下的开放源码发布，是当前流行的企业级搜索引擎。设计用于云计算中，能够达到实时搜索，稳定，可靠，快速，安装使用方便。
我们建立一个网站或应用程序，并要添加搜索功能，但是想要完成搜索工作的创建是非常困难的。我们希望搜索解决方案要运行速度快，我们希望能有一个零配置和一个完全免费的搜索模式，我们希望能够简单地使用JSON通过HTTP来索引数据，我们希望我们的搜索服务器始终可用，我们希望能够从一台开始并扩展到数百台，我们要实时搜索，我们要简单的多租户，我们希望建立一个云的解决方案。因此我们利用Elasticsearch来解决所有这些问题及可能出现的更多其它问题。
**ElasticSearch** 是 **Elastic Stack** 的核心，同时 **Elasticsearch** 是一个分布式、**RESTful** 风格的搜索和数据分析引擎，能够解决不断涌现出的各种用例。作为 **Elastic Stack** 的核心，它集中存储您的数据，帮助您发现意料之中以及意料之外的情况。
**Elasticsearch** 的发展是非常快速的，所以在 **ES5.0** 之前，**ELK** 的各个版本都不统一，出现了版本号混乱的状态，所以从 **5.0** 开始，所有 **Elastic Stack** 中的项目全部统一版本号。本篇将基于 **6.5.4** 版本进行学习。
### 下载
到官网下载：[https://www.elastic.co/cn/downloads/](https://www.elastic.co/cn/downloads/)
![下载](http://image.moguit.cn/248ee83cc3254c9f8510a18849280c76)
选择对应版本的数据，这里我使用的是 **Linux** 来进行安装，所以就先下载好 **ElasticSearch** 的 **Linux** 安装包
### 拉取Docker容器
因为我们需要部署在 **Linux** 下，为了以后迁移 **ElasticStack** 环境方便，我们就使用 **Docker** 来进行部署，首先我们拉取一个带有 **ssh** 的 **Centos** 镜像
    # 拉取镜像
    docker pull moxi/centos_ssh
    # 制作容器
    docker run --privileged -d -it -h ElasticStack --name ElasticStack -p 11122:22 -p 9200:9200 -p 5601:5601 -p 9300:9300 -v /etc/localtime:/etc/localtime:ro  moxi/centos_ssh /usr/sbin/init
然后直接远程连接 **11122** 端口即可
### 单机版安装
因为 **ElasticSearch** 不支持 **root** 用户直接操作，因此我们需要创建一个elsearch用户
    # 添加新用户
    useradd elsearch
    # 创建一个soft目录，存放下载的软件
    mkdir /soft
    # 进入，然后通过xftp工具，将刚刚下载的文件拖动到该目录下
    cd /soft
    # 解压缩
    tar -zxvf elasticsearch-7.9.1-linux-x86_64.tar.gz
    #重命名
    mv elasticsearch-7.9.1/ elsearch
因为刚刚我们是使用 **root** 用户操作的，所以我们还需要更改一下 **/soft** 文件夹的所属，改为 **elsearch** 用户
    chown elsearch:elsearch /soft/ -R
然后在切换成 **elsearch** 用户进行操作
    # 切换用户
    su - elsearch
然后我们就可以对我们的配置文件进行修改了
    # 进入到 elsearch下的config目录
    cd /soft/elsearch/config
然后找到下面的配置
    #打开配置文件
    vim elasticsearch.yml 
    #设置ip地址，任意网络均可访问
    network.host: 0.0.0.0 
在 **Elasticsearch** 中如果**network.host** 不是 **localhost** 或者**127.0.0.1** 的话，就会认为是生产环境，而生产环境的配置要求比较高，我们的测试环境不一定能够满足，一般情况下需要修改**两处配置**，如下：
    # 修改jvm启动参数
    vim conf/jvm.options
    #根据自己机器情况修改
    -Xms128m 
    -Xmx128m
然后在修改**第二处**的配置，这个配置要求我们到宿主机器上来进行配置
    # 到宿主机上打开文件
    vim /etc/sysctl.conf
    # 增加这样一条配置，一个进程在VMAs(虚拟内存区域)创建内存映射最大数量
    vm.max_map_count=655360
    # 让配置生效
    sysctl -p
### 启动ElasticSearch
首先我们需要切换到 **elsearch** 用户
    su - elsearch
然后在到 **bin**目录下，执行下面
    # 进入bin目录
    cd /soft/elsearch/bin
    # 后台启动
    ./elasticsearch -d
启动成功后，访问下面的 **URL**
    http://202.193.56.222:9200/
如果出现了下面的信息，就表示已经成功启动了
![ELastic启动成功](http://image.moguit.cn/e14d5c982436463d922099318ea1b7aa)
如果你在启动的时候，遇到过问题，那么请参考下面的错误分析~
错误分析
----
### 错误情况1
如果出现下面的错误信息
    java.lang.RuntimeException: can not run elasticsearch as root
    	at org.elasticsearch.bootstrap.Bootstrap.initializeNatives(Bootstrap.java:111)
    	at org.elasticsearch.bootstrap.Bootstrap.setup(Bootstrap.java:178)
    	at org.elasticsearch.bootstrap.Bootstrap.init(Bootstrap.java:393)
    	at org.elasticsearch.bootstrap.Elasticsearch.init(Elasticsearch.java:170)
    	at org.elasticsearch.bootstrap.Elasticsearch.execute(Elasticsearch.java:161)
    	at org.elasticsearch.cli.EnvironmentAwareCommand.execute(EnvironmentAwareCommand.java:86)
    	at org.elasticsearch.cli.Command.mainWithoutErrorHandling(Command.java:127)
    	at org.elasticsearch.cli.Command.main(Command.java:90)
    	at org.elasticsearch.bootstrap.Elasticsearch.main(Elasticsearch.java:126)
    	at org.elasticsearch.bootstrap.Elasticsearch.main(Elasticsearch.java:92)
    For complete error details, refer to the log at /soft/elsearch/logs/elasticsearch.log
    [root@e588039bc613 bin]# 2020-09-22 02:59:39,537121 UTC [536] ERROR CLogger.cc@310 Cannot log to named pipe /tmp/elasticsearch-5834501324803693929/controller_log_381 as it could not be opened for writing
    2020-09-22 02:59:39,537263 UTC [536] INFO  Main.cc@103 Parent process died - ML controller exiting
就说明你没有切换成 **elsearch** 用户，因为不能使用 **root** 用户去操作 **ElasticSearch**
    su - elsearch
### 错误情况2
    [1]:max file descriptors [4096] for elasticsearch process is too low, increase to at least[65536]
解决方法：切换到 **root** 用户，编辑 **limits.conf** 添加如下内容
    vi /etc/security/limits.conf
    # ElasticSearch添加如下内容:
    * soft nofile 65536
    * hard nofile 131072
    * soft nproc 2048
    * hard nproc 4096
### 错误情况3
    [2]: max number of threads [1024] for user [elsearch] is too low, increase to at least
    [4096]
也就是最大线程数设置的太低了，需要改成 **4096**
    #解决：切换到root用户，进入limits.d目录下修改配置文件。
    vi /etc/security/limits.d/90-nproc.conf
    #修改如下内容：
    * soft nproc 1024
    #修改为
    * soft nproc 4096
### 错误情况4
    [3]: system call filters failed to install; check the logs and fix your configuration
    or disable system call filters at your own risk
解决：**Centos6** 不支持 **SecComp**，而 **ES5.2.0** 默认 **bootstrap.system\_call\_filter** 为 **true**
    vim config/elasticsearch.yml
    # 添加
    bootstrap.system_call_filter: false
    bootstrap.memory_lock: false
### 错误情况5
    [elsearch@e588039bc613 bin]$ Exception in thread "main" org.elasticsearch.bootstrap.BootstrapException: java.nio.file.AccessDeniedException: /soft/elsearch/config/elasticsearch.keystore
    Likely root cause: java.nio.file.AccessDeniedException: /soft/elsearch/config/elasticsearch.keystore
    	at java.base/sun.nio.fs.UnixException.translateToIOException(UnixException.java:90)
    	at java.base/sun.nio.fs.UnixException.rethrowAsIOException(UnixException.java:111)
    	at java.base/sun.nio.fs.UnixException.rethrowAsIOException(UnixException.java:116)
    	at java.base/sun.nio.fs.UnixFileSystemProvider.newByteChannel(UnixFileSystemProvider.java:219)
    	at java.base/java.nio.file.Files.newByteChannel(Files.java:375)
    	at java.base/java.nio.file.Files.newByteChannel(Files.java:426)
    	at org.apache.lucene.store.SimpleFSDirectory.openInput(SimpleFSDirectory.java:79)
    	at org.elasticsearch.common.settings.KeyStoreWrapper.load(KeyStoreWrapper.java:220)
    	at org.elasticsearch.bootstrap.Bootstrap.loadSecureSettings(Bootstrap.java:240)
    	at org.elasticsearch.bootstrap.Bootstrap.init(Bootstrap.java:349)
    	at org.elasticsearch.bootstrap.Elasticsearch.init(Elasticsearch.java:170)
    	at org.elasticsearch.bootstrap.Elasticsearch.execute(Elasticsearch.java:161)
    	at org.elasticsearch.cli.EnvironmentAwareCommand.execute(EnvironmentAwareCommand.java:86)
    	at org.elasticsearch.cli.Command.mainWithoutErrorHandling(Command.java:127)
    	at org.elasticsearch.cli.Command.main(Command.java:90)
    	at org.elasticsearch.bootstrap.Elasticsearch.main(Elasticsearch.java:126)
    	at org.elasticsearch.bootstrap.Elasticsearch.main(Elasticsearch.java:92)
​    我们通过排查，发现是因为 **/soft/elsearch/config/elasticsearch.keystore** 存在问题
![](http://image.moguit.cn/12cf6759fe294c998995b52c2f932923)
也就是说该文件还是所属于**root** 用户，而我们使用 **elsearch** 用户无法操作，所以需要把它变成 **elsearch**
    chown elsearch:elsearch elasticsearch.keystore
### 错误情况6
    [1]: the default discovery settings are unsuitable for production use; at least one of [discovery.seed_hosts, discovery.seed_providers, cluster.initial_master_nodes] must be configured
    ERROR: Elasticsearch did not exit normally - check the logs at /soft/elsearch/logs/elasticsearch.log
继续修改配置 **elasticsearch.yaml**
    # 取消注释，并保留一个节点
    node.name: node-1
    cluster.initial_master_nodes: ["node-1"]
ElasticSearchHead可视化工具
----------------------
由于 **ES** 官方没有给 **ES** 提供可视化管理工具，仅仅是提供了后台的服务，**elasticsearch-head** 是一个为 **ES** 开发的一个页面客户端工具，其源码托管于Github
> Github地址：https://github.com/mobz/elasticsearch-head
head提供了以下安装方式
*   源码安装，通过npm run start 启动（不推荐）
*   通过docker安装（推荐）
*   通过chrome插件安装（推荐）
*   通过 ES 的plugin方式安装（不推荐）
### 通过Docker方式安装
    #拉取镜像
    docker pull mobz/elasticsearch-head:5
    #创建容器
    docker create --name elasticsearch-head -p 9100:9100 mobz/elasticsearch-head:5
    #启动容器
    docker start elasticsearch-head
通过浏览器进行访问：
![浏览器访问](http://image.moguit.cn/a7cadffda03648469fe956075837e692)
注意： 由于前后端分离开发，所以会存在跨域问题，需要在服务端做 **CORS** 的配置，如下：
    vim elasticsearch.yml
    http.cors.enabled: true http.cors.allow-origin: "*"
若通过 **Chrome** 插件的方式安装不存在该问题
### 通过Chrome插件安装
打开 **Chrome** 的应用商店，即可安装 [https://chrome.google.com/webstore/detail/elasticsearch-head/ffmkiejjmecolpfloofpjologoblkegm](https://chrome.google.com/webstore/detail/elasticsearch-head/ffmkiejjmecolpfloofpjologoblkegm)
![Chrome插件安装](http://image.moguit.cn/d222796697b54982954ff51761508a0e)
我们也可以新建索引
![新建索引](http://image.moguit.cn/046b484f652c47d9a90aba32d2d342ab)
>  推荐使用 **Chrome** 插件的方式安装，如果网络环境不允许，就采用其它方式安装。
ElasticSearch中的基本概念
-------------------
### 索引
索引是 **Elasticsearch** 对逻辑数据的逻辑存储，所以它可以分为更小的部分。
可以把索引看成关系型数据库的表，索引的结构是为快速有效的全文索引准备的，特别是它不存储原始值。
**Elasticsearch** 可以把索引存放在一台机器或者分散在多台服务器上，每个索引有一或多个分片（**shard**），每个分片可以有多个副本（**replica**）。
### 文档
*   存储在 **Elasticsearch** 中的主要实体叫文档（**document**）。用关系型数据库来类比的话，一个文档相当于数据库表中的一行记录。
*   **Elasticsearch** 和 **MongoDB** 中的文档类似，都可以有不同的结构，但 **Elasticsearch** 的文档中，相同字段必须有相同类型。
*   文档由多个字段组成，每个字段可能多次出现在一个文档里，这样的字段叫多值字段（**multivalued**）。 每个字段的类型，可以是文本、数值、日期等。字段类型也可以是复杂类型，一个字段包含其他子文档或者数 组。
### 映射
所有文档写进索引之前都会先进行分析，如何将输入的文本分割为词条、哪些词条又会被过滤，这种行为叫做 映射（**mapping**）。一般由用户自己定义规则。
### 文档类型
*   在 **Elasticsearch** 中，一个索引对象可以存储很多不同用途的对象。例如，一个博客应用程序可以保存文章和评论。
*   每个文档可以有不同的结构。
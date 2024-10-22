> 大家好，我是陌溪，欢迎点击下方的公众号名片，关注陌溪，让我们一起成长~
在前面的章节中，我们了解了蘑菇博客的日志收集模块，下面我们一起来学习蘑菇博客中的链路追踪模块~
![蘑菇博客中的链路追踪服务](images/image-20210618190706851.png)
随着微服务架构的流行，服务按照不同的维度进行拆分。一个由客户端发起的请求在后端系统中会经过多个不同的服务节点调用来协同产生最后的请求结果，每一个前端请求都会形成一条复杂的分布式服务调用链路，链路中的任何一环出现高延时或错误都会引起整个请求最后的失败。
![服务调用链路](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevgqgm3j30n60bjdj9.jpg)
并且，伴随着微服务数量的增加，对调用链路的分析将会越来越复杂，它们之间的关系可能如下所示。（密集恐惧症慎入~）
![庞大的调用链路](images/28aece2941f54d3aa76fedf64d2edb77)
在复杂的调用链路中假设存在一条调用链路响应缓慢，如何定位其中延迟高的服务呢？这个时候就需要有一个用于调用链路的监控和服务跟踪的解决方案。
## 什么是Zipkin?
### 定义
**Zipkin** 是 **Twitter** 的一个开源项目，它基于 **Google Dapper** 实现，它致力于收集服务的定时数据，以解决微服务架构中的延迟问题，包括数据的收集、存储、查找和展现。 我们可以使用它来收集各个服务器上请求链路的跟踪数据，并通过它提供的 **REST API** 接口来辅助我们查询跟踪数据以实现对分布式系统的监控程序，从而及时地发现系统中出现的延迟升高问题并找出系统性能瓶颈的根源。除了面向开发的 **API** 接口之外，它也提供了方便的 **UI** 组件来帮助我们直观的搜索跟踪信息和分析请求链路明细，比如：可以查询某段时间内各用户请求的处理时间等。
![zipkin收集信息](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevh2wpyj30j70g0t9d.jpg)
如上图所示，各业务系统在彼此调用时，将特定的跟踪消息传递至 **zipkin** , 同时 **zipkin**在收集到跟踪信息后将其聚合处理、存储、展示等，用户可通过 **web UI** 方便获得网络延迟、调用链路、系统依赖等等。
并且 **zipkin** 会根据调用关系通过 **zipkin ui** 生成依赖关系图，下面是我搭建成功后，蘑菇博客链路追踪的依赖图。
![蘑菇博客中的服务依赖图](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevha5o9j30wd0ifgmh.jpg)
注意: **Zipkin** 仅对 **RPC** 通信过程进行记录，注意它与业务代码日志是无关的，如果你希望找到一款 **LogAppender** 来分析所有 **Log4j** 留下的日志，那么建议还是使用 **Kakfa+ELK** 这种传统的方法来实现。
> 源码：https://github.com/apache/incubator-zipkin
### 概念
使用 **zipkin** 涉及到以下几个概念
- **Span**：基本工作单元，一次链路调用(可以是 **RPC**，**DB** 等没有特定的限制)创建一个 **span**，通过一个 **64** 位 **ID** 标识它，**span** 通过还有其他的数据，例如描述信息，时间戳，**key-value** 对的 ( **Annotation** ) **tag** 信息，**parent-id** 等,其中 **parent-id** 可以表示 **span** 调用链路来源，通俗的理解 **span** 就是一次请求信息
- **Trace**：类似于树结构的 **Span** 集合，表示一条调用链路，存在唯一标识
- **Annotation**：注解，用来记录请求特定事件相关信息（例如时间），通常包含四个注解信息
  - **CS**： Client Start，表示客户端发起请求
  - **SR**：Server Receive，表示服务端收到请求
  - **SS**：Server Send，表示服务端完成处理，并将结果发送给客户端
  - **CR**：Client Received，表示客户端获取到服务端返回信息
- **BinaryAnnotation**：提供一些额外信息，一般已 **key-value** 对出现
### 完整的调用链路图
![完整的调用链路图](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevil1kkj30ow0dlwgk.jpg)
上图表示一请求链路，一条链路通过 **Trace Id** 唯一标识，**Span** 标识发起的请求信息，各 **span** 通过 **parent id** 关联起来，如图
![](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevirn9bj30ix06kq33.jpg)
整个链路的依赖关系如下:
![链路依赖关系](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevizirjj30qj05gjrm.jpg)
完成链路调用的记录后，如何来计算调用的延迟呢，这就需要利用 **Annotation** 信息
![计算调用延迟](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevjdkn4j30gw06fdg6.jpg)
**SR-CS**：得到请求发出延迟
**SS-SR**：得到服务端处理延迟
**CR-CS**：得到整个链路完成延迟
### Zipkin Server
**Zipkin Server** 主要包括四个模块：
- **Collector**：接收或收集各应用传输的数据
- **Storage**：存储接受或收集过来的数据，当前支持 **Memory**，**MySQL**，**Cassandra**，**ElasticSearch** 等，默认存储在内存中
- **API**（Query）：负责查询Storage中存储的数据，提供简单的 **JSON API** 获取数据，主要提供给 **Web UI** 使用
- **Web**：提供简单的 **Web** 界面
### 缺点
- 在 **SpringCloud** 中强依赖与 **Spring-cloud-starter-zipkin**
- **Zipkin** 只能统计接口级别的信息
## 什么是Sleuth？
### 定义
**spring-cloud-starter-sleuth**: 英文名是侦探，它的功能是在项目中自动为日志加入 **Tag** 与序列号。
> 源码：https://github.com/spring-cloud/spring-cloud-sleuth
### 原理
调用侧请求中加入额外的 **Span** 序列号等上下文信息放入 **Header** 中(通过注入Feign定制Client实现)，被调用侧通过全局 **Filter** 模拟 **AOP** 记录执行情况，计算执行情况与耗时，并存入定制的 **ByteBoundedQueue** 队列中，然后通过 **HTTP** 等将信息异步发送到 **Zipkin** 收集器中，**Zipkin** 收集器通过UI显示调用详情
其中添加了如下组件
- **TraceFeignClient**： 请求端注入的 **FeignClient**，为 **Request** 的 **Header** 添加 **SpanID**, **TraceID**等信息
- **TraceFilter**： 接收端注入的定制 **Filter**，它将解析 **Request** 中的 **Header**，执行业务，计算耗时，最终算出一个完整的 **JSON** 格式的 **Span**，通过队列异步发送到收集器ZipKin中
- **ZipKin**：日志收集器，读取 **JSON** 格式的 **SPAN** 信息，并存储与展示
### 采样率
如果使用 **spring-cloud-sleuth-zipkin** 或 **spring-cloud-sleuth-stream**，**PercentageBasedSampler** 是默认的（默认值是0.1），你可以使用 **spring.sleuth.sampler.percentage** 配置输出。
### 附加信息
用户可以使用 **span tags** 定制关键字，为了限制 **span** 数据量，一般一个 **HTTP** 请求只会被少数元数据标记，例如 **status** **code**、**host** 以及 **URL**，用户可以通过配置 **spring.sleuth.keys.http.headers** (一系列头名称)添加 **request headers**
## 安装Zipkin
### 安装须知
在 **SpringBoot 2.x** 版本后就不推荐自定义 **zipkin server** 了，推荐使用官网下载的 **jar** 包方式
也就是说我们不需要编写一个 **mogu-zipkin** 服务了，而改成直接启动 **jar** 包即可
### 下载地址
```
https://search.maven.org/remote_content?g=io.zipkin.java&a=zipkin-server&v=LATEST&c=exec
```
### 运行
```shell
java -jar zipkin-server-2.12.5-exec.jar
# 或集成RabbitMQ
java -jar zipkin-server-2.12.5-exec.jar --zipkin.collector.rabbitmq.addresses=127.0.0.1
```
如果出现下图，表示 **zipkin**以内存存储的方式进行启动了。
![zipkin启动成功](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevhmkp6j30q309dq5o.jpg)
### 日志存储方式
目前 **zipkin** 收集的信息能够以三种方式进行存储
- 内存（默认）
- **Mysql**
- **ElasticSearch**
这里我们尝试的是以 **mysql** 的方式进行存储，如果不想以 **mysql** 进行存储的话，可以忽略这一步
首先，初始化 **mysql** 数据库，请执行下面的 **SQL** 脚本，在之前，需要创建一个数据库，叫 **zipkin**
```
--
-- Copyright 2015-2019 The OpenZipkin Authors
--
-- Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
-- in compliance with the License. You may obtain a copy of the License at
--
-- http://www.apache.org/licenses/LICENSE-2.0
--
-- Unless required by applicable law or agreed to in writing, software distributed under the License
-- is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
-- or implied. See the License for the specific language governing permissions and limitations under
-- the License.
--
CREATE TABLE IF NOT EXISTS zipkin_spans (
  `trace_id_high` BIGINT NOT NULL DEFAULT 0 COMMENT 'If non zero, this means the trace uses 128 bit traceIds instead of 64 bit',
  `trace_id` BIGINT NOT NULL,
  `id` BIGINT NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `remote_service_name` VARCHAR(255),
  `parent_id` BIGINT,
  `debug` BIT(1),
  `start_ts` BIGINT COMMENT 'Span.timestamp(): epoch micros used for endTs query and to implement TTL',
  `duration` BIGINT COMMENT 'Span.duration(): micros used for minDuration and maxDuration query',
  PRIMARY KEY (`trace_id_high`, `trace_id`, `id`)
) ENGINE=InnoDB ROW_FORMAT=COMPRESSED CHARACTER SET=utf8 COLLATE utf8_general_ci;
ALTER TABLE zipkin_spans ADD INDEX(`trace_id_high`, `trace_id`) COMMENT 'for getTracesByIds';
ALTER TABLE zipkin_spans ADD INDEX(`name`) COMMENT 'for getTraces and getSpanNames';
ALTER TABLE zipkin_spans ADD INDEX(`remote_service_name`) COMMENT 'for getTraces and getRemoteServiceNames';
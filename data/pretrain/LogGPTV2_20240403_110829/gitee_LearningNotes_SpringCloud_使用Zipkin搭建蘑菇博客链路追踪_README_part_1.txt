# 使用Zipkin搭建蘑菇博客链路追踪
## 前言
Zipkin是一个开源的分布式的链路追踪系统，每个微服务都会向zipkin报告计时数据，聚合各业务系统调用延迟数据，达到链路调用监控跟踪。
![image-20200206123422800](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevgqgm3j30n60bjdj9.jpg)
如图，在复杂的调用链路中假设存在一条调用链路响应缓慢，如何定位其中延迟高的服务呢？
- 日志： 通过分析调用链路上的每个服务日志得到结果
- zipkin：使用`zipkin`的`web UI`可以一眼看出延迟高的服务
![image-20200206123502226](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevh2wpyj30j70g0t9d.jpg)
如图所示，各业务系统在彼此调用时，将特定的跟踪消息传递至`zipkin`,zipkin在收集到跟踪信息后将其聚合处理、存储、展示等，用户可通过`web UI`方便获得网络延迟、调用链路、系统依赖等等。
同时zipkin会根据调用关系通过zipkin ui生成依赖关系图，下面是我搭建成功后，蘑菇博客链路追踪的依赖图。
![image-20200206103258522](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevha5o9j30wd0ifgmh.jpg)
tip：在使用zipkin链路追踪的时候，需要提前启动zipkin服务，然后在启动我们的蘑菇博客项目，这样才能够正常的将服务调用的信息注册到zipkin中
## 安装Zipkin
### 安装须知
在 SpringBoot 2.x 版本后就不推荐自定义 zipkin server 了，推荐使用官网下载的 jar 包方式
也就是说我们不需要编写一个mogu-zipkin服务了，而改成直接启动jar包即可
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
这样zipkin就是以内存存储的方式进行启动了
![image-20200206124625792](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevhmkp6j30q309dq5o.jpg)
### 日志存储方式
目前zipkin收集的信息能够以三种方式进行存储
- 内存（默认）
- Mysql
- ElasticSearch
这里我们尝试的是以mysql的方式进行存储，如果不想以mysql进行存储的话，可以忽略这一步
- 初始化mysql数据库
首先我们需要在mogu_blog数据库中，执行下面的官方SQL脚本，创建对应的表
[官方脚本传送门](https://github.com/openzipkin/zipkin/blob/master/zipkin-storage/mysql-v1/src/main/resources/mysql.sql)
如果上述地址过期，请执行下面的SQL脚本，在之前，需要创建一个数据库，叫zipkin
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
ALTER TABLE zipkin_spans ADD INDEX(`start_ts`) COMMENT 'for getTraces ordering and range';
CREATE TABLE IF NOT EXISTS zipkin_annotations (
  `trace_id_high` BIGINT NOT NULL DEFAULT 0 COMMENT 'If non zero, this means the trace uses 128 bit traceIds instead of 64 bit',
  `trace_id` BIGINT NOT NULL COMMENT 'coincides with zipkin_spans.trace_id',
  `span_id` BIGINT NOT NULL COMMENT 'coincides with zipkin_spans.id',
  `a_key` VARCHAR(255) NOT NULL COMMENT 'BinaryAnnotation.key or Annotation.value if type == -1',
  `a_value` BLOB COMMENT 'BinaryAnnotation.value(), which must be smaller than 64KB',
  `a_type` INT NOT NULL COMMENT 'BinaryAnnotation.type() or -1 if Annotation',
  `a_timestamp` BIGINT COMMENT 'Used to implement TTL; Annotation.timestamp or zipkin_spans.timestamp',
  `endpoint_ipv4` INT COMMENT 'Null when Binary/Annotation.endpoint is null',
  `endpoint_ipv6` BINARY(16) COMMENT 'Null when Binary/Annotation.endpoint is null, or no IPv6 address',
  `endpoint_port` SMALLINT COMMENT 'Null when Binary/Annotation.endpoint is null',
  `endpoint_service_name` VARCHAR(255) COMMENT 'Null when Binary/Annotation.endpoint is null'
) ENGINE=InnoDB ROW_FORMAT=COMPRESSED CHARACTER SET=utf8 COLLATE utf8_general_ci;
ALTER TABLE zipkin_annotations ADD UNIQUE KEY(`trace_id_high`, `trace_id`, `span_id`, `a_key`, `a_timestamp`) COMMENT 'Ignore insert on duplicate';
ALTER TABLE zipkin_annotations ADD INDEX(`trace_id_high`, `trace_id`, `span_id`) COMMENT 'for joining with zipkin_spans';
ALTER TABLE zipkin_annotations ADD INDEX(`trace_id_high`, `trace_id`) COMMENT 'for getTraces/ByIds';
ALTER TABLE zipkin_annotations ADD INDEX(`endpoint_service_name`) COMMENT 'for getTraces and getServiceNames';
ALTER TABLE zipkin_annotations ADD INDEX(`a_type`) COMMENT 'for getTraces and autocomplete values';
ALTER TABLE zipkin_annotations ADD INDEX(`a_key`) COMMENT 'for getTraces and autocomplete values';
ALTER TABLE zipkin_annotations ADD INDEX(`trace_id`, `span_id`, `a_key`) COMMENT 'for dependencies job';
CREATE TABLE IF NOT EXISTS zipkin_dependencies (
  `day` DATE NOT NULL,
  `parent` VARCHAR(255) NOT NULL,
  `child` VARCHAR(255) NOT NULL,
  `call_count` BIGINT,
  `error_count` BIGINT,
  PRIMARY KEY (`day`, `parent`, `child`)
) ENGINE=InnoDB ROW_FORMAT=COMPRESSED CHARACTER SET=utf8 COLLATE utf8_general_ci;
```
执行完成后，我们将会得到下面的三个表
![image-20200206130303873](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevhte5bj306x04ywec.jpg)
其中
- zipkin_spans：存放基本工作单元，也就是一次链路调用的信息
- zipkin_dependencies：存放的依赖信息
- zipkin_annotations：用来记录请求特定事件相关信息（例如时间）
然后在安装下面的方式进行启动
```
java -jar zipkin.jar --STORAGE_TYPE=mysql --MYSQL_DB=zipkin --MYSQL_USER=root --MYSQL_PASS=root --MYSQL_HOST=localhost --MYSQL_TCP_PORT=3306
```
启动完成后，我们在运行我们的服务，在打开数据库就能看到信息存储在mysql中了
![image-20200206194458065](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevi1l98j31hb0fsgog.jpg)
## 项目中集成Zipkin
安装完成后，我们需要引入 sleuth  和 zipkin的依赖
```xml
    org.springframework.cloud
    spring-cloud-starter-sleuth
    org.springframework.cloud
    spring-cloud-starter-zipkin
```
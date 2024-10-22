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
![创建三个表](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevhte5bj306x04ywec.jpg)
其中
- **zipkin_spans**：存放基本工作单元，也就是一次链路调用的信息
- **zipkin_dependencies**：存放的依赖信息
- **zipkin_annotations**：用来记录请求特定事件相关信息（例如时间）
然后在安装下面的方式进行启动
```
java -jar zipkin.jar --STORAGE_TYPE=mysql --MYSQL_DB=zipkin --MYSQL_USER=root --MYSQL_PASS=root --MYSQL_HOST=localhost --MYSQL_TCP_PORT=3306
```
启动完成后，我们在运行我们的服务，在打开数据库就能看到信息存储在 **mysql** 中了
![收集的数据](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevi1l98j31hb0fsgog.jpg)
## 蘑菇博客集成zipkin
安装完成后，我们需要引入 **sleuth**  和 **zipkin** 的依赖
```xml
    org.springframework.cloud
    spring-cloud-starter-sleuth
    org.springframework.cloud
    spring-cloud-starter-zipkin
```
然后在业务服务的application.yml增加下面的配置，其中蘑菇博客的业务服务主要是：mogu-web，mogu-admin，mogu-sms，mogu-picture，mogu-search
```yml
#spring
spring:
  # sleuth 配置
  sleuth:
    web:
      client:
        enabled: true
    sampler:
      probability: 1.0 # 采样比例为: 0.1(即10%),设置的值介于0.0到1.0之间，1.0则表示全部采集。
  # zipkin 配置
  zipkin:
    base-url: http://localhost:9411  # 指定了Zipkin服务器的地址
```
然后浏览器输入下面的地址：http://localhost:9411 ，如果出现下面的画面，那么代表我们 **zipkin** 服务配置成功了
![zipkin ui](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevibv3pj31ai0p7jsr.jpg)
## Zipkin ui界面介绍
### 首页
首页里面主要承载了trace的查询功能，根据不同的条件，搜索数据
![首页字段解释](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevjo5eoj30za0l7q65.jpg)
### trace详情
![详情页](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevjzpzlj31580cjwk6.jpg)
### span详情
![span详情页](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevk9vynj30qs0ew77a.jpg)
这个图中，需要注意的是相对时间和调用行为，调用行为分如下四种：
**CS - Client Send** ：客户端已经提出了请求。这就设置了跨度的开始。
**SR - Server Receive**：服务器已收到请求并将开始处理它。这与CS之间的差异将是网络延迟和时钟抖动的组合。
**SS - Server Send**：服务器已完成处理，并将请求发送回客户端。这与SR之间的差异将是服务器处理请求所花费的时间
**CR - Client Receive**： 客户端已经收到来自服务器的响应。这就设置了跨度的终点。当记录注释时，RPC被认为是完整的。
**相对时间**：表示在调用链开始到现在的时间，如下所示![](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevkim2tj30oa06hdg7.jpg)
**17ms** 的时候，**Client Send bas-ms** 这个应用发出了调用
**19ms** 的时候，**Server Receive ems-ms** 收到了 **bas-ms** 的调用。 这个说明，从 **bas-ms** 到 **ems-ms** 中间的网络耗时花费了2ms.
**34ms** 的时候，**Server Send ems-ms** 的方法执行完毕，准备返回响应结果给 **bas-ms** , 这说明 **ems-ms** 处理请求花费了 **34-19 = 15ms**
**34ms** 的时候，**Client Receive bas-ms** 收到了返回结果
界面显示的时候，是根据相对时间来排序的，所以 **Client Receive** 排在了第三位，因为他和 **Server Send** 的时间是一样的。
### 全局依赖
![全局依赖](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevld3bbj30r3051jrl.jpg)
点击服务名，弹出如下框，显示出了调用关系
![调用关系](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevljr4rj30r409ht8x.jpg)
点击具体的服务名，出现如下界面
![](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevmbq7qj30h007mgll.jpg)
- **Number of calls** ： 总的调用数（除去异常的）
- **Number of errors**：调用异常的次数
## 参考资料
- https://blog.csdn.net/singgel/article/details/89853346
- https://blog.csdn.net/u012394095/article/details/82585863
## 往期推荐
- [蘑菇博客从0到2000Star，分享我的Java自学路线图](https://mp.weixin.qq.com/s/3u6OOYkpj4_ecMzfMqKJRw)
- [从三本院校到斩获字节跳动后端研发Offer-讲述我的故事](https://mp.weixin.qq.com/s/c4rR_aWpmNNFGn-mZBLWYg)
- [陌溪在公众号摸滚翻爬半个月，整理的入门指南](https://mp.weixin.qq.com/s/Jj1i-mD9Tw0vUEFXi5y54g)
- [读者问:有没有高效的记视频笔记方法？](https://mp.weixin.qq.com/s/QcQnV1yretxmDQr4ELW7_g)
- [万字长文带你学习ElasticSearch](https://mp.weixin.qq.com/s/9eh6rK2aZHRiBpf5bRae9g)
- [如何使用一条命令完成蘑菇博客的部署？](https://mp.weixin.qq.com/s/LgRIqdPAGzN1tCPMi0Y8RQ)
## 结语
最近，应各位小伙伴们的需求，陌溪已经把 **开源学习笔记仓库** 整理成 **PDF** 版本啦，方便大家在手机或者电脑上阅读。
> 开源笔记地址：https://gitee.com/moxi159753/LearningNotes
以下笔记仓库的部分 **PDF** 文件 ~
![大厂面试第二季笔记](images/image-20210523171559176.png)
![Java面试突击笔记](images/image-20210523171833579.png)
![JVM笔记](images/image-20210523172056549.png)
如果有需要离线阅读的小伙伴可以到公众号回复 **PDF** ，即可获取下载地址~
![img](https://gitee.com/moxi159753/LearningNotes/raw/master/doc/images/qq/%E8%8E%B7%E5%8F%96PDF.jpg)
同时本公众号**申请较晚**，暂时没有开通**留言**功能，欢迎小伙伴们添加我的私人微信【备注：**加群**】，我将邀请你加入到**蘑菇博客交流群**中，欢迎小伙伴们找陌溪一块聊天唠嗑，共同学习进步，如果你觉得本文对你有所帮助，麻烦小伙伴们动动手指给文章点个“**赞**”和“**在看**”。
![快来找陌溪唠嗑吧](https://gitee.com/moxi159753/LearningNotes/raw/master/doc/images/qq/%E6%B7%BB%E5%8A%A0%E9%99%8C%E6%BA%AA.png)
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
然后浏览器输入下面的地址：http://localhost:9411 ，如果出现下面的画面，那么代表我们zipkin服务配置成功了
![image-20200206112551615](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevibv3pj31ai0p7jsr.jpg)
## Sleuth
### 定义
spring-cloud-starter-sleuth: 英文名是侦探，它的功能是在项目中自动为日志加入Tag与序列号
源码：https://github.com/spring-cloud/spring-cloud-sleuth
### 原理
调用侧请求中加入额外的Span序列号等上下文信息放入Header中(通过注入Feign定制Client实现)，被调用侧通过全局Filter模拟AOP记录执行情况，计算执行情况与耗时，并存入定制的ByteBoundedQueue队列中，然后通过HTTP等将信息异步发送到Zipkin收集器中，Zipkin收集器通过UI显示调用详情
其中添加了如下组件
- TraceFeignClient： 请求端注入的FeignClient，为Request的Header添加SpanID, TraceID等信息
- TraceFilter： 接收端注入的定制Filter，它将解析Request中的Header，执行业务，计算耗时，最终算出一个完整的JSON格式的Span，通过队列异步发送到收集器ZipKin中
- ZipKin：日志收集器，读取JSON格式的SPAN信息，并存储与展示
### 采样率
如果使用spring-cloud-sleuth-zipkin或spring-cloud-sleuth-stream，PercentageBasedSampler是默认的（默认值是0.1），你可以使用spring.sleuth.sampler.percentage配置输出
### 附加信息
用户可以使用span tags定制关键字，为了限制span数据量，一般一个HTTP请求只会被少数元数据标记，例如status code、host以及URL，用户可以通过配置spring.sleuth.keys.http.headers(一系列头名称)添加request headers
## Zipkin
### 定义
来自Twitte的分布式日志收集工具，分为上传端(spring-cloud-starter-zipkin，集成到项目中)与服务端(独立部署，默认将数据存到内存中) 
注意: Zipkin仅对RPC通信过程进行记录，注意它与业务代码日志是无关的，如果你希望找到一款LogAppender来分析所有Log4j留下的日志，那么建议还是使用Kakfa+ELK这种传统的方法来实现。
### 源码
https://github.com/apache/incubator-zipkin
### 概念
使用zipkin涉及到以下几个概念
- Span：基本工作单元，一次链路调用(可以是RPC，DB等没有特定的限制)创建一个span，通过一个64位ID标识它，span通过还有其他的数据，例如描述信息，时间戳，key-value对的(Annotation)tag信息，parent-id等,其中parent-id可以表示span调用链路来源，通俗的理解span就是一次请求信息
- Trace：类似于树结构的Span集合，表示一条调用链路，存在唯一标识
- Annotation：注解，用来记录请求特定事件相关信息（例如时间），通常包含四个注解信息
  - cs： Client Start,表示客户端发起请求
  - sr：Server Receive,表示服务端收到请求
  - ss：Server Send,表示服务端完成处理，并将结果发送给客户端
  - cr：Client Received,表示客户端获取到服务端返回信息
- BinaryAnnotation：提供一些额外信息，一般已key-value对出现
### 完整的调用链路图
![image-20200206124108256](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevil1kkj30ow0dlwgk.jpg)
上图表示一请求链路，一条链路通过`Trace Id`唯一标识，`Span`标识发起的请求信息，各`span`通过`parent id` 关联起来，如图
![image-20200206124142798](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevirn9bj30ix06kq33.jpg)
整个链路的依赖关系如下:
![image-20200206124156502](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevizirjj30qj05gjrm.jpg)
完成链路调用的记录后，如何来计算调用的延迟呢，这就需要利用`Annotation`信息
![image-20200206124208350](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevjdkn4j30gw06fdg6.jpg)
sr-cs 得到请求发出延迟
ss-sr 得到服务端处理延迟
cr-cs 得到整个链路完成延迟
### Zipkin Server
Zipkin Server主要包括四个模块：
- Collector 接收或收集各应用传输的数据
- Storage 存储接受或收集过来的数据，当前支持Memory，MySQL，Cassandra，ElasticSearch等，默认存储在内存中
- API（Query） 负责查询Storage中存储的数据，提供简单的JSON API获取数据，主要提供给web UI使用
- Web 提供简单的web界面
## 缺点
- 在springcloud中强依赖与spring-cloud-starter-zipkin
- zipkin只能统计接口级别的信息
## Sleuth 和 Zipkin ui界面介绍
### 首页
首页里面主要承载了trace的查询功能，根据不同的条件，搜索数据
![image-20200206112747752](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevjo5eoj30za0l7q65.jpg)
### trace详情
![image-20200206113151796](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevjzpzlj31580cjwk6.jpg)
### span详情
![image-20200206114035194](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevk9vynj30qs0ew77a.jpg)
这个图中，需要注意的是相对时间和调用行为
调用行为分如下四种：
cs - Client Send : 客户端已经提出了请求。这就设置了跨度的开始。
sr - Server Receive: 服务器已收到请求并将开始处理它。这与CS之间的差异将是网络延迟和时钟抖动的组合。
ss - Server Send: 服务器已完成处理，并将请求发送回客户端。这与SR之间的差异将是服务器处理请求所花费的时间
cr - Client Receive : 客户端已经收到来自服务器的响应。这就设置了跨度的终点。当记录注释时，RPC被认为是完整的。
相对时间：
表示在调用链开始到现在的时间，比如
![image-20200206114610081](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevkim2tj30oa06hdg7.jpg)
从trace生成到现在，
17ms的时候，Client Send bas-ms这个应用发出了调用
19ms的时候，Server Receive ems-ms收到了bas-ms的调用。 这个说明，从bas-ms到ems-ms中间的网络耗时花费了2ms.
34ms的时候，Server Send ems-ms的方法执行完毕，准备返回响应结果给bas-ms , 这说明ems-ms处理请求花费了34-19 = 15ms
34ms的时候，Client Receive bas-ms收到了返回结果
界面显示的时候，是根据相对时间来排序的，所以Client Receive排在了第三位，因为他和Server Send的时间是一样的。
### 全局依赖
![image-20200206114642063](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevld3bbj30r3051jrl.jpg)
点击服务名，弹出如下框，显示出了调用关系
![image-20200206114831472](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevljr4rj30r409ht8x.jpg)
点击具体的服务名，出现如下界面
![image-20200206115433974](http://ww3.sinaimg.cn/large/005HgCsWgy1gcyevmbq7qj30h007mgll.jpg)
- Number of calls ： 总的调用数（除去异常的）
- Number of errors：调用异常的次数
## 参考
- https://blog.csdn.net/singgel/article/details/89853346
- https://blog.csdn.net/u012394095/article/details/82585863
# SpringCloudAlibabaSentinel实现熔断和限流
## Sentinel
### 官网
Github：https://github.com/alibaba/Sentinel
Sentinel：分布式系统的流量防卫兵，相当于Hystrix
Hystrix存在的问题
- 需要我们程序员自己手工搭建监控平台
- 没有一套web界面可以给我们进行更加细粒度化的配置，流量控制，速率控制，服务熔断，服务降级。。
这个时候Sentinel运营而生
- 单独一个组件，可以独立出来
- 直接界面化的细粒度统一配置
约定 > 配置 >编码，都可以写在代码里，但是尽量使用注解和配置代替编码
### 是什么
随着微服务的流行，服务和服务之间的稳定性变得越来越重要。Sentinel 以流量为切入点，从流量控制、熔断降级、系统负载保护等多个维度保护服务的稳定性。
Sentinel 具有以下特征:
- **丰富的应用场景**：Sentinel 承接了阿里巴巴近 10 年的双十一大促流量的核心场景，例如秒杀（即突发流量控制在系统容量可以承受的范围）、消息削峰填谷、集群流量控制、实时熔断下游不可用应用等。
- **完备的实时监控**：Sentinel 同时提供实时的监控功能。您可以在控制台中看到接入应用的单台机器秒级数据，甚至 500 台以下规模的集群的汇总运行情况。
- **广泛的开源生态**：Sentinel 提供开箱即用的与其它开源框架/库的整合模块，例如与 Spring Cloud、Dubbo、gRPC 的整合。您只需要引入相应的依赖并进行简单的配置即可快速地接入 Sentinel。
- **完善的 SPI 扩展点**：Sentinel 提供简单易用、完善的 SPI 扩展接口。您可以通过实现扩展接口来快速地定制逻辑。例如定制规则管理、适配动态数据源等。
### 主要特征
![image-20200416073841558](images/image-20200416073841558.png)
### 生态圈
![image-20200416073905426](images/image-20200416073905426.png)
### 下载
Github：https://github.com/alibaba/Sentinel/releases
![image-20200416074923500](images/image-20200416074923500.png)
## 安装Sentinel控制台
sentinel组件由两部分组成，后台和前台8080
Sentinel分为两部分
- 核心库（Java客户端）不依赖任何框架/库，能够运行在所有Java运行时环境，同时对Dubbo、SpringCloud等框架也有较好的支持。
- 控制台（Dashboard）基于SpringBoot开发，打包后可以直接运行，不需要额外的Tomcat等应用容器
使用 `java -jar` 启动，同时Sentinel默认的端口号是8080，因此不能被占用
注意，下载时候，由于Github经常抽风，因此可以使用Gitee进行下，首先先去Gitee下载源码
![image-20200416080109354](images/image-20200416080109354.png)
然后执行`mvn package` 进行构建，本博客同级目录下了，已经有个已经下载好的，欢迎自取
## 初始化演示工程
启动Nacos8848成功
### 引入依赖
```
    com.alibaba.csp
    sentinel-datasource-nacos
    com.alibaba.cloud
    spring-cloud-starter-alibaba-sentinel
```
### 修改YML
```
server:
  port: 8401
spring:
  application:
    name: cloudalibaba-sentinel-service
  cloud:
    nacos:
      discovery:
        server-addr: localhost:8848 #Nacos服务注册中心地址
    sentinel:
      transport:
        dashboard: localhost:8080 #配置Sentinel dashboard地址
        port: 8719
```
### 增加业务类
```
@RestController
@Slf4j
public class FlowLimitController
{
    @GetMapping("/testA")
    public String testA()
    {
        return "------testA";
    }
    @GetMapping("/testB")
    public String testB()
    {
        log.info(Thread.currentThread().getName()+"\t"+"...testB");
        return "------testB";
    }
}
```
启动8401微服务，查看Sentinel控制台
我们会发现Sentinel里面空空如也，什么也没有，这是因为Sentinel采用的懒加载
执行一下访问即可：`http://localhost:8401/testA` `http://localhost:8401/testB`
![image-20200416083940979](images/image-20200416083940979.png)
## 流控规则
### 基本介绍
![image-20200416084144709](images/image-20200416084144709.png)
**字段说明**
- 资源名：唯一名称，默认请求路径
- 针对来源：Sentinel可以针对调用者进行限流，填写微服务名，默认default（不区分来源）
- 阈值类型 / 单机阈值
  - QPS：（每秒钟的请求数量）：但调用该API的QPS达到阈值的时候，进行限流
  - 线程数：当调用该API的线程数达到阈值的时候，进行限流
- 是否集群：不需要集群
- 流控模式
  - 直接：api都达到限流条件时，直接限流
  - 关联：当关联的资源达到阈值，就限流自己
  - 链路：只记录指定链路上的流量（指定资源从入口资源进来的流量，如果达到阈值，就进行限流）【API级别的针对来源】
- 流控效果
  - 快速失败：直接失败，抛异常
  - Warm UP：根据codeFactory（冷加载因子，默认3），从阈值/CodeFactor，经过预热时长，才达到设置的QPS阈值
  - 排队等待：匀速排队，让请求以匀速的速度通过，阈值类型必须设置QPS，否则无效
### 流控模式
#### 直接（默认）
我们给testA增加流控
![image-20200416084934271](images/image-20200416084934271.png)
![image-20200416085039034](images/image-20200416085039034.png)
![image-20200416085226574](images/image-20200416085226574.png)
然后我们请求 `http://localhost:8401/testA`，就会出现失败，被限流，快速失败
![image-20200416085117306](images/image-20200416085117306.png)
思考：
直接调用的是默认报错信息，能否有我们的后续处理，比如更加友好的提示，类似有hystrix的fallback方法
线程数
这里的线程数表示一次只有一个线程进行业务请求，当前出现请求无法响应的时候，会直接报错，例如，在方法的内部增加一个睡眠，那么后面来的就会失败
```
    @GetMapping("/testD")
    public String testD()
    {
        try { TimeUnit.SECONDS.sleep(1); } catch (InterruptedException e) { e.printStackTrace(); }
        return "------testD";
    }
```
#### 关联
当关联的资源达到阈值时，就限流自己
当与A关联的资源B达到阈值后，就限流A自己，B惹事，A挂了
场景：支付接口达到阈值后，就限流下订单的接口
设置：
当关联资源 /testB的QPS达到阈值超过1时，就限流/testA的Rest访问地址，当关联资源达到阈值后，限制配置好的资源名
![image-20200416090827339](images/image-20200416090827339.png)
这个使用我们利用postman模拟并发密集访问`testB`
首先我们需要使用postman，创建一个请求
![image-20200416091302584](images/image-20200416091302584.png)
同时将请求保存在 Collection中
然后点击箭头，选中接口，选择run
![image-20200416091349552](images/image-20200416091349552.png)
![image-20200416091517551](images/image-20200416091517551.png)
点击运行，大批量线程高并发访问B，导致A失效了，同时我们点击访问 `http://localhost:8401/testA`，结果发现，我们的A已经挂了
![image-20200416091801271](images/image-20200416091801271.png)
在测试A接口
![image-20200416091815140](images/image-20200416091815140.png)
这就是我们的关联限流
#### 链路
多个请求调用了同一个微服务
### 流控效果
#### 直接
快速失败，默认的流控处理
- 直接失败，抛出异常：Blocked by Sentinel（Flow limiting）
#### 预热
系统最怕的就是出现，平时访问是0，然后突然一瞬间来了10W的QPS
公式：阈值 除以 clodFactor（默认值为3），经过预热时长后，才会达到阈值
Warm Up方式，即预热/冷启动方式，当系统长期处于低水位的情况下，当流量突然增加时，直接把系统拉升到高水位可能会瞬间把系统压垮。通过冷启动，让通过的流量缓慢增加，在一定时间内逐渐增加到阈值，给冷系统一个预热的时间，避免冷系统被压垮。通常冷启动的过程系统允许的QPS曲线如下图所示
![image-20200416093702689](images/image-20200416093702689.png)
默认clodFactor为3，即请求QPS从threshold / 3开始，经预热时长逐渐提升至设定的QPS阈值
![image-20200416093919458](images/image-20200416093919458.png)
假设这个系统的QPS是10，那么最开始系统能够接受的 QPS  = 10 / 3 = 3，然后从3逐渐在5秒内提升到10
应用场景：
秒杀系统在开启的瞬间，会有很多流量上来，很可能把系统打死，预热的方式就是为了保护系统，可能慢慢的把流量放进来，慢慢的把阈值增长到设置的阈值。
![image-20200416094419813](images/image-20200416094419813.png)
#### 排队等待
大家均速排队，让请求以均匀的速度通过，阈值类型必须设置成QPS，否则无效
均速排队方式必须严格控制请求通过的间隔时间，也即让请求以匀速的速度通过，对应的是漏桶算法。
![image-20200416094734543](images/image-20200416094734543.png)
这种方式主要用于处理间隔性突发的流量，例如消息队列，想象一下这样的场景，在某一秒有大量的请求到来，而接下来的几秒处于空闲状态，我们系统系统能够接下来的空闲期间逐渐处理这些请求，而不是在第一秒直接拒绝多余的请求。
设置含义：/testA 每秒1次请求，超过的话，就排队等待，等待时间超过20000毫秒
![image-20200416094609143](images/image-20200416094609143.png)
# Nacos
## SpringCloud Alibaba简介
SpringCloud Alibaba诞生的主要原因是：因为Spring Cloud Netflix项目进入了维护模式
### 维护模式
将模块置为维护模式，意味着SpringCloud团队将不再向模块添加新功能，我们将恢复block级别的bug以及安全问题，我们也会考虑并审查社区的小型pull request
我们打算继续支持这些模块，知道Greenwich版本被普遍采用至少一年
### 意味着
Spring Cloud Netflix将不再开发新的组件，我们都知道Spring Cloud项目迭代算是比较快，因此出现了很多重大issue都还来不及Fix，就又推出了另一个Release。进入维护模式意思就是以后一段时间Spring Cloud Netflix提供的服务和功能就这么多了，不在开发新的组件和功能了，以后将以维护和Merge分支Pull Request为主，新组件将以其他替代
![image-20200414154600906](images/image-20200414154600906.png)
![image-20200414155024158](images/image-20200414155024158.png)
### 诞生
官网：[SpringCloud Alibaba](https://github.com/alibaba/spring-cloud-alibaba/blob/master/README-zh.md)
2018.10.31，Spring Cloud Alibaba正式入驻Spring Cloud官方孵化器，并在Maven仓库发布了第一个
![image-20200414155158301](images/image-20200414155158301.png)
### 能做啥
- 服务限流降级：默认支持servlet，Feign，RestTemplate，Dubbo和RocketMQ限流降级功能的接入，可以在运行时通过控制台实时修改限流降级规则，还支持查看限流降级Metrics监控
- 服务注册与发现：适配Spring Cloud服务注册与发现标准，默认集成了Ribbon的支持
- 分布式配置管理：支持分布式系统中的外部化配置，配置更改时自动刷新
- 消息驱动能力：基于Spring Cloud Stream （内部用RocketMQ）为微服务应用构建消息驱动能力
- 阿里云对象存储：阿里云提供的海量、安全、低成本、高可靠的云存储服务，支持在任何应用、任何时间、任何地点存储和访问任意类型的数据。
- 分布式任务调度：提供秒级，精准、高可靠、高可用的定时（基于Cron表达式）任务调度服务，同时提供分布式的任务执行模型，如网格任务，网格任务支持海量子任务均匀分配到所有Worker
### 引入依赖版本控制
```
            com.alibaba.cloud
            spring-cloud-alibaba-dependencies
            2.2.0.RELEASE
            pom
            import
```
### 怎么玩
- Sentinel：阿里巴巴开源产品，把流量作为切入点，从流量控制，熔断降级，系统负载 保护等多个维度保护系统服务的稳定性
- Nacos：阿里巴巴开源产品，一个更易于构建云原生应用的动态服务发现、配置管理和服务管理平台
- RocketMQ：基于Java的高性能，高吞吐量的分布式消息和流计算平台
- Dubbo：Apache Dubbo是一款高性能Java RPC框架
- Seata：一个易于使用的高性能微服务分布式事务解决方案
- Alibaba Cloud OOS：阿里云对象存储（Object Storage Service，简称OOS），是阿里云提供的海量，安全，低成本，高可靠的云存储服务，您可以在任何应用，任何时间，任何地点存储和访问任意类型的数据。
- Alibaba Cloud SchedulerX：阿里中间件团队开发的一款分布式任务调度产品，支持周期的任务与固定时间点触发
## Nacos简介
Nacos服务注册和配置中心，兼顾两种
### 为什么叫Nacos
前四个字母分别为：Naming（服务注册） 和 Configuration（配置中心） 的前两个字母，后面的s 是 Service
### 是什么
一个更易于构建云原生应用的动态服务发现，配置管理和服务
Nacos：Dynamic Naming and Configuration Server
Nacos就是注册中心 + 配置中心的组合
等价于：Nacos = Eureka + Config
### 能干嘛
替代Eureka做服务注册中心
替代Config做服务配置中心
### 下载
官网：https://github.com/alibaba/nacos
nacos文档：https://nacos.io/zh-cn/docs/what-is-nacos.html
### 比较
![image-20200414165716292](images/image-20200414165716292.png)
Nacos在阿里巴巴内部有超过10万的实例运行，已经过了类似双十一等各种大型流量的考验
### 安装并运行
本地需要 java8 + Maven环境
下载：[地址](https://github.com/alibaba/nacos/releases/tag/1.1.4)
github经常抽风，可以使用：https://blog.csdn.net/buyaopa/article/details/104582141
解压后：运行bin目录下的：startup.cmd
打开：`http://localhost:8848/nacos`
结果页面
![image-20200414181458943](images/image-20200414181458943.png)
## Nacos作为服务注册中心
### 服务提供者注册Nacos
#### 引入依赖
```
    com.alibaba.cloud
    spring-cloud-starter-alibaba-nacos-discovery
```
#### 修改yml
```
server:
  port: 9002
spring:
  application:
    name: nacos-payment-provider
  cloud:
    nacos:
      discovery:
        server-addr: 127.0.0.1:8848   # 配置nacos地址
management:
  endpoints:
    web:
      exposure:
        include: '*'
```
#### 主启动类
添加 `@EnableDiscoveryClient` 注解
```
@SpringBootApplication
@EnableDiscoveryClient
public class PaymentMain9002 {
    public static void main(String[] args) {
        SpringApplication.run(PaymentMain9002.class);
    }
}
```
#### 业务类
```
@RestController
public class PaymentController {
    @Value("${server.port}")
    private String serverPort;
    @GetMapping("/payment/nacos/{id}")
    public String getPayment(@PathVariable("id") Integer id) {
        return "nacos registry ,serverPore:"+serverPort+"\t id:"+id;
    }
}
```
#### 启动
nacos-payment-provider已经成功注册了
![image-20200414182221528](images/image-20200414182221528.png)
这个时候 nacos服务注册中心 + 服务提供者 9001 都OK了
通过IDEA的拷贝映射
![image-20200414215206684](images/image-20200414215206684.png)
添加
```
-DServer.port=9003
```
![image-20200414215128701](images/image-20200414215128701.png)
最后能够看到两个实例
![image-20200414215440351](images/image-20200414215440351.png)
![image-20200414215621673](images/image-20200414215621673.png)
### 服务消费者注册到Nacos
Nacos天生集成了Ribbon，因此它就具备负载均衡的能力
#### 引入依赖
```
    com.alibaba.cloud
    spring-cloud-starter-alibaba-nacos-discovery
```
#### 修改yml
```
server:
  port: 83
spring:
  application:
    name: nacos-order-consumer
  cloud:
    nacos:
      discovery:
        server-addr: localhost:8848
# 消费者将要去访问的微服务名称（注册成功进nacos的微服务提供者）
service-url:
  nacos-user-service: http://nacos-payment-provider
```
#### 增加配置类
因为nacos集成了Ribbon，因此需要配置RestTemplate，同时通过注解 `@LoadBalanced`实现负载均衡，默认是轮询的方式
```
@Configuration
public class ApplicationContextConfig {
    @Bean
    @LoadBalanced
    public RestTemplate getRestTemple() {
        return new RestTemplate();
    }
}
```
#### 业务类
```
@RestController
@Slf4j
public class OrderNacosController {
    @Resource
    private RestTemplate restTemplate;
    @Value("${service-url.nacos-user-service}")
    private String serverURL;
    @GetMapping(value = "/consumer/payment/nacos/{id}")
    public String paymentInfo(@PathVariable("id")Long id){
       return restTemplate.getForObject(serverURL+"/payment/nacos/" + id, String.class);
    }
}
```
测试
```
http://localhost:83/consumer/payment/nacos/13
```
得到的结果
```
nacos registry ,serverPore:9001 id:13
nacos registry ,serverPore:9002 id:13
```
我们发现只需要配置了nacos，就轻松实现负载均衡
### 服务中心对比
之前我们提到的注册中心对比图
![image-20200415193857281](images/image-20200415193857281.png)
但是其实Nacos不仅支持AP，而且还支持CP，它的支持模式是可以切换的，我们首先看看Spring Cloud Alibaba的全景图，
![image-20200415194047564](images/image-20200415194047564.png)
#### Nacos和CAP
CAP：分别是一致性，可用性，分容容忍
![image-20200415194123634](images/image-20200415194123634.png)
我们从下图能够看到，nacos不仅能够和Dubbo整合，还能和K8s，也就是偏运维的方向
![image-20200415194203594](images/image-20200415194203594.png)
#### Nacos支持AP和CP切换
C是指所有的节点同一时间看到的数据是一致的，而A的定义是所有的请求都会收到响应
合适选择何种模式？
一般来说，如果不需要存储服务级别的信息且服务实例是通过nacos-client注册，并能够保持心跳上报，那么就可以选择AP模式。当前主流的服务如Spring Cloud 和 Dubbo服务，都是适合AP模式，AP模式为了服务的可用性而减弱了一致性，因此AP模式下只支持注册临时实例。
如果需要在服务级别编辑或存储配置信息，那么CP是必须，K8S服务和DNS服务则适用于CP模式。
CP模式下则支持注册持久化实例，此时则是以Raft协议为集群运行模式，该模式下注册实例之前必须先注册服务，如果服务不存在，则会返回错误。
## Nacos作为服务配置中心演示
我们将我们的配置写入Nacos，然后以Spring Cloud Config的方式，用于抓取配置
### Nacos作为配置中心 - 基础配置
#### 引入依赖
```
    com.alibaba.cloud
    spring-cloud-starter-alibaba-nacos-config
```
#### 修改YML
Nacos同SpringCloud Config一样，在项目初始化时，要保证先从配置中心进行配置拉取，拉取配置之后，才能保证项目的正常运行。
SpringBoot中配置文件的加载是存在优先级顺序的：bootstrap优先级 高于 application
**application.yml配置**
```
spring:
  profiles:
 #   active: dev # 开发环境
 #   active: test # 测试环境
    active: info # 开发环境
```
**bootstrap.yml配置**
```
server:
  port: 3377
spring:
  application:
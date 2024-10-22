- Tracer定义统计
- ContextUtil定义了上下文
## 服务熔断
sentinel整合Ribbon + openFeign + fallback
搭建 9003 和 9004 服务提供者
### 不设置任何参数
然后在使用 84作为服务消费者，当我们值使用 `@SentinelResource`注解时，不添加任何参数，那么如果出错的话，是直接返回一个error页面，对前端用户非常不友好，因此我们需要配置一个兜底的方法
```
    @RequestMapping("/consumer/fallback/{id}")
    @SentinelResource(value = "fallback") //没有配置
    public CommonResult fallback(@PathVariable Long id)
    {
        CommonResult result = restTemplate.getForObject(SERVICE_URL + "/paymentSQL/"+id,CommonResult.class,id);
        if (id == 4) {
            throw new IllegalArgumentException ("IllegalArgumentException,非法参数异常....");
        }else if (result.getData() == null) {
            throw new NullPointerException ("NullPointerException,该ID没有对应记录,空指针异常");
        }
        return result;
    }
```
### 设置fallback
```
    @RequestMapping("/consumer/fallback/{id}")
    @SentinelResource(value = "fallback",fallback = "handlerFallback") //fallback只负责业务异常
    public CommonResult fallback(@PathVariable Long id)
    {
        CommonResult result = restTemplate.getForObject(SERVICE_URL + "/paymentSQL/"+id,CommonResult.class,id);
        if (id == 4) {
            throw new IllegalArgumentException ("IllegalArgumentException,非法参数异常....");
        }else if (result.getData() == null) {
            throw new NullPointerException ("NullPointerException,该ID没有对应记录,空指针异常");
        }
        return result;
    }
    //本例是fallback
    public CommonResult handlerFallback(@PathVariable  Long id,Throwable e) {
        Payment payment = new Payment(id,"null");
        return new CommonResult<>(444,"兜底异常handlerFallback,exception内容  "+e.getMessage(),payment);
    }
```
加入fallback后，当我们程序运行出错时，我们会有一个兜底的异常执行，但是服务限流和熔断的异常还是出现默认的
### 设置blockHandler
```
    @RequestMapping("/consumer/fallback/{id}")
    @SentinelResource(value = "fallback",blockHandler = "blockHandler" ,fallback = "handlerFallback") //blockHandler只负责sentinel控制台配置违规
    public CommonResult fallback(@PathVariable Long id)
    {
        CommonResult result = restTemplate.getForObject(SERVICE_URL + "/paymentSQL/"+id,CommonResult.class,id);
        if (id == 4) {
            throw new IllegalArgumentException ("IllegalArgumentException,非法参数异常....");
        }else if (result.getData() == null) {
            throw new NullPointerException ("NullPointerException,该ID没有对应记录,空指针异常");
        }
        return result;
    }
    //本例是blockHandler
    public CommonResult blockHandler(@PathVariable  Long id,BlockException blockException) {
        Payment payment = new Payment(id,"null");
        return new CommonResult<>(445,"blockHandler-sentinel限流,无此流水: blockException  "+blockException.getMessage(),payment);
    }
```
### blockHandler和fallback一起配置
```
    @RequestMapping("/consumer/fallback/{id}")
    @SentinelResource(value = "fallback",blockHandler = "blockHandler") //blockHandler只负责sentinel控制台配置违规
    public CommonResult fallback(@PathVariable Long id)
    {
        CommonResult result = restTemplate.getForObject(SERVICE_URL + "/paymentSQL/"+id,CommonResult.class,id);
        if (id == 4) {
            throw new IllegalArgumentException ("IllegalArgumentException,非法参数异常....");
        }else if (result.getData() == null) {
            throw new NullPointerException ("NullPointerException,该ID没有对应记录,空指针异常");
        }
        return result;
    }
```
若blockHandler 和 fallback都进行了配置，则被限流降级而抛出 BlockException时，只会进入blockHandler处理逻辑
### 异常忽略
![image-20200416213834495](images/image-20200416213834495.png)
## Feign系列
#### 引入依赖
```
    org.springframework.cloud
    spring-cloud-starter-openfeign
```
#### 修改YML
```
server:
  port: 84
spring:
  application:
    name: nacos-order-consumer
  cloud:
    nacos:
      discovery:
        server-addr: localhost:8848
    sentinel:
      transport:
        #配置Sentinel dashboard地址
        dashboard: localhost:8080
        #默认8719端口，假如被占用会自动从8719开始依次+1扫描,直至找到未被占用的端口
        port: 8719
#消费者将要去访问的微服务名称(注册成功进nacos的微服务提供者)
service-url:
  nacos-user-service: http://nacos-payment-provider
# 激活Sentinel对Feign的支持
feign:
  sentinel:
    enabled: true
```
#### 启动类激活Feign
```
@EnableDiscoveryClient
@SpringBootApplication
@EnableFeignClients
public class OrderNacosMain84
{
    public static void main(String[] args) {
        SpringApplication.run(OrderNacosMain84.class, args);
    }
}
```
#### 引入Feign接口
```
@FeignClient(value = "nacos-payment-provider",fallback = PaymentFallbackService.class)
public interface PaymentService
{
    @GetMapping(value = "/paymentSQL/{id}")
    public CommonResult paymentSQL(@PathVariable("id") Long id);
}
```
#### 加入fallback兜底方法实现
```
@Component
public class PaymentFallbackService implements PaymentService
{
    @Override
    public CommonResult paymentSQL(Long id)
    {
        return new CommonResult<>(44444,"服务降级返回,---PaymentFallbackService",new Payment(id,"errorSerial"));
    }
}
```
#### 测试
请求接口：`http://localhost:84/consumer/paymentSQL/1`
测试84调用9003，此时故意关闭9003微服务提供者，看84消费侧自动降级
我们发现过了一段时间后，会触发服务降级，返回失败的方法
## 熔断框架对比
![image-20200416215711875](images/image-20200416215711875.png)
## Sentinel规则持久化
### 是什么
一旦我们重启应用，sentinel规则将会消失，生产环境需要将规则进行持久化
### 怎么玩
将限流配置规则持久化进Nacos保存，只要刷新8401某个rest地址，sentinel控制台的流控规则就能看到，只要Nacos里面的配置不删除，针对8401上的流控规则持续有效
### 解决方法
使用nacos持久化保存
#### 引入依赖
```
    com.alibaba.csp
    sentinel-datasource-nacos
```
#### 修改yml
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
      datasource:
        ds1:
          nacos:
            server-addr: localhost:8848
            dataId: cloudalibaba-sentinel-service
            groupId: DEFAULT_GROUP
            data-type: json
            rule-type: flow
management:
  endpoints:
    web:
      exposure:
        include: '*'
feign:
  sentinel:
    enabled: true # 激活Sentinel对Feign的支持
```
#### 添加nacos配置
![image-20200416222218661](images/image-20200416222218661.png)
内容解析
![image-20200416222317824](images/image-20200416222317824.png)
- resource：资源名称
- limitApp：来源应用
- grade：阈值类型，0表示线程数，1表示QPS
- count：单机阈值
- strategy：流控模式，0表示直接，1表示关联，2表示链路
- controlBehavior：流控效果，0表示快速失败，1表示Warm，2表示排队等待
- clusterMode：是否集群
这样启动的时候，调用一下接口，我们的限流规则就会重新出现~
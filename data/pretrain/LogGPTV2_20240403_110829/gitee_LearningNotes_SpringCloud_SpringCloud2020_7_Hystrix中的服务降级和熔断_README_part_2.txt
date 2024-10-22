**方法1：**
除了个别重要核心业务有专属，其它普通的可以通过`@DefaultProperties(defaultFallback = "")`，这样通用的和独享的各自分开，避免了代码膨胀，合理减少了代码量
可以在Controller处设置 `@DefaultProperties(defaultFallback = "payment_Global_FallbackMethod")`
```
@RestController
@Slf4j
@DefaultProperties(defaultFallback = "payment_Global_FallbackMethod")
public class OrderHystrixController {
    @GetMapping("/consumer/payment/hystrix/timeout/{id}")
    @HystrixCommand  // 这个方法也会走全局 fallback
    public String paymentInfo_TimeOut(@PathVariable("id") Integer id) {
        int age = 10/0; //方法前挂了，跟后面挂了两种
        return paymentHystrixService.paymentInfo_TimeOut(id);
    }
    //下面是全局fallback方法
    public String payment_Global_FallbackMethod(){
        return "Global异常处理信息，请稍后再试,/(ㄒoㄒ)/~~";
    }
}
```
**方法2：**
我们现在还发现，兜底的方法 和 我们的业务代码耦合在一块比较混乱
我们可以在feign调用的时候，增加hystrix的服务降级处理的实现类，这样就可以进行解耦
格式：`@FeignClient(fallback = PaymentFallbackService.class)`
我们要面对的异常主要有
- 运行
- 超时
- 宕机
需要新建一个FallbackService实现类，然后通过实现类统一为feign接口里面的方法进行异常处理
feign接口
```
@Component
@FeignClient(value = "cloud-provider-hystrix-payment", fallback = PaymentFallbackService.class)
public interface PaymentHystrixService {
    /**
     * 正常访问
     *
     * @param id
     * @return
     */
    @GetMapping("/payment/hystrix/ok/{id}")
    public String paymentInfo_OK(@PathVariable("id") Integer id);
    /**
     * 超时访问
     *
     * @param id
     * @return
     */
    @GetMapping("/payment/hystrix/timeout/{id}")
    public String paymentInfo_TimeOut(@PathVariable("id") Integer id);
}
```
实现类
```
@Component
public class PaymentFallbackService implements PaymentHystrixService {
    @Override
    public String paymentInfo_OK(Integer id) {
        return "--- PaymentFallbackService  fall  paymentInfo_OK vack ，/(ㄒoㄒ)/~~";
    }
    @Override
    public String paymentInfo_TimeOut(Integer id) {
        return "--- PaymentFallbackService  fall  paymentInfo_TimeOut， /(ㄒoㄒ)/~~";
    }
}
```
这个时候，如果我们将服务提供方进行关闭，但是我们在客户端做了服务降级处理，让客户端在服务端不可用时，也会获得提示信息，而不会挂起耗死服务器
### 服务熔断
服务熔断也是服务降级的一个 特例
#### 熔断概念
熔断机制是应对雪崩效应的一种微服务链路保护机制，当扇出链路的某个微服务不可用或者响应时间太长时，会进行服务的降级，进而熔断该节点微服务的调用，快速返回错误的响应状态
当检测到该节点微服务调用响应正常后，恢复调用链路
在Spring Cloud框架里，熔断机制通过Hystrix实现，Hystrix会监控微服务间调用的状况，当失败的调用到一定的阈值，缺省是5秒内20次调用失败，就会启动熔断机制，熔断机制的注解还是 `@HystrixCommand`
来源，微服务提出者马丁福勒：https://martinfowler.com/bliki/CircuitBreaker.html
>这个简单的断路器避免了在电路打开时进行保护调用，但是当情况恢复正常时需要外部干预来重置它。对于建筑物中的断路器，这是一种合理的方法，但是对于软件断路器，我们可以让断路器本身检测底层调用是否再次工作。我们可以通过在适当的间隔之后再次尝试protected调用来实现这种自重置行为，并在断路器成功时重置它
![image-20200409095855788](images/image-20200409095855788.png)
熔断器的三种状态：打开，关闭，半开
这里提出了 半开的概念，首先打开一半的，然后慢慢的进行恢复，最后在把断路器关闭
降级 -> 熔断 -> 恢复
这里我们在服务提供方 8001，增加服务熔断
这里有四个字段
```
// 是否开启断路器
@HystrixProperty(name = "circuitBreaker.enabled", value = "true"),
// 请求次数
@HystrixProperty(name = "circuitBreaker.requestVolumeThreshold", value = "10"),
// 时间窗口期/时间范文
@HystrixProperty(name = "circuitBreaker.sleepWindowInMilliseconds", value = "10000"),
// 失败率达到多少后跳闸
@HystrixProperty(name = "circuitBreaker.errorThresholdPercentage", value = "60")
```
首先是是否开启熔断器，然后是在一个时间窗口内，有60%的失败，那么就启动断路器，也就是10次里面，6次失败，完整代码如下：
```
    /**
     * 在10秒窗口期中10次请求有6次是请求失败的,断路器将起作用
     * @param id
     * @return
     */
    @HystrixCommand(
            fallbackMethod = "paymentCircuitBreaker_fallback", commandProperties = {
            @HystrixProperty(name = "circuitBreaker.enabled", value = "true"),// 是否开启断路器
            @HystrixProperty(name = "circuitBreaker.requestVolumeThreshold", value = "10"),// 请求次数
            @HystrixProperty(name = "circuitBreaker.sleepWindowInMilliseconds", value = "10000"),// 时间窗口期/时间范文
            @HystrixProperty(name = "circuitBreaker.errorThresholdPercentage", value = "60")// 失败率达到多少后跳闸
    }
    )
    public String paymentCircuitBreaker(@PathVariable("id") Integer id) {
        if (id 
    org.springframework.cloud
    spring-cloud-starter-netflix-hystrix-dashboard
    org.springframework.boot
    spring-boot-starter-actuator
```
application.yml添加端口
```
server:
  port: 9001
```
主启动类：配置注解`@EnableHystrixDashboard`
```
@SpringBootApplication
@EnableHystrixDashboard
public class HystrixDashboardMain9001 {
    public static void main(String[] args) {
        SpringApplication.run(HystrixDashboardMain9001.class);
    }
}
```
同时，最后我们需要注意，每个服务类想要被监控的，都需要在pom文件中，添加一下注解
```
    org.springframework.boot
    spring-boot-starter-actuator
```
同时在服务提供者的启动类上，需要添加以下的内容
```
@SpringBootApplication
@EnableDiscoveryClient
@EnableCircuitBreaker
public class PaymentHystrixMain8001 {
    public static void main(String[] args) {
        SpringApplication.run(PaymentHystrixMain8001.class, args);
    }
    /**
     * 此配置是为了服务监控而配置，与服务容错本身无观，springCloud 升级之后的坑
     * ServletRegistrationBean因为springboot的默认路径不是/hystrix.stream
     * 只要在自己的项目中配置上下面的servlet即可
     * @return
     */
    @Bean
    public ServletRegistrationBean getServlet(){
        HystrixMetricsStreamServlet streamServlet = new HystrixMetricsStreamServlet();
        ServletRegistrationBean registrationBean = new ServletRegistrationBean<>(streamServlet);
        registrationBean.setLoadOnStartup(1);
        registrationBean.addUrlMappings("/hystrix.stream");
        registrationBean.setName("HystrixMetricsStreamServlet");
        return registrationBean;
    }
}
```
输入以下地址，进入Hystrix的图形化界面
```
http://localhost:9001/hystrix
```
![image-20200409121425718](images/image-20200409121425718.png)
### 使用监控
我们需要使用当前hystrix需要监控的端口号，也就是使用 9001 去监控 8001，即使用hystrix dashboard去监控服务提供者的端口号
![image-20200409122102137](images/image-20200409122102137.png)
然后我们运行
```
http://localhost:8001/payment/circuit/31
```
就能够发现Hystrix Dashboard能够检测到我们的请求
![image-20200409122312059](images/image-20200409122312059.png)
假设我们访问错误的方法后
```
http://localhost:8001/payment/circuit/-31
```
我们能够发现，此时断路器处于开启状态，并且错误率百分100
![image-20200409122448651](images/image-20200409122448651.png)
如何看懂图
首先是七种颜色
![image-20200409122754448](images/image-20200409122754448.png)
每个颜色都对应的一种结果
![image-20200409122820328](images/image-20200409122820328.png)
然后是里面的圆
实心圆：共有两种含义。它通过颜色的变化代表了实例的健康程度，它的健康程度从
绿色 < 黄色 < 橙色 <红色，递减
该实心圆除了颜色变化之外，它的大小也会根据实例的请求流量发生变化，流量越大该实心圆就越大，所以通过该实心圆的展示，就可以快速在大量的实例中快速发现故障实例和高压力实例
曲线：用于记录2分钟内流量的相对变化，可以通过它来观察到流量的上升和下降趋势
![image-20200409123214743](images/image-20200409123214743.png)
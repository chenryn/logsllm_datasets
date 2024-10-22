## 降级规则
### 名词介绍
![image-20200416095515859](images/image-20200416095515859.png)
- RT（平均响应时间，秒级）
  - 平均响应时间，超过阈值 且 时间窗口内通过的请求 >= 5，两个条件同时满足后出发降级
  - 窗口期过后，关闭断路器
  - RT最大4900（更大的需要通过 -Dcsp.sentinel.staticstic.max.rt=XXXXX才能生效）
- 异常比例（秒级）
  - QPA >= 5 且异常比例（秒级）超过阈值时，触发降级；时间窗口结束后，关闭降级
- 异常数（分钟级）
  - 异常数（分钟统计）超过阈值时，触发降级，时间窗口结束后，关闭降级
### 概念
Sentinel熔断降级会在调用链路中某个资源出现不稳定状态时（例如调用超时或异常异常比例升高），对这个资源的调用进行限制，让请求快速失败，避免影响到其它的资源而导致级联错误。
当资源被降级后，在接下来的降级时间窗口之内，对该资源的调用都进行自动熔断（默认行为是抛出DegradeException）
Sentinel的断路器是没有半开状态
半开的状态，系统自动去检测是否请求有异常，没有异常就关闭断路器恢复使用，有异常则继续打开断路器不可用，具体可以参考hystrix
![image-20200416100340083](images/image-20200416100340083.png)
### 降级策略实战
#### RT
平均响应时间 (`DEGRADE_GRADE_RT`)：当 1s 内持续进入 N 个请求，对应时刻的平均响应时间（秒级）均超过阈值（`count`，以 ms 为单位），那么在接下的时间窗口（`DegradeRule` 中的 `timeWindow`，以 s 为单位）之内，对这个方法的调用都会自动地熔断（抛出 `DegradeException`）。注意 Sentinel 默认统计的 RT 上限是 4900 ms，**超出此阈值的都会算作 4900 ms**，若需要变更此上限可以通过启动配置项 `-Dcsp.sentinel.statistic.max.rt=xxx` 来配置。
![image-20200416102754797](images/image-20200416102754797.png)
代码测试
```
    @GetMapping("/testD")
    public String testD()
    {
        try { TimeUnit.SECONDS.sleep(1); } catch (InterruptedException e) { e.printStackTrace(); }
        log.info("testD 异常比例");
        return "------testD";
    }
```
然后使用Jmeter压力测试工具进行测试
![image-20200416103619799](images/image-20200416103619799.png)
按照上述操作，永远1秒种打进来10个线程，大于5个了，调用tesetD，我们希望200毫秒内处理完本次任务，如果200毫秒没有处理完，在未来的1秒的时间窗口内，断路器打开（保险丝跳闸）微服务不可用，保险丝跳闸断电
```
Blocked by Sentinel (flow limiting)
```
![image-20200416103959047](images/image-20200416103959047.png)
后续我们停止使用jmeter，没有那么大的访问量了，断路器关闭（保险丝恢复），微服务恢复OK
#### 异常比例
异常比例 (`DEGRADE_GRADE_EXCEPTION_RATIO`)：当资源的每秒请求量 >= N（可配置），并且每秒异常总数占通过量的比值超过阈值（`DegradeRule` 中的 `count`）之后，资源进入降级状态，即在接下的时间窗口（`DegradeRule` 中的 `timeWindow`，以 s 为单位）之内，对这个方法的调用都会自动地返回。异常比率的阈值范围是 `[0.0, 1.0]`，代表 0% - 100%。
![image-20200416104157714](images/image-20200416104157714.png)
单独访问一次，必然来一次报错一次，开启jmeter后，直接高并发发送请求，多次调用达到我们的配置条件了，断路器开启（保险丝跳闸），微服务不可用，不在报错，而是服务降级了
![image-20200416104919798](images/image-20200416104919798.png)
设置3秒内，如果请求百分50出错，那么就会熔断
![image-20200416104908479](images/image-20200416104908479.png)
我们用jmeter每秒发送10次请求，3秒后，再次调用  `localhost:8401/testD` 出现服务降级
![image-20200416104858019](images/image-20200416104858019.png)
#### 异常数
异常数 (`DEGRADE_GRADE_EXCEPTION_COUNT`)：当资源近 1 分钟的异常数目超过阈值之后会进行熔断。注意由于统计时间窗口是分钟级别的，若 `timeWindow` 小于 60s，则结束熔断状态后仍可能再进入熔断状态
时间窗口一定要大于等于60秒
异常数是按分钟来统计的
![image-20200416105132256](images/image-20200416105132256.png)
下面设置是，一分钟内出现5次，则熔断
![image-20200416105535535](images/image-20200416105535535.png)
首先我们再次访问 `http://localhost:8401/testE`，第一次访问绝对报错，因为除数不能为0，我们看到error窗口，但是达到5次报错后，进入熔断后的降级
## Sentinel热点规则
### 什么是热点数据
[Github文档传送门](https://github.com/alibaba/Sentinel/wiki/%E7%83%AD%E7%82%B9%E5%8F%82%E6%95%B0%E9%99%90%E6%B5%81)
何为热点？热点即经常访问的数据。很多时候我们希望统计某个热点数据中访问频次最高的 Top K 数据，并对其访问进行限制。比如：
- 商品 ID 为参数，统计一段时间内最常购买的商品 ID 并进行限制
- 用户 ID 为参数，针对一段时间内频繁访问的用户 ID 进行限制
热点参数限流会统计传入参数中的热点参数，并根据配置的限流阈值与模式，对包含热点参数的资源调用进行限流。热点参数限流可以看做是一种特殊的流量控制，仅对包含热点参数的资源调用生效。
![image-20200416121306501](images/image-20200416121306501.png)
Sentinel 利用 LRU 策略统计最近最常访问的热点参数，结合令牌桶算法来进行参数级别的流控。热点参数限流支持集群模式。
### 兜底的方法
分为系统默认的和客户自定义的，两种，之前的case中，限流出现问题了，都用sentinel系统默认的提示：Blocked By Sentinel，我们能不能自定义，类似于hystrix，某个方法出现问题了，就找到对应的兜底降级方法。
从 `@HystrixCommand` 到 `@SentinelResource`
### 配置
@SentinelResource的value，就是我们的资源名，也就是对哪个方法配置热点规则
```
    @GetMapping("/testHotKey")
    @SentinelResource(value = "testHotKey",blockHandler = "deal_testHotKey")
    public String testHotKey(@RequestParam(value = "p1",required = false) String p1,
                             @RequestParam(value = "p2",required = false) String p2)
    {
        //int age = 10/0;
        return "------testHotKey";
    }
    // 和上面的参数一样，不错需要加入 BlockException
    public String deal_testHotKey (String p1, String p2, BlockException exception)
    {
        return "------deal_testHotKey,o(╥﹏╥)o";  //  兜底的方法
    }
```
我们对参数0，设置热点key进行限流
![image-20200416122406091](images/image-20200416122406091.png)
配置完成后
![image-20200416122450886](images/image-20200416122450886.png)
当我们不断的请求时候，也就是以第一个参数为目标，请求接口，我们会发现多次请求后
```
http://localhost:8401/testHotKey?p1=a
```
就会出现以下的兜底错误
```
------deal_testHotKey,o(╥﹏╥)o
```
这是因为我们针对第一个参数进行了限制，当我们QPS超过1的时候，就会触发兜底的错误
假设我们请求的接口是：`http://localhost:8401/testHotKey?p2=a` ，我们会发现他就没有进行限流
![image-20200416123605410](images/image-20200416123605410.png)
### 参数例外项
上述案例演示了第一个参数p1，当QPS超过1秒1次点击狗，马上被限流
- 普通：超过一秒1个后，达到阈值1后马上被限流
- 我们期望p1参数当它达到某个特殊值时，它的限流值和平时不一样
- 特例：假设当p1的值等于5时，它的阈值可以达到200
- 一句话说：当key为特殊值的时候，不被限制
![image-20200416123922325](images/image-20200416123922325.png)
平时的时候，参数1的QPS是1，超过的时候被限流，但是有特殊值，比如5，那么它的阈值就是200
我们通过 `http://localhost:8401/testHotKey?p1=5` 一直刷新，发现不会触发兜底的方法，这就是参数例外项
热点参数的注意点，参数必须是基本类型或者String
### 结语
`@SentinelResource` 处理的是Sentinel控制台配置的违规情况，有blockHandler方法配置的兜底处理
RuntimeException，如  int a = 10/0 ; 这个是java运行时抛出的异常，RuntimeException，@RentinelResource不管
也就是说：`@SentinelResource` 主管配置出错，运行出错不管。
如果想要有配置出错，和运行出错的话，那么可以设置 fallback
```
    @GetMapping("/testHotKey")
    @SentinelResource(value = "testHotKey",blockHandler = "deal_testHotKey", fallback = "fallBack")
    public String testHotKey(@RequestParam(value = "p1",required = false) String p1,
                             @RequestParam(value = "p2",required = false) String p2)
    {
        //int age = 10/0;
        return "------testHotKey";
    }
```
## Sentinel系统配置
Sentinel 系统自适应限流从整体维度对应用入口流量进行控制，结合应用的 Load、CPU 使用率、总体平均 RT、入口 QPS 和并发线程数等几个维度的监控指标，通过自适应的流控策略，让系统的入口流量和系统的负载达到一个平衡，让系统尽可能跑在最大吞吐量的同时保证系统整体的稳定性。
系统保护规则是从应用级别的入口流量进行控制，从单台机器的 load、CPU 使用率、平均 RT、入口 QPS 和并发线程数等几个维度监控应用指标，让系统尽可能跑在最大吞吐量的同时保证系统整体的稳定性。
系统保护规则是应用整体维度的，而不是资源维度的，并且**仅对入口流量生效**。入口流量指的是进入应用的流量（`EntryType.IN`），比如 Web 服务或 Dubbo 服务端接收的请求，都属于入口流量。
系统规则支持以下的模式：
- **Load 自适应**（仅对 Linux/Unix-like 机器生效）：系统的 load1 作为启发指标，进行自适应系统保护。当系统 load1 超过设定的启发值，且系统当前的并发线程数超过估算的系统容量时才会触发系统保护（BBR 阶段）。系统容量由系统的 `maxQps * minRt` 估算得出。设定参考值一般是 `CPU cores * 2.5`。
- **CPU usage**（1.5.0+ 版本）：当系统 CPU 使用率超过阈值即触发系统保护（取值范围 0.0-1.0），比较灵敏。
- **平均 RT**：当单台机器上所有入口流量的平均 RT 达到阈值即触发系统保护，单位是毫秒。
- **并发线程数**：当单台机器上所有入口流量的并发线程数达到阈值即触发系统保护。
- **入口 QPS**：当单台机器上所有入口流量的 QPS 达到阈值即触发系统保护。
![image-20200416144836658](images/image-20200416144836658.png)
这样相当于设置了全局的QPS过滤
## @SentinelResource注解
- 按资源名称限流 + 后续处理
- 按URL地址限流 + 后续处理
### 问题
- 系统默认的，没有体现我们自己的业务要求
- 依照现有条件，我们自定义的处理方法又和业务代码耦合在一块，不直观
- 每个业务方法都添加一个兜底方法，那代码膨胀加剧
- 全局统一的处理方法没有体现
- 关闭8401，发现流控规则已经消失，说明这个是没有持久化
### 客户自定义限流处理逻辑
创建CustomerBlockHandler类用于自定义限流处理逻辑
```
public class CustomerBlockHandler
{
    public static CommonResult handlerException(BlockException exception)
    {
        return new CommonResult(4444,"按客户自定义,global handlerException----1");
    }
    public static CommonResult handlerException2(BlockException exception)
    {
        return new CommonResult(4444,"按客户自定义,global handlerException----2");
    }
}
```
那么我们在使用的时候，就可以首先指定是哪个类，哪个方法
```
    @GetMapping("/rateLimit/customerBlockHandler")
    @SentinelResource(value = "customerBlockHandler",
            blockHandlerClass = CustomerBlockHandler.class,
            blockHandler = "handlerException2")
    public CommonResult customerBlockHandler()
    {
        return new CommonResult(200,"按客户自定义",new Payment(2020L,"serial003"));
    }
```
![image-20200416150947457](images/image-20200416150947457.png)
### 更多注解属性说明
所有的代码都要用try - catch - finally 进行处理
sentinel主要有三个核心API
- Sphu定义资源
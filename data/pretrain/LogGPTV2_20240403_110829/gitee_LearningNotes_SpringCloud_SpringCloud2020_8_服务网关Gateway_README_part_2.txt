```
http://localhost:8001/payment/get/31
```
添加网关之后，我们的访问路径是
```
http://localhost:9527/payment/get/31
```
这么做的好处是慢慢淡化我们真实的IP端口号
### 路由匹配
![image-20200409154741550](images/image-20200409154741550.png)
### 路由配置的两种方式
- 在配置文件yml中配置
- 代码中注入RouteLocator的Bean
```
@Configuration
public class GateWayConfig {
	// 配置了一个id为route-name的路由规则，当访问地址 http://localhost:9527/guonei时，会自动转发到
	// 地址 http;//news.baidu.com/guonei
    @Bean
    public RouteLocator customRouteLocator(RouteLocatorBuilder routeLocatorBuilder){
        RouteLocatorBuilder.Builder routes = routeLocatorBuilder.routes();
        routes.route("path route atguigu",
                r ->r.path("/guonei").uri("https://www.baidu.com")).build();
        return routes.build();
    }
}
```
## 通过微服务名实现动态路由
默认情况下Gateway会根据注册中心的服务列表，以注册中心上微服务名为路径创建动态路由进行转发，从而实现动态路由的功能。
首先需要开启从注册中心动态创建路由的功能，利用微服务名进行路由
```
spring:
  application:
    name: cloud-gateway
  cloud:
    gateway:
      discovery:
        locator:
          enabled: true # 开启从注册中心动态创建路由的功能，利用微服务名称进行路由
```
URL换成服务名
```
uri: lb://CLOUD-PAYMENT-SERVICE
```
## Predicate的使用
### 概念
断言，路径相匹配的进行路由
![image-20200409160651792](images/image-20200409160651792.png)
Spring Cloud Gateway将路由匹配作为Spring WebFlux HandlerMapping基础架构的一部分
Spring Cloud Gateway包括许多内置的Route Predicate 工厂，所有这些Predicate都与Http请求的不同属性相匹配，多个Route Predicate工厂可以进行组合
Spring Cloud Gateway创建Route对象时，使用RoutePredicateFactory创建Predicate对象，Predicate对象可以赋值给Route，SpringCloudGateway包含许多内置的RoutePredicateFactores。
所有这些谓词都匹配Http请求的不同属性。多种谓词工厂可以组合，并通过逻辑 and
![image-20200409161216925](images/image-20200409161216925.png)
### 常用的Predicate
- After Route Predicate：在什么时间之后执行
  ![image-20200409161713254](images/image-20200409161713254.png)
- Before Route Predicate：在什么时间之前执行
- Between Route Predicate：在什么时间之间执行
- Cookie  Route Predicate：Cookie级别
  常用的测试工具：
  - jmeter
  - postman
  - curl
  ```
  // curl命令进行测试，携带Cookie
  curl http://localhost:9527/payment/lb --cookie "username=zzyy"
  ```
- Header  Route Predicate：携带请求头
- Host  Route Predicate：什么样的URL路径过来
- Method  Route Predicate：什么方法请求的，Post，Get
- Path  Route Predicate：请求什么路径 	`- Path=/api-web/**`
- Query  Route Predicate：带有什么参数的
## Filter的使用
### 概念
路由过滤器可用于修改进入的HTTP请求和返回的HTTP响应，路由过滤器只能指定路由进行使用
Spring Cloud Gateway内置了多种路由过滤器，他们都由GatewayFilter的工厂类来产生的
### Spring Cloud Gateway Filter
生命周期：only Two：pre，Post
种类：Only Two
- GatewayFilter
- GlobalFilter
### 自定义过滤器
主要作用：
- 全局日志记录
- 统一网关鉴权
需要实现接口：`implements GlobalFilter, Ordered`
全局过滤器代码如下：
```
@Component
@Slf4j
public class MyLogGateWayFilter implements GlobalFilter, Ordered {
    @Override
    public Mono filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        log.info("come in global filter: {}", new Date());
        ServerHttpRequest request = exchange.getRequest();
        String uname = request.getQueryParams().getFirst("uname");
        if (uname == null) {
            log.info("用户名为null，非法用户");
            exchange.getResponse().setStatusCode(HttpStatus.NOT_ACCEPTABLE);
            return exchange.getResponse().setComplete();
        }
        // 放行
        return chain.filter(exchange);
    }
    /**
     * 过滤器加载的顺序 越小,优先级别越高
     *
     * @return
     */
    @Override
    public int getOrder() {
        return 0;
    }
}
```
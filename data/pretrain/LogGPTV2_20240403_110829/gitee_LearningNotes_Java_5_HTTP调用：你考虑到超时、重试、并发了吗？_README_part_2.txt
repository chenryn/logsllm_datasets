修改配置后重试，得到如下日志：
```
[15:43:39.955] [http-nio-45678-exec-3] [WARN ] [o.g.t.c.h.f.FeignAndRibbonController    :26  ] - 执行耗时：3006ms 错误：Read timed out executing POST http://clientsdk/feignandribbon/server
```
可见，3 秒读取超时生效了。注意：这里有一个大坑，如果你希望只修改读取超时，可能会只配置这么一行：
```
feign.client.config.default.readTimeout=3000
```
测试一下你就会发现，这样的配置是无法生效的！
结论二，也是坑点二，如果要配置 Feign 的读取超时，就必须同时配置连接超时，才能生效。
打开 FeignClientFactoryBean 可以看到，只有同时设置 ConnectTimeout 和 ReadTimeout，Request.Options 才会被覆盖：
```
if (config.getConnectTimeout() != null && config.getReadTimeout() != null) {
   builder.options(new Request.Options(config.getConnectTimeout(),
         config.getReadTimeout()));
}
```
更进一步，如果你希望针对单独的 Feign Client 设置超时时间，可以把 default 替换为 Client 的 name：
```
feign.client.config.default.readTimeout=3000
feign.client.config.default.connectTimeout=3000
feign.client.config.clientsdk.readTimeout=2000
feign.client.config.clientsdk.connectTimeout=2000
```
可以得出结论三，单独的超时可以覆盖全局超时，这符合预期，不算坑：
```
[15:45:51.708] [http-nio-45678-exec-3] [WARN ] [o.g.t.c.h.f.FeignAndRibbonController    :26  ] - 执行耗时：2006ms 错误：Read timed out executing POST http://clientsdk/feignandribbon/server
```
结论四，除了可以配置 Feign，也可以配置 Ribbon 组件的参数来修改两个超时时间。这里的坑点三是，参数首字母要大写，和 Feign 的配置不同。
```
ribbon.ReadTimeout=4000
ribbon.ConnectTimeout=4000
```
可以通过日志证明参数生效：
```
[15:55:18.019] [http-nio-45678-exec-3] [WARN ] [o.g.t.c.h.f.FeignAndRibbonController    :26  ] - 执行耗时：4003ms 错误：Read timed out executing POST http://clientsdk/feignandribbon/server
```
最后，我们来看看同时配置 Feign 和 Ribbon 的参数，最终谁会生效？如下代码的参数配置：
```
clientsdk.ribbon.listOfServers=localhost:45678
feign.client.config.default.readTimeout=3000
feign.client.config.default.connectTimeout=3000
ribbon.ReadTimeout=4000
ribbon.ConnectTimeout=4000
```
日志输出证明，最终生效的是 Feign 的超时：
```
[16:01:19.972] [http-nio-45678-exec-3] [WARN ] [o.g.t.c.h.f.FeignAndRibbonController    :26  ] - 执行耗时：3006ms 错误：Read timed out executing POST http://clientsdk/feignandribbon/server
```
结论五，同时配置 Feign 和 Ribbon 的超时，以 Feign 为准。这有点反直觉，因为 Ribbon 更底层所以你会觉得后者的配置会生效，但其实不是这样的。
在 LoadBalancerFeignClient 源码中可以看到，如果 Request.Options 不是默认值，就会创建一个 FeignOptionsClientConfig 代替原来 Ribbon 的 DefaultClientConfigImpl，导致 Ribbon 的配置被 Feign 覆盖：
```
IClientConfig getClientConfig(Request.Options options, String clientName) {
   IClientConfig requestConfig;
   if (options == DEFAULT_OPTIONS) {
      requestConfig = this.clientFactory.getClientConfig(clientName);
   }
   else {
      requestConfig = new FeignOptionsClientConfig(options);
   }
   return requestConfig;
}
```
但如果这么配置最终生效的还是 Ribbon 的超时（4 秒），这容易让人产生 Ribbon 覆盖了 Feign 的错觉，其实这还是因为坑二所致，单独配置 Feign 的读取超时并不能生效：
```
clientsdk.ribbon.listOfServers=localhost:45678
feign.client.config.default.readTimeout=3000
feign.client.config.clientsdk.readTimeout=2000
ribbon.ReadTimeout=4000
```
## 你是否知道 Ribbon 会自动重试请求呢？
一些 HTTP 客户端往往会内置一些重试策略，其初衷是好的，毕竟因为网络问题导致丢包虽然频繁但持续时间短，往往重试下第二次就能成功，但一定要小心这种自作主张是否符合我们的预期。
之前遇到过一个短信重复发送的问题，但短信服务的调用方用户服务，反复确认代码里没有重试逻辑。那问题究竟出在哪里了？我们来重现一下这个案例。
首先，定义一个 Get 请求的发送短信接口，里面没有任何逻辑，休眠 2 秒模拟耗时：
```
@RestController
@RequestMapping("ribbonretryissueserver")
@Slf4j
public class RibbonRetryIssueServerController {
    @GetMapping("sms")
    public void sendSmsWrong(@RequestParam("mobile") String mobile, @RequestParam("message") String message, HttpServletRequest request) throws InterruptedException {
        //输出调用参数后休眠2秒
        log.info("{} is called, {}=>{}", request.getRequestURL().toString(), mobile, message);
        TimeUnit.SECONDS.sleep(2);
    }
}
```
配置一个 Feign 供客户端调用：
```
@FeignClient(name = "SmsClient")
public interface SmsClient {
    @GetMapping("/ribbonretryissueserver/sms")
    void sendSmsWrong(@RequestParam("mobile") String mobile, @RequestParam("message") String message);
}
```
Feign 内部有一个 Ribbon 组件负责客户端负载均衡，通过配置文件设置其调用的服务端为两个节点：
```
SmsClient.ribbon.listOfServers=localhost:45679,localhost:45678
```
写一个客户端接口，通过 Feign 调用服务端：
```
@RestController
@RequestMapping("ribbonretryissueclient")
@Slf4j
public class RibbonRetryIssueClientController {
    @Autowired
    private SmsClient smsClient;
    @GetMapping("wrong")
    public String wrong() {
        log.info("client is called");
        try{
            //通过Feign调用发送短信接口
            smsClient.sendSmsWrong("13600000000", UUID.randomUUID().toString());
        } catch (Exception ex) {
            //捕获可能出现的网络错误
            log.error("send sms failed : {}", ex.getMessage());
        }
        return "done";
    }
}
```
在 45678 和 45679 两个端口上分别启动服务端，然后访问 45678 的客户端接口进行测试。因为客户端和服务端控制器在一个应用中，所以 45678 同时扮演了客户端和服务端的角色。
在 45678 日志中可以看到，29 秒时客户端收到请求开始调用服务端接口发短信，同时服务端收到了请求，2 秒后（注意对比第一条日志和第三条日志）客户端输出了读取超时的错误信息：
```
[12:49:29.020] [http-nio-45678-exec-4] [INFO ] [c.d.RibbonRetryIssueClientController:23  ] - client is called
[12:49:29.026] [http-nio-45678-exec-5] [INFO ] [c.d.RibbonRetryIssueServerController:16  ] - http://localhost:45678/ribbonretryissueserver/sms is called, 13600000000=>a2aa1b32-a044-40e9-8950-7f0189582418
[12:49:31.029] [http-nio-45678-exec-4] [ERROR] [c.d.RibbonRetryIssueClientController:27  ] - send sms failed : Read timed out executing GET http://SmsClient/ribbonretryissueserver/sms?mobile=13600000000&message=a2aa1b32-a044-40e9-8950-7f0189582418
```
而在另一个服务端 45679 的日志中还可以看到一条请求，30 秒时收到请求，也就是客户端接口调用后的 1 秒：
```
[12:49:30.029] [http-nio-45679-exec-2] [INFO ] [c.d.RibbonRetryIssueServerController:16  ] - http://localhost:45679/ribbonretryissueserver/sms is called, 13600000000=>a2aa1b32-a044-40e9-8950-7f0189582418
```
客户端接口被调用的日志只输出了一次，而服务端的日志输出了两次。虽然 Feign 的默认读取超时时间是 1 秒，但客户端 2 秒后才出现超时错误。显然，这说明客户端自作主张进行了一次重试，导致短信重复发送。
翻看 Ribbon 的源码可以发现，MaxAutoRetriesNextServer 参数默认为 1，也就是 Get 请求在某个服务端节点出现问题（比如读取超时）时，Ribbon 会自动重试一次：
```
// DefaultClientConfigImpl
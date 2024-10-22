    RedisTemplate redisTemplate;
    // 限流时间(单位：秒)
    @Value(value = "${IpLimiter.expireTime:1}")
    private Integer expireTime;
    // 限流次数
    @Value(value = "${IpLimiter.limitTimes:100}")
    private Integer limitTimes;
    /**
     * getRedisScript 读取脚本工具类
     * 这里设置为Long,是因为ipLimiter.lua 脚本返回的是数字类型
     */
    private DefaultRedisScript getRedisScript;
    private static String SIGN = ":";
    private static String IP_LIMIT_FILTER = "IP_LIMIT_FILTER:";
    // ip请求黑名单
    private static String IP_LIMIT_BLACK_LIST = "IP_LIMIT_BLACK_LIST:";
    @PostConstruct
    public void init() {
        getRedisScript = new DefaultRedisScript<>();
        getRedisScript.setResultType(Long.class);
        getRedisScript.setScriptSource(new ResourceScriptSource(new ClassPathResource("ipLimiter.lua")));
        log.info("IpLimitHandler[分布式限流处理器]脚本加载完成");
    }
    @Override
    public Mono filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        log.debug("IpLimitFilter[分布式限流处理器]开始执行限流操作");
        ServerHttpRequest request = exchange.getRequest();
        ServerHttpResponse response = exchange.getResponse();
        String limitIp = IpUtil.getIpAddr(request);
        //获取请求路径
        String url = request.getPath().toString();
        log.info("访问IP为:{}, 访问的地址: {}", limitIp, url);
        /**
         * 执行Lua脚本
         */
        List ipList = new ArrayList();
        // 设置key值为注解中的值
        String key = IP_LIMIT_FILTER.concat(url).concat(SIGN).concat(limitIp);
        ipList.add(key);
        /**
         * 调用脚本并执行
         */
        Long result = (Long) redisTemplate.execute(getRedisScript, ipList, expireTime, limitTimes);
        if (result == 0) {
            // TODO 放进全局黑名单【用于后续观察】
            redisTemplate.opsForValue().set(IP_LIMIT_BLACK_LIST + limitIp, 1, 7, TimeUnit.DAYS);
            String msg = "由于超过单位时间=" + expireTime + "-允许的请求次数=" + limitTimes + "[触发限流]";
            log.info(msg);
            // 达到限流返回给前端信息
            String errMessage = "{\"code\":\"error\",\"message\":\"请求过于频繁，请稍后再试\"}";
            byte[] bits = errMessage.getBytes(StandardCharsets.UTF_8);
            DataBuffer buffer = response.bufferFactory().wrap(bits);
            //指定编码，否则在浏览器中会中文乱码
            response.getHeaders().add("Content-Type", "text/plain;charset=UTF-8");
            return response.writeWith(Mono.just(buffer));
        } else {
            // 直接放行
            return chain.filter(exchange);
        }
    }
    @Override
    public int getOrder() {
        return 1;
    }
}
```
这里为了保证原子性，这边写了 **redis** 脚本 **ipLimiter.lua** 来执行 **redis** 命令，来保证操作原子性。
```lua
--获取KEY
local key1 = KEYS[1]
local val = redis.call('incr', key1)
local ttl = redis.call('ttl', key1)
--获取ARGV内的参数并打印
local expire = ARGV[1]
local times = ARGV[2]
redis.log(redis.LOG_DEBUG,tostring(times))
redis.log(redis.LOG_DEBUG,tostring(expire))
redis.log(redis.LOG_NOTICE, "incr "..key1.." "..val);
if val == 1 then
    redis.call('expire', key1, tonumber(expire))
else
    if ttl == -1 then
        redis.call('expire', key1, tonumber(expire))
    end
end
if val > tonumber(times) then
    return 0
end
return 1
```
获取用户 **IP** 的工具类 **IpUtil.java**
```java
@Slf4j
public class IpUtil {
    public static String getIpAddr(ServerHttpRequest request) {
        HttpHeaders headers = request.getHeaders();
        String ipAddress = headers.getFirst("X-Forwarded-For");
        if (ipAddress == null || ipAddress.length() == 0 || "unknown".equalsIgnoreCase(ipAddress)) {
            ipAddress = headers.getFirst("Proxy-Client-IP");
        }
        if (ipAddress == null || ipAddress.length() == 0 || "unknown".equalsIgnoreCase(ipAddress)) {
            ipAddress = headers.getFirst("WL-Proxy-Client-IP");
        }
        if (ipAddress == null || ipAddress.length() == 0 || "unknown".equalsIgnoreCase(ipAddress)) {
            ipAddress = request.getRemoteAddress().getAddress().getHostAddress();
            if (ipAddress.equals("127.0.0.1") || ipAddress.equals("0:0:0:0:0:0:0:1")) {
                // 根据网卡取本机配置的IP
                try {
                    InetAddress inet = InetAddress.getLocalHost();
                    ipAddress = inet.getHostAddress();
                } catch (UnknownHostException e) {
                    log.error("根据网卡获取本机配置的IP异常", e);
                }
            }
        }
        // 对于通过多个代理的情况，第一个IP为客户端真实IP，多个IP按照','分割
        if (ipAddress != null && ipAddress.indexOf(",") > 0) {
            ipAddress = ipAddress.split(",")[0];
        }
        return ipAddress;
    }
}
```
## 测试
下面，就进入了激动人心的测试环节了
首先，我们随意找一个不需要鉴权的接口，比如 **mogu-web** 的 **getHotTag**
![蘑菇接口](images/image-20220329092207736.png)
然后设置循环调用 **200** 次，点击启动进行压测
![单线程压测200次](images/image-20220329092329273.png)
点击启动，就可以看到 **200** 条请求已经完成了，因为这个请求没有编写对应的断言，所以只要返回 **http status = 200** 就代表成功
![压测成功](images/image-20220329092530287.png)
点开第**7、8**轮的时候，可以发现请求的是有正常返回的
![正确返回](images/image-20220329092702198.png)
但是到了 **10** 多轮的时候，可以看到接口已经触发了限流了，直接在网关就返回了错误信息
![限流返回](images/image-20220329092828335.png)
同时，观察日志可以看到，每隔一段时间后，在后台又会重新刷新我们的 **ip** 限流次数
![拦截日志](images/image-20220329092915961.png)
到这里，我们的 **Gateway** 限流算法就已经实现了，细心的小伙伴可能会发现，我们在代码中还留了一个 **TODO**
后续，可以接着这里继续扩展，做一个动态的全局 **IP** 黑名单功能，封掉那些屡屡来压测蘑菇的 **Ip** 地址~
```java
// TODO 放进全局黑名单【用于后续观察】
redisTemplate.opsForValue().set(IP_LIMIT_BLACK_LIST + limitIp, 1, 7, TimeUnit.DAYS);
```
好了，本期的 **Gateway** 限流算法教程就到这里了
我是 **陌溪**，我们下期再见
## 巨人肩膀
- https://blog.csdn.net/chaojunma/article/details/107352526
- https://www.jianshu.com/p/55de48fc484b
- https://github.com/yudiandemingzi/spring-boot-redis-ip-limiter
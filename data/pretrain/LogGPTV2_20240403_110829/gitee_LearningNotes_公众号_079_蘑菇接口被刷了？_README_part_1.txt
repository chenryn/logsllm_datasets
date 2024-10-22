大家好，我是**陌溪**
前阵子，陌溪在快乐搬砖的时候，突然群里小伙伴们疯狂 **@** 我，说蘑菇社区今天打不开了！
遇到事情不要慌，我琢磨着估计可能是网站又宕机了，重启一下就完事了
然后打开了蘑菇后台，顿时吓了一跳，好家伙今天的 **PV** 竟然有 **19w**，要知道蘑菇这个小破站，每天撑死也就几千的访问量，咋突然今天蹦到 **19W** 了，难道蘑菇火了？ 
带着疑惑，看了看下方的 **UV** 数，还是这 260 多的人数，咋就能搞到 **19W** 的 **UV**，难不成每个人把蘑菇文章都看了一遍？
![蘑菇后台PV、UV](images/image-20220320225104664.png)
我马上切到了蘑菇后台日志，好家伙原来你这小子，还用 **Jmeter** 在这压测蘑菇呢？直接给干了 **19W** 条记录，把蘑菇服务都给干趴了要
![蘑菇后台日志](images/image-20220320225119531.png)
我反手就是复制一波 **IP**，然后打开腾讯云服务器后台，找到防火墙创建新的规则，然后策略改为拒绝，同时这个小伙子的 **ip** 地址给加上去，同时端口选择全部端口，即 **1-65535**
![新增防火墙规则](images/image-20220328233353255.png)
创建完规则后，点击确定即可看到此条规则已经开始生效了
![规则生效](images/image-20220328233559059.png)
然后切到蘑菇的后台，再也没有看到接口有被刷的迹象，至此恢复了正常。
突然，我又想到了，这个小伙子会不会回头换了一个 **ip** 又卷土重来了？
那我岂不是他来一个 **ip**，就得封杀一个 **ip** ？这也太麻烦了吧
![](images/image-20220329095135953.png)
突然想到了，是不是可以在网关上搞点事，原来的蘑菇网关，啥事没做，就只用来转发了一个请求
我们都知道 **Gateway** 是对所有 **API** 服务进行统一管理的平台， 除了最基本的 **路由** 功能外，还可以实现 **安全验证**、**过滤**、**流控** 等策略
所以，就想到了用 **Gateway** 做一个限流功能，当某个 **ip** 访问次数过多的时候，直接给它拦截下来，防止一下把我们的服务给打挂了
## 定义全局过滤器
全局过滤器是作用于所有经过网关转发的请求的，实现 **GlobalFilter** 接口即可
同时 **Gateway** 是通过同时实现 **Ordered** 接口来实现控制过滤器的过滤顺序的，其中 **id** 越小其代表的优先级越高。
完整的文件结构如下所示：
![目录结构](images/image-20220329093354340.png)
在 **Gateway** 项目中，创建全局拦截器文件 **IpLimitFilter.java**
```bash
/**
 * IP限流
 * @author 陌溪
 * @date 2022年3月28日08:40:37
 */
@Slf4j
@RefreshScope
@Component
public class IpLimitFilter implements GlobalFilter, Ordered {
    @Override
    public Mono filter(ServerWebExchange exchange, GatewayFilterChain chain) {
  		return null;
  	}
    @Override
    public int getOrder() {
        return 1;
    }
}
```
## 基于 Redis 的分布式限流算法
实现了全局拦截器后， 陌溪在愉快的网上冲浪时，发现了一个 **spring-boot-redis-ip-limiter** 开源项目，使用的是 SpringBoot + Redis 组件，实现一个分布式接口 **IP** 限流功能 。
> Github地址：
>
> https://github.com/yudiandemingzi/spring-boot-redis-ip-limiter
### 项目的场景
为了防止我们的接口被人恶意访问，比如有人通过 **JMeter** 工具频繁访问我们的接口，导致接口响应变慢甚至崩溃,所以我们需要对一些特定的接口进行IP限流,即一定时间内同一 **IP** 访问的次数是有限的。
### 实现原理
用 **Redis** 作为限流组件的核心的原理,将用户的 **IP** 地址当 **Key**,一段时间内访问次数为 **value** ,同时设置该 **Key** 过期时间。
比如某接口设置  相同 **IP** **10** 秒 内请求 **5** 次，超过 **5** 次不让访问该接口。
1. 第一次该 **IP** 地址存入 **Redis** 的时候，key值为 **IP** 地址, **value**值为 **1**，设置 **key** 值过期时间为 **10** 秒。
2. 第二次该 **IP** 地址存入 **Redis** 时，如果 **key** 没有过期,那么更新 **value** 为 **2**。
3. 以此类推当 **value** 已经为 **5** 时，如果下次该 **IP** 地址在存入 **Redis** 同时 **key** 还没有过期，那么该 **Ip** 就不能访问了。
4. 当**10** 秒后，该 **key** 值过期，那么该 **IP** 地址再进来，**value** 又从 **1** 开始，过期时间还是 **10** 秒，这样反反复复。
说明：从上面的逻辑可以看出，是一时间段内访问次数受限,不是完全不让该 **IP** 访问接口。
技术框架：**SpringBoot** + **RedisTemplate** （采用自定义注解完成）
### 实现
因为原来的代码是使用 **AOP + 自定义注解** 的方式实现的，不太适用于网关的场景，所以我们可以把部分的核心代码放到 全局拦截器 **IpLimitFilter.java** 中
首先，引入项目中用到的 **maven** 依赖，因为需要使用 **Redis**，所以将 **Redis** 依赖引入
```pom
	org.springframework.data
	spring-data-redis
	redis.clients
	jedis
	3.0.1
```
然后，增加 **RedisTemplate** 的配置文件，**RedisConfig.java**
```java
@Configuration
public class RedisConfig extends CachingConfigurerSupport {
    @Bean
    public KeyGenerator keyGenerator() {
        return new KeyGenerator() {
            @Override
            public Object generate(Object target, java.lang.reflect.Method method, Object... params) {
                StringBuilder sb = new StringBuilder();
                sb.append(target.getClass().getName());
                sb.append(method.getName());
                for (Object obj : params) {
                    sb.append(obj.toString());
                }
                return sb.toString();
            }
        };
    }
    @Bean
    public CacheManager cacheManager(RedisConnectionFactory factory) {
        RedisCacheManager cacheManager = RedisCacheManager.create(factory);
        return cacheManager;
    }
    @Bean
    public RedisTemplate redisTemplate(RedisConnectionFactory factory) {
        StringRedisTemplate template = new StringRedisTemplate(factory);
        Jackson2JsonRedisSerializer jackson2JsonRedisSerializer = new Jackson2JsonRedisSerializer(Object.class);
        ObjectMapper om = new ObjectMapper();
        om.setVisibility(PropertyAccessor.ALL, JsonAutoDetect.Visibility.ANY);
        om.enableDefaultTyping(ObjectMapper.DefaultTyping.NON_FINAL);
        jackson2JsonRedisSerializer.setObjectMapper(om);
        template.setValueSerializer(jackson2JsonRedisSerializer);
        template.afterPropertiesSet();
        return template;
    }
}
```
开始在 **IpLimitFilter.java** 的全局拦截器中，实现我们的限流算法
首先，在 **nacos** 中的  **mogu-gateway-dev.yaml** 添加相关的配置
```yml
#spring
spring:
  #redis
  redis:
    host: 127.0.0.1 #redis的主机ip
    port: 6379
# 基于方法的全局IP限流
IpLimiter:
  # 时间，单位秒
  expireTime: 1  
  # 单位时间限制通过请求数  
  limitTimes: 20
```
下面是 **IpLimitFilter** 的完整代码
```java
/**
 * IP限流全局拦截器
 * @author 陌溪
 * @date 2022年3月28日08:40:37
 */
@Slf4j
@RefreshScope
@Component
public class IpLimitFilter implements GlobalFilter, Ordered {
    @Resource
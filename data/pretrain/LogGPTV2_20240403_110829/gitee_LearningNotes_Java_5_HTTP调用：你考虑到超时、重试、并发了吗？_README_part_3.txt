public static final int DEFAULT_MAX_AUTO_RETRIES_NEXT_SERVER = 1;
public static final int DEFAULT_MAX_AUTO_RETRIES = 0;
// RibbonLoadBalancedRetryPolicy
public boolean canRetry(LoadBalancedRetryContext context) {
   HttpMethod method = context.getRequest().getMethod();
   return HttpMethod.GET == method || lbContext.isOkToRetryOnAllOperations();
}
@Override
public boolean canRetrySameServer(LoadBalancedRetryContext context) {
   return sameServerCount  client) throws InterruptedException {
    //用于计数发送的请求个数
    AtomicInteger atomicInteger = new AtomicInteger();
    //使用HttpClient从server接口查询数据的任务提交到线程池并行处理
    ExecutorService threadPool = Executors.newCachedThreadPool();
    long begin = System.currentTimeMillis();
    IntStream.rangeClosed(1, count).forEach(i -> {
        threadPool.execute(() -> {
            try (CloseableHttpResponse response = client.get().execute(new HttpGet("http://127.0.0.1:45678/routelimit/server"))) {
                atomicInteger.addAndGet(Integer.parseInt(EntityUtils.toString(response.getEntity())));
            } catch (Exception ex) {
                ex.printStackTrace();
            }
        });
    });
    //等到count个任务全部执行完毕
    threadPool.shutdown();
    threadPool.awaitTermination(1, TimeUnit.HOURS);
    log.info("发送 {} 次请求，耗时 {} ms", atomicInteger.get(), System.currentTimeMillis() - begin);
    return atomicInteger.get();
}
```
首先，使用默认的 PoolingHttpClientConnectionManager 构造的 CloseableHttpClient，测试一下爬取 10 次的耗时：
```
static CloseableHttpClient httpClient1;
static {
    httpClient1 = HttpClients.custom().setConnectionManager(new PoolingHttpClientConnectionManager()).build();
}
@GetMapping("wrong")
public int wrong(@RequestParam(value = "count", defaultValue = "10") int count) throws InterruptedException {
    return sendRequest(count, () -> httpClient1);
}
```
虽然一个请求需要 1 秒执行完成，但我们的线程池是可以扩张使用任意数量线程的。按道理说，10 个请求并发处理的时间基本相当于 1 个请求的处理时间，也就是 1 秒，但日志中显示实际耗时 5 秒：
```
[12:48:48.122] [http-nio-45678-exec-1] [INFO ] [o.g.t.c.h.r.RouteLimitController        :54  ] - 发送 10 次请求，耗时 5265 ms
```
查看 PoolingHttpClientConnectionManager 源码，可以注意到有两个重要参数：
defaultMaxPerRoute=2，也就是同一个主机 / 域名的最大并发请求数为 2。我们的爬虫需要 10 个并发，显然是默认值太小限制了爬虫的效率。
maxTotal=20，也就是所有主机整体最大并发为 20，这也是 HttpClient 整体的并发度。目前，我们请求数是 10 最大并发是 10，20 不会成为瓶颈。举一个例子，使用同一个 HttpClient 访问 10 个域名，defaultMaxPerRoute 设置为 10，为确保每一个域名都能达到 10 并发，需要把 maxTotal 设置为 100。
```
public PoolingHttpClientConnectionManager(
    final HttpClientConnectionOperator httpClientConnectionOperator,
    final HttpConnectionFactory connFactory,
    final long timeToLive, final TimeUnit timeUnit) {
    ...    
    this.pool = new CPool(new InternalConnectionFactory(
            this.configData, connFactory), 2, 20, timeToLive, timeUnit);
   ...
} 
public CPool(
        final ConnFactory connFactory,
        final int defaultMaxPerRoute, final int maxTotal,
        final long timeToLive, final TimeUnit timeUnit) {
    ...
}}
```
HttpClient 是 Java 非常常用的 HTTP 客户端，这个问题经常出现。你可能会问，为什么默认值限制得这么小。
其实，这不能完全怪 HttpClient，很多早期的浏览器也限制了同一个域名两个并发请求。对于同一个域名并发连接的限制，其实是 HTTP 1.1 协议要求的，这里有这么一段话：
```
Clients that use persistent connections SHOULD limit the number of simultaneous connections that they maintain to a given server. A single-user client SHOULD NOT maintain more than 2 connections with any server or proxy. A proxy SHOULD use up to 2*N connections to another server or proxy, where N is the number of simultaneously active users. These guidelines are intended to improve HTTP response times and avoid congestion.
```
HTTP 1.1 协议是 20 年前制定的，现在 HTTP 服务器的能力强很多了，所以有些新的浏览器没有完全遵从 2 并发这个限制，放开并发数到了 8 甚至更大。如果需要通过 HTTP 客户端发起大量并发请求，不管使用什么客户端，请务必确认客户端的实现默认的并发度是否满足需求。
既然知道了问题所在，我们就尝试声明一个新的 HttpClient 放开相关限制，设置 maxPerRoute 为 50、maxTotal 为 100，然后修改一下刚才的 wrong 方法，使用新的客户端进行测试：
```
httpClient2 = HttpClients.custom().setMaxConnPerRoute(10).setMaxConnTotal(20).build();
```
输出如下，10 次请求在 1 秒左右执行完成。可以看到，因为放开了一个 Host 2 个并发的默认限制，爬虫效率得到了大幅提升：
```
[12:58:11.333] [http-nio-45678-exec-3] [INFO ] [o.g.t.c.h.r.RouteLimitController        :54  ] - 发送 10 次请求，耗时 1023 ms
```
## 重点回顾
今天，我和你分享了 HTTP 调用最常遇到的超时、重试和并发问题。
连接超时代表建立 TCP 连接的时间，读取超时代表了等待远端返回数据的时间，也包括远端程序处理的时间。在解决连接超时问题时，我们要搞清楚连的是谁；在遇到读取超时问题的时候，我们要综合考虑下游服务的服务标准和自己的服务标准，设置合适的读取超时时间。此外，在使用诸如 Spring Cloud Feign 等框架时务必确认，连接和读取超时参数的配置是否正确生效。
对于重试，因为 HTTP 协议认为 Get 请求是数据查询操作，是无状态的，又考虑到网络出现丢包是比较常见的事情，有些 HTTP 客户端或代理服务器会自动重试 Get/Head 请求。如果你的接口设计不支持幂等，需要关闭自动重试。但，更好的解决方案是，遵从 HTTP 协议的建议来使用合适的 HTTP 方法。
最后我们看到，包括 HttpClient 在内的 HTTP 客户端以及浏览器，都会限制客户端调用的最大并发数。如果你的客户端有比较大的请求调用并发，比如做爬虫，或是扮演类似代理的角色，又或者是程序本身并发较高，如此小的默认值很容易成为吞吐量的瓶颈，需要及时调整。
今天用到的代码，我都放在了 GitHub 上，你可以点击这个链接查看。
## 思考与讨论
第一节中我们强调了要注意连接超时和读取超时参数的配置，大多数的 HTTP 客户端也都有这两个参数。有读就有写，但为什么我们很少看到“写入超时”的概念呢？
除了 Ribbon 的 AutoRetriesNextServer 重试机制，Nginx 也有类似的重试功能。你了解 Nginx 相关的配置吗？
针对 HTTP 调用，你还遇到过什么坑吗？
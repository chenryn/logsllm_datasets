对这个接口进行几秒的压测（压测使用 wrk，1 个并发 1 个连接）可以看到，已经建立了三千多个 TCP 连接到 45678 端口（其中有 1 个是压测客户端到 Tomcat 的连接，大部分都是 HttpClient 到 Tomcat 的连接）：
![img](images/54a71ee9a7bbbd5e121b12fe6289aff2.png)
好在有了空闲连接回收的策略，60 秒之后连接处于 CLOSE_WAIT 状态，最终彻底关闭。
![img](images/8ea5f53e6510d76cf447c23fb15daa77.png)
这 2 点证明，CloseableHttpClient 属于第二种模式，即内部带有连接池的 API，其背后是连接池，最佳实践一定是复用。
复用方式很简单，你可以把 CloseableHttpClient 声明为 static，只创建一次，并且在 JVM 关闭之前通过 addShutdownHook 钩子关闭连接池，在使用的时候直接使用 CloseableHttpClient 即可，无需每次都创建。
首先，定义一个 right 接口来实现服务端接口调用：
```
private static CloseableHttpClient httpClient = null;
static {
    //当然，也可以把CloseableHttpClient定义为Bean，然后在@PreDestroy标记的方法内close这个HttpClient
    httpClient = HttpClients.custom().setMaxConnPerRoute(1).setMaxConnTotal(1).evictIdleConnections(60, TimeUnit.SECONDS).build();
    Runtime.getRuntime().addShutdownHook(new Thread(() -> {
        try {
            httpClient.close();
        } catch (IOException ignored) {
        }
    }));
}
@GetMapping("right")
public String right() {
    try (CloseableHttpResponse response = httpClient.execute(new HttpGet("http://127.0.0.1:45678/httpclientnotreuse/test"))) {
        return EntityUtils.toString(response.getEntity());
    } catch (Exception ex) {
        ex.printStackTrace();
    }
    return null;
}
```
然后，重新定义一个 wrong2 接口，修复之前按需创建 CloseableHttpClient 的代码，每次用完之后确保连接池可以关闭：
```
@GetMapping("wrong2")
public String wrong2() {
    try (CloseableHttpClient client = HttpClients.custom()
            .setConnectionManager(new PoolingHttpClientConnectionManager())
            .evictIdleConnections(60, TimeUnit.SECONDS).build();
         CloseableHttpResponse response = client.execute(new HttpGet("http://127.0.0.1:45678/httpclientnotreuse/test"))) {
            return EntityUtils.toString(response.getEntity());
        } catch (Exception ex) {
        ex.printStackTrace();
    }
    return null;
}
```
使用 wrk 对 wrong2 和 right 两个接口分别压测 60 秒，可以看到两种使用方式性能上的差异，每次创建连接池的 QPS 是 337，而复用连接池的 QPS 是 2022：
![img](images/b79fb99cf8a5c3a17e60b0850544472d.png)
如此大的性能差异显然是因为 TCP 连接的复用。你可能注意到了，刚才定义连接池时，我将最大连接数设置为 1。所以，复用连接池方式复用的始终应该是同一个连接，而新建连接池方式应该是每次都会创建新的 TCP 连接。
接下来，我们通过网络抓包工具 Wireshark 来证实这一点。
如果调用 wrong2 接口每次创建新的连接池来发起 HTTP 请求，从 Wireshark 可以看到，每次请求服务端 45678 的客户端端口都是新的。这里我发起了三次请求，程序通过 HttpClient 访问服务端 45678 的客户端端口号，分别是 51677、51679 和 51681：
![img](images/7b8f651755cef0c05ecb08727d315e35.png)
也就是说，每次都是新的 TCP 连接，放开 HTTP 这个过滤条件也可以看到完整的 TCP 握手、挥手的过程：
![img](images/4815c0edd21d5bf0cae8c0c3e578960d.png)
而复用连接池方式的接口 right 的表现就完全不同了。可以看到，第二次 HTTP 请求 #41 的客户端端口 61468 和第一次连接 #23 的端口是一样的，Wireshark 也提示了整个 TCP 会话中，当前 #41 请求是第二次请求，前一次是 #23，后面一次是 #75：
![img](images/2cbada9be98ce33321b29d38adb09f2c.png)
只有 TCP 连接闲置超过 60 秒后才会断开，连接池会新建连接。你可以尝试通过 Wireshark 观察这一过程。
接下来，我们就继续聊聊连接池的配置问题。
## 连接池的配置不是一成不变的
为方便根据容量规划设置连接处的属性，连接池提供了许多参数，包括最小（闲置）连接、最大连接、闲置连接生存时间、连接生存时间等。其中，最重要的参数是最大连接数，它决定了连接池能使用的连接数量上限，达到上限后，新来的请求需要等待其他请求释放连接。
但，最大连接数不是设置得越大越好。如果设置得太大，不仅仅是客户端需要耗费过多的资源维护连接，更重要的是由于服务端对应的是多个客户端，每一个客户端都保持大量的连接，会给服务端带来更大的压力。这个压力又不仅仅是内存压力，可以想一下如果服务端的网络模型是一个 TCP 连接一个线程，那么几千个连接意味着几千个线程，如此多的线程会造成大量的线程切换开销。
当然，连接池最大连接数设置得太小，很可能会因为获取连接的等待时间太长，导致吞吐量低下，甚至超时无法获取连接。
接下来，我们就模拟下压力增大导致数据库连接池打满的情况，来实践下如何确认连接池的使用情况，以及有针对性地进行参数优化。
首先，定义一个用户注册方法，通过 @Transactional 注解为方法开启事务。其中包含了 500 毫秒的休眠，一个数据库事务对应一个 TCP 连接，所以 500 多毫秒的时间都会占用数据库连接：
```
@Transactional
public User register(){
    User user=new User();
    user.setName("new-user-"+System.currentTimeMillis());
    userRepository.save(user);
    try {
        TimeUnit.MILLISECONDS.sleep(500);
    } catch (InterruptedException e) {
        e.printStackTrace();
    }
    return user;
}
```
随后，修改配置文件启用 register-mbeans，使 Hikari 连接池能通过 JMX MBean 注册连接池相关统计信息，方便观察连接池：
```
spring.datasource.hikari.register-mbeans=true
```
启动程序并通过 JConsole 连接进程后，可以看到默认情况下最大连接数为 10：
![img](images/7b8e5aff5a3ef6ade1d8027c20c92f94.png)
使用 wrk 对应用进行压测，可以看到连接数一下子从 0 到了 10，有 20 个线程在等待获取连接：
![img](images/b22169b8d8bbfabbb8b93ece11a1f9ef.png)
不久就出现了无法获取数据库连接的异常，如下所示：
```
[15:37:56.156] [http-nio-45678-exec-15] [ERROR] [.a.c.c.C.[.[.[/].[dispatcherServlet]:175 ] - Servlet.service() for servlet [dispatcherServlet] in context with path [] threw exception [Request processing failed; nested exception is org.springframework.dao.DataAccessResourceFailureException: unable to obtain isolated JDBC connection; nested exception is org.hibernate.exception.JDBCConnectionException: unable to obtain isolated JDBC connection] with root cause
java.sql.SQLTransientConnectionException: HikariPool-1 - Connection is not available, request timed out after 30000ms.
```
从异常信息中可以看到，数据库连接池是 HikariPool，解决方式很简单，修改一下配置文件，调整数据库连接池最大连接参数到 50 即可。
```
spring.datasource.hikari.maximum-pool-size=50
```
然后，再观察一下这个参数是否适合当前压力，满足需求的同时也不占用过多资源。从监控来看这个调整是合理的，有一半的富余资源，再也没有线程需要等待连接了：
![img](images/d24f23f05d49378a10a857cd8b9ef031.png)
在这个 Demo 里，我知道压测大概能对应使用 25 左右的并发连接，所以直接把连接池最大连接设置为了 50。在真实情况下，只要数据库可以承受，你可以选择在遇到连接超限的时候先设置一个足够大的连接数，然后观察最终应用的并发，再按照实际并发数留出一半的余量来设置最终的最大连接。
其实，看到错误日志后再调整已经有点儿晚了。更合适的做法是，对类似数据库连接池的重要资源进行持续检测，并设置一半的使用量作为报警阈值，出现预警后及时扩容。
在这里我是为了演示，才通过 JConsole 查看参数配置后的效果，生产上需要把相关数据对接到指标监控体系中持续监测。
这里要强调的是，修改配置参数务必验证是否生效，并且在监控系统中确认参数是否生效、是否合理。之所以要“强调”，是因为这里有坑。
我之前就遇到过这样一个事故。应用准备针对大促活动进行扩容，把数据库配置文件中 Druid 连接池最大连接数 maxActive 从 50 提高到了 100，修改后并没有通过监控验证，结果大促当天应用因为连接池连接数不够爆了。
经排查发现，当时修改的连接数并没有生效。原因是，应用虽然一开始使用的是 Druid 连接池，但后来框架升级了，把连接池替换为了 Hikari 实现，原来的那些配置其实都是无效的，修改后的参数配置当然也不会生效。
所以说，对连接池进行调参，一定要眼见为实。
## 重点回顾
今天，我以三种业务代码最常用的 Redis 连接池、HTTP 连接池、数据库连接池为例，和你探讨了有关连接池实现方式、使用姿势和参数配置的三大问题。
客户端 SDK 实现连接池的方式，包括池和连接分离、内部带有连接池和非连接池三种。要正确使用连接池，就必须首先鉴别连接池的实现方式。比如，Jedis 的 API 实现的是池和连接分离的方式，而 Apache HttpClient 是内置连接池的 API。
对于使用姿势其实就是两点，一是确保连接池是复用的，二是尽可能在程序退出之前显式关闭连接池释放资源。连接池设计的初衷就是为了保持一定量的连接，这样连接可以随取随用。从连接池获取连接虽然很快，但连接池的初始化会比较慢，需要做一些管理模块的初始化以及初始最小闲置连接。一旦连接池不是复用的，那么其性能会比随时创建单一连接更差。
最后，连接池参数配置中，最重要的是最大连接数，许多高并发应用往往因为最大连接数不够导致性能问题。但，最大连接数不是设置得越大越好，够用就好。需要注意的是，针对数据库连接池、HTTP 连接池、Redis 连接池等重要连接池，务必建立完善的监控和报警机制，根据容量规划及时调整参数配置。
今天用到的代码，我都放在了 GitHub 上，你可以点击这个链接查看。
## 思考与讨论
有了连接池之后，获取连接是从连接池获取，没有足够连接时连接池会创建连接。这时，获取连接操作往往有两个超时时间：一个是从连接池获取连接的最长等待时间，通常叫作请求连接超时 connectRequestTimeout 或连接等待超时 connectWaitTimeout；一个是连接池新建 TCP 连接三次握手的连接超时，通常叫作连接超时 connectTimeout。针对 JedisPool、Apache HttpClient 和 Hikari 数据库连接池，你知道如何设置这 2 个参数吗？
对于带有连接池的 SDK 的使用姿势，最主要的是鉴别其内部是否实现了连接池，如果实现了连接池要尽量复用 Client。对于 NoSQL 中的 MongoDB 来说，使用 MongoDB Java 驱动时，MongoClient 类应该是每次都创建还是复用呢？你能否在官方文档中找到答案呢？
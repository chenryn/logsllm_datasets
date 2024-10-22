            udpSendTimeMap.put(ackEntry.key, System.currentTimeMillis());
            Loggers.PUSH.info("send udp packet: " + ackEntry.key);
            //发送udp数据包
            udpSocket.send(ackEntry.origin);
            ackEntry.increaseRetryTime();
            //又提交了一个延迟任务（延迟10秒），其实这个任务的作用就是重试，
            //实现的效果就是当前发送完udp之后，如果没有收到ACK响应，就隔10秒重发一次，并且只重试一次
            GlobalExecutor.scheduleRetransmitter(new Retransmitter(ackEntry),
                    TimeUnit.NANOSECONDS.toMillis(ACK_TIMEOUT_NANOS), TimeUnit.MILLISECONDS);
            return ackEntry;
        } catch (Exception e) {
            Loggers.PUSH.error("[NACOS-PUSH] failed to push data: {} to client: {}, error: {}", ackEntry.data,
                    ackEntry.origin.getAddress().getHostAddress(), e);
            ackMap.remove(ackEntry.key);
            udpSendTimeMap.remove(ackEntry.key);
            failedPush += 1;
            return null;
        }
    }
    //实现重发的任务Retransmitter
    public static class Retransmitter implements Runnable {
        Receiver.AckEntry ackEntry;
        public Retransmitter(Receiver.AckEntry ackEntry) {
            this.ackEntry = ackEntry;
        }
        @Override
        public void run() {
            //如果ackMap中包含该数据包，就重发一次，ackMap存放的都是没有收到ACK响应的包
            //如果接受到ACK响应，会移除（参考Receiver线程）
            if (ackMap.containsKey(ackEntry.key)) {
                Loggers.PUSH.info("retry to push data, key: " + ackEntry.key);
                udpPush(ackEntry);
            }
        }
    }   
}
```
上面这段代码其实就一个作用：向nacos客户端发送udp包，如果隔了10秒还没收到ACK响应，就重发一次（通过另一个延迟任务实现）。
### PushService类结构
![img](https:////upload-images.jianshu.io/upload_images/13587608-8d30a502f5883d6f.png?imageMogr2/auto-orient/strip|imageView2/2/w/1200/format/webp)
第一眼就会看到一个关键接口：ApplicationListener，没错，PushService这个类就是一个事件监听类，它所监听的事件正是ServiceChangeEvent，onApplicationEvent方法已经在上面讲过了。
#### static代码块
PushService中有一个static代码块，static代码块在类被主动引用的时候会首先执行一次。
```java
@Component
@SuppressWarnings("PMD.ThreadPoolCreationRule")
public class PushService implements ApplicationContextAware, ApplicationListener {
    static {
        try {
            udpSocket = new DatagramSocket();
            Receiver receiver = new Receiver();
            Thread inThread = new Thread(receiver);
            inThread.setDaemon(true);
            inThread.setName("com.alibaba.nacos.naming.push.receiver");
            inThread.start();
            GlobalExecutor.scheduleRetransmitter(() -> {
                try {
                    removeClientIfZombie();
                } catch (Throwable e) {
                    Loggers.PUSH.warn("[NACOS-PUSH] failed to remove client zombie");
                }
            }, 0, 20, TimeUnit.SECONDS);
        } catch (SocketException e) {
            Loggers.SRV_LOG.error("[NACOS-PUSH] failed to init push service");
        }
    }
}
```
这个代码块里先是开启了一个线程：Receiver，然后又开启了一个定时任务（20秒执行一次），对应的逻辑代码：removeClientIfZombie()，对他们分别简单讲解下。
#### Receiver线程
```java
@Component
@SuppressWarnings("PMD.ThreadPoolCreationRule")
public class PushService implements ApplicationContextAware, ApplicationListener {
   public static class Receiver implements Runnable {
        @Override
        public void run() {
            while (true) {
                byte[] buffer = new byte[1024 * 64];
                DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
                try {
                    udpSocket.receive(packet);
                    String json = new String(packet.getData(), 0, packet.getLength(), StandardCharsets.UTF_8).trim();
                    AckPacket ackPacket = JacksonUtils.toObj(json, AckPacket.class);
                    InetSocketAddress socketAddress = (InetSocketAddress) packet.getSocketAddress();
                    String ip = socketAddress.getAddress().getHostAddress();
                    int port = socketAddress.getPort();
                    //接受到ACK响应的时间距离上次接受到的时间之差如果大于10秒
                    //ACK_TIMEOUT_NANOS = TimeUnit.SECONDS.toNanos(10L)
                    if (System.nanoTime() - ackPacket.lastRefTime > ACK_TIMEOUT_NANOS) {
                        Loggers.PUSH.warn("ack takes too long from {} ack json: {}", packet.getSocketAddress(), json);
                    }
                    String ackKey = getAckKey(ip, port, ackPacket.lastRefTime);
                    AckEntry ackEntry = ackMap.remove(ackKey);
                    if (ackEntry == null) {
                        throw new IllegalStateException(
                                "unable to find ackEntry for key: " + ackKey + ", ack json: " + json);
                    }
                    long pushCost = System.currentTimeMillis() - udpSendTimeMap.get(ackKey);
                    Loggers.PUSH
                            .info("received ack: {} from: {}:{}, cost: {} ms, unacked: {}, total push: {}", json, ip,
                                    port, pushCost, ackMap.size(), totalPush);
                    //pushCostMap存放每个数据包的耗时
                    pushCostMap.put(ackKey, pushCost);
                    udpSendTimeMap.remove(ackKey);
                } catch (Throwable e) {
                    Loggers.PUSH.error("[NACOS-PUSH] error while receiving ack data", e);
                }
            }
        }
    }
}
```
这个线程一直轮询接受UDP协议的响应，接受到ACK响应包后没干其它事，主要就是维护一些属性：ackMap、pushCostMap、udpSendTimeMap，至于这些属性干嘛用的（其中pushCostMap已经知道，见上面注释），可以往下看，后面会有用到。
#### 定时任务：removeClientIfZombie()
```java
@Component
@SuppressWarnings("PMD.ThreadPoolCreationRule")
public class PushService implements ApplicationContextAware, ApplicationListener {
    //根据方法命名，可以隐约猜到，应该是移除僵尸客户端的
    private static void removeClientIfZombie() {
        int size = 0;
        for (Map.Entry> entry : clientMap.entrySet()) {
            ConcurrentMap clientConcurrentMap = entry.getValue();
            for (Map.Entry entry1 : clientConcurrentMap.entrySet()) {
                PushClient client = entry1.getValue();
                //如果是僵尸client，则从clientMap中移除
                if (client.zombie()) {
                    clientConcurrentMap.remove(entry1.getKey());
                }
            }
            size += clientConcurrentMap.size();
        }
        if (Loggers.PUSH.isDebugEnabled()) {
            Loggers.PUSH.debug("[NACOS-PUSH] clientMap size: {}", size);
        }
    }
    public class PushClient {   
        public boolean zombie() {
            return System.currentTimeMillis() - lastRefTime > switchDomain.getPushCacheMillis(serviceName);
        }
    }       
}
```
该方法就是维护了clientMap（见onApplicationEvent方法中注释），在client.zombie()判断规则中有个很关键的属性：lastRefTime（位于PushClient中），要知道这个属性的意思，就需要知道clientMap是如何初始化的（clientMap中存放的就是PushClient）？
到这里，Receiver线程中维护的那几个属性的作用也已经很清楚了：
- ackMap：存放所有已经发送了udp但还没收到客户端的ACK响应的数据包；
- pushCostMap：存放每个数据包的耗时；
- udpSendTimeMap：存放每个数据包开始发送的时间；
   Receiver线程就是用来接收ACK响应的，所以每接受到一个响应包，就会从ackMap和udpSendTimeMap中移除，所以Receiver线程的作用也很清楚了。
#### UDP客户端的初始化
clientMap中存放的是所有的udp客户端，nacos服务端需要往客户端通过udp协议推送数据，所以需要将所有客户端进行初始化。
不知道大家有没有注意到上面onApplicationEvent方法的代码中我加了两个注释，在构建Receiver.AckEntry对象的时候，会执行到这行代码：ackEntry = prepareAckEntry(client, prepareHostsData(client), lastRefTime)，然后重点关注下prepareHostsData(client)方法：
```tsx
@Component
@SuppressWarnings("PMD.ThreadPoolCreationRule")
public class PushService implements ApplicationContextAware, ApplicationListener {
    private static Map prepareHostsData(PushClient client) throws Exception {
        Map cmd = new HashMap(2);
        cmd.put("type", "dom");
        //初始化udp客户端
        cmd.put("data", client.getDataSource().getData(client));
        return cmd;
    }
}
//InstanceController类中pushDataSource初始化代码
@RestController
@RequestMapping(UtilsAndCommons.NACOS_NAMING_CONTEXT + "/instance")
public class InstanceController {
    private DataSource pushDataSource = new DataSource() {
        @Override
        public String getData(PushService.PushClient client) {
            ObjectNode result = JacksonUtils.createEmptyJsonNode();
            try {
                //默认传入的udp的端口为0，即不开启nacos服务端udp推送功能
                result = doSrvIpxt(client.getNamespaceId(), client.getServiceName(), client.getAgent(),
                        client.getClusters(), client.getSocketAddr().getAddress().getHostAddress(), 0,
                        StringUtils.EMPTY, false, StringUtils.EMPTY, StringUtils.EMPTY, false);
            } catch (Exception e) {
                String serviceNameField = "name";
                String lastRefTimeField = "lastRefTime";
                if (result.get(serviceNameField) == null) {
                    String serviceName = client.getServiceName();
                    if (serviceName == null) {
                        serviceName = StringUtils.trimToEmpty(serviceName);
                    }
                    result.put(serviceNameField, serviceName);
                    result.put(lastRefTimeField, System.currentTimeMillis());
                }
                Loggers.SRV_LOG.warn("PUSH-SERVICE: service is not modified", e);
            }
            // overdrive the cache millis to push mode
            result.put("cacheMillis", switchDomain.getPushCacheMillis(client.getServiceName()));
            return result.toString();
        }
    };
    //继续看doSrvIpxt方法，方法很长，这里只贴片段    
    public ObjectNode doSrvIpxt(String namespaceId, String serviceName, String agent, String clusters, String clientIP,
            int udpPort, String env, boolean isCheck, String app, String tid, boolean healthyOnly) throws Exception {
        ClientInfo clientInfo = new ClientInfo(agent);
        ObjectNode result = JacksonUtils.createEmptyJsonNode();
        Service service = serviceManager.getService(namespaceId, serviceName);
        long cacheMillis = switchDomain.getDefaultCacheMillis();
        // now try to enable the push
        try {
            //udpPort是服务发现时指定的
            if (udpPort > 0 && pushService.canEnablePush(agent)) {
                pushService
                        .addClient(namespaceId, serviceName, clusters, agent, new InetSocketAddress(clientIP, udpPort),
                                pushDataSource, tid, app);
                cacheMillis = switchDomain.getPushCacheMillis(serviceName);
            }
        } catch (Exception e) {
            Loggers.SRV_LOG
                    .error("[NACOS-API] failed to added push client {}, {}:{}", clientInfo, clientIP, udpPort, e);
            cacheMillis = switchDomain.getDefaultCacheMillis();
        }
        //代码略……
    }       
}
```
#### doSrvIpxt方法会调用PushService类的addClient方法，而clientMap就是在addClient方法中初始化的：
```dart
@Component
public class PushService implements ApplicationContextAware, ApplicationListener {
    public void addClient(String namespaceId, String serviceName, String clusters, String agent,
            InetSocketAddress socketAddr, DataSource dataSource, String tenant, String app) {
        PushClient client = new PushClient(namespaceId, serviceName, clusters, agent, socketAddr, dataSource, tenant,
                app);
        addClient(client);
    }
    public void addClient(PushClient client) {
        // client is stored by key 'serviceName' because notify event is driven by serviceName change
        String serviceKey = UtilsAndCommons.assembleFullServiceName(client.getNamespaceId(), client.getServiceName());
        ConcurrentMap clients = clientMap.get(serviceKey);
        if (clients == null) {
            clientMap.putIfAbsent(serviceKey, new ConcurrentHashMap<>(1024));
            clients = clientMap.get(serviceKey);
        }
        PushClient oldClient = clients.get(client.toString());
        if (oldClient != null) {
            oldClient.refresh();
        } else {
            PushClient res = clients.putIfAbsent(client.toString(), client);
            if (res != null) {
                Loggers.PUSH.warn("client: {} already associated with key {}", res.getAddrStr(), res.toString());
            }
            Loggers.PUSH.debug("client: {} added for serviceName: {}", client.getAddrStr(), client.getServiceName());
        }
    }   
}
```
看到这我们已经清楚clientMap初始化的来龙去脉了，现在再回看一下僵尸client的判断规则：
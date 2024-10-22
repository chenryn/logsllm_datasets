        params.put("weight", String.valueOf(instance.getWeight()));
        params.put("enable", String.valueOf(instance.isEnabled()));
        params.put("healthy", String.valueOf(instance.isHealthy()));
        params.put("ephemeral", String.valueOf(instance.isEphemeral()));
        params.put("metadata", JacksonUtils.toJson(instance.getMetadata()));
        reqApi(UtilAndComs.nacosUrlInstance, params, HttpMethod.POST);
    }
}
```
心跳实际就是通过schedule定时向server发送数据包，然后启动一个线程检测服务端的返回，如果在指定时间没有返回则认为服务端出了问题，服务端也会根据发来的心跳包不断更新服务的状态。
### 1.2、服务端心跳
接下来我们把目光放到服务端，找到InstanceController的beat方法，如果是参数beat信息的话，说明是第一次发起心跳，则会带有服务实例信息，因为发起心跳成功则服务端会返回下次不要带beat信息的参数，这样客户端第二次就不会携带beat信息了。如果发现没有该服务，又没带beat信息，说明这个服务可能被移除过了，直接返回没找到。如果没有服务，但是发现有beat信息，那就从beat中获取服务实例信息，进行注册：
#### 看InstanceController的beat方法
```java
@RestController
@RequestMapping(UtilsAndCommons.NACOS_NAMING_CONTEXT + "/instance")
public class InstanceController {
    @CanDistro
    @PutMapping("/beat")
    @Secured(parser = NamingResourceParser.class, action = ActionTypes.WRITE)
    public ObjectNode beat(HttpServletRequest request) throws Exception {
        ObjectNode result = JacksonUtils.createEmptyJsonNode();
        //设置心跳间隔
        result.put(SwitchEntry.CLIENT_BEAT_INTERVAL, switchDomain.getClientBeatInterval());
        String beat = WebUtils.optional(request, "beat", StringUtils.EMPTY);
        RsInfo clientBeat = null;
        //判断有无心跳内容
        //如果存在心跳内容则不是轻量级心跳就转化为RsInfo
        if (StringUtils.isNotBlank(beat)) {
            clientBeat = JacksonUtils.toObj(beat, RsInfo.class);
        }
        String clusterName = WebUtils
                .optional(request, CommonParams.CLUSTER_NAME, UtilsAndCommons.DEFAULT_CLUSTER_NAME);
        String ip = WebUtils.optional(request, "ip", StringUtils.EMPTY);
        int port = Integer.parseInt(WebUtils.optional(request, "port", "0"));
        if (clientBeat != null) {
            if (StringUtils.isNotBlank(clientBeat.getCluster())) {
                clusterName = clientBeat.getCluster();
            } else {
                // fix #2533
                clientBeat.setCluster(clusterName);
            }
            ip = clientBeat.getIp();
            port = clientBeat.getPort();
        }
        String namespaceId = WebUtils.optional(request, CommonParams.NAMESPACE_ID, Constants.DEFAULT_NAMESPACE_ID);
        String serviceName = WebUtils.required(request, CommonParams.SERVICE_NAME);
        NamingUtils.checkServiceNameFormat(serviceName);
        Loggers.SRV_LOG.debug("[CLIENT-BEAT] full arguments: beat: {}, serviceName: {}", clientBeat, serviceName);
        //获取对应的实例的信息
        Instance instance = serviceManager.getInstance(namespaceId, serviceName, clusterName, ip, port);
        //如果实例不存在
        if (instance == null) {
            //并且心跳内容也不存在
            if (clientBeat == null) {
                result.put(CommonParams.CODE, NamingResponseCode.RESOURCE_NOT_FOUND);
                //返回RESOURCE_NOT_FOUND给客户端，客户端会发起服务注册
                return result;
            }
            Loggers.SRV_LOG.warn("[CLIENT-BEAT] The instance has been removed for health mechanism, "
                    + "perform data compensation operations, beat: {}, serviceName: {}", clientBeat, serviceName);
            //根据心跳内容创建一个实例信息
            instance = new Instance();
            instance.setPort(clientBeat.getPort());
            instance.setIp(clientBeat.getIp());
            instance.setWeight(clientBeat.getWeight());
            instance.setMetadata(clientBeat.getMetadata());
            instance.setClusterName(clusterName);
            instance.setServiceName(serviceName);
            instance.setInstanceId(instance.getInstanceId());
            instance.setEphemeral(clientBeat.isEphemeral());
            //注册实例
            serviceManager.registerInstance(namespaceId, serviceName, instance);
        }
        //获取服务的信息
        Service service = serviceManager.getService(namespaceId, serviceName);
        if (service == null) {
            throw new NacosException(NacosException.SERVER_ERROR,
                    "service not found: " + serviceName + "@" + namespaceId);
        }
        //不存在心跳内容的话，要创建一个进行处理
        if (clientBeat == null) {
            clientBeat = new RsInfo();
            clientBeat.setIp(ip);
            clientBeat.setPort(port);
            clientBeat.setCluster(clusterName);
        }
        service.processClientBeat(clientBeat);
        result.put(CommonParams.CODE, NamingResponseCode.OK);
        //5秒间隔
        if (instance.containsMetadata(PreservedMetadataKeys.HEART_BEAT_INTERVAL)) {
            result.put(SwitchEntry.CLIENT_BEAT_INTERVAL, instance.getInstanceHeartBeatInterval());
        }
        //告诉客户端不需要带上心跳信息了，变成轻量级心跳了
        result.put(SwitchEntry.LIGHT_BEAT_ENABLED, switchDomain.isLightBeatEnabled());
        return result;
    }
}
```
#### 接下来看一下processClientBeat方法，该方法将ClientBeatProcessor放入到线程池中，接下来我们看下重点看下run方法,
```java
public class Service extends com.alibaba.nacos.api.naming.pojo.Service implements Record, RecordListener {
    public void processClientBeat(final RsInfo rsInfo) {
        ClientBeatProcessor clientBeatProcessor = new ClientBeatProcessor();
        clientBeatProcessor.setService(this);
        //将服务提供者的心跳信息设置进去
        clientBeatProcessor.setRsInfo(rsInfo);
        //放入线程池
        HealthCheckReactor.scheduleNow(clientBeatProcessor);
    }
}
public class HealthCheckReactor {
    public static ScheduledFuture scheduleNow(Runnable task) {
        return GlobalExecutor.scheduleNamingHealth(task, 0, TimeUnit.MILLISECONDS);
    }
}
```
#### 该方法内部主要就是更新对应实例下心跳时间，并且发送服务变更事件。
```java
public class ClientBeatProcessor implements Runnable {
    private RsInfo rsInfo;
    private Service service;
    @Override
    public void run() {
        Service service = this.service;
        if (Loggers.EVT_LOG.isDebugEnabled()) {
            Loggers.EVT_LOG.debug("[CLIENT-BEAT] processing beat: {}", rsInfo.toString());
        }
        String ip = rsInfo.getIp();
        String clusterName = rsInfo.getCluster();
        int port = rsInfo.getPort();
        //获取对应集群下的所有实例信息
        Cluster cluster = service.getClusterMap().get(clusterName);
        List instances = cluster.allIPs(true);
        for (Instance instance : instances) {
            //更新对应实例下最近一次心跳信息
            if (instance.getIp().equals(ip) && instance.getPort() == port) {
                if (Loggers.EVT_LOG.isDebugEnabled()) {
                    Loggers.EVT_LOG.debug("[CLIENT-BEAT] refresh beat: {}", rsInfo.toString());
                }
                //更新该实例最后一次心跳更新时间
                instance.setLastBeat(System.currentTimeMillis());
                if (!instance.isMarked()) {
                    if (!instance.isHealthy()) {
                        //如果之前该实例是不健康的，会被设置为健康
                        instance.setHealthy(true);
                        Loggers.EVT_LOG
                                .info("service: {} {POS} {IP-ENABLED} valid: {}:{}@{}, region: {}, msg: client beat ok",
                                        cluster.getService().getName(), ip, port, cluster.getName(),
                                        UtilsAndCommons.LOCALHOST_SITE);
                        //发送服务变更事件
                        getPushService().serviceChanged(service);
                    }
                }
            }
        }
    }
}
@Component
public class PushService implements ApplicationContextAware, ApplicationListener {
    @Autowired
    private SwitchDomain switchDomain;
    private ApplicationContext applicationContext;
    public void serviceChanged(Service service) {
        // merge some change events to reduce the push frequency:
        if (futureMap
                .containsKey(UtilsAndCommons.assembleFullServiceName(service.getNamespaceId(), service.getName()))) {
            return;
        }
        //发送服务变更事件
        this.applicationContext.publishEvent(new ServiceChangeEvent(this, service));
    }
}
```
#### PushService.onApplicationEvent监听ServiceChangeEvent事件
```dart
@Component
public class PushService implements ApplicationContextAware, ApplicationListener {
    @Autowired
    private SwitchDomain switchDomain;
    private static ConcurrentMap futureMap = new ConcurrentHashMap<>(); 
    private static volatile ConcurrentMap ackMap = new ConcurrentHashMap<>();
    private static ConcurrentMap> clientMap = new ConcurrentHashMap<>();  
    @Override
    public void onApplicationEvent(ServiceChangeEvent event) {
        Service service = event.getService();
        String serviceName = service.getName();
        String namespaceId = service.getNamespaceId();
        //nacos服务端给每个客户端实例推送udp包时，该实例就是一个udp客户端，
        //clientMap中存放的就是这些udp客户端信息
        Future future = GlobalExecutor.scheduleUdpSender(() -> {
            try {
                Loggers.PUSH.info(serviceName + " is changed, add it to push queue.");
                ConcurrentMap clients = clientMap
                        .get(UtilsAndCommons.assembleFullServiceName(namespaceId, serviceName));
                if (MapUtils.isEmpty(clients)) {
                    return;
                }
                Map cache = new HashMap<>(16);
                long lastRefTime = System.nanoTime();
                for (PushClient client : clients.values()) {
                    if (client.zombie()) {
                        Loggers.PUSH.debug("client is zombie: " + client.toString());
                        clients.remove(client.toString());
                        Loggers.PUSH.debug("client is zombie: " + client.toString());
                        continue;
                    }
                    Receiver.AckEntry ackEntry;
                    Loggers.PUSH.debug("push serviceName: {} to client: {}", serviceName, client.toString());
                    String key = getPushCacheKey(serviceName, client.getIp(), client.getAgent());
                    byte[] compressData = null;
                    Map data = null;
                    //switchDomain.getDefaultPushCacheMillis()默认是10秒，
                    //即10000毫秒，不会进入这个分支，所以compressData=null
                    if (switchDomain.getDefaultPushCacheMillis() >= 20000 && cache.containsKey(key)) {
                        org.javatuples.Pair pair = (org.javatuples.Pair) cache.get(key);
                        compressData = (byte[]) (pair.getValue0());
                        data = (Map) pair.getValue1();
                        Loggers.PUSH.debug("[PUSH-CACHE] cache hit: {}:{}", serviceName, client.getAddrStr());
                    }
                    if (compressData != null) {
                        ackEntry = prepareAckEntry(client, compressData, data, lastRefTime);
                    } else {
                        //compressData=null，所以会进入这个分支，
                        //关注prepareHostsData(client)方法
                        ackEntry = prepareAckEntry(client, prepareHostsData(client), lastRefTime);
                        if (ackEntry != null) {
                            cache.put(key, new org.javatuples.Pair<>(ackEntry.origin.getData(), ackEntry.data));
                        }
                    }
                    Loggers.PUSH.info("serviceName: {} changed, schedule push for: {}, agent: {}, key: {}",
                            client.getServiceName(), client.getAddrStr(), client.getAgent(),
                            (ackEntry == null ? null : ackEntry.key));
                    //通过udp协议向nacos 消费者客户端推送数据
                    udpPush(ackEntry);
                }
            } catch (Exception e) {
                Loggers.PUSH.error("[NACOS-PUSH] failed to push serviceName: {} to client, error: {}", serviceName, e);
            } finally {
                futureMap.remove(UtilsAndCommons.assembleFullServiceName(namespaceId, serviceName));
            }
        }, 1000, TimeUnit.MILLISECONDS);
        futureMap.put(UtilsAndCommons.assembleFullServiceName(namespaceId, serviceName), future);
    }
}
```
咋一看这个方法很复杂，首先看一下这个方法的主体结构，其实主要就是开启了一个一次性延迟任务（注意不是定时任务，只会执行一次），它的职责就是通过udp协议向nacos客户端推送数据，对应方法：udpPush(ackEntry)
#### udpPush(ackEntry)
```java
@Component
public class PushService implements ApplicationContextAware, ApplicationListener {
    private static volatile ConcurrentMap ackMap = new ConcurrentHashMap<>();
    private static volatile ConcurrentMap ackMap = new ConcurrentHashMap<>();
    private static DatagramSocket udpSocket;
    private static Receiver.AckEntry udpPush(Receiver.AckEntry ackEntry) {
        if (ackEntry == null) {
            Loggers.PUSH.error("[NACOS-PUSH] ackEntry is null.");
            return null;
        }
        //如果重试次数大于MAX_RETRY_TIMES=1次，就不再发送udp包了
        if (ackEntry.getRetryTimes() > MAX_RETRY_TIMES) {
            Loggers.PUSH.warn("max re-push times reached, retry times {}, key: {}", ackEntry.retryTimes, ackEntry.key);
            ackMap.remove(ackEntry.key);
            udpSendTimeMap.remove(ackEntry.key);
            failedPush += 1;
            return ackEntry;
        }
        try {
            if (!ackMap.containsKey(ackEntry.key)) {
                totalPush++;
            }
            //结合Receiver.run()可知，ackMap存放的是已发送udp但是还没收到ACK响应的数据包
            ackMap.put(ackEntry.key, ackEntry);
            //udpSendTimeMap存放每个udp数据包开始发送的事件
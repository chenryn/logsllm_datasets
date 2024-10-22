## 一、Nacos服务心跳
### 1.1、客户端心跳
Nacos Client会维护一个定时任务通过持续调用服务端的接口更新心跳时间，保证自己处于存活状态，防止服务端将服务剔除，Nacos默认5秒向服务端发送一次，通过请求服务端接口**/instance/beat**发送心跳。
#### 客户端服务在注册服务
根据nacos-discovery的META-INF目录下的spring.factories配置来完成相关类的自动装配。
![img](https:////upload-images.jianshu.io/upload_images/13587608-7b1c1e2ce89e4156.png?imageMogr2/auto-orient/strip|imageView2/2/w/1200/format/webp)
- NacosServiceRegistryAutoConfiguration用来注册管理这几个bean。
```kotlin
@Configuration(proxyBeanMethods = false)
@EnableConfigurationProperties
@ConditionalOnNacosDiscoveryEnabled
@ConditionalOnProperty(value = "spring.cloud.service-registry.auto-registration.enabled",
        matchIfMissing = true)
@AutoConfigureAfter({ AutoServiceRegistrationConfiguration.class,
        AutoServiceRegistrationAutoConfiguration.class,
        NacosDiscoveryAutoConfiguration.class })
public class NacosServiceRegistryAutoConfiguration {
    @Bean
    public NacosServiceRegistry nacosServiceRegistry(
            NacosDiscoveryProperties nacosDiscoveryProperties) {
        return new NacosServiceRegistry(nacosDiscoveryProperties);
    }
    @Bean
    @ConditionalOnBean(AutoServiceRegistrationProperties.class)
    public NacosRegistration nacosRegistration(
            ObjectProvider> registrationCustomizers,
            NacosDiscoveryProperties nacosDiscoveryProperties,
            ApplicationContext context) {
        return new NacosRegistration(registrationCustomizers.getIfAvailable(),
                nacosDiscoveryProperties, context);
    }
    @Bean
    @ConditionalOnBean(AutoServiceRegistrationProperties.class)
    public NacosAutoServiceRegistration nacosAutoServiceRegistration(
            NacosServiceRegistry registry,
            AutoServiceRegistrationProperties autoServiceRegistrationProperties,
            NacosRegistration registration) {
        return new NacosAutoServiceRegistration(registry,
                autoServiceRegistrationProperties, registration);
    }
}
```
- NacosServiceRegistry：完成服务注册，实现ServiceRegistry。
- NacosRegistration：用来注册时存储nacos服务端的相关信息。
- NacosAutoServiceRegistration 继承spring中的AbstractAutoServiceRegistration，AbstractAutoServiceRegistration实现ApplicationListener，通过事件监听来发起服务注册，到时候会调用NacosServiceRegistry.register(registration)
#### 在NacosServiceRegistry.registry方法中，调用了nacos client sdk中的namingService.registerInstance完成服务注册。
```cpp
public class NacosServiceRegistry implements ServiceRegistry {
    @Override
    public void register(Registration registration) {
        if (StringUtils.isEmpty(registration.getServiceId())) {
            log.warn("No service to register for nacos client...");
            return;
        }
        NamingService namingService = namingService();
        String serviceId = registration.getServiceId();
        String group = nacosDiscoveryProperties.getGroup();
        Instance instance = getNacosInstanceFromRegistration(registration);
        try {
            namingService.registerInstance(serviceId, group, instance);
            log.info("nacos registry, {} {} {}:{} register finished", group, serviceId,
                    instance.getIp(), instance.getPort());
        }
        catch (Exception e) {
            if (nacosDiscoveryProperties.isFailFast()) {
                log.error("nacos registry, {} register failed...{},", serviceId,
                        registration.toString(), e);
                rethrowRuntimeException(e);
            }
            else {
                log.warn("Failfast is false. {} register failed...{},", serviceId,
                        registration.toString(), e);
            }
        }
    }
}
```
#### 继续看namingService.registerInstance的实现主要就两件事
- 1、beatReactor.addBeatInfo创建心跳信息实现健康检查，Nacos Server必须要确保注册的服务实例是健康的，而心跳检测就是服务监控检测的方式。
- 2、serverProxy.registerService 服务注册。
```java
public class NacosNamingService implements NamingService {
    private BeatReactor beatReactor;
    private NamingProxy serverProxy;
    @Override
    public void registerInstance(String serviceName, String groupName, Instance instance) throws NacosException {
        NamingUtils.checkInstanceIsLegal(instance);
        //创建group@@servciceName
        String groupedServiceName = NamingUtils.getGroupedName(serviceName, groupName);
        //如果当前实例是临时实例(默认是临时实例)
        if (instance.isEphemeral()) {
            // 创建心跳信息
            BeatInfo beatInfo = beatReactor.buildBeatInfo(groupedServiceName, instance);
            //beanReactor添加心跳信息检测
            beatReactor.addBeatInfo(groupedServiceName, beatInfo);
        }
        //发送请求向nacos注册服务
        serverProxy.registerService(groupedServiceName, groupName, instance);
    }
}
```
#### 看下BeatInfo这个类
- 给周期任务设定时间`beatInfo.setPeriod(instance.getInstanceHeartBeatInterval())`
```java
public class BeatReactor implements Closeable {
    public BeatInfo buildBeatInfo(String groupedServiceName, Instance instance) {
        BeatInfo beatInfo = new BeatInfo();
        //服务名称
        beatInfo.setServiceName(groupedServiceName);
        //IP
        beatInfo.setIp(instance.getIp());
        //端口
        beatInfo.setPort(instance.getPort());
        //集群名称
        beatInfo.setCluster(instance.getClusterName());
        //权重
        beatInfo.setWeight(instance.getWeight());
        //元数据
        beatInfo.setMetadata(instance.getMetadata());
        beatInfo.setScheduled(false);
        //心跳周期,给周期任务设定时间
        beatInfo.setPeriod(instance.getInstanceHeartBeatInterval());
        return beatInfo;
    }
}
public class Instance implements Serializable {
    public long getInstanceHeartBeatInterval() {
        return getMetaDataByKeyWithDefault(PreservedMetadataKeys.HEART_BEAT_INTERVAL,
                Constants.DEFAULT_HEART_BEAT_INTERVAL);
    }
}
public class Constants {
    //Constants内部定义的一个DEFAULT_HEART_BEAT_INTERVAL的常量，设定5秒:
    public static final long DEFAULT_HEART_BEAT_INTERVAL = TimeUnit.SECONDS.toMillis(5);
}
```
#### 接下来我们看下addBeatInfo方法，该方法内部主要是将BeatTask任务加入到线程池ScheduledExecutorService当中。
```java
public class BeatReactor implements Closeable {
    private final ScheduledExecutorService executorService;
    private final NamingProxy serverProxy;
    public BeatReactor(NamingProxy serverProxy, int threadCount) {
        this.serverProxy = serverProxy;
        //实例化客户端心跳机制线程池
        this.executorService = new ScheduledThreadPoolExecutor(threadCount, new ThreadFactory() {
            @Override
            public Thread newThread(Runnable r) {
                Thread thread = new Thread(r);
                thread.setDaemon(true);
                thread.setName("com.alibaba.nacos.naming.beat.sender");
                return thread;
            }
        });
    }
    public void addBeatInfo(String serviceName, BeatInfo beatInfo) {
        NAMING_LOGGER.info("[BEAT] adding beat: {} to beat map.", beatInfo);
        String key = buildKey(serviceName, beatInfo.getIp(), beatInfo.getPort());
        BeatInfo existBeat = null;
        //fix #1733
        if ((existBeat = dom2Beat.remove(key)) != null) {
            existBeat.setStopped(true);
        }
        dom2Beat.put(key, beatInfo);
        //将心跳任务添加到线程池中，发起一个心跳检测任务
        executorService.schedule(new BeatTask(beatInfo), beatInfo.getPeriod(), TimeUnit.MILLISECONDS);
        MetricsMonitor.getDom2BeatSizeMonitor().set(dom2Beat.size());
    }
}   
```
#### 重点部分就是看BeatTask
BeatTask继承Runnable，run方法就是我们的重点，该方法调用了NamingProxy的sendBeat方法，服务端请求地址为**/instance/beat**的方法。
```csharp
public class BeatReactor implements Closeable {
    private final ScheduledExecutorService executorService;
    private final NamingProxy serverProxy;  
    class BeatTask implements Runnable {
        BeatInfo beatInfo;
        public BeatTask(BeatInfo beatInfo) {
            this.beatInfo = beatInfo;
        }
        @Override
        public void run() {
            if (beatInfo.isStopped()) {
                return;
            }
            //心跳周期执行时间
            long nextTime = beatInfo.getPeriod();
            try {
                //向Nacos Server服务端发送心跳请求
                JsonNode result = serverProxy.sendBeat(beatInfo, BeatReactor.this.lightBeatEnabled);
                long interval = result.get("clientBeatInterval").asLong();
                boolean lightBeatEnabled = false;
                if (result.has(CommonParams.LIGHT_BEAT_ENABLED)) {
                    lightBeatEnabled = result.get(CommonParams.LIGHT_BEAT_ENABLED).asBoolean();
                }
                BeatReactor.this.lightBeatEnabled = lightBeatEnabled;
                if (interval > 0) {
                    nextTime = interval;
                }
                int code = NamingResponseCode.OK;
                if (result.has(CommonParams.CODE)) {
                    code = result.get(CommonParams.CODE).asInt();
                }
                //如果返回资源未找到，则立即重新注册服务
                if (code == NamingResponseCode.RESOURCE_NOT_FOUND) {
                    Instance instance = new Instance();
                    instance.setPort(beatInfo.getPort());
                    instance.setIp(beatInfo.getIp());
                    instance.setWeight(beatInfo.getWeight());
                    instance.setMetadata(beatInfo.getMetadata());
                    instance.setClusterName(beatInfo.getCluster());
                    instance.setServiceName(beatInfo.getServiceName());
                    instance.setInstanceId(instance.getInstanceId());
                    instance.setEphemeral(true);
                    try {
                        //发送http请求,向Nacos Server服务端注册服务
                        serverProxy.registerService(beatInfo.getServiceName(),
                                NamingUtils.getGroupName(beatInfo.getServiceName()), instance);
                    } catch (Exception ignore) {
                    }
                }
            } catch (NacosException ex) {
                NAMING_LOGGER.error("[CLIENT-BEAT] failed to send beat: {}, code: {}, msg: {}",
                        JacksonUtils.toJson(beatInfo), ex.getErrCode(), ex.getErrMsg());
            } catch (Exception unknownEx) {
                NAMING_LOGGER.error("[CLIENT-BEAT] failed to send beat: {}, unknown exception msg: {}",
                        JacksonUtils.toJson(beatInfo), unknownEx.getMessage(), unknownEx);
            } finally {
                //定时去运行,发送心跳请求
                executorService.schedule(new BeatTask(beatInfo), nextTime, TimeUnit.MILLISECONDS);
            }
        }
    }
}
public class NamingProxy implements Closeable {
    //向Nacos Server服务端发送心跳请求
    public JsonNode sendBeat(BeatInfo beatInfo, boolean lightBeatEnabled) throws NacosException {
        if (NAMING_LOGGER.isDebugEnabled()) {
            NAMING_LOGGER.debug("[BEAT] {} sending beat to server: {}", namespaceId, beatInfo.toString());
        }
        Map params = new HashMap(8);
        Map bodyMap = new HashMap(2);
        if (!lightBeatEnabled) {
            bodyMap.put("beat", JacksonUtils.toJson(beatInfo));
        }
        params.put(CommonParams.NAMESPACE_ID, namespaceId);
        params.put(CommonParams.SERVICE_NAME, beatInfo.getServiceName());
        params.put(CommonParams.CLUSTER_NAME, beatInfo.getCluster());
        params.put("ip", beatInfo.getIp());
        params.put("port", String.valueOf(beatInfo.getPort()));
        String result = reqApi(UtilAndComs.nacosUrlBase + "/instance/beat", params, bodyMap, HttpMethod.PUT);
        return JacksonUtils.toObj(result);
    }
    //发送http请求,向Nacos Server服务端注册服务
    public void registerService(String serviceName, String groupName, Instance instance) throws NacosException {
        NAMING_LOGGER.info("[REGISTER-SERVICE] {} registering service {} with instance: {}", namespaceId, serviceName,
                instance);
        final Map params = new HashMap(16);
        params.put(CommonParams.NAMESPACE_ID, namespaceId);
        params.put(CommonParams.SERVICE_NAME, serviceName);
        params.put(CommonParams.GROUP_NAME, groupName);
        params.put(CommonParams.CLUSTER_NAME, instance.getClusterName());
        params.put("ip", instance.getIp());
        params.put("port", String.valueOf(instance.getPort()));
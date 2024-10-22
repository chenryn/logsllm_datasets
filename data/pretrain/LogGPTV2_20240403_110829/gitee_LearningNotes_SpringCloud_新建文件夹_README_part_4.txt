```java
public boolean zombie() {
    //客户端从初始化到响应ack，超过了10秒，就认为是僵尸client
    //lastRefTime是PushClient类中的属性，默认是当前时间，可以代表PushClient初始化的时间
    //这句代码就可以理解为：如果一个客户端长时间没有进行ack响应，就认识它是僵尸client
    return System.currentTimeMillis() - lastRefTime > switchDomain.getPushCacheMillis(serviceName);
}
```
当任务某个客户端是僵尸client时，就从客户端集合（clientMap）中移除，下次就不会向它推送udp数据包了。
### Nacos心跳机制总结
PushService类的主要功能基本上讲的差不多了，可能有人会觉得一脸懵，nacos源码想说明白确实不容易，里面有太多的异步任务，跳来跳去，很容易晕，我这里做一个总结吧。
#### udp推送
- 当服务端注册表中实例发送了变更时，就会发布ServiceChangeEvent事件，就会被PushService监听到，监听到之后就会以服务维度向客户端通过udp协议推送通知，从clientMap中找出需要推送的客户端进行能推送；
- 如果发送失败或者超过10秒没收到ack响应，就会隔10秒进行重试（从ackMap中找出需要重试的包，ackMap由Receiver线程维护），最大重试次数默认为1次，超过1次就不再发送；
#### ack接收
- PushService类的static代码块中开启了守护线程Receiver，用于循环接收来自客户端的ack响应，使用ackMap维护所有已发送udp包但还没有进行ack响应的包，如果接收到ack响应，就从ackMap中移除；
#### udp客户端集合维护
- PushService类的static代码块中开启了一个定时任务（20秒一次）专门用来维护clientMap（存放了所有需要进行udp推送的客户端），如果发现哪个客户端从初始化到响应ack的时间间隔超过了10秒，就从clientMap中移除，那么下次就不会再往这个客户端推送udp了。
## Nacos服务的健康检查
Nacos Server会开启一个定时任务来检查注册服务的健康情况，对于超过15秒没收到客户端的心跳实例会将它的 healthy属性置为false，此时当客户端不会将该实例的信息发现，如果某个服务的实例超过30秒没收到心跳，则剔除该实例，如果剔除的实例恢复，发送心跳则会恢复。
当有实例注册的时候，我们会看到有个service.init()的方法，该方法的实现主要是将ClientBeatCheckTask加入到线程池当中:
```java
@Component
public class ServiceManager implements RecordListener {
    @Resource(name = "consistencyDelegate")
    private ConsistencyService consistencyService;
    private void putServiceAndInit(Service service) throws NacosException {
        putService(service);
        service = getService(service.getNamespaceId(), service.getName());
        //启动服务检查
        service.init();
        consistencyService
                .listen(KeyBuilder.buildInstanceListKey(service.getNamespaceId(), service.getName(), true), service);
        consistencyService
                .listen(KeyBuilder.buildInstanceListKey(service.getNamespaceId(), service.getName(), false), service);
        Loggers.SRV_LOG.info("[NEW-SERVICE] {}", service.toJson());
    }
}
```
#### ClientBeatCheckTask中的run方法主要做两件事心跳时间超过15秒则设置该实例信息为不健康状况和心跳时间超过30秒则删除该实例信息，如下代码:
```java
public class ClientBeatCheckTask implements Runnable {
    private Service service;
    @Override
    public void run() {
        try {
            if (!getDistroMapper().responsible(service.getName())) {
                return;
            }
            if (!getSwitchDomain().isHealthCheckEnabled()) {
                return;
            }
            //获取服务所有实例信息
            List instances = service.allIPs(true);
            // first set health status of instances:
            for (Instance instance : instances) {
                //如果心跳时间超过15秒则设置该实例信息为不健康状况
                if (System.currentTimeMillis() - instance.getLastBeat() > instance.getInstanceHeartBeatTimeOut()) {
                    if (!instance.isMarked()) {
                        if (instance.isHealthy()) {
                            //设置该实例信息为不健康状况
                            instance.setHealthy(false);
                            Loggers.EVT_LOG
                                    .info("{POS} {IP-DISABLED} valid: {}:{}@{}@{}, region: {}, msg: client timeout after {}, last beat: {}",
                                            instance.getIp(), instance.getPort(), instance.getClusterName(),
                                            service.getName(), UtilsAndCommons.LOCALHOST_SITE,
                                            instance.getInstanceHeartBeatTimeOut(), instance.getLastBeat());
                            getPushService().serviceChanged(service);
                            ApplicationUtils.publishEvent(new InstanceHeartbeatTimeoutEvent(this, instance));
                        }
                    }
                }
            }
            if (!getGlobalConfig().isExpireInstance()) {
                return;
            }
            // then remove obsolete instances:
            for (Instance instance : instances) {
                if (instance.isMarked()) {
                    continue;
                }
                //如果心跳时间超过30秒则删除该实例信息
                if (System.currentTimeMillis() - instance.getLastBeat() > instance.getIpDeleteTimeout()) {
                    // delete instance
                    Loggers.SRV_LOG.info("[AUTO-DELETE-IP] service: {}, ip: {}", service.getName(),
                            JacksonUtils.toJson(instance));
                    deleteIp(instance);
                }
            }
        } catch (Exception e) {
            Loggers.SRV_LOG.warn("Exception while processing client beat time out.", e);
        }
    }
}   
public static final long DEFAULT_HEART_BEAT_TIMEOUT = TimeUnit.SECONDS.toMillis(15);
public static final long DEFAULT_IP_DELETE_TIMEOUT = TimeUnit.SECONDS.toMillis(30);
```
#### 首先我们来看一下deleteIp方法，该方法内部主要通过构建删除请求，发送删除请求：
```java
public class ClientBeatCheckTask implements Runnable {
    private void deleteIp(Instance instance) {
        try {
            NamingProxy.Request request = NamingProxy.Request.newRequest();
            request.appendParam("ip", instance.getIp()).appendParam("port", String.valueOf(instance.getPort()))
                    .appendParam("ephemeral", "true").appendParam("clusterName", instance.getClusterName())
                    .appendParam("serviceName", service.getName()).appendParam("namespaceId", service.getNamespaceId());
            //构建Url
            String url = "http://" + IPUtil.localHostIP() + IPUtil.IP_PORT_SPLITER + EnvUtil.getPort() + EnvUtil.getContextPath()
                    + UtilsAndCommons.NACOS_NAMING_CONTEXT + "/instance?" + request.toUrl();
            //发送Http删除请求
            // delete instance asynchronously:
            HttpClient.asyncHttpDelete(url, null, null, new Callback() {
                @Override
                public void onReceive(RestResult result) {
                    if (!result.ok()) {
                        Loggers.SRV_LOG
                                .error("[IP-DEAD] failed to delete ip automatically, ip: {}, caused {}, resp code: {}",
                                        instance.toJson(), result.getMessage(), result.getCode());
                    }
                }
                @Override
                public void onError(Throwable throwable) {
                    Loggers.SRV_LOG
                            .error("[IP-DEAD] failed to delete ip automatically, ip: {}, error: {}", instance.toJson(),
                                    throwable);
                }
                @Override
                public void onCancel() {
                }
            });
        } catch (Exception e) {
            Loggers.SRV_LOG
                    .error("[IP-DEAD] failed to delete ip automatically, ip: {}, error: {}", instance.toJson(), e);
        }
    }
}   
```
#### 删除实例的接口
```java
@RestController
@RequestMapping(UtilsAndCommons.NACOS_NAMING_CONTEXT + "/instance")
public class InstanceController {
    @CanDistro
    @DeleteMapping
    @Secured(parser = NamingResourceParser.class, action = ActionTypes.WRITE)
    public String deregister(HttpServletRequest request) throws Exception {
        Instance instance = getIpAddress(request);
        String namespaceId = WebUtils.optional(request, CommonParams.NAMESPACE_ID, Constants.DEFAULT_NAMESPACE_ID);
        String serviceName = WebUtils.required(request, CommonParams.SERVICE_NAME);
        NamingUtils.checkServiceNameFormat(serviceName);
        Service service = serviceManager.getService(namespaceId, serviceName);
        if (service == null) {
            Loggers.SRV_LOG.warn("remove instance from non-exist service: {}", serviceName);
            return "ok";
        }
        //删除方法
        serviceManager.removeInstance(namespaceId, serviceName, instance.isEphemeral(), instance);
        return "ok";
    }
}
```
#### 内部通过调用ServiceManager的removeInstance方法
```java
@Component
public class ServiceManager implements RecordListener {
    public void removeInstance(String namespaceId, String serviceName, boolean ephemeral, Instance... ips)
            throws NacosException {
        Service service = getService(namespaceId, serviceName);
        synchronized (service) {
            removeInstance(namespaceId, serviceName, ephemeral, service, ips);
        }
    }
    private void removeInstance(String namespaceId, String serviceName, boolean ephemeral, Service service,
            Instance... ips) throws NacosException {
        String key = KeyBuilder.buildInstanceListKey(namespaceId, serviceName, ephemeral);
        //排除要删除的实例信息
        List instanceList = substractIpAddresses(service, ephemeral, ips);
        Instances instances = new Instances();
        instances.setInstanceList(instanceList);
        //更新实例信息
        consistencyService.put(key, instances);
    }   
}
```
#### 重点看下substractIpAddresses内部通过调用updateIpAddresses，该方法内部主要就是移除到超过30秒的实例信息
```dart
@Component
public class ServiceManager implements RecordListener {
    private List substractIpAddresses(Service service, boolean ephemeral, Instance... ips)
            throws NacosException {
        return updateIpAddresses(service, UtilsAndCommons.UPDATE_INSTANCE_ACTION_REMOVE, ephemeral, ips);
    }
    public List updateIpAddresses(Service service, String action, boolean ephemeral, Instance... ips)
            throws NacosException {
        Datum datum = consistencyService
                .get(KeyBuilder.buildInstanceListKey(service.getNamespaceId(), service.getName(), ephemeral));
        //获取所有实例信息
        List currentIPs = service.allIPs(ephemeral);
        Map currentInstances = new HashMap<>(currentIPs.size());
        Set currentInstanceIds = Sets.newHashSet();
        for (Instance instance : currentIPs) {
            currentInstances.put(instance.toIpAddr(), instance);
            currentInstanceIds.add(instance.getInstanceId());
        }
        //初始化Map
        Map instanceMap;
        if (datum != null && null != datum.value) {
            instanceMap = setValid(((Instances) datum.value).getInstanceList(), currentInstances);
        } else {
            instanceMap = new HashMap<>(ips.length);
        }
        for (Instance instance : ips) {
            if (!service.getClusterMap().containsKey(instance.getClusterName())) {
                Cluster cluster = new Cluster(instance.getClusterName(), service);
                cluster.init();
                service.getClusterMap().put(instance.getClusterName(), cluster);
                Loggers.SRV_LOG
                        .warn("cluster: {} not found, ip: {}, will create new cluster with default configuration.",
                                instance.getClusterName(), instance.toJson());
            }
            //移除超过30秒的实例信息
            if (UtilsAndCommons.UPDATE_INSTANCE_ACTION_REMOVE.equals(action)) {
                instanceMap.remove(instance.getDatumKey());
            } else {
                Instance oldInstance = instanceMap.get(instance.getDatumKey());
                if (oldInstance != null) {
                    instance.setInstanceId(oldInstance.getInstanceId());
                } else {
                    instance.setInstanceId(instance.generateInstanceId(currentInstanceIds));
                }
                instanceMap.put(instance.getDatumKey(), instance);
            }
        }
        if (instanceMap.size() (instanceMap.values());
    }   
}
```
#### 心跳机制简单图
![img](https:////upload-images.jianshu.io/upload_images/13587608-2cf73f5747d3a6f3.png?imageMogr2/auto-orient/strip|imageView2/2/w/1200/format/webp)
参考：
 [https://blog.csdn.net/jb84006/article/details/117634375](https://links.jianshu.com/go?to=https%3A%2F%2Fblog.csdn.net%2Fjb84006%2Farticle%2Fdetails%2F117634375)
[https://www.cnblogs.com/wtzbk/p/14366240.html](https://links.jianshu.com/go?to=https%3A%2F%2Fwww.cnblogs.com%2Fwtzbk%2Fp%2F14366240.html)
作者：小波同学
链接：https://www.jianshu.com/p/f95cb0c0d23f
来源：简书
著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。
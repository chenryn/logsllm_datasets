```
定义一个REST接口，调用的时候，发送一个消息
#### 测试
我们进入RabbitAdmin页面  `http://localhost:15672`
![image-20200414095920920](images/image-20200414095920920.png)
会发现它已经成功创建了一个studyExchange的交换机，这个就是我们上面配置的
```
      bindings: # 服务的整合处理
        output: # 这个名字是一个通道的名称
          destination: studyExchange # 表示要使用的exchange名称定义
          content-type: application/json # 设置消息类型，本次为json，文本则设为text/plain
          binder: defaultRabbit # 设置要绑定的消息服务的具体设置
```
以后就会通过这个交换机进行消息的消费
我们运行下列代码，进行测试消息发送 `http://localhost:8801/sendMessage`
能够发现消息已经成功被RabbitMQ捕获，这个时候就完成了消息的发送
![image-20200414100125220](images/image-20200414100125220.png)
## 消息驱动之消费者
### 引入依赖
```
    org.springframework.cloud
    spring-cloud-starter-stream-rabbit
```
### 修改yml
```
spring:
  application:
    name: cloud-stream-consumer
  cloud:
    stream:
      binders: # 在此处配置要绑定的rabbitMQ的服务信息
        defaultRabbit: # 表示定义的名称，用于binding的整合
          type: rabbit # 消息中间件类型
          environment: # 设置rabbitMQ的相关环境配置
            spring:
              rabbitmq:
                host: localhost
                port: 5672
                username: guest
                password: guest
      bindings: # 服务的整合处理
        input: # 这个名字是一个通道的名称
          destination: studyExchange # 表示要使用的exchange名称定义
          content-type: application/json # 设置消息类型，本次为json，文本则设为text/plain
          binder: defaultRabbit # 设置要绑定的消息服务的具体设置
          group: atguiguA
```
### 业务类
```
@Component
@EnableBinding(Sink.class)  // 绑定通道
public class ReceiveMessageListenerController {
    @Value("${server.port}")
    private String serverPort;
    // 监听队列，用于消费者队列的消息接收
    @StreamListener(Sink.INPUT)
    public void input(Message message) {
        System.out.println("消费者1号，0------>接收到消息："+message.getPayload()+"\t port:"+serverPort);
    }
}
```
## 分组消费
我们在创建一个8803的消费者服务，需要启动的服务
- RabbitMQ：消息中间件
- 7001：服务注册
- 8801：消息生产
- 8802：消息消费
- 8803：消息消费
### 运行后有两个问题
- 有重复消费问题
- 消息持久化问题
### 消费
目前8802 、8803同时都收到了，存在重复消费的问题
如何解决：使用分组和持久化属性 group来解决
比如在如下场景中，订单系统我们做集群部署，都会从RabbitMQ中获取订单信息，那如果一个订单同时被两个服务获取到，那么就会造成数据错误，我们得避免这种情况，这时我们就可以使用Stream中的消息分组来解决。
![image-20200414123004267](images/image-20200414123004267.png)
注意：在Stream中处于同一个group中的多个消费者是竞争关系，就能够保证消息只能被其中一个消费一次
不同组是可以全面消费的（重复消费）
同一组会发生竞争关系，只能其中一个可以消费
分布式微服务应用为了实现高可用和负载均衡，实际上都会部署多个实例，这里部署了8802 8803
多数情况下，生产者发送消息给某个具体微服务时，只希望被消费一次，按照上面我们启动两个应用的例子，虽然它们同属一个应用，但是这个消息出现了被重复消费两次的情况，为了解决这个情况，在SpringCloudStream中，就提供了 消费组 的概念
![image-20200414130034279](images/image-20200414130034279.png)
### 分组
#### 原理
微服务应用放置于同一个group中，就能够保证消息只会被其中一个应用消费一次，不同的组是可以消费的，同一组内会发生竞争关系，只有其中一个可以被消费。
我们将8802和8803划分为同一组
```yml
spring:
  application:
    name: cloud-stream-consumer
  cloud:
    stream:
      binders: # 在此处配置要绑定的rabbitMQ的服务信息
        defaultRabbit: # 表示定义的名称，用于binding的整合
          type: rabbit # 消息中间件类型
          environment: # 设置rabbitMQ的相关环境配置
            spring:
              rabbitmq:
                host: localhost
                port: 5672
                username: guest
                password: guest
      bindings: # 服务的整合处理
        input: # 这个名字是一个通道的名称
          destination: studyExchange # 表示要使用的exchange名称定义
          content-type: application/json # 设置消息类型，本次为json，文本则设为text/plain
          binder: defaultRabbit # 设置要绑定的消息服务的具体设置
          group: atguiguA
```
引入：`group: atguiguA `
然后我们执行消息发送的接口：`http://localhost:8801/sendMessage`
我们在8801服务，同时发送了6条消息
![image-20200414125203160](images/image-20200414125203160.png)
然后看8802服务，接收到了3条
![image-20200414125231537](images/image-20200414125231537.png)
8803服务，也接收到了3条
![image-20200414125243408](images/image-20200414125243408.png)
这个时候，就通过分组，避免了消息的重复消费问题
8802、8803通过实现轮询分组，每次只有一个消费者，最后发送的消息只能够被一个接受
如果将他们的group变成两个不同的组，那么消息就会被重复消费
## 消息持久化
通过上面的方式，我们解决了重复消费的问题，再看看持久化
### 案例
- 停止8802和8803，并移除8802的group，保留8803的group
- 8801先发送4条消息到RabbitMQ
- 先启动8802，无分组属性，后台没有打出来消息
- 在启动8803，有分组属性，后台打出来MQ上的消息
这就说明消息已经被持久化了，等消费者登录后，会自动从消息队列中获取消息进行消费
![image-20200414131334047](images/image-20200414131334047.png)
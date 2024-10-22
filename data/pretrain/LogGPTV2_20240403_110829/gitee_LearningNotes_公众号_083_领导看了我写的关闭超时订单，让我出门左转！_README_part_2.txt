public class OrderMQReciever {
    @RabbitHandler
    public void process(String message){
        System.out.println("OrderMQReciever接收到的消息是："+ message);
    }
}
```
#### 测试
通过调用接口，发现10秒之后才会消费消息
![图片](images/640-16500700567652.png)
## 问题升级
由于开发环境和测试环境使用的是同一个交换机和队列，所以发送的延时时间都是30分钟。但是为了在测试环境让测试同学方便测试，故手动将测试环境的时间改为了1分钟。
#### 问题复现
接着问题就来了：延时时间为1分钟的消息并没有立即被消费，而是等30分钟的消息被消费完之后才被消费了。至于原因，我们下边再分析，先用代码来给大家复现下该问题。
```
@GetMapping("/sendManyMessage")
public String sendManyMessage(){
    send("延迟消息睡10秒",10000+"");
    send("延迟消息睡2秒",2000+"");
    send("延迟消息睡5秒",5000+"");
    return "ok";
}
private void send(String msg, String delayTime){
 rabbitTemplate.convertAndSend(DelayQueueRabbitConfig.ORDER_EXCHANGE, 
                                  DelayQueueRabbitConfig.ORDER_ROUTING_KEY,
                                  msg,message->{
                                      message.getMessageProperties().setExpiration(delayTime);
                                      return message;
                                  });
}
```
执行结果如下：
```
OrderMQReciever接收到的消息是：延迟消息睡10秒
OrderMQReciever接收到的消息是：延迟消息睡2秒
OrderMQReciever接收到的消息是：延迟消息睡5秒
```
原因就是延时队列也满足队列先进先出的特征，当10秒的消息未出队列时，后边的消息不能顺利出队，造成后边的消息阻塞了，未能达到精准延时。
#### 问题解决
我们可以利用`x-delay-message`插件来解决该问题
> 消息的延迟范围是 Delay > 0, Delay = 官网下载：https://www.rabbitmq.com/community-plugins.html
我这边使用的是`v3.8.0.ez`，将文件下载下来放到服务器的`/usr/local/soft/rabbitmq_server-3.7.14/plugins` 路径下，执行`rabbitmq-plugins enable rabbitmq_delayed_message_exchange`命令即可。
![图片](images/640-16500700567654.png)
![图片](images/640-16500700567655.png)
出现如图所示，代表安装成功。
**配置类**
```
@Configuration
public class XDelayedMessageConfig {
    public static final String DIRECT_QUEUE = "queue.direct";//队列
    public static final String DELAYED_EXCHANGE = "exchange.delayed";//延迟交换机
    public static final String ROUTING_KEY = "routingkey.bind";//绑定的routing-key
    /**
     * 定义队列
     **/
    @Bean
    public Queue directQueue(){
        return new Queue(DIRECT_QUEUE,true);
    }
    /**
     * 定义延迟交换机
     * args:根据该参数进行灵活路由，设置为“direct”，意味着该插件具有与直连交换机具有相同的路由行为，
     * 如果想要不同的路由行为，可以更换现有的交换类型如：“topic”
     * 交换机类型为 x-delayed-message
     **/
    @Bean
    public CustomExchange delayedExchange(){
        Map args = new HashMap();
        args.put("x-delayed-type", "direct");
        return new CustomExchange(DELAYED_EXCHANGE, "x-delayed-message", true, false, args);
    }
    /**
     * 队列和延迟交换机绑定
     **/
    @Bean
    public Binding orderBinding() {
        return BindingBuilder.bind(directQueue()).to(delayedExchange()).with(ROUTING_KEY).noargs();
    }
}
```
**发送消息**
```
@RestController
@RequestMapping("/delayed")
public class DelayedSendMessageController {
    @Autowired
    private RabbitTemplate rabbitTemplate;
    @GetMapping("/sendManyMessage")
    public String sendManyMessage(){
        send("延迟消息睡10秒",10000);
        send("延迟消息睡2秒",2000);
        send("延迟消息睡5秒",5000);
        return "ok";
    }
    private void send(String msg, Integer delayTime){
        //将消息携带路由键值
        rabbitTemplate.convertAndSend(
                XDelayedMessageConfig.DELAYED_EXCHANGE,
                XDelayedMessageConfig.ROUTING_KEY,
                msg,
                message->{
                    message.getMessageProperties().setDelay(delayTime);
                    return message;
                });
    }
}
```
**消费消息**
```
@Component
@RabbitListener(queues = XDelayedMessageConfig.DIRECT_QUEUE)//监听队列名称
public class DelayedMQReciever {
    @RabbitHandler
    public void process(String message){
        System.out.println("DelayedMQReciever接收到的消息是："+ message);
    }
}
```
**测试**
```
DelayedMQReciever接收到的消息是：延迟消息睡2秒
DelayedMQReciever接收到的消息是：延迟消息睡5秒
DelayedMQReciever接收到的消息是：延迟消息睡10秒
```
这样我们的问题就顺利解决了。
#### 局限性
延迟的消息存储在一个`Mnesia`表中，当前节点上只有一个磁盘副本，它们将在节点重启后存活。
虽然触发计划交付的计时器不会持久化，但它将在节点启动时的插件激活期间重新初始化。显然，集群中只有一个预定消息的副本意味着丢失该节点或禁用其上的插件将丢失驻留在该节点上的消息。
该插件的当前设计并不适合延迟消息数量较多的场景（如数万条或数百万条），另外该插件的一个可变性来源是依赖于 `Erlang` 计时器，在系统中使用了一定数量的长时间计时器之后，它们开始争用调度程序资源，并且时间漂移不断累积。
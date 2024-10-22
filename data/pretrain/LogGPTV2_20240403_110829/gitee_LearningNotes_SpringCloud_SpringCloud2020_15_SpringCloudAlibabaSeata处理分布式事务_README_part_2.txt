    serverAddr = "localhost:6379"
    db = "0"
  }
  zk {
    cluster = "default"
    serverAddr = "127.0.0.1:2181"
    session.timeout = 6000
    connect.timeout = 2000
  }
  consul {
    cluster = "default"
    serverAddr = "127.0.0.1:8500"
  }
  etcd3 {
    cluster = "default"
    serverAddr = "http://localhost:2379"
  }
  sofa {
    serverAddr = "127.0.0.1:9603"
    application = "default"
    region = "DEFAULT_ZONE"
    datacenter = "DefaultDataCenter"
    cluster = "default"
    group = "SEATA_GROUP"
    addressWaitTime = "3000"
  }
  file {
    name = "file.conf"
  }
}
config {
  # file、nacos 、apollo、zk、consul、etcd3
  type = "file"
  nacos {
    serverAddr = "localhost"
    namespace = ""
  }
  consul {
    serverAddr = "127.0.0.1:8500"
  }
  apollo {
    app.id = "seata-server"
    apollo.meta = "http://192.168.1.204:8801"
  }
  zk {
    serverAddr = "127.0.0.1:2181"
    session.timeout = 6000
    connect.timeout = 2000
  }
  etcd3 {
    serverAddr = "http://localhost:2379"
  }
  file {
    name = "file.conf"
  }
}
```
#### domain
```
@Data
@AllArgsConstructor
@NoArgsConstructor
public class CommonResult
{
    private Integer code;
    private String  message;
    private T       data;
    public CommonResult(Integer code, String message)
    {
        this(code,message,null);
    }
}
@Data
@AllArgsConstructor
@NoArgsConstructor
public class Order
{
    private Long id;
    private Long userId;
    private Long productId;
    private Integer count;
    private BigDecimal money;
    private Integer status; //订单状态：0：创建中；1：已完结
}
```
#### Dao接口及实现
```
@Mapper
public interface OrderDao
{
    //1 新建订单
    void create(Order order);
    //2 修改订单状态，从零改为1
    void update(@Param("userId") Long userId,@Param("status") Integer status);
}
```
```
        insert into t_order (id,user_id,product_id,count,money,status)
        values (null,#{userId},#{productId},#{count},#{money},0);
        update t_order set status = 1
        where user_id=#{userId} and status = #{status};
```
#### Service实现类
OrderService接口
```
public interface OrderService
{
    void create(Order order);
}
```
StorageService的Feign接口，
```
@FeignClient(value = "seata-storage-service")
public interface StorageService
{
    @PostMapping(value = "/storage/decrease")
    CommonResult decrease(@RequestParam("productId") Long productId, @RequestParam("count") Integer count);
}
```
AccountService的Feign接口，账户接口
```
@FeignClient(value = "seata-account-service")
public interface AccountService
{
    @PostMapping(value = "/account/decrease")
    CommonResult decrease(@RequestParam("userId") Long userId, @RequestParam("money") BigDecimal money);
}
```
OrderServiceImpl实现类
```
@Service
@Slf4j
public class OrderServiceImpl implements OrderService
{
    @Resource
    private OrderDao orderDao;
    @Resource
    private StorageService storageService;
    @Resource
    private AccountService accountService;
    /**
     * 创建订单->调用库存服务扣减库存->调用账户服务扣减账户余额->修改订单状态
     * 简单说：下订单->扣库存->减余额->改状态
     */
    @Override
    @GlobalTransactional(name = "fsp-create-order",rollbackFor = Exception.class)
    public void create(Order order)
    {
        log.info("----->开始新建订单");
        //1 新建订单
        orderDao.create(order);
        //2 扣减库存
        log.info("----->订单微服务开始调用库存，做扣减Count");
        storageService.decrease(order.getProductId(),order.getCount());
        log.info("----->订单微服务开始调用库存，做扣减end");
        //3 扣减账户
        log.info("----->订单微服务开始调用账户，做扣减Money");
        accountService.decrease(order.getUserId(),order.getMoney());
        log.info("----->订单微服务开始调用账户，做扣减end");
        //4 修改订单状态，从零到1,1代表已经完成
        log.info("----->修改订单状态开始");
        orderDao.update(order.getUserId(),0);
        log.info("----->修改订单状态结束");
        log.info("----->下订单结束了，O(∩_∩)O哈哈~");
    }
}
```
#### 业务类
```
@RestController
public class OrderController
{
    @Resource
    private OrderService orderService;
    @GetMapping("/order/create")
    public CommonResult create(Order order)
    {
        orderService.create(order);
        return new CommonResult(200,"订单创建成功");
    }
}
```
#### Config配置
Mybatis DataSourceProxyConfig配置，这里是使用Seata对数据源进行代理
```
@Configuration
public class DataSourceProxyConfig {
    @Value("${mybatis.mapperLocations}")
    private String mapperLocations;
    @Bean
    @ConfigurationProperties(prefix = "spring.datasource")
    public DataSource druidDataSource(){
        return new DruidDataSource();
    }
    @Bean
    public DataSourceProxy dataSourceProxy(DataSource dataSource) {
        return new DataSourceProxy(dataSource);
    }
    @Bean
    public SqlSessionFactory sqlSessionFactoryBean(DataSourceProxy dataSourceProxy) throws Exception {
        SqlSessionFactoryBean sqlSessionFactoryBean = new SqlSessionFactoryBean();
        sqlSessionFactoryBean.setDataSource(dataSourceProxy);
        sqlSessionFactoryBean.setMapperLocations(new PathMatchingResourcePatternResolver().getResources(mapperLocations));
        sqlSessionFactoryBean.setTransactionFactory(new SpringManagedTransactionFactory());
        return sqlSessionFactoryBean.getObject();
    }
}
```
Mybatis配置
```
@Configuration
@MapperScan({"com.atguigu.springcloud.alibaba.dao"})
public class MyBatisConfig {
}
```
#### 启动类
```
@EnableDiscoveryClient
@EnableFeignClients
@SpringBootApplication(exclude = DataSourceAutoConfiguration.class)//取消数据源的自动创建
public class SeataOrderMainApp2001
{
    public static void main(String[] args)
    {
        SpringApplication.run(SeataOrderMainApp2001.class, args);
    }
}
```
### 新建Storage-Module
参考项目：seata-storage-service2002
### 新建账户Account-Module
参考项目：seata-account-service2003
### 测试
#### 数据库初始情况
![image-20200417225230939](images/image-20200417225230939.png)
#### 正常下单
访问
```
http://localhost:2001/order/create?userId=1&productId=1&count=10&money=100
```
![image-20200417225932063](images/image-20200417225932063.png)
#### 超时异常，没加@GlobalTransaction
我们在account-module模块，添加睡眠时间20秒，因为openFeign默认时间是1秒
![image-20200417230124982](images/image-20200417230124982.png)
出现了数据不一致的问题
故障情况
- 当库存和账户金额扣减后，订单状态并没有设置成已经完成，没有从零改成1
- 而且由于Feign的重试机制，账户余额还有可能被多次扣除
#### 超时异常，添加@GlobalTransaction
```
@GlobalTransactional(name = "fsp-create-order",rollbackFor = Exception.class)
```
rollbackFor表示，什么什么错误就会回滚
添加这个后，发现下单后的数据库并没有改变，记录都添加不进来
## 一部分补充
### Seata
2019年1月份，蚂蚁金服和阿里巴巴共同开源的分布式事务解决方案
Seata：Simple Extensible Autonomous Transaction Architecture，简单可扩展自治事务框架
2020起始，参加工作以后用1.0以后的版本。
### 再看TC/TM/RM三大组件
![image-20200417231145550](images/image-20200417231145550.png)
什么是TC，TM，RM
TC：seata服务器
TM：带有@GlobalTransaction注解的方法
RM：数据库，也就是事务参与方
![image-20200417231314748](images/image-20200417231314748.png)
### 分布式事务的执行流程
- TM开启分布式事务（TM向TC注册全局事务记录），相当于注解 `@GlobelTransaction`注解
- 按业务场景，编排数据库，服务等事务内部资源（RM向TC汇报资源准备状态）
- TM结束分布式事务，事务一阶段结束（TM通知TC提交、回滚分布式事务）
- TC汇总事务信息，决定分布式事务是提交还是回滚
- TC通知所有RM提交、回滚资源，事务二阶段结束
### AT模式如何做到对业务的无侵入
默认AT模式，阿里云GTS
### AT模式
#### 前提
- 基于支持本地ACID事务的关系型数据库
- Java应用，通过JDBC访问数据库
#### 整体机制
两阶段提交协议的演变
- 一阶段：业务数据和回滚日志记录在同一个本地事务中提交，释放本地锁和连接资源
- 二阶段
  - 提交异步化，非常快速的完成
  - 回滚通过一阶段的回滚日志进行反向补偿
#### 一阶段加载
在一阶段，Seata会拦截 业务SQL
- 解析SQL语义，找到业务SQL，要更新的业务数据，在业务数据被更新前，将其保存成 `before image（前置镜像）`
- 执行业务SQL更新业务数据，在业务数据更新之后
- 将其保存成 after image，最后生成行锁
以上操作全部在一个数据库事务内完成，这样保证了一阶段操作的原子性
![image-20200417232316157](images/image-20200417232316157.png)
#### 二阶段提交
二阶段如果顺利提交的话，因为业务SQL在一阶段已经提交至数据库，所以Seata框架只需将一阶段保存的快照和行锁删除掉，完成数据清理即可
![image-20200417232502282](images/image-20200417232502282.png)
#### 二阶段回滚
二阶段如果回滚的话，Seata就需要回滚到一阶段已经执行的 业务SQL，还原业务数据
回滚方式便是用 before image 还原业务数据，但是在还原前要首先校验脏写，对比数据库当前业务数据 和after image，如果两份数据完全一致，没有脏写，可以还原业务数据，如果不一致说明有脏读，出现脏读就需要转人工处理
![image-20200417232859708](images/image-20200417232859708.png)
#### 总结
![image-20200417233926182](images/image-20200417233926182.png)
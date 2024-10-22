下文是本次demo的代码，orm使用jpa,因此dao层和pojo的代码就没在文中写了。controller层只有一个接口，通过传参来选择是否使用锁。
> **表结构**
商品表 **product**
```sql
CREATE TABLE `product` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `amount` int DEFAULT NULL,
  PRIMARY KEY (`id`)
)
```
购买记录表 **purchase_history**
```sql
CREATE TABLE `purchase_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_name` varchar(255) DEFAULT NULL,
  `purchaser` varchar(255) DEFAULT NULL,
  `purchase_time` datetime DEFAULT NULL,
  `amount` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) 
```
> **pom.xml**
```xml
        org.springframework.boot
        spring-boot-starter-web
        org.springframework.boot
        spring-boot-starter-data-redis
        org.projectlombok
        lombok
        org.springframework.boot
        spring-boot-starter-data-jpa
        mysql
        mysql-connector-java
        org.springframework.boot
        spring-boot-starter-test
        test
        junit
        junit
```
> **application.yml**
```yaml
server:
  port: 8001
spring:
  redis:
    host: localhost
    port: 6379
 datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver
    url: jdbc:mysql://localhost:3306/demo
    username: root
    password: password
```
> **ProductController.java**
```java
@RestController
@RequestMapping("/product")
public class ProductController {
    public final static String PRODUCT_APPLE="apple";
    private final BuyService buyService;
    public ProductController(BuyService buyService){
        this.buyService=buyService;
    }
    /**
 * 购买商品
 * @param lock 是否有锁 Y/N
 */ @GetMapping("/buy")
    public void buy(@RequestParam(value = "lock",required = false) String lock)throws Exception{
       if("Y".equals(lock)){
           buyService.buyProductWithLock(PRODUCT_APPLE);
       }else {
           buyService.buyProduct(PRODUCT_APPLE);
       }
    }
}
```
> **BuyService.java**
```java
@Service
public class BuyService {
    private final ProductDao productDao;
    private final PurchaseHistoryDao purchaseHistoryDao;
    private final LockService lockService;
    public BuyService(ProductDao productDao, PurchaseHistoryDao purchaseHistoryDao, LockService lockService) {
        this.productDao = productDao;
        this.purchaseHistoryDao = purchaseHistoryDao;
        this.lockService = lockService;
    }
    /**
 * 购买：无锁
 * @param productName
 */
 public void buyProduct(String productName) {
        Product product = productDao.findOneByName(productName);
        if (product.getAmount() > 0) {
            //库存减1
            product.setAmount(product.getAmount() - 1);
            productDao.save(product);
            //记录日志
            PurchaseHistory purchaseHistory = new PurchaseHistory();
            purchaseHistory.setProductName(productName);
            purchaseHistory.setAmount(1);
            purchaseHistoryDao.save(purchaseHistory);
        }
    }
    /**
 * 购买：有锁
 * @param productName
 */
 public void buyProductWithLock(String productName) throws Exception{
        String uuid = UUID.randomUUID().toString();
        //加锁
        while (true) {
            if (lockService.lock(productName, uuid)) {
                break;
            }
            Thread.sleep(100);
        }
        Product product = productDao.findOneByName(productName);
        if (product.getAmount() > 0) {
            //库存减1
            product.setAmount(product.getAmount() - 1);
            productDao.save(product);
            //记录日志
            PurchaseHistory purchaseHistory = new PurchaseHistory();
            purchaseHistory.setProductName(productName);
            purchaseHistory.setAmount(1);
            purchaseHistoryDao.save(purchaseHistory);
        }
        lockService.unlock(productName, uuid);
    }
}
```
> **LockService.java**
```java
@Service
public class LockService {
    private final StringRedisTemplate stringRedisTemplate;
    public LockService(StringRedisTemplate stringRedisTemplate) {
        this.stringRedisTemplate = stringRedisTemplate;
    }
    /**
 * 加锁
 * @param lockKey
 * @param requestId
 * @return
 */
 public boolean lock(String lockKey, String requestId) {
        return stringRedisTemplate
 .opsForValue()
                .setIfAbsent(lockKey, requestId, Duration.ofSeconds(3));
    }
    /**
 * 解锁
 * @param lockKey
 * @param requestId
 */
 public void unlock(String lockKey, String requestId) {
        DefaultRedisScript script = new DefaultRedisScript<>();
        script.setResultType(Long.class);
        script.setScriptText("if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end");
        stringRedisTemplate.execute(script, Collections.singletonList(lockKey), requestId);
    }
}
```
### 4.2.测试和分析
测试用例中，商品的初始库存是100份，模拟200个用户购买，按道理来说最终只能购买100份。
我们想要模拟测试“有锁”和“无锁”下的区别，就必须得创建“高并行”的条件，这里要记住是“高并行”，不是“高并发”。因为这里的购买接口，一次请求响应还是很快的，要想模拟出多个用户同时调用接口的情况，本地应该用多线程来模拟。
关于模拟高并行的环境，我做过很多尝试。第一次是写Junit测试用例，起200个线程来调用接口，结果发现线程一多服务就挂了，虽然没弄清楚缘由，但Junit应该不是这么用的。第二次是使用postman来做并发的接口测试，但发现postman是假的并发测试，还是由单线程轮流调用200遍接口，并没有实现多线程。最终还是安装了JMeter，达到了我的期望。
当我们分别起200个线程调用无锁和有锁接口时，测试结果如下：
| 对比     | 无锁 | 有锁 |
| -------- | ---- | ---- |
| 剩余库存 | 68   | 0    |
| 购买记录 | 200  | 100  |
可以看到，无锁的情况下是会有“超卖”问题的，我们再来看看无锁的购买代码。
```java
/**
 * 购买：无锁
 * @param productName
 */
 public synchronized void buyProduct(String productName) {
        Product product = productDao.findOneByName(productName);
        if (product.getAmount() > 0) {
            //库存减1
 product.setAmount(product.getAmount() - 1);
            productDao.save(product);
            //记录日志
 PurchaseHistory purchaseHistory = new PurchaseHistory();
            purchaseHistory.setProductName(productName);
            purchaseHistory.setAmount(1);
            purchaseHistoryDao.save(purchaseHistory);
        }
    }
```
当多个请求同时调用`productDao.findOneByName(productName);`，查出来的结果一样，都认为还有库存，都去购买，超卖的问题就出现了。解决这个问题，如果是单进程，通过`synchronized`之类的锁就解决了。如果是分布式多节点，可以考虑本文的方式，使用redis的分布式锁实现。
今天，我来和你聊聊业务代码中与数据库事务相关的坑。
**Spring** 针对 **Java** **Transaction API** (**JTA**)、**JDBC**、**Hibernate** 和 **Java Persistence API (JPA)** 等事务 **API**，实现了一致的编程模型，而 **Spring** 的声明式事务功能更是提供了极其方便的事务配置方式，配合 **Spring Boot** 的自动配置，大多数 **Spring Boot** 项目只需要在方法上标记 **@Transactional** 注解，即可一键开启方法的事务性配置。
据我观察，大多数业务开发同学都有事务的概念，也知道如果整体考虑多个数据库操作要么成功要么失败时，需要通过数据库事务来实现多个操作的一致性和原子性。但，在使用上大多仅限于为方法标记 **@Transactional**，不会去关注事务是否有效、出错后事务是否正确回滚，也不会考虑复杂的业务代码中涉及多个子业务逻辑时，怎幺正确处理事务。
事务没有被正确处理，一般来说不会过于影响正常流程，也不容易在测试阶段被发现。但当系统越来越复杂、压力越来越大之后，就会带来大量的数据不一致问题，随后就是大量的人工介入查看和修复数据。
所以说，一个成熟的业务系统和一个基本可用能完成功能的业务系统，在事务处理细节上的差异非常大。要确保事务的配置符合业务功能的需求，往往不仅仅是技术问题，还涉及产品流程和架构设计的问题。今天这一讲的标题“ **20% 的业务代码的 Spring 声明式事务，可能都没处理正确** ”中，20% 这个数字在我看来还是比较保守的。
我今天要分享的内容，就是帮助你在技术问题上理清思路，避免因为事务处理不当让业务逻辑的实现产生大量偶发 Bug。
## 小心 Spring 的事务可能没有生效
在使用 **@Transactional** 注解开启声明式事务时， 第一个最容易忽略的问题是，很可能事务并没有生效。
实现下面的 **Demo** 需要一些基础类，首先定义一个具有 ID 和姓名属性的 **UserEntity**，也就是一个包含两个字段的用户表：
```
@Entity
@Data
public class UserEntity {
    @Id
    @GeneratedValue(strategy = AUTO)
    private Long id;
    private String name;
    public UserEntity() { }
    public UserEntity(String name) {
        this.name = name;
    }
}
```
为了方便理解，我使用 **Spring JPA** 做数据库访问，实现这样一个 **Repository**，新增一个根据用户名查询所有数据的方法：
```
@Repository
public interface UserRepository extends JpaRepository {
    List findByName(String name);
}
```
定义一个 **UserService** 类，负责业务逻辑处理。如果不清楚 **@Transactional** 的实现方式，只考虑代码逻辑的话，这段代码看起来没有问题。
定义一个入口方法 **createUserWrong1** 来调用另一个私有方法 **createUserPrivate**，私有方法上标记了 **@Transactional** 注解。当传入的用户名包含 **test** 关键字时判断为用户名不合法，抛出异常，让用户创建操作失败，期望事务可以回滚：
```java
@Service
@Slf4j
public class UserService {
    @Autowired
    private UserRepository userRepository;
    //一个公共方法供Controller调用，内部调用事务性的私有方法
    public int createUserWrong1(String name) {
        try {
            this.createUserPrivate(new UserEntity(name));
        } catch (Exception ex) {
            log.error("create user failed because {}", ex.getMessage());
        }
        return userRepository.findByName(name).size();
    }
    //标记了@Transactional的private方法
    @Transactional
    private void createUserPrivate(UserEntity entity) {
        userRepository.save(entity);
        if (entity.getName().contains("test"))
            throw new RuntimeException("invalid username!");
    }
    //根据用户名查询用户数
    public int getUserCount(String name) {
        return userRepository.findByName(name).size();
    }
}
```
下面是 **Controller** 的实现，只是调用一下刚才定义的 **UserService** 中的入口方法 **createUserWrong1**。
```java
@Autowired
private UserService userService;
@GetMapping("wrong1")
public int wrong1(@RequestParam("name") String name) {
    return userService.createUserWrong1(name);
}
```
调用接口后发现，即便用户名不合法，用户也能创建成功。刷新浏览器，多次发现有十几个的非法用户注册。
这里给出 **@Transactional** 生效原则 1，除非特殊配置（比如使用 **AspectJ** 静态织入实现 **AOP**），否则只有定义在 **public** 方法上的 **@Transactional** 才能生效。原因是，**Spring** 默认通过动态代理的方式实现 **AOP**，对目标方法进行增强，**private** 方法无法代理到，**Spring** 自然也无法动态增强事务处理逻辑。
你可能会说，修复方式很简单，把标记了事务注解的 **createUserPrivate** 方法改为 **public** 即可。在 **UserService** 中再建一个入口方法 **createUserWrong2**，来调用这个 **public** 方法再次尝试：
```java
public int createUserWrong2(String name) {
    try {
        this.createUserPublic(new UserEntity(name));
    } catch (Exception ex) {
        log.error("create user failed because {}", ex.getMessage());
    }
  return userRepository.findByName(name).size();
}
//标记了@Transactional的public方法
@Transactional
public void createUserPublic(UserEntity entity) {
    userRepository.save(entity);
    if (entity.getName().contains("test"))
        throw new RuntimeException("invalid username!");
}
```
测试发现，调用新的 **createUserWrong2** 方法事务同样不生效。这里，我给出 **@Transactional** 生效原则 2，必须通过代理过的类从外部调用目标方法才能生效。
**Spring** 通过 AOP 技术对方法进行增强，要调用增强过的方法必然是调用代理后的对象。我们尝试修改下 **UserService** 的代码，注入一个 **self**，然后再通过 self 实例调用标记有 **@Transactional** 注解的 **createUserPublic** 方法。设置断点可以看到，**self** 是由 Spring 通过 **CGLIB** 方式增强过的类：
**CGLIB** 通过继承方式实现代理类，**private** 方法在子类不可见，自然也就无法进行事务增强；
this 指针代表对象自己，Spring 不可能注入 this，所以通过 this 访问方法必然不是代理。
![img](images/b077c033fa394353309fbb4f8368e46c.png)
把 this 改为 self 后测试发现，在 Controller 中调用 createUserRight 方法可以验证事务是生效的，非法的用户注册操作可以回滚。
虽然在 UserService 内部注入自己调用自己的 createUserPublic 可以正确实现事务，但更合理的实现方式是，让 Controller 直接调用之前定义的 UserService 的 createUserPublic 方法，因为注入自己调用自己很奇怪，也不符合分层实现的规范：
```
@GetMapping("right2")
public int right2(@RequestParam("name") String name) {
    try {
        userService.createUserPublic(new UserEntity(name));
    } catch (Exception ex) {
        log.error("create user failed because {}", ex.getMessage());
    }
    return userService.getUserCount(name);
}
```
我们再通过一张图来回顾下 this 自调用、通过 self 调用，以及在 Controller 中调用 UserService 三种实现的区别：
![img](images/c43ea620b0b611ae194f8438506d7570.png)
通过 this 自调用，没有机会走到 Spring 的代理类；后两种改进方案调用的是 Spring 注入的 UserService，通过代理调用才有机会对 createUserPublic 方法进行动态增强。
这里，我还有一个小技巧，强烈建议你在开发时打开相关的 Debug 日志，以方便了解 Spring 事务实现的细节，并及时判断事务的执行情况。
我们的 Demo 代码使用 JPA 进行数据库访问，可以这么开启 Debug 日志：
```
logging.level.org.springframework.orm.jpa=DEBUG
```
开启日志后，我们再比较下在 UserService 中通过 this 调用和在 Controller 中通过注入的 UserService Bean 调用 createUserPublic 区别。很明显，this 调用因为没有走代理，事务没有在 createUserPublic 方法上生效，只在 Repository 的 save 方法层面生效：
```
//在UserService中通过this调用public的createUserPublic
[10:10:19.913] [http-nio-45678-exec-1] [DEBUG] [o.s.orm.jpa.JpaTransactionManager       :370 ] - Creating new transaction with name [org.springframework.data.jpa.repository.support.SimpleJpaRepository.save]: PROPAGATION_REQUIRED,ISOLATION_DEFAULT
//在Controller中通过注入的UserService Bean调用createUserPublic
[10:10:47.750] [http-nio-45678-exec-6] [DEBUG] [o.s.orm.jpa.JpaTransactionManager       :370 ] - Creating new transaction with name [org.geekbang.time.commonmistakes.transaction.demo1.UserService.createUserPublic]: PROPAGATION_REQUIRED,ISOLATION_DEFAULT
```
你可能还会考虑一个问题，这种实现在 Controller 里处理了异常显得有点繁琐，还不如直接把 createUserWrong2 方法加上 @Transactional 注解，然后在 Controller 中直接调用这个方法。这样一来，既能从外部（Controller 中）调用 UserService 中的方法，方法又是 public 的能够被动态代理 AOP 增强。
你可以试一下这种方法，但很容易就会踩第二个坑，即因为没有正确处理异常，导致事务即便生效也不一定能回滚。
## 事务即便生效也不一定能回滚
通过 AOP 实现事务处理可以理解为，使用 try…catch…来包裹标记了 @Transactional 注解的方法，当方法出现了异常并且满足一定条件的时候，在 catch 里面我们可以设置事务回滚，没有异常则直接提交事务。
这里的“一定条件”，主要包括两点。
第一，只有异常传播出了标记了 @Transactional 注解的方法，事务才能回滚。在 Spring 的 TransactionAspectSupport 里有个 invokeWithinTransaction 方法，里面就是处理事务的逻辑。可以看到，只有捕获到异常才能进行后续事务处理：
```
try {
   // This is an around advice: Invoke the next interceptor in the chain.
   // This will normally result in a target object being invoked.
   retVal = invocation.proceedWithInvocation();
}
catch (Throwable ex) {
   // target invocation exception
   completeTransactionAfterThrowing(txInfo, ex);
   throw ex;
}
finally {
   cleanupTransactionInfo(txInfo);
}
```
第二，默认情况下，出现 RuntimeException（非受检异常）或 Error 的时候，Spring 才会回滚事务。
打开 Spring 的 DefaultTransactionAttribute 类能看到如下代码块，可以发现相关证据，通过注释也能看到 Spring 这么做的原因，大概的意思是受检异常一般是业务异常，或者说是类似另一种方法的返回值，出现这样的异常可能业务还能完成，所以不会主动回滚；而 Error 或 RuntimeException 代表了非预期的结果，应该回滚：
```
/**
 * The default behavior is as with EJB: rollback on unchecked exception
 * ({@link RuntimeException}), assuming an unexpected outcome outside of any
 * business rules. Additionally, we also attempt to rollback on {@link Error} which
 * is clearly an unexpected outcome as well. By contrast, a checked exception is
 * considered a business exception and therefore a regular expected outcome of the
 * transactional business method, i.e. a kind of alternative return value which
 * still allows for regular completion of resource operations.
 * This is largely consistent with TransactionTemplate's default behavior,
 * except that TransactionTemplate also rolls back on undeclared checked exceptions
 * (a corner case). For declarative transactions, we expect checked exceptions to be
 * intentionally declared as business exceptions, leading to a commit by default.
 * @see org.springframework.transaction.support.TransactionTemplate#execute
 */
@Override
public boolean rollbackOn(Throwable ex) {
   return (ex instanceof RuntimeException || ex instanceof Error);
}
```
接下来，我和你分享 2 个反例。
重新实现一下 UserService 中的注册用户操作：
在 createUserWrong1 方法中会抛出一个 RuntimeException，但由于方法内 catch 了所有异常，异常无法从方法传播出去，事务自然无法回滚。
在 createUserWrong2 方法中，注册用户的同时会有一次 otherTask 文件读取操作，如果文件读取失败，我们希望用户注册的数据库操作回滚。虽然这里没有捕获异常，但因为 otherTask 方法抛出的是受检异常，createUserWrong2 传播出去的也是受检异常，事务同样不会回滚。
```
@Service
@Slf4j
public class UserService {
    @Autowired
    private UserRepository userRepository;
    //异常无法传播出方法，导致事务无法回滚
    @Transactional
    public void createUserWrong1(String name) {
        try {
            userRepository.save(new UserEntity(name));
            throw new RuntimeException("error");
        } catch (Exception ex) {
            log.error("create user failed", ex);
        }
    }
    //即使出了受检异常也无法让事务回滚
    @Transactional
    public void createUserWrong2(String name) throws IOException {
        userRepository.save(new UserEntity(name));
        otherTask();
    }
    //因为文件不存在，一定会抛出一个IOException
    private void otherTask() throws IOException {
        Files.readAllLines(Paths.get("file-that-not-exist"));
    }
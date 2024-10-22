  作为一个作用范围更广的缓存，它肯定是在SqlSession 的外层，否则不可能被多个SqlSession 共享。而一级缓存是在SqlSession 内部的，所以第一个问题，肯定是工作在一级缓存之前，也就是只有取不到二级缓存的情况下才到一个会话中去取一级缓存。第二个问题，二级缓存放在哪个对象中维护呢？ 要跨会话共享的话，SqlSession 本身和它里面的BaseExecutor 已经满足不了需求了，那我们应该在BaseExecutor 之外创建一个对象。
  实际上MyBatis 用了一个装饰器的类来维护，就是CachingExecutor。如果启用了二级缓存，MyBatis 在创建Executor 对象的时候会对Executor 进行装饰。CachingExecutor 对于查询请求，会判断二级缓存是否有缓存结果，如果有就直接返回，如果没有委派交给真正的查询器Executor 实现类，比如SimpleExecutor 来执行查询，再走到一级缓存的流程。最后会把结果缓存起来，并且返回给用户。
![img](images/1383365-20190628180149776-546074458.png)
  开启二级缓存的方法
第一步：配置 mybatis.configuration.cache-enabled=true，只要没有显式地设置cacheEnabled=false，都会用CachingExecutor 装饰基本的执行器。
第二步：在Mapper.xml 中配置标签：
```
```
基本上就是这样。这个简单语句的效果如下:
- 映射语句文件中的所有 select 语句的结果将会被缓存。
- 映射语句文件中的所有 insert、update 和 delete 语句会刷新缓存。
- 缓存会使用最近最少使用算法（LRU, Least Recently Used）算法来清除不需要的缓存。
- 缓存不会定时进行刷新（也就是说，没有刷新间隔）。
- 缓存会保存列表或对象（无论查询方法返回哪种）的 1024 个引用。
- 缓存会被视为读/写缓存，这意味着获取到的对象并不是共享的，可以安全地被调用者修改，而不干扰其他调用者或线程所做的潜在修改。
这个更高级的配置创建了一个 FIFO 缓存，每隔 60 秒刷新，最多可以存储结果对象或列表的 512 个引用，而且返回的对象被认为是只读的，因此对它们进行修改可能会在不同线程中的调用者产生冲突。可用的清除策略有：
- `LRU` – 最近最少使用：移除最长时间不被使用的对象。
- `FIFO` – 先进先出：按对象进入缓存的顺序来移除它们。
- `SOFT` – 软引用：基于垃圾回收器状态和软引用规则移除对象。
- `WEAK` – 弱引用：更积极地基于垃圾收集器状态和弱引用规则移除对象。
默认的清除策略是 LRU。
flushInterval（刷新间隔）属性可以被设置为任意的正整数，设置的值应该是一个以毫秒为单位的合理时间量。 默认情况是不设置，也就是没有刷新间隔，缓存仅仅会在调用语句时刷新。
size（引用数目）属性可以被设置为任意正整数，要注意欲缓存对象的大小和运行环境中可用的内存资源。默认值是 1024。
readOnly（只读）属性可以被设置为 true 或 false。只读的缓存会给所有调用者返回缓存对象的相同实例。 因此这些对象不能被修改。这就提供了可观的性能提升。而可读写的缓存会（通过序列化）返回缓存对象的拷贝。 速度上会慢一些，但是更安全，因此默认值是 false。
  注：二级缓存是事务性的。这意味着，当 SqlSession 完成并提交时，或是完成并回滚，但没有执行 flushCache=true 的 insert/delete/update 语句时，缓存会获得更新。
  Mapper.xml 配置了之后，select()会被缓存。update()、delete()、insert()会刷新缓存。：如果cacheEnabled=true，Mapper.xml 没有配置标签，还有二级缓存吗？（没有）还会出现CachingExecutor 包装对象吗？（会）
  只要cacheEnabled=true 基本执行器就会被装饰。有没有配置，决定了在启动的时候会不会创建这个mapper 的Cache 对象，只是最终会影响到CachingExecutorquery 方法里面的判断。如果某些查询方法对数据的实时性要求很高，不需要二级缓存，怎么办？我们可以在单个Statement ID 上显式关闭二级缓存（默认是true）：
```
```
  二级缓存验证（验证二级缓存需要先开启二级缓存）
 1、事务不提交，二级缓存不存在
```
System.out.println(mapper1.selectBlogById(1002));
// 事务不提交的情况下，二级缓存不会写入
// session1.commit();
System.out.println(mapper2.selectBlogById(1002));
```
  为什么事务不提交，二级缓存不生效？因为二级缓存使用TransactionalCacheManager（TCM）来管理，最后又调用了TransactionalCache 的getObject()、putObject 和commit()方法，TransactionalCache里面又持有了真正的Cache 对象，比如是经过层层装饰的PerpetualCache。在putObject 的时候，只是添加到了entriesToAddOnCommit 里面，只有它的commit()方法被调用的时候才会调用flushPendingEntries()真正写入缓存。它就是在DefaultSqlSession 调用commit()的时候被调用的。
2、使用不同的session 和mapper，验证二级缓存可以跨session 存在取消以上commit()的注释
3、在其他的session 中执行增删改操作，验证缓存会被刷新
```
System.out.println(mapper1.selectBlogById(1002));
//主键自增返回测试
Blog blog3 = new Blog();
blog3.setBid(1002);
blog3.setName("mybatis缓存机制");
mapper1.updateBlog(blog3);
session1.commit();
System.out.println(mapper2.selectBlogById(1002));
```
  为什么增删改操作会清空缓存？在CachingExecutor 的update()方法里面会调用flushCacheIfRequired(ms)，isFlushCacheRequired 就是从标签里面渠道的flushCache 的值。而增删改操作的flushCache 属性默认为true。
什么时候开启二级缓存？
一级缓存默认是打开的，二级缓存需要配置才可以开启。那么我们必须思考一个问题，在什么情况下才有必要去开启二级缓存？
1. 因为所有的增删改都会刷新二级缓存，导致二级缓存失效，所以适合在查询为主的应用中使用，比如历史交易、历史订单的查询。否则缓存就失去了意义。
2. 如果多个namespace 中有针对于同一个表的操作，比如Blog 表，如果在一个namespace 中刷新了缓存，另一个namespace 中没有刷新，就会出现读到脏数据的情况。所以，推荐在一个Mapper 里面只操作单表的情况使用。
  如果要让多个namespace 共享一个二级缓存，应该怎么做？跨namespace 的缓存共享的问题，可以使用来解决：
```
```
  cache-ref 代表引用别的命名空间的Cache 配置，两个命名空间的操作使用的是同一个Cache。在关联的表比较少，或者按照业务可以对表进行分组的时候可以使用。
  注意：在这种情况下，多个Mapper 的操作都会引起缓存刷新，缓存的意义已经不大了.
第三方缓存做二级缓存
  除了MyBatis 自带的二级缓存之外，我们也可以通过实现Cache 接口来自定义二级缓存。MyBatis 官方提供了一些第三方缓存集成方式，比如ehcache 和redis：https://github.com/mybatis/redis-cache ,这里就不过多介绍了。当然，我们也可以使用独立的缓存服务，不使用MyBatis 自带的二级缓存。
自定义缓存：
  除了上述自定义缓存的方式，你也可以通过实现你自己的缓存，或为其他第三方缓存方案创建适配器，来完全覆盖缓存行为。
```
```
  这个示例展示了如何使用一个自定义的缓存实现。type 属性指定的类必须实现 org.mybatis.cache.Cache 接口，且提供一个接受 String 参数作为 id 的构造器。 这个接口是 MyBatis 框架中许多复杂的接口之一，但是行为却非常简单。
```
public interface Cache {
  String getId();
  int getSize();
  void putObject(Object key, Object value);
  Object getObject(Object key);
  boolean hasKey(Object key);
  Object removeObject(Object key);
  void clear();
}
```
  为了对你的缓存进行配置，只需要简单地在你的缓存实现中添加公有的 JavaBean 属性，然后通过 cache 元素传递属性值，例如，下面的例子将在你的缓存实现上调用一个名为 `setCacheFile(String file)` 的方法：
```
```
  你可以使用所有简单类型作为 JavaBean 属性的类型，MyBatis 会进行转换。 你也可以使用占位符（如 `${cache.file}`），以便替换成在配置文件属性中定义的值。从版本 3.4.2 开始，MyBatis 已经支持在所有属性设置完毕之后，调用一个初始化方法。 如果想要使用这个特性，请在你的自定义缓存类里实现 `org.apache.ibatis.builder.InitializingObject` 接口。
```
public interface InitializingObject {
  void initialize() throws Exception;
}
```
  请注意，缓存的配置和缓存实例会被绑定到 SQL 映射文件的命名空间中。 因此，同一命名空间中的所有语句和缓存将通过命名空间绑定在一起。 每条语句可以自定义与缓存交互的方式，或将它们完全排除于缓存之外，这可以通过在每条语句上使用两个简单属性来达成。 默认情况下，语句会这样来配置：
```
```
  鉴于这是默认行为，显然你永远不应该以这样的方式显式配置一条语句。但如果你想改变默认的行为，只需要设置 flushCache 和 useCache 属性。比如，某些情况下你可能希望特定 select 语句的结果排除于缓存之外，或希望一条 select 语句清空缓存。类似地，你可能希望某些 update 语句执行时不要刷新缓存。
# MyBatis 缓存机制
## 来源
转载于 博客园  [吴振照](https://home.cnblogs.com/u/wuzhenzhao/) 的博客：https://www.cnblogs.com/wuzhenzhao/p/11103043.html
## 前言
  缓存是一般的ORM 框架都会提供的功能，目的就是提升查询的效率和减少数据库的压力。跟Hibernate 一样，MyBatis 也有一级缓存和二级缓存，并且预留了集成第三方缓存的接口。
  缓存体系结构：
MyBatis 跟缓存相关的类都在cache 包里面，其中有一个Cache 接口，只有一个默认的实现类 PerpetualCache，它是用HashMap 实现的。我们可以通过 以下类找到这个缓存的庐山真面目
**DefaultSqlSession**
  -> **BaseExecutor**
    -> **PerpetualCache** localCache
      ->**private Map cache = new HashMap();**
  除此之外，还有很多的装饰器，通过这些装饰器可以额外实现很多的功能：回收策略、日志记录、定时刷新等等。但是无论怎么装饰，经过多少层装饰，最后使用的还是基本的实现类（默认PerpetualCache）。可以通过 CachingExecutor 类 Debug 去查看。
![img](images/1383365-20190628165835198-1731504252.png)
  所有的缓存实现类总体上可分为三类：基本缓存、淘汰算法缓存、装饰器缓存。
![img](images/1383365-20190628172253737-1751427739.png)
## 一级缓存（本地缓存）
  一级缓存也叫本地缓存，MyBatis 的一级缓存是在会话（SqlSession）层面进行缓存的。MyBatis 的一级缓存是默认开启的，不需要任何的配置。首先我们必须去弄清楚一个问题，在MyBatis 执行的流程里面，涉及到这么多的对象，那么缓存PerpetualCache 应该放在哪个对象里面去维护？如果要在同一个会话里面共享一级缓存，这个对象肯定是在SqlSession 里面创建的，作为SqlSession 的一个属性。
  DefaultSqlSession 里面只有两个属性，Configuration 是全局的，所以缓存只可能放在Executor 里面维护——SimpleExecutor/ReuseExecutor/BatchExecutor 的父类BaseExecutor 的构造函数中持有了PerpetualCache。在同一个会话里面，多次执行相同的SQL 语句，会直接从内存取到缓存的结果，不会再发送SQL 到数据库。但是不同的会话里面，即使执行的SQL 一模一样（通过一个Mapper 的同一个方法的相同参数调用），也不能使用到一级缓存。
  每当我们使用MyBatis开启一次和数据库的会话，MyBatis会创建出一个SqlSession对象表示一次数据库会话。
  在对数据库的一次会话中，我们有可能会反复地执行完全相同的查询语句，如果不采取一些措施的话，每一次查询都会查询一次数据库,而我们在极短的时间内做了完全相同的查询，那么它们的结果极有可能完全相同，由于查询一次数据库的代价很大，这有可能造成很大的资源浪费。
  为了解决这一问题，减少资源的浪费，MyBatis会在表示会话的SqlSession对象中建立一个简单的缓存，将每次查询到的结果结果缓存起来，当下次查询的时候，如果判断先前有个完全一样的查询，会直接从缓存中直接将结果取出，返回给用户，不需要再进行一次数据库查询了。
  如下图所示，MyBatis会在一次会话的表示----一个SqlSession对象中创建一个本地缓存(local cache)，对于每一次查询，都会尝试根据查询的条件去本地缓存中查找是否在缓存中，如果在缓存中，就直接从缓存中取出，然后返回给用户；否则，从数据库读取数据，将查询结果存入缓存并返回给用户。
![img](images/1383365-20190628172851422-987384747.png)
一级缓存的生命周期有多长？
1. MyBatis在开启一个数据库会话时，会 创建一个新的SqlSession对象，SqlSession对象中会有一个新的Executor对象，Executor对象中持有一个新的PerpetualCache对象；当会话结束时，SqlSession对象及其内部的Executor对象还有PerpetualCache对象也一并释放掉。
2. 如果SqlSession调用了close()方法，会释放掉一级缓存PerpetualCache对象，一级缓存将不可用；
3. 如果SqlSession调用了clearCache()，会清空PerpetualCache对象中的数据，但是该对象仍可使用；
4. SqlSession中执行了任何一个update操作(update()、delete()、insert()) ，都会清空PerpetualCache对象的数据，但是该对象可以继续使用；
SqlSession 一级缓存的工作流程：
1. 对于某个查询，根据statementId,params,rowBounds来构建一个key值，根据这个key值去缓存Cache中取出对应的key值存储的缓存结果
2. 判断从Cache中根据特定的key值取的数据数据是否为空，即是否命中；
3. 如果命中，则直接将缓存结果返回；
4. 如果没命中：
1. 1. 去数据库中查询数据，得到查询结果；
   2. 将key和查询到的结果分别作为key,value对存储到Cache中；
   3. 将查询结果返回；
  接下来我们来验证一下，MyBatis 的一级缓存到底是不是只能在一个会话里面共享，以及跨会话（不同session）操作相同的数据会产生什么问题。判断是否命中缓存：如果再次发送SQL 到数据库执行，说明没有命中缓存；如果直接打印对象，说明是从内存缓存中取到了结果。
1、在同一个session 中共享（不同session 不能共享）
```
//同Session
SqlSession session1 = sqlSessionFactory.openSession();
BlogMapper mapper1 = session1.getMapper(BlogMapper.class);
System.out.println(mapper1.selectBlogById(1002));
System.out.println(mapper1.selectBlogById(1002));
```
  执行以上sql我们可以看到控制台打印如下信息（需配置mybatis.configuration.log-impl=org.apache.ibatis.logging.stdout.StdOutImpl），会发现我们两次的查询就发送了一次查询数据库的操作，这说明了缓存在发生作用：
*![img](images/1383365-20190628173854959-1659491558.png)*
  PS：一级缓存在BaseExecutor 的query()——queryFromDatabase()中存入。在queryFromDatabase()之前会get()。
```
public  List query(MappedStatement ms, Object parameter, RowBounds rowBounds, ResultHandler resultHandler, CacheKey key, BoundSql boundSql) throws SQLException {
        ErrorContext.instance().resource(ms.getResource()).activity("executing a query").object(ms.getId());
    。。。。。。try {
                ++this.queryStack;//从缓存中获取
                list = resultHandler == null ? (List)this.localCache.getObject(key) : null;
                if (list != null) {
                    this.handleLocallyCachedOutputParameters(ms, key, parameter, boundSql);
                } else {//缓存中获取不到，查询数据库
                    list = this.queryFromDatabase(ms, parameter, rowBounds, resultHandler, key, boundSql);
                }
    。。。。。。
    }
```
2.同一个会话中，update（包括delete）会导致一级缓存被清空
```
//同Session
SqlSession session1 = sqlSessionFactory.openSession();
BlogMapper mapper1 = session1.getMapper(BlogMapper.class);
System.out.println(mapper1.selectBlogById(1002));
Blog blog3 = new Blog();
blog3.setBid(1002);
blog3.setName("mybatis缓存机制修改");
mapper1.updateBlog(blog3);
session1.commit();// 注意要提交事务，否则不会清除缓存
System.out.println(mapper1.selectBlogById(1002));
```
  一级缓存是在BaseExecutor 中的update()方法中调用clearLocalCache()清空的（无条件），query 中会判断。
```
public int update(MappedStatement ms, Object parameter) throws SQLException {
        ErrorContext.instance().resource(ms.getResource()).activity("executing an update").object(ms.getId());
        if (this.closed) {
            throw new ExecutorException("Executor was closed.");
        } else {        //清除本地缓存
            this.clearLocalCache();
            return this.doUpdate(ms, parameter);
        }
}
```
3.其他会话更新了数据，导致读取到脏数据（一级缓存不能跨会话共享）
```
SqlSession session1 = sqlSessionFactory.openSession();
BlogMapper mapper1 = session1.getMapper(BlogMapper.class);
SqlSession session2 = sqlSessionFactory.openSession();
BlogMapper mapper2 = session2.getMapper(BlogMapper.class);
System.out.println(mapper2.selectBlogById(1002));
Blog blog3 = new Blog();
blog3.setBid(1002);
blog3.setName("mybatis缓存机制1");
mapper1.updateBlog(blog3);
session1.commit();
System.out.println(mapper2.selectBlogById(1002));
```
一级缓存的不足：
  使用一级缓存的时候，因为缓存不能跨会话共享，不同的会话之间对于相同的数据可能有不一样的缓存。在有多个会话或者分布式环境下，会存在脏数据的问题。如果要解决这个问题，就要用到二级缓存。MyBatis 一级缓存（MyBaits 称其为 Local Cache）无法关闭，但是有两种级别可选：
1. session 级别的缓存，在同一个 sqlSession 内，对同样的查询将不再查询数据库，直接从缓存中。
2. statement 级别的缓存，避坑： 为了避免这个问题，可以将一级缓存的级别设为 statement 级别的，这样每次查询结束都会清掉一级缓存。
## 二级缓存：
  二级缓存是用来解决一级缓存不能跨会话共享的问题的，范围是namespace 级别的，可以被多个SqlSession 共享（只要是同一个接口里面的相同方法，都可以共享），生命周期和应用同步。如果你的MyBatis使用了二级缓存，并且你的Mapper和select语句也配置使用了二级缓存，那么在执行select查询的时候，MyBatis会先从二级缓存中取输入，其次才是一级缓存，即MyBatis查询数据的顺序是：二级缓存  —> 一级缓存 —> 数据库。
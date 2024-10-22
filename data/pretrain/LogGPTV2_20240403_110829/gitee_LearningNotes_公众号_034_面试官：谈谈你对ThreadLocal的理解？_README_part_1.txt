> 大家好，我是陌溪，欢迎点击下方的公众号名片，关注陌溪，让我们一起成长~
**ThreadLocal** 作为 **Java** 面试的高频题，陌溪在之前面试的时候也遇到过，所以后面专门针对 **ThreadLocal** 写了一份笔记，让我们一起来看看~
## 什么是ThreadLocal？
从 **Java** 官方文档中的描述：**ThreadLocal** 类用来提供线程内部的局部变量。这种变量在多线程环境下访问（通过**get** 和 **set** 方法访问）时能保证各个线程的变量相对独立于其他线程内的变量。ThreadLocal实例通常来说都是**private static** 类型的，用于关联线程和线程上下文。
我们可以得知 **ThreadLocal** 的作用是：提供线程内的局部变量，不同的线程之间不会相互干扰，这种变量在线程的生命周期内起作用，减少同一个线程内多个函数或组件之间一些公共变量传递的复杂度。
- 线程并发：在多线程并发的场景下
- 传递数据：我们可以通过 **ThreadLocal** 在同一线程，不同组件之间传递公共变量（有点类似于 **Session**？）
- 线程隔离：每个线程的变量都是独立的，不会互相影响
## 基本使用
在介绍 **ThreadLocal** 使用之前，我们首先认识几个 **ThreadLocal** 的常见方法
| 方法声明                 | 描述                       |
| ------------------------ | -------------------------- |
| ThreadLocal()            | 创建ThreadLocal对象        |
| public void set(T value) | 设置当前线程绑定的局部变量 |
| public T get()           | 获取当前线程绑定的局部变量 |
| public void remove()     | 移除当前线程绑定的局部变量 |
## 使用案例
我们来看下面这个案例，感受一下 **ThreadLocal** 线程隔离的特点。
```java
/**
 * 需求：线程隔离
 * 在多线程并发的场景下，每个线程中的变量都是相互独立的
 * 线程A：设置变量1，获取变量2
 * 线程B：设置变量2，获取变量2
 * @author: 陌溪
 */
public class MyDemo01 {
    // 变量
    private String content;
    public String getContent() {
        return content;
    }
    public void setContent(String content) {
        this.content = content;
    }
    public static void main(String[] args) {
        MyDemo01 myDemo01 = new MyDemo01();
        for (int i = 0; i  {
                myDemo01.setContent(Thread.currentThread().getName() + "的数据");
                System.out.println("-----------------------------------------");
                System.out.println(Thread.currentThread().getName() + "\t  " + myDemo01.getContent());
            }, String.valueOf(i)).start();
        }
    }
}
```
运行后的效果
```bash
-----------------------------------------
-----------------------------------------
-----------------------------------------
3	  4的数据
-----------------------------------------
2	  4的数据
-----------------------------------------
1	  4的数据
4	  4的数据
0	  4的数据
```
从上面我们可以看到，出现了线程不隔离的问题，也就是线程1取出了线程4的内，那么如何解决呢？
这个时候就可以用到 **ThreadLocal** 了，我们通过 **set** 将变量绑定到当前线程中，然后 **get** 获取当前线程绑定的变量
```java
/**
 * 需求：线程隔离
 * 在多线程并发的场景下，每个线程中的变量都是相互独立的
 * 线程A：设置变量1，获取变量2
 * 线程B：设置变量2，获取变量2
 * @author: 陌溪
 */
public class MyDemo01 {
    // 变量
    private String content;
    public String getContent() {
        return content;
    }
    public void setContent(String content) {
        this.content = content;
    }
    public static void main(String[] args) {
        MyDemo01 myDemo01 = new MyDemo01();
        ThreadLocal threadLocal = new ThreadLocal<>();
        for (int i = 0; i  {
                threadLocal.set(Thread.currentThread().getName() + "的数据");
                System.out.println("-----------------------------------------");
                System.out.println(Thread.currentThread().getName() + "\t  " + threadLocal.get());
            }, String.valueOf(i)).start();
        }
    }
}
```
我们引入 **ThreadLocal** 后，查看运行结果如下：
```
-----------------------------------------
-----------------------------------------
4	  4的数据
-----------------------------------------
3	  3的数据
-----------------------------------------
2	  2的数据
-----------------------------------------
1	  1的数据
0	  0的数据
```
我们发现不会出现上面的情况了，也就是当前线程只能获取线程线程存储的对象
## ThreadLocal类和Synchronized关键字
### Synchronized同步方式
对于上述的例子，我们完全可以通过加锁的方式来实现这个功能，我们来看一下用 **Synchronized** 代码块实现的效果：
```java
    public static void main(String[] args) {
        MyDemo03 myDemo01 = new MyDemo03();
        for (int i = 0; i  {
                synchronized (MyDemo03.class) {
                    myDemo01.setContent(Thread.currentThread().getName() + "的数据");
                    System.out.println("-----------------------------------------");
                    System.out.println(Thread.currentThread().getName() + "\t  " + myDemo01.getContent());
                }
            }, String.valueOf(i)).start();
        }
    }
```
运行结果如下所示，我们发现我们可以看到同样实现了功能，但是并发性降低了
```
-----------------------------------------
0	  0的数据
-----------------------------------------
4	  4的数据
-----------------------------------------
3	  3的数据
-----------------------------------------
2	  2的数据
-----------------------------------------
1	  1的数据
```
### ThreadLocal与Synchronized的区别
虽然 **ThreadLocal** 模式与 **Synchronized** 关键字都用于处理多线程并发访问变量的问题，不过两者处理问题的角度和思路不同。
|        | Synchronized                                                 | ThreadLocal                                                  |
| ------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 原理   | 同步机制采用以时间换空间的方式，只提供了一份变量，让不同的线程排队访问 | ThreadLocal采用以空间换时间的概念，为每个线程都提供一份变量副本，从而实现同时访问而互不干扰 |
| 侧重点 | 多个线程之间访问资源的同步                                   | 多线程中让每个线程之间的数据相互隔离                         |
总结：在刚刚的案例中，虽然使用 **ThreadLocal** 和 **Synchronized** 都能解决问题，但是使用 **ThreadLocal** 更为合适，因为这样可以使程序拥有更高的并发性。
## 运用场景
通过以上的介绍，我们已经基本了解 **ThreadLocal** 的特点，但是它具体是运用在什么场景中的呢？接下来让我们看一个案例：事务操作
### 转账案例
这里们先构建一个简单的转账场景：有一个数据表 **account** ，里面有两个用户 **jack** 和 **Rose**，用户 **Jack** 给用户**Rose** 转账。案例的实现主要是用 **mysql** 数据库，**JDBC** 和 **C3P0** 框架，以下是详细代码
![image-20200710204941153](images/image-20200710204941153.png)
### 引入事务
案例中转账涉及两个 **DML** 操作：一个转出，一个转入。这些操作是需要具备原子性的，不可分割。不然有可能出现数据修改异常情况。
```java
public class AccountService {
    public boolean transfer(String outUser, String isUser, int money) {
        AccountDao ad = new AccountDao();
        try {
            // 转出
            ad.out(outUser, money);
            // 模拟转账过程中的异常
            int i = 1/0;
            // 转入
            ad.in(inUser, money);
        } catch(Exception e) {
            e.printStackTrace();
            return false;
        }
        return true;
    }
}
```
所以这里就需要操作事务，来保证转入和转出具备原子性，要么成功，要么失败。
**JDBC** 中关于事务操作的 **API**
| Connection接口的方法      | 作用                             |
| ------------------------- | -------------------------------- |
| void setAutoCommit(false) | 禁用事务自动提交（改为手动提交） |
| void commit()             | 提交事务                         |
| void rollbakc()           | 回滚事务                         |
开启事务的注意点
- 为了保证所有操作在一个事务中，案例中使用的连接必须是同一个；
- **service** 层开启事务的 **connection** 需要跟 **dao** 层访问数据库的 **connection** 保持一致
- 线程并发情况下，每个线程只能操作各自的 **connection**，也就是线程隔离
### 常规解决方法
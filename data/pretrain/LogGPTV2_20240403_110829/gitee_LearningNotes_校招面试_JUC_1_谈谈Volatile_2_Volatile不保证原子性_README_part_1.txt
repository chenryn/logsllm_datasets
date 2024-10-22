# Volatile不保证原子性
## 前言
通过前面对JMM的介绍，我们知道，各个线程对主内存中共享变量的操作都是各个线程各自拷贝到自己的工作内存进行操作后在写回到主内存中的。
这就可能存在一个线程AAA修改了共享变量X的值，但是还未写入主内存时，另外一个线程BBB又对主内存中同一共享变量X进行操作，但此时A线程工作内存中共享变量X对线程B来说是不可见，这种工作内存与主内存同步延迟现象就造成了可见性问题。
## 原子性
不可分割，完整性，也就是说某个线程正在做某个具体业务时，中间不可以被加塞或者被分割，需要具体完成，要么同时成功，要么同时失败。
数据库也经常提到事务具备原子性
## 代码测试
为了测试volatile是否保证原子性，我们创建了20个线程，然后每个线程分别循环1000次，来调用number++的方法
```
        MyData myData = new MyData();
        // 创建10个线程，线程里面进行1000次循环
        for (int i = 0; i  {
                // 里面
                for (int j = 0; j  2) {
    // yield表示不执行
    Thread.yield();
}
```
然后在线程执行完毕后，我们在查看number的值，假设volatile保证原子性的话，那么最后输出的值应该是
20 * 1000 = 20000,
完整代码如下所示：
```
/**
 * Volatile Java虚拟机提供的轻量级同步机制
 *
 * 可见性（及时通知）
 * 不保证原子性
 * 禁止指令重排
 *
 * @author: 陌溪
 * @create: 2020-03-09-15:58
 */
import java.util.concurrent.TimeUnit;
/**
 * 假设是主物理内存
 */
class MyData {
    /**
     * volatile 修饰的关键字，是为了增加 主线程和线程之间的可见性，只要有一个线程修改了内存中的值，其它线程也能马上感知
     */
    volatile int number = 0;
    public void addTo60() {
        this.number = 60;
    }
    /**
     * 注意，此时number 前面是加了volatile修饰
     */
    public void addPlusPlus() {
        number ++;
    }
}
/**
 * 验证volatile的可见性
 * 1、 假设int number = 0， number变量之前没有添加volatile关键字修饰
 * 2、添加了volatile，可以解决可见性问题
 *
 * 验证volatile不保证原子性
 * 1、原子性指的是什么意思？
 */
public class VolatileDemo {
    public static void main(String args []) {
        MyData myData = new MyData();
        // 创建10个线程，线程里面进行1000次循环
        for (int i = 0; i  {
                // 里面
                for (int j = 0; j  2) {
            // yield表示不执行
            Thread.yield();
        }
        // 查看最终的值
        // 假设volatile保证原子性，那么输出的值应该为：  20 * 1000 = 20000
        System.out.println(Thread.currentThread().getName() + "\t finally number value: " + myData.number);
    }
}
```
最终结果我们会发现，number输出的值并没有20000，而且是每次运行的结果都不一致的，这说明了volatile修饰的变量不保证原子性
第一次：
![image-20200309172900462](images/image-20200309172900462.png)
第二次：
![image-20200309172919295](images/image-20200309172919295.png)
第三次：
![image-20200309172929820](images/image-20200309172929820.png)
## 为什么出现数值丢失
![image-20200309174220675](images/image-20200309174220675.png)
各自线程在写入主内存的时候，出现了数据的丢失，而引起的数值缺失的问题
下面我们将一个简单的number++操作，转换为字节码文件一探究竟
```
public class T1 {
    volatile int n = 0;
    public void add() {
        n++;
    }
}
```
转换后的字节码文件
```
public class com.moxi.interview.study.thread.T1 {
  volatile int n;
  public com.moxi.interview.study.thread.T1();
    Code:
       0: aload_0
       1: invokespecial #1                  // Method java/lang/Object."":()V
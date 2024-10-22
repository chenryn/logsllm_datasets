# JVM参数调优
## 前言
你说你做过JVM调优和参数配置，请问如何盘点查看JVM系统默认值
使用jps和jinfo进行查看
```
-Xms：初始堆空间
-Xmx：堆最大值
-Xss：栈空间
```
-Xms 和 -Xmx最好调整一致，防止JVM频繁进行收集和回收
## JVM参数类型
- 标配参数（从JDK1.0 - Java12都在，很稳定）
  - -version
  - -help
  - java -showversion
- X参数（了解）
  - -Xint：解释执行
  - -Xcomp：第一次使用就编译成本地代码
  - -Xmixed：混合模式
- XX参数（重点）
  - Boolean类型
    - 公式：-XX:+ 或者-某个属性   + 表示开启，-表示关闭
    - Case：-XX:-PrintGCDetails：表示关闭了GC详情输出
  - key-value类型
    - 公式：-XX:属性key=属性value
    - 不满意初始值，可以通过下列命令调整
    - case：如何：-XX:MetaspaceSize=21807104：查看Java元空间的值
## 查看运行的Java程序，JVM参数是否开启，具体值为多少？
首先我们运行一个HelloGC的java程序
```
/**
 * @author: 陌溪
 * @create: 2020-03-19-12:14
 */
public class HelloGC {
    public static void main(String[] args) throws InterruptedException {
        System.out.println("hello GC");
        Thread.sleep(Integer.MAX_VALUE);
    }
}
```
然后使用下列命令查看它的默认参数
```
jps：查看java的后台进程
jinfo：查看正在运行的java程序
```
具体使用：
```
jps -l得到进程号
```
```
12608 com.moxi.interview.study.GC.HelloGC
15200 sun.tools.jps.Jps
15296 org.jetbrains.idea.maven.server.RemoteMavenServer36
4528
12216 org.jetbrains.jps.cmdline.Launcher
9772 org.jetbrains.kotlin.daemon.KotlinCompileDaemon
```
查看到HelloGC的进程号为：12608
我们使用jinfo -flag 然后查看是否开启PrintGCDetails这个参数
```
jinfo -flag PrintGCDetails 12608
```
得到的内容为
```
-XX:-PrintGCDetails
```
上面提到了，-号表示关闭，即没有开启PrintGCDetails这个参数
下面我们需要在启动HelloGC的时候，增加 PrintGCDetails这个参数，需要在运行程序的时候配置JVM参数
![image-20200319122922264](images/image-20200319122922264.png)
然后在VM Options中加入下面的代码，现在+号表示开启
```
-XX:+PrintGCDetails
```
然后在使用jinfo查看我们的配置
```
jps -l
jinfo -flag PrintGCDetails 13540
```
得到的结果为
```
-XX:+PrintGCDetails
```
我们看到原来的-号变成了+号，说明我们通过 VM Options配置的JVM参数已经生效了
使用下列命令，会把jvm的全部默认参数输出
```
jinfo -flags ***
```
## 题外话（坑题）
两个经典参数：-Xms  和 -Xmx，这两个参数 如何解释
这两个参数，还是属于XX参数，因为取了别名
- -Xms  等价于 -XX:InitialHeapSize  ：初始化堆内存（默认只会用最大物理内存的64分1）
- -Xmx 等价于 -XX:MaxHeapSize    ：最大堆内存（默认只会用最大物理内存的4分1）
## 查看JVM默认参数
- -XX:+PrintFlagsInitial
  - 主要是查看初始默认值
  - 公式
    - java -XX:+PrintFlagsInitial -version
    - java -XX:+PrintFlagsInitial（重要参数）
  ![image-20200320212256284](images/image-20200320212256284.png)
- -XX:+PrintFlagsFinal：表示修改以后，最终的值
​         会将JVM的各个结果都进行打印
​         如果有  := 表示修改过的， = 表示没有修改过的
## 工作中常用的JVM基本配置参数
![image-20200322163252777](images/image-20200322163252777.png)
### 查看堆内存
查看JVM的初始化堆内存 -Xms 和最大堆内存 Xmx
```
/**
 * @author: 陌溪
 * @create: 2020-03-19-12:14
 */
public class HelloGC {
    public static void main(String[] args) throws InterruptedException {
        // 返回Java虚拟机中内存的总量
        long totalMemory = Runtime.getRuntime().totalMemory();
        // 返回Java虚拟机中试图使用的最大内存量
        long maxMemory = Runtime.getRuntime().maxMemory();
        System.out.println("TOTAL_MEMORY(-Xms) = " + totalMemory + "(字节)、" + (totalMemory / (double)1024 / 1024) + "MB");
        System.out.println("MAX_MEMORY(-Xmx) = " + maxMemory + "(字节)、" + (maxMemory / (double)1024 / 1024) + "MB");
    }
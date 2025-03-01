# 类加载子系统
## 概述
![image-20200705080719531](images/image-20200705080719531.png)
完整图如下
![image-20200705080911284](images/image-20200705080911284.png)
如果自己想手写一个Java虚拟机的话，主要考虑哪些结构呢？
- 类加载器
- 执行引擎
## 类加载器子系统作用
类加载器子系统负责从文件系统或者网络中加载Class文件，class文件在文件开头有特定的文件标识。
ClassLoader只负责class文件的加载，至于它是否可以运行，则由Execution Engine决定。
加载的类信息存放于一块称为方法区的内存空间。除了类的信息外，方法区中还会存放运行时常量池信息，可能还包括字符串字面量和数字常量（这部分常量信息是Class文件中常量池部分的内存映射）
![image-20200705081813409](images/image-20200705081813409.png)
- class file存在于本地硬盘上，可以理解为设计师画在纸上的模板，而最终这个模板在执行的时候是要加载到JVM当中来根据这个文件实例化出n个一模一样的实例。
- class file加载到JVM中，被称为DNA元数据模板，放在方法区。
- 在.class文件->JVM->最终成为元数据模板，此过程就要一个运输工具（类装载器Class Loader），扮演一个快递员的角色。
![image-20200705081913538](images/image-20200705081913538.png)
## 类的加载过程
例如下面的一段简单的代码
```java
/**
 * 类加载子系统
 * @author: 陌溪
 * @create: 2020-07-05-8:24
 */
public class HelloLoader {
    public static void main(String[] args) {
        System.out.println("我已经被加载啦");
    }
}
```
它的加载过程是怎么样的呢?
![image-20200705082255746](images/image-20200705082255746.png)
完整的流程图如下所示
![image-20200705082601441](images/image-20200705082601441.png)
### 加载阶段
通过一个类的全限定名获取定义此类的二进制字节流
将这个字节流所代表的静态存储结构转化为方法区的运行时数据结构
在内存中生成一个代表这个类的java.lang.Class对象，作为方法区这个类的各种数据的访问入口
### 加载class文件的方式
- 从本地系统中直接加载
- 通过网络获取，典型场景：Web Applet
- 从zip压缩包中读取，成为日后jar、war格式的基础
- 运行时计算生成，使用最多的是：动态代理技术
- 由其他文件生成，典型场景：JSP应用从专有数据库中提取.class文件，比较少见
- 从加密文件中获取，典型的防Class文件被反编译的保护措施
### 链接阶段
#### 验证 Verify
目的在于确保Class文件的字节流中包含信息符合当前虚拟机要求，保证被加载类的正确性，不会危害虚拟机自身安全。
主要包括四种验证，文件格式验证，元数据验证，字节码验证，符号引用验证。
> 工具：Binary Viewer查看
![image-20200705084038680](images/image-20200705084038680.png)
如果出现不合法的字节码文件，那么将会验证不通过
同时我们可以通过安装IDEA的插件，来查看我们的Class文件
![image-20200705090237078](images/image-20200705090237078.png)
安装完成后，我们编译完一个class文件后，点击view即可显示我们安装的插件来查看字节码方法了
![image-20200705090328171](images/image-20200705090328171.png)
### 准备 Prepare
为类变量分配内存并且设置该类变量的默认初始值，即零值。
```java
/**
 * @author: 陌溪
 * @create: 2020-07-05-8:42
 */
public class HelloApp {
    private static int a = 1;  // 准备阶段为0，在下个阶段，也就是初始化的时候才是1
    public static void main(String[] args) {
        System.out.println(a);
    }
}
```
上面的变量a在准备阶段会赋初始值，但不是1，而是0。
这里不包含用final修饰的static，因为final在编译的时候就会分配了，准备阶段会显式初始化；
这里不会为实例变量分配初始化，类变量会分配在方法区中，而实例变量是会随着对象一起分配到Java堆中。
例如下面这段代码
### 解析 Resolve
将常量池内的符号引用转换为直接引用的过程。
事实上，解析操作往往会伴随着JVM在执行完初始化之后再执行。
符号引用就是一组符号来描述所引用的目标。符号引用的字面量形式明确定义在《java虚拟机规范》的class文件格式中。直接引用就是直接指向目标的指针、相对偏移量或一个间接定位到目标的句柄。
解析动作主要针对类或接口、字段、类方法、接口方法、方法类型等。对应常量池中的CONSTANT Class info、CONSTANT Fieldref info、CONSTANT Methodref info等
### 初始化阶段
初始化阶段就是执行类构造器法（）的过程。
此方法不需定义，是javac编译器自动收集类中的所有类变量的赋值动作和静态代码块中的语句合并而来。
- 也就是说，当我们代码中包含static变量的时候，就会有clinit方法
构造器方法中指令按语句在源文件中出现的顺序执行。
（）不同于类的构造器。（关联：构造器是虚拟机视角下的（））若该类具有父类，JVM会保证子类的（）执行前，父类的（）已经执行完毕。
- 任何一个类在声明后，都有生成一个构造器，默认是空参构造器
```java
/**
 * @author: 陌溪
 * @create: 2020-07-05-8:47
 */
public class ClassInitTest {
    private static int num = 1;
    static {
        num = 2;
        number = 20;
        System.out.println(num);
        System.out.println(number);  //报错，非法的前向引用
    }
    private static int number = 10;
    public static void main(String[] args) {
        System.out.println(ClassInitTest.num); // 2
        System.out.println(ClassInitTest.number); // 10
    }
}
```
关于涉及到父类时候的变量赋值过程
```java
/**
 * @author: 陌溪
 * @create: 2020-07-05-9:06
 */
public class ClinitTest1 {
    static class Father {
        public static int A = 1;
        static {
            A = 2;
        }
    }
    static class Son extends Father {
        public static int b = A;
    }
    public static void main(String[] args) {
        System.out.println(Son.b);
    }
}
```
我们输出结果为 2，也就是说首先加载ClinitTest1的时候，会找到main方法，然后执行Son的初始化，但是Son继承了Father，因此还需要执行Father的初始化，同时将A赋值为2。我们通过反编译得到Father的加载过程，首先我们看到原来的值被赋值成1，然后又被复制成2，最后返回
```bash
iconst_1
putstatic #2 
iconst_2
putstatic #2 
return
```
虚拟机必须保证一个类的（）方法在多线程下被同步加锁。
```java
/**
 * @author: 陌溪
 * @create: 2020-07-05-9:14
 */
public class DeadThreadTest {
    public static void main(String[] args) {
        new Thread(() -> {
            System.out.println(Thread.currentThread().getName() + "\t 线程t1开始");
            new DeadThread();
        }, "t1").start();
        new Thread(() -> {
            System.out.println(Thread.currentThread().getName() + "\t 线程t2开始");
            new DeadThread();
        }, "t2").start();
    }
}
class DeadThread {
    static {
        if (true) {
            System.out.println(Thread.currentThread().getName() + "\t 初始化当前类");
            while(true) {
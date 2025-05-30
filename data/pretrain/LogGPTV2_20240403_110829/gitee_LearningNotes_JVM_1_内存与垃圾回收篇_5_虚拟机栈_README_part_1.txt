# 虚拟机栈
## 虚拟机栈概述
由于跨平台性的设计，Java的指令都是根据栈来设计的。不同平台CPU架构不同，所以不能设计为基于寄存器的。
优点是跨平台，指令集小，编译器容易实现，缺点是性能下降，实现同样的功能需要更多的指令。
有不少Java开发人员一提到Java内存结构，就会非常粗粒度地将JVM中的内存区理解为仅有Java堆（heap）和Java战（stack）？为什么？
首先栈是运行时的单位，而堆是存储的单位
- 栈解决程序的运行问题，即程序如何执行，或者说如何处理数据。
- 堆解决的是数据存储的问题，即数据怎么放，放哪里
![image-20200705163928652](images/image-20200705163928652.png)
### Java虚拟机栈是什么
Java虚拟机栈（Java Virtual Machine Stack），早期也叫Java栈。每个线程在创建时都会创建一个虚拟机栈，其内部保存一个个的栈帧（Stack Frame），对应着一次次的Java方法调用。
>是线程私有的
![image-20200705164722033](images/image-20200705164722033.png)
### 生命周期
生命周期和线程一致，也就是线程结束了，该虚拟机栈也销毁了
### 作用
主管Java程序的运行，它保存方法的局部变量、部分结果，并参与方法的调用和返回。
> 局部变量，它是相比于成员变量来说的（或属性）
>
> 基本数据类型变量 VS  引用类型变量（类、数组、接口）
### 栈的特点
栈是一种快速有效的分配存储方式，访问速度仅次于罹序计数器。JVM直接对Java栈的操作只有两个：
- 每个方法执行，伴随着进栈（入栈、压栈）
- 执行结束后的出栈工作
对于栈来说不存在垃圾回收问题（栈存在溢出的情况）
![image-20200705165025382](images/image-20200705165025382.png)
### 开发中遇到哪些异常？
栈中可能出现的异常
Java 虚拟机规范允许Java栈的大小是动态的或者是固定不变的。
如果采用固定大小的Java虚拟机栈，那每一个线程的Java虚拟机栈容量可以在线程创建的时候独立选定。如果线程请求分配的栈容量超过Java虚拟机栈允许的最大容量，Java虚拟机将会抛出一个StackoverflowError 异常。
如果Java虚拟机栈可以动态扩展，并且在尝试扩展的时候无法申请到足够的内存，或者在创建新的线程时没有足够的内存去创建对应的虚拟机栈，那Java虚拟机将会抛出一个 outofMemoryError 异常。
```
/**
 * 演示栈中的异常：StackOverflowError
 * @author: 陌溪
 * @create: 2020-07-05-17:11
 */
public class StackErrorTest {
    private static int count = 1;
    public static void main(String[] args) {
        System.out.println(count++);
        main(args);
    }
}
```
当栈深度达到9803的时候，就出现栈内存空间不足
### 设置栈内存大小
我们可以使用参数 -Xss选项来设置线程的最大栈空间，栈的大小直接决定了函数调用的最大可达深度
```java
-Xss1m
-Xss1k
```
## 栈的存储单位
每个线程都有自己的栈，栈中的数据都是以栈帧（Stack Frame）的格式存在。
在这个线程上正在执行的每个方法都各自对应一个栈帧（Stack Frame）。
栈帧是一个内存区块，是一个数据集，维系着方法执行过程中的各种数据信息。
### 栈中存储什么？
每个线程都有自己的栈，栈中的数据都是以栈帧（Stack Frame）的格式存在。在这个线程上正在执行的每个方法都各自对应一个栈颜（Stack Frame）。栈帧是一个内存区块，是一个数据集，维系着方法执行过程中的各种数据信息。
> OOP的基本概念：类和对象
>
> 类中基本结构：field（属性、字段、域）、method
JVM直接对Java栈的操作只有两个，就是对栈帧的压栈和出栈，遵循“先进后出”/“后进先出”原则。
在一条活动线程中，一个时间点上，只会有一个活动的栈帧。即只有当前正在执行的方法的栈帧（栈顶栈帧）是有效的，这个栈帧被称为当前栈帧（Current Frame），与当前栈帧相对应的方法就是当前方法（Current Method），定义这个方法的类就是当前类（Current Class）。
执行引擎运行的所有字节码指令只针对当前栈帧进行操作。
如果在该方法中调用了其他方法，对应的新的栈帧会被创建出来，放在栈的顶端，成为新的当前帧。
![image-20200705203142545](images/image-20200705203142545.png)
下面写一个简单的代码
```java
/**
 * 栈帧
 *
 * @author: 陌溪
 * @create: 2020-07-05-20:33
 */
public class StackFrameTest {
    public static void main(String[] args) {
        method01();
    }
    private static int method01() {
        System.out.println("方法1的开始");
        int i = method02();
        System.out.println("方法1的结束");
        return i;
    }
    private static int method02() {
        System.out.println("方法2的开始");
        int i = method03();;
        System.out.println("方法2的结束");
        return i;
    }
    private static int method03() {
        System.out.println("方法3的开始");
        int i = 30;
        System.out.println("方法3的结束");
        return i;
    }
}
```
输出结果为
```bash
方法1的开始
方法2的开始
方法3的开始
方法3的结束
方法2的结束
方法1的结束
```
满足栈先进后出的概念，通过Idea的 DEBUG，能够看到栈信息
![image-20200705203916023](images/image-20200705203916023.png)
### 栈运行原理
不同线程中所包含的栈帧是不允许存在相互引用的，即不可能在一个栈帧之中引用另外一个线程的栈帧。
如果当前方法调用了其他方法，方法返回之际，当前栈帧会传回此方法的执行结果给前一个栈帧，接着，虚拟机会丢弃当前栈帧，使得前一个栈帧重新成为当前栈帧。
Java方法有两种返回函数的方式，一种是正常的函数返回，使用return指令；另外一种是抛出异常。不管使用哪种方式，都会导致栈帧被弹出。
### 栈帧的内部结构
每个栈帧中存储着：
- 局部变量表（Local Variables）
- 操作数栈（operand Stack）（或表达式栈）
- 动态链接（DynamicLinking）（或指向运行时常量池的方法引用）
- 方法返回地址（Return Address）（或方法正常退出或者异常退出的定义）
- 一些附加信息
![image-20200705204836977](images/image-20200705204836977.png)
并行每个线程下的栈都是私有的，因此每个线程都有自己各自的栈，并且每个栈里面都有很多栈帧，栈帧的大小主要由局部变量表 和 操作数栈决定的
![image-20200705205443993](images/image-20200705205443993.png)
## 局部变量表
局部变量表：Local Variables，被称之为局部变量数组或本地变量表
定义为一个数字数组，主要用于存储方法参数和定义在方法体内的局部变量这些数据类型包括各类基本数据类型、对象引用（reference），以及returnAddress类型。
由于局部变量表是建立在线程的栈上，是线程的私有数据，因此不存在数据安全问题
局部变量表所需的容量大小是在编译期确定下来的，并保存在方法的Code属性的maximum local variables数据项中。在方法运行期间是不会改变局部变量表的大小的。
方法嵌套调用的次数由栈的大小决定。一般来说，栈越大，方法嵌套调用次数越多。对一个函数而言，它的参数和局部变量越多，使得局部变量表膨胀，它的栈帧就越大，以满足方法调用所需传递的信息增大的需求。进而函数调用就会占用更多的栈空间，导致其嵌套调用次数就会减少。
局部变量表中的变量只在当前方法调用中有效。在方法执行时，虚拟机通过使用局部变量表完成参数值到参数变量列表的传递过程。当方法调用结束后，随着方法栈帧的销毁，局部变量表也会随之销毁。
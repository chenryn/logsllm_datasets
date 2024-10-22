annotation：注解@interface
primitive type：基本数据类型
void
```
/**
 * 获取Class的方式
 *
 * @author: 陌溪
 * @create: 2020-03-29-10:16
 */
public class GetClassDemo {
    public static void main(String[] args) {
        Class c1 = Object.class; // 类
        Class c2 = Comparable.class; // 接口
        Class c3 = String[].class; // 数组
        Class c4 = int[][].class; // 二维数组
        Class c5 = Override.class; // 注解
        Class c6 = ElementType.class; // 枚举
        Class c7 = Integer.class; // 基本数据类型
        Class c8 = void.class; // void，空数据类型
        Class c9 = Class.class; // Class
        System.out.println(c1);
        System.out.println(c2);
        System.out.println(c3);
        System.out.println(c4);
        System.out.println(c5);
        System.out.println(c6);
        System.out.println(c7);
        System.out.println(c8);
        System.out.println(c9);
    }
}
```
最后运行结果为：
```
class java.lang.Object
interface java.lang.Comparable
class [Ljava.lang.String;
class [[I
interface java.lang.Override
class java.lang.annotation.ElementType
class java.lang.Integer
void
class java.lang.Class
```
同时需要注意，只要类型和维度一样，那就是同一个Class对象
```
int [] a = new int[10];
int [] b = new int[10];
System.out.println(a.getClass().hashCode());
System.out.println(b.getClass().hashCode());
```
这两个的hashcode是一样的
### Java内存分析
java内存分为以下三部分
- 堆
  - 存放new的对象和数组
  - 可以被所有的线程共享，不会存放别的对象引用
- 栈
  - 存放基本变量（会包含这个基本类型的具体数值）
  - 引用对象的变量（会存放这个引用在对堆里面的具体地址）
- 方法区
  - 可以被所有线程共享
  - 包含了所有的class和static变量
## 类的加载与ClassLoader的理解
### 类加载过程
当程序主动使用某个类时，如果该类还未被加载到内存中，则系统会通过如下三个步骤对该类进行初始化：
![image-20200329105217945](images/image-20200329105217945.png)
- 加载：将class文件字节码内容加载到内存，并将这些静态数据转换成方法区的运行时数据结构，然后生成一个代表这个类的 `java.lang.Class` 对象。
- 链接：将Java类的二进制代码合并到JVM的运行状态之中的过程。
  - 验证：确保加载的类信息符合JVM规范，没有安全方面的问题
  - 准备：正式为类变量(static)分配内存并设置类变量默认初始值的阶段，这些内存都将在方法区中进行分配。
  - 解析：虚拟机常量池的符号引用(常量名)替换为直接引用(地址)的过程
- 初始化：
  - 执行类构造器方法的过程，类构造器 方法是由编译期自动收集类中所有类变量的赋值动作和静态代码块中的语句合并产生的。（类构造器是构造类信息的，不是构造该类对象的构造器）
  - 当初始化一个类的时候，如果发现其父类还没有初始化完成，则需要先触发其父类的初始化
  - 虚拟机会保证一个类的方法在多相差环境中被正确的加锁和同步
下面一段代码，分别说明了static代码块，以及子类和父类构造方法的执行流程
```
/**
 * 类加载流程
 *
 * @author: 陌溪
 * @create: 2020-03-29-11:02
 */
class SuperA {
    static {
        System.out.println("父类静态代码块初始化");
    }
    public SuperA() {
        System.out.println("父类构造函数初始化");
    }
}
class A extends SuperA{
    static {
        System.out.println("静态代码块初始化");
        m = 300;
    }
    static int m = 100;
    public A() {
        System.out.println("A类的无参构造方法");
    }
}
public class ClassLoaderDemo {
    public static void main(String[] args) {
        A a = new A();
        System.out.println(a.m);
    }
}
```
最后的结果为：
```
父类静态代码块初始化
静态代码块初始化
父类构造函数初始化
A类的无参构造方法
100
```
说明静态代码块都是执行的，并且父类优先
### 类加载步骤
- 加载到内存，会产生一个类对应Class对象
- 链接，链接结束 m = 0
- 初始化：
  - ```
    () {
    	syso("A类静态方法")
    	m = 300;
    	m = 100;
    }
    ```
![image-20200329113526771](images/image-20200329113526771.png)
### 什么时候发生类初始化
#### 类的主动引用（一定发生初始化）
- 当虚拟机启动，先初始化main方法所有在类
- new 一个类的对象
- 调用类的静态成员（除了 final常量）和静态方法
- 使用 java.lang.reflect包的方法对类进行反射调用
- 当初始化一个类，如果其父类没有被初始化，则会先初始化它的父类
#### 类的被动引用（不会发生初始化）
- 当访问一个静态域时，只有真正的申明这个域的类才会被初始化，如：当通过子类引用父类的静态变量，不会导致子类初始化
- 通过数组定义类引用，不会触发此类的初始化
- 引用常量不会触发此类的初始化（常量在链接阶段就存入调用类的常量池了）
### 类加载器的作用
- 类加载的作用：将class文件字节码内容加载到内存中，并将这些静态数据转换成方法区的运行时数据结构，然后在堆中生成了一个代表这个类的 `java.lang.Class`对象，作为方法区中类数据的访问入口。
- 类缓存：标准的JavaSE类加载器可以按要求查找类，但是一旦某个类被加载到类加载器中，它将维持加载（缓存）一段时间。不过JVM垃圾回收机制可以回收这些Class对象
![image-20200329114720558](images/image-20200329114720558.png)
类加载器作用是用来把类（Class）装载进内存的，JVM规范定义了如下类型的类的加载器
![image-20200329114953888](images/image-20200329114953888.png)
代码如下：
```
/**
 * 类加载器的种类
 *
 * @author: 陌溪
 * @create: 2020-03-29-11:51
 */
public class ClassLoaderTypeDemo {
    public static void main(String[] args) {
        //当前类是哪个加载器
        ClassLoader loader = ClassLoaderTypeDemo.class.getClassLoader();
        System.out.println(loader);
        // 获取系统类加载器
        ClassLoader classLoader = ClassLoader.getSystemClassLoader();
        System.out.println(classLoader);
        // 获取系统类加载器的父类加载器 -> 扩展类加载器
        ClassLoader parentClassLoader = classLoader.getParent();
        System.out.println(parentClassLoader);
        // 获取扩展类加载器的父类加载器 -> 根加载器（C、C++）
        ClassLoader superParentClassLoader = parentClassLoader.getParent();
        System.out.println(superParentClassLoader);
        // 测试JDK内置类是谁加载的
        ClassLoader loader2 = Object.class.getClassLoader();
        System.out.println(loader2);
    }
}
```
运行结果：我们发现，根加载器我们无法获取到
```
sun.misc.Launcher$AppClassLoader@18b4aac2
sun.misc.Launcher$AppClassLoader@18b4aac2
sun.misc.Launcher$ExtClassLoader@45ee12a7
null
null
```
获取类加载器能够加载的路径
```
// 如何获取类加载器可以加载的路径
System.out.println(System.getProperty("java.class.path"));
```
最后输出结果为：
```
        // 如何获取类加载器可以加载的路径
        System.out.println(System.getProperty("java.class.path"));
        /*
        E:\Software\JDK1.8\Java\jre\lib\charsets.jar;
        E:\Software\JDK1.8\Java\jre\lib\deploy.jar;
        E:\Software\JDK1.8\Java\jre\lib\ext\access-bridge-64.jar;
        E:\Software\JDK1.8\Java\jre\lib\ext\cldrdata.jar;
        E:\Software\JDK1.8\Java\jre\lib\ext\dnsns.jar;
        E:\Software\JDK1.8\Java\jre\lib\ext\jaccess.jar;
        E:\Software\JDK1.8\Java\jre\lib\ext\jfxrt.jar;
        E:\Software\JDK1.8\Java\jre\lib\ext\localedata.jar;
        E:\Software\JDK1.8\Java\jre\lib\ext\nashorn.jar;
        E:\Software\JDK1.8\Java\jre\lib\ext\sunec.jar;
        E:\Software\JDK1.8\Java\jre\lib\ext\sunjce_provider.jar;
        E:\Software\JDK1.8\Java\jre\lib\ext\sunmscapi.jar;
        E:\Software\JDK1.8\Java\jre\lib\ext\sunpkcs11.jar;
        E:\Software\JDK1.8\Java\jre\lib\ext\zipfs.jar;
        E:\Software\JDK1.8\Java\jre\lib\javaws.jar;
        E:\Software\JDK1.8\Java\jre\lib\jce.jar;
        E:\Software\JDK1.8\Java\jre\lib\jfr.jar;
        E:\Software\JDK1.8\Java\jre\lib\jfxswt.jar;
        E:\Software\JDK1.8\Java\jre\lib\jsse.jar;
        E:\Software\JDK1.8\Java\jre\lib\management-agent.jar;
        E:\Software\JDK1.8\Java\jre\lib\plugin.jar;
        E:\Software\JDK1.8\Java\jre\lib\resources.jar;
        E:\Software\JDK1.8\Java\jre\lib\rt.jar;
        C:\Users\Administrator\Desktop\LearningNotes\校招面试\JUC\Code\target\classes;
        C:\Users\Administrator\.m2\repository\org\projectlombok\lombok\1.18.10\lombok-1.18.10.jar;
        C:\Users\Administrator\.m2\repository\cglib\cglib\3.3.0\cglib-3.3.0.jar;
        C:\Users\Administrator\.m2\repository\org\ow2\asm\asm\7.1\asm-7.1.jar;
        E:\Software\IntelliJ IDEA\IntelliJ IDEA 2019.1.2\lib\idea_rt.jar
         */
```
我们能够发现，类在加载的时候，都是有自己的加载区域的，而不是任何地方的类都能够被加载
### 获取运行时候类的完整结构
通过反射能够获取运行时类的完整结构
- 实现的全部接口
- 所继承的父类
- 全部的构造器
- 全部的方法
- 全部的Field
- 注解
```
/**
 * 获取运行时类信息
 * @author: 陌溪
 * @create: 2020-03-29-12:13
 */
public class GetClassInfo {
    public static void main(String[] args) throws ClassNotFoundException, NoSuchFieldException, NoSuchMethodException {
        Class clazz = Class.forName("com.moxi.interview.study.annotation.User");
        // 获取类名字
        System.out.println(clazz.getName()); // 包名 + 类名
        System.out.println(clazz.getSimpleName()); // 类名
        // 获取类属性
        System.out.println("================");
        // 只能找到public属性
        Field [] fields = clazz.getFields();
        // 找到全部的属性
        Field [] fieldAll = clazz.getDeclaredFields();
        for (int i = 0; i < fieldAll.length; i++) {
            System.out.println(fieldAll[i]);
        }
        // 获取指定属性的值
        Field name = clazz.getDeclaredField("name");
        // 获取方法
        Method [] methods = clazz.getDeclaredMethods(); // 获取本类和父类的所有public方法
        Method [] methods2 = clazz.getMethods(); // 获取本类所有方法
        // 获得指定方法
        Method method = clazz.getDeclaredMethod("getName", null);
        // 获取方法的时候，可以把参数也丢进去，这样因为避免方法重载，而造成不知道加载那个方法
        Method method2 = clazz.getDeclaredMethod("setName", String.class);
    }
}
```
## 双亲委派机制
如果我们想定义一个：java.lang.string 包，我们会发现无法创建
因为类在加载的时候，会逐级往上
也就是说当前的系统加载器，不会马上的创建该类，而是将该类委派给 扩展类加载器，扩展类加载器在委派为根加载器，然后引导类加载器去看这个类在不在能访问的路径下，发现 sring包已经存在了，所以就无法进行，也就是我们无法使用自己自定义的string类，而是使用初始化的stirng类
当一个类收到了类加载请求，他首先不会尝试自己去加载这个类，而是把这个请求委派给父类去完成，每一个层次类加载器都是如此，因此所有的加载请求都应该传送到启动类加载其中，只有当父类加载器反馈自己无法完成这个请求的时候（在它的加载路径下没有找到所需加载的Class），子类加载器才会尝试自己去加载。
采用双亲委派的一个好处是比如加载位于rt.jar 包中的类java.lang.Object，不管是哪个加载器加载这个类，最终都是委托给顶层的启动类加载器进行加载，这样就保证了使用不同的类加载器最终得到的都是同样一个Object 对象
![image-20200329122029227](images/image-20200329122029227.png)
## 有了Class对象，我们能够做什么？
创建类的对象：通过调用Class对象的newInstance()方法
- 类必须有一个无参数的构造器
- 类的构造器的权限需要足够
如果没有无参构造器就不能创建对象？
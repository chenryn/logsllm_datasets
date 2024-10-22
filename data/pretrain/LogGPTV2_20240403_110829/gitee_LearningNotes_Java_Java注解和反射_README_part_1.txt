# Java注解和反射
## 什么是注解
- Annotation是JDK5.0开始引入的新技术
- Annotation的作用
  - 不是程序本身，可以对程序做出解释（这一点和注释没有什么区别）
  - 可以被其它程序，比如编译器读取
- Annotation的格式
  - 注解以 `@注释名` 在代码中存在的，还可以添加一些参数值
  - 例如：`@SuppressWarnings(value = "unchecked")`
- Annotation在那里使用？
  - 可以附加在package、class、method、field等上面，相当于给他们添加了额外的辅助信息
  - 通过反射机制变成实现对这些元数据的控制
## 内置注解
- @Override：定义在 `java.lang.Override`中，此注释只适用于修饰方法，表示一个方法声明打算重写超类中的另一个方法声明
- @Deprecated：定义在`java.lang.Deprecated`中，此注释可以用于修饰方法，属性，类，表示不鼓励程序员使用这样的元素，通常是因为它很危险，或者存在更好的选择
- @SuppressWarnings：定义在`java.lang.SuppressWarnings`中，用来抑制编译时的警告信息，与前面的两个注释不同，你需要额外添加一个参数才能正确使用，这些参数都是已经定义好了的，我们选择性的使用就好了。
  - @SuppressWarnings("all")
  - @SuppressWarnings("unchecked")
  - @SuppressWarnings(value={"unchecked", "deprecation"})
  - ...
## 元注解
元注解的作用就是负责注解其它注解，Java定义了4个标准的meta-annotation类型，他们被用来提供对其它annotation类型作说明。
这些类型和它们所支持的类在 `java.lang.annotation`包可以找到 `@Target ` 、`@Retention`、`@Documented`、`@Inherited`
- @Target：用于描述注解的使用范围，即：被描述的注解可以在什么地方使用
- @Retention：表示需要什么保存该注释信息，用于描述注解的生命周期
  - 级别范围：Source < Class < Runtime
- @Document：说明该注解被包含在java doc中
- @Inherited：说明子类可以集成父类中的注解
示例
```
/**
 * 元注解
 *
 * @author: 陌溪
 * @create: 2020-03-28-22:57
 */
@MyAnnotation
public class MateAnnotationDemo {
}
/**
 * 定义一个注解
 */
@Target(value={ElementType.METHOD, ElementType.TYPE})  // target表示我们注解应用的范围，在方法上，和类上有效
@Retention(RetentionPolicy.RUNTIME)   // Retention：表示我们的注解在什么时候还有效，运行时候有效
@Documented   // 表示说我们的注解是否生成在java doc中
@Inherited   // 表示子类可以继承父类的注解
@interface MyAnnotation {
}
```
## 自定义注解
使用 `@interface`自定义注解时，自动继承了 `java.lang.annotation.Annotation`接口
- @interface 用来声明一个注解，格式：public @interface 注解名 {定义内容
- 其中的每个方法实际上是申明了一个配置参数
- 方法的名称就是参数的类型
- 返回值类型就是参数的类型（返回值只能是基本数据类型，Class，String，enum）
- 通过default来申明参数的默认值
- 如果只有一个参数成员，一般参数名为 value
- 注解元素必须要有值，我们定义元素时，经常使用空字符串或者0作为默认值
```
/**
 * 自定义注解
 *
 * @author: 陌溪
 * @create: 2020-03-28-22:57
 */
public class MateAnnotationDemo {
    // 注解可以显示赋值，如果没有默认值，我们就必须给注解赋值
    @MyAnnotation(schools = {"大学"})
    public void test(){
    }
}
/**
 * 定义一个注解
 */
@Target(value={ElementType.METHOD, ElementType.TYPE})  // target表示我们注解应用的范围，在方法上，和类上有效
@Retention(RetentionPolicy.RUNTIME)   // Retention：表示我们的注解在什么时候还有效，运行时候有效
@Documented   // 表示说我们的注解是否生成在java doc中
@Inherited   // 表示子类可以继承父类的注解
@interface MyAnnotation {
    // 注解的参数：参数类型 + 参数名()
    String name() default "";
    int age() default 0;
    // 如果默认值为-1，代表不存在
    int id() default -1;
    String[] schools();
}
```
## 反射机制
### 动态语言与静态语言
#### 动态语言
动态语言是一类在运行时可以改变其结构的语言：例如新的函数，对象，甚至代码可以被引进，已有的函数可以被删除或是其它结构上的变化。通俗点说就是在运行时代码可以根据某些条件改变自身结构
主要的动态语言有：Object-c、C#、JavaScript、PHP、Python等
#### 静态语言
与动态语言相比，运行时结构不可变的语言就是静态语言。例如Java、C、C++
Java不是动态语言，但是Java可以称为“准动态语言”。即Java有一定的动态性，我们可以利用反射机制来获取类似于动态语言的 特性，Java的动态性让编程的时候更加灵活。
### Java反射机制概述
#### 什么是反射
Java Reflection：Java反射是Java被视为动态语言的关键，反射机制运行程序在执行期借助于Reflection API 去的任何类内部的信息，并能直接操作任意对象的内部属性及方法。
```
Class c = Class.forName("java.lang.String")
```
在加载完类后，在堆内存的方法区就产生了一个Class类型的对象（一个类只有一个Class对象），这个对象就包含了完整的类的结构信息，我们可以通过这个对象看到类的结构，这个对象就像一面镜子，透过这个镜子看到类的结构，所以我们形象的称之为：反射
![image-20200328232620190](images/image-20200328232620190.png)
tip：反射可以获取到private修饰的成员变量和方法
#### 反射的应用
- 在运行时判断任意一个对象所属类
- 在运行时构造任意一个类的对象
- 在运行时判断任意一个类所具有的成员变量和方法
- 在运行时获取泛型信息
- 在运行时调用任意一个对象的成员变量和方法
- 在运行时候处理注解
- 生成动态代理
- .....
#### Java反射的优缺点
- 优点：可以实现动态创建对象和编译，体现出很大的灵活性
- 缺点：对性能有影响。使用反射基本上是一种解释操作，我们可以告诉JVM，我们希望做什么并且它满足我们的要求，这类操作总是慢于直接执行相同的操作。也就是说new创建和对象，比反射性能更高
#### 反射相关的主要API
- java.lang.Class：代表一个类
- java.lang.reflect.Method：代表类的方法
- java.lang.reflect.Field：代表类的成员变量
- java.lang.reflect.Constructor：代表类的构造器
- ........
## 理解Class类并获取Class实例
### Class类
我们下面通过Class.forName来获取一个实例对象
```
/**
 * 反射Demo
 *
 * @author: 陌溪
 * @create: 2020-03-29-8:21
 */
public class ReflectionDemo {
    public static void main(String[] args) throws ClassNotFoundException {
        // 通过反射获取类的Class对象
        Class c1 = Class.forName("com.moxi.interview.study.annotation.User");
        Class c2 = Class.forName("com.moxi.interview.study.annotation.User");
        Class c3 = Class.forName("com.moxi.interview.study.annotation.User");
        System.out.println(c1.hashCode());
        System.out.println(c2.hashCode());
        System.out.println(c3.hashCode());
    }
}
/**
 * 实体类：pojo，entity
 */
class User {
    private String name;
    private int id;
    private int age;
    public User() {
    }
    public String getName() {
        return name;
    }
    public void setName(String name) {
        this.name = name;
    }
    public int getId() {
        return id;
    }
    public void setId(int id) {
        this.id = id;
    }
    public int getAge() {
        return age;
    }
    public void setAge(int age) {
        this.age = age;
    }
    @Override
    public String toString() {
        return "User{" +
                "name='" + name + '\'' +
                ", id=" + id +
                ", age=" + age +
                '}';
    }
}
```
上面我们通过反射获取了三个对象，我们输出对应对象的hashcode码，会发现
```
1173230247
1173230247
1173230247
```
它们的hashcode码是一样的，这就说明了：
- 一个类在内存中只有一个Class对象
- 一个类被加载后，类的整体结构都会被封装在Class对象中
在Object类中定义了以下的方法，此方法将被所有子类继承
```
public final Class getClass()
```
以上方法的返回值的类型是一个Class类，此类是Java反射的源头，实际上所谓反射从程序的运行结果来看也很好理解，即：可以通过对象反射求出类的名称。
![image-20200329093212035](images/image-20200329093212035.png)
也就是说，我们通过对象来获取到它的Class，相当于逆过程
通过对照镜子我们可以得到的信息：某个类的属性，方法和构造器，某个类到底实现了那些接口。对于每个类而言，JRE都为其保留一个不变的Class类型对象，一个CLass对象包含了特定某个结构的有关信息
- Class本身也是一个类
- Class对象只能由系统建立对象
- 一个加载的类在JVM中只会有一个Class实例
- 一个Class对象对应的是一个加载到JVM中的一个.class文件
- 每个类的实例都会记得自己是由哪个Class实例所生成
- 通过Class可以完整地得到一个类中所有被加载的结构
- Class类是Reflection的根源，针对任何你想动态加载、运行的类、唯有先获得相应的Class对象
### Class类常用的方法
- ClassforName(String name)：返回指定类name的Class对象
- newInstance()：调用缺省构造函数，返回Class对象的一个实例
- getName()：返回此Class对象所表示的实体（类，接口，数组或void）的名称
- getSuperClass()：返回当前Class对象的父类Class对象
- getinterfaces()：返回当前对象的接口
- getClassLoader()：返回该类的类加载器
- getConstructors()：返回一个包含某些Constructor对象的数组
- getMethod(String name, Class.. T)：返回一个Method对象，此对象的形参类型为paramsType
- getDeclaredFields()：返回Field对象的一个数组
### 获取对象实例的方法
- 若已知具体的类，通过类的class属性获取，该方法最为安全可靠，程序性能最高
  - Class clazz = Person.class;
- 已知某个类的实例，调用该实例的getClass()方法获取Class对象
  - Class clazz = person.getClass()
- 已经一个类的全类名，且该类在类路径下，可以通过Class类的静态方法forName()获取，HIA可能抛出ClassNotFoundException
  - Class clazz = Class.forName("demo01.Sutdent")
- 内置数据类型可以直接通过 类名.Type
- 还可以利用ClassLoader
```
/**
 * Class类创建的方式
 *
 * @author: 陌溪
 * @create: 2020-03-29-9:56
 */
class Person {
    public String name;
    public Person() {
    }
    public Person(String name) {
        this.name = name;
    }
    @Override
    public String toString() {
        return "Person{" +
                "name='" + name + '\'' +
                '}';
    }
}
class Student extends Person{
    public Student() {
        this.name = "学生";
    }
}
class Teacher extends Person {
    public Teacher() {
        this.name = "老师";
    }
}
public class ClassCreateDemo {
    public static void main(String[] args) throws ClassNotFoundException {
        Person person = new Student();
        System.out.println("这个人是：" + person.name);
        // 方式1：通过对象获得
        Class c1 = person.getClass();
        System.out.println("c1:" + c1.hashCode());
        //方式2：通过forName获得
        Class c2 = Class.forName("com.moxi.interview.study.annotation.Student");
        System.out.println("c2:" + c2.hashCode());
        // 方式3：通过类名获取（最为高效）
        Class c3 = Student.class;
        System.out.println("c3:" + c3.hashCode());
        // 方式4：基本内置类型的包装类，都有一个Type属性
        Class c4 = Integer.TYPE;
        System.out.println(c4.getName());
        // 方式5：获取父类类型
        Class c5 = c1.getSuperclass();
    }
}
```
### 哪些类型可以有Class对象
class：外部类，成员（成员内部类，静态内部类），局部内部类，匿名内部类
interface：接口
[]：数组
enum：枚举
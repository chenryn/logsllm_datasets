只要在操作的时候明确的调用类中的构造器，并将参数传递进去之后，才可以实例化操作。
步骤如下：
- 通过Class类的getDeclaredConstructor(Class ... parameterTypes)取得本类的指定形参类型的构造器
- 向构造器的形参中，传递一个对象数组进去，里面包含了构造器中所需的各个参数
- 通过Constructor实例化对象
#### 调用指定方法
通过反射，调用类中的方法，通过Method类完成。
- 通过Class类的getMethod方法取得一个Method对象，并设置此方法操作是所需要的参数类型
- 之后使用Object invoke进行调用，并向方法中传递要设置的obj对象的参数信息
#### Invoke方法
- Object invoke(Object obj， Object ... args)
- Object对应原方法的返回值，若原方法无返回值，此时返回null
- 若原方法为静态方法，此时形参Object 可以为null
- 若原方法形参列表为空，则Object[] args 为 null
- 若原方法声明private，则需要在调用此invoke() 方法前，显示调用方法对象的setAccessible(true)方法，将可访问private的方法
#### setAccessible方法
- Method和Field、Constructor对象都有setAccessible()方法
- setAccessible作用是启动和禁用访问安全检查的开关
- 参数值为true则指示反射对象再使用时应该取消Java语言访问检查
  - 提高反射效率，如果代码中必须使用反射，而这句代码需要频繁被嗲用，那么设置成true
  - 使得原本无法访问的私有成员也可以访问
- 参数值为false则指示反射的对象应该实行Java语言访问检查
![image-20200329144428207](images/image-20200329144428207.png)
完整代码：
```
/**
 * 通过反射获取对象
 *
 * @author: 陌溪
 * @create: 2020-03-29-12:43
 */
public class GetObjectByReflectionDemo {
    public static void main(String[] args) throws ClassNotFoundException, IllegalAccessException, InstantiationException, NoSuchMethodException, InvocationTargetException, NoSuchFieldException {
        // 获取Class
        Class clazz = Class.forName("com.moxi.interview.study.annotation.User");
        // 构造一个对象，newInstance调用的是无参构造器，如果没有无参构造器的话，本方法会出错
//        User user = (User)clazz.newInstance();
        // 获取class的有参构造器
        Constructor constructor = clazz.getDeclaredConstructor(String.class, int.class, int.class);
        User user2 = (User) constructor.newInstance("小溪", 10, 10);
        System.out.println(user2);
        // 通过反射调用普通构造方法
        User user3 = (User)clazz.newInstance();
        // 获取setName 方法
        Method setName = clazz.getDeclaredMethod("setName", String.class);
        // 执行setName方法，传入对象 和 参数
        setName.invoke(user3, "小白");
        System.out.println(user3);
        System.out.println("============");
        Field age = clazz.getDeclaredField("age");
        // 关闭权限检测,这样才能直接修改字段，因为 set方法不能直接操作私有变量
        age.setAccessible(true);
        age.set(user3, 10);
        System.out.println(user3);
    }
}
```
运行结果
```
User{name='小溪', id=10, age=10}
User{name='小白', id=0, age=0}
============
User{name='小白', id=0, age=10}
```
## 反射性能对比
下面我们编写代码来具体试一试，使用反射的时候和不适用反射，在执行方法时的性能对比
```
/**
 * 反射性能
 *
 * @author: 陌溪
 * @create: 2020-03-29-14:55
 */
public class ReflectionPerformance {
    /**
     * 普通方式调用
     */
    public static void test01() {
        User user = new User();
        long startTime = System.currentTimeMillis();
        for (int i = 0; i 
- GenericArrayType：表示一种元素类型是参数化类型或者类型变量的数组类型
- TypeVariable：是各种类型变量的公共父接口
- WildcardType：代表一种通配符类型的表达式
下面我们通过代码来获取方法上的泛型，包括参数泛型，以及返回值泛型
```
/**
 * 通过反射获取泛型
 *
 * @author: 陌溪
 * @create: 2020-03-29-15:15
 */
public class GenericityDemo {
    public void test01(Map map, List list) {
        System.out.println("test01");
    }
    public Map test02() {
        System.out.println("test02");
        return null;
    }
    public static void main(String[] args) throws Exception{
        Method method = GenericityDemo.class.getMethod("test01", Map.class, List.class);
        // 获取所有的泛型，也就是参数泛型
        Type[] genericParameterTypes = method.getGenericParameterTypes();
        // 遍历打印全部泛型
        for (Type genericParameterType : genericParameterTypes) {
            System.out.println(" # " +genericParameterType);
            if(genericParameterType instanceof ParameterizedType) {
                Type[] actualTypeArguments = ((ParameterizedType) genericParameterType).getActualTypeArguments();
                for (Type actualTypeArgument : actualTypeArguments) {
                    System.out.println(actualTypeArgument);
                }
            }
        }
        // 获取返回值泛型
        Method method2 = GenericityDemo.class.getMethod("test02", null);
        Type returnGenericParameterTypes = method2.getGenericReturnType();
        // 遍历打印全部泛型
        if(returnGenericParameterTypes instanceof ParameterizedType) {
            Type[] actualTypeArguments = ((ParameterizedType) returnGenericParameterTypes).getActualTypeArguments();
            for (Type actualTypeArgument : actualTypeArguments) {
                System.out.println(actualTypeArgument);
            }
        }
    }
}
```
得到的结果
```
 # java.util.Map
class java.lang.String
class com.moxi.interview.study.annotation.User
 # java.util.List
class com.moxi.interview.study.annotation.User
###################
class java.lang.String
class com.moxi.interview.study.annotation.User
```
## 反射操作注解
通过反射能够获取到 类、方法、字段。。。等上的注解
- getAnnotation
- getAnnotations
### ORM对象关系映射
ORM即为：Object relationship Mapping，对象关系映射
- 类和表结构对应
- 属性和字段对应
- 对象和记录对应
![image-20200329153301047](images/image-20200329153301047.png)
下面使用代码，模拟ORM框架的简单使用
```
/**
 * ORMDemo
 *
 * @author: 陌溪
 * @create: 2020-03-29-15:33
 */
@TableKuang("db_student")
class Student2 {
    @FieldKuang(columnName = "db_id", type="int", length = 10)
    private int id;
    @FieldKuang(columnName = "db_age", type="int", length = 10)
    private int age;
    @FieldKuang(columnName = "db_name", type="varchar", length = 10)
    private String name;
    public Student2() {
    }
    public Student2(int id, int age, String name) {
        this.id = id;
        this.age = age;
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
    public String getName() {
        return name;
    }
    public void setName(String name) {
        this.name = name;
    }
    @Override
    public String toString() {
        return "Student2{" +
                "id=" + id +
                ", age=" + age +
                ", name='" + name + '\'' +
                '}';
    }
}
/**
 * 自定义注解：类名的注解
 */
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@interface TableKuang {
    String value();
}
/**
 * 自定义注解：属性的注解
 */
@Target(ElementType.FIELD)
@Retention(RetentionPolicy.RUNTIME)
@interface FieldKuang {
    String columnName();
    String type();
    int length() default 0;
}
public class ORMDemo {
    public static void main(String[] args) throws Exception{
        // 获取Student 的 Class对象
        Class c1 = Class.forName("com.moxi.interview.study.annotation.Student2");
        // 通过反射，获取到全部注解
        Annotation [] annotations = c1.getAnnotations();
        for (Annotation annotation : annotations) {
            System.out.println(annotation);
        }
        // 获取注解的value值
        TableKuang tableKuang = (TableKuang)c1.getAnnotation(TableKuang.class);
        String value = tableKuang.value();
        System.out.println(value);
        // 获得类指定的注解
        Field f = c1.getDeclaredField("name");
        FieldKuang fieldKuang = f.getAnnotation(FieldKuang.class);
        System.out.println(fieldKuang.columnName());
        System.out.println(fieldKuang.type());
        System.out.println(fieldKuang.length());
    }
}
```
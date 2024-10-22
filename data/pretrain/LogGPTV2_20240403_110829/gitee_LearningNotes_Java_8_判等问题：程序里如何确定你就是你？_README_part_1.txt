今天，我来和你聊聊程序里的判等问题。
你可能会说，判等不就是一行代码的事情吗，有什么好说的。但，这一行代码如果处理不当，不仅会出现 Bug，还可能会引起内存泄露等问题。涉及判等的 Bug，即使是使用 == 这种错误的判等方式，也不是所有时候都会出问题。所以类似的判等问题不太容易发现，可能会被隐藏很久。
今天，我就 equals、compareTo 和 Java 的数值缓存、字符串驻留等问题展开讨论，希望你可以理解其原理，彻底消除业务代码中的相关 Bug。
## 注意 equals 和 == 的区别
在业务代码中，我们通常使用 equals 或 == 进行判等操作。equals 是方法而 == 是操作符，它们的使用是有区别的：
对基本类型，比如 int、long，进行判等，只能使用 ==，比较的是直接值。因为基本类型的值就是其数值。
对引用类型，比如 Integer、Long 和 String，进行判等，需要使用 equals 进行内容判等。因为引用类型的直接值是指针，使用 == 的话，比较的是指针，也就是两个对象在内存中的地址，即比较它们是不是同一个对象，而不是比较对象的内容。
这就引出了我们必须必须要知道的第一个结论：比较值的内容，除了基本类型只能使用 == 外，其他类型都需要使用 equals。
在开篇我提到了，即使使用 == 对 Integer 或 String 进行判等，有些时候也能得到正确结果。这又是为什么呢？
我们用下面的测试用例深入研究下：
使用 == 对两个值为 127 的直接赋值的 Integer 对象判等；
使用 == 对两个值为 128 的直接赋值的 Integer 对象判等；
使用 == 对一个值为 127 的直接赋值的 Integer 和另一个通过 new Integer 声明的值为 127 的对象判等；
使用 == 对两个通过 new Integer 声明的值为 127 的对象判等；
使用 == 对一个值为 128 的直接赋值的 Integer 对象和另一个值为 128 的 int 基本类型判等。
```java
Integer a = 127; //Integer.valueOf(127)
Integer b = 127; //Integer.valueOf(127)
log.info("\nInteger a = 127;\n" +
        "Integer b = 127;\n" +
        "a == b ? {}",a == b);    // true
Integer c = 128; //Integer.valueOf(128)
Integer d = 128; //Integer.valueOf(128)
log.info("\nInteger c = 128;\n" +
        "Integer d = 128;\n" +
        "c == d ? {}", c == d);   //false
Integer e = 127; //Integer.valueOf(127)
Integer f = new Integer(127); //new instance
log.info("\nInteger e = 127;\n" +
        "Integer f = new Integer(127);\n" +
        "e == f ? {}", e == f);   //false
Integer g = new Integer(127); //new instance
Integer h = new Integer(127); //new instance
log.info("\nInteger g = new Integer(127);\n" +
        "Integer h = new Integer(127);\n" +
        "g == h ? {}", g == h);  //false
Integer i = 128; //unbox
int j = 128;
log.info("\nInteger i = 128;\n" +
        "int j = 128;\n" +
        "i == j ? {}", i == j); //true
```
通过运行结果可以看到，虽然看起来永远是在对 127 和 127、128 和 128 判等，但 == 却没有永远给我们 true 的答复。原因是什么呢？
第一个案例中，编译器会把 Integer a = 127 转换为 Integer.valueOf(127)。查看源码可以发现，这个转换在内部其实做了缓存，使得两个 Integer 指向同一个对象，所以 == 返回 true。
```java
public static Integer valueOf(int i) {
    if (i >= IntegerCache.low && i = 127;
    }
}
```
第三和第四个案例中，New 出来的 Integer 始终是不走缓存的新对象。比较两个新对象，或者比较一个新对象和一个来自缓存的对象，结果肯定不是相同的对象，因此返回 false。
第五个案例中，我们把装箱的 Integer 和基本类型 int 比较，前者会先拆箱再比较，比较的肯定是数值而不是引用，因此返回 true。
看到这里，对于 Integer 什么时候是相同对象什么时候是不同对象，就很清楚了吧。但知道这些其实意义不大，因为在大多数时候，我们并不关心 Integer 对象是否是同一个，只需要记得比较 Integer 的值请使用 equals，而不是 ==（对于基本类型 int 的比较当然只能使用 ==）。
其实，我们应该都知道这个原则，只是有的时候特别容易忽略。以我之前遇到过的一个生产事故为例，有这么一个枚举定义了订单状态和对于状态的描述：
```java
enum StatusEnum {
    CREATED(1000, "已创建"),
    PAID(1001, "已支付"),
    DELIVERED(1002, "已送到"),
    FINISHED(1003, "已完成");
    private final Integer status; //注意这里的Integer
    private final String desc;
    StatusEnum(Integer status, String desc) {
        this.status = status;
        this.desc = desc;
    }
}
```
在业务代码中，开发同学使用了 == 对枚举和入参 OrderQuery 中的 status 属性进行判等：
```java
@Data
public class OrderQuery {
    private Integer status;
    private String name;
}
@PostMapping("enumcompare")
public void enumcompare(@RequestBody OrderQuery orderQuery){
    StatusEnum statusEnum = StatusEnum.DELIVERED;
    log.info("orderQuery:{} statusEnum:{} result:{}", orderQuery, statusEnum, statusEnum.status == orderQuery.getStatus());
}
```
因为枚举和入参 OrderQuery 中的 status 都是包装类型，所以通过 == 判等肯定是有问题的。只是这个问题比较隐晦，究其原因在于：
只看枚举的定义 CREATED(1000, “已创建”)，容易让人误解 status 值是基本类型；
因为有 Integer 缓存机制的存在，所以使用 == 判等并不是所有情况下都有问题。在这次事故中，订单状态的值从 100 开始增长，程序一开始不出问题，直到订单状态超过 127 后才出现 Bug。
在了解清楚为什么 Integer 使用 == 判等有时候也有效的原因之后，我们再来看看为什么 String 也有这个问题。我们使用几个用例来测试下：
对两个直接声明的值都为 1 的 String 使用 == 判等；
对两个 new 出来的值都为 2 的 String 使用 == 判等；
对两个 new 出来的值都为 3 的 String 先进行 intern 操作，再使用 == 判等；
对两个 new 出来的值都为 4 的 String 通过 equals 判等。
```java
String a = "1";
String b = "1";
log.info("\nString a = \"1\";\n" +
        "String b = \"1\";\n" +
        "a == b ? {}", a == b); //true
String c = new String("2");
String d = new String("2");
log.info("\nString c = new String(\"2\");\n" +
        "String d = new String(\"2\");" +
        "c == d ? {}", c == d); //false
String e = new String("3").intern();
String f = new String("3").intern();
log.info("\nString e = new String(\"3\").intern();\n" +
        "String f = new String(\"3\").intern();\n" +
        "e == f ? {}", e == f); //true
String g = new String("4");
String h = new String("4");
log.info("\nString g = new String(\"4\");\n" +
        "String h = new String(\"4\");\n" +
        "g == h ? {}", g.equals(h)); //true
```
在分析这个结果之前，我先和你说说 Java 的字符串常量池机制。首先要明确的是其设计初衷是节省内存。当代码中出现双引号形式创建字符串对象时，JVM 会先对这个字符串进行检查，如果字符串常量池中存在相同内容的字符串对象的引用，则将这个引用返回；否则，创建新的字符串对象，然后将这个引用放入字符串常量池，并返回该引用。这种机制，就是字符串驻留或池化。
再回到刚才的例子，再来分析一下运行结果：
第一个案例返回 true，因为 Java 的字符串驻留机制，直接使用双引号声明出来的两个 String 对象指向常量池中的相同字符串。
第二个案例，new 出来的两个 String 是不同对象，引用当然不同，所以得到 false 的结果。
第三个案例，使用 String 提供的 intern 方法也会走常量池机制，所以同样能得到 true。
第四个案例，通过 equals 对值内容判等，是正确的处理方式，当然会得到 true。
虽然使用 new 声明的字符串调用 intern 方法，也可以让字符串进行驻留，但在业务代码中滥用 intern，可能会产生性能问题。
写代码测试一下，通过循环把 1 到 1000 万之间的数字以字符串形式 intern 后，存入一个 List：
```java
List list = new ArrayList<>();
@GetMapping("internperformance")
public int internperformance(@RequestParam(value = "size", defaultValue = "10000000")int size) {
    //-XX:+PrintStringTableStatistics
    //-XX:StringTableSize=10000000
    long begin = System.currentTimeMillis();
    list = IntStream.rangeClosed(1, size)
            .mapToObj(i-> String.valueOf(i).intern())
            .collect(Collectors.toList());
    log.info("size:{} took:{}", size, System.currentTimeMillis() - begin);
    return list.size();
}
```
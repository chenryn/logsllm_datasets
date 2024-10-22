在启动程序时设置 JVM 参数 -XX:+PrintStringTableStatistic，程序退出时可以打印出字符串常量表的统计信息。调用接口后关闭程序，输出如下：
```java
[11:01:57.770] [http-nio-45678-exec-2] [INFO ] [.t.c.e.d.IntAndStringEqualController:54  ] - size:10000000 took:44907
StringTable statistics:
Number of buckets       :     60013 =    480104 bytes, avg   8.000
Number of entries       :  10030230 = 240725520 bytes, avg  24.000
Number of literals      :  10030230 = 563005568 bytes, avg  56.131
Total footprint         :           = 804211192 bytes
Average bucket size     :   167.134
Variance of bucket size :    55.808
Std. dev. of bucket size:     7.471
Maximum bucket size     :       198
```
可以看到，1000 万次 intern 操作耗时居然超过了 44 秒。
其实，原因在于字符串常量池是一个固定容量的 Map。如果容量太小（Number of buckets=60013）、字符串太多（1000 万个字符串），那么每一个桶中的字符串数量会非常多，所以搜索起来就很慢。输出结果中的 Average bucket size=167，代表了 Map 中桶的平均长度是 167。
解决方式是，设置 JVM 参数 -XX:StringTableSize，指定更多的桶。设置 -XX:StringTableSize=10000000 后，重启应用：
```java
[11:09:04.475] [http-nio-45678-exec-1] [INFO ] [.t.c.e.d.IntAndStringEqualController:54  ] - size:10000000 took:5557
StringTable statistics:
Number of buckets       :  10000000 =  80000000 bytes, avg   8.000
Number of entries       :  10030156 = 240723744 bytes, avg  24.000
Number of literals      :  10030156 = 562999472 bytes, avg  56.131
Total footprint         :           = 883723216 bytes
Average bucket size     :     1.003
Variance of bucket size :     1.587
Std. dev. of bucket size:     1.260
Maximum bucket size     :        10
```
可以看到，1000 万次调用耗时只有 5.5 秒，Average bucket size 降到了 1，效果明显。
好了，是时候给出第二原则了：没事别轻易用 intern，如果要用一定要注意控制驻留的字符串的数量，并留意常量表的各项指标。
## 实现一个 equals 没有这么简单
如果看过 Object 类源码，你可能就知道，equals 的实现其实是比较对象引用：
```java
public boolean equals(Object obj) {
    return (this == obj);
}
```
之所以 Integer 或 String 能通过 equals 实现内容判等，是因为它们都重写了这个方法。比如，String 的 equals 的实现：
```java
public boolean equals(Object anObject) {
    if (this == anObject) {
        return true;
    }
    if (anObject instanceof String) {
        String anotherString = (String)anObject;
        int n = value.length;
        if (n == anotherString.value.length) {
            char v1[] = value;
            char v2[] = anotherString.value;
            int i = 0;
            while (n-- != 0) {
                if (v1[i] != v2[i])
                    return false;
                i++;
            }
            return true;
        }
    }
    return false;
}
```
对于自定义类型，如果不重写 equals 的话，默认就是使用 Object 基类的按引用的比较方式。我们写一个自定义类测试一下。
假设有这样一个描述点的类 Point，有 x、y 和描述三个属性：
```java
class Point {
    private int x;
    private int y;
    private final String desc;
    public Point(int x, int y, String desc) {
        this.x = x;
        this.y = y;
        this.desc = desc;
    }
}
```
定义三个点 p1、p2 和 p3，其中 p1 和 p2 的描述属性不同，p1 和 p3 的三个属性完全相同，并写一段代码测试一下默认行为：
```java
Point p1 = new Point(1, 2, "a");
Point p2 = new Point(1, 2, "b");
Point p3 = new Point(1, 2, "a");
log.info("p1.equals(p2) ? {}", p1.equals(p2));
log.info("p1.equals(p3) ? {}", p1.equals(p3));
```
通过 equals 方法比较 p1 和 p2、p1 和 p3 均得到 false，原因正如刚才所说，我们并没有为 Point 类实现自定义的 equals 方法，Object 超类中的 equals 默认使用 == 判等，比较的是对象的引用。
我们期望的逻辑是，只要 x 和 y 这 2 个属性一致就代表是同一个点，所以写出了如下的改进代码，重写 equals 方法，把参数中的 Object 转换为 Point 比较其 x 和 y 属性：
```java
class PointWrong {
    private int x;
    private int y;
    private final String desc;
    public PointWrong(int x, int y, String desc) {
        this.x = x;
        this.y = y;
        this.desc = desc;
    }
    @Override
    public boolean equals(Object o) {
        PointWrong that = (PointWrong) o;
        return x == that.x && y == that.y;
    }
}
```
为测试改进后的 Point 是否可以满足需求，我们定义了三个用例：
比较一个 Point 对象和 null；
比较一个 Object 对象和一个 Point 对象；
比较两个 x 和 y 属性值相同的 Point 对象。
```java
PointWrong p1 = new PointWrong(1, 2, "a");
try {
    log.info("p1.equals(null) ? {}", p1.equals(null));
} catch (Exception ex) {
    log.error(ex.getMessage());
}
Object o = new Object();
try {
    log.info("p1.equals(expression) ? {}", p1.equals(o));
} catch (Exception ex) {
    log.error(ex.getMessage());
}
PointWrong p2 = new PointWrong(1, 2, "b");
log.info("p1.equals(p2) ? {}", p1.equals(p2));
```
通过日志中的结果可以看到，第一次比较出现了空指针异常，第二次比较出现了类型转换异常，第三次比较符合预期输出了 true。
```log
[17:54:39.120] [http-nio-45678-exec-1] [ERROR] [t.c.e.demo1.EqualityMethodController:32  ] - java.lang.NullPointerException
[17:54:39.120] [http-nio-45678-exec-1] [ERROR] [t.c.e.demo1.EqualityMethodController:39  ] - java.lang.ClassCastException: java.lang.Object cannot be cast to org.geekbang.time.commonmistakes.equals.demo1.EqualityMethodController$PointWrong
[17:54:39.120] [http-nio-45678-exec-1] [INFO ] [t.c.e.demo1.EqualityMethodController:43  ] - p1.equals(p2) ? true
```
通过这些失效的用例，我们大概可以总结出实现一个更好的 equals 应该注意的点：
考虑到性能，可以先进行指针判等，如果对象是同一个那么直接返回 true；
需要对另一方进行判空，空对象和自身进行比较，结果一定是 fasle；
需要判断两个对象的类型，如果类型都不同，那么直接返回 false；
确保类型相同的情况下再进行类型强制转换，然后逐一判断所有字段。
修复和改进后的 equals 方法如下：
```java
@Override
public boolean equals(Object o) {
    if (this == o) return true;
    if (o == null || getClass() != o.getClass()) return false;
    PointRight that = (PointRight) o;
    return x == that.x && y == that.y;
}
```
改进后的 equals 看起来完美了，但还没完。我们继续往下看。
## hashCode 和 equals 要配对实现
我们来试试下面这个用例，定义两个 x 和 y 属性值完全一致的 Point 对象 p1 和 p2，把 p1 加入 HashSet，然后判断这个 Set 中是否存在 p2：
```java
PointWrong p1 = new PointWrong(1, 2, "a");
PointWrong p2 = new PointWrong(1, 2, "b");
HashSet points = new HashSet<>();
points.add(p1);
log.info("points.contains(p2) ? {}", points.contains(p2));
```
按照改进后的 equals 方法，这 2 个对象可以认为是同一个，Set 中已经存在了 p1 就应该包含 p2，但结果却是 false。
出现这个 Bug 的原因是，散列表需要使用 hashCode 来定位元素放到哪个桶。如果自定义对象没有实现自定义的 hashCode 方法，就会使用 Object 超类的默认实现，得到的两个 hashCode 是不同的，导致无法满足需求。
要自定义 hashCode，我们可以直接使用 Objects.hash 方法来实现，改进后的 Point 类如下：
```java
class PointRight {
    private final int x;
    private final int y;
    private final String desc;
    ...
    @Override
    public boolean equals(Object o) {
        ...
    }
    @Override
    public int hashCode() {
        return Objects.hash(x, y);
    }
}
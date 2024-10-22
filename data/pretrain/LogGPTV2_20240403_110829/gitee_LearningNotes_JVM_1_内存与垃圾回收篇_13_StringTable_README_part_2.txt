改进的空间
- 我们使用的是StringBuilder的空参构造器，默认的字符串容量是16，然后将原来的字符串拷贝到新的字符串中， 我们也可以默认初始化更大的长度，减少扩容的次数
- 因此在实际开发中，我们能够确定，前前后后需要添加的字符串不高于某个限定值，那么建议使用构造器创建一个阈值的长度
## intern()的使用
intern是一个native方法，调用的是底层C的方法
字符串池最初是空的，由String类私有地维护。在调用intern方法时，如果池中已经包含了由equals(object)方法确定的与该字符串对象相等的字符串，则返回池中的字符串。否则，该字符串对象将被添加到池中，并返回对该字符串对象的引用。
如果不是用双引号声明的string对象，可以使用string提供的intern方法：intern方法会从字符串常量池中查询当前字符串是否存在，若不存在就会将当前字符串放入常量池中。
比如：
```
String myInfo = new string("I love atguigu").intern();
```
也就是说，如果在任意字符串上调用string.intern方法，那么其返回结果所指向的那个类实例，必须和直接以常量形式出现的字符串实例完全相同。因此，下列表达式的值必定是true
```java
（"a"+"b"+"c"）.intern（）=="abc"
```
通俗点讲，Interned string就是确保字符串在内存里只有一份拷贝，这样可以节约内存空间，加快字符串操作任务的执行速度。注意，这个值会被存放在字符串内部池（String Intern Pool）
### intern的空间效率测试
我们通过测试一下，使用了intern和不使用的时候，其实相差还挺多的
```
/**
 * 使用Intern() 测试执行效率
 * @author: 陌溪
 * @create: 2020-07-11-15:19
 */
public class StringIntern2 {
    static final int MAX_COUNT = 1000 * 10000;
    static final String[] arr = new String[MAX_COUNT];
    public static void main(String[] args) {
        Integer [] data = new Integer[]{1,2,3,4,5,6,7,8,9,10};
        long start = System.currentTimeMillis();
        for (int i = 0; i 
 3 dup
 4 ldc #3 
 6 invokespecial #4 >
 9 astore_1
10 return
```
这里面就是两个对象
- 一个对象是：new关键字在堆空间中创建
- 另一个对象：字符串常量池中的对象
### new String("a") + new String("b") 会创建几个对象
```java
/**
 * new String("ab") 会创建几个对象？ 看字节码就知道是2个对象
 *
 * @author: 陌溪
 * @create: 2020-07-11-11:17
 */
public class StringNewTest {
    public static void main(String[] args) {
        String str = new String("a") + new String("b");
    }
}
```
字节码文件为
```
 0 new #2 
 3 dup
 4 invokespecial #3 >
 7 new #4 
10 dup
11 ldc #5 
13 invokespecial #6 >
16 invokevirtual #7 
19 new #4 
22 dup
23 ldc #8 
25 invokespecial #6 >
28 invokevirtual #7 
31 invokevirtual #9 
34 astore_1
35 return
```
我们创建了6个对象
- 对象1：new StringBuilder()
- 对象2：new String("a")
- 对象3：常量池的 a
- 对象4：new String("b")
- 对象5：常量池的 b
- 对象6：toString中会创建一个 new String("ab")
  - 调用toString方法，不会在常量池中生成ab
### intern的使用：JDK6和JDK7
#### JDK6中
```java
String s = new String("1");  // 在常量池中已经有了
s.intern(); // 将该对象放入到常量池。但是调用此方法没有太多的区别，因为已经存在了1
String s2 = "1";
System.out.println(s == s2); // false
String s3 = new String("1") + new String("1");
s3.intern();
String s4 = "11";
System.out.println(s3 == s4); // false
```
输出结果
```
false
false
```
为什么对象会不一样呢？
- 一个是new创建的对象，一个是常量池中的对象，显然不是同一个
如果是下面这样的，那么就是true
```
String s = new String("1");
s = s.intern();
String s2 = "1";
System.out.println(s == s2); // true
```
而对于下面的来说，因为 s3变量记录的地址是  new String("11")，然后这段代码执行完以后，常量池中不存在 "11"，这是JDK6的关系，然后执行 s3.intern()后，就会在常量池中生成 "11"，最后 s4用的就是s3的地址
> 为什么最后输出的 s3 == s4  会为false呢？
>
> 这是因为在JDK6中创建了一个新的对象 "11"，也就是有了新的地址， s2 = 新地址
>
> 而在JDK7中，在JDK7中，并没有创新一个新对象，而是指向常量池中的新对象
#### JDK7中
```
String s = new String("1");
s.intern();
String s2 = "1";
System.out.println(s == s2); // false
String s3 = new String("1") + new String("1");
s3.intern();
String s4 = "11";
System.out.println(s3 == s4); // true
```
![image-20200711145925091](images/image-20200711145925091.png)
### 扩展
```java
String s3 = new String("1") + new String("1");
String s4 = "11";  // 在常量池中生成的字符串
s3.intern();  // 然后s3就会从常量池中找，发现有了，就什么事情都不做
System.out.println(s3 == s4);
```
我们将 s4的位置向上移动一行，发现变化就会很大，最后得到的是 false
### 总结
总结string的intern（）的使用：
JDK1.6中，将这个字符串对象尝试放入串池。
- 如果串池中有，则并不会放入。返回已有的串池中的对象的地址
- 如果没有，会把此**对象复制一份**，放入串池，并返回串池中的对象地址
JDK1.7起，将这个字符串对象尝试放入串池。
- 如果串池中有，则并不会放入。返回已有的串池中的对象的地址
- 如果没有，则会把**对象的引用地址**复制一份，放入串池，并返回串池中的引用地址
练习：
![image-20200711150859709](images/image-20200711150859709.png)
- 在JDK6中，在字符串常量池中创建一个字符串 “ab”
- 在JDK8中，在字符串常量池中没有创建 “ab”，而是将堆中的地址复制到 串池中。
所以上述结果，在JDK6中是：
```
true
false
```
在JDK8中是
```
false
true
```
![image-20200711151326909](images/image-20200711151326909.png)
针对下面这题，在JDK6和8中表现的是一样的
![image-20200711151433277](images/image-20200711151433277.png)
## StringTable的垃圾回收
```java
/**
 * String的垃圾回收
 * -Xms15m -Xmx15m -XX:+PrintStringTableStatistics -XX:+PrintGCDetails
 * @author: 陌溪
 * @create: 2020-07-11-16:55
 */
public class StringGCTest {
    public static void main(String[] args) {
        for (int i = 0; i UsestringDeduplication（bool）：开启string去重，默认是不开启的，需要手动开启。
>Printstringbeduplicationstatistics（bool）：打印详细的去重统计信息
>stringpeduplicationAgeThreshold（uintx）：达到这个年龄的string对象被认为是去重的候选对象
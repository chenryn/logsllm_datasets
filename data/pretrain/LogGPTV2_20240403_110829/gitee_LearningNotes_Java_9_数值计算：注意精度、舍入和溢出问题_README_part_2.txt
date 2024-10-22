format.setRoundingMode(RoundingMode.DOWN);
System.out.println(format.format(num1));
format.setRoundingMode(RoundingMode.DOWN);
System.out.println(format.format(num2));
```
当我们把这 2 个浮点数向下舍入取 2 位小数时，输出分别是 3.35 和 3.34，还是我们之前说的浮点数无法精确存储的问题。
因此，即使通过 DecimalFormat 来精确控制舍入方式，double 和 float 的问题也可能产生意想不到的结果，所以浮点数避坑第二原则：**浮点数的字符串格式化也要通过 BigDecimal 进行**。
比如下面这段代码，使用 **BigDecimal** 来格式化数字 3.35，分别使用向下舍入和四舍五入方式取 1 位小数进行格式化：
```java
BigDecimal num1 = new BigDecimal("3.35");
BigDecimal num2 = num1.setScale(1, BigDecimal.ROUND_DOWN);
System.out.println(num2);
BigDecimal num3 = num1.setScale(1, BigDecimal.ROUND_HALF_UP);
System.out.println(num3);
```
这次得到的结果是 **3.3** 和 **3.4**，符合预期。
## 用 equals 做判等，就一定是对的吗？
现在我们知道了，应该使用 **BigDecimal** 来进行浮点数的表示、计算、格式化。在上一讲介绍判等问题时，我提到一个原则：包装类的比较要通过 **equals** 进行，而不能使用 **==**。那么，使用 **equals** 方法对两个 **BigDecimal** 判等，一定能得到我们想要的结果吗？
我们来看下面的例子。使用 **equals** 方法比较 1.0 和 1 这两个 **BigDecimal**：
```java
System.out.println(new BigDecimal("1.0").equals(new BigDecimal("1")))
```
你可能已经猜到我要说什么了，结果当然是 **false**。
**BigDecimal** 的 **equals** 方法的注释中说明了原因，**equals** 比较的是 **BigDecimal** 的 value 和 **scale**，1.0 的 scale 是 **1**，1 的 scale 是 **0**，所以结果一定是  ：
```java
/**
 * Compares this {@code BigDecimal} with the specified
 * {@code Object} for equality.  Unlike {@link
 * #compareTo(BigDecimal) compareTo}, this method considers two
 * {@code BigDecimal} objects equal only if they are equal in
 * value and scale (thus 2.0 is not equal to 2.00 when compared by
 * this method).
 *
 * @param  x {@code Object} to which this {@code BigDecimal} is
 *         to be compared.
 * @return {@code true} if and only if the specified {@code Object} is a
 *         {@code BigDecimal} whose value and scale are equal to this
 *         {@code BigDecimal}'s.
 * @see    #compareTo(java.math.BigDecimal)
 * @see    #hashCode
 */
@Override
public boolean equals(Object x)
```
如果我们希望只比较 **BigDecimal** 的 **value**，可以使用 **compareTo** 方法，修改后代码如下：
```java
System.out.println(new BigDecimal("1.0").compareTo(new BigDecimal("1"))==0);
```
学过上一讲，你可能会意识到 **BigDecimal** 的 **equals** 和 **hashCode** 方法会同时考虑 **value** 和 **scale**，如果结合 **HashSet** 或 **HashMap** 使用的话就可能会出现麻烦。比如，我们把值为 **1.0** 的 **BigDecimal** 加入 **HashSet**，然后判断其是否存在值为 **1** 的 **BigDecimal**，得到的结果是 **false**：
```java
Set hashSet1 = new HashSet<>();
hashSet1.add(new BigDecimal("1.0"));
System.out.println(hashSet1.contains(new BigDecimal("1")));//返回false
```
解决这个问题的办法有两个：
第一个方法是，使用 **TreeSet** 替换 **HashSet**。**TreeSet** 不使用 **hashCode** 方法，也不使用 **equals** 比较元素，而是使用 **compareTo** 方法，所以不会有问题。
```java
Set treeSet = new TreeSet<>();
treeSet.add(new BigDecimal("1.0"));
System.out.println(treeSet.contains(new BigDecimal("1")));//返回true
```
第二个方法是，把 **BigDecimal** 存入 **HashSet** 或 **HashMap** 前，先使用 **stripTrailingZeros** 方法去掉尾部的零，比较的时候也去掉尾部的 **0**，确保 **value** 相同的 **BigDecimal**，**scale** 也是一致的：
```java
Set hashSet2 = new HashSet<>();
hashSet2.add(new BigDecimal("1.0").stripTrailingZeros());
System.out.println(hashSet2.contains(new BigDecimal("1.000").stripTrailingZeros()));//返回true
```
## 小心数值溢出问题
数值计算还有一个要小心的点是溢出，不管是 **int** 还是 **long**，所有的基本数值类型都有超出表达范围的可能性。
比如，对 **Long** 的最大值进行 +1 操作：
```java
long l = Long.MAX_VALUE;
System.out.println(l + 1);
System.out.println(l + 1 == Long.MIN_VALUE);
```
输出结果是一个负数，因为 **Long** 的最大值 **+1** 变为了 **Long** 的最小值：
```java
-9223372036854775808
true
```
显然这是发生了溢出，而且是默默地溢出，并没有任何异常。这类问题非常容易被忽略，改进方式有下面 2 种。
方法一是，考虑使用 **Math** 类的 **addExact**、**subtractExact** 等 **xxExact** 方法进行数值运算，这些方法可以在数值溢出时主动抛出异常。我们来测试一下，使用 **Math.addExact** 对 **Long** 最大值做 **+1** 操作：
```java
try {
    long l = Long.MAX_VALUE;
    System.out.println(Math.addExact(l, 1));
} catch (Exception ex) {
    ex.printStackTrace();
}
```
执行后，可以得到 **ArithmeticException**，这是一个 **RuntimeException**：
```log
java.lang.ArithmeticException: long overflow
  at java.lang.Math.addExact(Math.java:809)
  at org.geekbang.time.commonmistakes.numeralcalculations.demo3.CommonMistakesApplication.right2(CommonMistakesApplication.java:25)
  at org.geekbang.time.commonmistakes.numeralcalculations.demo3.CommonMistakesApplication.main(CommonMistakesApplication.java:13)
```
方法二是，使用大数类 **BigInteger**。**BigDecimal** 是处理浮点数的专家，而 **BigInteger** 则是对大数进行科学计算的专家。
如下代码，使用 **BigInteger** 对 **Long** 最大值进行 **+1** 操作；如果希望把计算结果转换一个 **Long** 变量的话，可以使用 **BigInteger** 的 **longValueExact** 方法，在转换出现溢出时，同样会抛出 **ArithmeticException**：
```log
BigInteger i = new BigInteger(String.valueOf(Long.MAX_VALUE));
System.out.println(i.add(BigInteger.ONE).toString());
try {
    long l = i.add(BigInteger.ONE).longValueExact();
} catch (Exception ex) {
    ex.printStackTrace();
}
```
输出结果如下：
```java
9223372036854775808
java.lang.ArithmeticException: BigInteger out of long range
  at java.math.BigInteger.longValueExact(BigInteger.java:4632)
  at org.geekbang.time.commonmistakes.numeralcalculations.demo3.CommonMistakesApplication.right1(CommonMistakesApplication.java:37)
  at org.geekbang.time.commonmistakes.numeralcalculations.demo3.CommonMistakesApplication.main(CommonMistakesApplication.java:11)
```
可以看到，通过 **BigInteger** 对 **Long** 的最大值加 **1** 一点问题都没有，当尝试把结果转换为 **Long** 类型时，则会提示 **BigInteger out of long range**。
## 重点回顾
今天，我与你分享了浮点数的表示、计算、舍入和格式化、溢出等涉及的一些坑。
第一，切记，要精确表示浮点数应该使用 **BigDecimal**。并且，使用 **BigDecimal** 的 **Double** 入参的构造方法同样存在精度丢失问题，应该使用 **String** 入参的构造方法或者 **BigDecimal.valueOf** 方法来初始化。
第二，对浮点数做精确计算，参与计算的各种数值应该始终使用 **BigDecimal**，所有的计算都要通过 **BigDecimal** 的方法进行，切勿只是让 **BigDecimal** 来走过场。任何一个环节出现精度损失，最后的计算结果可能都会出现误差。
第三，对于浮点数的格式化，如果使用 **String.format** 的话，需要认识到它使用的是四舍五入，可以考虑使用 **DecimalFormat** 来明确指定舍入方式。但考虑到精度问题，我更建议使用 **BigDecimal** 来表示浮点数，并使用其 **setScale** 方法指定舍入的位数和方式。
第四，进行数值运算时要小心溢出问题，虽然溢出后不会出现异常，但得到的计算结果是完全错误的。我们考虑使用 **Math.xxxExact** 方法来进行运算，在溢出时能抛出异常，更建议对于可能会出现溢出的大数运算使用 **BigInteger** 类。
总之，对于金融、科学计算等场景，请尽可能使用 **BigDecimal** 和 **BigInteger**，避免由精度和溢出问题引发难以发现，但影响重大的 **Bug**。
## 思考与讨论
**BigDecimal** 提供了 **8** 种舍入模式，你能通过一些例子说说它们的区别吗？
数据库（比如 **MySQL**）中的浮点数和整型数字，你知道应该怎样定义吗？又如何实现浮点数的准确计算呢？
针对数值运算，你还遇到过什么坑吗？
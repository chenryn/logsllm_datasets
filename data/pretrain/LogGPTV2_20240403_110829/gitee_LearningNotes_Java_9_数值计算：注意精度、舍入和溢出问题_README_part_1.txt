今天，我要和你说说数值计算的精度、舍入和溢出问题。
之所以要单独分享数值计算，是因为很多时候我们习惯的或者说认为理所当然的计算，在计算器或计算机看来并不是那么回事儿。就比如前段时间爆出的一条新闻，说是手机计算器把 **10%** + **10%** 算成了 **0.11** 而不是 **0.2**。
出现这种问题的原因在于，国外的计算程序使用的是单步计算法。在单步计算法中，**a+b%** 代表的是 **a*(1+b%)** 。所以，手机计算器计算 **10%+10%** 时，其实计算的是 **10%*（1+10%）**，所以得到的是 **0.11** 而不是 **0.2**。
在我看来，计算器或计算机会得到反直觉的计算结果的原因，可以归结为：
在人看来，浮点数只是具有小数点的数字，**0.1** 和 1 都是一样精确的数字。但，计算机其实无法精确保存浮点数，因此浮点数的计算结果也不可能精确。
在人看来，一个超大的数字只是位数多一点而已，多写几个 1 并不会让大脑死机。但，计算机是把数值保存在了变量中，不同类型的数值变量能保存的数值范围不同，当数值超过类型能表达的数值上限则会发生溢出问题。
接下来，我们就具体看看这些问题吧。
## “危险”的 Double
我们先从简单的反直觉的四则运算看起。对几个简单的浮点数进行加减乘除运算：
```java
System.out.println(0.1+0.2);
System.out.println(1.0-0.8);
System.out.println(4.015*100);
System.out.println(123.3/100);
double amount1 = 2.15;
double amount2 = 1.10;
if (amount1 - amount2 == 1.05)
    System.out.println("OK");
```
输出结果如下：
```text
0.30000000000000004
0.19999999999999996
401.49999999999994
1.2329999999999999
```
可以看到，输出结果和我们预期的很不一样。比如，**0.1+0.2** 输出的不是 **0.3** 而是 0.30000000000000004；再比如，对 **2.15-1.10** 和 **1.05** 判等，结果判等不成立。
出现这种问题的主要原因是，计算机是以二进制存储数值的，浮点数也不例外。**Java** 采用了 **IEEE 754** 标准实现浮点数的表达和运算，你可以通过这里查看数值转化为二进制的结果。
比如，**0.1** 的二进制表示为 **0.0 0011 0011 0011**… （0011 无限循环)，再转换为十进制就是 **0.1000000000000000055511151231257827021181583404541015625**。对于计算机而言，0.1 无法精确表达，这是浮点数计算造成精度损失的根源。
你可能会说，以 0.1 为例，其十进制和二进制间转换后相差非常小，不会对计算产生什么影响。但，所谓积土成山，如果大量使用 **double** 来作大量的金钱计算，最终损失的精度就是大量的资金出入。比如，每天有一百万次交易，每次交易都差一分钱，一个月下来就差 **30** 万。这就不是小事儿了。那，如何解决这个问题呢？
我们大都听说过 **BigDecimal** 类型，浮点数精确表达和运算的场景，一定要使用这个类型。不过，在使用 **BigDecimal** 时有几个坑需要避开。我们用 BigDecimal 把之前的四则运算改一下：
```java
System.out.println(new BigDecimal(0.1).add(new BigDecimal(0.2)));
System.out.println(new BigDecimal(1.0).subtract(new BigDecimal(0.8)));
System.out.println(new BigDecimal(4.015).multiply(new BigDecimal(100)));
System.out.println(new BigDecimal(123.3).divide(new BigDecimal(100)));
```
输出如下：
```java
0.3000000000000000166533453693773481063544750213623046875
0.1999999999999999555910790149937383830547332763671875
401.49999999999996802557689079549163579940795898437500
1.232999999999999971578290569595992565155029296875
```
可以看到，运算结果还是不精确，只不过是精度高了而已。这里给出浮点数运算避坑第一原则：使用 **BigDecimal** 表示和计算浮点数，且务必使用字符串的构造方法来初始化 **BigDecimal**：
```java
System.out.println(new BigDecimal("0.1").add(new BigDecimal("0.2")));
System.out.println(new BigDecimal("1.0").subtract(new BigDecimal("0.8")));
System.out.println(new BigDecimal("4.015").multiply(new BigDecimal("100")));
System.out.println(new BigDecimal("123.3").divide(new BigDecimal("100")));
```
改进后，就能得到我们想要的输出了：
```java
0.3
0.2
401.500
1.233
```
到这里，你可能会继续问，不能调用 **BigDecimal** 传入 **Double** 的构造方法，但手头只有一个 **Double**，如何转换为精确表达的 BigDecimal 呢？
我们试试用 Double.toString 把 double 转换为字符串，看看行不行？
```java
System.out.println(new BigDecimal("4.015").multiply(new BigDecimal(Double.toString(100))));
```
输出为 **401.5000**。与上面字符串初始化 **100** 和 4.015 相乘得到的结果 **401.500** 相比，这里为什么多了 1 个 0 呢？原因就是，**BigDecimal** 有 **scale** 和 precision 的概念，**scale** 表示小数点右边的位数，而 **precision** 表示精度，也就是有效数字的长度。
调试一下可以发现，**new BigDecimal(Double.toString(100))** 得到的 **BigDecimal** 的 **scale=1**、**precision=4**；而 **new BigDecimal(“100”)** 得到的 **BigDecimal** 的 **scale=0、precision=3**。对于 **BigDecimal** 乘法操作，返回值的 **scale** 是两个数的 **scale** 相加。所以，初始化 100 的两种不同方式，导致最后结果的 scale 分别是 4 和 3：
```java
private static void testScale() {
    BigDecimal bigDecimal1 = new BigDecimal("100");
    BigDecimal bigDecimal2 = new BigDecimal(String.valueOf(100d));
    BigDecimal bigDecimal3 = new BigDecimal(String.valueOf(100));
    BigDecimal bigDecimal4 = BigDecimal.valueOf(100d);
    BigDecimal bigDecimal5 = new BigDecimal(Double.toString(100));
    print(bigDecimal1); //scale 0 precision 3 result 401.500
    print(bigDecimal2); //scale 1 precision 4 result 401.5000
    print(bigDecimal3); //scale 0 precision 3 result 401.500
    print(bigDecimal4); //scale 1 precision 4 result 401.5000
    print(bigDecimal5); //scale 1 precision 4 result 401.5000
}
private static void print(BigDecimal bigDecimal) {
    log.info("scale {} precision {} result {}", bigDecimal.scale(), bigDecimal.precision(), bigDecimal.multiply(new BigDecimal("4.015")));
}
```
**BigDecimal** 的 **toString** 方法得到的字符串和 **scale** 相关，又会引出了另一个问题：对于浮点数的字符串形式输出和格式化，我们应该考虑显式进行，通过格式化表达式或格式化工具来明确小数位数和舍入方式。接下来，我们就聊聊浮点数舍入和格式化。
## 考虑浮点数舍入和格式化的方式
除了使用 **Double** 保存浮点数可能带来精度问题外，更匪夷所思的是这种精度问题，加上 **String.format** 的格式化舍入方式，可能得到让人摸不着头脑的结果。
我们看一个例子吧。首先用 **double** 和 **float** 初始化两个 **3.35** 的浮点数，然后通过 **String.format** 使用 **%.1f** 来格式化这 **2** 个数字：
```java
double num1 = 3.35;
float num2 = 3.35f;
System.out.println(String.format("%.1f", num1));//四舍五入
System.out.println(String.format("%.1f", num2));
```
得到的结果居然是 3.4 和 3.3。
这就是由精度问题和舍入方式共同导致的，double 和 float 的 3.35 其实相当于 3.350xxx 和 3.349xxx：
```java
3.350000000000000088817841970012523233890533447265625
3.349999904632568359375
```
**String.format** 采用四舍五入的方式进行舍入，取 1 位小数，double 的 3.350 四舍五入为 3.4，而 float 的 3.349 四舍五入为 3.3。
我们看一下 Formatter 类的相关源码，可以发现使用的舍入模式是 HALF_UP（代码第 11 行）：
```java
else if (c == Conversion.DECIMAL_FLOAT) {
    // Create a new BigDecimal with the desired precision.
    int prec = (precision == -1 ? 6 : precision);
    int scale = value.scale();
    if (scale > prec) {
        // more "scale" digits than the requested "precision"
        int compPrec = value.precision();
        if (compPrec <= scale) {
            // case of 0.xxxxxx
            value = value.setScale(prec, RoundingMode.HALF_UP);
        } else {
            compPrec -= (scale - prec);
            value = new BigDecimal(value.unscaledValue(),
                                   scale,
                                   new MathContext(compPrec));
        }
    }
}
```
如果我们希望使用其他舍入方式来格式化字符串的话，可以设置 DecimalFormat，如下代码所示：
```java
double num1 = 3.35;
float num2 = 3.35f;
DecimalFormat format = new DecimalFormat("#.##");
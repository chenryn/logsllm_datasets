```
改进 equals 和 hashCode 后，再测试下之前的四个用例，结果全部符合预期。
```log
[18:25:23.091] [http-nio-45678-exec-4] [INFO ] [t.c.e.demo1.EqualityMethodController:54  ] - p1.equals(null) ? false
[18:25:23.093] [http-nio-45678-exec-4] [INFO ] [t.c.e.demo1.EqualityMethodController:61  ] - p1.equals(expression) ? false
[18:25:23.094] [http-nio-45678-exec-4] [INFO ] [t.c.e.demo1.EqualityMethodController:67  ] - p1.equals(p2) ? true
[18:25:23.094] [http-nio-45678-exec-4] [INFO ] [t.c.e.demo1.EqualityMethodController:71  ] - points.contains(p2) ? true
```
看到这里，你可能会觉得自己实现 equals 和 hashCode 很麻烦，实现 equals 有很多注意点而且代码量很大。不过，实现这两个方法也有简单的方式，一是后面要讲到的 Lombok 方法，二是使用 IDE 的代码生成功能。IDEA 的类代码快捷生成菜单支持的功能如下：
![img](images/944fe3549e4c24936e9837d0bf1e3936.jpg)
## 注意 compareTo 和 equals 的逻辑一致性
除了自定义类型需要确保 equals 和 hashCode 要逻辑一致外，还有一个更容易被忽略的问题，即 compareTo 同样需要和 equals 确保逻辑一致性。
我之前遇到过这么一个问题，代码里本来使用了 ArrayList 的 indexOf 方法进行元素搜索，但是一位好心的开发同学觉得逐一比较的时间复杂度是 O(n)，效率太低了，于是改为了排序后通过 Collections.binarySearch 方法进行搜索，实现了 O(log n) 的时间复杂度。没想到，这么一改却出现了 Bug。
我们来重现下这个问题。首先，定义一个 Student 类，有 id 和 name 两个属性，并实现了一个 Comparable 接口来返回两个 id 的值：
```java
@Data
@AllArgsConstructor
class Student implements Comparable{
    private int id;
    private String name;
    @Override
    public int compareTo(Student other) {
        int result = Integer.compare(other.id, id);
        if (result==0)
            log.info("this {} == other {}", this, other);
        return result;
    }
}
```
然后，写一段测试代码分别通过 indexOf 方法和 Collections.binarySearch 方法进行搜索。列表中我们存放了两个学生，第一个学生 id 是 1 叫 zhang，第二个学生 id 是 2 叫 wang，搜索这个列表是否存在一个 id 是 2 叫 li 的学生：
```java
@GetMapping("wrong")
public void wrong(){
    List list = new ArrayList<>();
    list.add(new Student(1, "zhang"));
    list.add(new Student(2, "wang"));
    Student student = new Student(2, "li");
    log.info("ArrayList.indexOf");
    int index1 = list.indexOf(student);
    Collections.sort(list);
    log.info("Collections.binarySearch");
    int index2 = Collections.binarySearch(list, student);
    log.info("index1 = " + index1);
    log.info("index2 = " + index2);
}
```
代码输出的日志如下：
```log
[18:46:50.226] [http-nio-45678-exec-1] [INFO ] [t.c.equals.demo2.CompareToController:28  ] - ArrayList.indexOf
[18:46:50.226] [http-nio-45678-exec-1] [INFO ] [t.c.equals.demo2.CompareToController:31  ] - Collections.binarySearch
[18:46:50.227] [http-nio-45678-exec-1] [INFO ] [t.c.equals.demo2.CompareToController:67  ] - this CompareToController.Student(id=2, name=wang) == other CompareToController.Student(id=2, name=li)
[18:46:50.227] [http-nio-45678-exec-1] [INFO ] [t.c.equals.demo2.CompareToController:34  ] - index1 = -1
[18:46:50.227] [http-nio-45678-exec-1] [INFO ] [t.c.equals.demo2.CompareToController:35  ] - index2 = 1
```
我们注意到如下几点：
binarySearch 方法内部调用了元素的 compareTo 方法进行比较；
indexOf 的结果没问题，列表中搜索不到 id 为 2、name 是 li 的学生；
binarySearch 返回了索引 1，代表搜索到的结果是 id 为 2，name 是 wang 的学生。
修复方式很简单，确保 compareTo 的比较逻辑和 equals 的实现一致即可。重新实现一下 Student 类，通过 Comparator.comparing 这个便捷的方法来实现两个字段的比较：
```java
@Data
@AllArgsConstructor
class StudentRight implements Comparable{
    private int id;
    private String name;
    @Override
    public int compareTo(StudentRight other) {
        return Comparator.comparing(StudentRight::getName)
                .thenComparingInt(StudentRight::getId)
                .compare(this, other);
    }
}
```
其实，这个问题容易被忽略的原因在于两方面：
一是，我们使用了 Lombok 的 @Data 标记了 Student，@Data 注解（详见这里）其实包含了 @EqualsAndHashCode 注解（详见这里）的作用，也就是默认情况下使用类型所有的字段（不包括 static 和 transient 字段）参与到 equals 和 hashCode 方法的实现中。因为这两个方法的实现不是我们自己实现的，所以容易忽略其逻辑。
二是，compareTo 方法需要返回数值，作为排序的依据，容易让人使用数值类型的字段随意实现。
我再强调下，对于自定义的类型，如果要实现 Comparable，请记得 equals、hashCode、compareTo 三者逻辑一致。
## 小心 Lombok 生成代码的“坑”
Lombok 的 @Data 注解会帮我们实现 equals 和 hashcode 方法，但是有继承关系时，Lombok 自动生成的方法可能就不是我们期望的了。
我们先来研究一下其实现：定义一个 Person 类型，包含姓名和身份证两个字段：
```java
@Data
class Person {
    private String name;
    private String identity;
    public Person(String name, String identity) {
        this.name = name;
        this.identity = identity;
    }
}
```
对于身份证相同、姓名不同的两个 Person 对象：
```java
Person person1 = new Person("zhuye","001");
Person person2 = new Person("Joseph","001");
log.info("person1.equals(person2) ? {}", person1.equals(person2));
```
使用 equals 判等会得到 false。如果你希望只要身份证一致就认为是同一个人的话，可以使用 @EqualsAndHashCode.Exclude 注解来修饰 name 字段，从 equals 和 hashCode 的实现中排除 name 字段：
```java
@EqualsAndHashCode.Exclude
private String name;
```
修改后得到 true。打开编译后的代码可以看到，Lombok 为 Person 生成的 equals 方法的实现，确实只包含了 identity 属性：
```java
public boolean equals(final Object o) {
    if (o == this) {
        return true;
    } else if (!(o instanceof LombokEquealsController.Person)) {
        return false;
    } else {
        LombokEquealsController.Person other = (LombokEquealsController.Person)o;
        if (!other.canEqual(this)) {
            return false;
        } else {
            Object this$identity = this.getIdentity();
            Object other$identity = other.getIdentity();
            if (this$identity == null) {
                if (other$identity != null) {
                    return false;
                }
            } else if (!this$identity.equals(other$identity)) {
                return false;
            }
            return true;
        }
    }
}
```
但到这里还没完，如果类型之间有继承，Lombok 会怎么处理子类的 equals 和 hashCode 呢？我们来测试一下，写一个 Employee 类继承 Person，并新定义一个公司属性：
```java
@Data
class Employee extends Person {
    private String company;
    public Employee(String name, String identity, String company) {
        super(name, identity);
        this.company = company;
    }
}
```
在如下的测试代码中，声明两个 Employee 实例，它们具有相同的公司名称，但姓名和身份证均不同：
```java
Employee employee1 = new Employee("zhuye","001", "bkjk.com");
Employee employee2 = new Employee("Joseph","002", "bkjk.com");
log.info("employee1.equals(employee2) ? {}", employee1.equals(employee2));  
```
很遗憾，结果是 true，显然是没有考虑父类的属性，而认为这两个员工是同一人，说明 @EqualsAndHashCode 默认实现没有使用父类属性。
为解决这个问题，我们可以手动设置 callSuper 开关为 true，来覆盖这种默认行为：
```java
@Data
@EqualsAndHashCode(callSuper = true)
class Employee extends Person {
```
修改后的代码，实现了同时以子类的属性 company 加上父类中的属性 identity，作为 equals 和 hashCode 方法的实现条件（实现上其实是调用了父类的 equals 和 hashCode）。
## 重点回顾
现在，我们来回顾下对象判等和比较的重点内容吧。
首先，我们要注意 equals 和 == 的区别。业务代码中进行内容的比较，针对基本类型只能使用 ==，针对 Integer、String 在内的引用类型，需要使用 equals。Integer 和 String 的坑在于，使用 == 判等有时也能获得正确结果。
其次，对于自定义类型，如果类型需要参与判等，那么务必同时实现 equals 和 hashCode 方法，并确保逻辑一致。如果希望快速实现 equals、hashCode 方法，我们可以借助 IDE 的代码生成功能，或使用 Lombok 来生成。如果类型也要参与比较，那么 compareTo 方法的逻辑同样需要和 equals、hashCode 方法一致。
最后，Lombok 的 @EqualsAndHashCode 注解实现 equals 和 hashCode 的时候，默认使用类型所有非 static、非 transient 的字段，且不考虑父类。如果希望改变这种默认行为，可以使用 @EqualsAndHashCode.Exclude 排除一些字段，并设置 callSuper = true 来让子类的 equals 和 hashCode 调用父类的相应方法。
在比较枚举值和 POJO 参数值的例子中，我们还可以注意到，使用 == 来判断两个包装类型的低级错误，确实容易被忽略。所以，我建议你在 IDE 中安装阿里巴巴的 Java 规约插件（详见这里），来及时提示我们这类低级错误：
![img](images/fe020d747a35cec23e5d92c1277d02c3.png)
今天用到的代码，我都放在了 GitHub 上，你可以点击这个链接查看。
## 思考与讨论
在实现 equals 时，我是先通过 getClass 方法判断两个对象的类型，你可能会想到还可以使用 instanceof 来判断。你能说说这两种实现方式的区别吗？
在第三节的例子中，我演示了可以通过 HashSet 的 contains 方法判断元素是否在 HashSet 中，同样是 Set 的 TreeSet 其 contains 方法和 HashSet 有什么区别吗？
有关对象判等、比较，你还遇到过其他坑吗？
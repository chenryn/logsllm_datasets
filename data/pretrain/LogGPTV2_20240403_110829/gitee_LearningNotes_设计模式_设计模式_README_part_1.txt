#  设计模式
## 前言
有一些重要的设计原则在开篇和大家分享下，这些原则将贯通全文：
- 面向接口编程，而不是面向实现。这个很重要，也是优雅的、可扩展的代码的第一步，这就不需要多说了吧。
- 职责单一原则。每个类都应该只有一个单一的功能，并且该功能应该由这个类完全封装起来。
- 对修改关闭，对扩展开放。对修改关闭是说，我们辛辛苦苦加班写出来的代码，该实现的功能和该修复的 bug 都完成了，别人可不能说改就改；对扩展开放就比较好理解了，也就是说在我们写好的代码基础上，很容易实现扩展。
创建型模式比较简单，但是会比较没有意思，结构型和行为型比较有意思
每个代理模式的代码都必须自己手动完成一遍。
## 创建型模式
创建型模式的作用就是创建对象，说到创建一个对象，最熟悉的就是 new 一个对象，然后 set 相关属性。但是，在很多场景下，我们需要给客户端提供更加友好的创建对象的方式，尤其是那种我们定义了类，但是需要提供给其他开发者用的时候。
工厂模式分为简单工厂模式，工厂模式，抽象工厂模式
在工厂模式中，我们在创建对象时不会对客户端暴露创建逻辑，并且是通过使用一个共同的接口来指向新创建的对象。**本质就是使用工厂方法代替new操作。**
### 简单工厂模式
```java
public class FoodFactory {
    public static Food makeFood(String name) {
        if (name.equals("兰州拉面")) {
            Food noodle = new LanZhouNoodle();
            System.out.println("兰州拉面"+noodle+"出锅啦");
            return noodle;
        } else if (name.equals("黄焖鸡")) {
            Food chicken = new HuangMenChicken();
            System.out.println("黄焖鸡"+ chicken +"出锅啦");
            return chicken;
        } else {
            System.out.println("不知道你做的什么哦~");
            return null;
        }
    }
}
```
其中，LanZhouNoodle 和 HuangMenChicken 都继承自 Food。
```java
public class Cook {
    public static void main(String[] args) {
        Food food = FoodFactory.makeFood("黄焖鸡");
        FoodFactory.makeFood("jaja");
    }
}
```
简单地说，**简单工厂模式通常就是这样，一个工厂类 XxxFactory，里面有一个静态方法，根据我们不同的参数，返回不同的派生自同一个父类（或实现同一接口）的实例对象。**
> 我们强调**职责单一**原则，一个类只提供一种功能，FoodFactory 的功能就是只要负责生产各种 Food。
在此例中可以看出，Cook 类在使用 FoodFactory 时就不需要 new 任何一个对象，这就是简单工厂模式的好处，封装了 new 的部分，做到的代码易用性。
### 工厂模式
简单工厂模式很简单，如果它能满足我们的需要，我觉得就不要折腾了。之所以需要引入工厂模式，是因为我们往往需要使用两个或两个以上的工厂。
```java
public interface FoodFactory {
    Food makeFood(String name);
}
public class ChineseFoodFactory implements FoodFactory {
    @Override
    public Food makeFood(String name) {
        if (name.equals("A")) {
            return new ChineseFoodA();
        } else if (name.equals("B")) {
            return new ChineseFoodB();
        } else {
            return null;
        }
    }
}
public class AmericanFoodFactory implements FoodFactory {
    @Override
    public Food makeFood(String name) {
        if (name.equals("A")) {
            return new AmericanFoodA();
        } else if (name.equals("B")) {
            return new AmericanFoodB();
        } else {
            return null;
        }
    }
}
```
其中，ChineseFoodA、ChineseFoodB、AmericanFoodA、AmericanFoodB 都派生自 Food。
客户端调用：
```java
public class APP {
    public static void main(String[] args) {
        // 先选择一个具体的工厂
        FoodFactory factory = new ChineseFoodFactory();
        // 由第一步的工厂产生具体的对象，不同的工厂造出不一样的对象
        Food food = factory.makeFood("A");
    }
}
```
虽然都是调用 makeFood("A") 制作 A 类食物，但是，不同的工厂生产出来的完全不一样。
第一步，我们需要选取合适的工厂，然后第二步基本上和简单工厂一样。
**核心在于，我们需要在第一步选好我们需要的工厂**。比如，我们有 LogFactory 接口，实现类有 FileLogFactory 和 KafkaLogFactory，分别对应将日志写入文件和写入 Kafka 中，显然，我们客户端第一步就需要决定到底要实例化 FileLogFactory 还是 KafkaLogFactory，这将决定之后的所有的操作。
### 抽象工厂模式
当涉及到**产品族**的时候，就需要引入抽象工厂模式了。 一个经典的例子是造一台电脑 。
当涉及到这种产品族的问题的时候，就需要抽象工厂模式来支持了。我们不再定义 CPU 工厂、主板工厂、硬盘工厂、显示屏工厂等等，我们直接定义电脑工厂，每个电脑工厂负责生产所有的设备，这样能保证肯定不存在兼容问题。
当然，抽象工厂的问题也是显而易见的，比如我们要加个显示器，就需要修改所有的工厂，给所有的工厂都加上制造显示器的方法。这有点违反了**对修改关闭，对扩展开放**这个设计原则。
本节要介绍的抽象工厂模式将考虑多等级产品的生产，将同一个具体工厂所生产的位于不同等级的一组产品称为一个产品族，图 1 所示的是海尔工厂和 TCL 工厂所生产的电视机与空调对应的关系图。
![电器工厂的产品等级与产品族](images/3-1Q1141559151S.gif)
抽象工厂（AbstractFactory）模式的定义：是一种为访问类提供一个创建一组相关或相互依赖对象的接口，且访问类无须指定所要产品的具体类就能得到同族的不同等级的产品的模式结构。
抽象工厂模式是工厂方法模式的升级版本，工厂方法模式只生产一个等级的产品，而抽象工厂模式可生产多个等级的产品。
使用抽象工厂模式一般要满足以下条件。
- 系统中有多个产品族，每个具体工厂创建同一族但属于不同等级结构的产品。
- 系统一次只可能消费其中某一族产品，即同族的产品一起使用。
抽象工厂模式除了具有工厂方法模式的优点外，其他主要优点如下。
- 可以在类的内部对产品族中相关联的多等级产品共同管理，而不必专门引入多个新的类来进行管理。
- 当增加一个新的产品族时不需要修改原代码，满足开闭原则。
其缺点是：当产品族中需要增加一个新的产品时，所有的工厂类都需要进行修改。
### 单例模式
简单点说，就是一个应用程序中，某个类的实例对象只有一个，你没有办法去new，因为构造器是被private修饰的，一般通过getInstance()的方法来获取它们的实例。
getInstance()的返回值是一个对象的引用，并不是一个新的实例，所以不要错误的理解成多个对象。
**特点**
- 类构造器私有
- 持有自己类型的属性
- 对外提供获取实例的静态方法
**饿汉式写法**
```
public class Singleton {  
   private static Singleton instance = new Singleton();  
   private Singleton (){}  
   public static Singleton getInstance() {  
   return instance;  
   }  
}
```
弊端：因为类加载的时候就会创建对象，所以有的时候还不需要使用对象，就会创建对象，造成内存的浪费；
**饱汉模式最容易出错：**
```
public class Singleton {
    // 首先，也是先堵死 new Singleton() 这条路
    private Singleton() {}
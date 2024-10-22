    // 和饿汉模式相比，这边不需要先实例化出来，注意这里的 volatile，它是必须的
    private static volatile Singleton instance = null;
    public static Singleton getInstance() {
        if (instance == null) {
            // 加锁
            synchronized (Singleton.class) {
                // 这一次判断也是必须的，不然会有并发问题
                if (instance == null) {
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```
> 双重检查，指的是两次检查 instance 是否为 null。
>
> volatile 在这里是需要的，希望能引起读者的关注。
>
> 很多人不知道怎么写，直接就在 getInstance() 方法签名上加上 synchronized，这就不多说了，性能太差。
嵌套类最经典，以后大家就用它吧：
```
public class Singleton {
    private Singleton() {}
    // 主要是使用了 嵌套类可以访问外部类的静态属性和静态方法 的特性
    private static class Holder {
        private static Singleton instance = new Singleton();
    }
    public static Singleton getInstance() {
        return Holder.instance;
    }
}
```
> 注意，很多人都会把这个**嵌套类**说成是**静态内部类**，严格地说，内部类和嵌套类是不一样的，它们能访问的外部类权限也是不一样的。
最后，我们说一下枚举，枚举很特殊，它在类加载的时候会初始化里面的所有的实例，而且 JVM 保证了它们不会再被实例化，所以它天生就是单例的。
**TODO:**
建造者模式
原型模式
## 结构型模式
前面创建型模式介绍了创建对象的一些设计模式，这节介绍的结构型模式旨在通过改变代码结构来达到解耦的目的，使得我们的代码容易维护和扩展。
### 代理模式
第一个要介绍的代理模式是最常使用的模式之一了，用一个代理来隐藏具体实现类的实现细节，通常还用于在真实的实现的前后添加一部分逻辑。
既然说是**代理**，那就要对客户端隐藏真实实现，由代理来负责客户端的所有请求。当然，代理只是个代理，它不会完成实际的业务逻辑，而是一层皮而已，但是对于客户端来说，它必须表现得就是客户端需要的真实实现。
理解**代理**这个词，这个模式其实就简单了。 下面上代码理解。 代理接口：
```
//要有一个代理接口让实现类和代理实现类来实现。
public interface FoodService {
    Food makeChicken();
}
```
被代理的实现类：
```
public class FoodServiceImpl implements FoodService {
    @Override
    public Food makeChicken() {
        Food f = new Chicken();
        f.setChicken("1kg");
        f.setSpicy("1g");
        f.setSalt("3g");
        System.out.println("鸡肉加好佐料了");
        return f;
    }
}
```
被代理实现类就只需要做自己该做的事情就好了，不需要管别的。
代理实现类：
```
public class FoodServiceProxy implements FoodService {
    // 内部一定要有一个真实的实现类，当然也可以通过构造方法注入
    private FoodService foodService = new FoodServiceImpl();
    @Override
    public Food makeChicken() {
        System.out.println("开始制作鸡肉");
        // 如果我们定义这句为核心代码的话，那么，核心代码是真实实现类做的，
        // 代理只是在核心代码前后做些“无足轻重”的事情
        Food food = foodService.makeChicken();
        System.out.println("鸡肉制作完成啦，加点胡椒粉");
        food.addCondiment("pepper");
        System.out.println("上锅咯");
        return food;
    }
}
```
客户端调用，注意，我们要用代理来实例化接口：
```
// 这里用代理类来实例化
FoodService foodService = new FoodServiceProxy();
foodService.makeChicken();
```
所谓代理模式，**就是对被代理方法包装或者叫增强， 在面向切面编程（AOP）中，其实就是动态代理的过程。比如 Spring 中，我们自己不定义代理类，但是 Spring 会帮我们动态来定义代理，然后把我们定义在 @Before、@After、@Around 中的代码逻辑动态添加到代理中。**
待续。。。
## 行为型模式
### 模板模式
在含有继承结构的代码中，模板方法模式是非常常用的。
**父类定义了骨架（调用哪些方法及顺序），某些特定方法由子类实现**
模板方法只负责定义第一步应该要做什么，第二步应该做什么，第三步应该做什么，至于怎么做，由子类来实现。
好处：代码复用，减少重复代码。除了子类要实现的特定方法，其他方法及方法调用顺序都在父类中预先写好
缺点： 每一个不同的实现都需要一个子类来实现，导致类个数增加，使系统更加庞大
**模板模式的关键点：**
    1、使用抽象类定义模板类，并在其中定义所有的基本方法、模板方法，钩子方法，不限数量，以实现功能逻辑为主。其中基本方法使用final修饰，其中要调用基本方法和钩子方法，基本方法和钩子方法可以使用protected修饰，表明可被子类修改。
    2、定义实现抽象类的子类，重写其中的模板方法，甚至钩子方法，完善具体的逻辑。
  使用场景：
    1、在多个子类中拥有相同的方法，而且逻辑相同时，可以将这些方法抽出来放到一个模板抽象类中。
    2、程序主框架相同，细节不同的情况下，也可以使用模板方法。
#### 架构方法介绍
模板方法使得子类可以在不改变算法结构的情况下，重新定义算法中的某些步骤。其主要分为两大类：模版方法和基本方法，而基本方法又分为：抽象方法（Abstract Method），具体方法（Concrete Method），钩子方法（Hook Method）。
四种方法的基本定义（前提：在抽象类中定义）：
（1）抽象方法：由抽象类声明，由具体子类实现，并以abstract关键字进行标识。
（2）具体方法：由抽象类声明并且实现，子类并不实现或者做覆盖操作。其实质就是普遍适用的方法，不需要子类来实现。
（3）钩子方法：由抽象类声明并且实现，子类也可以选择加以扩展。通常抽象类会给出一个空的钩子方法，也就是没有实现的扩展。**它和具体方法在代码上没有区别，不过是一种意识的区别**；而它和抽象方法有时候也是没有区别的，就是在子类都需要将其实现的时候。而不同的是抽象方法必须实现，而钩子方法可以不实现。也就是说钩子方法为你在实现某一个抽象类的时候提供了可选项，**相当于预先提供了一个默认配置。**
（4）模板方法：定义了一个方法，其中定义了整个逻辑的基本骨架。
```
public abstract class AbstractTemplate {
    // 这就是模板方法
    public void templateMethod() {
        init();
        apply(); // 这个是重点
        end(); // 可以作为钩子方法
    }
	//这是具体方法
    protected void init() {
        System.out.println("init 抽象层已经实现，子类也可以选择覆写");
    }
    // 这是抽象方法，留给子类实现
    protected abstract void apply();
	//这是钩子方法，可定义一个默认操作，或者为空
    protected void end() {
    }
}
```
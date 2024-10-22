可以看到，C中的方法全部通过调用h实现，其中h就是InvocationHandler，是我们在生成C时传递的第三个参数。这里还有个关键就是SayHello方法（业务方法）跟调用invoke方法时传递的参数m4一定要是一一对应的，但是这些对我们来说都是透明的，由Proxy在newProxyInstance时保证的。留心看到C在invoke时把自己this传递了过去，InvocationHandler的invoke的第一个方法也就是我们的动态代理实例类，业务上有需要就可以使用它。（所以千万不要在invoke方法里把请求分发给第一个参数，否则很明显就死循环了）C类中有B中所有方法的成员变量
```
private static Method m1;
private static Method m3;
private static Method m4;
private static Method m2;
private static Method m0;
```
这些变量在static静态代码块初始化，这些变量是在调用invocationhander时必要的入参，也让我们依稀看到Proxy在生成C时留下的痕迹。
```
static
  {
    try
    {
      m1 = Class.forName("java.lang.Object").getMethod("equals", new Class[] { Class.forName("java.lang.Object") });
      m3 = Class.forName("jiankunking.Subject").getMethod("SayGoodBye", new Class[0]);
      m4 = Class.forName("jiankunking.Subject").getMethod("SayHello", new Class[] { Class.forName("java.lang.String") });
      m2 = Class.forName("java.lang.Object").getMethod("toString", new Class[0]);
      m0 = Class.forName("java.lang.Object").getMethod("hashCode", new Class[0]);
      return;
    }
    catch (NoSuchMethodException localNoSuchMethodException)
    {
      throw new NoSuchMethodError(localNoSuchMethodException.getMessage());
    }
    catch (ClassNotFoundException localClassNotFoundException)
    {
      throw new NoClassDefFoundError(localClassNotFoundException.getMessage());
    }
  }
```
从以上分析来看，要想彻底理解一个东西，再多的理论不如看源码，底层的原理非常重要。
jdk动态代理类图如下
![image-20200429101023902](images/image-20200429101023902.png)
## CGLIB动态代理
我们了解到，“代理”的目的是构造一个和被代理的对象有同样行为的对象，一个对象的行为是在类中定义的，对象只是类的实例。所以构造代理，不一定非得通过持有、包装对象这一种方式。
通过“继承”可以继承父类所有的公开方法，然后可以重写这些方法，在重写时对这些方法增强，这就是cglib的思想。根据里氏代换原则（LSP），父类需要出现的地方，子类可以出现，所以cglib实现的代理也是可以被正常使用的。
先看下代码
```java
package proxy;
import java.lang.reflect.Method;
import net.sf.cglib.proxy.Enhancer;
import net.sf.cglib.proxy.MethodInterceptor;
import net.sf.cglib.proxy.MethodProxy;
public class CglibProxy implements MethodInterceptor
{
    // 根据一个类型产生代理类，此方法不要求一定放在MethodInterceptor中
    public Object CreatProxyedObj(Class clazz)
    {
        Enhancer enhancer = new Enhancer();
        enhancer.setSuperclass(clazz);
        enhancer.setCallback(this);
        return enhancer.create();
    }
    @Override
    public Object intercept(Object arg0, Method arg1, Object[] arg2, MethodProxy arg3) throws Throwable
    {
        // 这里增强
        System.out.println("收钱");
        return arg3.invokeSuper(arg0, arg2);
    } 
}
```
从代码可以看出，它和jdk动态代理有所不同，对外表现上看CreatProxyedObj，它只需要一个类型clazz就可以产生一个代理对象， 所以说是“类的代理”，且创造的对象通过打印类型发现也是一个新的类型。不同于jdk动态代理，jdk动态代理要求对象必须实现接口（三个参数的第二个参数），cglib对此没有要求。
cglib的原理是这样，它生成一个继承B的类型C（代理类），这个代理类持有一个MethodInterceptor，我们setCallback时传入的。 C重写所有B中的方法（方法名一致），然后在C中，构建名叫“CGLIB”+“$父类方法名$”的方法（下面叫cglib方法，所有非private的方法都会被构建），方法体里只有一句话super.方法名()，可以简单的认为保持了对父类方法的一个引用，方便调用。
这样的话，C中就有了重写方法、cglib方法、父类方法（不可见），还有一个统一的拦截方法（增强方法intercept）。其中重写方法和cglib方法肯定是有映射关系的。
C的重写方法是外界调用的入口（LSP原则），它调用MethodInterceptor的intercept方法，调用时会传递四个参数，第一个参数传递的是this，代表代理类本身，第二个参数标示拦截的方法，第三个参数是入参，第四个参数是cglib方法，intercept方法完成增强后，我们调用cglib方法间接调用父类方法完成整个方法链的调用。
这里有个疑问就是intercept的四个参数，为什么我们使用的是arg3而不是arg1?
```
    @Override
    public Object intercept(Object arg0, Method arg1, Object[] arg2, MethodProxy arg3) throws Throwable
    {
        System.out.println("收钱");
        return arg3.invokeSuper(arg0, arg2);
    }
```
 因为如果我们通过反射 arg1.invoke(arg0, ...)这种方式是无法调用到父类的方法的，子类有方法重写，隐藏了父类的方法，父类的方法已经不可见，如果硬调arg1.invoke(arg0, ...)很明显会死循环。
所以调用的是cglib开头的方法，但是，我们使用arg3也不是简单的invoke，而是用的invokeSuper方法，这是因为cglib采用了fastclass机制，不仅巧妙的避开了调不到父类方法的问题，还加速了方法的调用。
fastclass基本原理是，给每个方法编号，通过编号找到方法执行避免了通过反射调用。
对比JDK动态代理，cglib依然需要一个第三者分发请求，只不过jdk动态代理分发给了目标对象，cglib最终分发给了自己，通过给method编号完成调用。cglib是继承的极致发挥，本身还是很简单的，只是fastclass需要另行理解。
## JDK动态代理和CGLIB的区别
DK动态代理只能对实现了接口的类生成代理，而不能针对类。
CGLIB是针对类实现代理，主要是对指定的类生成一个子类，覆盖其中的方法，并覆盖其中方法实现增强，但是因为采用的是继承，所以该类或方法最好不要声明成final， 对于final类或方法，是无法继承的
使用CGLib实现动态代理，CGLib底层采用ASM字节码生成框架，使用字节码技术生成代理类，在jdk6之前比使用Java反射效率要高。唯一需要注意的是，CGLib不能对声明为final的方法进行代理，因为CGLib原理是动态生成被代理类的子类
在jdk6、jdk7、jdk8逐步对JDK动态代理优化之后，在调用次数较少的情况下，JDK代理效率高于CGLIB代理效率，只有当进行大量调用的时候，jdk6和jdk7比CGLIB代理效率低一点，但是到jdk8的时候，jdk代理效率高于CGLIB代理，总之，每一次jdk版本升级，jdk代理效率都得到提升，而CGLIB代理消息确有点跟不上步伐Spring如何选择用
JDK还是CGLIB？
- 当Bean实现接口时，Spring就会用JDK的动态代理。
- 当Bean没有实现接口时，Spring使用CGlib是实现。
为什么继承只能使用CGLib，因为JDK代理生成的代理类，默认会继承一个类，由于java是单继承，所以当原始类继承一个类的时候，只能使用CGLib动态代理
## 总结
- 如果目标对象实现了接口，默认情况下会采用JDK的动态代理实现AOP。
- 如果目标对象实现了接口，可以强制使用CGLIB实现AOP。
- 如果目标对象没有实现了接口，必须采用CGLIB库，Spring会自动在JDK动态代理和CGLIB之间转换
JDK代理是不需要第三方库支持，只需要JDK环境就可以进行代理，使用条件:
- 实现InvocationHandler 
- 使用Proxy.newProxyInstance产生代理对象
- 被代理的对象必须要实现接口
CGLib必须依赖于CGLib的类库，但是它需要类来实现任何接口代理的是指定的类生成一个子类，
## 来源
https://blog.csdn.net/yhl_jxy/article/details/80635012
https://blog.csdn.net/flyfeifei66/article/details/81481222
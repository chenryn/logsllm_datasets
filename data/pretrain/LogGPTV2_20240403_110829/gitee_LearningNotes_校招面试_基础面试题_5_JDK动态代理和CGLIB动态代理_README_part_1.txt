# Java两种动态代理JDK动态代理和CGLIB动态代理
## 代理模式
代理模式是23种设计模式的一种，他是指一个对象A通过持有另一个对象B，可以具有B同样的行为的模式。为了对外开放协议，B往往实现了一个接口，A也会去实现接口。但是B是“真正”实现类，A则比较“虚”，他借用了B的方法去实现接口的方法。A虽然是“伪军”，但它可以增强B，在调用B的方法前后都做些其他的事情。Spring AOP就是使用了动态代理完成了代码的动态“织入”。
使用代理好处还不止这些，一个工程如果依赖另一个工程给的接口，但是另一个工程的接口不稳定，经常变更协议，就可以使用一个代理，接口变更时，只需要修改代理，不需要一一修改业务代码。从这个意义上说，所有调外界的接口，我们都可以这么做，不让外界的代码对我们的代码有侵入，这叫防御式编程。代理其他的应用可能还有很多。
上述例子中，类A写死持有B，就是B的静态代理。如果A代理的对象是不确定的，就是动态代理。动态代理目前有两种常见的实现，jdk动态代理和cglib动态代理。
## JDK动态代理
jdk动态代理是jre提供给我们的类库，可以直接使用，不依赖第三方。先看下jdk动态代理的使用代码，再理解原理。首先有个“明星”接口类，有唱、跳两个功能：
```java
public interface Star
{
    String sing(String name);
    String dance(String name);
}
```
然后有明星实现类，“刘德华”
```java
public class LiuDeHua implements Star
{   
    @Override
    public String sing(String name)
    {
         System.out.println("给我一杯忘情水");
        return "唱完" ;
    }
    @Override
    public String dance(String name)
    {
        System.out.println("开心的马骝");
        return "跳完" ;
    }
}
```
明星演出前需要有人收钱，由于要准备演出，自己不做这个工作，一般交给一个经纪人。便于理解，它的名字以Proxy结尾，但他不是代理类，原因是它没有实现我们的明星接口，无法对外服务，它仅仅是一个wrapper。
```
package proxy;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
public class StarProxy implements InvocationHandler
{
    // 目标类，也就是被代理对象
    private Object target;
    public void setTarget(Object target)
    {
        this.target = target;
    }
    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable
    {
        // 这里可以做增强
        System.out.println("收钱");
        Object result = method.invoke(target, args);
        return result;
    }
    // 生成代理类
    public Object CreatProxyedObj()
    {
        return Proxy.newProxyInstance(target.getClass().getClassLoader(), target.getClass().getInterfaces(), this);
    }  
}
```
上述例子中，方法CreatProxyedObj返回的对象才是我们的代理类，它需要三个参数，前两个参数的意思是在同一个classloader下通过接口创建出一个对象，该对象需要一个属性，也就是第三个参数，它是一InvocationHandler。需要注意的是这个CreatProxyedObj方法不一定非得在我们的StarProxy类中，往往放在一个工厂类中。上述代理的代码使用过程一般如下：
- new一个目标对象
- new一个InvocationHandler，将目标对象set进去
- 通过CreatProxyedObj创建代理对象，强转为目标对象的接口类型即可使用，实际上生成的代理对象实现了目标接口。
```
Star ldh = new LiuDeHua();
StarProxy proxy = new StarProxy();
proxy.setTarget(ldh); 
Object obj = proxy.CreatProxyedObj();
Star star = (Star)obj;
```
Proxy（jdk类库提供）根据B的接口生成一个实现类，我们称为C，它就是动态代理类（该类型是 $Proxy+数字 的“新的类型”）。生成过程是：由于拿到了接口，便可以获知接口的所有信息（主要是方法的定义），也就能声明一个新的类型去实现该接口的所有方法，这些方法显然都是“虚”的，它调用另一个对象的方法。当然这个被调用的对象不能是对象B，如果是对象B，我们就没法增强了，等于饶了一圈又回来了。
所以它调用的是B的包装类，这个包装类需要我们来实现，但是jdk给出了约束，它必须实现InvocationHandler，上述例子中就是StarProxy， 这个接口里面有个方法，它是所有Target的所有方法的调用入口（invoke），调用之前我们可以加自己的代码增强。
看下我们的实现，我们在InvocationHandler里调用了对象B（target）的方法，调用之前增强了B的方法。
```java
@Override
public Object invoke(Object proxy, Method method, Object[] args) throws Throwable
{
    // 这里增强
    System.out.println("收钱");
    Object result = method.invoke(target, args);
    return result;
}
```
所以可以这么认为C代理了InvocationHandler，InvocationHandler代理了我们的类B，两级代理。
整个JDK动态代理的秘密也就这些，简单一句话，动态代理就是要生成一个包装类对象，由于代理的对象是动态的，所以叫动态代理。由于我们需要增强，这个增强是需要留给开发人员开发代码的，因此代理类不能直接包含被代理对象，而是一个InvocationHandler，该InvocationHandler包含被代理对象，并负责分发请求给被代理对象，分发前后均可以做增强。从原理可以看出，JDK动态代理是“对象”的代理。
下面看下动态代理类到底如何调用的InvocationHandler的，为什么InvocationHandler的一个invoke方法能为分发target的所有方法。C中的部分代码示例如下，通过反编译生成后的代码查看，摘自链接地址。Proxy创造的C是自己（Proxy）的子类，且实现了B的接口，一般都是这么修饰的：
```java
public final class XXX extends Proxy implements XXX
```
一个方法代码如下
```java
  public final String SayHello(String paramString)
  {
    try
    {
      return (String)this.h.invoke(this, m4, new Object[] { paramString });
    }
    catch (Error|RuntimeException localError)
    {
      throw localError;
    }
    catch (Throwable localThrowable)
    {
      throw new UndeclaredThrowableException(localThrowable);
    }
}    
```
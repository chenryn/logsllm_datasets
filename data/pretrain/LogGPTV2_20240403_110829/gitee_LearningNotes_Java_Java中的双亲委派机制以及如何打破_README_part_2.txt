### Tomcat第二部分自定义类加载器（绿色部分）
绿色是Java项目在打war包的时候，tomcat自动生成的类加载器，也就是说，每一个项目打成war包，tomcat都会自动生成一个类加载器，专门用来加载这个war包，而这个类加载器打破了双亲委派机制，我们可以想象一下，加入这个webapp类没有打破双亲委派机制会怎么样？
如果没有打破，它就会委托父类加载器去加载，一旦加载到了，紫烈加载器就没有机会加载了，那么Spring4和Spring5的项目就没有可能共存了。
所以，这一部分它打破了双亲委派机制，这样一来webapp类加载器就不需要在让上级类去加载，它自己就可以加载对应的war里的class文件，当然了，其它的项目文件还是要委托上级加载的。
### 举例
我们首先列举一个场景，比如现在我有一个自定义类加载器，加载的是 /com/lxl/jvm/User1.class类，而在应用程序的target目录下也有一个 com/lxl/jvm/User1.class，那么最终User1.class这个类将被哪个类加载器加载呢？根据双亲委派机制，我们知道它一定是被应用程序类加载器AppClassLoader加载，而不是我们自定义的类加载器，为什么呢？因为他要向上寻找，向下委托，当找到以后，便不再向后执行了。
而我们要打破双亲委派机制，就是要让自定义类加载器来加载我们的User1.class，而不是应用程序类加载器来加载。
接下来分析，如何打破双亲委派机制？双亲委派机制是在那里实现的呢？
双亲委派机制是在ClassLoader类的loadClass()中实现的，如果我们不想使用系统自带的双亲委派模型，只需要重新实现ClassLoader的loadClass()方法即可，下面是ClassLoader中定义的loadClass()方法，里面实现了双亲委派机制
![img](images/1187916-20200630063024959-377229775.png)
下面给DefinedClassLoaderTest.java增加一个loadClass方法, 拷贝上面的代码即可. 删除掉中间实现双亲委派机制的部分
![img](images/1187916-20200630064955278-658375195.png)
这里需要注意的是，com.lxl.jvm是自定义的雷暴，只有我们自己定义的类才可以从这里加载，如果是系统类，依然使用双亲委派机制来加载，下面来看看运行结果
```bash
# 调用user1的sout方法
com.lxl.jvm.DefinedClassLoaderTest
```
现在User1方法确实是由自定义类加载器加载的了，源码如下
```java
package com.lxl.jvm;
import java.io.FileInputStream;
import java.lang.reflect.Method;
/**
 * 自定义的类加载器
 */
public class DefinedClassLoaderTest extends ClassLoader{
    private String classPath;
    public DefinedClassLoaderTest(String classPath) {
        this.classPath = classPath;
    }
    /**
     * 重写findClass方法
     *
     * 如果不会写, 可以参考URLClassLoader中是如何加载AppClassLoader和ExtClassLoader的
     * @param name
     * @return
     * @throws ClassNotFoundException
     */
    @Override
    protected Class findClass(String name) throws ClassNotFoundException {
        try {
            byte[] data = loadBytes(name);
            return defineClass(name, data, 0, data.length);
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }
    private byte[] loadBytes(String name) throws Exception {
        // 我们需要读取类的路径
        String path = name.replace('.', '/').concat(".class");
        //String path = "";
        // 去路径下查找这个类
        FileInputStream fileInputStream = new FileInputStream(classPath + "/"  + path);
        int len = fileInputStream.available();
        byte[] data = new byte[len];
        fileInputStream.read(data);
        fileInputStream.close();
        return data;
    }
    protected Class loadClass(String name, boolean resolve)
            throws ClassNotFoundException
    {
        synchronized (getClassLoadingLock(name)) {
            // First, check if the class has already been loaded
            Class c = findLoadedClass(name);
            if (c == null) {
                /**
                 * 直接执行findClass()...什么意思呢? 首先会使用自定义类加载器加载类, 不在向上委托, 直接由
                 * 自己执行
                 *
                 * jvm自带的类还是需要由引导类加载器自动加载
                 */
                if (!name.startsWith("com.lxl.jvm")) {
                    c = this.getParent().loadClass(name);
                } else {
                    c = findClass(name);
                }
            }
            if (resolve) {
                resolveClass(c);
            }
            return c;
        }
    }
    public static void main(String[] args) throws Exception {
        DefinedClassLoaderTest classLoader = new DefinedClassLoaderTest("/Users/luoxiaoli");
        Class clazz = classLoader.loadClass("com.lxl.jvm.User1");
        Object obj = clazz.newInstance();
        Method sout = clazz.getDeclaredMethod("sout", null);
        sout.invoke(obj, null);
        System.out.println(clazz.getClassLoader().getClass().getName());
    }
}
```
## 参考
-  [打破双亲委派机制](https://www.cnblogs.com/ITPower/p/13211490.html)
-  [tomcat是如何打破双亲委派机制的?](https://www.cnblogs.com/ITPower/p/13217145.html)
- 
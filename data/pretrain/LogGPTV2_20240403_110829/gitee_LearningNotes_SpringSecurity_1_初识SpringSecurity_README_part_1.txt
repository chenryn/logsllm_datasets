# 初识SpringSecurity
## 参考
来源于黑马程序员： [手把手教你精通新版SpringSecurity](https://www.bilibili.com/video/BV1EE411u7YV?p=1)
## 权限管理概念
权限管理，一般指根据系统设置的安全规则或者安全策略，用户可以访问而且只能访问自己被授权的资源。权限管
理几乎出现在任何系统里面，前提是需要有用户和密码认证的系统。
> 在权限管理的概念中，有两个非常重要的名词：
>
> - 认证：通过用户名和密码成功登陆系统后，让系统得到当前用户的角色身份。
> - 授权：系统根据当前用户的角色，给其授予对应可以操作的权限资源。
## 完成权限管理需要三个对象
- 用户：主要包含用户名，密码和当前用户的角色信息，可实现认证操作。
- 角色：主要包含角色名称，角色描述和当前角色拥有的权限信息，可实现授权操作。
- 权限：权限也可以称为菜单，主要包含当前权限名称，url地址等信息，可实现动态展示菜单。
> 注：这三个对象中，用户与角色是多对多的关系，角色与权限是多对多的关系，用户与权限没有直接关系，
> 二者是通过角色来建立关联关系的。
## 初识SpringSecurity
Spring Security是spring采用AOP思想，基于servlet过滤器实现的安全框架。它提供了完善的认证机制和方法级的
授权功能。是一款非常优秀的权限管理框架。
### 创建SpringSecurity
Spring Security主要jar包功能介绍
- spring-security-core.jar：核心包，任何Spring Security功能都需要此包。
- spring-security-web.jar：web工程必备，包含过滤器和相关的Web安全基础结构代码。
- spring-security-config.jar：用于解析xml配置文件，用到Spring Security的xml配置文件的就要用到此包。
- spring-security-taglibs.jar：Spring Security提供的动态标签库，jsp页面可以用。
导入pom依赖
```pom
    org.springframework.security
    spring-security-taglibs
    5.1.5.RELEASE
    org.springframework.security
    spring-security-config
    5.1.5.RELEASE
```
最终依赖树
![image-20200919183927385](images/image-20200919183927385.png)
### 配置web.xml
```xml
Archetype Created Web Application
        springSecurityFilterChain
        org.springframework.web.filter.DelegatingFilterProxy
        springSecurityFilterChain
        /*
```
### 配置SpringSecurity.xml
```xml
```
## SpringSecurity常用过滤器介绍
过滤器是一种典型的AOP思想
### SecurityContextPersistenceFilter
首当其冲的一个过滤器，作用之重要，自不必多言。
SecurityContextPersistenceFilter主要是使用SecurityContextRepository在session中保存或更新一SecurityContext，并将SecurityContext给以后的过滤器使用，来为后续filter建立所需的上下文。SecurityContext中存储了当前用户的认证以及权限信息。
### WebAsyncManagerIntegrationFilter
此过滤器用于集成SecurityContext到Spring异步执行机制中的WebAsyncManager
### HeaderWriterFilter
向请求的Header中添加相应的信息,可在http标签内部使用security:headers来控制（仅限于JSP页面）
### CsrfFilter
csrf又称跨域请求伪造，SpringSecurity会对所有post请求验证是否包含系统生成的csrf的token信息，
如果不包含，则报错。起到防止csrf攻击的效果。
### LogoutFilter
匹配URL为/logout的请求，实现用户退出,清除认证信息。
### UsernamePasswordAuthenticationFilter
认证操作全靠这个过滤器，默认匹配URL为/login且必须为POST请求。
### DefaultLoginPageGeneratingFilter
如果没有在配置文件中指定认证页面，则由该过滤器生成一个默认认证页面。
### DefaultLogoutPageGeneratingFilter
由此过滤器可以生产一个默认的退出登录页面
### BasicAuthenticationFilter
此过滤器会自动解析HTTP请求中头部名字为Authentication，且以Basic开头的头信息。
### RequestCacheAwareFilter
通过HttpSessionRequestCache内部维护了一个RequestCache，用于缓存HttpServletRequest
### SecurityContextHolderAwareRequestFilter
针对ServletRequest进行了一次包装，使得request具有更加丰富的API
### AnonymousAuthenticationFilter
当SecurityContextHolder中认证信息为空,则会创建一个匿名用户存入到SecurityContextHolder中。
spring security为了兼容未登录的访问，也走了一套认证流程，只不过是一个匿名的身份。
> 当用户以游客身份登录的时候，也就是可以通过设置某些接口可以匿名访问
### SessionManagementFilter
SecurityContextRepository限制同一用户开启多个会话的数量
### ExceptionTranslationFilter
异常转换过滤器位于整个springSecurityFilterChain的后方，用来转换整个链路中出现的异常
### FilterSecurityInterceptor
获取所配置资源访问的授权信息，根据SecurityContextHolder中存储的用户信息来决定其是否有权
限
> 该过滤器限制哪些资源可以访问，哪些不能够访问
## SpringSecurity过滤器链加载原理
通过前面十五个过滤器功能的介绍，对于SpringSecurity简单入门中的疑惑是不是在心中已经有了答案了呀？
但新的问题来了！我们并没有在web.xml中配置这些过滤器啊？它们都是怎么被加载出来的？
### DelegatingFilterProxy
我们在web.xml中配置了一个名称为springSecurityFilterChain的过滤器DelegatingFilterProxy，接下我直接对
DelegatingFilterProxy源码里重要代码进行说明，其中删减掉了一些不重要的代码，大家注意我写的注释就行了！
![image-20200919191221857](images/image-20200919191221857.png)
![image-20200919191241102](images/image-20200919191241102.png)
![image-20200919191302644](images/image-20200919191302644.png)
第二步debug结果如下
![image-20200919191331949](images/image-20200919191331949.png)
由此可知，DelegatingFilterProxy通过springSecurityFilterChain这个名称，得到了一个FilterChainProxy过滤器，最终在第三步执行了这个过滤器。
### FilterChainProxy
注意代码注释！注意代码注释！注意代码注释！
![image-20200919191609357](images/image-20200919191609357.png)
![image-20200919191701128](images/image-20200919191701128.png)
![image-20200919191724782](images/image-20200919191724782.png)
第二步debug结果如下图所示，惊不惊喜？十五个过滤器都在这里了！
![image-20200919191746095](images/image-20200919191746095.png)
再看第三步，怀疑这么久！原来这些过滤器还真是都被封装进SecurityFilterChain中了。
### SecurityFilterChain
最后看SecurityFilterChain，这是个接口，实现类也只有一个，这才是web.xml中配置的过滤器链对象！
![image-20200919191830091](images/image-20200919191830091.png)
![image-20200919191841552](images/image-20200919191841552.png)
### 总结
通过此章节，我们对SpringSecurity工作原理有了一定的认识。但理论千万条，功能第一条，探寻底层，是
为了更好的使用框架。
那么，言归正传！到底如何使用自己的页面来实现SpringSecurity的认证操作呢？要完成此功能，首先要有一套
自己的页面！
## SpringSecurity使用自定义认证页面
在SpringSecurity主配置文件中指定认证页面配置信息
![image-20200919191951927](images/image-20200919191951927.png)
修改认证页面的请求地址
![image-20200919192105365](images/image-20200919192105365.png)
再次启动项目后就可以看到自定义的酷炫认证页面了！
![image-20200919192142213](images/image-20200919192142213.png)
然后你开开心心的输入了用户名user，密码user，就出现了如下的界面：
![image-20200919192203613](images/image-20200919192203613.png)
403什么异常？这是SpringSecurity中的权限不足！这个异常怎么来的？还记得上面SpringSecurity内置认证页面源码中的那个_csrf隐藏input吗？问题就在这了！
完整的spring-security配置如下
```xml
<beans xmlns="http://www.springframework.org/schema/beans"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
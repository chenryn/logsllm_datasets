        xmlns:context="http://www.springframework.org/schema/context"
        xmlns:aop="http://www.springframework.org/schema/aop"
        xmlns:tx="http://www.springframework.org/schema/tx"
        xmlns:mvc="http://www.springframework.org/schema/mvc"
        xmlns:security="http://www.springframework.org/schema/security"
        xsi:schemaLocation="http://www.springframework.org/schema/beans
			    http://www.springframework.org/schema/beans/spring-beans.xsd
			    http://www.springframework.org/schema/context
			    http://www.springframework.org/schema/context/spring-context.xsd
			    http://www.springframework.org/schema/aop
			    http://www.springframework.org/schema/aop/spring-aop.xsd
			    http://www.springframework.org/schema/tx
			    http://www.springframework.org/schema/tx/spring-tx.xsd
			    http://www.springframework.org/schema/mvc
			    http://www.springframework.org/schema/mvc/spring-mvc.xsd
                http://www.springframework.org/schema/security
			    http://www.springframework.org/schema/security/spring-security.xsd">
        -->
```
## SpringSecurity的csrf防护机制
CSRF（Cross-site request forgery）跨站请求伪造，是一种难以防范的网络攻击方式。
SpringSecurity中CsrfFilter过滤器说明
![image-20200919193139125](images/image-20200919193139125.png)
![image-20200919193203700](images/image-20200919193203700.png)
通过源码分析，我们明白了，自己的认证页面，请求方式为POST，但却没有携带token，所以才出现了403权限不
足的异常。那么如何处理这个问题呢？
方式一：直接禁用csrf，不推荐。
方式二：在认证页面携带token请求。
### 禁用csrf防护机制
在SpringSecurity主配置文件中添加禁用crsf防护的配置。
![image-20200919194217293](images/image-20200919194217293.png)
### 在认证页面携带token请求
![image-20200919194236585](images/image-20200919194236585.png)
注：HttpSessionCsrfTokenRepository对象负责生成token并放入session域中。
## SpringSecurity使用数据库数据完成认证
### 认证流程
先看主要负责认证的过滤器UsernamePasswordAuthenticationFilter，有删减，注意注释。
![image-20200919194541154](images/image-20200919194541154.png)
![image-20200919194554290](images/image-20200919194554290.png)
上面的过滤器的意思就是，我们发送的登录请求，请求地址需要是 /login，请求方法 post，然后用户名 username，密码为 password
### AuthenticationManager
由上面源码得知，真正认证操作在AuthenticationManager里面！然后看AuthenticationManager的实现类ProviderManager：
![image-20200919195156738](images/image-20200919195156738.png)
![image-20200919195209419](images/image-20200919195209419.png)
### AbstractUserDetailsAuthenticationProvider
咱们继续再找到AuthenticationProvider的实现类AbstractUserDetailsAuthenticationProvider
![image-20200919195243996](images/image-20200919195243996.png)
### AbstractUserDetailsAuthenticationProvider中authenticate返回值
按理说到此已经知道自定义认证方法的怎么写了，但咱们把返回的流程也大概走一遍，上面不是说到返回了一个
UserDetails对象对象吗？跟着它，就又回到了AbstractUserDetailsAuthenticationProvider对象中authenticate方法的最后一行了。
![image-20200919195340553](images/image-20200919195340553.png)
### UsernamePasswordAuthenticationToken
来到UsernamePasswordAuthenticationToken对象发现里面有两个构造方法
![image-20200919195400048](images/image-20200919195400048.png)
![image-20200919195407334](images/image-20200919195407334.png)
### AbstractAuthenticationToken
再点进去super(authorities)看看：
![image-20200919195433849](images/image-20200919195433849.png)
由此，咱们需要牢记自定义认证业务逻辑返回的UserDetails对象中一定要放置权限信息啊！
现在可以结束源码分析了吧？先不要着急！
咱们回到最初的地方UsernamePasswordAuthenticationFilter，你看好看了，这可是个过滤器，咱们分析这么
久，都没提到doFilter方法，你不觉得心里不踏实？
可是这里面也没有doFilter呀？那就从父类找！
### AbstractAuthenticationProcessingFilter
点开AbstractAuthenticationProcessingFilter，删掉不必要的代码！
![image-20200919195547370](images/image-20200919195547370.png)
![image-20200919195601300](images/image-20200919195601300.png)
可见AbstractAuthenticationProcessingFilter这个过滤器对于认证成功与否，做了两个分支，成功执行
successfulAuthentication，失败执行unsuccessfulAuthentication。
在successfulAuthentication内部，将认证信息存储到了SecurityContext中。并调用了loginSuccess方法，这就是
常见的“记住我”功能！此功能具体应用，咱们后续再研究！
## 初步实现认证功能
让我们自己的UserService接口继承UserDetailsService，毕竟SpringSecurity是只认UserDetailsService的：
### 创建UserDetailsService
```java
public interface UserService extends UserDetailsService {
    public void save(SysUser user);
    public List findAll();
    public Map toAddRolePage(Integer id);
    public void addRoleToUser(Integer userId, Integer[] ids);
}
```
### 编写loadUserByUsername业务
```java
@Override
public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
    SysUser sysUser = userDao.findByName(username);
    if(sysUser==null){
        //若用户名不对，直接返回null，表示认证失败。
        return null;
    }
    List authorities = new ArrayList<>();
    List roles = sysUser.getRoles();
    for (SysRole role : roles) {
    	authorities.add(new SimpleGrantedAuthority(role.getRoleName()));
    }
    //最终需要返回一个SpringSecurity的UserDetails对象，{noop}表示不加密认证。
    return new User(sysUser.getUsername(), "{noop}"+sysUser.getPassword(), authorities);
}
```
### 在SpringSecurity主配置文件中指定认证使用的业务对象
```xml
```
## 加密认证
### 在IOC容器中提供加密对象
```xml
```
### 修改认证方法
去掉{noop}，该方法可以让我们的密码不加密
```java
@Override
public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
    SysUser sysUser = userDao.findByName(username);
    if(sysUser==null){
        //若用户名不对，直接返回null，表示认证失败。
        return null;
    }
    List authorities = new ArrayList<>();
    List roles = sysUser.getRoles();
    for (SysRole role : roles) {
    	authorities.add(new SimpleGrantedAuthority(role.getRoleName()));
    }
    //最终需要返回一个SpringSecurity的UserDetails对象，{noop}表示不加密认证。
    return new User(sysUser.getUsername(), sysUser.getPassword(), authorities);
}
```
### 修改添加用户的操作
```java
@Service
@Transactional
public class UserServiceImpl implements UserService {
    @Autowired
    private UserDao userDao;
    @Autowired
    private RoleService roleService;
    @Autowired
    private BCryptPasswordEncoder passwordEncoder;
    @Override
    public void save(SysUser user) {
        //对密码进行加密，然后再入库
        user.setPassword(passwordEncoder.encode(user.getPassword()));
        userDao.save(user);
	}
}
```
### 手动将数据库中用户密码改为加密后的密文
![image-20200919202157273](images/image-20200919202157273.png)
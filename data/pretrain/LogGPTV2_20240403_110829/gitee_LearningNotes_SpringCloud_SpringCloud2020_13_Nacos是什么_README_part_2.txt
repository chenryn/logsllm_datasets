    name: nacos-config-client
  cloud:
    nacos:
      discovery:
        server-addr: localhost:8848 # 注册中心
      config:
        server-addr: localhost:8848 # 配置中心
        file-extension: yml # 这里指定的文件格式需要和nacos上新建的配置文件后缀相同，否则读不到
        group: TEST_GROUP
        namespace: 1bdf1418-3ed4-442c-97c1-f525b6a85b34
#  ${spring.application.name}-${spring.profile.active}.${spring.cloud.nacos.config.file-extension}
```
#### 主启动类
```
@SpringBootApplication
@EnableDiscoveryClient
public class NacosConfigClientMain3377 {
    public static void main(String[] args) {
        SpringApplication.run(NacosConfigClientMain3377.class, args);
    }
}
```
#### 业务类
```
@RestController
@RefreshScope // 支持nacos的动态刷新
public class ConfigClientController {
    @Value("${config.info}")
    private String configInfo;
    @GetMapping("/config/info")
    public String getConfigInfo(){
        return configInfo;
    }
}
```
通过SpringCloud原生注解 `@RefreshScope` 实现配置自动刷新
#### 在Nacos中添加配置信息
##### Nacos中匹配规则
Nacos中的dataid的组成格式及与SpringBoot配置文件中的匹配规则
```
${spring.application.name}-${spring.profile.active}.${spring.cloud.nacos.config.file-extension}
```
这样，就对应我们Nacos中的这样一个配置
```
nacos-config-client-dev.yml
```
配置说明
![image-20200415201834108](images/image-20200415201834108.png)
我们在Nacos中添加配置
![image-20200415201605809](images/image-20200415201605809.png)
![image-20200415201532098](images/image-20200415201532098.png)
这里需要注意的是，在`config:` 的后面必须加上一个空格
#### 测试
启动前需要在nacos客户端-配置管理下有对应的yml配置文件，然后运行cloud-config-nacos-client:3377的主启动类，调用接口查看配置信息。
启动的时候出现问题
![image-20200415202334437](images/image-20200415202334437.png)
这是因为无法读取配置所引起的，解决方案就是我们的文件名不能用 .yml 而应该是 .yaml
![image-20200415202411451](images/image-20200415202411451.png)
我们需要删除重新建立。
#### 自带动态刷新
修改Nacos中的yaml配置文件，再次查看配置的接口，就会发现配置已经刷新了
### Nacos作为配置中心 - 分类配置
从上面的配置中心 + 动态刷新 ， 就相当于 有了 SpringCloud Config + Spring Cloud Bus的功能
作为后起之秀的Nacos，还具备分类配置的功能
#### 问题
用于解决多环境多项目管理
在实际开发中，通常一个系统会准备
- dev开发环境
- test测试环境
- prod生产环境
如何保证指定环境启动时，服务能正确读取到Nacos上相应环境的配置文件呢？
同时，一个大型分布式微服务系统会有很多微服务子项目，每个微服务子项目又都会有相应的开发环境，测试环境，预发环境，正式环境，那怎么对这些微服务配置进行管理呢？
#### Nacos图形化界面
配置管理:
![image-20200415203545643](images/image-20200415203545643.png)
命名空间：
![image-20200415203611077](images/image-20200415203611077.png)
#### Namespace + Group + Data ID 三者关系
这种分类的设计思想，就类似于java里面的package名 和 类名，最外层的namespace是可以用于区分部署环境的，Group 和 DataID逻辑上区分两个目标对象
![image-20200415203750816](images/image-20200415203750816.png)
默认情况：
Namespace=public，Group=DEFAULT_GROUP，默认Cluster是DEFAULT
Nacos默认的命名空间是public，Namespace主要用来实现隔离
比如说我们现在有三个环境：开发，测试，生产环境，我们就可以建立三个Namespace，不同的Namespace之间是隔离的。
Group默认是DEFAULT_GROUP，Group可以把不同微服务划分到同一个分组里面去
Service就是微服务，一个Service可以包含多个Cluster（集群），Nacos默认Cluster是DEFAULT，Cluster是对指定微服务的一个虚拟划分。比如说为了容灾，将Service微服务分别部署在了杭州机房，这时就可以给杭州机房的Service微服务起一个集群名称（HZ），给广州机房的Service微服务起一个集群名称，还可以尽量让同一个机房的微服务相互调用，以提升性能，最后Instance，就是微服务的实例。
#### 三种方案加载配置
##### DataID方案
- 指定spring.profile.active 和 配置文件的DataID来使不同环境下读取不同的配置
- 默认空间 + 默认分组 + 新建dev 和 test两个DataID
##### Group方案
在创建的时候，添加分组信息
![image-20200415211944859](images/image-20200415211944859.png)
然后就可以添加分组
```
server:
  port: 3377
spring:
  application:
    name: nacos-config-client
  cloud:
    nacos:
      discovery:
        server-addr: localhost:8848 # 注册中心
      config:
        server-addr: localhost:8848 # 配置中心
        file-extension: yaml # 这里指定的文件格式需要和nacos上新建的配置文件后缀相同，否则读不到
        group: TEST_GROUP
```
##### Namspace方案
首先我们需要新建一个命名空间
![image-20200415212414302](images/image-20200415212414302.png)
新建完成后，能够看到有命名空间id
![image-20200415212455416](images/image-20200415212455416.png)
创建完成后，我们会发现，多出了几个命名空间切换
![image-20200415212550443](images/image-20200415212550443.png)
同时，我们到服务列表，发现也多了命名空间的切换
![image-20200415212638006](images/image-20200415212638006.png)
下面我们就可以通过引入namespaceI，来创建到指定的命名空间下
```
server:
  port: 3377
spring:
  application:
    name: nacos-config-client
  cloud:
    nacos:
      discovery:
        server-addr: localhost:8848 # 注册中心
      config:
        server-addr: localhost:8848 # 配置中心
        file-extension: yaml # 这里指定的文件格式需要和nacos上新建的配置文件后缀相同，否则读不到
        group: DEV_GROUP
        namespace: bbf379fb-f979-4eab-8947-2f38cfae6c0c
```
最后通过 namespace + group + DataID 形成三级分类
## Nacos集群和持久化配置
### 官网说明
用于部署生产中的集群模式
![image-20200415214554761](images/image-20200415214554761.png)
默认Nacos使用嵌入数据库实现数据的存储，所以，如果启动多个默认配置下的Nacos节点，数据存储是存在一致性问题的。为了解决这个问题，Nacos采用了集中式存储的方式来支持集群化部署，目前只支持MySQL的存储。
Nacos支持三种部署模式
- 单机模式：用于测试和单机使用
- 集群模式：用于生产环境，确保高可用
- 多集群模式：用于多数据中心场景
### 单机模式支持mysql
在0.7版本之前，在单机模式下nacos使用嵌入式数据库实现数据的存储，不方便观察数据存储的基本情况。0.7版本增加了支持mysql数据源能力，具体的操作流程：
- 安装数据库，版本要求：5.6.5 + 
- 初始化数据库，数据库初始化文件：nacos-mysql.sql
- 修改conf/application.properties文件，增加mysql数据源配置，目前仅支持mysql，添加mysql数据源的url，用户名和密码
![image-20200415215209988](images/image-20200415215209988.png)
再次以单机模式启动nacos，nacos所有写嵌入式数据库的数据都写到了mysql中。
### Nacos持久化配置解释
Nacos默认自带的是嵌入式数据库derby
因此我们需要完成derby到mysql切换配置步骤
- 在nacos\conf目录下，找到SQL脚本
![image-20200415231605632](images/image-20200415231605632.png)
然后执行SQL脚本，同时修改application.properties目录
[官网地址](https://nacos.io/zh-cn/docs/deployment.html)
```
spring.datasource.platform=mysql
db.num=1
db.url.0=jdbc:mysql://127.0.0.1:3306/nacos_devtest?characterEncoding=utf8&connectTimeout=1000&socketTimeout=3000&autoReconnect=true
db.user=root
db.password=root
```
修改完成后，启动nacos，可以看到是一个全新的空记录页面，以前是记录进derby
### Linux版Nacos + Mysql生产环境配置
#### 配置
预计需要：1个Nginx + 3个nacos注册中心 + 1个mysql
所有的请求过来，首先先打到nginx上
#### Nacos下载Linux版本
在nacos github下载：`https://github.com/alibaba/nacos/releases`
选择Linux版本下载
![image-20200415232903575](images/image-20200415232903575.png)
#### 集群配置
如果是一个nacos：启动 8848即可
如果是多个nacos：3333,4444,5555
那么就需要修改startup.sh里面的，传入端口号
步骤：
- Linux服务器上mysql数据库配置
- application.properties配置
- Linux服务器上nacos的集群配置cluster.conf
  - 梳理出3台nacos集群的不同服务端口号
  - 复制出cluster.conf（备份）
  - 修改
![image-20200415233933223](images/image-20200415233933223.png)
- 编辑Nacos的启动脚本startup.sh，使它能够接受不同的启动端口
  - /nacos/bin 目录下有startup.sh
  - 平时单机版的启动，直接./startup.sh
  - 但是集群启动时，我们希望可以类似其它软件的shell命令，传递不同的端口号启动不同的nacos实例，命令：./startup.sh -p 3333表示启动端口号为3333的nacos服务器实例，和上一步的cluster.conf配置一样。
  修改启动脚本，添加P，这样能够明确nacos启动的什么脚本
![image-20200415235915453](images/image-20200415235915453.png)
![image-20200415235932505](images/image-20200415235932505.png)
修改完成后，就能够使用下列命令启动集群了
```
./startup.sh -p 3333
./startup.sh -p 4444
./startup.sh -p 5555
```
- Nginx的配置，由它作为负载均衡器
  - 修改nginx的配置文件
![image-20200416000415104](images/image-20200416000415104.png)
作为负载均衡分流，同时upstream 支持weight
通过nginx访问nacos节点：`http://192.168.111.144:1111/nacos/#/login`
微服务注册进集群中
```
server:
  port: 9002
spring:
  application:
    name: nacos-payment-provider
  cloud:
    nacos:
      discovery:
        server-addr: 192.168.111.144:1111 # 换成nginx的1111端口，做负债均衡
management:
  endpoints:
    web:
      exposure:
        include: '*'
```
#### 总结
Nginx + 3个Nacos + mysql的集群化配置
![image-20200416001145081](images/image-20200416001145081.png)
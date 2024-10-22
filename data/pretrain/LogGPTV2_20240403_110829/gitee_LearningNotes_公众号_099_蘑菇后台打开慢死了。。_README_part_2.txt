下面，让我们一起来看看如何给自己的网站，集成 **Druid** 连接池，用来检测网站 **SQL** 性能吧~
## SpringBoot如何集成Druid？
首先，需要添加依赖，在 **pom.xml** 文件中加入
```pom
com.alibaba
druid
1.1.8
```
然后在 **application.yml** 中，添加配置
```yml
#spring
spring:
  # DATABASE CONFIG
  datasource:
    username: root
    password: root
    url: jdbc:mysql://localhost:3306/mogu_blog_business?useUnicode=true&allowMultiQueries=true&characterEncoding=utf-8&zeroDateTimeBehavior=convertToNull&transformedBitIsBoolean=true&useSSL=false&serverTimezone=Asia/Shanghai
    driver-class-name: com.mysql.cj.jdbc.Driver
    type: com.alibaba.druid.pool.DruidDataSource
    # 初始化大小，最小，最大
    initialSize: 20
    minIdle: 5
    maxActive: 200
    #连接等待超时时间
    maxWait: 60000
    #配置隔多久进行一次检测(检测可以关闭的空闲连接)
    timeBetweenEvictionRunsMillis: 60000
    #配置连接在池中的最小生存时间
    minEvictableIdleTimeMillis: 300000
    validationQuery: SELECT 1 FROM DUAL
    dbcp:
      remove-abandoned: true
      #泄露的连接可以被删除的超时时间（秒），该值应设置为应用程序查询可能执行的最长时间
      remove-abandoned-timeout: 180
    testWhileIdle: true
    testOnBorrow: false
    testOnReturn: false
    poolPreparedStatements: true
    #配置监控统计拦截的filters，去掉后监控界面sql无法统计，'wall'用于防火墙
    filters: stat,wall,log4j
    maxPoolPreparedStatementPerConnectionSize: 20
    useGlobalDataSourceStat: true
    connectionProperties: druid.stat.mergeSql=true;druid.stat.slowSqlMillis=500
```
在创建配置 **DruidConfig.java**，创建 **DataSource** 数据源，同时配置监控页面的登录账号和密码
```java
package com.moxi.mogublog.admin.config;
import com.alibaba.druid.filter.Filter;
import com.alibaba.druid.pool.DruidDataSource;
import com.alibaba.druid.support.http.StatViewServlet;
import com.alibaba.druid.support.http.WebStatFilter;
import com.alibaba.druid.wall.WallConfig;
import com.alibaba.druid.wall.WallFilter;
import com.moxi.mougblog.base.global.Constants;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.web.servlet.FilterRegistrationBean;
import org.springframework.boot.web.servlet.ServletRegistrationBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import javax.sql.DataSource;
import java.sql.SQLException;
import java.util.*;
/**
 * DruidConfig
 *
 * @author Administrator
 * @Date 2020年1月9日19:06:23
 */
@Slf4j
@Configuration
public class DruidConfig {
    @Value("${spring.datasource.url}")
    private String dbUrl;
    @Value("${spring.datasource.username}")
    private String username;
    @Value("${spring.datasource.password}")
    private String password;
    @Value("${spring.datasource.driver-class-name}")
    private String driverClassName;
    @Value("${spring.datasource.initialSize}")
    private int initialSize;
    @Value("${spring.datasource.minIdle}")
    private int minIdle;
    @Value("${spring.datasource.maxActive}")
    private int maxActive;
    @Value("${spring.datasource.maxWait}")
    private int maxWait;
    @Value("${spring.datasource.timeBetweenEvictionRunsMillis}")
    private int timeBetweenEvictionRunsMillis;
    @Value("${spring.datasource.minEvictableIdleTimeMillis}")
    private int minEvictableIdleTimeMillis;
    @Value("${spring.datasource.validationQuery}")
    private String validationQuery;
    @Value("${spring.datasource.testWhileIdle}")
    private boolean testWhileIdle;
    @Value("${spring.datasource.testOnBorrow}")
    private boolean testOnBorrow;
    @Value("${spring.datasource.testOnReturn}")
    private boolean testOnReturn;
    @Value("${spring.datasource.poolPreparedStatements}")
    private boolean poolPreparedStatements;
    @Value("${spring.datasource.maxPoolPreparedStatementPerConnectionSize}")
    private int maxPoolPreparedStatementPerConnectionSize;
    @Value("${spring.datasource.filters}")
    private String filters;
    @Value("{spring.datasource.connectionProperties}")
    private String connectionProperties;
    /**
     * 声明其为Bean实例
     * 在同样的DataSource中，首先使用被标注的DataSource
     *
     * @return
     */
    @Bean
    @Primary
    public DataSource dataSource() {
        DruidDataSource datasource = new DruidDataSource();
        datasource.setUrl(this.dbUrl);
        datasource.setUsername(username);
        datasource.setPassword(password);
        datasource.setDriverClassName(driverClassName);
        // configuration
        datasource.setInitialSize(initialSize);
        datasource.setMinIdle(minIdle);
        datasource.setMaxActive(maxActive);
        datasource.setMaxWait(maxWait);
        datasource.setTimeBetweenEvictionRunsMillis(timeBetweenEvictionRunsMillis);
        datasource.setMinEvictableIdleTimeMillis(minEvictableIdleTimeMillis);
        datasource.setValidationQuery(validationQuery);
        datasource.setTestWhileIdle(testWhileIdle);
        datasource.setTestOnBorrow(testOnBorrow);
        datasource.setTestOnReturn(testOnReturn);
        datasource.setPoolPreparedStatements(poolPreparedStatements);
        datasource.setMaxPoolPreparedStatementPerConnectionSize(maxPoolPreparedStatementPerConnectionSize);
        try {
            /**
             * 加入过滤
             */
            List filterList = new ArrayList<>();
            filterList.add(wallFilter());
            datasource.setProxyFilters(filterList);
            datasource.setFilters(filters);
        } catch (SQLException e) {
            log.error("druid configuration initialization filter");
        }
        datasource.setConnectionProperties(connectionProperties);
        return datasource;
    }
    /**
     * 配置一个管理后台的Servlet
     */
    @Bean
    public ServletRegistrationBean statViewServlet() {
        ServletRegistrationBean bean = new ServletRegistrationBean(new StatViewServlet(), "/druid/*");
        Map initParams = new HashMap<>(Constants.NUM_TWO);
        initParams.put("loginUsername", "admin");
        initParams.put("loginPassword", " ");
        //默认就是允许所有访问
        initParams.put("allow", "");
        bean.setInitParameters(initParams);
        return bean;
    }
    /**
     * 配置一个web监控的filter
     *
     * @return
     */
    @Bean
    public FilterRegistrationBean webStatFilter() {
        FilterRegistrationBean bean = new FilterRegistrationBean();
        bean.setFilter(new WebStatFilter());
        Map initParams = new HashMap<>(Constants.NUM_ONE);
        initParams.put("exclusions", "*.vue,*.js,*.gif,*.jpg,*.bmp,*.png,*.css,*.ico,/druid/*");
        bean.setInitParameters(initParams);
        bean.setUrlPatterns(Arrays.asList("/*"));
        return bean;
    }
    @Bean
    public WallFilter wallFilter() {
        WallFilter wallFilter = new WallFilter();
        WallConfig config = new WallConfig();
        //允许一次执行多条语句
        config.setMultiStatementAllow(true);
        //允许非基本语句的其他语句
        config.setNoneBaseStatementAllow(true);
        wallFilter.setConfig(config);
        return wallFilter;
    }
}
```
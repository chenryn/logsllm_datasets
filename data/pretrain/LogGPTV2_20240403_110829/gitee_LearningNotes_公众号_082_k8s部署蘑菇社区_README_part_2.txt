### 添加helm chart仓库
```bash
helm repo add mogu-chart http://47.106.230.203:9090/
helm repo update
```
### 部署sentinel
编写配置文件`sentinel.yaml`
```bash
tee sentinel.yaml<<-EOF
env:
  open:
    # 本实例服务端口
    SERVER_PORT: 8080
    # 是否启用nacos持久化配置
    SENTINEL_DATASOURCE_NACOS_ENABLED: true
    # nacos地址
    SENTINEL_DATASOURCE_NACOS_SERVER_ADDR: 10.168.1.20:8848
    # nacos命名空间
    SENTINEL_DATASOURCE_NACOS_NAMESPACE: public
service:
  enabled: true
  type: ClusterIP
ingress:
  enabled: true
  host: sentinel.local.com
EOF
```
- 执行安装
```bash
helm upgrade --install sentinel mogu-chart/sentinel \
    -f sentinel.yaml \
    --create-namespace \
    --namespace base-system
```
## Zipkin部署
### 添加helm chart仓库
```bash
helm repo add mogu-chart http://47.106.230.203:9090/
helm repo update
```
### 部署zipkin
编写配置文件`zipkin.yaml`
```bash
tee zipkin.yaml<<-EOF
env:
  open:
    # 本实例服务端口
    SERVER_PORT: 9411
service:
  enabled: true
  type: ClusterIP
ingress:
  enabled: true
  host: zipkin.local.com
EOF
```
- 执行安装
```bash
helm upgrade --install zipkin mogu-chart/zipkin \
    -f zipkin.yaml \
    --create-namespace \
    --namespace base-system
```
### 导入数据库
- 在 **kubernetes** 目录下执行以下命令
```bash
kubectl -n base-system exec -it $(kubectl -n base-system get pod -l "mysql/release=mogu-mysql" -o jsonpath='{.items[0].metadata.name}') -- mysql -uroot -ppassword  < DB/mogu_blog.sql
kubectl -n base-system exec -it $(kubectl -n base-system get pod -l "mysql/release=mogu-mysql" -o jsonpath='{.items[0].metadata.name}') -- mysql -uroot -ppassword  < DB/mogu_picture.sql
```
## 部署mogu-picture
### 添加helm chart仓库
```bash
helm repo add mogu-chart http://47.106.230.203:9090/
helm repo update
```
### 部署mogu-admin
编写配置文件`mogu-admin.yaml`
```bash
tee mogu-admin.yaml<<-EOF
env:
  open:
    # 本实例运行的配置环境
    SPRING_PROFILES_ACTIVE: test
    # 本实例服务端口
    SERVER_PORT: 8601
    # 注册中心地址
    SPRING_CLOUD_NACOS_DISCOVERY_SERVER_ADDR: nacos-cs.base-system:8848
    # 注册中心命名空间
    SPRING_CLOUD_NACOS_DISCOVERY_NAMESPACE: test
    # 配置中心地址
    SPRING_CLOUD_NACOS_CONFIG_SERVER_ADDR: nacos-cs.base-system:8848
    # 配置文件格式
    SPRING_CLOUD_NACOS_CONFIG_FILE_EXTENSION: yaml
    #指定分组
    SPRING_CLOUD_NACOS_CONFIG_GROUP: test
    # 指定命名空间
    SPRING_CLOUD_NACOS_CONFIG_NAMESPACE: test
    # sentinel流控地址
    SPRING_CLOUD_SENTINEL_TRANSPORT_DASHBOARD: sentinel.base-system:8080
    # sentinel交互端口
    SPRING_CLOUD_SENTINEL_TRANSPORT_PORT: 8719
ingress:
  enabled: true
  host: admin.mogu.local.com
EOF
```
- 执行安装
```bash
helm upgrade --install mogu-admin mogu-chart/mogu-admin \
    -f mogu-admin.yaml \
    --create-namespace \
    --namespace mogu-system
```
## 部署mogu-sms
### 添加helm chart仓库
```bash
helm repo add mogu-chart http://47.106.230.203:9090/
helm repo update
```
### 部署mogu-sms
编写配置文件`mogu-sms.yaml`
```bash
tee mogu-sms.yaml<<-EOF
env:
  open:
    # 本实例运行的配置环境
    SPRING_PROFILES_ACTIVE: test
    # 本实例服务端口
    SERVER_PORT: 8604
    # 注册中心地址
    SPRING_CLOUD_NACOS_DISCOVERY_SERVER_ADDR: nacos-cs.base-system:8848
    # 注册中心命名空间
    SPRING_CLOUD_NACOS_DISCOVERY_NAMESPACE: test
    # 配置中心地址
    SPRING_CLOUD_NACOS_CONFIG_SERVER_ADDR: nacos-cs.base-system:8848
    # 配置文件格式
    SPRING_CLOUD_NACOS_CONFIG_FILE_EXTENSION: yaml
    #指定分组
    SPRING_CLOUD_NACOS_CONFIG_GROUP: test
    # 指定命名空间
    SPRING_CLOUD_NACOS_CONFIG_NAMESPACE: test
    # sentinel流控地址
    SPRING_CLOUD_SENTINEL_TRANSPORT_DASHBOARD: sentinel.base-system:8080
    # sentinel交互端口
    SPRING_CLOUD_SENTINEL_TRANSPORT_PORT: 8719
ingress:
  enabled: true
  host: sms.mogu.local.com
EOF
```
- 执行安装
```bash
helm upgrade --install mogu-sms mogu-chart/mogu-sms \
    -f mogu-sms.yaml \
    --create-namespace \
    --namespace mogu-system
```
## 部署mogu-admin
### 添加helm chart仓库
```bash
helm repo add mogu-chart http://47.106.230.203:9090/
helm repo update
```
### 部署mogu-admin
编写配置文件`mogu-admin.yaml`
```bash
tee mogu-admin.yaml<<-EOF
env:
  open:
    # 本实例运行的配置环境
    SPRING_PROFILES_ACTIVE: test
    # 本实例服务端口
    SERVER_PORT: 8601
    # 注册中心地址
    SPRING_CLOUD_NACOS_DISCOVERY_SERVER_ADDR: nacos-cs.base-system:8848
    # 注册中心命名空间
    SPRING_CLOUD_NACOS_DISCOVERY_NAMESPACE: test
    # 配置中心地址
    SPRING_CLOUD_NACOS_CONFIG_SERVER_ADDR: nacos-cs.base-system:8848
    # 配置文件格式
    SPRING_CLOUD_NACOS_CONFIG_FILE_EXTENSION: yaml
    #指定分组
    SPRING_CLOUD_NACOS_CONFIG_GROUP: test
    # 指定命名空间
    SPRING_CLOUD_NACOS_CONFIG_NAMESPACE: test
    # sentinel流控地址
    SPRING_CLOUD_SENTINEL_TRANSPORT_DASHBOARD: sentinel.base-system:8080
    # sentinel交互端口
    SPRING_CLOUD_SENTINEL_TRANSPORT_PORT: 8719
ingress:
  enabled: true
  host: admin.mogu.local.com
EOF
```
- 执行安装
```bash
helm upgrade --install mogu-admin mogu-chart/mogu-admin \
    -f mogu-admin.yaml \
    --create-namespace \
    --namespace mogu-system
```
## 部署mogu-web
### 添加helm chart仓库
```bash
helm repo add mogu-chart http://47.106.230.203:9090/
helm repo update
```
### 部署mogu-web
编写配置文件`mogu-web.yaml`
```bash
tee mogu-web.yaml<<-EOF
env:
  open:
    # 本实例运行的配置环境
    SPRING_PROFILES_ACTIVE: test
    # 本实例服务端口
    SERVER_PORT: 8603
    # 注册中心地址
    SPRING_CLOUD_NACOS_DISCOVERY_SERVER_ADDR: nacos-cs.base-system:8848
    # 注册中心命名空间
    SPRING_CLOUD_NACOS_DISCOVERY_NAMESPACE: test
    # 配置中心地址
    SPRING_CLOUD_NACOS_CONFIG_SERVER_ADDR: nacos-cs.base-system:8848
    # 配置文件格式
    SPRING_CLOUD_NACOS_CONFIG_FILE_EXTENSION: yaml
    #指定分组
    SPRING_CLOUD_NACOS_CONFIG_GROUP: test
    # 指定命名空间
    SPRING_CLOUD_NACOS_CONFIG_NAMESPACE: test
    # sentinel流控地址
    SPRING_CLOUD_SENTINEL_TRANSPORT_DASHBOARD: sentinel.base-system:8080
    # sentinel交互端口
    SPRING_CLOUD_SENTINEL_TRANSPORT_PORT: 8719
ingress:
  enabled: true
  host: web.mogu.local.com
EOF
```
- 执行安装
```bash
helm upgrade --install mogu-web mogu-chart/mogu-web \
    -f mogu-web.yaml \
    --create-namespace \
    --namespace mogu-system
```
## 部署vue-mogu-admin
首先，添加helm chart仓库
```bash
helm repo add mogu-chart http://47.106.230.203:9090/
helm repo update
```
安装蘑菇博客vue-mogu-admin
编写参数配置文件`vue-mogu-admin.yaml`
```yaml
tee vue-mogu-admin.yaml<<-EOF
image:
  pullPolicy: Always
env:
  open:
    WEB_API: http://web.mogu.local.com
    FILE_API: http://file.mogu.local.com
    RABBIT_MQ_ADMIN: http://rabbitmq.local.com
    SENTINEL_ADMIN: http://sentinel.local.com
    EUREKA_API: http://eureka.local.com
    Search_API: http://search.local.com
    ADMIN_API: http://admin.mogu.local.com
    NODE_ENV: production
    Zipkin_Admin: http://zipkin.local.com
    DRUID_ADMIN: http://admin.mogu.local.com/druid/login.html
    SPRING_BOOT_ADMIN: http://monitor.mogu.local.com/wallboard
    BLOG_WEB_URL: http://moguit.local.cn
    ELASTIC_SEARCH: http://es.local.com
    PICTURE_API: http://picture.mogu.local.com
    SOLR_API: http://solr.mogu.local.com/solr
ingress:
  enabled: true
  host: admin.moguit.local.cn
EOF
```
### 安装
```bash
helm upgrade --install vue-mogu-admin mogu-chart/vue-mogu-admin \
    -f vue-mogu-admin.yaml \
    --create-namespace \
    --namespace mogu-system
```
使用`——set key=value[key=value]`参数指定每个参数为`helm install`。
### 卸载chart
```bash
helm uninstall vue-mogu-admin -n mogu-system
```
### 验证部署
```bash
curl $(kubectl get svc vue-mogu-admin -o jsonpath="{.spec.clusterIP}" -n mogu-system)
```
如果能输出对应的页面，代表部署成功
## 部署vue-mogu-web
添加helm chart仓库
```bash
helm repo add mogu-chart http://47.106.230.203:9090/
helm repo update
```
安装蘑菇博客vue-mogu-web
编写参数配置文件`vue-mogu-web.yaml`
```yaml
tee vue-mogu-web.yaml<<-EOF
image:
  pullPolicy: Always
env:
  open:
    NODE_ENV: production
    VUE_MOGU_WEB: http://moguit.local.cn
    PICTURE_API: http://picture.mogu.local.com
    WEB_API: http://web.mogu.local.com
    ELASTICSEARCH: http://es.mogu.local.com
ingress:
  enabled: true
  host: moguit.local.cn
EOF
```
### 安装
```bash
helm upgrade --install vue-mogu-web mogu-chart/vue-mogu-web \
    -f vue-mogu-web.yaml \
    --create-namespace \
    --namespace mogu-system
```
使用`——set key=value[key=value]`参数指定每个参数为`helm install`。
### 卸载chart
```bash
helm uninstall vue-mogu-web -n mogu-system
```
### 验证部署
```bash
curl $(kubectl get svc vue-mogu-web -o jsonpath="{.spec.clusterIP}" -n mogu-system)
```
如果能输出对应的页面，代表部署成功
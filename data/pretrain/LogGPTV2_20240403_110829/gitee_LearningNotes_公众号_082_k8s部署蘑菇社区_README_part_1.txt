大家好，我是陌溪
今天整理了一下钉钉之前写的蘑菇博客 **K8S** 部署指南，用于后续蘑菇社区迁移到 **K8S** 中
前提条件：已安装 **k8s** 、**kubectl**、**helm3**
## NFS动态存储卷
### 创建 NFS 服务器
NFS 允许系统将其目录和文件共享给网络上的其他系统。通过 NFS，用户和应用程序可以访问远程系统上的文件，就象它们是本地文件一样。
### 安装nfs-utils
- 在集群每一个节点安装`nfs-utils`
```bash
sudo yum install -y nfs-utils
```
### 配置nfs-server
- 创建共享目录
```bash
mkdir -p /k8s/data
```
- 编辑`/etc/exports`文件添加需要共享目录，每个目录的设置独占一行，编写格式如下：
```bash
NFS共享目录路径 客户机IP段(参数1,参数2,...,参数n)
```
- 例如：
```bash
/k8s/data 10.168.1.1/16(rw,sync,insecure,no_subtree_check,no_root_squash)
```
| 参数             | 说明                                                         |
| ---------------- | ------------------------------------------------------------ |
| ro               | 只读访问                                                     |
| rw               | 读写访问                                                     |
| sync             | 所有数据在请求时写入共享                                     |
| async            | nfs在写入数据前可以响应请求                                  |
| secure           | nfs通过1024以下的安全TCP/IP端口发送                          |
| insecure         | nfs通过1024以上的端口发送                                    |
| wdelay           | 如果多个用户要写入nfs目录，则归组写入（默认）                |
| no_wdelay        | 如果多个用户要写入nfs目录，则立即写入，当使用async时，无需此设置 |
| hide             | 在nfs共享目录中不共享其子目录                                |
| no_hide          | 共享nfs目录的子目录                                          |
| subtree_check    | 如果共享/usr/bin之类的子目录时，强制nfs检查父目录的权限（默认） |
| no_subtree_check | 不检查父目录权限                                             |
| all_squash       | 共享文件的UID和GID映射匿名用户anonymous，适合公用目录        |
| no_all_squash    | 保留共享文件的UID和GID（默认）                               |
| root_squash      | root用户的所有请求映射成如anonymous用户一样的权限（默认）    |
| no_root_squash   | root用户具有根目录的完全管理访问权限                         |
| anonuid=xxx      | 指定nfs服务器/etc/passwd文件中匿名用户的UID                  |
| anongid=xxx      | 指定nfs服务器/etc/passwd文件中匿名用户的GID                  |
- 注1：尽量指定IP段最小化授权可以访问NFS 挂载的资源的客户端
- 注2：经测试参数insecure必须要加，否则客户端挂载出错mount.nfs: access denied by server while mounting
### 启动NFS服务
- 配置完成后，您可以在终端提示符后运行以下命令来启动 NFS 服务器：
```bash
sudo systemctl enable nfs-server
sudo systemctl start nfs-server
```
### 检查NFS服务提供是否正常
- 到客户机上执行showmount命令进行检查(`showmount -e `)
```bash
[root@node1 ~]# showmount -e 10.168.1.14
Export list for 10.168.1.14:
/k8s/data 10.168.1.1/16
```
### 安装 nfs-client-provisioner
添加helm chart仓库
```bash
helm repo add mogu-chart https://it00021hot.github.io/mogu-chart
helm repo update
```
- 在集群每一个节点安装`nfs-utils`
```bash
sudo yum install -y nfs-utils
```
- 在master节点执行下面helm命令，安装`nfs-client-provisioner`
```bash
helm upgrade --install nfs-client-provisioner mogu-chart/nfs-client-provisioner \
    --set rbac.create=true \
    --set persistence.enabled=true \
    --set storageClass.name=nfs-provisioner \
    --set persistence.nfsServer=10.168.1.14 \
    --set persistence.nfsPath=/k8s/data \
    --version 0.1.1 \
    --namespace kube-system
```
### 验证安装
- 新建`write-pod.yaml`文件，粘贴以下内容：
```yaml
kind: Pod
apiVersion: v1
metadata:
  name: write-pod
spec:
  containers:
  - name: write-pod
    image: busybox
    command:
      - "/bin/sh"
    args:
      - "-c"
      - "touch /mnt/SUCCESS && exit 0 || exit 1"
    volumeMounts:
      - name: nfs-pvc
        mountPath: "/mnt"
  restartPolicy: "Never"
  volumes:
    - name: nfs-pvc
      persistentVolumeClaim:
        claimName: myclaim
---
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: myclaim
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: nfs-provisioner
  resources:
    requests:
      storage: 1Mi
```
- 部署测试用例
```bash
kubectl apply -f write-pod.yaml
```
- 验证是否正常
```bash
[root@node1 ~]# kubectl get pod
NAME        READY   STATUS      RESTARTS   AGE
write-pod   0/1     Completed   0          3s
```
pod状态为`Completed`则为正常，若长时间为`ContainerCreating`状态则为不正常，请确认安装操作步骤是否正确。
- 清除测试用例
```bash
kubectl delete -f write-pod.yaml
```
## MySQL部署
### 添加helm chart仓库
```bash
helm repo add mogu-chart http://47.106.230.203:9090/
helm repo update
```
### 部署Mysql
#### 编写配置文件`mysql.yaml`
```bash
tee mysql.yaml mogu.sql; sed -i '2d' mogu.sql
```
- 导入sql脚本
```bash
kubectl -n base-system exec -it $(kubectl -n base-system get pod -l "mysql/release=mogu-mysql" -o jsonpath='{.items[0].metadata.name}') -- mysql -uroot -ppassword < mogu.sql
```
## Redis部署
### 添加helm chart仓库
```bash
helm repo add mogu-chart http://47.106.230.203:9090/
helm repo update
```
### 部署redis
编写配置文件`redis.yaml`
```bash
tee redis.yaml<<-EOF
service:
  enabled: true
  type: ClusterIP
persistence:
  enabled: true
  storageClass: nfs-provisioner
  accessMode: ReadWriteOnce
EOF
```
- 执行安装
```bash
helm upgrade --install mogu-redis mogu-chart/redis \
    -f redis.yaml \
    --create-namespace \
    --version 0.2.6	\
    --namespace base-system
```
## Minio部署
### 添加helm chart仓库
```bash
helm repo add mogu-chart http://47.106.230.203:9090/
helm repo update
```
### 部署minio
编写配置文件`minio.yaml`
```bash
tee minio.yaml<<-EOF
service:
  enabled: true
persistence:
  enabled: true
  storageClass: nfs-provisioner
ingress:
  enabled: true
  host: minio.local.com
  path: 
EOF
```
- 执行安装
```bash
helm upgrade --install minio mogu-chart/minio \
    -f minio.yaml \
    --create-namespace \
    --version 1.0.0	\
    --namespace base-system
```
## RabbitMQ部署
### 添加helm chart仓库
```bash
helm repo add mogu-chart http://47.106.230.203:9090/
helm repo update
```
### 部署rabbitmq
编写配置文件`rabbitmq.yaml`
```bash
tee rabbitmq.yaml<<-EOF
auth:
  username: mogumq
  password: mogumq
persistence:
  enabled: true
  storageClass: nfs-provisioner
  size: 1Gi
ingress:
  enabled: true
  hostname: rabbitmq.local.com
EOF
```
- 执行安装
```bash
helm upgrade --install rabbitmq mogu-chart/rabbitmq \
    -f rabbitmq.yaml \
    --create-namespace \
    --namespace base-system
```
## Nacos部署
### 添加helm chart仓库
```bash
helm repo add mogu-chart http://47.106.230.203:9090/
helm repo update
```
### 部署nacos
#### 导入数据库
- 导入DB中的数据库文件`nacos.sql`到mysql中
```bash
kubectl -n base-system exec -it $(kubectl -n base-system get pod -l "mysql/release=mogu-mysql" -o jsonpath='{.items[0].metadata.name}') -- mysql -uroot -ppassword nacos < nacos.sql
```
#### 部署nacos
- 编写配置文件`nacos.yaml`
```bash
tee nacos.yaml<<-EOF
global:
  mode: standalone
mysql:
  rootPassword: password
  database: nacos
  user: nacos
  password: nacos
  port: 3306
env:
  dbHost: mogu-mysql  
service:
  type: ClusterIP
ingress:
  enabled: true
  hosts:
    - host: nacos.local.com  
resources:
  limits:
    cpu: 1000m
    memory: 2Gi
  requests:
    cpu: 1000m
    memory: 2Gi    
EOF
```
- 执行安装
```bash
helm upgrade --install nacos mogu-chart/nacos \
    -f nacos.yaml \
    --create-namespace \
    --namespace base-system
```
## Sentinel部署
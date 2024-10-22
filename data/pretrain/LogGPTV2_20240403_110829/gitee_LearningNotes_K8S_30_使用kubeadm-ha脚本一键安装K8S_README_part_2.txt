```
cd kubeadm-ha
```
### 执行一键部署命令
```sh
ansible-playbook -i example/hosts.s-master.ip.ini 90-init-cluster.yml
```
### 查看节点运行情况
```sh
kubectl get nodes
```
等待所有节点ready 即为创建成功	
```
NAME             STATUS   ROLES                AGE     VERSION
192.168.28.128   Ready    etcd,worker          2m57s   v1.18.14
192.168.28.80    Ready    etcd,master,worker   3m29s   v1.18.14
192.168.28.89    Ready    etcd,worker          2m57s   v1.18.14
```
### 集群重置
如果部署失败了，想要重置整个集群【包括数据】，执行下面脚本
```bash
ansible-playbook -i example/hosts.s-master.ip.ini 99-reset-cluster.yml
```
## 部署kuboard
### 安装Docker
因为我们需要拉取镜像，所以需要在服务器提前安装好Docker，首先配置一下Docker的阿里yum源
```bash
cat >/etc/yum.repos.d/docker.repo> /etc/docker/daemon.json  kuboard和rancher建议部署其中一个
### helm安装
使用helm部署rancher会方便很多，所以需要安装helm
```bash
curl -O http://rancher-mirror.cnrancher.com/helm/v3.2.4/helm-v3.2.4-linux-amd64.tar.gz
tar -zxvf helm-v3.2.4-linux-amd64.tar.gz
mv linux-amd64/helm /usr/local/bin
```
#### 验证
```bash
helm version
```
输入以下内容说明helm安装成功
```bash
version.BuildInfo{Version:"v3.2.4", GitCommit:"0ad800ef43d3b826f31a5ad8dfbb4fe05d143688", GitTreeState:"clean", GoVersion:"go1.13.12"}
```
### 添加rancher chart仓库
```bash
helm repo add rancher-stable http://rancher-mirror.oss-cn-beijing.aliyuncs.com/server-charts/stable
helm repo update
```
### 安装rancher
```bash
helm install rancher rancher-stable/rancher \
 --create-namespace	\
 --namespace cattle-system \
 --set hostname=rancher.local.com
```
##### 等待 Rancher 运行：
```bash
kubectl -n cattle-system rollout status deploy/rancher
```
输出信息：
```bash
Waiting for deployment "rancher" rollout to finish: 0 of 3 updated replicas are available...
deployment "rancher" successfully rolled out
```
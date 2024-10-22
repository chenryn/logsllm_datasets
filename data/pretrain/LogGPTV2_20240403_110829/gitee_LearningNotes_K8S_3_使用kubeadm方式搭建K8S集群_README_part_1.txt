# 使用kubeadm方式搭建K8S集群
kubeadm是官方社区推出的一个用于快速部署kubernetes集群的工具。
这个工具能通过两条指令完成一个kubernetes集群的部署：
```bash
# 创建一个 Master 节点
kubeadm init
# 将一个 Node 节点加入到当前集群中
kubeadm join 
```
## Kubeadm方式搭建K8S集群
使用kubeadm方式搭建K8s集群主要分为以下几步
- 准备三台虚拟机，同时安装操作系统CentOS 7.x
- 对三个安装之后的操作系统进行初始化操作
- 在三个节点安装 docker kubelet kubeadm kubectl
- 在master节点执行kubeadm init命令初始化
- 在node节点上执行 kubeadm join命令，把node节点添加到当前集群
- 配置CNI网络插件，用于节点之间的连通【失败了可以多试几次】
- 通过拉取一个nginx进行测试，能否进行外网测试
## 安装要求
在开始之前，部署Kubernetes集群机器需要满足以下几个条件：
- 一台或多台机器，操作系统 CentOS7.x-86_x64
- 硬件配置：2GB或更多RAM，2个CPU或更多CPU，硬盘30GB或更多【注意master需要两核】
- 可以访问外网，需要拉取镜像，如果服务器不能上网，需要提前下载镜像并导入节点
- 禁止swap分区
## 准备环境
| 角色   | IP              |
| ------ | --------------- |
| master | 192.168.177.130 |
| node1  | 192.168.177.131 |
| node2  | 192.168.177.132 |
然后开始在每台机器上执行下面的命令
```bash
# 关闭防火墙
systemctl stop firewalld
systemctl disable firewalld
# 关闭selinux
# 永久关闭
sed -i 's/enforcing/disabled/' /etc/selinux/config  
# 临时关闭
setenforce 0  
# 关闭swap
# 临时
swapoff -a 
# 永久关闭
sed -ri 's/.*swap.*/#&/' /etc/fstab
# 根据规划设置主机名【master节点上操作】
hostnamectl set-hostname k8smaster
# 根据规划设置主机名【node1节点操作】
hostnamectl set-hostname k8snode1
# 根据规划设置主机名【node2节点操作】
hostnamectl set-hostname k8snode2
# 在master添加hosts
cat >> /etc/hosts  /etc/sysctl.d/k8s.conf /etc/yum.repos.d/docker.repo> /etc/docker/daemon.json  /etc/yum.repos.d/kubernetes.repo  注意，以下的命令是在master初始化完成后，每个人的都不一样！！！需要复制自己生成的
```bash
kubeadm join 192.168.177.130:6443 --token 8j6ui9.gyr4i156u30y80xf \
    --discovery-token-ca-cert-hash sha256:eda1380256a62d8733f4bddf926f148e57cf9d1a3a58fb45dd6e80768af5a500
```
默认token有效期为24小时，当过期之后，该token就不可用了。这时就需要重新创建token，操作如下：
```
kubeadm token create --print-join-command
```
当我们把两个节点都加入进来后，我们就可以去Master节点 执行下面命令查看情况
```bash
kubectl get node
```
![image-20201113165358663](images/image-20201113165358663.png)
## 部署CNI网络插件
上面的状态还是NotReady，下面我们需要网络插件，来进行联网访问
```bash
# 下载网络插件配置
wget https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
```
默认镜像地址无法访问，sed命令修改为docker hub镜像仓库。
```bash
# 使用kubeadm-ha脚本一键安装K8S
## 前情提示
以前安装 **K8S** 集群的时候使用的是 **k8s** 官网的教程 使用的镜像源都是国外的 速度慢就不说了 还有一些根本就下载不动 导致安装失败 最后在群里小伙伴(蘑菇博客交流群/@你钉钉响了) 的建议下使用一个开源的一键安装k8s的脚本就好了起来了
> Github地址：https://github.com/TimeBye/kubeadm-ha
## 环境准备
官网的安装说明也很简单但是还有些细节还是没有提到，所以我自己照着官网的教程 补充了一些细节
### 硬件系统要求
- Master节点：2C4G +
- Worker节点：2C4G +
使用centos7.7安装请按上面配置准备好3台centos,1台作为Master节点,2台Worker节点
本方式为1主2worker的配置
这是我的各个节点的配置
| 主机名     | ip              | 配置 |
| ---------- | --------------- | ---- |
| k8s-master | 192.168.177.130 | 2C4G |
| k8s-node1  | 192.168.177.131 | 2C2G |
| k8s-node2  | 192.168.177.132 | 2C2G |
### centos准备
`在安装之前需要准备一些基础的软件环境用于下载一键安装k8s的脚本和编辑配置`
#### centos网络准备
安装时需要连接互联网下载各种软件 所以需要保证每个节点都可以访问外网
```sh
ping baidu.com
```
建议关闭 **CentOS** 的防火墙
```sh
systemctl stop firewalld  && systemctl disable firewalld && systemctl status firewalld 
```
同时需要保证各个节点间可以相互ping通
```sh
ping 其他节点ip
```
#### CentOS软件准备
用 **ssh** 连接到 **Master** 节点上安装 Git
```sh
yum install git -y
```
## 部署k8s前配置
#### 下载部署脚本
在Master节点clone安装脚本 [脚本地址](https://github.com/TimeBye/kubeadm-ha)
```
git clone --depth 1 https://github.com/TimeBye/kubeadm-ha
```
进入到下载的部署脚本的目录
```
cd kubeadm-ha
```
#### 安装 Ansible 运行环境
在master节点安装Ansible环境
```sh
sudo ./install-ansible.sh
```
#### 修改安装的配置文件
由于我是一个master两个node的方式构建的centos所以我们需要修改example/hosts.s-master.ip.ini 文件
```sh
vi example/hosts.s-master.ip.ini 
```
具体要修改的就是 ip 和密码 其他的保持默认
我的hosts.s-master.ip.ini 文件预览
```ini
; 将所有节点信息在这里填写
;    第一个字段                  为远程服务器内网IP
;    第二个字段 ansible_port     为节点 sshd 监听端口
;    第三个字段 ansible_user     为节点远程登录用户名
;    第四个字段 ansible_ssh_pass 为节点远程登录用户密码
[all]
192.168.177.130 ansible_port=22 ansible_user="root" ansible_ssh_pass="moxi"
192.168.177.131 ansible_port=22 ansible_user="root" ansible_ssh_pass="moxi"
192.168.177.132 ansible_port=22 ansible_user="root" ansible_ssh_pass="moxi"
; 单 master 节点不需要进行负载均衡，lb节点组留空。
[lb]
; 注意etcd集群必须是1,3,5,7...奇数个节点
[etcd]
192.168.177.130
192.168.177.131
192.168.177.132
[kube-master]
192.168.177.130
[kube-worker]
192.168.177.130
192.168.177.131
192.168.177.132
; 预留组，后续添加master节点使用
[new-master]
; 预留组，后续添加worker节点使用
[new-worker]
; 预留组，后续添加etcd节点使用
[new-etcd]
; 预留组，后续删除worker角色使用
[del-worker]
; 预留组，后续删除master角色使用
[del-master]
; 预留组，后续删除etcd角色使用
[del-etcd]
; 预留组，后续删除节点使用
[del-node]
;-------------------------------------- 以下为基础信息配置 ------------------------------------;
[all:vars]
; 是否跳过节点物理资源校验，Master节点要求2c2g以上，Worker节点要求2c4g以上
skip_verify_node=true
; kubernetes版本
kube_version="1.18.14"
; 负载均衡器
;   有 nginx、openresty、haproxy、envoy  和 slb 可选，默认使用 nginx
;   为什么单 master 集群 apiserver 也使用了负载均衡请参与此讨论： https://github.com/TimeBye/kubeadm-ha/issues/8
lb_mode="nginx"
; 使用负载均衡后集群 apiserver ip，设置 lb_kube_apiserver_ip 变量，则启用负载均衡器 + keepalived
; lb_kube_apiserver_ip="192.168.56.15"
; 使用负载均衡后集群 apiserver port
lb_kube_apiserver_port="8443"
; 网段选择：pod 和 service 的网段不能与服务器网段重叠，
; 若有重叠请配置 `kube_pod_subnet` 和 `kube_service_subnet` 变量设置 pod 和 service 的网段，示例参考：
;    如果服务器网段为：10.0.0.1/8
;       pod 网段可设置为：192.168.0.0/18
;       service 网段可设置为 192.168.64.0/18
;    如果服务器网段为：172.16.0.1/12
;       pod 网段可设置为：10.244.0.0/18
;       service 网段可设置为 10.244.64.0/18
;    如果服务器网段为：192.168.0.1/16
;       pod 网段可设置为：10.244.0.0/18
;       service 网段可设置为 10.244.64.0/18
; 集群pod ip段，默认掩码位 18 即 16384 个ip
kube_pod_subnet="10.244.0.0/18"
; 集群service ip段
kube_service_subnet="10.244.64.0/18"
; 分配给节点的 pod 子网掩码位，默认为 24 即 256 个ip，故使用这些默认值可以纳管 16384/256=64 个节点。
kube_network_node_prefix="24"
; node节点最大 pod 数。数量与分配给节点的 pod 子网有关，ip 数应大于 pod 数。
; https://cloud.google.com/kubernetes-engine/docs/how-to/flexible-pod-cidr
kube_max_pods="110"
; 集群网络插件，目前支持flannel,calico
network_plugin="calico"
; 若服务器磁盘分为系统盘与数据盘，请修改以下路径至数据盘自定义的目录。
; Kubelet 根目录
kubelet_root_dir="/var/lib/kubelet"
; docker容器存储目录
docker_storage_dir="/var/lib/docker"
; Etcd 数据根目录
etcd_data_dir="/var/lib/etcd"
```
#### 升级内核
修改完配置文件后建议升级内核
```sh
ansible-playbook -i example/hosts.s-master.ip.ini 00-kernel.yml
```
内核升级完毕后重启所有节点 在master node1 node2上执行
```sh
reboot
```
## 开始部署k8s
等待所有的节点重启完成后进入脚本目录
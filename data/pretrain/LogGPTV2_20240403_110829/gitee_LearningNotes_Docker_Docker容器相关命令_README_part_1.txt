本文整理在 Ubuntu 16.04.x LTS 操作系统上容器相关部署手册
容器平台
- Rancher
- Kubernetes
- Helm
- Docker
容器服务
- prometheus
- grafana
- postgresql
# 1.Docker
## 1.1.apt source
更换apt源大多数情况下可以加快软件下载速度。
```
cp /etc/apt/sources.list /etc/apt/sources.list.bak
# 阿里源
tee > /etc/apt/sources.list  /etc/apt/sources.list  /etc/apt/sources.list  /etc/apt/sources.list ”表示覆写文件，“>>”表示在文件尾部添加。“tee”可以省略“>”来覆写，“cat”不能省略。
“deb”是指deb包目录；“deb-src”是源码目录，一般注释掉。
## 1.2.install docker
官网
https://docs.docker.com/engine/install/ubuntu/
```
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
```
指定版本
```
apt-cache madison docker-ce
sudo apt-get install docker-ce= docker-ce-cli= containerd.io
```
## 1.3.docker source
配置镜像加速器
https://cr.console.aliyun.com/cn-hangzhou/instances/mirrors
```
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json  Dockerfile “自定义”，“安全设置”选择“自定义关键词”，即包含该关键词才能发送报警，记住最终生成的webhook
   ![image](images/1587988512682-beed08e0-a1f2-4809-bfab-98b5253610af.png)
   ![image](images/1587988610421-81bd3819-5a3d-4f14-8f80-f1c8e5b90329.png)
   ![image](images/1587988702278-175f3247-b5bd-4a40-834e-bfdfe4fba5d3.png)
   ![image](images/1587988437050-b19bcf36-2577-45eb-96d2-d88fd65507fa.png)
2. grafana配置报警
1. 1. 配置全局的dingding报警，输入webhook
   2. 在具体的图表中配置报警选择已配置的dingding报警
      ![image](images/1587989954726-3f5b6a7f-15cf-434a-b526-66522eaca98b.png)![image](images/1587990143702-1cefd6df-0f83-4e68-846e-cf8e4ebdb123.png)![image](images/1587990196040-4e320a97-10e1-4362-8dcf-efbf2ef6c3ff.png)![image](images/1587991013837-715ba47b-c043-4236-906b-6d1e406a162f.png)
### 1.6.2.dashboard template
https://grafana.com/grafana/dashboards?orderBy=name&direction=asc
https://grafana.com/grafana/dashboards/11376
![image](images/1587985751427-8e176c22-6bf1-410e-af31-4d36f2462c44.png)
基于docker 搭建Prometheus+Grafana
https://www.cnblogs.com/xiao987334176/p/9930517.html
Grafana + Prometheus 监控PostgreSQL
https://www.cnblogs.com/ilifeilong/p/10543876.html
# 2.rancher
官网
https://rancher.com/docs/rancher/v2.x/en/installation/other-installation-methods/single-node-docker/
```
docker run -d --restart=unless-stopped -p 80:80 -p 443:443 rancher/rancher:stable
```
如果下载慢，可以换源
```
docker run -d --restart=unless-stopped -p 80:80 -p 443:443 registry.cn-hangzhou.aliyuncs.com/rancher/rancher:v2.4.2
```
在rancher中可以快速创建k8s集群，rancher会生成一段命令，把命令复制到目标节点就可以快速创建集群。
# 3.Kubernetes
本地运行 k8s https://github.com/kubernetes/community/blob/master/contributors/devel/running-locally.md
## 3.1.prepare env
port
```
vim /etc/ssh/sshd_config
service ssh restart
sudo reboot
```
hostname
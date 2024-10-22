# 使用DockerCompose制作蘑菇博客YAML镜像文件
## 前言
首先特别感谢群里的小伙伴 [@touch fish](https://gitee.com/chengccn1) 使用DockerCompose部署了蘑菇博客，并且提供了 [搭建文档](https://gitee.com/chengccn1/mogu_blog_v2/blob/Nacos/docker-compose%E9%83%A8%E7%BD%B2.md)，本博客也是在上面的文档基础上进行修改~
本文主要讲解的是，如果将蘑菇博客制作成多个Docker业务镜像，逐步讲解每个镜像制作的过程
如果你只想快速部署蘑菇博客，那么可直接参考：[DockerCompose一键部署蘑菇博客(Nacos版)](http://www.moguit.cn/#/info?blogOid=565)
如果你想了解一下Docker Compose的使用，参考： [Docker Compose入门学习](http://www.moguit.cn/#/info?blogOid=568)
如果你想把制作好的镜像提交到镜像仓库，参考：[使用GithubAction构建蘑菇博客镜像提交DockerHub](http://www.moguit.cn/#/info?blogOid=569)
如果你想了解Docker图形化工具Portainer的使用，参考：[Docker图形化工具Portainer介绍与安装](http://www.moguit.cn/#/info?blogOid=570)
## 安装常用工具
我们首先安装一些可能会用到的工具
```bash
yum install vim net-tools unzip wget git maven -y
```
## 安装Docker
首先配置一下Docker的阿里yum源
```bash
cat >/etc/yum.repos.d/docker.repo> /etc/docker/daemon.json  /usr/local/bin/docker-compose
```
加入执行权限
```bash
# 加入执行权限
sudo chmod +x /usr/local/bin/docker-compose
# 查看docker-compose版本
docker-compose -v
```
### 离线安装
！！注意，如果上面下载速度过于缓慢，可以采用离线的安装方式
```bash
# 到github release中下载我们的docker-compose
https://github.com/docker/compose/releases
```
然后选择Linux版本下载
![image-20201124204747145](images/image-20201124204747145.png)
> 如果上述地址下载过于缓慢，请备用地址：[点我传送](https://wws.lanzous.com/iTHoIiuilvi)
把下载到的文件使用Xftp工具，拷贝到 `/usr/local/bin/` 目录下
```bash
# 重命名
mv docker-compose-Linux-x86_64  docker-compose
# 加入执行权限
sudo chmod +x /usr/local/bin/docker-compose
# 查看docker-compose版本
docker-compose -v
```
## 安装Git
我们下面需要安装Git，然后下载蘑菇博客源码，我们采用yum来进行安装
```bash
# 首先查看是否安装过 git【如果安装了就跳过】
git --version
```
然后进行安装
```bash
yum -y install git
```
安装好后，我们下载蘑菇博客的源码【选择nacos分支】
```bash
git clone -b Nacos --depth 1 https://gitee.com/chengccn1/mogu_blog_v2.git
```
## 安装基础环境
下面我们到蘑菇博客的源码目录，运行 `bash.sh` 脚本，主要用于安装常用工具，node等环境，内容如下。
```bash
#!/usr/bin/env bash
echo "=====Linux必要软件安装====="
echo "=====安装vim net-tools unzip wget git maven====="
yum install vim net-tools unzip wget git maven -y
echo "=====安装node14====="
wget https://mirrors.tuna.tsinghua.edu.cn/nodejs-release/v14.15.1/node-v14.15.1-linux-x64.tar.gz
tar xf node-v14.15.1-linux-x64.tar.gz -C /usr/local
mv /usr/local/node-v14.15.1-linux-x64/ /usr/local/node14
echo '
export NODE_HOME=/usr/local/node14
export PATH=$NODE_HOME/bin:$PATH
' >> /etc/bashrc
source /etc/bashrc
ln -s /usr/local/node14/bin/npm /usr/local/bin/
ln -s /usr/local/node14/bin/node /usr/local/bin/
echo "=====node14版本====="
node -v
echo "=====npm 版本====="
npm -v
rm -rf node-v14.15.1-linux-x64
```
我们进入源码目录，运行命令
```bash
sh base.sh
```
## 配置maven镜像源
maven的依赖，默认是从 maven repository中央仓库拉取的，可能会比较慢，我们需要增加镜像地址+
编辑文件
```bash
vim /usr/share/maven/conf/settings.xml
```
`` 标签下，增加如下内容
```bash
        alimaven
        central
        aliyun maven
        http://maven.aliyun.com/nexus/content/repositories/central/
        jboss-public-repository-group
        central
        JBoss Public Repository Group
        http://repository.jboss.org/nexus/content/groups/public
		central
		Maven Repository Switchboard
		http://repo1.maven.org/maven2/
		central
		repo2
		central
		Human Readable Name for this Mirror.
		http://repo2.maven.org/maven2/
```
## 部署博客初始环境
下面我们在源码目录，找到 `mogublog_base_service` 文件夹，然后拷贝到 `/root` 目录
```bash
# 拷贝
cp -R mogublog_base_service /root/
```
### 创建容器用的网络
创建网络
```bash
docker network create mogu
```
重启docker
```bash
systemctl restart docker
```
### 部署mysql
在 /soft/mogublog_base_service 执行下面命令
```bash
cd mysql && docker-compose up -d && cd ..
```
该命令主要执行了 mysql文件夹中的 docker-compose.yml ，然后给我们创建一个mysql容器
```bash
version: '3.1'
services:
  mysql:
    image: mysql
    restart: always
    container_name: mysql
    environment:
      MYSQL_ROOT_PASSWORD: root
    command:
      --default-authentication-plugin=mysql_native_password
      --character-set-server=utf8mb4
      --collation-server=utf8mb4_general_ci
      --explicit_defaults_for_timestamp=true
      --lower_case_table_names=1
    ports:
      - 3306:3306
    volumes:
      - ./data:/var/lib/mysql
      - ./init/:/docker-entrypoint-initdb.d/
    networks:
      - mogu
networks:
  mogu:
    external: true
```
- 在里面定义了用户名：root【默认】，密码：root
执行后，即会给我们拉取对应的mysql镜像
![image-20201124213715204](images/image-20201124213715204.png)
拉取完成后，我们使用下面命令，查看我们的启动情况
```bash
docker ps -a
```
![image-20201125092216871](images/image-20201125092216871.png)
能够看到我们的mysql容器，已经成功运行
### 部署nacos & redis & rabbitmq
然后我们执行下面的命令，完成nacos & redis & rabbitmq 的部署
```bash
docker-compose up -d
```
`docker-compose.yml`脚本内容如下所示： 
```bash
version: '3.1'
services:
  nacos:
    image: nacos/nacos-server
    container_name: nacos
    env_file:
      - ./nacos/nacos-msyql.env
    volumes:
      - ./nacos/standalone-logs/:/home/nacos/logs
      - ./nacos/custom.properties:/home/nacos/init.d/custom.properties
    ports:
      - "8848:8848"
      - "9555:9555"
    restart: always
    networks:
      - mogu
  redis:
    image: redis
    restart: always
    container_name: redis
    ports:
      - 6379:6379
    volumes:
      - ./redis/data:/data
    networks:
      - mogu
  rabbitmq:
    restart: always
    image: rabbitmq:management
    container_name: rabbitmq
    ports:
      - 5672:5672
      - 15672:15672
    environment:
      TZ: Asia/Shanghai
      RABBITMQ_DEFAULT_USER: guest
      RABBITMQ_DEFAULT_PASS: guest
    volumes:
      - ./rabbitmq/data:/var/lib/rabbitmq
    networks:
      - mogu
networks:
  mogu:
    external: true
```
执行完命令后，就会开始拉取 nacos、redis、rabbitmq的镜像
![image-20201125093823312](images/image-20201125093823312.png)
### 部署本地文件存储
我们执行下面的命令
```bash
docker-compose -f ./mogu_data/mogu_data.yml up -d
```
`mogu_data.yml` 脚本内容如下所示
```yml
version: '3'
services:
  #授权服务
  vue_mogu_web:
    image: nginx
    container_name: mogu_data
    restart: always
    ports:
      - 8600:80
    networks:
      - mogu
    volumes:
      - /home/moxi/mogu_blog_v2/mogu_data/:/home/mogu_blog/mogu_data/
      - ./default.conf:/etc/nginx/conf.d/default.conf
networks:
  mogu:
    external: true
```
这里将我们的 mogu_data数据目录挂载出来了，同时也把配置文件挂载了出来，default.confi 如下所示
```bash
    server {
        listen       80;
        server_name  localhost;
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS';
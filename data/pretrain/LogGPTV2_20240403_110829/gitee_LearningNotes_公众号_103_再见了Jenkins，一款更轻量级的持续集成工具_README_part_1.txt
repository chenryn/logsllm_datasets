大家好，我是 **陌溪**
最近，群里有小伙伴在倒腾一个叫 **Drone** 的项目，说它比 **Jenkins** 更轻量级。
其实，在原来很久之前，蘑菇博客就已经接入了 **Github Actions** 做持续集成，想要了解的小伙伴可以看看这篇文章：还在人肉运维？[看看蘑菇博客是如何实现自动化部署](https://mp.weixin.qq.com/s?__biz=MzkyMzE5NTYzMA==&amp;mid=2247485568&amp;idx=1&amp;sn=d96b4d04014d24bd1547e44e12842827&amp;chksm=c1e98901f69e0017083c37d2551e0854c868d844c94abf9d81ce5c4b7aa1803f9956b1a18af2&token=1905884391&lang=zh_CN#rd)。
目前 **Github** + **Github Actions** 的方式，也是个人和小型公司的首选，因为 **Github Actions** 会提供一台 **1C 4G** 的机器，用来帮助我们构建镜像，并且不限时长。
对比 **Coding** 的流水线，在我使用了 **300** 分钟后。。就提示我要充值了，**Github** 的流水线还是非常良心的~
![Coding流水线](images/dd9cb3bb35ad4d99b88854b47e7e220d.png)
好了，下面回归正题，在接受了群友的安利后。抱着学习的新技术的态度，周末两天开启了 **Drone** 学习之旅，
在学一门技术之前，首先看看 **Github** 上能不能搜到，打开一看，没想到 **Star** 已经有 **25.6K** 了！
> Github地址：https://github.com/harness/drone
![Drone Github](images/image-20220904220158885.png)
再去看看 **jenkins**  **19.4K** Star， 通过点赞数就能看出来， **Drone** 是比 **Jenkins** 更火了~
![Jenkins Github官网](images/image-20220904220334635.png)
相比 **Gitlab + Jenkins** 实现自动化部署，大概需要 **4G** 以上的内存才能够运行起来。而 **Drone** + **Gitee** 使用内存不到 **1G** ~
以下是两者的对比图，小伙伴也可以了解一下~
![对比图](images/image-20220905125416493.png)
## 什么是 Drone？
**Drone **是一个面向忙碌的开发团队的自助持续集成和持续交付平台。
> 官网：https://www.drone.io/
同时，**Drone** 是使用 **Golang** 语言进行编写。所有的编译、测试的流程都在 Docker 容器中执行。**Drone** 通过使用简单的 **YAML** 配置文件，就可以轻松的定义出一条流水线，并且每一个构建操作都是在一个临时的 **Docker** 容器中执行，能够完全控制其构建环境并保证隔离。最后，开发人员只需要在项目中引入 **.drone.yml** 文件，将代码推送到 Git 仓库中，即可自动化的完成**编译**、**测试** 和 **发布**。
简单来说，**Drone** 其实就是一款轻量级的 **Jenkins** ，可以占用更少的资源，实现软件的流水线操作，并且可以轻松的和 **Gitlab**、**Gitee**、**Github** 相结合。
![Drone官网](images/image-20220904223731751.png)
## 创建 OAuth2应用
由于**蘑菇博客**是部署在 **Gitee** 中的，因此本文将介绍 **Drone** 如何实现：代码提交到 **Gitee** 上，自动触发 **Drone** 流水线，完成项目的打包和部署
首先，打开 **Gitee** 上的设置页面，找到 **第三方应用**，然后选择创建应用
> 地址：https://gitee.com/oauth/applications
![创建Gitee应用](images/image-20220904224325440.png)
然后填写相关的信息，需要注意的是，这里的 **ip** 地址，需要换成自己服务器的
- **应用主页**：服务器地址+端口号
- **应用回调地址**：服务器地址+端口号/login 
- **权限**：把这四个都勾选上，否则后面登录可能会报错
![配置应用信息](images/image-20220904224546243.png)
点击创建应用，就会得到 **ClientKey** 和 **ClientSecret** ，需要保存好，后续在编写 **docker-compose.yml** 文件的时候会用到
![获取ClientId](images/image-20220904225103874.png)
## 生成RPC秘钥
由于 **drone server** 和 **drone runner** 通信需要使用秘钥，因此可以使用 openssl 命令生成
```bash
$ openssl rand -hex 16
bea26a2221fd8090ea38720fc445eca6
```
可以也需要保存改秘钥，在下面需要使用
## 编写 drone.yml 文件
首先，需要编写 **drone** 的 **docker-compose** 文件，用来创建 **drone** 容器 
创建 **drone.yml** 文件，并修改以下的内容
- **DRONE_GITEE_CLIENT_ID**：上面的 **Gtiee** 的 **Client ID** 值
- **DRONE_GITEE_CLIENT_SECRET**：**Gitee OAuth2** 客户端密钥（上面的 **Client Secret** 值）
- **DRONE_RPC_SECRET**：**Drone** 的共享密钥（生成 **RPC** 密钥）
- **DRONE_SERVER_HOST**：**Drone** 的主机名(改成自己的域名获得 ip+端口(注意是drome的))
- **DRONE_USER_CREATE**：创建管理员账户，这里对应为 **Gitee** 的用户名(也就是登录的账号,不是昵称)(填错了回导致自动化部署失败)
```yml
version: '3'
networks:
  mogu:
    external: false
services:
  # 容器名称
  drone-server:
    container_name: drone
    # 构建所使用的镜像
    image: drone/drone
    # 映射容器内80端口到宿主机的8611端口8611端口,若修改的话，那么上面Gitee上也需要进行修改
    ports:
      - 8611:80
    # 映射容器内/data目录到宿主机的目录
    volumes:
      - /usr/local/bin/drone:/data
    # 容器随docker自动启动
    restart: always
    privileged: true
    networks:
      - mogu
    environment:
      # Gitee 服务器地址如果github就把GITEE改成GITHUB和https://gitee.com改成https://github.com
      - DRONE_GITEE_SERVER=https://gitee.com
      # Gitee OAuth2客户端ID
      # - DRONE_GITEA_CLI（上面的Client ID值）
      - DRONE_GITEE_CLIENT_ID=0a334xxxxxxxxc711e40af
      # Gitee OAuth2客户端密钥（上面的Client Secret值）
      - DRONE_GITEE_CLIENT_SECRET=79173f5367xxxxx000899
      # drone的共享密钥（生成rpc密钥）
      - DRONE_RPC_SECRET=bea26a2221fd8090ea38720fc445eca6
      # drone的主机名(改成自己的域名获得ip+端口(注意是drome的))
      - DRONE_SERVER_HOST=192.168.11.1:8611
      # 外部协议方案根据你的域名判断是http还是https(ip加端口是http)
      - DRONE_SERVER_PROTO=http
      - DRONE_GIT_ALWAYS_AUTH=false
     # 创建管理员账户，这里对应为gitee的用户名(也就是登录的账号,不是昵称)(填错了回导致自动化部署失败)
      - DRONE_USER_CREATE=username:PI:EMAIL,admin:true
  docker-runner:
    container_name: drone-runner
    image: drone/drone-runner-docker
    restart: always
    privileged: true
    networks:
      - mogu
    depends_on:
      - drone-server
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /sync/drone/agent/drone.key:/root/drone.key
    environment:
      # 用于连接到Drone服务器的协议。该值必须是http或https。(同上)
      - DRONE_RPC_PROTO=http
      # 用于连接到Drone服务器的主机名(同上)
      - DRONE_RPC_HOST=81.70.100.87:8611
      # Drone服务器进行身份验证的共享密钥，和上面设置一样（生成rpc密钥）
      - DRONE_RPC_SECRET=bea26a2221fd8090ea38720fc445eca6
      # 限制运行程序可以执行的并发管道数
      - DRONE_RUNNER_CAPACITY=2
        # docker runner 名称
      - DRONE_RUNNER_NAME=docker-runner
      - DRONE_DEBUG=true                      # 调试相关，部署的时候建议先打开
      - DRONE_LOGS_DEBUG=true                 # 调试相关，部署的时候建议先打开
      - DRONE_LOGS_TRACE=true                 # 调试相关，部署的时候建议先打开
      - TZ=Asia/Shanghai
```
填写完毕后，我们将 **drone.yml** 文件拷贝到服务器上，使用下面的命令运行
```bash
docker-compose -f drone.yml up -d
```
这里需要小伙伴们提前下载好 **docker-compose**，如果不清楚什么是 **docker-compose** 的小伙伴，下面有一个简单的介绍
> Docker Compose 是用来定义和运行多个Docker应用程序的工具。通过Compose，可以使用YAML文件来配置应用程序需要的所有服务，然后使用一个命令即可从YML文件配置中创建并启动所有服务
首先到 **Github release**中下载我们的 **docker-compose**
```bash
https://github.com/docker/compose/releases
```
然后选择 **Linux** 版本下载
![下载 docker-compose](images/2349756c7481408896e00f6a6cf8a8b7.png)
把下载到的文件使用 **Xftp** 工具，拷贝到 `/usr/local/bin/` 目录下
```bash
# 重命名
mv docker-compose-Linux-x86_64  docker-compose
# 加入执行权限
sudo chmod +x /usr/local/bin/docker-compose
# 查看docker-compose版本
docker-compose -v
```
安装完成后，再次使用上面的命令，安装 **drone**，安装完成后，使用 **docker ps  -a** 即可查看到安装的 **drone** 了
![运行的drone容器](images/image-20220904231425541.png)
下面两个运行的容器的作用分别如下：
- **drone**：为 **Drone** 的管理提供了 **Web** 页面，用于管理从 **Git** 上获取的仓库中的流水线任务
- **drone-runner**：一个单独的守护进程，会轮询 **Server**，获取需要执行的流水线任务，之后执行
如果你正确的启动了上述的两个容器，那么你打开浏览器，输入**IP:8611** 可以进入到 **Drone** 主服务的 **Web** 管理界面的登录界面，
![drone登录页](images/image-20220904231651466.png)
点击 **Continue** 后，即可跳转到 **Gitee** 的 **OAuth** 授权页面，这里直接点击 **同意授权**
![Gitee授权登录](images/image-20220904231738315.png)
授权通过后，在我们仓库的管理页面，即可看到新增了一条 **WebHook** 记录，当 **Gitee** 有新的代码提交请求后，就会通过调用下面的地址，从而让 **Drone** 能够启动流水线操作。 
![新增Webhook记录](images/image-20220904232045948.png)
登录成功后，即可跳转到 **Drone** 的主页，在这里是能够看到 **Gitee** 上全部的项目的
![查看所有项目](images/image-20220904232627233.png)
我们找到需要构建流水线的项目，然后进入后点击 **激活仓库**
> 这里是有BUG的，如果你的项目是中文名称的话，进去是会 404 
![激活项目](images/image-20220904232858152.png)
然后把下面几个开关进行打开，主要是开启容器特权，以及自动取消构建
![开启开关](images/image-20220904233033596.png)
## 创建一个 **SpringBoot** 项目
首先，我们在 Gitee 上创建一个私有的仓库 **hello-mogu**
> https://gitee.com/projects/new
![新建一个仓库](images/image-20220904235604920.png)
然后打开网站 **start.spring.io** 初始化一个最简单的 **SpringBoot** 项目
![初始化一个SpringBoot项目](images/image-20220904235847611.png)
然后下载后解压，即可看到以下的目录
![解压项目](images/image-20220904235934524.png)
然后使用以下命令，将该项目和刚刚创建的Gitee仓库关联上
```bash
git init
git commit -m "first commit"
git remote add origin https://gitee.com/moxi159753/hello-mogu.git
git push -u origin "master"
```
下面即可看到代码成功推送到 **Gitee** 上了
![推送到Gitee](images/image-20220905000632080.png)
## Drone 流水线命令
接下来，需要通过将 **.drone.yml** 文件创建到 **Git** 存储库的根目录来配置管道。在这个文件中，定义了每次收到 **Webhook** 时执行的一系列步骤。
下面这个是最简单的一个 **drone** 流水线，我们创建  **.drone.yml** 文件，写上下面的内容
```YML
kind: pipeline  # kind 属性定义了对象的种类。此示例定义了一个管道对象。
type: docker	# type 属性定义管道的类型。此示例定义了一个 Docker 管道，其中每个管道步骤都在 Docker 容器内执行。
name: default   # name 属性定义了管道的名称。您可以为您的项目定义一个或多个管道
steps: # 步骤部分定义了一系列串行执行的管道步骤。如果管道中的任何步骤失败，管道将立即退出
- name: greeting # name 属性定义管道步骤的名称
  image: alpine # image 属性定义了一个执行 shell 命令的 Docker 镜像。您可以使用来自任何 DockerHub 中的任何 Docker镜像。
  commands: # commands 属性将在 Docker 容器内执行的 shell 命令列表定义为容器入口点。如果任何命令返回非零退出代码，则管道步骤将失败。
  - echo hello
  - echo world
```
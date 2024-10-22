写完后，再次将该提交提交到远程仓库，然后找到刚刚创建的仓库（如果没有，先执行 **SYNC** 操作）
![Drone中找到刚刚创建的仓库](images/image-20220905000816874.png)
点击仓库内，设置好配置，点击保存
![修改配置并保存](images/image-20220905000915796.png)
然后切换到构建页面，点击创建
![启动构建](images/image-20220905001021162.png)
创建完成后，项目就会进行流水线构建【以后可以设置代码提交，主动触发】
![构建记录](images/image-20220905001105048.png)
点击记录详情页，可以看到打印出来的 **hello world**
![构建详情页](images/image-20220905001208643.png)
## 更多流水线操作
例如，我们可以将两个步骤串连起来，第一个步骤输出 **hello world**、第一个输出  **bonjour monde**
```yml
kind: pipeline
type: docker
name: greeting
steps:
- name: en
  image: alpine
  commands:
  - echo hello world
- name: fr
  image: alpine
  commands:
  - echo bonjour monde
```
在我们推送代码后，就可以看到流水线已经正常输出内容了
![流水线运行成功](images/image-20220905083537532.png)
同时，我们也可以定义多个管道，串联的去执行
```yml
kind: pipeline
type: docker
name: en
steps:
- name: greeting
  image: alpine
  commands:
  - echo hello world
---
kind: pipeline
type: docker
name: fr
steps:
- name: greeting
  image: alpine
  commands:
  - echo bonjour monde
```
同时，通过增加 **trigger** 可以设置管道触发的方式，例如，push：代码提交后触发，pull_request：代码PR后触发
```yml
kind: pipeline
type: docker
name: en
steps:
- name: greeting
  image: alpine
  commands:
  - echo hello world
trigger:
  event:
  - push
  - pull_request
  - tag
  - promote
  - rollback
```
下面我们来完整的测试一下 **hello-mogu**
首先，我们在刚刚的 **SpringBoot** 项目中，创建一个 **Controller** 文件，写上一个 hello 蘑菇的方法
![hello mogu](images/image-20220905085002294.png)
```java
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
@RestController
public class HelloMogu {
    @GetMapping("/hello-mogu")
    public String helloMogu() {
        return "hello-mogu";
    }
}
```
然后编辑 .drone.yml 文件，编写流水线代码
```yml
kind: pipeline # 定义对象类型，还有secret和signature两种类型
type: docker # 定义流水线类型，还有kubernetes、exec、ssh等类型
name: hello-mogu # 定义流水线名称
steps: # 定义流水线执行步骤，这些步骤将顺序执行
  - name: build-package # 流水线名称
    image: maven:3.8.5-openjdk-8 # 定义创建容器的Docker镜像
    volumes: # 将容器内目录挂载到宿主机，仓库需要开启Trusted设置
      - name: maven-build
        path: /root/hello-mogu # 将应用打包好的Jar和执行脚本挂载出来
    commands:
      - mvn clean package -DskipTests=true
      # 将打包后的jar包，拷贝到 /root/hello-mogu 目录
      - cp /drone/src/target/hello-mogu-0.0.1-SNAPSHOT.jar  /root/hello-mogu
volumes: # 定义流水线挂载目录，用于共享数据
  - name: maven-build
    host:
      path: /root/hello-mogu   #jar包目录可以修改从宿主机中挂载的目录
```
这里使用了  **build-package** 的镜像进行构建，里面包含了 **Java** 和 **Mavne** 环境。
同时，为了方便将构建好的 **Jar** 包挂载出来，我们使用了 **volumes** ，需要指定容器内的地址 以及 挂载到宿主机的位置
将修改后的代码推送到 Gitee 中，可以看到流水线正常运行，并且在开始下载依赖进行构建 **jar** 包
![构建详情页](images/image-20220905085833237.png)
执行成功后，我们打开自己的服务器，在 /root/hello-mogu 目录，就可以看到刚刚打包后的 **jar** 包了
![打包成功的jar](images/image-20220905090914303.png)
如果你服务器有 java 环境，可以直接用下面的命令启动
```bash
java -jar hello-mogu-0.0.1-SNAPSHOT.jar 
```
下面，我们可以继续编写流水线，创建项目的 **Dockerfile** 文件，
> Dockerfile的主要作用是用来构建镜像的
```bash
FROM registry.cn-shenzhen.aliyuncs.com/mogu-zh/jdk:8-mogu-alpine
ENV LANG C.UTF-8
ENV TZ Asia/Shanghai
VOLUME /tmp
ADD hello-mogu-0.0.1-SNAPSHOT.jar hello-mogu-0.0.1-SNAPSHOT.jar
ENTRYPOINT ["java","-Xms256m","-Xmx256m","-jar","/hello-mogu-0.0.1-SNAPSHOT.jar"]
```
存放位置如下所示，主要拉取了带着 jdk8 环境的镜像，然后设置启动参数
![编写Dockerfile](images/image-20220905090730480.png)
继续编写 .drone.yml 文件，这里除了需要拷贝  **jar** 文件外，还需要把刚刚写的 **Dockerfile** 文件也拷贝到宿主机上
同时，引入 **appleboy/drone-ssh** 镜像，听名字就可以知道，这个命令是用来远程 **SSH** 连接服务器的
这里有两个变量：**TEST_SERVER_IP** 和 **TEST_SERVER_PASSWORD**，分别是服务器的 **ip** 和 **密码**。为了防止信息泄露，我们需要配置到 **secret**
![新增秘钥](images/image-20220905092411935.png)
然后填写秘钥的名称和值，保存即可
![创建秘钥](images/image-20220905092444021.png)
配置完成后，一共包含以下两个值
![创建成功](images/image-20220905092552055.png)
完整的流水线代码如下：
```yml
kind: pipeline # 定义对象类型，还有secret和signature两种类型
type: docker # 定义流水线类型，还有kubernetes、exec、ssh等类型
name: hello-mogu # 定义流水线名称
steps: # 定义流水线执行步骤，这些步骤将顺序执行
  - name: build-package # 流水线名称
    image: maven:3.8.5-openjdk-8 # 定义创建容器的Docker镜像
    volumes: # 将容器内目录挂载到宿主机，仓库需要开启Trusted设置
      - name: maven-build
        path: /root/hello-mogu # 将应用打包好的Jar和执行脚本挂载出来
    commands:
      - mvn clean package -DskipTests=true
      # 将打包后的jar包，拷贝到挂载目录
      - cp /drone/src/target/hello-mogu-0.0.1-SNAPSHOT.jar  /root/hello-mogu
      # 将Dockerfile拷贝到挂载目录
      - cp /drone/src/target/classes/Dockerfile /root/hello-mogu
  - name: ssh
    image: appleboy/drone-ssh
    settings:
      # 你服务器ip地址
      host:
        from_secret: TEST_SERVER_IP
      # 服务器账号
      username: root
      # 密码登入写法
      password:
        from_secret: TEST_SERVER_PASSWORD
      port: 22
      script:
        - cd /root/hello-mogu
        - ls
        - docker build  -t hello-mogu:latest .
        - docker run -p 8080:8080 -d hello-mogu:latest
volumes: # 定义流水线挂载目录，用于共享数据
  - name: maven-build
    host:
      path: /root/hello-mogu   #jar包目录可以修改从宿主机中挂载的目录
```
核心操作就是：在 jar 打包完成后，会通过 ssh 进入到我们服务器中，通过 Dockerfile 构建我们的 **hello-mogu** 镜像，同时使用 **docker run** 启动镜像，完成最简单的一个流水线工作，以下是流水线运行成功的截图：
![构建成功](images/image-20220905093019633.png)
下面，我们去我们的服务器中，使用 docker images 命令，即可查看到制作完成的镜像了
![查看容器](images/image-20220905093042672.png)
通过使用  docker ps -a ，可以看到目前 hello-mogu 容器正在运行
![查看运行的容器](images/image-20220905093106325.png)
最后，我们访问服务器：http://81.70.100.87:8080/hello-mogu，久违的 **hello-mogu** 终于出现了
![hello mogu](images/image-20220905093233102.png)
同时，**Drone** 还提供了很多插件，可以打开 https://plugins.drone.io/  进行查看
![drone插件](images/image-20220905093521208.png)
在这里，可以下载别人做好的插件，例如在构建成功后，发送邮件通知，这里用到了  **Email** 插件
![Email插件](images/image-20220905093623288.png)
或者使用 Drone Cache 插件，将中间结果缓存到**云存储**中
![Drone缓存插件](images/image-20220905093731999.png)
好了，本期 **Drone** 学习之旅就到这里了，本文简单的介绍了一下 **Drone** 的接入流程，更多使用技巧欢迎到 Drone 官网学习~
最后，本次学习中所有的源码，陌溪也整理到了一个压缩包中，有需要的小伙伴可以在公众号回复【**drone**】获取
我是 **陌溪**，我们下期再见~
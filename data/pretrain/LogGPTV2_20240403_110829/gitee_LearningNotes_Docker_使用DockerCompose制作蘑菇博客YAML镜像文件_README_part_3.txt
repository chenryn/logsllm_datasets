构建完镜像后，我们使用下面命令，能够看到我们已经构建的业务镜像
```bash
docker images;
```
![image-20201125144121048](images/image-20201125144121048.png)
构建完镜像后，然后就可以执行docker-compose脚本，启动容器了
```bash
# 运行容器
sh run.sh
# 关闭容器
sh down.sh
```
`run.sh` 脚本内容如下所示 【可以根据配置修改启动的服务】
```bash
#!/usr/bin/env bash
echo '=====开始运行后台====='
cd docker-compose
echo '=====开始运行mogu_gateway====='
docker-compose -f mogu_gateway.yml up -d
echo '=====开始运行mogu_admin====='
docker-compose -f mogu_admin.yml up -d
echo '=====开始运行mogu_picture====='
docker-compose -f mogu_picture.yml up -d
echo '=====开始运行mogu_search====='
docker-compose -f mogu_search.yml up -d
echo '=====开始运行mogu_sms====='
docker-compose -f mogu_sms.yml up -d
echo '=====开始运行mogu_monitor====='
docker-compose -f mogu_monitor.yml up -d
echo '=====开始运行mogu_web====='
docker-compose -f mogu_web.yml up -d
echo '执行完成 日志目录mogu_blog_v2/log'
```
`down.sh` 脚本内容如下所示
```bash
#!/usr/bin/env bash
echo '=====结束运行====='
cd docker-compose
echo '=====结束运行mogu_gateway====='
docker-compose -f mogu_gateway.yml down
echo '=====结束运行mogu_admin====='
docker-compose -f mogu_admin.yml down
echo '=====结束运行mogu_picture====='
docker-compose -f mogu_picture.yml down
echo '=====结束运行mogu_search====='
docker-compose -f mogu_search.yml down
echo '=====结束运行mogu_sms====='
docker-compose -f mogu_sms.yml down
echo '=====结束运行mogu_monitor====='
docker-compose -f mogu_monitor.yml down
echo '=====结束运行mogu_web====='
docker-compose -f mogu_web.yml down
```
我们找到启动的一个脚本，以 `mogu_picture` 为例 【内部其实就是】
```yaml
version: '3'
services:
  #授权服务
  mogu_admin:
    image: moxi/mogu_admin:latest
    container_name: mogu_admin
    restart: always
    ports:
      - 8601:8601
    networks:
      - mogu
    environment:
      - COMPOSE_PROJECT_NAME=mogu_admin
    volumes:
      - ../log/:/logs/
networks:
  mogu:
    external: true
```
部署完成后，我们访问如下地址，即可查看swagger页面了
```bash
# mogu_admin
http://192.168.177.150:8601/swagger-ui/index.html
# mogu_picture
http://192.168.177.150:8602/swagger-ui/index.html
# mogu_web
http://192.168.177.150:8603/swagger-ui/index.html
```
## 部署蘑菇前台项目
首先我们需要安装好nodejs环境，在上面已经介绍了安装流程
### 依赖安装&打包
然后我们到 源码目录 mogu_blog_v2 目录下，执行vue构建和打包脚本【过程较慢，耐心等待】
```sh
sh vue_build.sh
```
`vue_build.sh` 的脚本内容如下所示：
```bash
#!/usr/bin/env bash
echo "=====开始构建前端项目====="
echo "=====开始npm install & npm run build vue_mogu_admin====="
echo "=====构建比较慢 请稍等====="
cd vue_mogu_admin
npm i node-sass --sass_binary_site=https://npm.taobao.org/mirrors/node-sass --unsafe-perm
npm install  --registry=https://registry.npm.taobao.org  --unsafe-perm
npm run build
cd ..
echo "=====开始npm install & npm run build vue_mogu_web====="
echo "=====构建比较慢 请稍等====="
cd vue_mogu_web
npm i node-sass --sass_binary_site=https://npm.taobao.org/mirrors/node-sass --unsafe-perm
npm install --registry=https://registry.npm.taobao.org  --unsafe-perm
npm run build
cd ..
```
### 制作vue_mogu_admin镜像
制作 vue_mogu_admin 镜像，首先我们需要准备一份 Dockerfile 文件【在vue_mogu_admin 目录下】
```bash
FROM registry.cn-shenzhen.aliyuncs.com/mogublog/nginx:latest
ADD ./dist/ /usr/share/nginx/html
RUN sed -i 's/\r$//' /usr/share/nginx/html/env.sh
RUN chmod +x /usr/share/nginx/html/env.sh
ENTRYPOINT ["/usr/share/nginx/html/env.sh"]
CMD ["nginx", "-g", "daemon off;"]
```
然后开始制作
```bash
docker build -t moxi/vue_mogu_admin .
```
### 制作vue_mogu_web镜像
制作 vue_mogu_admin 镜像，首先我们需要准备一份 Dockerfile 文件【在vue_mogu_admin 目录下】
```bash
FROM registry.cn-shenzhen.aliyuncs.com/mogublog/nginx:latest
ADD ./dist/ /usr/share/nginx/html
RUN sed -i 's/\r$//' /usr/share/nginx/html/env.sh
RUN chmod +x /usr/share/nginx/html/env.sh
ENTRYPOINT ["/usr/share/nginx/html/env.sh"]
CMD ["nginx", "-g", "daemon off;"]
```
然后开始制作
```bash
docker build -t moxi/vue_mogu_admin .
```
### 挂载前端配置
因为前端项目的配置，我们需要做到动态的变化，如何做到的，参考 Vue项目打包后动态配置解决方案
所以我们需要准备两个配置文件   config/vue_mogu_web.env 和 config/vue_mogu_admin.env ,这两个配置文件将在下面Docker compose 脚本中使用到
vue_mogu_web.env 文件内容如下
```bash
NODE_ENV=production
VUE_MOGU_WEB=http://192.168.1.101:9527
PICTURE_API=http://192.168.1.101:8602
WEB_API=http://192.168.1.101:8603
ELASTICSEARCH=http://192.168.1.101:8605
```
vue_mogu_admin.env 文件内容如下
```bash
WEB_API=http://192.168.1.101:8603
FILE_API=http://192.168.1.101:8600/
RABBIT_MQ_ADMIN=http://192.168.1.101:15672
SENTINEL_ADMIN=http://192.168.1.101:8070/sentinel/
EUREKA_API=http://192.168.1.101:8761
Search_API=http://192.168.1.101:8605
ADMIN_API=http://192.168.1.101:8601
Zipkin_Admin=http://192.168.1.101:9411/zipkin/
DRUID_ADMIN=http://192.168.1.101:8601/druid/login.html
SPRING_BOOT_ADMIN=http://192.168.1.101:8606/wallboard
BLOG_WEB_URL=http://192.168.1.101:9527
ELASTIC_SEARCH=http://192.168.1.101:5601
PICTURE_API=http://192.168.1.101:8602
SOLR_API=http://192.168.1.101:8080/solr
```
### 运行
然后开始运行前端的脚本
```bash
sh vue_run.sh
```
`vue_run.sh` 脚本内容如下所示：
```bash
#!/usr/bin/env bash
echo '=====开始运行前台====='
cd docker-compose
echo '=====开始运行mogu_gateway====='
docker-compose -f vue_mogu_admin.yml up -d
echo '=====开始运行mogu_admin====='
docker-compose -f vue_mogu_web.yml up -d
```
该脚本其实主要是执行了两个 docker-compose.yml 文件
`vue_mogu_admin.yml` 的内容如下
```bash
version: '3'
services:
  #授权服务
  vue_mogu_admin:
    image: registry.cn-shenzhen.aliyuncs.com/mogublog/vue_mogu_admin:latest
    container_name: vue_mogu_admin
    restart: always
    ports:
      - 9528:80
    networks:
      - mogu
    env_file:
      - ../config/vue_mogu_admin.env
    environment:
      - COMPOSE_PROJECT_NAME=vue_mogu_admin
networks:
  mogu:
    external: true
```
`vue_mogu_web.yml` 的内容如下
```yaml
version: '3'
services:
  #授权服务
  vue_mogu_web:
    image: registry.cn-shenzhen.aliyuncs.com/mogublog/vue_mogu_web:latest
    container_name: vue_mogu_web
    restart: always
    ports:
      - 9527:80
    networks:
      - mogu
    env_file:
      - ../config/vue_mogu_web.env
    environment:
      - COMPOSE_PROJECT_NAME=vue_mogu_web
networks:
  mogu:
    external: true
```
其实，制作的镜像里面就包含nginx，然后暴露80端口，映射到我们前端项目上
启动访问后，我们访问如下地址，即可看到我们部署好的前端页面了
```bash
# 前台页面
http://192.168.177.150:9527
# 后台页面
http://192.168.177.150:9528
```
## 部署Docker容器可视化管理工具
可以参考博客：[Docker图形化工具Portainer介绍与安装](http://www.moguit.cn/#/info?blogOid=570)
在我们完成上面的服务后，就可以部署可视化管理工具 portainer了
```bash
# 进入目录
cd docker-compose
# 创建配置文件
vim mogu_portainer.yml
```
然后添加如下内容
```bash
version: '3.1'
services:
  portainer:
    image: portainer/portainer
    container_name: portainer
    ports:
      - 9000:9000
      - 8000:8000
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./data:/data
      - ./public:/public
```
然后在执行汉化
```bash
# 下载汉化包
wget https://dl.quchao.net/Soft/Portainer-CN.zip
# 解压缩
unzip Portainer-CN.zip -d public
```
然后运行下面命令
```bash
docker-compose -f mogu_portainer.yml up -d
```
构建portainer容器后，我们访问下面页面
```bash
http://ip:9000
```
即可看到我们的图形化页面了【首次登录需要填写默认密码】
![image-20201125143917252](images/image-20201125143917252.png)
登录后，即可看到我们的容器信息
![image-20201125144030439](images/image-20201125144030439.png)
最后附上一张，蘑菇博客所有容器启动后的图片
![image-20201125202352995](images/image-20201125202352995.png)
到此为止，蘑菇博客的镜像改造已经结束了~，后面就可以使用制作好的镜像来完成我们 [蘑菇博客的一键部署](http://www.moguit.cn/#/info?blogOid=565) 咯
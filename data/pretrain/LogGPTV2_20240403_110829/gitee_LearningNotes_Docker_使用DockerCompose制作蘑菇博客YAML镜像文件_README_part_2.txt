        add_header Access-Control-Allow-Headers 'DNT,X-Mx-ReqToken,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization,lang,access-token';
        if ($request_method = 'OPTIONS') {
         return 204;
        }
        location / {
                root   /home/mogu_blog/mogu_data/;
                index  index.html index.htm;
        }
    }
```
### 部署zipkin & sentinel【可选】
然后我们执行下面的命令，完成 zipkin 和 sentinel 的安装，可以根据自己的情况选择是否安装
```bash
docker-compose -f docker-compose-extra.yml up -d
```
`docker-compose-extra.yml` 脚本内容如下所示
```yml
version: '3.1'
services:
  zipkin:
    image: openzipkin/zipkin
    container_name: zipkin
    environment:
      - STORAGE_TYPE=mysql
      - MYSQL_DB=zipkin
      - MYSQL_USER=root
      - MYSQL_PASS=root
      - MYSQL_HOST=mysql
      - MYSQL_TCP_PORT=3306
    ports:
      - 9411:9411
    networks:
      - mogu
  sentinel:
    image: registry.cn-shenzhen.aliyuncs.com/mogublog/sentinel
    restart: always
    container_name: sentinel
    ports:
      - 8070:8858
    networks:
      - mogu
networks:
  mogu:
    external: true
```
> 注意，这里我们使用的是  bladex/sentinel-dashboard 镜像，但是在使用的时候，发现还存在问题，就是服务无法正常注册到sentinel dashboard中，因此我和小伙伴后面尝试了自己构建一个 sentinel的镜像
#### 准备
首先我们需要准备可运行的  sentinel.jar，可以从官网下载
#### 编写Dockerfile
然后编写Dockerfile文件
```bash
FROM java:alpine
WORKDIR /usr/local/docker/sentinel
ADD ./sentinel.jar sentinel.jar
EXPOSE 8070
ENTRYPOINT ["java", "-jar", "sentinel.jar", "--server.port=8070"]
```
这里采用了基础镜像是 alpine提供的精简版环境，相比于其他的【openjdk】，能够大大减少容量
然后开始构建镜像【因为我需要上传到阿里云，所以使用了阿里云的镜像前缀】
```bash
docker build -t registry.cn-shenzhen.aliyuncs.com/mogublog/sentinel .
```
完成后，即可看到构建成功的镜像了【体积相对较少】
![image-20201206091428787](images/image-20201206091428787.png)
#### 启动
下面可以编写docker compose脚本如下
```bash
version: '3.1'
services:
  sentinel:
    image: registry.cn-shenzhen.aliyuncs.com/mogublog/sentinel
    restart: always
    container_name: sentinel
    ports:
      - 8070:8070
    networks:
      - mogu
networks:
  mogu:
    external: true
```
使用下面脚本运行
```bash
docker-compose -f docker-compose.yaml down
```
启动成功后，反问如下地址【输入 sentinel  sentinel】，即可看到我们的控制台
```bash
http://ip:8070
```
![image-20201206091653953](images/image-20201206091653953.png)
### 部署ELK【可选】
因为ElasticSearch的启动配置要求比较高，所以我们需要修改一些配置
```bash
# 到宿主机上打开文件
vim /etc/sysctl.conf
# 增加这样一条配置，一个进程在VMAs(虚拟内存区域)创建内存映射最大数量
vm.max_map_count=655360
# 让配置生效
sysctl -p
# 重启 docker，让内核参数对docker服务生效
systemctl restart docker
```
默认情况下，Elasticsearch 使用 uid:gid（1000:1000）作为容器内的运行用户，如果把数据和日志挂载到宿主机目录中，需要修改权限
```bash
chown -R 1000:1000 ./data/elasticsearch_data
chown -R 1000:1000 ./log/elk
```
然后开始部署ELK
```bash
cd elk && docker-compose up -d && cd ..
```
ELK：ElasticSearch + Logstash + Kibana
![image-20201129091936117](images/image-20201129091936117.png)
我们看到的外部docker-compose.yml 即为 ELK的配置
```yml
version: '3'
services:
  elk:
    image: sebp/elk:793
    container_name: elk
    restart: "always"
    ports:
      - "5601:5601"
      - "9200:9200"
      - "5044:5044"
      - "9300:9300"
    environment:
      - "ES_JAVA_OPTS=-Xms256m -Xmx256m"
      - "LS_HEAP_SIZE=128m"
    volumes:
      - ./elasticsearch/elasticsearch.yml:/etc/elasticsearch/elasticsearch.yml
      - ./elasticsearch/data:/var/lib/elasticsearch
      - ./elasticsearch/plugins:/opt/elasticsearch/plugins
      - ./elasticsearch/log:/var/log/elasticsearch
      - ./logstash/log:/var/log/logstash
      - ./logstash/patterns:/opt/logstash/patterns
      - ./logstash/conf:/etc/logstash/conf.d
      - ./kibana/kibana.yml:/opt/kibana/config/kibana.yml
    networks:
      - mogu
networks:
  mogu:
    external: true
```
elasticsearch.yaml 的配置如下所示
```yaml
node.name: elk
path.repo: /var/backups
network.host: 0.0.0.0
cluster.initial_master_nodes: ["elk"]
```
./logstash/conf 的配置如下
```yaml
input {
        beats {
                port => "5044"
        }
}
filter {
        mutate {
                split => {"message"=>"|"}
        }
        mutate {
                add_field => {
                "userId" => "%{[message][1]}"
                "visit" => "%{[message][2]}"
                "date" => "%{[message][3]}"
                }
        }
        mutate {
                convert => {
                "userId" => "integer"
                "visit" => "string"
                "date" => "string"
                }
        }
        mutate {
           remove_field => [ "host" ]
        }
}
#output {
# stdout { codec => rubydebug }
#}
output {
    if [from] == 'mogu_web' {
        elasticsearch {
          hosts => ["127.0.0.1:9200"]
          index => "logstash_mogu_web_%{+YYYY.MM.dd}"
        }
    }
    if [from] == "mogu_admin" {
        elasticsearch {
          hosts => ["127.0.0.1:9200"]
          index => "logstash_mogu_admin_%{+YYYY.MM.dd}"
        }
    }
    if [from] == "mogu_sms" {
        elasticsearch {
          hosts => ["127.0.0.1:9200"]
          index => "logstash_mogu_sms_%{+YYYY.MM.dd}"
        }
    }
    if [from] == "mogu_picture" {
        elasticsearch {
          hosts => ["127.0.0.1:9200"]
          index => "logstash_mogu_picture_%{+YYYY.MM.dd}"
        }
    }
    if [from] == "mogu_nginx" {
        elasticsearch {
          hosts => ["127.0.0.1:9200"]
          index => "logstash_mogu_nginx_%{+YYYY.MM.dd}"
        }
    }
}
```
kibana.yml 配置如下所示
```bash
server.host: "0.0.0.0"
i18n.locale: zh-CN
```
### 部署minio【可选】
文件上传选用minio可选
```bash
cd minio && docker-compose up -d && cd ..
```
minio.yml 配置信息如下
```yml
version: '3'
services:
  minio:
    image: minio/minio
    container_name: minio
    restart: "always"
    ports:
      - "9090:9000"
    environment:
      - "MINIO_ACCESS_KEY=mogu2018"
      - "MINIO_SECRET_KEY=mogu2018"
    command: server /data
    volumes:
      - ./minio:/data
    networks:
      - mogu
networks:
  mogu:
    external: true
```
## 部署蘑菇博客后台项目
在我们完成上述的环境搭建后，下面就可以开始部署我们的业务容器了，首先我们到我们的源码目录
```bash
# 下载依赖
mvn clean install
```
依赖安装完成后，然后执行镜像构建脚本
```bash
sh build_image.sh
```
`build_images.sh` 脚本内容如下所示：
```bash
#!/usr/bin/env bash
echo '=====开始mvn clean====='
mvn clean
echo '=====开始mvn install&&package====='
mvn install -DskipTests=true && mvn package -DskipTests=true
echo '=====开始构建镜像====='
echo '=====开始构建mogu_admin====='
cd mogu_admin
mvn docker:build
cd ..
echo '=====开始构建mogu_gateway====='
cd mogu_gateway
mvn docker:build
cd ..
echo '=====开始构建mogu_monitor====='
cd mogu_monitor
mvn docker:build
cd ..
echo '=====开始构建mogu_picture====='
cd mogu_picture
mvn docker:build
cd ..
echo '=====开始构建mogu_search====='
cd mogu_search
mvn docker:build
cd ..
echo '=====开始构建mogu_sms====='
cd mogu_sms
mvn docker:build
cd ..
echo '=====开始构建mogu_spider====='
cd mogu_spider
mvn docker:build
cd ..
echo '=====开始构建mogu_web====='
cd mogu_web
mvn docker:build
cd ..
echo '=====镜像构建结束====='
echo '=====删除镜像====='
docker rmi $(docker images | grep "none" | awk '{print $3}')
```
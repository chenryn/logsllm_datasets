  index.number_of_shards: 1
output.elasticsearch:
  hosts: ["127.0.0.1:9200"]
```
启动后，可以在 **Elasticsearch** 中看到索引以及查看数据
![image-20200924161739842](images/image-20200924161739842.png)
可以看到，在 **message** 中已经获取到了 **nginx** 的日志，但是，内容并没有经过处理，只是读取到原数据，那么对于我们后期的操作是不利的，有办法解决吗？
![收集的数据](images/image-20200924161814066.png)
### Module
前面要想实现日志数据的读取以及处理都是自己手动配置的，其实，在 **Filebeat** 中，有大量的 **Module**，可以简化我们的配置，直接就可以使用，如下：
```bash
./filebeat modules list
```
可以看到，内置了很多的 module，但是都没有启用，如果需要启用需要进行 **enable** 操作：
```bash
#启动
./filebeat modules enable nginx 
#禁用
./filebeat modules disable nginx 
```
可以发现，nginx的module已经被启用。
#### nginx module 配置
我们到下面的目录，就能看到module的配置了
```bash
# 进入到module目录
cd modules.d/
#查看文件
vim nginx.yml.disabled
```
得到的文件内容如下所示
```bash
# Module: nginx
# Docs: https://www.elastic.co/guide/en/beats/filebeat/7.9/filebeat-module-nginx.html
- module: nginx
  # Access logs
  access:
    enabled: true
    # 添加日志文件
    var.paths: ["/var/log/nginx/access.log*"]
    # Set custom paths for the log files. If left empty,
    # Filebeat will choose the paths depending on your OS.
    #var.paths:
  # Error logs
  error:
    enabled: true
    var.paths: ["/var/log/nginx/error.log*"]
```
#### 配置filebeat
我们需要修改刚刚的 **mogublog-nginx.yml** 文件，然后添加到我们的 **module**
```yml
filebeat.inputs:
setup.template.settings:
  index.number_of_shards: 1
output.elasticsearch:
  hosts: ["127.0.0.1:9200"]
filebeat.config.modules:
  path: ${path.config}/modules.d/*.yml
  reload.enabled: false
```
#### 测试
我们启动我们的 **filebeat**
```bash
./filebeat -e -c itcast-nginx.yml
```
如果启动的时候发现出错了，错误如下所示，执行如图所示的脚本即可 【新版本的ES好像不会出现这个错误】
```bash
#启动会出错，如下
ERROR fileset/factory.go:142 Error loading pipeline: Error loading pipeline for
fileset nginx/access: This module requires the following Elasticsearch plugins:
ingest-user-agent, ingest-geoip. You can install them by running the following
commands on all the Elasticsearch nodes:
  sudo bin/elasticsearch-plugin install ingest-user-agent
  sudo bin/elasticsearch-plugin install ingest-geoip
```
启动成功后，能看到日志记录已经成功刷新进去了
![](images/image-20200924164750123.png)
我们可以测试一下，刷新 **nginx** 页面，或者向错误日志中，插入数据
```bash
echo "err" >> error.log
```
能够看到，刚刚的记录已经成功插入了
![插入数据成功](images/image-20200924164927557.png)
关于module的其它使用，可以参考文档：
> 文档地址：
>
> https://www.elastic.co/guide/en/beats/filebeat/current/filebeat-modules.html
## Metricbeat
**Metricbeat** 是一个轻量性指标采集器，用于从系统和服务收集指标。**Metricbeat** 能够以一种轻量型的方式，输送各种系统和服务统计数据，从 **CPU** 到内存，从 **Redis** 到 **Nginx**，不一而足。
![什么是MetricBeat](images/image-20200924170741928.png)
- 定期收集操作系统或应用服务的指标数据
- 存储到 **Elasticsearch** 中，进行实时分析
### Metricbeat组成
**Metricbeat** 有2部分组成，一部分是 **Module**，另一个部分为 **Metricset**
- **Module**：收集的对象：如 **MySQL**、**Redis**、**Nginx**、操作系统等
- **Metricset**：收集指标的集合：如 **cpu**、**memory**，**network**等
以 **Redis Module**为例，我们查看一下它的组成结构如下所示：
![Metricbeat组成](images/image-20200924170958343.png)
### 下载
首先我们到官网，找到 **Metricbeat** 进行下载
> 下载地址：
>
> https://www.elastic.co/cn/downloads/beats/metricbeat
![下载](images/image-20200924171232384.png)
下载完成后，我们通过xftp工具，移动到指定的目录下
```bash
# 移动到该目录下
cd /soft/beats
# 解压文件
tar -zxvf 
# 修改文件名
mv  metricbeat
```
然后修改配置文件
```bash
vim metricbeat.yml
```
添加如下内容
```yml
metricbeat.config.modules:
  path: ${path.config}/modules.d/*.yml
  reload.enabled: false
setup.template.settings:
  index.number_of_shards: 1
  index.codec: best_compression
setup.kibana:
output.elasticsearch:
  hosts: [""127.0.0.1:9200"]
processors:
  - add_host_metadata: ~
  - add_cloud_metadata: ~
```
默认会指定的配置文件，就是在
```bash
${path.config}/modules.d/*.yml
```
也就是 **system.yml** 文件，我们也可以自行开启其它的收集
### 启动
在配置完成后，我们通过如下命令启动即可
```bash
./metricbeat -e
```
在 **ELasticsearch** 中可以看到，系统的一些指标数据已经写入进去了：
![指标写入成功](images/image-20200924171839291.png)
### system module配置
```yml
- module: system
  period: 10s  # 采集的频率，每10秒采集一次
  metricsets:  # 采集的内容
    - cpu
    - load
    - memory
    - network
    - process
    - process_summary
```
### Metricbeat Module
Metricbeat Module的用法和我们之前学的filebeat的用法差不多
```bash
#查看列表
./metricbeat modules list 
```
### Nginx Module
#### 开启Nginx Module
在 **nginx** 中，需要开启状态查询，才能查询到指标数据。
```bash
#重新编译nginx
./configure --prefix=/usr/local/nginx --with-http_stub_status_module
make
make install
./nginx -V #查询版本信息
nginx version: nginx/1.11.6
built by gcc 4.4.7 20120313 (Red Hat 4.4.7-23) (GCC)
configure arguments: --prefix=/usr/local/nginx --with-http_stub_status_module
#配置nginx
vim nginx.conf
location /nginx-status {
    stub_status on;
    access_log off;
}
# 重启nginx
./nginx -s reload
```
重启完成后，进行测试
![](images/image-20200924172317526.png)
结果说明：
- **Active connections**：正在处理的活动连接数
- server accepts handled requests
  - 第一个 server 表示Nginx启动到现在共处理了9个连接
  - 第二个 accepts 表示Nginx启动到现在共成功创建 9 次握手
  - 第三个 handled requests 表示总共处理了 21 次请求
  - 请求丢失数 = 握手数 - 连接数 ，可以看出目前为止没有丢失请求
- Reading: 0 Writing: 1 Waiting: 1
  - Reading：Nginx 读取到客户端的 Header 信息数
  - Writing：Nginx 返回给客户端 Header 信息数
  - Waiting：Nginx 已经处理完正在等候下一次请求指令的驻留链接（开启keep-alive的情况下，这个值等于
    Active - (Reading+Writing)）
### 配置nginx module
```bash
#启用redis module
./metricbeat modules enable nginx
#修改redis module配置
vim modules.d/nginx.yml
```
然后修改下面的信息
```bash
# Module: nginx
# Docs: https://www.elastic.co/guide/en/beats/metricbeat/6.5/metricbeat-modulenginx.
html
  - module: nginx
#metricsets:
# - stubstatus
  period: 10s
# Nginx hosts
  hosts: ["http://127.0.0.1"]
# Path to server status. Default server-status
  server_status_path: "nginx-status"
#username: "user"
#password: "secret"
```
修改完成后，启动 **nginx**
```bash
#启动
./metricbeat -e
```
### 测试
我们能看到，我们的 **nginx** 数据已经成功的采集到我们的系统中了
![收集nginx数据](images/image-20200924173058267.png)
## 参考
-  [Filebeat 模块与配置](https://www.cnblogs.com/cjsblog/p/9495024.html)
- [Elastic Stack（ELK）从入门到实践](https://www.bilibili.com/video/BV1iJ411c7Az)
## 结语
**陌溪**是一个从三本院校一路摸滚翻爬上来的互联网大厂程序员。独立做过几个开源项目，其中**蘑菇博客**在码云上有 **2K Star** 。目前就职于**字节跳动的Data广告部门**，是字节跳动全线产品的商业变现研发团队。本公众号将会持续性的输出很多原创小知识以及学习资源。如果你觉得本文对你有所帮助，麻烦给文章点个“赞”和“在看”。
同时，因为本公众号**申请较晚**，暂时没有开通**留言**功能，欢迎小伙伴们添加我的私人微信【备注：**加群**】，我将邀请你加入到**蘑菇博客交流群**中，欢迎小伙伴们找陌溪一块聊天唠嗑，共同学习进步。
![img](https://gitee.com/moxi159753/LearningNotes/raw/master/doc/images/qq/%E6%B7%BB%E5%8A%A0%E9%99%8C%E6%BA%AA.png)
> 大家好，我是陌溪，欢迎点击下方的公众号名片，关注陌溪，让我们一起成长~
上篇我们讲解了 **ElasticStack** 技术栈中 [ElasticSearch的使用](https://mp.weixin.qq.com/s/9eh6rK2aZHRiBpf5bRae9g)，这次给大家带来的是 **ElasticStack** 技术栈中日志采集器 **Beats** 的使用。
## Beats简介
通过查看 **ElasticStack** 可以发现，**Beats** 主要用于采集数据
> 官网地址：https://www.elastic.co/cn/beats/
![ElasticStack组成](images/image-20200924091657242.png)
**Beats** 平台其实是一个轻量性数据采集器，通过集合多种单一用途的采集器，从成百上千台机器中向 **Logstash** 或 **ElasticSearch** 中发送数据。
![Beats-轻量级数据采集器](images/image-20200924091716757.png)
通过 **Beats** 包含以下的数据采集功能
- **Filebeat**：采集日志文件
- **Metricbeat**：采集指标
- **Packetbeat**：采集网络数据
![Beats全家桶](images/image-20200924092015934.png)
如果使用 **Beats** 收集的数据不需要任何处理，那么就可以直接发送到 **ElasticSearch** 中。但是，如果们的数据需要经过一些处理的话，那么就可以发送到 **Logstash** 中，然后处理完成后，在发送到 **ElasticSearch**，最后在通过 **Kibana** 对我们的数据进行一系列的可视化展示。
![](images/image-20200924092348121.png)
## Filebeat使用
### 介绍
**Filebeat** 是一个轻量级的日志采集器
![FileBeats](images/image-20200924092551044.png)
### 为什么要用Filebeat？
当你面对成百上千、甚至成千上万的服务器、虚拟机和容器生成的日志时，请告别SSH吧！**Filebeat** 将为你提供一种轻量型方法，用于转发和汇总日志与文件，让简单的事情不再繁华，关于 **Filebeat** 的记住以下两点：
- 轻量级日志采集器
- 输送至 **ElasticSearch** 或者 **Logstash**，在 **Kibana** 中实现可视化
### 架构
用于监控、收集服务器日志文件
![FileBeats架构图](images/image-20200924092749077.png)
流程如下：
- 首先是 **input** 输入，我们可以指定多个数据输入源，然后通过通配符进行日志文件的匹配
- 匹配到日志后，就会使用 **Harvester**（收割机），将日志源源不断的读取到来
- 然后收割机收割到的日志，就传递到 **Spooler**（卷轴），然后卷轴就在将他们传到对应的地方
### 下载
> 官网下载地址：
>
> https://www.elastic.co/cn/downloads/beats/filebeat
选中对应版本的 **Filebeat**，我这里是 **Centos** 部署的，所以下载 **Linux** 版本
![下载](images/image-20200924093459418.png)
下载后，上传到 **CentOS** 服务器上，然后创建一个文件夹
```bash
# 创建文件夹
mkdir -p /soft/beats
# 解压文件
tar -zxvf filebeat-7.9.1-linux-x86_64.tar.gz 
# 重命名
mv filebeat-7.9.1-linux-x86_64/ filebeat
```
然后我们进入到 **filebeat** 目录下，创建对应的配置文件
```bash
# 进入文件夹
cd filebeats
# 创建配置文件
vim mogublog.yml
```
添加如下内容
```yml
filebeat.inputs: # filebeat input输入
- type: stdin    # 标准输入
  enabled: true  # 启用标准输入
setup.template.settings: 
  index.number_of_shards: 3 # 指定下载数
output.console:  # 控制台输出
  pretty: true   # 启用美化功能
  enable: true
```
### 启动
在我们添加完配置文件后，我们就可以对 **filebeat** 进行启动了
```bash
./filebeat -e -c mogublog.yml
```
![启动FileBeats](images/image-20200924094825962.png)
然后我们在控制台输入 **hello**，就能看到我们会有一个 **json** 的输出，是通过读取到我们控制台的内容后输出的
![](images/image-20200924095032365.png)
内容如下
```json
{
    "@timestamp":"2019-01-12T12:50:03.585Z",
    "@metadata":{ #元数据信息
        "beat":"filebeat",
        "type":"doc",
        "version":"6.5.4"
    },
    "source":"",
    "offset":0,
    "message":"hello", #元数据信息
    "prospector":{
        "type":"stdin" #元数据信息
    },
    "input":{ #控制台标准输入
        "type":"stdin"
    },
    "beat":{  #beat版本以及主机信息
        "name":"itcast01",
        "hostname":"ElasticStack",
        "version":"6.5.4"
    },
    "host":{
        "name":"ElasticStack"
    }
}
```
### 读取文件
我们需要再次创建一个文件，叫 **mogublog-log.yml**，然后在文件里添加如下内容
```yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /soft/beats/logs/*.log
setup.template.settings:
  index.number_of_shards: 3
output.console:
  pretty: true
  enable: true
```
添加完成后，我们在到下面目录创建一个日志文件
```bash
# 创建文件夹
mkdir -p /soft/beats/logs
# 进入文件夹
cd /soft/beats/logs
# 追加内容
echo "hello" >> a.log
```
然后我们再次启动 **filebeat**
```bash
 ./filebeat -e -c mogublog-log.yml
```
能够发现，它已经成功加载到了我们的日志文件 **a.log**
![](images/image-20200924095926036.png)
同时我们还可以继续往文件中追加内容
```bash
echo "are you ok ?" >> a.log
```
追加后，我们再次查看filebeat，也能看到刚刚我们追加的内容
![](images/image-20200924102409656.png)
可以看出，已经检测到日志文件有更新，立刻就会读取到更新的内容，并且输出到控制台。
### 自定义字段
但我们的元数据没办法支撑我们的业务时，我们还可以自定义添加一些字段
```bash
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /soft/beats/logs/*.log
  tags: ["web", "test"]  #添加自定义tag，便于后续的处理
  fields:  #添加自定义字段
    from: test-web
  fields_under_root: true #true为添加到根节点，false为添加到子节点中
setup.template.settings:
  index.number_of_shards: 3
output.console:
  pretty: true
  enable: true
```
添加完成后，我们重启 **filebeat**
```bash
./filebeat -e -c mogublog-log.yml
```
然后添加新的数据到 **a.log** 中
```bash
echo "test-web" >> a.log
```
我们就可以看到字段在原来的基础上，增加了两个
![](images/image-20200924103323033.png)
### 输出到ElasticSearch
我们可以通过配置，将修改成如下所示
```yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /soft/beats/logs/*.log
  tags: ["web", "test"]
  fields:
    from: test-web
  fields_under_root: false 
setup.template.settings:
  index.number_of_shards: 1
output.elasticsearch:
  hosts: ["127.0.0.1:9200"]
```
启动成功后，我们就能看到它已经成功连接到了 **ElasticSearch** 了
![](images/image-20200924145624812.png)
然后我们到刚刚的 **logs** 文件夹向 **a.log** 文件中添加内容
```bash
echo "hello mogublog" >> a.log
```
在 **ElasticSearch** 中，我们可以看到，多出了一个 **filebeat** 的索引库
![查看索引库](images/image-20200924145928050.png)
然后我们浏览对应的数据，看看是否有插入的数据内容
![数据插入成功](images/image-20200924150500441.png)
### Filebeat工作原理
Filebeat主要由下面几个组件组成： **harvester**、**prospector** 、**input**
#### harvester
- 负责读取单个文件的内容
- **harvester** 逐行读取每个文件（一行一行读取），并把这些内容发送到输出
- 每个文件启动一个 **harvester**，并且 **harvester** 负责打开和关闭这些文件，这就意味着 **harvester** 运行时文件描述符保持着打开的状态。
- 在 **harvester** 正在读取文件内容的时候，文件被删除或者重命名了，那么 **Filebeat** 就会续读这个文件，这就会造成一个问题，就是只要负责这个文件的 **harvester** 没用关闭，那么磁盘空间就不会被释放。
#### prospector
- **prospector** 负责管理 **harvester** 并找到所有要读取的文件来源
- 如果输入类型为日志，则查找器将查找路径匹配的所有文件，并为每个文件启动一个 **harvester**
- **Filebeat** 目前支持两种 **prospector** 类型：**log** 和 **stdin**
- **Filebeat** 如何保持文件的状态
  - **Filebeat** 保存每个文件的状态并经常将状态刷新到磁盘上的注册文件中
  - 该状态用于记住 **harvester** 正在读取的最后偏移量，并确保发送所有日志行。
  - 如果输出（例如 **ElasticSearch** 或 **Logstash** ）无法访问，**Filebeat** 会跟踪最后发送的行，并在输出再次可以用时继续读取文件。
  - 在 **Filebeat** 运行时，每个 **prospector** 内存中也会保存的文件状态信息，当重新启动 **Filebat** 时，将使用注册文件的数量来重建文件状态，Filebeat将每个harvester在从保存的最后偏移量继续读取
  - 文件状态记录在data/registry文件中
### input
- 一个 **input** 负责管理 **harvester**，并找到所有要读取的源
- 如果 **input** 类型是 **log**，则 **input** 查找驱动器上与已定义的 **glob** 路径匹配的所有文件，并为每个文件启动一个 **harvester**
- 每个 **input** 都在自己的 **Go** 例程中运行
- 下面的例子配置Filebeat从所有匹配指定的glob模式的文件中读取行
```yml
filebeat.inputs:
- type: log
  paths:
    - /var/log/*.log
    - /var/path2/*.log
```
### 启动命令
```bash
./filebeat -e -c mogublog-es.yml
./filebeat -e -c mogublog-es.yml -d "publish"
```
### 参数说明
- **-e：**输出到标准输出，默认输出到syslog和logs下
- **-c：**指定配置文件
- **-d：**输出debug信息
### 读取Nginx中的配置文件
我们需要创建一个 **mogublog-nginx.yml** 配置文件
```yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /soft/nginx/*.log
  tags: ["nginx"]
  fields_under_root: false 
setup.template.settings:
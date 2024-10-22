```
相似度应该多少合适，需要在实际的需求中进行反复测试，才可得到合理的值。
### 组合搜索
在搜索时，也可以使用过滤器中讲过的bool组合查询，示例：
```bash
POST /itcast/person/_search
{
    "query":{
        "bool":{
            "must":{
                "match":{
                    "hobby":"篮球"
                }
            },
            "must_not":{
                "match":{
                    "hobby":"音乐"
                }
            },
            "should":[
                {
                    "match":{
                        "hobby":"游泳"
                    }
                }
            ]
        }
    },
    "highlight":{
        "fields":{
            "hobby":{
            }
        }
    }
}
```
>上面搜索的意思是：
>搜索结果中必须包含篮球，不能包含音乐，如果包含了游泳，那么它的相似度更高。
结果：
![image-20200923145310698](images/image-20200923145310698.png)
>评分的计算规则
>
>bool 查询会为每个文档计算相关度评分 _score ， 再将所有匹配的 must 和 should 语句的分数 _score 求和，最后除以 must 和 should 语句的总数。
>
>must_not 语句不会影响评分； 它的作用只是将不相关的文档排除。
默认情况下，should中的内容不是必须匹配的，如果查询语句中没有must，那么就会至少匹配其中一个。当然了，也可以通过minimum_should_match参数进行控制，该值可以是数字也可以的百分比。
示例：
```bash
POST /itcast/person/_search
{
    "query":{
        "bool":{
            "should":[
                {
                    "match":{
                        "hobby":"游泳"
                    }
                },
                {
                    "match":{
                        "hobby":"篮球"
                    }
                },
                {
                    "match":{
                        "hobby":"音乐"
                    }
                }
            ],
            "minimum_should_match":2
        }
    },
    "highlight":{
        "fields":{
            "hobby":{
            }
        }
    }
}
```
minimum_should_match为2，意思是should中的三个词，至少要满足2个。
### 权重
有些时候，我们可能需要对某些词增加权重来影响该条数据的得分。如下：
搜索关键字为“游泳篮球”，如果结果中包含了“音乐”权重为10，包含了“跑步”权重为2。
```bash
POST /itcast/person/_search
{
    "query":{
        "bool":{
            "must":{
                "match":{
                    "hobby":{
                        "query":"游泳篮球",
                        "operator":"and"
                    }
                }
            },
            "should":[
                {
                    "match":{
                        "hobby":{
                            "query":"音乐",
                            "boost":10
                        }
                    }
                },
                {
                    "match":{
                        "hobby":{
                            "query":"跑步",
                            "boost":2
                        }
                    }
                }
            ]
        }
    },
    "highlight":{
        "fields":{
            "hobby":{
            }
        }
    }
}
```
## ElasticSearch集群
### 集群节点
ELasticsearch的集群是由多个节点组成的，通过cluster.name设置集群名称，并且用于区分其它的集群，每个节点通过node.name指定节点的名称。
在Elasticsearch中，节点的类型主要有4种：
- master节点
  - 配置文件中node.master属性为true(默认为true)，就有资格被选为master节点。master节点用于控制整个集群的操作。比如创建或删除索引，管理其它非master节点等。
- data节点
  - 配置文件中node.data属性为true(默认为true)，就有资格被设置成data节点。data节点主要用于执行数据相关的操作。比如文档的CRUD。
- 客户端节点
  - 配置文件中node.master属性和node.data属性均为false。
  - 该节点不能作为master节点，也不能作为data节点。
  - 可以作为客户端节点，用于响应用户的请求，把请求转发到其他节点
- 部落节点
  - 当一个节点配置tribe.*的时候，它是一个特殊的客户端，它可以连接多个集群，在所有连接的集群上执行
    搜索和其他操作。
### 搭建集群
```bash
#启动3个虚拟机，分别在3台虚拟机上部署安装Elasticsearch
mkdir /itcast/es-cluster
#分发到其它机器
scp -r es-cluster PI:EMAIL:/itcast
#node01的配置：
cluster.name: es-itcast-cluster
node.name: node01
node.master: true
node.data: true
network.host: 0.0.0.0
http.port: 9200
discovery.zen.ping.unicast.hosts: ["192.168.40.133","192.168.40.134","192.168.40.135"]
# 最小节点数
discovery.zen.minimum_master_nodes: 2
# 跨域专用
http.cors.enabled: true
http.cors.allow-origin: "*"
#node02的配置：
cluster.name: es-itcast-cluster
node.name: node02
node.master: true
node.data: true
network.host: 0.0.0.0
http.port: 9200
discovery.zen.ping.unicast.hosts: ["192.168.40.133","192.168.40.134","192.168.40.135"]
discovery.zen.minimum_master_nodes: 2
http.cors.enabled: true
http.cors.allow-origin: "*"
#node03的配置：
cluster.name: es-itcast-cluster
node.name: node02
node.master: true
node.data: true
network.host: 0.0.0.0
http.port: 9200
discovery.zen.ping.unicast.hosts: ["192.168.40.133","192.168.40.134","192.168.40.135"]
discovery.zen.minimum_master_nodes: 2
http.cors.enabled: true
http.cors.allow-origin: "*"
#分别启动3个节点
./elasticsearch
```
查看集群
![image-20200923151823672](images/image-20200923151823672.png)
创建索引：
![image-20200923151851785](images/image-20200923151851785.png)
![image-20200923151935283](images/image-20200923151935283.png)
查询集群状态：/_cluster/health
响应：
![image-20200923151953227](images/image-20200923151953227.png)
集群中有三种颜色
![image-20200923152005930](images/image-20200923152005930.png)
### 分片和副本
为了将数据添加到Elasticsearch，我们需要索引(index)——一个存储关联数据的地方。实际上，索引只是一个用来指向一个或多个分片(shards)的“逻辑命名空间(logical namespace)”.
- 一个分片(shard)是一个最小级别“工作单元(worker unit)”,它只是保存了索引中所有数据的一部分。
- 我们需要知道是分片就是一个Lucene实例，并且它本身就是一个完整的搜索引擎。应用程序不会和它直接通
  信。
- 分片可以是主分片(primary shard)或者是复制分片(replica shard)。
- 索引中的每个文档属于一个单独的主分片，所以主分片的数量决定了索引最多能存储多少数据。
- 复制分片只是主分片的一个副本，它可以防止硬件故障导致的数据丢失，同时可以提供读请求，比如搜索或者从别的shard取回文档。
- 当索引创建完成的时候，主分片的数量就固定了，但是复制分片的数量可以随时调整。
### 故障转移
#### 将data节点停止
这里选择将node02停止：
![image-20200923152229908](images/image-20200923152229908.png)
当前集群状态为黄色，表示主节点可用，副本节点不完全可用，过一段时间观察，发现节点列表中看不到node02，副本节点分配到了node01和node03，集群状态恢复到绿色。
![image-20200923152248547](images/image-20200923152248547.png)
将node02恢复： ./node02/1 bin/elasticsearch
![image-20200923152328458](images/image-20200923152328458.png)
可以看到，node02恢复后，重新加入了集群，并且重新分配了节点信息。
#### 将master节点停止
接下来，测试将node01停止，也就是将主节点停止。
![image-20200923152415890](images/image-20200923152415890.png)
从结果中可以看出，集群对master进行了重新选举，选择node03为master。并且集群状态变成黄色。
等待一段时间后，集群状态从黄色变为了绿色：
![image-20200923153343555](images/image-20200923153343555.png)
恢复node01节点：
```bash
./node01/1 bin/elasticsearch
```
重启之后，发现node01可以正常加入到集群中，集群状态依然为绿色：
![image-20200923153415117](images/image-20200923153415117.png)
特别说明：
如果在配置文件中discovery.zen.minimum_master_nodes设置的不是N/2+1时，会出现脑裂问题，之前宕机
的主节点恢复后不会加入到集群。
![image-20200923153441693](images/image-20200923153441693.png)
### 分布式文档
#### 路由
首先，来看个问题：
![image-20200923153556720](images/image-20200923153556720.png)
如图所示：当我们想一个集群保存文档时，文档该存储到哪个节点呢？ 是随机吗？ 是轮询吗？实际上，在ELasticsearch中，会采用计算的方式来确定存储到哪个节点，计算公式如下：
```bash
shard = hash(routing) % number_1 of_primary_shards
```
其中：
- routing值是一个任意字符串，它默认是_id但也可以自定义。
- 这个routing字符串通过哈希函数生成一个数字，然后除以主切片的数量得到一个余数(remainder)，余数
  的范围永远是0到number_of_primary_shards - 1，这个数字就是特定文档所在的分片
这就是为什么创建了主分片后，不能修改的原因。
#### 文档的写操作
新建、索引和删除请求都是写（write）操作，它们必须在主分片上成功完成才能复制分片上
![image-20200923155314424](images/image-20200923155314424.png)
下面我们罗列在主分片和复制分片上成功新建、索引或删除一个文档必要的顺序步骤：
1. 客户端给Node 1 发送新建、索引或删除请求。
2. 节点使用文档的_id 确定文档属于分片0 。它转发请求到Node 3 ，分片0 位于这个节点上。
3. Node 3 在主分片上执行请求，如果成功，它转发请求到相应的位于Node 1 和Node 2 的复制节点上。当所有
的复制节点报告成功， Node 3 报告成功到请求的节点，请求的节点再报告给客户端。
客户端接收到成功响应的时候，文档的修改已经被应用于主分片和所有的复制分片。你的修改生效了。
### 搜索文档
文档能够从主分片或任意一个复制分片被检索。
![image-20200923160046962](images/image-20200923160046962.png)
下面我们罗列在主分片或复制分片上检索一个文档必要的顺序步骤：
1. 客户端给Node 1 发送get请求。
2. 节点使用文档的_id 确定文档属于分片0 。分片0 对应的复制分片在三个节点上都有。此时，它转发请求到
Node 2 。
3. Node 2 返回文档(document)给Node 1 然后返回给客户端。对于读请求，为了平衡负载，请求节点会为每个请求选择不同的分片——它会循环所有分片副本。可能的情况是，一个被索引的文档已经存在于主分片上却还没来得及同步到复制分片上。这时复制分片会报告文档未找到，主分片会成功返回文档。一旦索引请求成功返回给用户，文档则在主分片和复制分片都是可用的。
### 全文搜索
对于全文搜索而言，文档可能分散在各个节点上，那么在分布式的情况下，如何搜索文档呢？
搜索，分为2个阶段，
- 搜索（query）
- 取回（fetch）
#### 搜索（query）
![image-20200923161323235](images/image-20200923161323235.png)
查询阶段包含以下三步：
1. 客户端发送一个search（搜索） 请求给Node 3 , Node 3 创建了一个长度为from+size 的空优先级队
2. Node 3 转发这个搜索请求到索引中每个分片的原本或副本。每个分片在本地执行这个查询并且结果将结果到
一个大小为from+size 的有序本地优先队列里去。
3. 每个分片返回document的ID和它优先队列里的所有document的排序值给协调节点Node 3 。Node 3 把这些
值合并到自己的优先队列里产生全局排序结果。
#### 取回 fetch
![image-20200923161447618](images/image-20200923161447618.png)
分发阶段由以下步骤构成：
1. 协调节点辨别出哪个document需要取回，并且向相关分片发出GET 请求。
2. 每个分片加载document并且根据需要丰富（enrich）它们，然后再将document返回协调节点。
3. 一旦所有的document都被取回，协调节点会将结果返回给客户端。
## Java客户端
在Elasticsearch中，为java提供了2种客户端，一种是REST风格的客户端，另一种是Java API的客户端
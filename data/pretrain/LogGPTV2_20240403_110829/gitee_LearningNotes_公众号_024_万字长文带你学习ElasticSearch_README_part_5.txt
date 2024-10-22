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
> 上面搜索的意思是： 搜索结果中必须包含篮球，不能包含音乐，如果包含了游泳，那么它的相似度更高。
结果：
![](http://image.moguit.cn/06cbf0d78599403186508e6a82d1b3d7)
> 评分的计算规则
> 
> bool 查询会为每个文档计算相关度评分 \_score ， 再将所有匹配的 must 和 should 语句的分数 \_score 求和，最后除以 must 和 should 语句的总数。
> 
> must\_not 语句不会影响评分； 它的作用只是将不相关的文档排除。
默认情况下，**should** 中的内容不是必须匹配的，如果查询语句中没有must，那么就会至少匹配其中一个。当然了，也可以通过minimum\_should\_match参数进行控制，该值可以是数字也可以的百分比。示例：
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
minimum\_should\_match为2，意思是should中的三个词，至少要满足2个。
### 权重
有些时候，我们可能需要对某些词增加权重来影响该条数据的得分。如下：
搜索关键字为“游泳篮球”，如果结果中包含了“音乐”权重为10，包含了“跑步”权重为2。
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
ElasticSearch集群
---------------
### 集群节点
ELasticsearch的集群是由多个节点组成的，通过cluster.name设置集群名称，并且用于区分其它的集群，每个节点通过node.name指定节点的名称。
在Elasticsearch中，节点的类型主要有4种：
*   master节点
    *   配置文件中node.master属性为true(默认为true)，就有资格被选为master节点。master节点用于控制整个集群的操作。比如创建或删除索引，管理其它非master节点等。
*   data节点
    *   配置文件中node.data属性为true(默认为true)，就有资格被设置成data节点。data节点主要用于执行数据相关的操作。比如文档的CRUD。
*   客户端节点
    *   配置文件中node.master属性和node.data属性均为false。
    *   该节点不能作为master节点，也不能作为data节点。
    *   可以作为客户端节点，用于响应用户的请求，把请求转发到其他节点
*   部落节点
    *   当一个节点配置tribe.\*的时候，它是一个特殊的客户端，它可以连接多个集群，在所有连接的集群上执行 搜索和其他操作。
### 搭建集群
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
查看集群
![](http://image.moguit.cn/19c11f641a8241eeb0f0523443ae439c)
创建索引：
![](http://image.moguit.cn/1603c680619940d195d55c778abe02e1)
![](http://image.moguit.cn/f4eb83efa57f4d53bc92b2ec70c85390)
查询集群状态：/\_cluster/health 响应：
![](http://image.moguit.cn/8e0db68354704750a4e08ccd088f2e86)
集群中有三种颜色
![](http://image.moguit.cn/6656a5134ac74a1a948b87c2f627c691)
### 分片和副本
为了将数据添加到 **Elasticsearch**，我们需要索引(**index**)——一个存储关联数据的地方。实际上，索引只是一个用来指向一个或多个分片(**shards**)的 逻辑命名空间 (logical namespace).
*   一个分片(**shard**)是一个最小级别“工作单元(**worker unit**)，它只是保存了索引中所有数据的一部分。
*   我们需要知道是分片就是一个Lucene实例，并且它本身就是一个完整的搜索引擎。应用程序不会和它直接通 信。
*   分片可以是主分片(**primary shard**)或者是复制分片(**replica shard**)。
*   索引中的每个文档属于一个单独的主分片，所以主分片的数量决定了索引最多能存储多少数据。
*   复制分片只是主分片的一个副本，它可以防止硬件故障导致的数据丢失，同时可以提供读请求，比如搜索或者从别的 **shard** 取回文档。
*   当索引创建完成的时候，主分片的数量就固定了，但是复制分片的数量可以随时调整。
### 故障转移
#### 将data节点停止
这里选择将 **node02** 停止：
![](http://image.moguit.cn/ac4de8c4cba14cc09d2d0ffa2499dfcf)
当前集群状态为黄色，表示主节点可用，副本节点不完全可用，过一段时间观察，发现节点列表中看不到node02，副本节点分配到了 **node01** 和 **node03**，集群状态恢复到绿色。
![](http://image.moguit.cn/c4aeb71743bb42d38aef0af7e2f2f655)
将 **node02** 恢复
![](http://image.moguit.cn/33a3c0d1fdbe4f24a1cff406a4f7d60d)
可以看到，node02恢复后，重新加入了集群，并且重新分配了节点信息。
#### 将master节点停止
接下来，测试将 **node01** 停止，也就是将主节点停止。
![](http://image.moguit.cn/72716d4033ae4d9f837a6f472a139c79)
从结果中可以看出，集群对 **master** 进行了重新选举，选择 **node03** 为 **master** 。并且集群状态变成黄色。 等待一段时间后，集群状态从黄色变为了绿色：
![image-20200923153343555](http://image.moguit.cn/c8a20692dafd48f0a76cbb756df06659)
恢复 **node01** 节点：
    ./node01/1 bin/elasticsearch
重启之后，发现 **node01** 可以正常加入到集群中，集群状态依然为绿色：
![image-20200923153415117](http://image.moguit.cn/584aabd78d7e483abb23a8728a923096)
特别说明：如果在配置文件中 **discovery.zen.minimum\_master\_nodes** 设置的不是 **N/2+1** 时，会出现脑裂问题，之前宕机 的主节点恢复后不会加入到集群。
![image-20200923153441693](http://image.moguit.cn/4bfa555211754fab937049cd4c5a679b)
### 分布式文档
#### 路由
首先，来看个问题：
![](http://image.moguit.cn/87ce25edea05452eacd0f40238f1ccc5)
如图所示：当我们想一个集群保存文档时，文档该存储到哪个节点呢？ 是随机吗？ 是轮询吗？实际上，在**ELasticsearch** 中，会采用计算的方式来确定存储到哪个节点，计算公式如下：
    shard = hash(routing) % number_1 of_primary_shards
其中：
*   **routing** 值是一个任意字符串，它默认是 **\_id** 但也可以自定义。
*   这个 **routing** 字符串通过哈希函数生成一个数字，然后除以主切片的数量得到一个余数(remainder)，余数 的范围永远是0到 **number\_of\_primary\_shards - 1**，这个数字就是特定文档所在的分片
这就是为什么创建了主分片后，不能修改的原因。
#### 文档的写操作
新建、索引和删除请求都是写（**write**）操作，它们必须在主分片上成功完成才能复制分片上
![](http://image.moguit.cn/82de794014654dec9bebea62ec433756)
下面我们罗列在主分片和复制分片上成功新建、索引或删除一个文档必要的顺序步骤：
1.  客户端给 **Node 1** 发送新建、索引或删除请求。
2.  节点使用文档的 \_id 确定文档属于 **分片0** 。它转发请求到 **Node 3** ，**分片0** 位于这个节点上。
3.  Node 3 在主分片上执行请求，如果成功，它转发请求到相应的位于Node 1 和Node 2 的复制节点上。当所有 的复制节点报告成功， Node 3 报告成功到请求的节点，请求的节点再报告给客户端。
客户端接收到成功响应的时候，文档的修改已经被应用于主分片和所有的复制分片。你的修改生效了。
### 搜索文档
文档能够从主分片或任意一个复制分片被检索。
![](http://image.moguit.cn/1bb297c3f9bd48d2b93b56d211cabf75)
下面我们罗列在主分片或复制分片上检索一个文档必要的顺序步骤：
1.  客户端给Node 1 发送get请求。
2.  节点使用文档的\_id 确定文档属于分片0 。分片0 对应的复制分片在三个节点上都有。此时，它转发请求到 Node 2 。
3.  Node 2 返回文档(document)给Node 1 然后返回给客户端。对于读请求，为了平衡负载，请求节点会为每个请求选择不同的分片——它会循环所有分片副本。可能的情况是，一个被索引的文档已经存在于主分片上却还没来得及同步到复制分片上。这时复制分片会报告文档未找到，主分片会成功返回文档。一旦索引请求成功返回给用户，文档则在主分片和复制分片都是可用的。
### 全文搜索
对于全文搜索而言，文档可能分散在各个节点上，那么在分布式的情况下，如何搜索文档呢？
搜索，分为2个阶段，
*   搜索（query）
*   取回（fetch）
#### 搜索（query）
![](http://image.moguit.cn/e32ebfac9d9e416c8a62445b84ff9fc0)
查询阶段包含以下三步：
1.  客户端发送一个search（搜索） 请求给Node 3 , Node 3 创建了一个长度为from+size 的空优先级队
2.  Node 3 转发这个搜索请求到索引中每个分片的原本或副本。每个分片在本地执行这个查询并且结果将结果到 一个大小为from+size 的有序本地优先队列里去。
3.  每个分片返回document的ID和它优先队列里的所有document的排序值给协调节点Node 3 。Node 3 把这些 值合并到自己的优先队列里产生全局排序结果。
#### 取回 fetch
![](http://image.moguit.cn/b363119d1f7e45faa06ef2a87950f1cf)
分发阶段由以下步骤构成：
1.  协调节点辨别出哪个document需要取回，并且向相关分片发出GET 请求。
2.  每个分片加载document并且根据需要丰富（enrich）它们，然后再将document返回协调节点。
3.  一旦所有的document都被取回，协调节点会将结果返回给客户端。
Java客户端
-------
在Elasticsearch中，为java提供了2种客户端，一种是REST风格的客户端，另一种是Java API的客户端
### REST客户端
Elasticsearch提供了2种REST客户端，一种是低级客户端，一种是高级客户端。
*   Java Low Level REST Client：官方提供的低级客户端。该客户端通过http来连接Elasticsearch集群。用户在使 用该客户端时需要将请求数据手动拼接成Elasticsearch所需JSON格式进行发送，收到响应时同样也需要将返回的JSON数据手动封装成对象。虽然麻烦，不过该客户端兼容所有的Elasticsearch版本。
*   Java High Level REST Client：官方提供的高级客户端。该客户端基于低级客户端实现，它提供了很多便捷的 API来解决低级客户端需要手动转换数据格式的问题。
### 构造数据
    POST /haoke/house/_bulk
    {"index":{"_index":"haoke","_type":"house"}}
    {"id":"1001","title":"整租 · 南丹大楼 1居室 7500","price":"7500"}
    {"index":{"_index":"haoke","_type":"house"}}
    {"id":"1002","title":"陆家嘴板块，精装设计一室一厅，可拎包入住诚意租。","price":"8500"}
    {"index":{"_index":"haoke","_type":"house"}}
    {"id":"1003","title":"整租 · 健安坊 1居室 4050","price":"7500"}
    {"index":{"_index":"haoke","_type":"house"}}
    {"id":"1004","title":"整租 · 中凯城市之光+视野开阔+景色秀丽+拎包入住","price":"6500"}
    {"index":{"_index":"haoke","_type":"house"}}
    {"id":"1005","title":"整租 · 南京西路品质小区 21213三轨交汇 配套齐* 拎包入住","price":"6000"}
    {"index":{"_index":"haoke","_type":"house"}}
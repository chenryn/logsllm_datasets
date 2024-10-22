*   不同的文档类型不能为相同的属性设置不同的类型。例如，在同一索引中的所有文档类型中，一个叫 **title** 的字段必须具有相同的类型。
RESTful API
-----------
在 **Elasticsearch** 中，提供了功能丰富的 **RESTful API** 的操作，包括基本的 **CRUD**、创建索引、删除索引等操作。
### 创建非结构化索引
在 **Lucene** 中，创建索引是需要定义字段名称以及字段的类型的，在 **Elasticsearch** 中提供了非结构化的索引，就是不需要创建索引结构，即可写入数据到索引中，实际上在 **Elasticsearch** 底层会进行结构化操作，此操作对用户是透明的。
### 创建空索引
    PUT /haoke
    {
        "settings": {
            "index": {
            "number_of_shards": "2", #分片数
            "number_of_replicas": "0" #副本数
            }
        }
    }
### 删除索引
    #删除索引
    DELETE /haoke
    {
    	"acknowledged": true
    }
### 插入数据
> **URL** 规则： **POST** /{索引}/{类型}/{id}
    POST /haoke/user/1001
    #数据
    {
    "id":1001,
    "name":"张三",
    "age":20,
    "sex":"男"
    }
使用 **postman** 操作成功后
![操作成功](http://image.moguit.cn/988b16134db444148f4473bc2821c480)
我们通过 **ElasticSearchHead** 进行数据预览就能够看到我们刚刚插入的数据了
![ElasticSearchHead插件浏览](http://image.moguit.cn/bd43ce7c75dc4ca786c2fc8b43570633)
说明：非结构化的索引，不需要事先创建，直接插入数据默认创建索引。不指定id插入数据：
![自动生成ID](http://image.moguit.cn/8eacb27d865145d4a4ef743b8540b3ff)
### 更新数据
在 **Elasticsearch** 中，文档数据是不能修改的，但是可以通过覆盖的方式进行更新。
    PUT /haoke/user/1001
    {
    "id":1001,
    "name":"张三",
    "age":21,
    "sex":"女"
    }
覆盖成功后的结果如下：
![更新数据](http://image.moguit.cn/a9f85d7c1d5b47bcb94b863914ca0d7a)
![](http://image.moguit.cn/21283d6f07ad4dcb99f9f5a25b03b8e7)
可以看到数据已经被覆盖了。问题来了，可以局部更新吗？ -- 可以的。前面不是说，文档数据不能更新吗？ 其实是这样的：在内部，依然会查询到这个文档数据，然后进行覆盖操作，步骤如下：
1.  从旧文档中检索JSON
2.  修改它
3.  删除旧文档
4.  索引新文档
```yaml
#注意：这里多了_update标识
POST /haoke/user/1001/_update
{
    "doc":{
    	"age":23
    }
}
```
![更新操作](http://image.moguit.cn/2aea6055e5a84bd78061934c3da0ef97)
![](http://image.moguit.cn/e40e1718f6a542189bf6b6443dee441e)
可以看到，数据已经是局部更新了
### 删除索引
在 **Elasticsearch** 中，删除文档数据，只需要发起 **DELETE** 请求即可，不用额外的参数
    DELETE 1 /haoke/user/1001
![删除索引](http://image.moguit.cn/c85b838db28949b392b381cf8cecb952)
需要注意的是，**result** 表示已经删除，**version** 也增加了。
如果删除一条不存在的数据，会响应 **404**
![](http://image.moguit.cn/853781404013411aaca085cd6311da23)
> 删除一个文档也不会立即从磁盘上移除，它只是被标记成已删除。Elasticsearch将会在你之后添加更多索引的时候才会在后台进行删除内容的清理。【相当于批量操作】
### 搜索数据
#### 根据id搜索数据
    GET /haoke/user/BbPe_WcB9cFOnF3uebvr
    #返回的数据如下
    {
        "_index": "haoke",
        "_type": "user",
        "_id": "BbPe_WcB9cFOnF3uebvr",
        "_version": 8,
        "found": true,
        "_source": { #原始数据在这里
            "id": 1002,
            "name": "李四",
            "age": 40,
            "sex": "男"
            }
    }
#### 搜索全部数据
    GET 1 /haoke/user/_search
注意，使用查询全部数据的时候，默认只会返回**10**条
![](http://image.moguit.cn/a0f1e6567bdb40ddaf21139832a68e0b)
#### 关键字搜索数据
    #查询年龄等于20的用户
    GET /haoke/user/_search?q=age:20
结果如下：
![](http://image.moguit.cn/f8f4f3d7473f4af1abecb98ad6c3da53)
### DSL搜索
Elasticsearch提供丰富且灵活的查询语言叫做DSL查询(Query DSL),它允许你构建更加复杂、强大的查询。 DSL(Domain Specific Language特定领域语言)以JSON请求体的形式出现。
    POST /haoke/user/_search
    #请求体
    {
        "query" : {
            "match" : { #match只是查询的一种
            	"age" : 20
            }
        }
    }
实现：查询年龄大于30岁的男性用户。
![](http://image.moguit.cn/dbc43dae5a3d402b9b714fc1015d561a)
    POST /haoke/user/_search
    #请求数据
    {
        "query": {
            "bool": {
                "filter": {
                        "range": {
                            "age": {
                            "gt": 30
                        }
                    }
                },
                "must": {
                    "match": {
                    	"sex": "男"
                    }
                }
            }
        }
    }
查询出来的结果
![](http://image.moguit.cn/92f90ada9259420fb69b9a210585774c)
#### 全文搜索
    POST /haoke/user/_search
    #请求数据
    {
        "query": {
            "match": {
            	"name": "张三 李四"
            }
        }
    }
![](http://image.moguit.cn/120b2f45ea0a40389b53820937747826)
**高亮显示**：只需要在添加一个 **highlight** 即可
    POST /haoke/user/_search
    #请求数据
    {
        "query": {
            "match": {
            	"name": "张三 李四"
            }
        }
        "highlight": {
            "fields": {
            	"name": {}
            }
        }
    }
![](http://image.moguit.cn/300bb278862046c19b0c93381d3e38c5)
#### 聚合
在 **Elasticsearch** 中，支持聚合操作，类似**SQL**中的group by操作。
    POST /haoke/user/_search
    {
        "aggs": {
            "all_interests": {
                "terms": {
                    "field": "age"
                }
            }
        }
    }
结果如下，我们通过年龄进行聚合
![](http://image.moguit.cn/681499e029454245895687df0a4b0643)
从结果可以看出，年龄30的有2条数据，20的有一条，40的一条。
ElasticSearch核心详解
-----------------
### 文档
在Elasticsearch中，文档以JSON格式进行存储，可以是复杂的结构，如：
    {
        "_index": "haoke",
        "_type": "user",
        "_id": "1005",
        "_version": 1,
        "_score": 1,
        "_source": {
            "id": 1005,
            "name": "孙七",
            "age": 37,
            "sex": "女",
            "card": {
                "card_number": "123456789"
             }
        }
    }
其中，card是一个复杂对象，嵌套的Card对象
#### 元数据（metadata）
一个文档不只有数据。它还包含了元数据(metadata)——关于文档的信息。三个必须的元数据节点是：
![image-20200922165956176](http://image.moguit.cn/81b4b1e81a7c4424afcb4699e671eebf)
#### index
索引(index)类似于关系型数据库里的“数据库”——它是我们存储和索引关联数据的地方。
> 提示：事实上，我们的数据被存储和索引在分片(shards)中，索引只是一个把一个或多个分片分组在一起的逻辑空间。然而，这只是一些内部细节——我们的程序完全不用关心分片。对于我们的程序而言，文档存储在索引(index)中。剩下的细节由Elasticsearch关心既可。
#### \_type
在应用中，我们使用对象表示一些“事物”，例如一个用户、一篇博客、一个评论，或者一封邮件。每个对象都属于一个类(class)，这个类定义了属性或与对象关联的数据。user 类的对象可能包含姓名、性别、年龄和Email地址。 在关系型数据库中，我们经常将相同类的对象存储在一个表里，因为它们有着相同的结构。同理，在Elasticsearch 中，我们使用相同类型(type)的文档表示相同的“事物”，因为他们的数据结构也是相同的。
每个类型(type)都有自己的映射(mapping)或者结构定义，就像传统数据库表中的列一样。所有类型下的文档被存储在同一个索引下，但是类型的映射(mapping)会告诉Elasticsearch不同的文档如何被索引。
\_type 的名字可以是大写或小写，不能包含下划线或逗号。我们将使用blog 做为类型名。
#### \_id
id仅仅是一个字符串，它与\_index 和\_type 组合时，就可以在Elasticsearch中唯一标识一个文档。当创建一个文 档，你可以自定义\_id ，也可以让Elasticsearch帮你自动生成（32位长度）
### 查询响应
#### pretty
可以在查询url后面添加pretty参数，使得返回的json更易查看。
![](http://image.moguit.cn/0dea5130d3f04dd3988713df1500564f)
#### 指定响应字段
在响应的数据中，如果我们不需要全部的字段，可以指定某些需要的字段进行返回。通过添加 \_source
    GET /haoke/user/1005?_source=id,name
    #响应
    {
        "_index": "haoke",
        "_type": "user",
        "_id": "1005",
        "_version": 1,
        "found": true,
        "_source": {
            "name": "孙七",
            "id": 1005
         }
    }
如不需要返回元数据，仅仅返回原始数据，可以这样：
    GET /haoke/1 user/1005/_source
![](http://image.moguit.cn/1c0fe6613292420a87cf9179973e6b7e)
还可以这样：
    GET /haoke/user/1005/_source?_1 source=id,name
![](http://image.moguit.cn/1c1d9294aeaf4d38b57fe93ba5ac616f)
#### 判断文档是否存在
如果我们只需要判断文档是否存在，而不是查询文档内容，那么可以这样：
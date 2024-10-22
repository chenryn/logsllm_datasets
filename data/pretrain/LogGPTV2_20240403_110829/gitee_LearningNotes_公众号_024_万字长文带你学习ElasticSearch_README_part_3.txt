    HEAD /haoke/user/1005
通过发送一个head请求，来判断数据是否存在
![判断数据是否存在](http://image.moguit.cn/b844868e796f4faea7872a475de0119e)
    HEAD 1 /haoke/user/1006
![数据不存在](http://image.moguit.cn/c9a70889fde245358afdf48b4671f39c)
> 当然，这只表示你在查询的那一刻文档不存在，但并不表示几毫秒后依旧不存在。另一个进程在这期间可能创建新文档。
### 批量操作
有些情况下可以通过批量操作以减少网络请求。如：批量查询、批量插入数据。
#### 批量查询
    POST /haoke/user/_mget
    {
    	"ids" : [ "1001", "1003" ]
    }
结果：
![批量查询](http://image.moguit.cn/61036f13c32e4828ab4e66dea8decb23)
如果，某一条数据不存在，不影响整体响应，需要通过found的值进行判断是否查询到数据。
    POST /haoke/user/_mget
    {
    	"ids" : [ "1001", "1006" ]
    }
![](http://image.moguit.cn/fc019c0ea0a347a9933d2d58185f70fe)
> 也就是说，一个数据的存在不会影响其它数据的返回
#### bulk操作
在**Elasticsearch** 中，支持批量的插入、修改、删除操作，都是通过 **bulk** 的 **api** 完成的。
请求格式如下：（请求格式不同寻常）
    { action: { metadata }}
    { request body }
    { action: { metadata }}
    { request body }
    ...
批量插入数据：
    {"create":{"_index":"haoke","_type":"user","_id":2001}}
    {"id":2001,"name":"name1","age": 20,"sex": "男"}
    {"create":{"_index":"haoke","_type":"user","_id":2002}}
    {"id":2002,"name":"name2","age": 20,"sex": "男"}
    {"create":{"_index":"haoke","_type":"user","_id":2003}}
    {"id":2003,"name":"name3","age": 20,"sex": "男"}
注意最后一行的回车：
![](http://image.moguit.cn/0981dc6aee5647c9b5ceb07ed1f73b15)
批量删除：
    {"delete":{"_index":"haoke","_type":"user","_id":2001}}
    {"delete":{"_index":"haoke","_type":"user","_id":2002}}
    {"delete":{"_index":"haoke","_type":"user","_id":2003}}
由于 **delete** 没有请求体，所以 **action** 的下一行直接就是下一个 **action**。
![](http://image.moguit.cn/dd8fc81e9844456186bb019c0a9c75be)
其他操作就类似了。一次请求多少性能最高？
*   整个批量请求需要被加载到接受我们请求节点的内存里，所以请求越大，给其它请求可用的内存就越小。有一 个最佳的bulk请求大小。超过这个大小，性能不再提升而且可能降低。
*   最佳大小，当然并不是一个固定的数字。它完全取决于你的硬件、你文档的大小和复杂度以及索引和搜索的负 载。
*   幸运的是，这个最佳点(**sweetspot**)还是容易找到的：试着批量索引标准的文档，随着大小的增长，当性能开始 降低，说明你每个批次的大小太大了。开始的数量可以在1000~5000个文档之间，如果你的文档非常大，可以使用较小的批次。
*   通常着眼于你请求批次的物理大小是非常有用的。一千个 **1kB** 的文档和一千个 **1MB** 的文档大不相同。一个好的 批次最好保持在 **5-15MB** 大小间。
### 分页
和 **SQL** 使用 **LIMIT** 关键字返回只有一页的结果一样，**Elasticsearch** 接受 **from** 和 **size** 参数：
*   **size**: 结果数，默认10
*   **from**: 跳过开始的结果数，默认0
如果你想每页显示5个结果，页码从1到3，那请求如下：
    GET /_search?size=5
    GET /_search?size=5&from=5
    GET /_search?size=5&from=10
应该当心分页太深或者一次请求太多的结果。结果在返回前会被排序。但是记住一个搜索请求常常涉及多个分 片。每个分片生成自己排好序的结果，它们接着需要集中起来排序以确保整体排序正确。
    GET /haoke/user/_1 search?size=1&from=2
![](http://image.moguit.cn/85f46260323a4702a1029d76904c6b62)
#### 在集群系统中深度分页
为了理解为什么深度分页是有问题的，让我们假设在一个有 **5** 个主分片的索引中搜索。当我们请求结果的第一 页（结果1到10）时，每个分片产生自己最顶端10个结果然后返回它们给请求节点(requesting node)，它再 排序这所有的50个结果以选出顶端的10个结果。
现在假设我们请求第 **1000** 页 — 结果10001到10010。工作方式都相同，不同的是每个分片都必须产生顶端的 10010个结果。然后请求节点排序这50050个结果并丢弃50040个！
你可以看到在分布式系统中，排序结果的花费随着分页的深入而成倍增长。这也是为什么网络搜索引擎中任何 语句不能返回多于1000个结果的原因。
### 映射
前面我们创建的索引以及插入数据，都是由 **Elasticsearch** 进行自动判断类型，有些时候我们是需要进行明确字段类型的，否则，自动判断的类型和实际需求是不相符的。
自动判断的规则如下：
![image-20200923103848097](http://image.moguit.cn/edc2fa9f5f814194b956f1c571dab275)
Elasticsearch中支持的类型如下：
![image-20200923103917807](http://image.moguit.cn/c3cbf05cfeaf4578b3ee2e0f1e3f133a)
*   **string** 类型在 **ElasticSearch** 旧版本中使用较多，从 **ElasticSearch 5.x** 开始不再支持 **string**，由**text**和 **keyword** 类型替代。
*   **text** 类型，当一个字段是要被全文搜索的，比如 **Email** 内容、产品描述，应该使用 **text** 类型。设置text类型 以后，字段内容会被分析，在生成倒排索引以前，字符串会被分析器分成一个一个词项。text类型的字段 不用于排序，很少用于聚合。
*   **keyword** 类型适用于索引结构化的字段，比如 **email** 地址、主机名、状态码和标签。如果字段需要进行过 滤(比如查找已发布博客中status属性为published的文章)、排序、聚合。**keyword** 类型的字段只能通过精 确值搜索到。
#### 创建明确类型的索引：
> 如果你要像之前旧版版本一样兼容自定义 type ,需要将 include\_type\_name=true 携带
    put http://202.193.56.222:9200/itcast?include_type_name=true
    {
        "settings":{
            "index":{
                "number_of_shards":"2",
                "number_of_replicas":"0"
            }
        },
        "mappings":{
            "person":{
                "properties":{
                    "name":{
                        "type":"text"
                    },
                    "age":{
                        "type":"integer"
                    },
                    "mail":{
                        "type":"keyword"
                    },
                    "hobby":{
                        "type":"text"
                    }
                }
            }
        }
    }
查看映射
    GET /itcast/_mapping
![](http://image.moguit.cn/b9fe8584a62940ecade92d47ee07c159)
插入数据
    POST /itcast/_bulk
    {"index":{"_index":"itcast","_type":"person"}}
    {"name":"张三","age": 20,"mail": "PI:EMAIL","hobby":"羽毛球、乒乓球、足球"}
    {"index":{"_index":"itcast","_type":"person"}}
    {"name":"李四","age": 21,"mail": "PI:EMAIL","hobby":"羽毛球、乒乓球、足球、篮球"}
    {"index":{"_index":"itcast","_type":"person"}}
    {"name":"王五","age": 22,"mail": "PI:EMAIL","hobby":"羽毛球、篮球、游泳、听音乐"}
    {"index":{"_index":"itcast","_type":"person"}}
    {"name":"赵六","age": 23,"mail": "PI:EMAIL","hobby":"跑步、游泳"}
    {"index":{"_index":"itcast","_type":"person"}}
    {"name":"孙七","age": 24,"mail": "PI:EMAIL","hobby":"听音乐、看电影"}
![](http://image.moguit.cn/e8cc794b311540e095bfa964af83ad89)
#### 测试搜索
    POST /itcast/person/_search
    {
        "query":{
            "match":{
                "hobby":"音乐"
            }
        }
    }
![](http://image.moguit.cn/20c882efb7da4f5e928ba8089392490d)
### 结构化查询
#### term查询
term 主要用于精确匹配哪些值，比如数字，日期，布尔值或 not\_analyzed 的字符串(未经分析的文本数据类型)：
    { "term": { "age": 26 }}
    { "term": { "date": "2014-09-01" }}
    { "term": { "public": true }}
    { "term": { "tag": "full_text" }}
示例
    POST /itcast/person/_search
    {
        "query":{
            "term":{
                "age":20
            }
        }
    }
![](http://image.moguit.cn/eb648749d1fc4525b32befcdfd478f98)
#### terms查询
terms 跟 term 有点类似，但 terms 允许指定多个匹配条件。 如果某个字段指定了多个值，那么文档需要一起去 做匹配：
    {
        "terms":{
            "tag":[
                "search",
                "full_text",
                "nosql"
            ]
        }
    }
示例：
    POST /itcast/person/_search
    {
        "query":{
            "terms":{
                "age":[
                    20,
                    21
                ]
            }
        }
    }
![](http://image.moguit.cn/32caab1937e14103a74ba0b6e8eb6c6b)
#### range查询
range 过滤允许我们按照指定范围查找一批数据：
    {
        "range":{
            "age":{
                "gte":20,
                "lt":30
            }
        }
    }
范围操作符包含：
*   gt : 大于
*   gte:: 大于等于
*   lt : 小于
*   lte: 小于等于
示例：
    POST /itcast/person/_search
    {
        "query":{
            "range":{
                "age":{
                    "gte":20,
                    "lte":22
                }
            }
        }
    }
#### exists 查询
exists 查询可以用于查找文档中是否包含指定字段或没有某个字段，类似于SQL语句中的IS\_NULL 条件
    {
        "exists": {
        	"field": "title"
        }
    }
这两个查询只是针对已经查出一批数据来，但是想区分出某个字段是否存在的时候使用。示例：
    POST /haoke/user/_search
    {
        "query": {
            "exists": { #必须包含
            	"field": "card"
            }
        }
    }
![](http://image.moguit.cn/97909954892e4a9ca70907af1e77bb73)
#### match查询
match 查询是一个标准查询，不管你需要全文本查询还是精确查询基本上都要用到它。
如果你使用 match 查询一个全文本字段，它会在真正查询之前用分析器先分析match 一下查询字符：
    {
        "match": {
        	"tweet": "About Search"
        }
    }
如果用match 下指定了一个确切值，在遇到数字，日期，布尔值或者not\_analyzed 的字符串时，它将为你搜索你 给定的值：
    { "match": { "age": 26 }}
    { "match": { "date": "2014-09-01" }}
    { "match": { "public": true }}
    { "match": { "tag": "full_text" }}
#### bool查询
*   bool 查询可以用来合并多个条件查询结果的布尔逻辑，它包含一下操作符：
*   must :: 多个查询条件的完全匹配,相当于 and 。
*   must\_not :: 多个查询条件的相反匹配，相当于 not 。
*   should :: 至少有一个查询条件匹配, 相当于 or 。
这些参数可以分别继承一个查询条件或者一个查询条件的数组：
    {
        "bool":{
            "must":{
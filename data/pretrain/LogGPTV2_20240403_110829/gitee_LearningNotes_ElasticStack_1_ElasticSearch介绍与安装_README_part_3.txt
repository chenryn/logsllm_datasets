```bash
GET /haoke/user/1005/_source?_1 source=id,name
```
![image-20200923101319728](images/image-20200923101319728.png)
#### 判断文档是否存在
如果我们只需要判断文档是否存在，而不是查询文档内容，那么可以这样：
```bash
HEAD /haoke/user/1005
```
通过发送一个head请求，来判断数据是否存在
![image-20200923101354992](images/image-20200923101354992.png)
```bash
HEAD 1 /haoke/user/1006
```
![image-20200923101433608](images/image-20200923101433608.png)
> 当然，这只表示你在查询的那一刻文档不存在，但并不表示几毫秒后依旧不存在。另一个进程在这期间可能创建新文档。
### 批量操作
有些情况下可以通过批量操作以减少网络请求。如：批量查询、批量插入数据。
#### 批量查询
```bash
POST /haoke/user/_mget
{
	"ids" : [ "1001", "1003" ]
}
```
结果：
![image-20200923101540616](images/image-20200923101540616.png)
如果，某一条数据不存在，不影响整体响应，需要通过found的值进行判断是否查询到数据。
```bash
POST /haoke/user/_mget
{
	"ids" : [ "1001", "1006" ]
}
```
结果：
![image-20200923101721344](images/image-20200923101721344.png)
> 也就是说，一个数据的存在不会影响其它数据的返回
#### _bulk操作
在Elasticsearch中，支持批量的插入、修改、删除操作，都是通过_bulk的api完成的。
请求格式如下：（请求格式不同寻常）
```
{ action: { metadata }}
{ request body }
{ action: { metadata }}
{ request body }
...
```
批量插入数据： 
```bash
{"create":{"_index":"haoke","_type":"user","_id":2001}}
{"id":2001,"name":"name1","age": 20,"sex": "男"}
{"create":{"_index":"haoke","_type":"user","_id":2002}}
{"id":2002,"name":"name2","age": 20,"sex": "男"}
{"create":{"_index":"haoke","_type":"user","_id":2003}}
{"id":2003,"name":"name3","age": 20,"sex": "男"}
```
注意最后一行的回车。
![image-20200923101946147](images/image-20200923101946147.png)
批量删除：
```bash
{"delete":{"_index":"haoke","_type":"user","_id":2001}}
{"delete":{"_index":"haoke","_type":"user","_id":2002}}
{"delete":{"_index":"haoke","_type":"user","_id":2003}}
```
由于delete没有请求体，所以，action的下一行直接就是下一个action。
![image-20200923102044231](images/image-20200923102044231.png)
其他操作就类似了。一次请求多少性能最高？
- 整个批量请求需要被加载到接受我们请求节点的内存里，所以请求越大，给其它请求可用的内存就越小。有一
  个最佳的bulk请求大小。超过这个大小，性能不再提升而且可能降低。
- 最佳大小，当然并不是一个固定的数字。它完全取决于你的硬件、你文档的大小和复杂度以及索引和搜索的负
  载。
- 幸运的是，这个最佳点(sweetspot)还是容易找到的：试着批量索引标准的文档，随着大小的增长，当性能开始
  降低，说明你每个批次的大小太大了。开始的数量可以在1000~5000个文档之间，如果你的文档非常大，可以使用较小的批次。
- 通常着眼于你请求批次的物理大小是非常有用的。一千个1kB的文档和一千个1MB的文档大不相同。一个好的
  批次最好保持在5-15MB大小间。
### 分页
和SQL使用LIMIT 关键字返回只有一页的结果一样，Elasticsearch接受from 和size 参数：
- size: 结果数，默认10
- from: 跳过开始的结果数，默认0
如果你想每页显示5个结果，页码从1到3，那请求如下：
```bash
GET /_search?size=5
GET /_search?size=5&from=5
GET /_search?size=5&from=10
```
应该当心分页太深或者一次请求太多的结果。结果在返回前会被排序。但是记住一个搜索请求常常涉及多个分
片。每个分片生成自己排好序的结果，它们接着需要集中起来排序以确保整体排序正确。
```bash
GET /haoke/user/_1 search?size=1&from=2
```
![image-20200923102611567](images/image-20200923102611567.png)
#### 在集群系统中深度分页
为了理解为什么深度分页是有问题的，让我们假设在一个有5个主分片的索引中搜索。当我们请求结果的第一
页（结果1到10）时，每个分片产生自己最顶端10个结果然后返回它们给请求节点(requesting node)，它再
排序这所有的50个结果以选出顶端的10个结果。
现在假设我们请求第1000页——结果10001到10010。工作方式都相同，不同的是每个分片都必须产生顶端的
10010个结果。然后请求节点排序这50050个结果并丢弃50040个！
你可以看到在分布式系统中，排序结果的花费随着分页的深入而成倍增长。这也是为什么网络搜索引擎中任何
语句不能返回多于1000个结果的原因。
### 映射
前面我们创建的索引以及插入数据，都是由Elasticsearch进行自动判断类型，有些时候我们是需要进行明确字段类型的，否则，自动判断的类型和实际需求是不相符的。
自动判断的规则如下：
![image-20200923103848097](images/image-20200923103848097.png)
Elasticsearch中支持的类型如下：
![image-20200923103917807](images/image-20200923103917807.png)
- string类型在ElasticSearch 旧版本中使用较多，从ElasticSearch 5.x开始不再支持string，由text和
  keyword类型替代。
- text 类型，当一个字段是要被全文搜索的，比如Email内容、产品描述，应该使用text类型。设置text类型
  以后，字段内容会被分析，在生成倒排索引以前，字符串会被分析器分成一个一个词项。text类型的字段
  不用于排序，很少用于聚合。
- keyword类型适用于索引结构化的字段，比如email地址、主机名、状态码和标签。如果字段需要进行过
  滤(比如查找已发布博客中status属性为published的文章)、排序、聚合。keyword类型的字段只能通过精
  确值搜索到。
#### 创建明确类型的索引：
>  如果你要像之前旧版版本一样兼容自定义 type ,需要将 \**i\**nclude_type_name=true 携带
```bash
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
```
查看映射
```bash
GET /itcast/_mapping
```
![image-20200923104201613](images/image-20200923104201613.png)
插入数据
```bash
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
```
![image-20200923104551405](images/image-20200923104551405.png)
#### 测试搜索
```bash
POST /itcast/person/_search
{
    "query":{
        "match":{
            "hobby":"音乐"
        }
    }
}
```
![image-20200923104653427](images/image-20200923104653427.png)
### 结构化查询
#### term查询
term 主要用于精确匹配哪些值，比如数字，日期，布尔值或 not_analyzed 的字符串(未经分析的文本数据类型)：
```bash
{ "term": { "age": 26 }}
{ "term": { "date": "2014-09-01" }}
{ "term": { "public": true }}
{ "term": { "tag": "full_text" }}
```
示例
```bash
POST /itcast/person/_search
{
    "query":{
        "term":{
            "age":20
        }
    }
}
```
![image-20200923104851159](images/image-20200923104851159.png)
#### terms查询
terms 跟 term 有点类似，但 terms 允许指定多个匹配条件。 如果某个字段指定了多个值，那么文档需要一起去
做匹配：
```bash
{
    "terms":{
        "tag":[
            "search",
            "full_text",
            "nosql"
        ]
    }
}
```
示例：
```bash
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
```
![image-20200923105030182](images/image-20200923105030182.png)
#### range查询
range 过滤允许我们按照指定范围查找一批数据：
```bash
{
    "range":{
        "age":{
            "gte":20,
            "lt":30
        }
    }
}
```
范围操作符包含：
- gt : 大于
- gte:: 大于等于
- lt : 小于
- lte: 小于等于
示例：
```bash
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
```
#### exists 查询
exists 查询可以用于查找文档中是否包含指定字段或没有某个字段，类似于SQL语句中的IS_NULL 条件
```bash
{
    "exists": {
    	"field": "title"
    }
}
```
这两个查询只是针对已经查出一批数据来，但是想区分出某个字段是否存在的时候使用。示例：
```bash
POST /haoke/user/_search
{
    "query": {
        "exists": { #必须包含
        	"field": "card"
        }
    }
}
```
![image-20200923105416339](images/image-20200923105416339.png)
#### match查询
match 查询是一个标准查询，不管你需要全文本查询还是精确查询基本上都要用到它。
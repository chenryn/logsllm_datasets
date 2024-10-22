                "term":{
                    "folder":"inbox"
                }
            },
            "must_not":{
                "term":{
                    "tag":"spam"
                }
            },
            "should":[
                {
                    "term":{
                        "starred":true
                    }
                },
                {
                    "term":{
                        "unread":true
                    }
                }
            ]
        }
    }
### 过滤查询
前面讲过结构化查询，Elasticsearch也支持过滤查询，如term、range、match等。
示例：查询年龄为20岁的用户。
    POST /itcast/person/_search
    {
        "query":{
            "bool":{
                "filter":{
                    "term":{
                        "age":20
                    }
                }
            }
        }
    }
#### 查询和过滤的对比
*   一条过滤语句会询问每个文档的字段值是否包含着特定值。
*   查询语句会询问每个文档的字段值与特定值的匹配程度如何。
*   一条查询语句会计算每个文档与查询语句的相关性，会给出一个相关性评分 \_score，并且 按照相关性对匹 配到的文档进行排序。 这种评分方式非常适用于一个没有完全配置结果的全文本搜索。
*   一个简单的文档列表，快速匹配运算并存入内存是十分方便的， 每个文档仅需要1个字节。这些缓存的过滤结果集与后续请求的结合使用是非常高效的。
*   查询语句不仅要查找相匹配的文档，还需要计算每个文档的相关性，所以一般来说查询语句要比 过滤语句更耗时，并且查询结果也不可缓存。
#### 建议：
做精确匹配搜索时，最好用过滤语句，因为过滤语句可以缓存数据。
中文分词
----
### 什么是分词
分词就是指将一个文本转化成一系列单词的过程，也叫文本分析，在Elasticsearch中称之为Analysis。
举例：我是中国人 --> 我/是/中国人
### 分词api
指定分词器进行分词
    POST /_analyze
    {
        "analyzer":"standard",
        "text":"hello world"
    }
结果如下
![](http://image.moguit.cn/aebb930de4414872a0f4957b02aac876)
在结果中不仅可以看出分词的结果，还返回了该词在文本中的位置。
> 指定索引分词
    POST /itcast/_analyze
    {
        "analyzer": "standard",
        "field": "hobby",
        "text": "听音乐"
    }
![](http://image.moguit.cn/f4e46fb990ef4f71923e321169e59d54)
### 中文分词难点
中文分词的难点在于，在汉语中没有明显的词汇分界点，如在英语中，空格可以作为分隔符，如果分隔不正确就会造成歧义。如：
*   **我/爱/炒肉丝**
*   **我/爱/炒/肉丝**
常用中文分词器，**IK**、**jieba**、**THULAC**等，推荐使用 **IK分词器**。
**IK Analyzer** 是一个开源的，基于java语言开发的轻量级的中文分词工具包。从2006年12月推出1.0版开始，**IKAnalyzer** 已经推出了3个大版本。最初，它是以开源项目Luence为应用主体的，结合词典分词和文法分析算法的中文分词组件。新版本的IK Analyzer 3.0则发展为面向Java的公用分词组件，独立于Lucene项目，同时提供了对 **Lucene** 的默认优化实现。
采用了特有的“正向迭代最细粒度切分算法“，具有80万字/秒的高速处理能力 采用了多子处理器分析模式，支持：英文字母（IP地址、Email、URL）、数字（日期，常用中文数量词，罗马数字，科学计数法），中文词汇（姓名、地名处理）等分词处理。 优化的词典存储，更小的内存占用。
> **IK**分词器 **Elasticsearch** 插件地址：
>
> https://github.com/medcl/elasticsearch-analysis-ik
### 安装分词器
首先下载到最新的ik分词器，下载完成后，使用xftp工具，拷贝到服务器上
    #安装方法：将下载到的 es/plugins/ik 目录下
    mkdir es/plugins/ik
    #解压
    unzip elasticsearch-analysis-ik-7.9.1.zip
    #重启
    ./bin/elasticsearch
我们通过日志，发现它已经成功加载了 **ik** 分词器插件
![](http://image.moguit.cn/bedf4113b2934db5a571b82b17dfb567)
### 测试
    POST /_analyze
    {
        "analyzer": "ik_max_word",
        "text": "我是中国人"
    }
我们发现 **ik** 分词器已经成功分词完成
![](http://image.moguit.cn/953816f401e74228b66105e2fbcb0251)
全文搜索
----
全文搜索两个最重要的方面是：
*   相关性（**Relevance**） 它是评价查询与其结果间的相关程度，并根据这种相关程度对结果排名的一种能力，这 种计算方式可以是 **TF/IDF** 方法、地理位置邻近、模糊相似，或其他的某些算法。
*   分词（**Analysis**） 它是将文本块转换为有区别的、规范化的 **token** 的一个过程，目的是为了创建倒排索引以及查询倒排索引。
### 构造数据
> ES 7.4 默认不在支持指定索引类型，默认索引类型是\_doc
    http://202.193.56.222:9200/itcast?include_type_name=true
    {
        "settings":{
            "index":{
                "number_of_shards":"1",
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
                        "type":"text",
                        "analyzer":"ik_max_word"
                    }
                }
            }
        }
    }
然后插入数据
    POST http://202.193.56.222:9200/itcast/_bulk
    {"index":{"_index":"itcast","_type":"person"}}
    {"name":"张三","age": 20,"mail": "PI:EMAIL","hobby":"羽毛球、乒乓球、足球"}
    {"index":{"_index":"itcast","_type":"person"}}
    {"name":"李四","age": 21,"mail": "PI:EMAIL","hobby":"羽毛球、乒乓球、足球、篮球"}
    {"index":{"_index":"itcast","_type":"person"}}
    {"name":"王五","age": 22,"mail": "PI:EMAIL","hobby":"羽毛球、篮球、游泳、听音乐"}
    {"index":{"_index":"itcast","_type":"person"}}
    {"name":"赵六","age": 23,"mail": "PI:EMAIL","hobby":"跑步、游泳、篮球"}
    {"index":{"_index":"itcast","_type":"person"}}
    {"name":"孙七","age": 24,"mail": "PI:EMAIL","hobby":"听音乐、看电影、羽毛球"}
![](http://image.moguit.cn/7a32c301896c45c1a83324d5c82db126)
### 单词搜索
    POST /itcast/person/_search
    {
        "query":{
            "match":{
                "hobby":"音乐"
            }
        },
        "highlight":{
            "fields":{
                "hobby":{
                }
            }
        }
    }
查询出来的结果如下，并且还带有高亮
![](http://image.moguit.cn/2bb41eb4262041e38e365c82133c2359)
过程说明：
*   检查字段类型
    *   爱好 hobby 字段是一个 text 类型（ 指定了IK分词器），这意味着查询字符串本身也应该被分词。
*   分析查询字符串 。
    *   将查询的字符串 “音乐” 传入IK分词器中，输出的结果是单个项 音乐。因为只有一个单词项，所以 match 查询执行的是单个底层 term 查询。
*   查找匹配文档 。
    *   用 term 查询在倒排索引中查找 “音乐” 然后获取一组包含该项的文档，本例的结果是文档：3 、5 。
*   为每个文档评分 。
    *   用 term 查询计算每个文档相关度评分 \_score ，这是种将 词频（term frequency，即词 “音乐” 在相关文档的hobby 字段中出现的频率）和 反向文档频率（inverse document frequency，即词 “音乐” 在所有文档的hobby 字段中出现的频率），以及字段的长度（即字段越短相关度越高）相结合的计算方式。
### 多词搜索
    POST /itcast/person/_search
    {
        "query":{
            "match":{
                "hobby":"音乐 篮球"
            }
        },
        "highlight":{
            "fields":{
                "hobby":{
                }
            }
        }
    }
可以看到，包含了“音乐”、“篮球”的数据都已经被搜索到了。可是，搜索的结果并不符合我们的预期，因为我们想搜索的是既包含“音乐”又包含“篮球”的用户，显然结果返回的“或”的关系。在Elasticsearch中，可以指定词之间的逻辑关系，如下：
    POST /itcast/person/_search
    {
        "query":{
            "match":{
                "hobby":"音乐 篮球"
                "operator":"and"
            }
        },
        "highlight":{
            "fields":{
                "hobby":{
                }
            }
        }
    }
通过这样的话，就会让两个关键字之间存在and关系了
![](http://image.moguit.cn/c41c479edd7a4085855515721854a814)
可以看到结果符合预期。
前面我们测试了“OR” 和 “AND”搜索，这是两个极端，其实在实际场景中，并不会选取这2个极端，更有可能是选取这种，或者说，只需要符合一定的相似度就可以查询到数据，在Elasticsearch中也支持这样的查询，通过 minimum\_should\_match来指定匹配度，如：70%；示例如下：
    {
        "query":{
            "match":{
            "hobby":{
                "query":"游泳 羽毛球",
                "minimum_should_match":"80%"
                }
                }
                },
            "highlight": {
            "fields": {
            "hobby": {}
            }
        }
    }
    #结果：省略显示
    "hits": {
    "total": 4, #相似度为80%的情况下，查询到4条数据
    "max_score": 1.621458,
    "hits": [
    }
    #设置40%进行测试：
    {
        "query":{
            "match":{
                "hobby":{
                "query":"游泳 羽毛球",
                "minimum_should_match":"40%"
                }
                }
                },
                "highlight": {
                "fields": {
                "hobby": {}
            }
        }
    }
    #结果：
    "hits": {
    "total": 5, #相似度为40%的情况下，查询到5条数据
    "max_score": 1.621458,
    "hits": [
    }
相似度应该多少合适，需要在实际的需求中进行反复测试，才可得到合理的值。
### 组合搜索
在搜索时，也可以使用过滤器中讲过的 **bool** 组合查询，示例：
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
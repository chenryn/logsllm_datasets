```
也可以参考陌溪录制的视频教程完成博客初始环境的搭建
因为一键部署脚本只支持核心板启动，而切换 **ES** 搜索需要用到 **mogu-search** 和 **elk**。因此，在完成博客的初始环境搭建后，进入到 **docker-compose** 文件夹
```bash
# 给文件夹增加权限
chown -R 1000:1000 data/elasticsearch_data
chown -R 1000:1000 log/elk
```
然后执行下面的脚本，安装 **elk**，**elk** 由 **ElasticSearch** 、**Logstash**、**Kibana** 组成
```bash
docker-compose -f yaml/elk.yml up -d 
```
同时在启动后，也可以使用下列命令通过查看启动日志
```BASH
docker logs -f -t elk
```
关于如何验证启动是否成功，可以输入：**ip + 9200**，如果出现下面的标识，标识已经启动成功了 
![验证es启动](images/image-20210912171926367.png)
同时安装的 **elk**  也包含了 **kibana**，可以输入：**域名 + 5601** 访问图形化界面，在这里面可以搭建一些**日志**看板。
![验证kibana启动](images/image-20210912172239079.png)
在 **ELK** 启动成功后，就可以接着启动 **mogu-search** 项目。如果看过**搜索模块**源码的小伙伴，是可以发现目前 **mogu-search** 是通过注释的方式来进行切换的，因为 **ES** 用的比较多，所以默认是把 **solr** 相关的代码注释了起来的，未来的话陌溪可能会考虑制作两个镜像，一个是 **mogu-search-es**，另外一个是 **mogu-search-solr**，然后通过运行不同的镜像，使用不同的全文检索工具。
在启动前需要先配置一下 **ElasticSearch** 的地址，到 **nacos** 页面，找到 **mogu-search-prod.yml**
> nacos地址：http://ip:8848/nacos
![修改nacos配置](images/image-20210913085630171.png)
将里面的 **ip** 替换成自己的就OK啦
```bash
  data:
    elasticsearch:
      cluster-name: elasticsearch
      cluster-nodes: 38.84.74.140:9300
  elasticsearch:
    rest:
      uris: ["http://38.84.74.140:9200"]
```
修改完成后，回到服务器中，执行下面命令，启动 **mogu-search**
```BASH
docker-compose -f yaml/search.yml up -d 
```
启动完成后，就可以在后台进行初始化 **ElasticSearch** 索引了，到 **监控中心** -> **ElasticSearch**，点击初始化 **ES** 索引，系统将会对我们所有的文章建立索引，以便后续进行分词检索。
![初始化索引](images/image-20210912173603793.png)
最后到门户页面，输入关键字 **java** 进行搜索，若地址栏中包含了 **model=1**，表示已经开启了 **ES** 搜索，并且能搜索到内容，说明已经成功完成搭建。
![开始搜索](images/image-20210912173831301.png)
 若 **model=0** 或者没有 **model** 字段，那么需要到系统配置处，看开关是否勾选到了 **ES** 搜索，若还存在问题，记得清空 **redis** 缓存后在试试。
 ![切换搜索模式](images/image-20210912165229742.png)
## 评论支持Markdown
最近发现有有一些小伙伴会在留言区贴一些错误代码，为了方便小伙伴同时增加代码的可读性，目前支持 **markdown** 进行评论啦。
![评论支持markdown](images/image-20210912174644753.png)
好啦，本次蘑菇版本更新就到这里啦。我是陌溪，我们下期再见~
往期推荐
----
*   [蘑菇博客从0到2000Star，分享我的Java自学路线图](https://mp.weixin.qq.com/s/3u6OOYkpj4_ecMzfMqKJRw)
*   [从三本院校到斩获字节跳动后端研发Offer-讲述我的故事](https://mp.weixin.qq.com/s/c4rR_aWpmNNFGn-mZBLWYg)
*   [万字长文带你学习ElasticSearch](https://mp.weixin.qq.com/s/9eh6rK2aZHRiBpf5bRae9g)
*   [双非本科，折戟成沙铁未销，九面字节终上岸！](https://mp.weixin.qq.com/s/SRf2f8wFFyjz2BUUXD_pmg)
*   [如何使用一条命令完成蘑菇博客的部署？](https://mp.weixin.qq.com/s/LgRIqdPAGzN1tCPMi0Y8RQ)
*   [为什么你们制作镜像只有5MB，而我却200MB？](https://mp.weixin.qq.com/s/iWpivtTAKMPKT6gq_3nwaA)
*   [字节二面：蘑菇博客是怎么解决缓存穿透的?](https://mp.weixin.qq.com/s/JNnL6sTySXL9ta5p0rjjXg)
*   [还在用破解IDEA？陌溪手把手教如何申请正版](https://mp.weixin.qq.com/s/mZjoSjk0QqeKFxPbFySomg)
*   [32图，教你部署一个博客小程序](https://mp.weixin.qq.com/s/hFfsDPBdBpaLjXV8Bm5Ycg)
结语
--
博主就职于字节跳动商业化部门，一直在维护校招笔记仓库 **LearningNote**“在Gitee上已有 **3.9k+ star**，仓库地址：https://gitee.com/moxi159753/LearningNotes”，公众号上的文章也会在此同步更新，欢迎各位小伙伴一起交流学习，回复 “**PDF**”获取PDF笔记，点击查看原文可以**在线阅读**。
同时，想要丰富项目经验的小伙伴，可以参考我维护的开源微服务博客项目： **蘑菇博客**“ **Gitee** 官方推荐项目，博客类搜索排名**第一**，在 **Gitee** 已有 **3.6K** star，仓库地址：https://gitee.com/moxi159753/mogu_blog_v2 ”。
本公众号**申请较晚**，暂时没有开通**留言**功能，欢迎小伙伴们添加我的私人微信 **coder_moxi**【备注：**加群**】，我将邀请你加入到**蘑菇博客交流群**中，欢迎小伙伴们找陌溪一块聊天唠嗑，共同学习进步。最后，如果你觉得本文对你有所帮助，麻烦小伙伴们动动手指给文章点个“**赞**”和“**在看**”，非常感谢大家的支持。
![快来找陌溪唠嗑吧](https://gitee.com/moxi159753/LearningNotes/raw/master/doc/images/qq/%E6%B7%BB%E5%8A%A0%E9%99%8C%E6%BA%AA.png)
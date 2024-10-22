# MySQL索引
## 索引的优点
最典型的例子就是查新华字典，通过查找目录快速定位到查找的字
- 大大减少了服务器需要扫描的数量
- 帮助服务器避免排序和临时表
- 将IO变成顺序IO
  - 尽可能的降低磁盘的寻址时间，也就是局部性原理，就是很大一部分数据在未来的一段时间被连续访问
  - 在复制1G压缩包 和 1G小文件，前者的速度会大于后者
  - 减少IO的量，例如写SQL语句的时候，不要写 select *
  - 减少IO的次数，一次IO能搞定的事，不使用3次IO
## 索引的用处
- 快速查找匹配where子句的行
- 从consideration中消除行，如果可以在多个索引之间进行选择，mysql通常会使用栈找到最少行的索引
- 如果表具有多列索引，则优化器可以使用索引的最左匹配前缀来查找
- 当有表连接的时候，从其他表检测行数据
- 查找特定索引列min或max值
- 如果排序或分组是，在可用索引的最左前缀上完成的，则对表进行排序和分组
- 在某些清空下，可以优化查询以检索值而无需查询数据行
## 索引的分类
### 主键索引
如果你在创建索引的时候，使用的是主键这个值，那么就是主键索引，primary key
我们建表的时候，例如下面这个建表语句
``` sql
CREATE TABLE `t_blog_sort` (
  `uid` varchar(32) NOT NULL COMMENT '唯一uid',
  `sort_name` varchar(255) DEFAULT NULL COMMENT '分类内容',
  `content` varchar(255) DEFAULT NULL COMMENT '分类简介',
  `create_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00' COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00' COMMENT '更新时间',
  `status` tinyint(1) unsigned NOT NULL DEFAULT '1' COMMENT '状态',
  `sort` int(11) DEFAULT '0' COMMENT '排序字段，越大越靠前',
  `click_count` int(11) DEFAULT '0' COMMENT '点击数',
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='博客分类表';
```
这里面有使用到    PRIMARY KEY (`uid`)，这就是主键索引
### 唯一索引
唯一索引 类似于普通索引，索引列的值必须唯一
唯一索引和主键索引的区别就是，唯一索引允许出现空值，而主键索引不能为空
```sql
create unique index index_name on table(column)
```
或者创建表时指定
```sql
unique index_name column
```
### 普通索引
当我们需要建立索引的字段，既不是主键索引，也不是唯一索引
那么就可以创建一个普通索引
```sql
create index  index_name on table(column)
```
或者创建表时指定
``` sql
create table(..., index index_name column)
```
### 全文索引
lunce、solr和ElasticSearch就是做全文检索的，里面涉及到了倒排索引的概念，mysql很少使用全文索引。
要用来查找文本中的关键字，不是直接与索引中的值相比较，像是一个搜索引擎，配合 match against 使用，现在只有char，varchar，text上可以创建索引，在数据量比较大时，先将数据放在一个没有全文索引的表里，然后在利用create index创建全文索引，比先生成全文索引在插入数据快很多。
### 组合索引
目前，在业务不是特别复杂的时候，可能使用一个列作为索引，或者直接采用主键索引即可，但是如果业务变得复杂的时候，就需要用到组合索引，通过对多个列建立索引。
组合索引的用处，假设我现在表有个多个字段：id、name、age、gender，然后我经常使用以下的查询条件
```sql
select * from user where name = 'xx' and age = xx
```
这个时候，我们就可以通过组合 name 和 age 来建立一个组合索引，加快查询效率，建立成组合索引后，我的索引将包含两个key值
在多个字段上创建索引，遵循**最左匹配**原则
```sql
alter table t add index index_name(a,b,c);
```
## 索引的使用与否
### 索引的使用
MySQL每次只使用一个索引，与其说 数据库查询只能用一个索引，倒不如说，和全表扫描比起来，去分析两个索引 B+树更耗费时间，所以where A=a and B=b 这种查询使用（A，B）的组合索引最佳，B+树根据（A，B）来排序。
- 主键，unique字段
- 和其他表做连接的字段需要加索引
- 在where 里使用 >, >=, = , ）,not in 等
## 面试技术名词
### 回表
首先我们需要知道，我们建立几个索引，就会生成几棵B+Tree，但是带有原始数据行的B+Tree只有一棵，另外一棵树上的叶子节点带的是主键值。
例如，我们通过主键建立了主键索引，然后在叶子节点上存放的是我们的数据
![image-20200629094621998](images/image-20200629094621998.png)
当我们创建了两个索引时，一个是主键，一个是name，它还会在生成一棵B+Tree，这棵树的叶子节点存放的是主键，当我们通过name进行查找的时候，会得到一个主键，然后在通过主键再去上面的这个主键B+Tree中进行查找，我们称这个操作为 ==**回表**==
![image-20200629094800800](images/image-20200629094800800.png)
当我们的SQL语句使用的是下面这种的时候，它会查找第一颗树，直接返回我们的数据
```mysql
select * from tb where id = 1
```
当我们使用下面这种查询的时候，它会先查找第二棵树得到我们的主键，然后拿着主键再去查询第一棵树
```mysql
select * from tb  where name = 'gang'
```
回表就是通过普通列的索引进行检索，然后再去主键列进行检索，这个操作就是回表
==但是我们在使用检索的时候，尽量避免回表，因为这会造成两次B+Tree的查询，假设一次B+Tree查询需要三次IO操作，那么查询两次B+Tree就需要六次IO操作。==
### 索引覆盖
我们看下面的两个SQL语句，看看它们的查询过程是一样的么？
```SQL
select * from tb where id = 1
select name from tb where name = zhou
```
答案是不一样的，首先我们看第二个语句，就是要输出的列中，就是我们的主键，当我们通过name建立的B+Tree进行查询的时候
![image-20200629094800800](images/image-20200629094800800.png)
我们可以直接找到我们的数据，并得到主键，但是因为我们要返回的就是name，此时说明数据存在了，那么就直接把当前的name进行返回，而不需要通过主键再去主键B+Tree中进行查询。
这样一个不需要进行回表操作的过程，我们称为**索引覆盖**
### 最左匹配
这里提到的 **最左匹配** 和 **索引下推** 都是针对于组合索引的。
例如，我们有这样一个索引
```
name  age：组合索引
```
必须要先匹配name，才能匹配到age。这个我们就被称为最左匹配
例如下面的几条SQL语句，那些语句不会使用组合索引
```sql
where name = ? and age = ?
where name = ?
where age = ?
where age = ? and name = ?
```
根据最左匹配原则，我们的 3 不会使用组合索引的。
那为什么4的顺序不一样，也会使用组合索引呢？
其实内部的优化器会进行调整，例如下面的一个连表操作
```sql
select * from tb1 join tb2 on tb1.id = tb2.id
```
其实在加载表的时候，并不一定是先加载tb1，在加载tb2，而是可能根据表的大小决定的，小的表优先加载进内存中。
### 索引下推
在说索引下推的时候，我们首先在举两个例子
```sql
select * from tb1 where name = ? and age = ?
```
在mysq 5.6之前，会先根据name去存储引擎中拿到所有的数据，然后在server层对age进行数据过滤
在mysql5.6之后，根据name 和 age两个列的值去获取数据，直到把数据返回。
通过对比能够发现，第一个的效率低，第二个的效率高，因为整体的IO量少了，原来是把数据查询出来，在server层进行筛选，而现在在存储引擎层面进行筛选，然后返回结果。我们把这个过程就称为  **索引下推**
> 业务上有这样的需求，A、B 两个用户，如果互相关注，则成为好友。设计上是有两张表，一个是 like 表，一个是 friend 表，like 表有 user_id、liker_id 两个字段，我设置为复合唯一索引即 uk_user_id_liker_id。语句执行逻辑是这样的：
> 以 A 关注 B 为例： 第一步，先查询对方有没有关注自己（B 有没有关注 A） select * from like where user_id = B and liker_id = A;
> 如果有，则成为好友 insert into friend;
> 没有，则只是单向关注关系 insert into like;
> 但是如果 A、B 同时关注对方，会出现不会成为好友的情况。因为上面第 1 步，双方都没关注对方。第 1 步即使使用了排他锁也不行，因为记录不存在，行锁无法生效。请问这种情况，在 MySQL 锁层面有没有办法处理？
首先，我要先赞一下这样的提问方式。虽然极客时间现在的评论区还不能追加评论，但如果大家能够一次留言就把问题讲清楚的话，其实影响也不大。所以，我希望你在留言提问的时候，也能借鉴这种方式。
接下来，我把 @ithunter 同学说的表模拟出来，方便我们讨论。
```sql
CREATE TABLE `like` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `liker_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_id_liker_id` (`user_id`,`liker_id`)
) ENGINE=InnoDB;
CREATE TABLE `friend` (
  id` int(11) NOT NULL AUTO_INCREMENT,
  `friend_1_id` int(11) NOT NULL,
  `firned_2_id` int(11) NOT NULL,
  UNIQUE KEY `uk_friend` (`friend_1_id`,`firned_2_id`)
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;
```
虽然这个题干中，并没有说到 friend 表的索引结构。但我猜测 friend_1_id 和 friend_2_id 也有索引，为便于描述，我给加上唯一索引。
顺便说明一下，“like”是关键字，我一般不建议使用关键字作为库名、表名、字段名或索引名。
我把他的疑问翻译一下，在并发场景下，同时有两个人，设置为关注对方，就可能导致无法成功加为朋友关系。
现在，我用你已经熟悉的时刻顺序表的形式，把这两个事务的执行语句列出来：![img](images/c45063baf1ae521bf5d98b6d7c0e0ced.png)
图 3 并发“喜欢”逻辑操作顺序
由于一开始 A 和 B 之间没有关注关系，所以两个事务里面的 select 语句查出来的结果都是空。
因此，session 1 的逻辑就是“既然 B 没有关注 A，那就只插入一个单向关注关系”。session 2 也同样是这个逻辑。
这个结果对业务来说就是 bug 了。因为在业务设定里面，这两个逻辑都执行完成以后，是应该在 friend 表里面插入一行记录的。
如提问里面说的，“第 1 步即使使用了排他锁也不行，因为记录不存在，行锁无法生效”。不过，我想到了另外一个方法，来解决这个问题。
首先，要给“like”表增加一个字段，比如叫作 relation_ship，并设为整型，取值 1、2、3。
> 值是 1 的时候，表示 user_id 关注 liker_id; 值是 2 的时候，表示 liker_id 关注 user_id; 值是 3 的时候，表示互相关注。
然后，当 A 关注 B 的时候，逻辑改成如下所示的样子：
应用代码里面，比较 A 和 B 的大小，如果 A begin; /* 启动事务 */
insert into `like`(user_id, liker_id, relation_ship) values(A, B, 1) on duplicate key update relation_ship=relation_ship | 1;
select relation_ship from `like` where user_id=A and liker_id=B;
/* 代码中判断返回的 relation_ship，
  如果是 1，事务结束，执行 commit
  如果是 3，则执行下面这两个语句：
  */
insert ignore into friend(friend_1_id, friend_2_id) values(A,B);
commit;
```
如果 A>B，则执行下面的逻辑
```sql
mysql> begin; /* 启动事务 */
insert into `like`(user_id, liker_id, relation_ship) values(B, A, 2) on duplicate key update relation_ship=relation_ship | 2;
select relation_ship from `like` where user_id=B and liker_id=A;
/* 代码中判断返回的 relation_ship，
  如果是 2，事务结束，执行 commit
  如果是 3，则执行下面这两个语句：
*/
insert ignore into friend(friend_1_id, friend_2_id) values(B,A);
commit;
```
这个设计里，让“like”表里的数据保证 user_id  CREATE TABLE `t` (
`id` int(11) NOT NULL primary key auto_increment,
`a` int(11) DEFAULT NULL
) ENGINE=InnoDB;
insert into t values(1,2);
```
这时候，表 t 里有唯一的一行数据 (1,2)。假设，我现在要执行：
```shell
mysql> update t set a=2 where id=1;
```
你会看到这样的结果：
![img](images/367b3f299b94353f32f75ea825391170.png)结果显示，匹配 (rows matched) 了一行，修改 (Changed) 了 0 行。
仅从现象上看，MySQL 内部在处理这个命令的时候，可以有以下三种选择：
1. 更新都是先读后写的，MySQL 读出数据，发现 a 的值本来就是 2，不更新，直接返回，执行结束；
2. MySQL 调用了 InnoDB 引擎提供的“修改为 (1,2)”这个接口，但是引擎发现值与原来相同，不更新，直接返回；
3. InnoDB 认真执行了“把这个值修改成 (1,2)"这个操作，该加锁的加锁，该更新的更新。
你觉得实际情况会是以上哪种呢？你可否用构造实验的方式，来证明你的结论？进一步地，可以思考一下，MySQL 为什么要选择这种策略呢？
你可以把你的验证方法和思考写在留言区里，我会在下一篇文章的末尾和你讨论这个问题。感谢你的收听，也欢迎你把这篇文章分享给更多的朋友一起阅读。
# 上期问题时间
上期的问题是，用一个计数表记录一个业务表的总行数，在往业务表插入数据的时候，需要给计数值加 1。
逻辑实现上是启动一个事务，执行两个语句：
1. insert into 数据表；
2. update 计数表，计数值加 1。
从系统并发能力的角度考虑，怎么安排这两个语句的顺序。
这里，我直接复制 @阿建 的回答过来供你参考：
> 并发系统性能的角度考虑，应该先插入操作记录，再更新计数表。 知识点在[《行锁功过：怎么减少行锁对性能的影响？》] 因为更新计数表涉及到行锁的竞争，先插入再更新能最大程度地减少事务之间的锁等待，提升并发度。
评论区有同学说，应该把 update 计数表放后面，因为这个计数表可能保存了多个业务表的计数值。如果把 update 计数表放到事务的第一个语句，多个业务表同时插入数据的话，等待时间会更长。
这个答案的结论是对的，但是理解不太正确。即使我们用一个计数表记录多个业务表的行数，也肯定会给表名字段加唯一索引。类似于下面这样的表结构：
```sql
CREATE TABLE `rows_stat` (
  `table_name` varchar(64) NOT NULL,
  `row_count` int(10) unsigned NOT NULL,
  PRIMARY KEY (`table_name`)
) ENGINE=InnoDB;
```
在更新计数表的时候，一定会传入 where table_name=$table_name，使用主键索引，更新加行锁只会锁在一行上。
而在不同业务表插入数据，是更新不同的行，不会有行锁。
# Go操作MySQL数据库
## 来源
http://moguit.cn/#/info?blogUid=3d1cc9ce434aeaf2187692eb0feea294
https://www.liwenzhou.com/posts/Go/go_mysql/
## 前言
常见的数据库有
- SqlLite
- MySQL
- SQLServer
- postgreSQL
- Oracle
MySQL主流的关系型数据库，类似的还有postgreSQL
关系型数据库：用表来存储一类的数据
表结构设计的三大范式：《漫画数据库》
## MySQL知识点
### SQL语句
DDL：操作数据库的
DML：表的增删改查
DCL：用户及权限
### 存储引擎
MySQL支持插件式的存储引擎
常见的存储引擎：MyISAM和InnoDB
#### MyISAM：
- 查询快
- 只支持表锁
- 不支持事务
#### InnoDB
- 整体速度快
- 支持表锁和行锁
### 事务
把多个SQL操作当成是一个整体
### 事务的特点
ACID就是事务的特性
- 原子性：事务要么成功要么失败，没有中间操作
- 一致性：数据库的完整性没有被破坏
- 隔离性：事务之间是相互隔离的
- 持久性：事务操作完成后，是持久化到数据库的，不会再次改变
### 索引
索引的原理是：B树和B+树
索引的类型和索引的命中
### 其它内容
分库分表
SQL注入
SQL慢查询优化
MySQL主从
MySQL读写分离
## Go操作数据库
Go语言中的`database/sql`包提供了保证SQL或类SQL数据库的泛用接口，并不提供具体的数据库驱动。使用`database/sql`包时必须注入（至少）一个数据库驱动。
我们常用的数据库基本上都有完整的第三方实现。例如：[MySQL驱动](https://github.com/go-sql-driver/mysql)
### database/sql
原生支持连接池，是并发安全的
这个标准库没有具体的实现，只是列出一些需要第三方库实现的具体内容
### 下载依赖
首先我们需要使用go mod命令初始化项目
```bash
go mod init GoAdvanceCode
```
执行完成后，会在项目的根目录下生成一个go.mod的文件，以后我们添加的依赖，就会在这里显示出来
然后下载数据库依赖
```bash
go get -u github.com/go-sql-driver/mysql
```
`go get`包的路径就是下载第三方的依赖，将第三方的依赖默认保存在 `$GOPATH/src`
### 使用MySQL驱动
 导入刚刚引入的包
```go
package main
import (
	"database/sql"
	"fmt"
	_"github.com/go-sql-driver/mysql"
)
// 定义一个全局的DB，是一个连接池对象
var db *sql.DB
func initDB()(err error)  {
	// 连接数据库
	dsn := "root:root@tcp(127.0.0.1:3306)/mogu_demo"
	// 连接MySQL数据库（注意不能使用 := ）
	db, err = sql.Open("mysql", dsn)
	if err != nil {
		fmt.Printf("open %s failed, err: %v \n", dsn, err)
		return
	}
	// 尝试连接数据库
	err = db.Ping()
	if err != nil {
		fmt.Printf("open %s failed, err: %v, \n", dsn, err)
		return
	}
	fmt.Println("连接数据库成功")
	return
}
type user struct {
	id   string
	name  string
	age int
}
// 查询操作
func query()  {
	sqlStr := "select id, name, age from user where id > ?"
	rows, err := db.Query(sqlStr, 0)
	if err != nil {
		fmt.Println()
		fmt.Printf("query failed, err:%v\n", err)
		return
	}
	// 非常重要：关闭rows释放持有的数据库链接
	defer rows.Close()
	// 循环读取结果集中的数据
	for rows.Next() {
		var u user
		err := rows.Scan(&u.id, &u.name, &u.age)
		if err != nil {
			fmt.Printf("scan failed, err:%v\n", err)
			return
		}
		fmt.Printf("id:%d name:%s age:%d\n", u.id, u.name, u.age)
	}
}
// Go连接MySQL
func main() {
	err := initDB()
	if err != nil {
		fmt.Println("数据库初始化失败")
	}
	// 查询单条记录
	query()
}
```
其中`sql.DB`是表示连接的数据库对象（结构体实例），它保存了连接数据库相关的所有信息。它内部维护着一个具有零到多个底层连接的连接池，它可以安全地被多个goroutine同时使用。
### SetMaxOpenConns
```go
func (db *DB) SetMaxOpenConns(n int)
```
`SetMaxOpenConns`设置与数据库建立连接的最大数目。 如果n大于0且小于最大闲置连接数，会将最大闲置连接数减小到匹配最大开启连接数的限制。 如果n 需要注意的是，我们再查询完成后，需要使用Scan进行连接的释放
>
> ```go
> // 调用Scan才会释放我们的连接
> err := rows.Scan(&u.id, &u.name, &u.age)
> if err != nil {
>     fmt.Printf("scan failed, err:%v\n", err)
>     return
> }
> ```
### SetMaxIdleConns
```go
func (db *DB) SetMaxIdleConns(n int)
```
SetMaxIdleConns设置连接池中的最大闲置连接数。 如果n大于最大开启连接数，则新的最大闲置连接数会减小到匹配最大开启连接数的限制。 如果n ?"
	rows, err := db.Query(sqlStr, 0)
	if err != nil {
		fmt.Printf("query failed, err:%v\n", err)
		return
	}
	// 非常重要：关闭rows释放持有的数据库链接
	defer rows.Close()
	// 循环读取结果集中的数据
	for rows.Next() {
		var u user
		err := rows.Scan(&u.id, &u.name, &u.age)
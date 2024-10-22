-version
    print version string
```
## NSQ架构
### NSQ工作模式
![nsq架构设计](images/nsq4.png)
### Topic和Channel
每个nsqd实例旨在一次处理多个数据流。这些数据流称为`“topics”`，一个`topic`具有1个或多个`“channels”`。每个`channel`都会收到`topic`所有消息的副本，实际上下游的服务是通过对应的`channel`来消费`topic`消息。
`topic`和`channel`不是预先配置的。`topic`在首次使用时创建，方法是将其发布到指定`topic`，或者订阅指定`topic`上的`channel`。`channel`是通过订阅指定的`channel`在第一次使用时创建的。
`topic`和`channel`都相互独立地缓冲数据，防止缓慢的消费者导致其他`chennel`的积压（同样适用于`topic`级别）。
`channel`可以并且通常会连接多个客户端。假设所有连接的客户端都处于准备接收消息的状态，则每条消息将被传递到随机客户端。例如：
![nsq架构设计](images/nsq5.gif)总而言之，消息是从`topic -> channel`（每个channel接收该topic的所有消息的副本）多播的，但是从`channel -> consumers`均匀分布（每个消费者接收该channel的一部分消息）。
### NSQ接收和发送消息流程
![nsq架构设计](images/nsq6.png)
- input Chan：就是go语言中的通道
- In-Memory Chan：是内存的通道，负责将消息进行持久化
- Output Chan：
## NSQ特性
- 消息默认不持久化，可以配置成持久化模式。nsq采用的方式时内存+硬盘的模式，当内存到达一定程度时就会将数据持久化到硬盘。
  - 如果将`--mem-queue-size`设置为0，所有的消息将会存储到磁盘。
  - 服务器重启时也会将当时在内存中的消息持久化。
- 每条消息至少传递一次。
- 消息不保证有序。
## Go操作NSQ
官方提供了Go语言版的客户端：[go-nsq](https://github.com/nsqio/go-nsq)，更多客户端支持请查看[CLIENT LIBRARIES](https://nsq.io/clients/client_libraries.html)。
### 启动
首先进入bin目录下，打开cmd，输入
```bash
nsqlookupd
```
然后就开启了nsq服务，端口号是4160
![image-20200901110859477](images/image-20200901110859477.png)
然后我们在启动一个cmd界面，输入下面的代码，启动nsqd，nsqd是一个守护进程，它用于接收、排队并向客户端发送消息，启动nsqd，指定 `-broadcast-address=127.0.0.1` 来配置广播地址
```bash
nsqd -broadcast-address=127.0.0.1
```
如果是在搭配 `nsqlookupd`，使用的模式下需要还指定`nsqlookupd`的地址
```bash
nsqd -broadcast-address=127.0.0.1 -lookupd-tcp-address=127.0.0.1:4160
```
启动成功的图片如下所示
![image-20200901111133414](images/image-20200901111133414.png)
### 安装
```bash
go get -u github.com/nsqio/go-nsq
```
### 生产者
一个简单的生产者示例代码如下：
```go
// nsq_producer/main.go
package main
import (
	"bufio"
	"fmt"
	"os"
	"strings"
	"github.com/nsqio/go-nsq"
)
// NSQ Producer Demo
var producer *nsq.Producer
// 初始化生产者
func initProducer(str string) (err error) {
	config := nsq.NewConfig()
	producer, err = nsq.NewProducer(str, config)
	if err != nil {
		fmt.Printf("create producer failed, err:%v\n", err)
		return err
	}
	return nil
}
func main() {
	nsqAddress := "127.0.0.1:4150"
	err := initProducer(nsqAddress)
	if err != nil {
		fmt.Printf("init producer failed, err:%v\n", err)
		return
	}
	reader := bufio.NewReader(os.Stdin) // 从标准输入读取
	for {
		data, err := reader.ReadString('\n')
		if err != nil {
			fmt.Printf("read string from stdin failed, err:%v\n", err)
			continue
		}
		data = strings.TrimSpace(data)
		if strings.ToUpper(data) == "Q" { // 输入Q退出
			break
		}
		// 向 'topic_demo' publish 数据
		err = producer.Publish("topic_demo", []byte(data))
		if err != nil {
			fmt.Printf("publish msg to nsq failed, err:%v\n", err)
			continue
		}
	}
}
```
将上面的代码编译执行，然后在终端输入两条数据`123`和`456`：
```bash
$ ./nsq_producer 
123
2018/10/22 18:41:20 INF    1 (127.0.0.1:4150) connecting to nsqd
456
```
使用浏览器打开`http://127.0.0.1:4171/`可以查看到类似下面的页面： 在下面这个页面能看到当前的`topic`信息：![nsqadmin界面1](images/nsqadmin1.png)
点击页面上的`topic_demo`就能进入一个展示更多详细信息的页面，在这个页面上我们可以查看和管理`topic`，同时能够看到目前在`LWZMBP:4151 (127.0.01:4151)`这个`nsqd`上有2条message。又因为没有消费者接入所以暂时没有创建`channel`。![nsqadmin界面2](images/nsqadmin2.png)
在`/nodes`这个页面我们能够很方便的查看当前接入`lookupd`的`nsqd`节点。![nsqadmin界面3](images/nsqadmin3.png)
这个`/counter`页面显示了处理的消息数量，因为我们没有接入消费者，所以处理的消息数量为0。![images/nsqadmin4.png)
在`/lookup`界面支持创建`topic`和`channel`。![nsqadmin界面5](images/nsqadmin5.png)
### 消费者
一个简单的消费者示例代码如下：
```go
// nsq_consumer/main.go
package main
import (
	"fmt"
	"os"
	"os/signal"
	"syscall"
	"time"
	"github.com/nsqio/go-nsq"
)
// NSQ Consumer Demo
// MyHandler 是一个消费者类型
type MyHandler struct {
	Title string
}
// HandleMessage 是需要实现的处理消息的方法
func (m *MyHandler) HandleMessage(msg *nsq.Message) (err error) {
	fmt.Printf("%s recv from %v, msg:%v\n", m.Title, msg.NSQDAddress, string(msg.Body))
	return
}
// 初始化消费者
func initConsumer(topic string, channel string, address string) (err error) {
	config := nsq.NewConfig()
	config.LookupdPollInterval = 15 * time.Second
	c, err := nsq.NewConsumer(topic, channel, config)
	if err != nil {
		fmt.Printf("create consumer failed, err:%v\n", err)
		return
	}
	consumer := &MyHandler{
		Title: "沙河1号",
	}
	c.AddHandler(consumer)
	// if err := c.ConnectToNSQD(address); err != nil { // 直接连NSQD
	if err := c.ConnectToNSQLookupd(address); err != nil { // 通过lookupd查询
		return err
	}
	return nil
}
func main() {
	err := initConsumer("topic_demo", "first", "127.0.0.1:4161")
	if err != nil {
		fmt.Printf("init consumer failed, err:%v\n", err)
		return
	}
	c := make(chan os.Signal)        // 定义一个信号的通道
	signal.Notify(c, syscall.SIGINT) // 转发键盘中断信号到c
	<-c                              // 阻塞
}
```
将上面的代码保存之后编译执行，就能够获取之前我们publish的两条消息了：
```bash
$ ./nsq_consumer 
2018/10/22 18:49:06 INF    1 [topic_demo/first] querying nsqlookupd http://127.0.0.1:4161/lookup?topic=topic_demo
2018/10/22 18:49:06 INF    1 [topic_demo/first] (127.0.0.1:4150) connecting to nsqd
沙河1号 recv from 127.0.0.1:4150, msg:123
沙河1号 recv from 127.0.0.1:4150, msg:456
```
同时在nsqadmin的`/counter`页面查看到处理的数据数量为2。![nsqadmin界面5](images/nsqadmin6.png)
关于`go-nsq`的更多内容请阅读[go-nsq的官方文档](https://godoc.org/github.com/nsqio/go-nsq)。
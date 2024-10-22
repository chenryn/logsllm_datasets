	// 成功交付的消息将在 success channel返回
	config.Producer.Return.Successes = true
	msg := &sarama.ProducerMessage{}
	msg.Topic = "web_log"
	msg.Value = sarama.StringEncoder("this is a test log")
	// 连接kafka，可以连接一个集群
	client, err := sarama.NewSyncProducer([]string{"127.0.0.1:9092"}, config)
	if err != nil {
		fmt.Println("producer closed, err: ", err)
	}
	fmt.Println("连接kafka成功！")
	// 定义延迟关闭
	defer client.Close()
	// 发送消息
	pid, offset, err := client.SendMessage(msg)
	if err != nil {
		fmt.Println("send msg failed, err:", err)
		return
	}
	fmt.Printf("pid:%v offset:%v \n", pid, offset)
}
```
## LogAgent编码
首先我们需要创建一个 kafka.go 用来初始化kafka和发送消息到kafka
```go
package kafka
import (
	"fmt"
	"github.com/Shopify/sarama"
)
// 专门往kafka写日志的模块
var (
	// 声明一个全局连接kafka的生产者
	client sarama.SyncProducer
)
// 初始化client
func Init()(err error)  {
	config := sarama.NewConfig()
	// tailf包使用，发送完数据需要 leader 和 follow都确定
	config.Producer.RequiredAcks = sarama.WaitForAll
	// 新选出一个partition
	config.Producer.Partitioner = sarama.NewRandomPartitioner
	// 成功交付的消息将在 success channel返回
	config.Producer.Return.Successes = true
	msg := &sarama.ProducerMessage{}
	msg.Topic = "web_log"
	msg.Value = sarama.StringEncoder("this is a test log")
	// 连接kafka，可以连接一个集群
	client, err = sarama.NewSyncProducer([]string{"127.0.0.1:9092"}, config)
	if err != nil {
		fmt.Println("producer closed, err: ", err)
	}
	fmt.Println("Kafka初始化成功")
	return err
}
// 发送消息到Kafka
func SendToKafka(topic, data string) {
	msg := &sarama.ProducerMessage{}
	msg.Topic = topic
	msg.Value = sarama.StringEncoder(data)
	// 发送到kafka
	pid, offset, err := client.SendMessage(msg)
	if err != nil {
		fmt.Println("send msg failed, err:", err)
		return
	}
	fmt.Println("发送消息：", data)
	fmt.Printf("发送成功~  pid:%v offset:%v \n", pid, offset)
}
```
然后我们在创建一个 taillog.go文件，用来记录日志
```go
package taillog
import (
	"fmt"
	"github.com/hpcloud/tail"
)
// 定义全局对象
var (
	// 声明一个全局连接kafka的生产者
	tailObj *tail.Tail
)
// 专门从日志文件收集日志的模块
func Init(fileName string)(err error ){
	// 定义配置文件
	config := tail.Config{
		ReOpen: true, // 重新打开，日志文件到了一定大小，就会分裂
		Follow: true, // 是否跟随
		Location: &tail.SeekInfo{Offset: 0, Whence: 2}, // 从文件的哪个位置开始读
		MustExist: false, // 是否必须存在，如果不存在是否报错
		Poll: true, //
	}
	tailObj, err = tail.TailFile(fileName, config)
	if err != nil {
		fmt.Println("tail file failed, err:", err)
		return
	}
	return err
}
// 读取日志，返回一个只读的chan
func ReadChan() <-chan *tail.Line {
	return tailObj.Lines
}
```
最后我们创建main.go作为启动类
```go
package main
import (
	"LogDemo/kafka"
	"LogDemo/taillog"
	"fmt"
	"time"
)
// logAgent入口程序
func run()  {
	// 1.读取日志
	for {
		select {
		case line := <-taillog.ReadChan():
			{
				// 2.发送到kafka
				kafka.SendToKafka("web_log", line.Text)
			}
		default:
			time.Sleep(1 * time.Second)
		}
	}
}
func main() {
	// 1. 初始化kafka连接
	err := kafka.Init()
	if err != nil {
		fmt.Printf("init Kafka failed, err:%v \n", err)
		return
	}
	// 2. 打开日志文件，准备收集
	err = taillog.Init("./my.log")
	if err != nil {
		fmt.Printf("Init taillog failed, err: %v \n", err)
		return
	}
	// 3.执行业务逻辑
	run()
}
```
最后我们启动main.go，然后往文件里面插入内容，然后就会将日志记录发送到kafka中
![image-20200909210434742](images/image-20200909210434742.png)
最后通过下面的脚本，来进行kafka的消息的消费
```bash
 .\kafka-console-consumer.bat --bootstrap-server=127.0.0.1:9092 --topic=web_log --from-beginning
```
然后就开始消费kafka中的消息
![image-20200909210448475](images/image-20200909210448475.png)
### 存在的问题
上述的代码还存在硬编码的问题，我们将通过配置文件将一些信息配置出来，这样能够提高代码的扩展性，这里我们用的是ini文件，创建一个 config.ini文件，填入配置信息
```ini
[kafka]
address=127.0.0.1:9092
topic=web_log
[taillog]
path:=./my.log
```
### 引入依赖
我们需要使用go-ini的依赖，来对我们的配置文件进行解析  ，[go-ini官网](https://github.com/go-ini/ini)
首先下载依赖
```bash
go get gopkg.in/ini.v1
```
然后通过下面的方式进行读取
```go
// 0. 加载配置文件
cfg, err := ini.Load("./conf/config.ini")
if err != nil {
    fmt.Printf("Fail to read file: %v", err)
    os.Exit(1)
}
// 典型读取操作，默认分区可以使用空字符串表示
fmt.Println("kafka address:", cfg.Section("kafka").Key("address").String())
fmt.Println("kafka topic:", cfg.Section("kafka").Key("topic").String())
fmt.Println("taillog path:", cfg.Section("taillog").Key("path").String())
```
优化后的main.go如下所示
```go
package main
import (
	"LogDemo/kafka"
	"LogDemo/taillog"
	"fmt"
	"gopkg.in/ini.v1"
	"os"
	"time"
)
// logAgent入口程序
func run()  {
	// 1.读取日志
	for {
		select {
		case line := <-taillog.ReadChan():
			{
				// 2.发送到kafka
				kafka.SendToKafka("web_log", line.Text)
			}
		default:
			time.Sleep(1 * time.Second)
		}
	}
}
func main() {
	// 0. 加载配置文件
	cfg, err := ini.Load("./conf/config.ini")
	if err != nil {
		fmt.Printf("Fail to read file: %v", err)
		os.Exit(1)
	}
	// 典型读取操作，默认分区可以使用空字符串表示
	fmt.Println("kafka address:", cfg.Section("kafka").Key("address").String())
	fmt.Println("kafka topic:", cfg.Section("kafka").Key("topic").String())
	fmt.Println("taillog path:", cfg.Section("taillog").Key("path").String())
	// 1. 初始化kafka连接
	address := []string{cfg.Section("kafka").Key("address").String()}
	topic := cfg.Section("taillog").Key("path").String()
	err = kafka.Init(address, topic)
	if err != nil {
		fmt.Printf("init Kafka failed, err:%v \n", err)
		return
	}
	// 2. 打开日志文件，准备收集
	err = taillog.Init(cfg.Section("taillog").Key("path").String())
	if err != nil {
		fmt.Printf("Init taillog failed, err: %v \n", err)
		return
	}
	// 3.执行业务逻辑
	run()
}
```
### 最终版本
上述的方式，还是存在一些问题，就是配置信息不能传递，只能在main方法里面，那么我们可以在定义一个结构体，conf.go
```go
package conf
type AppConf struct {
	KafkaConf `ini:"kafka"`
	TaillogConf `ini:"taillog"`
}
type KafkaConf struct {
	Address string `ini:"address"`
	Topic string `ini:"topic"`
}
type TaillogConf struct {
	FileName string `ini:"filename"`
}
```
然后原来的main.go改为
```go
package main
import (
	"LogDemo/conf"
	"LogDemo/kafka"
	"LogDemo/taillog"
	"fmt"
	"gopkg.in/ini.v1"
	"time"
)
var (
	cfg = new(conf.AppConf)
)
// logAgent入口程序
func run()  {
	// 1.读取日志
	for {
		select {
		case line := <-taillog.ReadChan():
			{
				// 2.发送到kafka
				kafka.SendToKafka(cfg.Topic, line.Text)
			}
		default:
			time.Sleep(1 * time.Second)
		}
	}
}
func main() {
	// 0. 加载配置文件
	// 方式2
	err := ini.MapTo(&cfg, "./conf/config.ini")
	if err != nil {
		fmt.Printf("load ini failed, err: %v \n", err)
		return
	}
	fmt.Println("读取到的配置信息", cfg)
	// 1. 初始化kafka连接
	address := []string{cfg.Address}
	topic := cfg.Topic
	err = kafka.Init(address, topic)
	if err != nil {
		fmt.Printf("init Kafka failed, err:%v \n", err)
		return
	}
	// 2. 打开日志文件，准备收集
	err = taillog.Init(cfg.FileName)
	if err != nil {
		fmt.Printf("Init taillog failed, err: %v \n", err)
		return
	}
	// 3.执行业务逻辑
	run()
}
```
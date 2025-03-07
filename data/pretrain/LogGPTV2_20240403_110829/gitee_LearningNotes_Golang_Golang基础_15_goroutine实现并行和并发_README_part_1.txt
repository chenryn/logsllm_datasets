# Golang goroutine channel 实现并发和并行
## 为什么要使用goroutine呢
需求：要统计1-10000000的数字中那些是素数，并打印这些素数？
素数：就是除了1和它本身不能被其他数整除的数
**实现方法：**
- 传统方法，通过一个for循环判断各个数是不是素数
- 使用并发或者并行的方式，将统计素数的任务分配给多个goroutine去完成，这个时候就用到了goroutine
- goroutine 结合 channel
## 进程、线程以及并行、并发
### 进程
进程（Process）就是程序在操作系统中的一次执行过程，是系统进行资源分配和调度的基本单位，进程是一个动态概念，是程序在执行过程中分配和管理资源的基本单位，每一个进程都有一个自己的地址空间。一个进程至少有5种基本状态，它们是：初始态，执行态，等待状态，就绪状态，终止状态。
通俗的讲进程就是一个正在执行的程序。
### 线程
线程是进程的一个执行实例，是程序执行的最小单元，它是比进程更小的能独立运行的基本单位
一个进程可以创建多个线程，同一个进程中多个线程可以并发执行 ，一个线程要运行的话，至少有一个进程
### 并发和并行
并发：多个线程同时竞争一个位置，竞争到的才可以执行，每一个时间段只有一个线程在执行。
并行：多个线程可以同时执行，每一个时间段，可以有多个线程同时执行。
通俗的讲多线程程序在单核CPU上面运行就是并发，多线程程序在多核CUP上运行就是并行，如果线程数大于CPU核数，则多线程程序在多个CPU上面运行既有并行又有并发
![image-20200723091802816](images/image-20200723091802816.png)
![image-20200723092334895](images/image-20200723092334895.png)
## Golang中协程（goroutine）以及主线程
golang中的主线程：（可以理解为线程/也可以理解为进程），在一个Golang程序的主线程上可以起多个协程。Golang中多协程可以实现并行或者并发。
**协程**：可以理解为用户级线程，这是对内核透明的，也就是系统并不知道有协程的存在，是完全由用户自己的程序进行调度的。Golang的一大特色就是从语言层面原生持协程，在函数或者方法前面加go关键字就可创建一个协程。可以说Golang中的协程就是goroutine。
![image-20200723092645188](images/image-20200723092645188.png)
Golang中的多协程有点类似于Java中的多线程
### 多协程和多线程
多协程和多线程：Golang中每个goroutine（协程）默认占用内存远比Java、C的线程少。
OS线程（操作系统线程）一般都有固定的栈内存（通常为2MB左右），一个goroutine（协程）占用内存非常小，只有2KB左右，多协程goroutine切换调度开销方面远比线程要少。
这也是为什么越来越多的大公司使用Golang的原因之一。
## goroutine的使用以及sync.WaitGroup
### 并行执行需求
在主线程（可以理解成进程）中，开启一个goroutine，该协程每隔50毫秒秒输出“你好golang"
在主线程中也每隔50毫秒输出“你好golang"，输出10次后，退出程序，要求主线程和goroutine同时执行。
这是时候，我们就可以开启协程来了，通过 go关键字开启
```go
// 协程需要运行的方法
func test()  {
	for i := 0; i < 5; i++ {
		fmt.Println("test 你好golang")
		time.Sleep(time.Millisecond * 100)
	}
}
func main() {
	// 通过go关键字，就可以直接开启一个协程
	go test()
	// 这是主进程执行的
	for i := 0; i < 5; i++ {
		fmt.Println("main 你好golang")
		time.Sleep(time.Millisecond * 100)
	}
}
```
运行结果如下，我们能够看到他们之间不存在所谓的顺序关系了
```go
main 你好golang
test 你好golang
main 你好golang
test 你好golang
test 你好golang
main 你好golang
main 你好golang
test 你好golang
test 你好golang
main 你好golang
```
但是上述的代码其实还有问题的，也就是说当主进程执行完毕后，不管协程有没有执行完成，都会退出
![image-20200723094125527](images/image-20200723094125527.png)
这是使用我们就需要用到  sync.WaitGroup等待协程
首先我们需要创建一个协程计数器
```go
// 定义一个协程计数器
var wg sync.WaitGroup
```
然后当我们开启协程的时候，我们要让计数器加1
```go
// 开启协程，协程计数器加1
wg.Add(1)
go test2()
```
当我们协程结束前，我们需要让计数器减1
```go
// 协程计数器减1
wg.Done()
```
完整代码如下
```go
// 定义一个协程计数器
var wg sync.WaitGroup
func test()  {
	// 这是主进程执行的
	for i := 0; i < 1000; i++ {
		fmt.Println("test1 你好golang", i)
		//time.Sleep(time.Millisecond * 100)
	}
	// 协程计数器减1
	wg.Done()
}
func test2()  {
	// 这是主进程执行的
	for i := 0; i < 1000; i++ {
		fmt.Println("test2 你好golang", i)
		//time.Sleep(time.Millisecond * 100)
	}
	// 协程计数器减1
	wg.Done()
}
func main() {
	// 通过go关键字，就可以直接开启一个协程
	wg.Add(1)
	go test()
	// 协程计数器加1
	wg.Add(1)
	go test2()
	// 这是主进程执行的
	for i := 0; i < 1000; i++ {
		fmt.Println("main 你好golang", i)
		//time.Sleep(time.Millisecond * 100)
	}
	// 等待所有的协程执行完毕
	wg.Wait()
	fmt.Println("主线程退出")
}
```
## 设置Go并行运行的时候占用的cpu数量
Go运行时的调度器使用GOMAXPROCS参数来确定需要使用多少个OS线程来同时执行Go代码。默认值是机器上的CPU核心数。例如在一个8核心的机器上，调度器会把Go代码同时调度到8个oS线程上。
Go 语言中可以通过runtime.GOMAXPROCS（）函数设置当前程序并发时占用的CPU逻辑核心数。
Go1.5版本之前，默认使用的是单核心执行。Go1.5版本之后，默认使用全部的CPU逻辑核心数。
```go
func main() {
	// 获取cpu个数
	npmCpu := runtime.NumCPU()
	fmt.Println("cup的个数:", npmCpu)
	// 设置允许使用的CPU数量
	runtime.GOMAXPROCS(runtime.NumCPU() - 1)
}
```
## for循环开启多个协程
类似于Java里面开启多个线程，同时执行
```go
func test(num int)  {
	for i := 0; i < 10; i++ {
		fmt.Printf("协程（%v）打印的第%v条数据 \n", num, i)
	}
	// 协程计数器减1
	vg.Done()
}
var vg sync.WaitGroup
func main() {
	for i := 0; i < 10; i++ {
		go test(i)
		vg.Add(1)
	}
	vg.Wait()
	fmt.Println("主线程退出")
}
```
因为我们协程会在主线程退出后就终止，所以我们还需要使用到  sync.WaitGroup来控制主线程的终止。
## Channel管道
管道是Golang在语言级别上提供的goroutine间的通讯方式，我们可以使用channel在多个goroutine之间传递消息。如果说goroutine是Go程序并发的执行体，channel就是它们之间的连接。channel是可以让一个goroutine发送特定值到另一个goroutine的通信机制。
Golang的并发模型是CSP（Communicating Sequential Processes），提倡通过通信共享内存而不是通过共享内存而实现通信。
Go语言中的管道（channel）是一种特殊的类型。管道像一个传送带或者队列，总是遵循先入先出（First In First Out）的规则，保证收发数据的顺序。每一个管道都是一个具体类型的导管，也就是声明channel的时候需要为其指定元素类型。
### channel类型
channel是一种类型，一种引用类型。声明管道类型的格式如下：
```go
// 声明一个传递整型的管道
var ch1 chan int
// 声明一个传递布尔类型的管道
var ch2 chan bool
// 声明一个传递int切片的管道
var ch3 chan []int
```
### 创建channel
声明管道后，需要使用make函数初始化之后才能使用
```go
make(chan 元素类型, 容量)
```
举例如下：
```go
// 创建一个能存储10个int类型的数据管道
ch1 = make(chan int, 10)
// 创建一个能存储4个bool类型的数据管道
ch2 = make(chan bool, 4)
// 创建一个能存储3个[]int切片类型的管道
ch3 = make(chan []int, 3)
```
### channel操作
管道有发送，接收和关闭的三个功能
发送和接收 都使用 <- 符号
现在我们先使用以下语句定义一个管道：
```go
ch := make(chan int, 3)
```
#### 发送
将数据放到管道内，将一个值发送到管道内
```go
// 把10发送到ch中
ch <- 10
```
#### 取操作
```go
x := <- ch
```
#### 关闭管道.
通过调用内置的close函数来关闭管道
```go
close(ch)
```
#### 完整示例
```go
// 创建管道
ch := make(chan int, 3)
// 给管道里面存储数据
ch <- 10
ch <- 21
ch <- 32
// 获取管道里面的内容
a := <- ch
fmt.Println("打印出管道的值：", a)
fmt.Println("打印出管道的值：", <- ch)
fmt.Println("打印出管道的值：", <- ch)
// 管道的值、容量、长度
fmt.Printf("地址：%v 容量：%v 长度：%v \n", ch, cap(ch), len(ch))
// 管道的类型
fmt.Printf("%T \n", ch)
// 管道阻塞（当没有数据的时候取，会出现阻塞，同时当管道满了，继续存也会）
<- ch  // 没有数据取，出现阻塞
ch <- 10
ch <- 10
ch <- 10
ch <- 10 // 管道满了，继续存，也出现阻塞
```
## for range从管道循环取值
当向管道中发送完数据时，我们可以通过close函数来关闭管道，当管道被关闭时，再往该管道发送值会引发panic，从该管道取值的操作会去完管道中的值，再然后取到的值一直都是对应类型的零值。那如何判断一个管道是否被关闭的呢？
```go
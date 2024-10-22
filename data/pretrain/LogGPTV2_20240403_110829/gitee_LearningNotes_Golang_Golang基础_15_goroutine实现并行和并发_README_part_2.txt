// 创建管道
ch := make(chan int, 10)
// 循环写入值
for i := 0; i  默认的管道是 可读可写
```go
// 定义一种可读可写的管道
var ch = make(chan int, 2)
ch  tip：使用select来获取数据的时候，不需要关闭chan，不然会出现问题
## Goroutine Recover解决协程中出现的Panic
```go
func sayHello()  {
	for i := 0; i < 10; i++ {
		fmt.Println("hello")
	}
}
func errTest()  {
	// 捕获异常
	defer func() {
		if err := recover(); err != nil {
			fmt.Println("errTest发生错误")
		}
	}()
	var myMap map[int]string
	myMap[0] = "10"
}
func main {
    go sayHello()
    go errTest()
}
```
当我们出现问题的时候，我们还是按照原来的方法，通过defer func创建匿名自启动
```go
// 捕获异常
defer func() {
    if err := recover(); err != nil {
        fmt.Println("errTest发生错误")
    }
}()
```
## Go中的并发安全和锁
如下面一段代码，我们在并发环境下进行操作，就会出现并发访问的问题
```go
var count = 0
var wg sync.WaitGroup
func test()  {
	count++
	fmt.Println("the count is : ", count)
	time.Sleep(time.Millisecond)
	wg.Done()
}
func main() {
	for i := 0; i < 20; i++ {
		wg.Add(1)
		go test()
	}
	time.Sleep(time.Second * 10)
}
```
### 互斥锁
互斥锁是传统并发编程中对共享资源进行访问控制的主要手段，它由标准库sync中的Mutex结构体类型表示。sync.Mutex类型只有两个公开的指针方法，Lock和Unlock。Lock锁定当前的共享资源，Unlock 进行解锁
```go
// 定义一个锁
var mutex sync.Mutex
// 加锁
mutex.Lock()
// 解锁
mutex.Unlock()
```
完整代码
```go
var count = 0
var wg sync.WaitGroup
var mutex sync.Mutex
func test()  {
	// 加锁
	mutex.Lock()
	count++
	fmt.Println("the count is : ", count)
	time.Sleep(time.Millisecond)
	wg.Done()
	// 解锁
	mutex.Unlock()
}
func main() {
	for i := 0; i < 20; i++ {
		wg.Add(1)
		go test()
	}
	time.Sleep(time.Second * 10)
}
```
通过下面命令，build的时候，可以查看是否具有竞争关系
```go
// 通过 -race 参数进行构建
go build -race main.go
// 运行插件
main.ext
```
### 读写互斥锁
互斥锁的本质是当一个goroutine访问的时候，其他goroutine都不能访问。这样在资源同步，避免竞争的同时也降低了程序的并发性能。程序由原来的并行执行变成了串行执行。
其实，当我们对一个不会变化的数据只做“读”操作的话，是不存在资源竞争的问题的。因为数据是不变的，不管怎么读取，多少goroutine同时读取，都是可以的。
所以问题不是出在“读”上，主要是修改，也就是“写”。修改的数据要同步，这样其他goroutine才可以感知到。所以真正的互斥应该是读取和修改、修改和修改之间，读和读是没有互斥操作的必要的。
因此，衍生出另外一种锁，叫做读写锁。
读写锁可以让多个读操作并发，同时读取，但是对于写操作是完全互斥的。也就是说，当一个goroutine进行写操作的时候，其他goroutine既不能进行读操作，也不能进行写操作。
GO中的读写锁由结构体类型sync.RWMutex表示。此类型的方法集合中包含两对方法：
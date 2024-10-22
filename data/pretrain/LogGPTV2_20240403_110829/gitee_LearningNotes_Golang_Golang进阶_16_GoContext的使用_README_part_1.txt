# Go Context的使用
在 Go http包的Server中，每一个请求在都有一个对应的 goroutine 去处理。请求处理函数通常会启动额外的 goroutine 用来访问后端服务，比如数据库和RPC服务。用来处理一个请求的 goroutine 通常需要访问一些与请求特定的数据，比如终端用户的身份认证信息、验证相关的token、请求的截止时间。 当一个请求被取消或超时时，所有用来处理该请求的 goroutine 都应该迅速退出，然后系统才能释放这些 goroutine 占用的资源。
## 来源
https://www.liwenzhou.com/posts/Go/go_context/
## 为什么需要Context
### 基本示例
```go
package main
import (
	"fmt"
	"sync"
	"time"
)
var wg sync.WaitGroup
// 初始的例子
func worker() {
	for {
		fmt.Println("worker")
		time.Sleep(time.Second)
	}
	// 如何接收外部命令实现退出
	wg.Done()
}
func main() {
	wg.Add(1)
	go worker()
	// 如何优雅的实现结束子goroutine
	wg.Wait()
	fmt.Println("over")
}
```
### 全局变量方式
```go
package main
import (
	"fmt"
	"sync"
	"time"
)
var wg sync.WaitGroup
var exit bool
// 全局变量方式存在的问题：
// 1. 使用全局变量在跨包调用时不容易统一
// 2. 如果worker中再启动goroutine，就不太好控制了。
func worker() {
	for {
		fmt.Println("worker")
		time.Sleep(time.Second)
		if exit {
			break
		}
	}
	wg.Done()
}
func main() {
	wg.Add(1)
	go worker()
	time.Sleep(time.Second * 3) // sleep3秒以免程序过快退出
	exit = true                 // 修改全局变量实现子goroutine的退出
	wg.Wait()
	fmt.Println("over")
}
```
### 通道方式
```go
package main
import (
	"fmt"
	"sync"
	"time"
)
var wg sync.WaitGroup
// 管道方式存在的问题：
// 1. 使用全局变量在跨包调用时不容易实现规范和统一，需要维护一个共用的channel
func worker(exitChan chan struct{}) {
LOOP:
	for {
		fmt.Println("worker")
		time.Sleep(time.Second)
		select {
		case <-exitChan: // 等待接收上级通知
			break LOOP
		default:
		}
	}
	wg.Done()
}
func main() {
	var exitChan = make(chan struct{})
	wg.Add(1)
	go worker(exitChan)
	time.Sleep(time.Second * 3) // sleep3秒以免程序过快退出
	exitChan <- struct{}{}      // 给子goroutine发送退出信号
	close(exitChan)
	wg.Wait()
	fmt.Println("over")
}
```
### 官方版的方案
```go
package main
import (
	"context"
	"fmt"
	"sync"
	"time"
)
var wg sync.WaitGroup
func worker(ctx context.Context) {
LOOP:
	for {
		fmt.Println("worker")
		time.Sleep(time.Second)
		select {
		case <-ctx.Done(): // 等待上级通知
			break LOOP
		default:
		}
	}
	wg.Done()
}
func main() {
	ctx, cancel := context.WithCancel(context.Background())
	wg.Add(1)
	go worker(ctx)
	time.Sleep(time.Second * 3)
	cancel() // 通知子goroutine结束
	wg.Wait()
	fmt.Println("over")
}
```
当子goroutine又开启另外一个goroutine时，只需要将ctx传入即可：
```go
package main
import (
	"context"
	"fmt"
	"sync"
	"time"
)
var wg sync.WaitGroup
func worker(ctx context.Context) {
	go worker2(ctx)
LOOP:
	for {
		fmt.Println("worker")
		time.Sleep(time.Second)
		select {
		case <-ctx.Done(): // 等待上级通知
			break LOOP
		default:
		}
	}
	wg.Done()
}
func worker2(ctx context.Context) {
LOOP:
	for {
		fmt.Println("worker2")
		time.Sleep(time.Second)
		select {
		case <-ctx.Done(): // 等待上级通知
			break LOOP
		default:
		}
	}
}
func main() {
	ctx, cancel := context.WithCancel(context.Background())
	wg.Add(1)
	go worker(ctx)
	time.Sleep(time.Second * 3)
	cancel() // 通知子goroutine结束
	wg.Wait()
	fmt.Println("over")
}
```
## Context初识
Go1.7加入了一个新的标准库`context`，它定义了`Context`类型，专门用来简化 对于处理单个请求的多个 goroutine 之间与请求域的数据、取消信号、截止时间等相关操作，这些操作可能涉及多个 API 调用。
对服务器传入的请求应该创建上下文，而对服务器的传出调用应该接受上下文。它们之间的函数调用链必须传递上下文，或者可以使用`WithCancel`、`WithDeadline`、`WithTimeout`或`WithValue`创建的派生上下文。当一个上下文被取消时，它派生的所有上下文也被取消。
## Context接口
`context.Context`是一个接口，该接口定义了四个需要实现的方法。具体签名如下：
```go
type Context interface {
    Deadline() (deadline time.Time, ok bool)
    Done() <-chan struct{}
    Err() error
    Value(key interface{}) interface{}
}
```
其中：
- `Deadline`方法需要返回当前`Context`被取消的时间，也就是完成工作的截止时间（deadline）；
- `Done`方法需要返回一个`Channel`，这个Channel会在当前工作完成或者上下文被取消之后关闭，多次调用`Done`方法会返回同一个Channel；
- ```
  Err
  ```
  方法会返回当前
  ```
  Context
  ```
  结束的原因，它只会在
  ```
  Done
  ```
  返回的Channel被关闭时才会返回非空的值；
  - 如果当前`Context`被取消就会返回`Canceled`错误；
  - 如果当前`Context`超时就会返回`DeadlineExceeded`错误；
- `Value`方法会从`Context`中返回键对应的值，对于同一个上下文来说，多次调用`Value` 并传入相同的`Key`会返回相同的结果，该方法仅用于传递跨API和进程间跟请求域的数据；
### Background()和TODO()
Go内置两个函数：`Background()`和`TODO()`，这两个函数分别返回一个实现了`Context`接口的`background`和`todo`。我们代码中最开始都是以这两个内置的上下文对象作为最顶层的`partent context`，衍生出更多的子上下文对象。
`Background()`主要用于main函数、初始化以及测试代码中，作为Context这个树结构的最顶层的Context，也就是根Context。
`TODO()`，它目前还不知道具体的使用场景，如果我们不知道该使用什么Context的时候，可以使用这个。
`background`和`todo`本质上都是`emptyCtx`结构体类型，是一个不可取消，没有设置截止时间，没有携带任何值的Context。
## With系列函数
此外，`context`包中还定义了四个With系列函数。
### WithCancel
`WithCancel`的函数签名如下：
```go
func WithCancel(parent Context) (ctx Context, cancel CancelFunc)
```
`WithCancel`返回带有新Done通道的父节点的副本。当调用返回的cancel函数或当关闭父上下文的Done通道时，将关闭返回上下文的Done通道，无论先发生什么情况。
取消此上下文将释放与其关联的资源，因此代码应该在此上下文中运行的操作完成后立即调用cancel。
```go
func gen(ctx context.Context) <-chan int {
		dst := make(chan int)
		n := 1
		go func() {
			for {
				select {
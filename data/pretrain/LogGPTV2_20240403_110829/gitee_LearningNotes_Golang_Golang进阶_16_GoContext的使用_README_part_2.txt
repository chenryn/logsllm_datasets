				case <-ctx.Done():
					return // return结束该goroutine，防止泄露
				case dst <- n:
					n++
				}
			}
		}()
		return dst
	}
func main() {
    // context.Background：传递的是根节点
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel() // 当我们取完需要的整数后调用cancel，相当于向ctx里面添加值
    // 遍历chan
	for n := range gen(ctx) {
		fmt.Println(n)
		if n == 5 {
			break
		}
	}
}
```
上面的示例代码中，`gen`函数在单独的goroutine中生成整数并将它们发送到返回的通道。 gen的调用者在使用生成的整数之后需要取消上下文，以免`gen`启动的内部goroutine发生泄漏。
### WithDeadline
`WithDeadline`的函数签名如下：
```go
func WithDeadline(parent Context, deadline time.Time) (Context, CancelFunc)
```
返回父上下文的副本，并将deadline调整为不迟于d。如果父上下文的deadline已经早于d，则WithDeadline(parent, d)在语义上等同于父上下文。当截止日过期时，当调用返回的cancel函数时，或者当父上下文的Done通道关闭时，返回上下文的Done通道将被关闭，以最先发生的情况为准。
取消此上下文将释放与其关联的资源，因此代码应该在此上下文中运行的操作完成后立即调用cancel。
```go
func main() {
    // 设置过期时间50毫秒
	d := time.Now().Add(50 * time.Millisecond)
	ctx, cancel := context.WithDeadline(context.Background(), d)
	// 尽管ctx会过期，但在任何情况下调用它的cancel函数都是很好的实践。
	// 如果不这样做，可能会使上下文及其父类存活的时间超过必要的时间。
	defer cancel()
	select {
	case <-time.After(1 * time.Second):
		fmt.Println("overslept")
	case <-ctx.Done():
		fmt.Println(ctx.Err())
	}
}
```
上面的代码中，定义了一个50毫秒之后过期的deadline，然后我们调用`context.WithDeadline(context.Background(), d)`得到一个上下文（ctx）和一个取消函数（cancel），然后使用一个select让主程序陷入等待：等待1秒后打印`overslept`退出或者等待ctx过期后退出。 因为ctx50秒后就过期，所以`ctx.Done()`会先接收到值，上面的代码会打印ctx.Err()取消原因。
### WithTimeout
`WithTimeout`的函数签名如下：
```go
func WithTimeout(parent Context, timeout time.Duration) (Context, CancelFunc)
```
`WithTimeout`返回`WithDeadline(parent, time.Now().Add(timeout))`。
取消此上下文将释放与其相关的资源，因此代码应该在此上下文中运行的操作完成后立即调用cancel，通常用于数据库或者网络连接的超时控制。具体示例如下：
```go
package main
import (
	"context"
	"fmt"
	"sync"
	"time"
)
// context.WithTimeout
var wg sync.WaitGroup
func worker(ctx context.Context) {
LOOP:
	for {
		fmt.Println("db connecting ...")
		time.Sleep(time.Millisecond * 10) // 假设正常连接数据库耗时10毫秒
		select {
		case <-ctx.Done(): // 50毫秒后自动调用
			break LOOP
		default:
		}
	}
	fmt.Println("worker done!")
	wg.Done()
}
func main() {
	// 设置一个50毫秒的超时
	ctx, cancel := context.WithTimeout(context.Background(), time.Millisecond*50)
	wg.Add(1)
	go worker(ctx)
	time.Sleep(time.Second * 5)
	cancel() // 通知子goroutine结束
	wg.Wait()
	fmt.Println("over")
}
```
### WithValue
`WithValue`函数能够将请求作用域的数据与 Context 对象建立关系。声明如下：
```go
func WithValue(parent Context, key, val interface{}) Context
```
`WithValue`返回父节点的副本，其中与key关联的值为val。
仅对API和进程间传递请求域的数据使用上下文值，而不是使用它来传递可选参数给函数。
所提供的键必须是可比较的，并且不应该是`string`类型或任何其他内置类型，以避免使用上下文在包之间发生冲突。`WithValue`的用户应该为键定义自己的类型。为了避免在分配给interface{}时进行分配，上下文键通常具有具体类型`struct{}`。或者，导出的上下文关键变量的静态类型应该是指针或接口。
```go
package main
import (
	"context"
	"fmt"
	"sync"
	"time"
)
// context.WithValue
type TraceCode string
var wg sync.WaitGroup
func worker(ctx context.Context) {
	key := TraceCode("TRACE_CODE")
    // .(string) 是类型断言
	traceCode, ok := ctx.Value(key).(string) // 在子goroutine中获取trace code
	if !ok {
		fmt.Println("invalid trace code")
	}
LOOP:
	for {
		fmt.Printf("worker, trace code:%s\n", traceCode)
		time.Sleep(time.Millisecond * 10) // 假设正常连接数据库耗时10毫秒
		select {
		case <-ctx.Done(): // 50毫秒后自动调用
			break LOOP
		default:
		}
	}
	fmt.Println("worker done!")
	wg.Done()
}
func main() {
	// 设置一个50毫秒的超时
	ctx, cancel := context.WithTimeout(context.Background(), time.Millisecond*50)
	// 在系统的入口中设置trace code传递给后续启动的goroutine实现日志数据聚合
	ctx = context.WithValue(ctx, TraceCode("TRACE_CODE"), "12512312234")
	wg.Add(1)
	go worker(ctx)
	time.Sleep(time.Second * 5)
	cancel() // 通知子goroutine结束
	wg.Wait()
	fmt.Println("over")
}
```
## 使用Context的注意事项
- 推荐以参数的方式显示传递Context
- 以Context作为参数的函数方法，应该把Context作为第一个参数。
- 给一个函数方法传递Context的时候，不要传递nil，如果不知道传递什么，就使用context.TODO()
- Context的Value相关方法应该传递请求域的必要数据，不应该用于传递可选参数
- Context是线程安全的，可以放心的在多个goroutine中传递
## 客户端超时取消示例
调用服务端API时如何在客户端实现超时控制？
### server端
```go
// context_timeout/server/main.go
package main
import (
	"fmt"
	"math/rand"
	"net/http"
	"time"
)
// server端，随机出现慢响应
func indexHandler(w http.ResponseWriter, r *http.Request) {
	number := rand.Intn(2)
	if number == 0 {
		time.Sleep(time.Second * 10) // 耗时10秒的慢响应
		fmt.Fprintf(w, "slow response")
		return
	}
	fmt.Fprint(w, "quick response")
}
func main() {
	http.HandleFunc("/", indexHandler)
	err := http.ListenAndServe(":8000", nil)
	if err != nil {
		panic(err)
	}
}
```
### client端
```go
// context_timeout/client/main.go
package main
import (
	"context"
	"fmt"
	"io/ioutil"
	"net/http"
	"sync"
	"time"
)
// 客户端
type respData struct {
	resp *http.Response
	err  error
}
func doCall(ctx context.Context) {
	transport := http.Transport{
	   // 请求频繁可定义全局的client对象并启用长链接
	   // 请求不频繁使用短链接
	   DisableKeepAlives: true, 	}
	client := http.Client{
		Transport: &transport,
	}
	respChan := make(chan *respData, 1)
	req, err := http.NewRequest("GET", "http://127.0.0.1:8000/", nil)
	if err != nil {
		fmt.Printf("new requestg failed, err:%v\n", err)
		return
	}
	req = req.WithContext(ctx) // 使用带超时的ctx创建一个新的client request
	var wg sync.WaitGroup
	wg.Add(1)
	defer wg.Wait()
	go func() {
		resp, err := client.Do(req)
		fmt.Printf("client.do resp:%v, err:%v\n", resp, err)
		rd := &respData{
			resp: resp,
			err:  err,
		}
		respChan <- rd
		wg.Done()
	}()
	select {
	case <-ctx.Done():
		//transport.CancelRequest(req)
		fmt.Println("call api timeout")
	case result := <-respChan:
		fmt.Println("call server api success")
		if result.err != nil {
			fmt.Printf("call server api failed, err:%v\n", result.err)
			return
		}
		defer result.resp.Body.Close()
		data, _ := ioutil.ReadAll(result.resp.Body)
		fmt.Printf("resp:%v\n", string(data))
	}
}
func main() {
	// 定义一个100毫秒的超时
	ctx, cancel := context.WithTimeout(context.Background(), time.Millisecond*100)
	defer cancel() // 调用cancel释放子goroutine资源
	doCall(ctx)
}
```
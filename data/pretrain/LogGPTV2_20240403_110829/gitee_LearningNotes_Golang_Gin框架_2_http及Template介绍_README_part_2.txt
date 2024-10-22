len
    返回它的参数的整数类型长度
index
    执行结果为第一个参数以剩下的参数为索引/键指向的值；
    如"index x 1 2 3"返回x[1][2][3]的值；每个被索引的主体必须是数组、切片或者字典。
print
    即fmt.Sprint
printf
    即fmt.Sprintf
println
    即fmt.Sprintln
html
    返回与其参数的文本表示形式等效的转义HTML。
    这个函数在html/template中不可用。
urlquery
    以适合嵌入到网址查询中的形式返回其参数的文本表示的转义值。
    这个函数在html/template中不可用。
js
    返回与其参数的文本表示形式等效的转义JavaScript。
call
    执行结果是调用第一个参数的返回值，该参数必须是函数类型，其余参数作为调用该函数的参数；
    如"call .X.Y 1 2"等价于go语言里的dot.X.Y(1, 2)；
    其中Y是函数类型的字段或者字典的值，或者其他类似情况；
    call的第一个参数的执行结果必须是函数类型的值（和预定义函数如print明显不同）；
    该函数类型值必须有1到2个返回值，如果有2个则后一个必须是error接口类型；
    如果有2个返回值的方法返回的error非nil，模板执行会中断并返回给调用模板执行者该错误；
```
### 比较函数
布尔函数会将任何类型的零值视为假，其余视为真。
下面是定义为函数的二元比较运算的集合：
```template
eq      如果arg1 == arg2则返回真
ne      如果arg1 != arg2则返回真
lt      如果arg1  arg2则返回真
ge      如果arg1 >= arg2则返回真
```
为了简化多参数相等检测，eq（只有eq）可以接受2个或更多个参数，它会将第一个参数和其余参数依次比较，返回下式的结果：
```template
{{eq arg1 arg2 arg3}}
```
比较函数只适用于基本类型（或重定义的基本类型，如”type Celsius float32”）。但是，整数和浮点数不能互相比较。
### 自定义函数
Go的模板支持自定义函数。
```go
package main
import (
	"fmt"
	"html/template"
	"net/http"
	"os"
)
/**
 * @Description f1函数
 * @Param 
 * @return
 **/
func f1(w http.ResponseWriter, r *http.Request) {
	// 定义模板
	// 解析模板
	// 获取项目的绝对路径
	wd, err := os.Getwd()
	if err != nil {
		fmt.Printf("get wd failed, err:%v \n", wd)
		return
	}
	// 定义一个自定义函数
	// 要么只有一个返回值，要么有两个返回值，第二个返回值必须是error类型
	kua := func(name string)(string, error) {
		return name + "年轻又帅气!", nil
	}
	// 创建一个名字为f的模板对象。注意，这个名字一定要和模板的名字对应上
	tmpl := template.New("hello.tmpl")
	// 告诉模板引擎，我现在多了一个自定义的函数kua
	tmpl.Funcs(template.FuncMap{
		"kua": kua,
	})
	// 解析模板
	_, err = tmpl.ParseFiles( wd + "\\lesson06\\hello.tmpl")
	if err != nil {
		fmt.Printf("parse template failed, err:%v \n", err)
		return
	}
	// 采用一个map
	m1 := map[string]interface{}{
		"Name": "小王子",
		"Age": 18,
		"Gender": "男",
	}
	// 渲染模板
	tmpl.Execute(w, m1)
}
func main() {
	http.HandleFunc("/hello", f1)
	err := http.ListenAndServe(":9090", nil)
	if err != nil {
		fmt.Println("HTTP server failed,err:", err)
		return
	}
}
```
我们可以在模板文件`hello.tmpl`中按照如下方式使用我们自定义的`kua`函数了。
```template
{{kua .Name}}
```
最后运行的结果
![image-20200916101259659](images/image-20200916101259659.png)
### 模板的嵌套template
我们可以在template中嵌套其他的template。这个template可以是单独的文件，也可以是通过`define`定义的template。
举个例子： `t.tmpl`文件内容如下：
```template
    tmpl test
    测试嵌套template语法
    {{template "ul.tmpl"}}
    {{template "ol.tmpl"}}
{{ define "ol.tmpl"}}
    吃饭
    睡觉
    打豆豆
{{end}}
```
`ul.tmpl`文件内容如下：
```template
    注释
    日志
    测试
```
我们注册一个`templDemo`路由处理函数.
```go
http.HandleFunc("/tmpl", tmplDemo)
```
`tmplDemo`函数的具体内容如下：
```go
func tmplDemo(w http.ResponseWriter, r *http.Request) {
	tmpl, err := template.ParseFiles("./t.tmpl", "./ul.tmpl")
	if err != nil {
		fmt.Println("create template failed, err:", err)
		return
	}
	user := UserInfo{
		Name:   "小王子",
		Gender: "男",
		Age:    18,
	}
	tmpl.Execute(w, user)
}
```
**注意**：在解析模板时，被嵌套的模板一定要在后面解析，例如上面的示例中`t.tmpl`模板中嵌套了`ul.tmpl`，所以`ul.tmpl`要在`t.tmpl`后进行解析。
### block
```template
{{block "name" pipeline}} T1 {{end}}
```
`block`是定义模板`{{define "name"}} T1 {{end}}`和执行`{{template "name" pipeline}}`缩写，典型的用法是定义一组根模板，然后通过在其中重新定义块模板进行自定义。
定义一个根模板`templates/base.tmpl`，内容如下：
```template
    Go Templates
    {{block "content" . }}{{end}}
```
然后定义一个`templates/index.tmpl`，”继承”`base.tmpl`：
```tempalte
{{template "base.tmpl"}}
{{define "content"}}
    Hello world!
{{end}}
```
然后使用`template.ParseGlob`按照正则匹配规则解析模板文件，然后通过`ExecuteTemplate`渲染指定的模板：
```go
func index(w http.ResponseWriter, r *http.Request){
	tmpl, err := template.ParseGlob("templates/*.tmpl")
	if err != nil {
		fmt.Println("create template failed, err:", err)
		return
	}
	err = tmpl.ExecuteTemplate(w, "index.tmpl", nil)
	if err != nil {
		fmt.Println("render template failed, err:", err)
		return
	}
}
```
如果我们的模板名称冲突了，例如不同业务线下都定义了一个`index.tmpl`模板，我们可以通过下面两种方法来解决。
1. 在模板文件开头使用`{{define 模板名}}`语句显式的为模板命名。
2. 可以把模板文件存放在`templates`文件夹下面的不同目录中，然后使用`template.ParseGlob("templates/**/*.tmpl")`解析模板。
### 修改默认的标识符
Go标准库的模板引擎使用的花括号`{{`和`}}`作为标识，而许多前端框架（如`Vue`和 `AngularJS`）也使用`{{`和`}}`作为标识符，所以当我们同时使用Go语言模板引擎和以上前端框架时就会出现冲突，这个时候我们需要修改标识符，修改前端的或者修改Go语言的。这里演示如何修改Go语言模板引擎默认的标识符：
```go
template.New("test").Delims("{[", "]}").ParseFiles("./t.tmpl")
```
最后我们在渲染的时候
```html
    自定义模板函数
姓名: {[.Name]}
性别: {[.Gender]}
年龄: {[.Age]}
```
最后运行结果，发现也能够正常显示
![image-20200916214044623](images/image-20200916214044623.png)
## text/template与html/tempalte的区别
`html/template`针对的是需要返回HTML内容的场景，在模板渲染过程中会对一些有风险的内容进行转义，以此来防范跨站脚本攻击。
例如，我定义下面的模板文件：
```template
    Hello
    {{.}}
```
这个时候传入一段JS代码并使用`html/template`去渲染该文件，会在页面上显示出转义后的JS内容。 `alert('嘿嘿嘿')` 这就是`html/template`为我们做的事。
但是在某些场景下，我们如果相信用户输入的内容，不想转义的话，可以自行编写一个safe函数，手动返回一个`template.HTML`类型的内容。示例如下：
```go
func xss(w http.ResponseWriter, r *http.Request){
	tmpl,err := template.New("xss.tmpl").Funcs(template.FuncMap{
		"safe": func(s string)template.HTML {
			return template.HTML(s)
		},
	}).ParseFiles("./xss.tmpl")
	if err != nil {
		fmt.Println("create template failed, err:", err)
		return
	}
	jsStr := ``
	err = tmpl.Execute(w, jsStr)
	if err != nil {
		fmt.Println(err)
	}
}
```
这样我们只需要在模板文件不需要转义的内容后面使用我们定义好的safe函数就可以了。
```template
{{ . | safe }}
```
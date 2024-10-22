```go
/**
	定义一个人结构体
 */
type Person struct {
	string
	int
}
func main() {
	// 结构体的匿名字段
	var person = Person{
		"张三",
		18
	}
}
```
结构体的字段类型可以是：基本数据类型，也可以是切片、Map 以及结构体
如果结构体的字段类似是：指针、slice、和 map 的零值都是nil，即还没有分配空间
如果需要使用这样的字段，需要先make，才能使用
```go
/**
	定义一个人结构体
 */
type Person struct {
	name string
	age int
	hobby []string
	mapValue map[string]string
}
func main() {
	// 结构体的匿名字段
	var person = Person{}
	person.name = "张三"
	person.age = 10
	// 给切片申请内存空间
	person.hobby = make([]string, 4, 4)
	person.hobby[0] = "睡觉"
	person.hobby[1] = "吃饭"
	person.hobby[2] = "打豆豆"
	// 给map申请存储空间
	person.mapValue = make(map[string]string)
	person.mapValue["address"] = "北京"
	person.mapValue["phone"] = "123456789"
	// 加入#打印完整信息
	fmt.Printf("%#v", person)
}
```
同时我们还支持结构体的嵌套，如下所示
```go
// 用户结构体
type User struct {
	userName string
	password string
	sex string
	age int
	address Address // User结构体嵌套Address结构体
}
// 收货地址结构体
type Address struct {
	name string
	phone string
	city string
}
func main() {
	var u User
	u.userName = "moguBlog"
	u.password = "123456"
	u.sex = "男"
	u.age = 18
	var address Address
	address.name = "张三"
	address.phone = "110"
	address.city = "北京"
	u.address = address
	fmt.Printf("%#v", u)
}
```
## 嵌套结构体的字段名冲突
嵌套结构体内部可能存在相同的字段名，这个时候为了避免歧义，需要指定具体的内嵌结构体的字段。（例如，父结构体中的字段 和 子结构体中的字段相似）
默认会从父结构体中寻找，如果找不到的话，再去子结构体中在找
如果子类的结构体中，同时存在着两个相同的字段，那么这个时候就会报错了，因为程序不知道修改那个字段的为准。
## 结构体的继承
结构体的继承，其实就类似于结构体的嵌套，如下所示，我们定义了两个结构体，分别是Animal 和 Dog，其中每个结构体都有各自的方法，然后通过Dog结构体 继承于 Animal结构体
```go
// 用户结构体
type Animal struct {
	name string
}
func (a Animal) run() {
	fmt.Printf("%v 在运动 \n", a.name)
}
// 子结构体
type Dog struct {
	age int
	// 通过结构体嵌套，完成继承
	Animal
}
func (dog Dog) wang()  {
	fmt.Printf("%v 在汪汪汪 \n", dog.name)
}
func main() {
	var dog = Dog{
		age: 10,
		Animal: Animal{
			name: "阿帕奇",
		},
	}
	dog.run();
	dog.wang();
}
```
运行后，发现Dog拥有了父类的方法
```bash
阿帕奇 在运动 
阿帕奇 在汪汪汪
```
## Go中的结构体和Json相互转换
JSON（JavaScript Object Notation）是一种轻量级的数据交换格式。易于人阅读和编写。同时也易于机器解析和生成。RESTfull Api接口中返回的数据都是json数据。
```json
{
    "name": "张三",
    "age": 15
}
```
比如我们Golang要给App或者小程序提供Api接口数据，这个时候就需要涉及到结构体和Json之间的相互转换
Golang JSON序列化是指把结构体数据转化成JSON格式的字符串，Golang JSON的反序列化是指把JSON数据转化成Golang中的结构体对象
Golang中的序列化和反序列化主要通过“encoding/json”包中的 json.Marshal() 和 son.Unmarshal()
```go
// 定义一个学生结构体，注意结构体的首字母必须大写，代表公有，否则将无法转换
type Student struct {
	ID string
	Gender string
	Name string
	Sno string
}
func main() {
	var s1 = Student{
		ID: "12",
		Gender: "男",
		Name: "李四",
		Sno: "s001",
	}
	// 结构体转换成Json（返回的是byte类型的切片）
	jsonByte, _ := json.Marshal(s1)
	jsonStr := string(jsonByte)
	fmt.Printf(jsonStr)
}
```
将字符串转换成结构体类型
```go
// 定义一个学生结构体，注意结构体的首字母必须大写，代表公有，否则将无法转换
type Student struct {
	ID string
	Gender string
	Name string
	Sno string
}
func main() {
	// Json字符串转换成结构体
	var str = `{"ID":"12","Gender":"男","Name":"李四","Sno":"s001"}`
	var s2 = Student{}
	// 第一个是需要传入byte类型的数据，第二参数需要传入转换的地址
	err := json.Unmarshal([]byte(str), &s2)
	if err != nil {
		fmt.Printf("转换失败 \n")
	} else {
		fmt.Printf("%#v \n", s2)
	}
}
```
### 注意
我们想要实现结构体转换成字符串，必须保证结构体中的字段是公有的，也就是首字母必须是大写的，这样才能够实现结构体 到 Json字符串的转换。
## 结构体标签Tag
Tag是结构体的元信息，可以在运行的时候通过反射的机制读取出来。Tag在结构体字段的后方定义，由一对反引号包裹起来，具体的格式如下：
```json
key1："value1" key2："value2"
```
结构体tag由一个或多个键值对组成。键与值使用冒号分隔，值用双引号括起来。同一个结构体字段可以设置多个键值对tag，不同的键值对之间使用空格分隔。
注意事项：为结构体编写Tag时，必须严格遵守键值对的规则。结构体标签的解析代码的容错能力很差，一旦格式写错，编译和运行时都不会提示任何错误，通过反射也无法正确取值。例如不要在key和value之间添加空格。
如下所示，我们通过tag标签，来转换字符串的key
```go
// 定义一个Student体，使用结构体标签
type Student2 struct {
	Id string `json:"id"` // 通过指定tag实现json序列化该字段的key
	Gender string `json:"gender"`
	Name string `json:"name"`
	Sno string `json:"sno"`
}
func main() {
	var s1 = Student2{
		Id: "12",
		Gender: "男",
		Name: "李四",
		Sno: "s001",
	}
	// 结构体转换成Json
	jsonByte, _ := json.Marshal(s1)
	jsonStr := string(jsonByte)
	fmt.Println(jsonStr)
	// Json字符串转换成结构体
	var str = `{"Id":"12","Gender":"男","Name":"李四","Sno":"s001"}`
	var s2 = Student2{}
	// 第一个是需要传入byte类型的数据，第二参数需要传入转换的地址
	err := json.Unmarshal([]byte(str), &s2)
	if err != nil {
		fmt.Printf("转换失败 \n")
	} else {
		fmt.Printf("%#v \n", s2)
	}
}
```
## 嵌套结构体和Json序列化反序列化
和刚刚类似，我们同样也是使用的是 json.Marshal()
```go
// 嵌套结构体 到 Json的互相转换
// 定义一个Student结构体
type Student3 struct {
	Id int
	Gender string
	Name string
}
// 定义一个班级结构体
type Class struct {
	Title string
	Students []Student3
}
func main() {
	var class = Class{
		Title: "1班",
		Students: make([]Student3, 0),
	}
	for i := 0; i < 10; i++ {
		s := Student3{
			Id: i + 1,
			Gender: "男",
			Name: fmt.Sprintf("stu_%v", i + 1),
		}
		class.Students = append(class.Students, s)
	}
	fmt.Printf("%#v \n", class)
	// 转换成Json字符串
	strByte, err := json.Marshal(class)
	if err != nil {
		fmt.Println("打印失败")
	} else {
		fmt.Println(string(strByte))
	}
}
```
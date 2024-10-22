const bigHumpPlaceholder = /\$VAR_BIG_HUMP\$/g
//连字符格式占位符
const hyphenPlaceholder = /\$VAR_HYPHEN\$/g
//常量格式占位符
const constantPlaceholder = /\$VAR_CONSTANT\$/g
//表名占位符
const sqlTableNamePlaceholder = /\$MY_SQL_TABLE_NAME\$/g
//类名占位符
const classNamePlaceholder = /\$VAR_CLASS_NAME\$/g
```
- 将替换好的代码写入对应目录下
当实现了自定义的代码生成器后，第一次生成一个模块的代码时，满满的都是成就感😊
## 如何运行项目
首先先克隆仓库 **pupu_blog** 项目
```bash
git clone https://gitee.com/hrbust_cheny/pupu_blog.git
```
新建数据库 **pupublog** ，然后在本地导入数据库 **pupublog2.sql**，脚本位于 **/koa-blog-service/** 目录下，执行下面的`sql`语句，新建管理员用户： 创建了一个账号为admin的用户，密码是123123
```BASH
delete from t_admin_user where uid = '-1';
insert into t_admin_user( uid, user_name, user_password, order_num, create_time, update_time ) values ('-1','admin','$2a$10$2veC0JLAmmOavUlyyDN25.3vRix0nyH9Vf5lAcI8DRyQgKGnQBKVG',-1,localtime(),localtime());
```
### 运行后端项目
然后开始给node 项目  **koa-blog-service** 目录下，安装依赖
```
## 进入到 koa-blog-service 目录下，安装依赖 /pupublog/koa-blog-service
npm install --registry=https://registry.npm.taobao.org
## 全局安装 supervisor，文件变更会自动重启node服务
npm install -g supervisor
```
安装完依赖后，打开项目，找到 **koa-blog-service/src/constant/config.js** 文件，然后修改如下配置
```JS
// /koa-blog-service/src/constant/config.js
// mysql配置
const database = {
    host: 'localhost', // 连接的服务器
    port: 3306, // mysql服务运行的端口
    database: 'pupublog', // 连接的数据库
    user: 'root', // 你数据库的用户名
    password: 'root' //数据库密码
}
/**
 * 1、如果是本地运行
 *  http://localhost:20517
 * 2、如果是部署到服务器，正式生产环境
 *  http://你的ip:20517 或者是你的域名
 * 
 */
const baseUrl = 'http://localhost:20517'
/**
 * Gitee第三方登录的相关参数
 */
const giteeLogin = {
    client_id: '你自己申请的客户id',
    client_secret: '你自己申请的密钥',
    expires: 3600, // token默认过期时间，单位是秒 3600s就是一小时
}
```
修改完成后，执行 **npm run dev** 运行项目
执行成功后，会显示运行的端口号，表示 **node** 后端服务已经运行成功
![启动后端项目](images/image-20211031111419525.png)
如果想检验的话，可以复制打开，看能否出现对应的 **Swagger** 接口文档
![打开Swagger项目](images/image-20211031111752711.png)
### 运行前端项目
首先运行管理端  **vue-blog-admin**，到目录 **pupu_blog\vue-blog-admin** 下执行下面命令
```bash
## 安装依赖
npm install --registry=https://registry.npm.taobao.org
## 启动管理端项目
npm run dev
```
运行成功后的，会自动打开 http://localhost:20519/ 
![后端页面](images/image-20211031145723002.png)
然后再运行管理端  **vue-blog-web**，到目录 **pupu_blog\vue-blog-admin** 下执行下面命令
```bash
## 安装依赖
npm install --registry=https://registry.npm.taobao.org
## 启动管理端项目
npm run dev
```
运行成功后，会打开  http://localhost:20518/
![前端页面](images/image-20211031183015300.png)
## 最后
前几天在蘑菇博客交流群里给大家看了一下实现的效果，得到了陌溪大佬的肯定，还是很开心的。
生活还在继续，短暂的停歇一下，继续向着自己的目标迈进吧，加油加油💪
本人是一年开发经验的小前端，项目是在空闲时间完成的，后期还会慢慢完善，目前先暂停一阵，备战面试~
另外附上项目地址，感兴趣的小伙伴可以帮忙点个star关注一下🙏，也欢迎大家提 **issue** 和留言，如哪里有错误的地方，欢迎指正，让我们共同进步💪
> 项目线上地址：
>
> http://bnbiye.cn
>
> 项目仓库地址：
>
> https://gitee.com/hrbust_cheny/pupu_blog
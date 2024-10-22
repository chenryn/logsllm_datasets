# SpringBoot+Vue如何集成第三方登录登录JustAuth
## 前言
这两天打算给蘑菇博客增加第三方登录模块，所有对目前的第三方登录的Github和Gitee中的Demo进行的调查，发现在gitee有个做的非常不错的项目：史上最全的整合第三方登录的开源库。目前已支持Github、Gitee、微博、钉钉、百度、Coding、腾讯云开发者平台、OSChina、支付宝、QQ、微信、淘宝、Google、Facebook、抖音、领英、小米、微软、今日头条、Teambition、StackOverflow、Pinterest、人人、华为、企业微信、酷家乐、Gitlab、美团、饿了么和推特等第三方平台的授权登录。 Login, so easy!
JustAuth仓库：https://gitee.com/yadong.zhang/JustAuth
JustAuth文档：https://docs.justauth.whnb.wang/#/
## 编写登录页面Vue样式和代码
首先需要编写一个登录框代码，下面是使用vue创建了一个组件 LoginBox，同时里面还引入了阿里矢量库中的几个图标，感兴趣的小伙伴可以查看这篇博客：[Vue项目使用阿里巴巴矢量图标库](http://moguit.cn/#/info?blogUid=1310f62f726ef0892e1de19bc14bba09)
```vue
          登录
          X
          登录
          注册
              &#xe602;
              &#xe64a;
              &#xe601;
              &#xe66f;
        登录过的用户请沿用之前的登录方式
          登录
          X
          注册
          返回登录
        注册后，需要到邮箱进行邮件认证~
```
下面是运行后的结果如下所示
![image-20191230091751151](images/image-20191230091751151.png)
因为目前没打算自己制作登录和注册功能，所以用户名、密码、以及登录和注册都被设置成disabled了，下面是引入的接口：login
```javascript
import request from '@/utils/request'
export function login(params) {
  return request({
    url: process.env.WEB_API + '/oauth/render',
    method: 'post',
    params
  })
}
```
## 引入第三方登录
完成了前端的页面后，我们就需要撰写后端代码了
首先需要引入JustAuth的Maven依赖，我们在pom文件中添加对应依赖
```xml
    me.zhyd.oauth
    JustAuth
    1.13.1
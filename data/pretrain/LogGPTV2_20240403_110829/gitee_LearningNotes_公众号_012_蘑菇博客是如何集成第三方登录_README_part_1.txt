## 前言
大家好，我是**陌溪**
这篇主要给搭建讲解的是，蘑菇博客项目是如何集成第三方登录。陌溪在做第三方登录的时候，也没有上来就造轮子，而是先在 **Gitee** 中找到了一个第三方登录的开源库：**JustAuth**。
**JustAuth**，如你所见，它仅仅是一个**第三方授权登录**的**工具类库**，它可以让我们脱离繁琐的第三方登录 SDK，让登录变得 **So easy!**  **JustAuth** 集成了诸如：**Github**、**Gitee**、支付宝、新浪微博、微信、Google、Facebook、Twitter、StackOverflow等国内外数十家第三方平台。
>JustAuth仓库：https://gitee.com/yadong.zhang/JustAuth
>
>JustAuth文档：https://docs.justauth.whnb.wang/#/
## 编写登录页面
首先需要编写一个登录框代码，下面是陌溪使用 **Vue** 编写的一个组件 **LoginBox.vue**，同时里面还引入了**阿里矢量库**中的几个图标，感兴趣的小伙伴可以查看这篇博客：[蘑菇博客前端页面如何引入矢量图标](https://mp.weixin.qq.com/s/mO0HlIZsjdluY16YW8rOdA)
```html
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
![登录框](images/1577773839268.png)
下面是第三方登录的请求接口
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
首先需要引入 **JustAuth** 的 **Maven** 依赖，在 **pom** 文件中添加对应依赖
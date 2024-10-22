# 蘑菇博客
- 蘑菇博客，一个基于微服务架构的前后端分离博客系统。前台使用Vue + Element , 后端使用spring boot + spring cloud + mybatis-plus进行开发，使用 Jwt + Spring Security做登录验证和权限校验，使用ElasticSearch和Solr作为全文检索服务，使用Github Actions完成博客的持续集成，文件支持上传七牛云。
[![star](https://gitee.com/moxi159753/mogu_blog_v2/badge/star.svg?theme=dark)](https://gitee.com/moxi159753/mogu_blog_v2/stargazers)
[![fork](https://gitee.com/moxi159753/mogu_blog_v2/badge/fork.svg?theme=dark)](https://gitee.com/moxi159753/mogu_blog_v2/members)
[Gitee]()
[Github]()
[开始阅读](README.md)
```
效果图如下所示：
![设置封面](images/image-20201225194013287.png)
在这里使用了两个 **Gitee** 挂件，可以在开源项目的挂件按钮那里获取
![添加Gitee的挂件](images/image-20201225194041281.png)
**注意：**一份文档只会在根目录下加载封面，其他页面或者二级目录下都不会加载。
## 自定义封面背景
目前的背景是随机生成的渐变色，每次刷新都会显示不同的颜色。 docsify封面支持自定义背景色或者背景图，在`_coverpage.md`文档末尾添加：
```bash
![](_media/bg.png)
![color](#2f4253)
```
**注意：**
- 自定义背景配置一定要在`_coverpage.md`文档末尾。
- 背景图片和背景色只能有一个生效.
- 背景色一定要是`#2f4253`这种格式的。
## 封面作为首页
配置了封面后，封面和首页是同时出现的，封面在上面，首页在下面。通过设置`onlyCover`参数，可以让docsify网站首页只显示封面，原来的首页通过`http://localhost:3000/#/README`访问。在`index.html`文件中的`window.$docsify`添加`onlyCover: true,`选项：
```bash
window.$docsify = {
    coverpage: true,
    onlyCover: true,
}
```
通过此配置可以把`./README.md`文件独立出来，当成项目真正的README介绍文件
### 搜索插件
全文搜索插件会根据当前页面上的超链接获取文档内容，在 localStorage 内建立文档索引。默认过期时间为一天，当然我们可以自己指定需要缓存的文件列表或者配置过期时间。
```html
```
安装后，我们就能够使用搜索功能了
![加入搜索功能](images/image-20201225194227046.png)
## 自定义域名
首先我们需要创建项目 `moxi624.github.io` ，第一个moxi624是你的用户名，然后我们在创建一个文件 `CNAME`
![添加CNAME文件](images/image-20201225194257231.png)
里面添加我们需要自定义的域名
```bash
doc.moguit.cn
```
然后把当前项目提交到 **moxi624.github.io** 远程项目，然后选择 **settings**
![Github的Settings](images/image-20201225194327913.png)
然后找到 **Github Pages**，选择主分支 **master**
![](images/image-20201225194352538.png)
![设置Github Pages](images/image-20201225194404370.png)
完成后，我们能够看到这样的页面，说明我们的站点已经发布在 **doc.moguit.cn** 了
![](images/image-20201225194430720.png)
这个时候就需要配置域名解析了，我们到阿里云下的域名解析
![修改阿里云域名解析](images/image-20201225194448952.png)
注意，这边 **moxi624.github.io** 就是我们刚刚创建的仓库名
创建完成后，我们等待十分钟后，就能够正常访问我们的页面了~
## 评论插件Gitalk
**Gitalk**：一个现代化的，基于 **Preact** 和 **Github issue** 的评论系统。**Gitalk** 的特性如下：
- 使用 **GitHub** 登录 
- 支持多语言 **[en, zh-CN, zh-TW, es-ES, fr, ru]** 
- 支持个人或组织 
- 无干扰模式（设置 **distractionFreeMode** 为 **true** 开启） 
- 快捷键提交评论 （**cmd**|**ctrl + enter**）
使用例子：
```bash
```
其中我们首先需要到 **Github Settings** 中，创建一个 **New OAuth App**
![添加一个Oauth Apps](images/image-20201225194616569.png)
然后添加如下内容
![填写内容](images/image-20201225194634481.png)
创建完成后，在复制我们的密钥，替换上面的 **clientID** 和 **clientSecret**
![获取密钥](images/image-20201225194652322.png)
最终，在页面引入 **Gittalk** 的效果图
![引入后的效果](images/image-20201225194712833.png)
到此为止，蘑菇博客的开源文档就已经完成了，后续只需要不断加入文章完善即可。
## 结语
**陌溪**是一个从三本院校一路摸滚翻爬上来的互联网大厂程序员。独立做过几个开源项目，其中**蘑菇博客**在码云上有 **2K Star** 。目前就职于**字节跳动的Data广告部门**，是字节跳动全线产品的商业变现研发团队。本公众号将会持续性的输出很多原创小知识以及学习资源。如果你觉得本文对你有所帮助，麻烦给文章点个“赞”和“在看”。同时欢迎各位小伙伴关注陌溪，让我们一起成长~
![图片](images/1608514024370.jpg)
    “种树的最好时间是十年前，其次是现在”
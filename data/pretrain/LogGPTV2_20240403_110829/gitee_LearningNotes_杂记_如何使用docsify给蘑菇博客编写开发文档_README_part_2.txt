# 蘑菇博客
- 蘑菇博客，一个基于微服务架构的前后端分离博客系统。前台使用Vue + Element , 后端使用spring boot + spring cloud + mybatis-plus进行开发，使用 Jwt + Spring Security做登录验证和权限校验，使用ElasticSearch和Solr作为全文检索服务，使用Github Actions完成博客的持续集成，文件支持上传七牛云。
[![star](https://gitee.com/moxi159753/mogu_blog_v2/badge/star.svg?theme=dark)](https://gitee.com/moxi159753/mogu_blog_v2/stargazers)
[![fork](https://gitee.com/moxi159753/mogu_blog_v2/badge/fork.svg?theme=dark)](https://gitee.com/moxi159753/mogu_blog_v2/members)
[Gitee]()
[Github]()
[开始阅读](README.md)
```
效果图如下所示
![image-20200210095242574](images/image-20200210095242574.png)
在这里使用了两个挂件，可以在开源项目的挂件按钮那里获取
![image-20200210095321298](images/image-20200210095321298.png)
**注意：**一份文档只会在根目录下加载封面，其他页面或者二级目录下都不会加载。
### 自定义封面背景
目前的背景是随机生成的渐变色，每次刷新都会显示不同的颜色。
docsify封面支持自定义背景色或者背景图，在`_coverpage.md`文档末尾添加：
```
![](_media/bg.png)
![color](#2f4253)
```
**注意：**
- 自定义背景配置一定要在`_coverpage.md`文档末尾。
- 背景图片和背景色只能有一个生效.
- 背景色一定要是`#2f4253`这种格式的。
### 封面作为首页
配置了封面后，封面和首页是同时出现的，封面在上面，首页在下面。通过设置`onlyCover`参数，可以让docsify网站首页只显示封面，原来的首页通过`http://localhost:3000/#/README`访问。在`index.html`文件中的`window.$docsify`添加`onlyCover: true,`选项：
```
  window.$docsify = {
    coverpage: true,
    onlyCover: true,
  }
```
通过此配置可以把`./README.md`文件独立出来，当成项目真正的README介绍文件
### 搜索插件
全文搜索插件会根据当前页面上的超链接获取文档内容，在 localStorage 内建立文档索引。默认过期时间为一天，当然我们可以自己指定需要缓存的文件列表或者配置过期时间。
```
```
安装后，我们就能够使用搜索功能了
![image-20200210100056607](images/image-20200210100056607.png)
### 使用Github Page发布页面并自定义域名
现在我的文档，通过自定义域名  doc.moguit.cn就能够访问了
首先我们需要创建项目 `moxi624.github.io` ，第一个moxi624是你的用户名
然后我们在创建一个文件 `CNAME` 
![image-20200210132208627](images/image-20200210132208627.png)
里面添加我们需要自定义的域名
```
doc.moguit.cn
```
然后把当前项目提交到 moxi624.github.io远程项目，然后选择setting
![image-20200210132325581](images/image-20200210132325581.png)
然后找到Github Pages，选择主分支master
![image-20200210132527460](images/image-20200210132527460.png)
![image-20200210132602156](images/image-20200210132602156.png)
完成后，我们能够看到这样的页面，说明我们的站点已经发布在 doc.moguit.cn了
![image-20200210132632682](images/image-20200210132632682.png)
这个时候就需要配置域名解析了，我们到阿里云下的域名解析
![image-20200210132754297](images/image-20200210132754297.png)
注意，这边moxi624.github.io就是我们刚刚创建的仓库名
创建完成后，我们等待十分钟后，就能够正常访问我们的页面了~
![image-20200210132925813](images/image-20200210132925813.png)
### 评论插件Gitalk
Gitalk：一个现代化的，基于Preact和Github Issue的评论系统。
Gitalk 的特性：
> 1、使用 GitHub 登录
> 2、支持多语言 [en, zh-CN, zh-TW, es-ES, fr, ru]
> 3、支持个人或组织
> 4、无干扰模式（设置 distractionFreeMode 为 true 开启）
> 5、快捷键提交评论 （cmd|ctrl + enter）
使用例子：
```
```
其中我们首先需要 创建一个 New OAuth App
![image-20200210131556706](images/image-20200210131556706.png)
内容如下
![image-20200210131643326](images/image-20200210131643326.png)
创建完成后，在替换里面的密钥
![image-20200210131739060](images/image-20200210131739060.png)
页面引入后的效果图
![image-20200210131515154](images/image-20200210131515154.png)
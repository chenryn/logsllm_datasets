# 如何使用docsify给蘑菇博客编写开发文档
## 前言
最近看到很多开源项目都有自己的帮助文档，如下图所示，因为它确实能够方便大家进行文档的检索
![image-20200209103832912](images/image-20200209103832912.png)
后面就开始琢磨着，自己也编写一个帮助文档，来展示蘑菇博客的一些配置博客都放在上面，这样即使网站宕机了，也能够查看到相关的文档
经过技术调查，发现别人开源项目的文档都是通过docsify进行编写的
官网：https://docsify.js.org/#/
下面看最终的效果图：
![image-20200210133005865](images/image-20200210133005865.png)
有了 docsify我们就可以编写和下图一样的文档了，方便文档的查阅与长期维护。
![image-20200209105342392](images/image-20200209105342392.png)
## 安装
首先需要安装docsify-cli脚手架，用于初始化docsify文档项目
```
npm i docsify-cli -g
```
然后初始化
```
docsify init ./docs
```
初始化后，我们就能看到 docs文件夹，里面含有下面内容
![image-20200209105721071](images/image-20200209105721071.png)
目录结构如下所示
- index.html 入口文件
- README.md 会做为主页内容渲染
- .nojekyll 用于阻止 GitHub Pages 会忽略掉下划线开头的文件 (.后缀结尾的是隐藏文件)
## 启动
在我们使用init命令初始化一个文档后，我们需要通过下面命令运行一个本地服务器
```
docsify serve
```
项目启动后，默认访问 [http://localhost:3000](http://localhost:3000/) ，如下图所示，我们能够看到一个帮助文档的骨架了
![image-20200209110442467](images/image-20200209110442467.png)
同时docsify还提供了LiveReload功能，也就是可以在我们修改文档后，能够实时预览
## 编辑
### 修改Loading
初始化时会显示 Loading... 内容，你可以自定义提示信息，我们只需要修改index.html中的标签即可，在里面加入我们需要的提示内容
![image-20200209110822841](images/image-20200209110822841.png)
### 定制侧边栏
默认情况下，侧边栏会根据当前文档的标题生成目录，也可以通过设置文档链接，通过Markdown文件生成，效果如当前的文件的侧边栏，首先我们在index.html里面进行设置
```
    window.$docsify = {
      loadSidebar: true, // 设置侧边栏
    }
```
然后新增一个markdown文件`_sidebar.md` , 如我的侧边栏为下面所示，其实是使用了超链接，每个目录都链接到我的目录下的markdown文件。
```
- [**蘑菇博客**](README.md)
- **文档**
  - [项目介绍](doc/文档/项目介绍.md)
  - [技术选型](doc/文档/技术选型.md)
  - 项目搭建
    - [Windows环境下搭建蘑菇博客](doc/文档/项目搭建/Windows环境下搭建蘑菇博客/README.md)
    - [Docker搭建蘑菇博客](doc/文档/项目搭建/Docker搭建蘑菇博客/README.md)
    - [蘑菇博客部署到云服务器](doc/文档/项目搭建/蘑菇博客部署到云服务器/README.md)
    - [Github Actions完成蘑菇博客持续集成](doc/文档/项目搭建/蘑菇博客使用GithubAction完成持续集成/README.md)
    - [蘑菇博客切换搜索模式](doc/文档/项目搭建/蘑菇博客切换搜索模式/README.md)
    - [蘑菇博客配置七牛云对象存储](doc/文档/项目搭建/蘑菇博客配置七牛云存储/README.md)
    - [使用Zipkin搭建蘑菇博客链路追踪](doc/文档/项目搭建/使用Zipkin搭建蘑菇博客链路追踪/README.md)
- **其他**
  - [致谢](doc/文档/致谢.md)
  - [将要做的事](doc/文档/将要做的事.md)
  - [贡献代码](doc/文档/贡献代码.md)
```
效果图：
![image-20200210092508749](images/image-20200210092508749.png)
### 显示页面目录
定制的侧边栏仅显示了页面的链接。还可以设置在侧边栏显示当前页面的目录(标题)。需要在`index.html`文件中的`window.$docsify`添加`subMaxLevel`字段来设置：
```
  window.$docsify = {
    loadSidebar: true,
    subMaxLevel: 3
  }
```
通过subMaxLevel来限制显示的标题等级，效果如下所示：
![image-20200210093741441](images/image-20200210093741441.png)
subMaxLevel说明：
> subMaxLevel类型是number(数字)，表示显示的目录层级
> **注意：**如果md文件中的第一个标题是一级标题，那么不会显示在侧边栏，如上图所示
| 值   | 说明                                           |
| ---- | ---------------------------------------------- |
| 0    | 默认值，表示不显示目录                         |
| 1    | 显示一级标题(`h1`)                             |
| 2    | 显示一、二级标题(`h1` ~ `h2`)                  |
| 3    | 显示一、二、三级标题(`h1` ~ `h3`)              |
| n    | n是数字，显示一、二、....n 级标题(`h1` ~ `hn`) |
### 定制导航栏
首先需要在`index.html`文件中的`window.$docsify`添加`loadNavbar: true,`选项：
```
  window.$docsify = {
    loadNavbar: true
  }
```
接着在项目根目录创建`_navbar.md`文件，内容格式如下：
```
- [Gitee](https://gitee.com/moxi159753/mogu_blog_v2)
- [Github](https://github.com/moxi624/mogu_blog_v2)
- [演示](http://moguit.cn/#/)
```
![image-20200210094725641](images/image-20200210094725641.png)
**注意**
- 如果使用配置文件来设置导航栏，那么在`index.html`中定义的导航栏只有在定制的首页才会生效，其他页面会被覆盖。
- 如果只在根目录有一个`_navbar.md`文件，那么所有页面都将使用这个一个配置，也就是所有页面的导航栏都一样。
- 如果一个子目录中有`_navbar.md`文件，那么这个子目录下的所有页面将使用这个文件的导航栏。
- `_navbar.md`的加载逻辑是从每层目录下获取文件，如果当前目录不存在该文件则回退到上一级目录。例如当前路径为`/zh-cn/more-pages`则从`/zh-cn/_navbar.md`获取文件，如果不存在则从`/_navbar.md`获取。
### 设置封面
docsify默认是没有封面的，默认有个首页`./README.md`。
通过设置`coverpage`参数，可以开启渲染封面的功能。
首先需要在`index.html`文件中的`window.$docsify`添加`coverpage: true`选项：
```
  window.$docsify = {
    coverpage: true
  }
```
接着在项目根目录创建`_coverpage.md`文件，内容格式如下：
```
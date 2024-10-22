# Vue如何制作一个评论模块
## 前言
一直想着重写蘑菇博客的评论功能，但是一直之前一直没有头绪，最比较让人头疼的是前端的样式问题，最近在看蚂蚁的UI框架的时候，偶然看到了评论组件：[点我传送](https://www.antdv.com/components/comment-cn/)
![image-20200103210924666](images/image-20200103210924666.png)
瞬间感觉发现了新大陆，但是相对来说功能还有些简单，无法满足博客的要求，所以想办法改造一下，下面看最终封装好的组件为： 
源码地址为：https://gitee.com/moxi159753/Vue_Comment_Component
![111](images/111-1578139983946.gif)
## 封装CommentList组件
为了实现多级递归渲染，首先要做的是，将单条评论封装成一个组件，然后里面重复调用自身
```
            回复
            {{item.userName}}
                {{item.content}}
```
在这里需要用到的一个非常重要的字段就是：
```
name:"CommentList",
```
如果我们想要在该组件中嵌套本身，那么直接就可以在模板中使用name属性值 递归调用自身，之前一直不太明白name字段是做什么用处的，有的时候可以加，有的时候删除也可以，今天才了解是为了在组件中调用自己的时候就能用得上。
## 在父组件中调用该CommentList组件
首先我们需要定义一些多级评论的数据，这里的数据是多层嵌套的，通过reply字段
```
comments: [
                    {
                        uid: 'uid000',
                        userName: "陌溪",
                        avatar: 'https://zos.alipayobjects.com/rmsportal/ODTLcjxAfvqbxHnVXCYX.png',
                        content: '我是一级评论',
                        reply: [
                            {
                                uid: 'uid001',
                                userName: "陌溪",
                                avatar: 'https://zos.alipayobjects.com/rmsportal/ODTLcjxAfvqbxHnVXCYX.png',
                                content: '我是二级评论',
                                reply: [
                                    {
                                        uid: 'uid002',
                                        userName: "陌溪",
                                        avatar: 'https://zos.alipayobjects.com/rmsportal/ODTLcjxAfvqbxHnVXCYX.png',
                                        content: '我是三级评论',
                                        reply: []
                                    }
                                ]
                            }, {
                                uid: 'uid003',
                                userName: "陌溪",
                                avatar: 'https://zos.alipayobjects.com/rmsportal/ODTLcjxAfvqbxHnVXCYX.png',
                                content: '我是二级评论',
                                reply: []
                            }
                        ]
                    },
                    {
                        uid: 'uid004',
                        userName: "陌溪",
                        avatar: 'https://zos.alipayobjects.com/rmsportal/ODTLcjxAfvqbxHnVXCYX.png',
                        content: '我是一级评论',
                        reply: [
                            {
                                uid: 'uid005',
                                userName: "陌溪",
                                avatar: 'https://zos.alipayobjects.com/rmsportal/ODTLcjxAfvqbxHnVXCYX.png',
                                content: '我是二级评论',
                                reply: []
                            }
                        ]
                    },
                ],
```
然后我们需要引入刚刚定义的CommentList子组件，传递进对应的评论数据，完整的代码如下所示：
```html
```
到目前为止，我们渲染出来的评论模块已经具备层次关系了
![image-20200103215015767](images/image-20200103215015767.png)
下面我们需要做的就是引入回复模块
## 封装CommentBox组件
ant design也提供了回复框，如下所示
![image-20200103215133593](images/image-20200103215133593.png)
我们将其封装成对应的组件 CommentBox
```html
                        添加评论
                        取消评论
```
然后在CommentList中引入对应的模块，具体需要做的事情是，在回复按钮出设置点击时间，当我们点击的时候，将对应的评论渲染出来，我们首先将CommentBox设置为不显示
```
```
然后当我们点击的时候，就需要将我们点击的comment设置为显示状态，其它的设置为none
```
replyTo: function (uid) {
    var lists = document.getElementsByClassName("comment");
    for (var i = 0; i < lists.length; i++) {
    lists[i].style.display = 'none';
    }
    document.getElementById(uid).style.display = 'block';
    this.replyInfo.replyUid = uid
},
```
我们通过document.getElementByClassName把所有的CommentBox获取到来，然后设置成none，同时将我们点击的CommentBox设置成显示即可
运行效果如下所示：
 ![111](images/111.gif)
## 引入Vuex
通过上面所述，我们就能完成点击回复，弹出对话框，然后输入对话框的内容后，我们还需要回显到页面上
但是这样的方式存在一个问题，就是通过this.$emit和父组件通信的时候，父组件只有在一级评论时，才能够监听到子组件的改变，所以后面就改变了策略，采用vuex存储data数据，也就是评论数据
首先创建如下文件：
![image-20200104151042434](images/image-20200104151042434.png)
app.js文件内容如下，该文件主要是编写操作store的一些方法
```
import {SET_COMMENT_LIST, INCREMENT} from "./mutation-types";
const app = {
  // 全局状态
  state: {
    commentList: [],
    id: 100,
  },
  // getters是对数据的包装，例如对数据进行拼接，或者过滤
  getters: {
    //类似于计算属性
    // 增加的方法
  },
  // 如果我们需要更改store中的状态，一定要通过mutations来进行操作
  mutations: {
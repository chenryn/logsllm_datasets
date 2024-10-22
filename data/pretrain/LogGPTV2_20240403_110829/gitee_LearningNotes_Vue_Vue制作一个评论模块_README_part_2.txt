    // 传入自定义参数
    [SET_COMMENT_LIST](state, commentList) {
      state.commentList = commentList
    },
    [INCREMENT](state) {
      state.id += 1
    },
  },
  // actions是我们定义的一些操作，正常情况下，我们很少会直接调用mutation方法来改变state
  actions: {
  }
}
export default app
```
mutation-types.js文件，用来定义一些常量
```
export const SET_COMMENT_LIST =  "setCommentList"
export const INCREMENT =  "increment"
export const DECREMENT =  "decrement"
```
index.js，如果是多模块，则可以在这里进行配置
```
import Vue from 'vue'
import Vuex from 'vuex'
import app from './app'
//让vuex生效
Vue.use(Vuex)
const store = new Vuex.Store({
  // 将app和user放在store中
  modules: {
    app
  }
})
export default  store
```
然后修改最新的CommentList组件
```
            回复
            {{item.userName}}
                {{item.content}}
    import {mapMutations} from 'vuex';
    import CommentBox from "../components/CommentBox";
    export default {
        name: "CommentList",
        props: ['comments'],
        data() {
            return {
                showCancle: true,
                submitting: false,
                value: '',
                userInfo: {
                    uid: "uid000001",
                    userName: "张三",
                    avatar: "https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif"
                },
                replyInfo: {
                    uid: "",
                    blogUid: "uid000003",
                    replyUserUid: 0,
                    avatar: "https://zos.alipayobjects.com/rmsportal/ODTLcjxAfvqbxHnVXCYX.png"
                },
            };
        },
        created() {
        },
        components: {
            CommentBox
        },
        compute: {},
        methods: {
            ...mapMutations(['setCommentList', 'increment']),
            replyTo: function (uid) {
                var lists = document.getElementsByClassName("comment");
                for (var i = 0; i 
```
这里Vuex参考了之前的一篇博客：[Vuex学习指南-实现一个计数器](http://moguit.cn/#/info?blogUid=a00ebe1473c584ff94bdd40402a4d573)
主要实现思路是：首先当用户在CommentBox中输入内容，并且提交后，触发CommentList中的submitBox方法，该方法传入参数e，也就是发送的评论，然后我们首先判断是否是一级评论
```
submitBox(e) {
// 一级评论
    if (e.replyUid == 0) {
        var firstComment = this.$store.state.app.commentList;
        firstComment.push(e);
        this.$store.commit("setCommentList", firstComment);
        this.$store.commit("increment");
        return;
    }
    document.getElementById(e.replyUid).style.display = 'none'
    var comments = this.$store.state.app.commentList;
    this.getMenuBtnList(comments, e.replyUid, e)
    this.$store.commit("setCommentList", comments);
    this.$store.commit("increment");
},
```
通过replyUid来判断，如果replyUid为0，说明该评论是一级评论，那么直接从store中获取，关于store中的commentList，是在index.vue页面，初始化的时候填入的
```
mounted() {
	this.setCommentList(this.comments);
},
```
如果是一级评论，我们直接把评论追加到commentList中，然后通过 
```
this.$store.commit("setCommentList", comments);
this.$store.commit("increment");
```
更新CommentList列表的数据，那么页面就会重新渲染，也就看到我们新加入的评论了，同时我们的id也需要变换，id的改变，是为了唯一表示CommentBox，这样我们就可以通过以下代码
```
document.getElementById(e.replyUid).style.display = 'none'
```
来控制评论box的显示与否，同时当不是一级评论的时候，我们需要通过递归，找到该评论的父ID，这个方法需要三个参数，一个是评论列表，一个是 父评论Uid，一个是需要填充的评论，那么执行该方法后，会自动将评论填充到指定的父评论的reply下
```
updateCommentList(commentList, uid, targetComment) {
    if (commentList == undefined || commentList.length 
```
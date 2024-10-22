```
完整的代码如下：
main.js：
```javascript
import Vue from 'vue'
import App from './App.vue'
import Vuex from 'vuex'
// 让Vuex生效
Vue.use(Vuex)
const store = new Vuex.Store({
  // 全局状态
  state: {
    count: 0
  },
  // getters是对数据的包装，例如对数据进行拼接，或者过滤
  getters: {
  },
  // 如果我们需要更改store中的状态，一定要通过mutations来进行操作
  mutations: {
    // 增加的方法
    increment(state) {
      state.count += 1
    },
    // 减少的方法
    decrement(state) {
      state.count -= 1
    },
    // 传入自定义参数
    incrementN(state, N) {
      state.count += N
    }
  },
  // actions是我们定义的一些操作，正常情况下，我们很少会直接调用mutation方法来改变state
  actions: {
    // 编写业务代码
    myIncrement: function(context) {
      // 进行一系列的计算
      context.commit('increment')
    },
    myIncrementN: function(context, N) {
      // 这里在提交的时候，我们就可以在添加一个参数
      console.log("传递过来的N", N);
      context.commit('incrementN', N)
    },
    myDecrement: function(context) {
      // 进行一系列的状态
      context.commit("decrement")
    }
  }
})
new Vue({
  el: '#app',
  render: h => h(App),
  //需要将store和vue实例进行关联，这里将其传递进去
  store
})
```
App.vue代码如下：
```vue
    {{count}}
    +
    -
    +N
```
我们再次查看运行结果：
![](./images/222.gif)
### 将main.js中的store提取出来
一般的，我们的store定义不会写在main.js里面，一般会有专门一个文件夹用于存储store的
我们这里需要创建一个store文件夹，然后新建四个文件，分别为 index.js，mutation-types.js，app.js，user.js
![image-20191222144248663](E:\MarkDown学习笔记\LearningNotes\Vue\VueX\images\image-20191222144248663.png)
其中mutation-types.js是将我们mutations中的方法名给定义成常量，内容如下
```javascript
export const INCREMENT =  "increment"
export const INCREMENT_N =  "incrementN"
export const DECREMENT =  "decrement"
```
其中app.js就是我们刚刚在main里面定义的 store，我们给它重新取个名字叫app
```javascript
import {INCREMENT, DECREMENT, INCREMENT_N} from "./mutation-types";
const app = {
  // 全局状态
  state: {
    count: 0
  },
  // getters是对数据的包装，例如对数据进行拼接，或者过滤
  getters: {
    //类似于计算属性
    myCount(state) {
      return `current count is ${state.count}`
    }
  },
  // 如果我们需要更改store中的状态，一定要通过mutations来进行操作
  mutations: {
    // 增加的方法
    [INCREMENT](state) {
      state.count += 1
    },
    // 减少的方法
    [DECREMENT](state) {
      state.count -= 1
    },
    // 传入自定义参数
    [INCREMENT_N](state, N) {
      state.count += N
    }
  },
  // actions是我们定义的一些操作，正常情况下，我们很少会直接调用mutation方法来改变state
  actions: {
    // 编写业务代码
    myIncrement: function (context) {
      // 进行一系列的计算
      context.commit(INCREMENT)
    },
    myIncrementN: function (context, N) {
      // 这里在提交的时候，我们就可以在添加一个参数
      console.log("传递过来的N", N);
      context.commit(INCREMENT_N, N)
    },
    myDecrement: function (context) {
      // 进行一系列的状态
      context.commit(DECREMENT)
    }
  }
}
export default app
```
然后项目中可能不止一个store，假设我们需要登录注册，在创建一个user store用于存储登录注册的信息
```javascript
const user = {
  // 全局状态
  state: {
    userInfo: {}
  },
  // getters是对数据的包装，例如对数据进行拼接，或者过滤
  getters: {
  },
  // 如果我们需要更改store中的状态，一定要通过mutations来进行操作
  mutations: {
  },
  // actions是我们定义的一些操作，正常情况下，我们很少会直接调用mutation方法来改变state
  actions: {
  }
}
export default user
```
最后我们使用index.js管理这两个store
```javascript
import Vue from 'vue'
import Vuex from 'vuex'
import app from './app'
import user from './user'
//让vuex生效
Vue.use(Vuex)
const store = new Vuex.Store({
  // 将app和user放在store中
  modules: {
    app, user
  }
})
export default  store
```
然后下面就是 main.js的内容了，我们在抽取完 const store后，只需要把 /store/index.js引入即可
```javascript
import Vue from 'vue'
import App from './App.vue'
import store from './store'
new Vue({
  el: '#app',
  render: h => h(App),
  //需要将store和vue实例进行关联，这里将其传递进去
  store
})
```
然后就是修改APP.vue中的内容了，因为我们分模块进行管理了，所以在获取count的时候有些区别
```javascript
...mapState({
   count: state => {
    return state.app.count
   }
}),
```
我们需要选中state下面的app模块，然后在获取count属性
最后附上修改后的App.vue
```vue
    {{count}}
    {{myCount}}
    +
    -
    +N
```
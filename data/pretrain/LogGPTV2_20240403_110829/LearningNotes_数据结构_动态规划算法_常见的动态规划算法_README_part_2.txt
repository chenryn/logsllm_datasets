leetcode63 [不同路径II](https://leetcode-cn.com/problems/unique-paths-ii/)
### 描述
一个机器人位于一个 m x n 网格的左上角 （起始点在下图中标记为“Start” ）。
机器人每次只能向下或者向右移动一步。机器人试图达到网格的右下角（在下图中标记为“Finish”）。
问总共有多少条不同的路径？
![image-20201010212332680](images/image-20201010212332680.png)
```bash
例如，上图是一个7 x 3 的网格。有多少可能的路径？
示例 1:
输入: m = 3, n = 2
输出: 3
解释:
从左上角开始，总共有 3 条路径可以到达右下角。
1. 向右 -> 向右 -> 向下
2. 向右 -> 向下 -> 向右
3. 向下 -> 向右 -> 向右
示例 2:
输入: m = 7, n = 3
输出: 28
提示：
1 = len(nums):
            return 0
        if self.map.get(index) != None:
            return self.map.get(index)
        res = 0
        for i in range(index, len(nums)):
            res = max(nums[i] + self.tryRob(nums, i+2), res)
        self.map[index] = res
        return res
    def rob(self, nums):
        return self.tryRob(nums, 0)
if __name__ == '__main__':
    print(Solution().rob([2,7,9,3,1]))
```
### 动态规划解决
```python
class Solution(object):
    # map.get(index): 表示考虑抢劫 nums[i ... n] 所能获得的最大收益
    map = {}
    def rob2(self, nums):
        n = len(nums)
        if n == 0:
            return 0
        self.map[n - 1] = nums[n -1]
        for i in range(n-2, 0, -1):
            # 求解map[i]
            for j in range(i, n):
                a = nums[j]
                if j + 2 = weight[index]:
            # 价值该物品存入背包的时候
            res2 = value[index] + self.bestValue(weight, value, index-1, capacity - weight[index])
            # 两种策略，找出价值最大的结果
            res = max(res, res2)
        self.map[str(index) + "_" + str(capacity)] = res
        return res
if __name__ == '__main__':
    weight = [1, 2, 3]
    value = [6, 10, 12]
    print(Solution().bestValue(weight, value, len(weight) - 1, 5))
```
### 动态规划
下面我们采用动态规划来对问题进行解答
![image-20201011213351373](images/image-20201011213351373.png)
代码如下
```python
class Solution:
    # 用 [0 .... index] 的物品，来填充容积为 capacity的背包的最大价值
    map = {}
    # 采用记忆化搜索
    def bestValue(self, weight, value, index, capacity):
        # 当物品无法放入的时候，或者没有价值
        if index = weight[index]:
            # 价值该物品存入背包的时候
            res2 = value[index] + self.bestValue(weight, value, index-1, capacity - weight[index])
            # 两种策略，找出价值最大的结果
            res = max(res, res2)
        self.map[str(index) + "_" + str(capacity)] = res
        return res
    # 采用动态规划
    def bestValue2(self, weight, value, index, capacity):
        n = len(weight)
        if n == 0:
            return 0
        for j in range(capacity):
            if j >= weight[0]:
                self.map["0_" + str(j)] = weight[0]
            else:
                self.map["0_" + str(j)] = 0
        for i in range(1, n):
            for j in range(capacity):
                # 两种策略， 假设不放入到背包中
                res = self.map.get(str(i-1) + "_" + str(j))
                # 假设物品能够放入到背包中
                if j >= weight[i]:
                    res2 = value[i] + self.map.get(str(i-1) + "_" + str(j-weight[i]))
                    res = max(res, res2)
                # 重新调整数组
                self.map[str(i) + "_" + str(j)] = res
        return self.map.get(str(n-1) + "_" + str(capacity))
if __name__ == '__main__':
    weight = [1, 2, 3]
    value = [6, 10, 12]
    print(Solution().bestValue2(weight, value, len(weight) - 1, 5))
```
### 优化
从上面的代码我们可以知道，0-1背包问题，它的时空复杂度如下
- 时间复杂度：O(n * C)
- 空间复杂度：O(n * C)
我们再次到 0-1背包问题之前提到的状态转移方程
> F(n, C) 考虑将n个物品放进容量为C的背包，使得价值最大
>
> F(i, c) = max(F(i-1, c) , v(i) + F(i-1, c- w(i)))
从上面的方程我们可以发现，第i行元素只依赖于第i-1行元素。理论上，只需要保持两行元素
空间复杂度：O(2 * C) = O(C)
```
class Solution:
    # 用 [0 .... index] 的物品，来填充容积为 capacity的背包的最大价值
    map = {}
    # 采用动态规划
    def bestValue2(self, weight, value, index, capacity):
        n = len(weight)
        if n == 0:
            return 0
        for j in range(capacity):
            if j >= weight[0]:
                self.map["0_" + str(j)] = weight[0]
            else:
                self.map["0_" + str(j)] = 0
        for i in range(1, n):
            for j in range(capacity):
                # 两种策略， 假设不放入到背包中
                res = self.map.get(str((i-1)%2) + "_" + str(j))
                # 假设物品能够放入到背包中
                if j >= weight[i]:
                    res2 = value[i] + self.map.get(str((i-1)%2) + "_" + str(j-weight[i]))
                    res = max(res, res2)
                # 重新调整数组
                self.map[str(i) + "_" + str(j)] = res
        return self.map.get(str((n-1)%2) + "_" + str(capacity))
if __name__ == '__main__':
    weight = [1, 2, 3]
    value = [6, 10, 12]
    print(Solution().bestValue2(weight, value, len(weight) - 1, 5))
```
有没有只使用一行大小的C来完成数组的动态规划呢？
### 背包问题具体解
同时我们还通过最后的状态数组，来反推我们具体的解
![image-20201017202953190](images/image-20201017202953190.png)
然后从右下角出发，不断寻找我们的结果
![image-20201017203134475](images/image-20201017203134475.png)
## 最长上升子序列
### 来源
leetcode 300 [最长上升子序列](https://leetcode-cn.com/problems/longest-increasing-subsequence/)
### 描述
给定一个整数序列，求其中最长上升子序列的长度
如 [10,9,2,5,3,7,101,18]，其最长上升子序列的长度为4.
最长上升子序列为 [2,5,7,101]
- 注意1：什么是子序列？
- 注意2：什么是上升？
- 注意3：一个序列可能有多个最长上升子序列；但这个最长的长度只有1个
### 思考
如果使用暴力解法：选择所有的子序列进行判断。O((2^n)*n)，也就是说对于一个数组，我们需要考虑每个元素是否放入到我们的序列中，只有两种情况，一个是放入，一个是不放入，最后n次代表判断是否是上升子序列
LIS(i)表示第i个数字为结尾的最长上升子序列的长度
LIS(i) 表示 [0 .... i ] 的范围内，选择数字 nums[i] 可以获得的最长上升子序列长度 
然后我们得到了状态转移方程
```bash
LIS(i) = max( 1 + LIS(j) if nums[i] > nums[j])
```
我们通过计算，求出LIS状态
![image-20201017163022177](images/image-20201017163022177.png)
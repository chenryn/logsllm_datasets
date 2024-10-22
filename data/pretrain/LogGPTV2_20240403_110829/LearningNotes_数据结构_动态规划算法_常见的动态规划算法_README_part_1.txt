# 动态规划
## 视频教程
[动态规划](https://www.bilibili.com/video/BV1a4411y7uh)
## 斐波那契数列
我们还是以菲波那切数列为例，使用python编写一个最简单的菲波那切数列计算
```bash
# 大家都知道斐波那契数列，现在要求输入一个整数n，请你输出斐波那契数列的第n项（从0开始，第0项为0）  n 0:
            return self.Fibonacci(n - 1) + self.Fibonacci(n -2);
        else:
            return None
        return ret
if __name__ == '__main__':
    print(Solution().Fibonacc(10))
```
但是上述的代码其实存在着大量的计算过程，
![image-20201008113107022](images/image-20201008113107022.png)
也就是说我们同一个数，被多次进行计算了，如果我们能够保留中间解决的话，那么就可以省下很多计算时间
## 保留中间结果
下面这种方法，我们就可以保留中间的计算结果，采用的是一个字典map来进行存储
```bash
class Solution:
    map = {}
    # 保留中间结果
    def Fibonacci3(self, n):
        if n == 0:
            return 0
        if n == 1:
            return 1
        if self.map.get(n) == None:
            self.map[n] = self.Fibonacci3(n - 1) + self.Fibonacci3(n - 2)
        return self.map[n]
if __name__ == '__main__':
    print(Solution().Fibonacci3(10))
```
上面这个保留中间结果的操作，又被称之为 `记忆化搜索`
## 记忆化搜索
记忆化搜索其实就是 自上而下的解决问题，也就是说我们没有从最基本的来解决问题，而是假设最基本的已经解决了，就比如说，我们假设已经会求 第n个菲波那切数列了
```bash
self.map[n] = self.Fibonacci3(n - 1) + self.Fibonacci3(n - 2)
```
然后我们在这个基础在把 n-1 和 n-2的数加起来即可，这就是自上而下的解决问题。而还有另外一种解决问题的方法，就是自下而上，也就是我们要说的动态规划
## 动态规划
自上而下的解决问题，是我们首先就容易想到的一种方法，因为它更容易被我们所理解。而这里我们将的是一种自下而上的解决问题的思路，也就是我们先从小的问题开始解决，然后逐步解决大的问题，这个方法也叫动态规划 
```python
class Solution:
    # 动态规划
    map2 = {}
    def Fibonacci4(self, n):
        self.map2[0] = 0
        self.map2[1] = 1
        for i in range(2, n+1):
            self.map2[i] = self.map2.get(i-1) + self.map2.get(i - 2)
        return self.map2.get(n)
if __name__ == '__main__':
    print(Solution().Fibonacci4(10))
```
将原问题拆解成若干子问题，同时保存子问题的答案，使得每个子问题只求解一次，最终获得原问题的答案
![image-20201008203540814](images/image-20201008203540814.png)
先通过自顶向下的方法来思考问题，然后用动态规划来解决问题
## 爬楼梯
###  来源
leetcode70 [爬楼梯](https://leetcode-cn.com/problems/climbing-stairs/)
### 描述
假设你正在爬楼梯。需要 *n* 阶你才能到达楼顶。
每次你可以爬 1 或 2 个台阶。你有多少种不同的方法可以爬到楼顶呢？
**注意：**给定 *n* 是一个正整数。
示例 1：
输入： 2
输出： 2
解释： 有两种方法可以爬到楼顶。
```bash
1.  1 阶 + 1 阶
2.  2 阶
```
示例 2：
输入： 3
输出： 3
解释： 有三种方法可以爬到楼顶。
```bash
1.  1 阶 + 1 阶 + 1 阶
2.  1 阶 + 2 阶
3.  2 阶 + 1 阶
```
### 思考
我们也可以将上述的问题，想象成刚刚的菲波那切数列，求n的时候，我们先求 n -1 和 n -2，然后在相加
![image-20201008204100626](images/image-20201008204100626.png)
### 代码
```bash
# 爬楼梯
class Solution:
    map = {}
    def ClimbingStairs(self, n):
        # 爬1阶楼梯，有1种方法
        self.map[1] = 1
        # 爬2阶楼梯，有2种方法
        self.map[2] = 2
        for i in range(3, n+1):
            self.map[i] = self.map[i-1] + self.map[i-2]
        return self.map.get(n)
if __name__ == '__main__':
    print(Solution().ClimbingStairs(10))
```
## 三角形最小路径和
### 来源
[leetcode 三角形最小路径和](https://leetcode-cn.com/problems/triangle/)
### 描述
给定一个三角形，找出自顶向下的最小路径和。每一步只能移动到下一行中相邻的结点上。
相邻的结点 在这里指的是 下标 与 上一层结点下标 相同或者等于 上一层结点下标 + 1 的两个结点。
例如，给定三角形：
```bash
[
     [2],
    [3,4],
   [6,5,7],
  [4,1,8,3]
]
```
自顶向下的最小路径和为 `11`（即，**2** + **3** + **5** + **1** = 11）。
### 思路
我们现在通过自顶向下来思考，从最后的结果往前推，因为我们要保证找到最小的数，所以我们只需要每次把中间结果都保留即可，最后求得的数就是我们最小的和
### 代码
```python
# 三角形最小路径和
class Solution(object):
    def minimumTotal(self, triangle):
        for i in range(len(triangle) - 1, 0, -1):
            for j in range(i):
                triangle[i-1][j] += min(triangle[i][j], triangle[i][j+1])
        return triangle[0][0]
```
## 最小路径和
### 来源
leet64 [最小路径和](https://leetcode-cn.com/problems/minimum-path-sum/)
### 描述
给定一个包含非负整数的 m x n 网格，请找出一条从左上角到右下角的路径，使得路径上的数字总和为最小。
说明：每次只能向下或者向右移动一步。
示例:
```bash
输入:
[
  [1,3,1],
  [1,5,1],
  [4,2,1]
]
输出: 7
解释: 因为路径 1→3→1→1→1 的总和最小。
```
## 整数拆分
### 来源
#### [343. 整数拆分](https://leetcode-cn.com/problems/integer-break/)
### 描述
给定一个正整数 *n*，将其拆分为**至少**两个正整数的和，并使这些整数的乘积最大化。 返回你可以获得的最大乘积。
```bash
示例 1:
输入: 2
输出: 1
解释: 2 = 1 + 1, 1 × 1 = 1。
示例 2:
输入: 10
输出: 36
解释: 10 = 3 + 3 + 4, 3 × 3 × 4 = 36。
说明: 你可以假设 n 不小于 2 且不大于 58。
```
### 思路
暴力解法：回溯遍历算法将一个数做分割的所有可能性O(2^n)
我们在用画图的方式，将一个大的问题，转换为一个一个小的问题，转换成一个递归树
![image-20201010155358717](images/image-20201010155358717.png)
从我们拆分出来的结果来看，我们存在大量计算重复子问题，所以可以采用动态规划的方式来做，我们将4延伸出来，到一个分割n的问题上
![image-20201010155524351](images/image-20201010155524351.png)
### 最优子结构
通过求子问题的最优解，可以获得原问题的最优解
### 方法1
方法1采用的是自顶向下的 记忆化搜索来解决
```python
class Solution(object):
    map = {}
    # 使用记忆化搜索解决
    def integerBreak(self, n):
        if n == 1:
            return 1
        res = -1
        if self.map.get(n) == None:
            for i in range(1, n+1):
                # 找到最大值【需要判断三个值，一个 n * n-i】
                a = i * self.integerBreak(n - i)
                b = i * (n - i)
                c = res
                res = max(a, b, c)
            self.map[n] = res
            return res
        else:
            return self.map[n]
if __name__ == '__main__':
    print(Solution().integerBreak2(10))
```
### 方法2
采用自底向上的方法，也就是动态规划来解决
```python
class Solution(object):
    map = {}
    # 使用动态规划解决
    def integerBreak2(self, n):
        self.map[1] = 1
        for i in range(2, n+1):
            for j in range(1, i):
                # 求解 j+(i-j)的形式
                a = j*(i-j)
                b = j * self.map.get(i-j)
                c = -1
                if self.map.get(i) != None:
                    c = self.map.get(i)
                self.map[i] = max(a, b, c)
        return self.map[n]
if __name__ == '__main__':
    print(Solution().integerBreak2(10))
```
## 完全平方数
### 来源
leetcode279 [完全平方数](https://leetcode-cn.com/problems/perfect-squares/)
### 描述
给定正整数 *n*，找到若干个完全平方数（比如 `1, 4, 9, 16, ...`）使得它们的和等于 *n*。你需要让组成和的完全平方数的个数最少。
```bash
示例 1:
输入: n = 12
输出: 3 
解释: 12 = 4 + 4 + 4.
示例 2:
输入: n = 13
输出: 2
解释: 13 = 4 + 9.
```
## 解码方法
### 来源
leetcode91. [解码方法](https://leetcode-cn.com/problems/decode-ways/)
### 描述
一条包含字母 A-Z 的消息通过以下方式进行了编码：
'A' -> 1
'B' -> 2
...
'Z' -> 26
给定一个只包含数字的非空字符串，请计算解码方法的总数。
题目数据保证答案肯定是一个 32 位的整数。
```bash
示例 1：
输入："12"
输出：2
解释：它可以解码为 "AB"（1 2）或者 "L"（12）。
示例 2：
输入："226"
输出：3
解释：它可以解码为 "BZ" (2 26), "VF" (22 6), 或者 "BBF" (2 2 6) 。
示例 3：
输入：s = "0"
输出：0
示例 4：
输入：s = "1"
输出：1
示例 5：
输入：s = "2"
输出：1
```
## 不同路径
### 来源
leetcode62 [不同路径](https://leetcode-cn.com/problems/unique-paths/)
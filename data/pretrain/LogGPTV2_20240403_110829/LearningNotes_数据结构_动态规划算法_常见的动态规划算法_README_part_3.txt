### 代码
我们通过分析后，就可以从自底向上的动态规划方法，来求得我们的值
```python
# 最长上升子序列
class Solution(object):
    def lengthOfLIS(self, nums):
        if nums == []:
            return 0
        status = [1 for _ in range(len(nums))]
        for i in range(1, len(nums)):
            max = 1
            for j in range(i):
                if nums[j] = max:
                    max = status[j] + 1
            status[i] = max
        result = 1
        for i in status:
            if i > result:
                result = i
        return result
if __name__ == '__main__':
    print(Solution().lengthOfLIS([10,9,2,5,3,7,101,18]))
```
我们也可以通过状态数组，反推我们的结果，得到有哪些最长上升子序列满足条件
![image-20201017201918704](images/image-20201017201918704.png)
## 摆动序列
### 来源
leetcode.376 [摆动序列](https://leetcode-cn.com/problems/wiggle-subsequence/)
### 描述
如果连续数字之间的差严格地在正数和负数之间交替，则数字序列称为摆动序列。第一个差（如果存在的话）可能是正数或负数。少于两个元素的序列也是摆动序列。
例如， [1,7,4,9,2,5] 是一个摆动序列，因为差值 (6,-3,5,-7,3) 是正负交替出现的。相反, [1,4,7,2,5] 和 [1,7,4,5,5] 不是摆动序列，第一个序列是因为它的前两个差值都是正数，第二个序列是因为它的最后一个差值为零。
给定一个整数序列，返回作为摆动序列的最长子序列的长度。 通过从原始序列中删除一些（也可以不删除）元素来获得子序列，剩下的元素保持其原始顺序。
示例 1:
```bash
输入: [1,7,4,9,2,5]
输出: 6 
解释: 整个序列均为摆动序列。
```
示例 2:
```bash
输入: [1,17,5,10,13,15,10,5,16,8]
输出: 7
解释: 这个序列包含几个长度为 7 摆动序列，其中一个可为[1,17,10,13,10,16,8]。
```
**示例 3:**
```
输入: [1,2,3,4,5,6,7,8,9]
输出: 2
```
### 思考
## 最长公共子序列
### 来源
leetcode.1143 [最长公共子序列](https://leetcode-cn.com/problems/longest-common-subsequence/)
### 描述
给定两个字符串 text1 和 text2，返回这两个字符串的最长公共子序列的长度。
一个字符串的 子序列 是指这样一个新的字符串：它是由原字符串在不改变字符的相对顺序的情况下删除某些字符（也可以不删除任何字符）后组成的新字符串。
例如，"ace" 是 "abcde" 的子序列，但 "aec" 不是 "abcde" 的子序列。两个字符串的“公共子序列”是这两个字符串所共同拥有的子序列。
若这两个字符串没有公共子序列，则返回 0。
示例 1:
```bash
输入：text1 = "abcde", text2 = "ace" 
输出：3  
解释：最长公共子序列是 "ace"，它的长度为 3。
```
示例 2:
```bash
输入：text1 = "abc", text2 = "abc"
输出：3
解释：最长公共子序列是 "abc"，它的长度为 3。
```
示例 3:
```bash
输入：text1 = "abc", text2 = "def"
输出：0
解释：两个字符串没有公共子序列，返回 0。
```
### 思考
LCS(m, n)   S1[0 .... m] 和 S2[0 ... n ] 的最长公共子序列的长度
```bash
S1[m] == S2[n]:
	LCS(m, n) = 1 + LCS(m-1, n-1)
S1[m] != S2[n]:
	LCS(m, n) = max(LCS(m-1, n), LCS(m, n-1))
```
![image-20201017201043326](images/image-20201017201043326.png)
我们通过比较 ABCD 和 AEBD，画出我们的递归树，就能非常形象的了解我们算法的执行过程
同时，我们需要了解的是，dijkstra单源最短路径算法也是动态规划
## 分割等和子集
对于我们上面遇到的背包问题，其实很多时候不会直接从题目中就能知道答案，而是需要我们通过计算得到，例如下面这个算法，其实也是一个典型的背包问题
### 来源
leetcode.416 [分割等和子集](https://leetcode-cn.com/problems/partition-equal-subset-sum/)
### 描述
给定一个只包含正整数的非空数组。是否可以将这个数组分割成两个子集，使得两个子集的元素和相等。
注意:
每个数组中的元素不会超过 100
数组的大小不会超过 200
```bash
示例 1:
输入: [1, 5, 11, 5]
输出: true
解释: 数组可以分割成 [1, 5, 5] 和 [11].
```
示例 2:
```bash
输入: [1, 2, 3, 5]
输出: false
解释: 数组不能分割成两个元素和相等的子集.
```
### 思考
这个算法其实就是典型的背包问题，在n个物品中，选出一定物品，填满 sum /2 的背包，和背包问题的区别就是，这里不涉及到物品的价值，而是只需要将 背包完全填满即可。
我们需要考虑的问题就是：F(n, C) 考虑将n个物品填满容量为C的背包，从而得到如下所示的状态转移方程
```bash
F(i, c) = F(i-1, c) || F(i-1, c-w(i))
```
### 记忆化搜索
我们使用记忆化搜索的方式
```python
class Solution(object):
    map = {}
    # 使用 nums[0 ... index]，是否可以完全填充一个容量为sum的背包
    def tryPartition(self, nums, index, sum):
        if sum == 0:
            return True
        if sum < 0 or index < 0:
            return False
        if self.map.get(str(index) + "_" + str(sum)) != None:
            return self.map.get(str(index) + "_" + str(sum))
        result = self.tryPartition(nums, index - 1, sum) or self.tryPartition(nums, index - 1, sum - nums[index])
        self.map[str(index) + "_" + str(sum)] = result
        return result
    def canPartition(self, nums):
        sum = 0
        for i in nums:
            sum += i
        if sum % 2 != 0:
            return False
        return self.tryPartition(nums, len(nums) -1, sum/2)
if __name__ == '__main__':
    print(Solution().canPartition([2,2,3,5]))
```
## 零钱兑换
### 来源
leetcode.322 [零钱兑换](https://leetcode-cn.com/problems/coin-change/)
### 描述
给定不同面额的硬币 coins 和一个总金额 amount。编写一个函数来计算可以凑成总金额所需的最少的硬币个数。如果没有任何一种硬币组合能组成总金额，返回 -1。
你可以认为每种硬币的数量是无限的。
示例 1：
```bash
输入：coins = [1, 2, 5], amount = 11
输出：3 
解释：11 = 5 + 5 + 1
```
示例 2：
```bash
输入：coins = [2], amount = 3
输出：-1
```
示例 3：
```bash
输入：coins = [1], amount = 0
输出：0
```
示例 4：
```bash
输入：coins = [1], amount = 1
输出：1
```
示例 5：
```bash
输入：coins = [1], amount = 2
输出：2
```
### 代码
## 组合总和
### 来源
leetcode.377 [组合总和 Ⅳ](https://leetcode-cn.com/problems/combination-sum-iv/)
### 描述
给定一个由正整数组成且不存在重复数字的数组，找出和为给定目标正整数的组合的个数。
```bash
nums = [1, 2, 3]
target = 4
所有可能的组合为：
(1, 1, 1, 1)
(1, 1, 2)
(1, 2, 1)
(1, 3)
(2, 1, 1)
(2, 2)
(3, 1)
请注意，顺序不同的序列被视作不同的组合。
因此输出为 7。
```
## 一和零
### 来源
leetcode.474  [一和零](https://leetcode-cn.com/problems/ones-and-zeroes/)
### 描述
在计算机界中，我们总是追求用有限的资源获取最大的收益。
现在，假设你分别支配着 m 个 0 和 n 个 1。另外，还有一个仅包含 0 和 1 字符串的数组。
你的任务是使用给定的 m 个 0 和 n 个 1 ，找到能拼出存在于数组中的字符串的最大数量。每个 0 和 1 至多被使用一次。
示例 1:
```bash
输入: strs = ["10", "0001", "111001", "1", "0"], m = 5, n = 3
输出: 4
解释: 总共 4 个字符串可以通过 5 个 0 和 3 个 1 拼出，即 "10","0001","1","0" 。
```
示例 2:
```bash
输入: strs = ["10", "0", "1"], m = 1, n = 1
输出: 2
解释: 你可以拼出 "10"，但之后就没有剩余数字了。更好的选择是拼出 "0" 和 "1" 。
```
## 单词拆分
### 来源
leetcode.139  [单词拆分](https://leetcode-cn.com/problems/word-break/)
### 描述
给定一个非空字符串 s 和一个包含非空单词的列表 wordDict，判定 s 是否可以被空格拆分为一个或多个在字典中出现的单词。
说明：
拆分时可以重复使用字典中的单词。
你可以假设字典中没有重复的单词。
示例 1：
```bash
输入: s = "leetcode", wordDict = ["leet", "code"]
输出: true
解释: 返回 true 因为 "leetcode" 可以被拆分成 "leet code"。
```
示例 2：
```bash
输入: s = "applepenapple", wordDict = ["apple", "pen"]
输出: true
解释: 返回 true 因为 "applepenapple" 可以被拆分成 "apple pen apple"。
     注意你可以重复使用字典中的单词。
```
示例 3：
```bash
输入: s = "catsandog", wordDict = ["cats", "dog", "sand", "and", "cat"]
输出: false
```
## 目标和
### 来源
leetcode.494 [目标和](https://leetcode-cn.com/problems/target-sum/)
### 描述
给定一个非负整数数组，a1, a2, ..., an, 和一个目标数，S。现在你有两个符号 + 和 -。对于数组中的任意一个整数，你都可以从 + 或 -中选择一个符号添加在前面。
返回可以使最终数组和为目标数 S 的所有添加符号的方法数。
示例：
```bash
输入：nums: [1, 1, 1, 1, 1], S: 3
输出：5
解释：
-1+1+1+1+1 = 3
+1-1+1+1+1 = 3
+1+1-1+1+1 = 3
+1+1+1-1+1 = 3
+1+1+1+1-1 = 3
一共有5种方法让最终目标和为3。
```
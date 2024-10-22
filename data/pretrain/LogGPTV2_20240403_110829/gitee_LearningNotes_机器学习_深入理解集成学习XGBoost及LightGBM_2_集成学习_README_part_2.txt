GBDT与提升树的区别是残差使用梯度代替，而且每个基学习器有对应的参数权重。
GBDT使用梯度提升的决策树（CART），CART树回归将空间划分为K个不相交的区域，并确定每个区域的输出CK，数学表达式如下：
![image-20200428160111309](images/image-20200428160111309.png)
### GBDT完成回归任务
![image-20200428160954632](images/image-20200428160954632.png)
### 使用GBDT完成分类任务
![image-20200428161136964](images/image-20200428161136964.png)
![image-20200428161352770](images/image-20200428161352770.png)
## XGBoost
ⅹGBoost是GBDT的一种，也是加法模型和前向优化算法在监督学习中，可以分为:模型，参数，目标函数和学习方法
- 模型：给定输入X后预测输出y的方法，比如说回归，分类，排序等
- 参数：模型中的参数，比如线性回归中的权重和偏置
- 目标函数：即损失函数，包含正则化项
- 学习方法：给定目标函数后求解模型和参数的方法，比如
- 梯度下降法，数学推导等
这四方面的内容也指导着 XGBoost系统的设计。
### 模型形式
假设要判断一个人是否喜欢电脑游戏，输入年龄、性别、职业等特征，可以得到如下的回归树：
![image-20200428162009041](images/image-20200428162009041.png)
在叶子节点上会有一个分数，利用这个分数我们可以回归，或者映射成概率进行分类等。
但是一颗CART树的拟合能力有限，我们可以进行集成学习，比如用两棵树进行预测，结果是两个树的和：
![image-20200428162142920](images/image-20200428162142920.png)
用多棵树进行预测的方法就是随机森林或提升树。
给定数据集：
$$
D=\left(X_{i}, y_{i}\right)\left(|\mathrm{D}|=\mathrm{n}, x_{i} \in R^{m}, y_{i} \in R\right)
$$
XGBoost利用前向分布算法，学习到包含K棵树的加法模型：
$$
\hat{y}_{i}=\sum_{t=1}^{K} f_{t}\left(x_{i}\right), \quad f_{t} \in \mathcal{F}
$$
其中有K棵树，f是回归树，而F对应回归树组成的函数空间，那怎么得到这些树，也就是树的结构和叶子节点的预测结果？
### 目标函数
定义目标函数，包含正则项：
$$
\operatorname{Obj}(\Theta)=\sum_{i=1}^{N} l\left(y_{i}, \hat{y}_{i}\right)+\sum_{j=1}^{t} \Omega\left(f_{j}\right), \quad f_{j} \in \mathcal{F}
$$
如何优化这个目标函数呢？因为f是决策树，而不是数值型的向量，我们不能使用梯度下降的算法进行优化。
XGBoost是前向分布算法，我们通过贪心算法寻找局部最优解：
$$
\hat{y}_{i}^{(t)}=\sum_{j=1}^{t} f_{j}\left(x_{i}\right)=\hat{y}_{i}^{(t-1)}+f_{t}\left(x_{i}\right)
$$
每一次迭代我们寻找使损失函数降低最大的 f（CART树），因此目标函数可改写成
$$
\begin{aligned}
O b j^{(t)} &=\sum_{i=1}^{N} l\left(y_{i}, \hat{y}_{i}^{(t)}\right)+\sum_{j=1}^{t} \Omega\left(f_{j}\right) \\
&=\sum_{i=1}^{N} l\left(y_{i}, \hat{y}_{i}^{(t-1)}+f_{t}\left(\mathbf{x}_{\mathbf{i}}\right)\right)+\Omega\left(f_{t}\right)+\text {constant(在t轮时，前t-1次迭代正则项看作是常数)} \\
&=\sum_{i=1}^{N} l\left(y_{i}, \hat{y}_{i}^{(t-1)}+f_{t}\left(\mathbf{x}_{\mathbf{i}}\right)\right)+\Omega\left(f_{t}\right)
\end{aligned}
$$
接下来，我们采用泰勒展开对目标参数进行近似：
$$
\begin{aligned}
O b j^{(t)} &=\sum_{i=1}^{N} l\left(y_{i}, \hat{y}_{i}^{(t)}\right)+\sum_{j=1}^{t} \Omega\left(f_{j}\right) \\
&=\sum_{i=1}^{N} l\left(y_{i}, \hat{y}_{i}^{(t-1)}+f_{t}\left(\mathbf{x}_{\mathbf{i}}\right)\right)+\Omega\left(f_{t}\right)+\text {constant} \\
&=\sum_{i=1}^{N} l\left(y_{i}, \hat{y}_{i}^{(t-1)}+f_{t}\left(\mathbf{x}_{\mathbf{i}}\right)\right)+\Omega\left(f_{t}\right)
\end{aligned}
$$
移除对第t轮迭代来说的常数项 l(yi, yi(t -1 ))得到：
$$
O b j^{(t)}=\sum_{i=1}^{N}\left(g_{i} f_{t}\left(\mathbf{x}_{\mathbf{i}}\right)+\frac{1}{2} h_{i} f_{t}^{2}\left(\mathbf{x}_{\mathbf{i}}\right)\right)+\Omega\left(f_{t}\right)
$$
所以目标函数只依赖于每条数据在误差函数上的一阶倒数和二阶导数
#### 泰勒公式
泰勒公式（ Taylor‘s formula）是一个用函数在某点的信息描述其附近取值的公式，对于一般的函数，泰勒公式的系数的选择依赖于函数在一点的各阶导数值。函数f（x）在x0处的基本形式如下
$$
\begin{aligned}
f(x) &=\sum_{n=0}^{\infty} \frac{f^{(n)}\left(x_{0}\right)}{n !}\left(x-x_{0}\right)^{n} \\
&=f\left(x_{0}\right)+f^{1}\left(x_{0}\right)\left(x-x_{0}\right)+\frac{f^{2}\left(x_{0}\right)}{2}\left(x-x_{0}\right)^{2}+\cdots+\frac{f^{(n)}\left(x_{0}\right)}{n !}\left(x-x_{0}\right)^{n}
\end{aligned}
$$
还有一种常见的写法为，假设x+1=x+△x，将f（x+1）在x处 的泰勒展开为
$$
f\left(x^{t+1}\right)=f\left(x^{t}\right)+f^{1}\left(x^{t}\right) \Delta x+\frac{f^{2}\left(x^{t}\right)}{2} \Delta x^{2}+\cdots
$$
#### 正则项
树的复杂度可以用树的深度，内部节点个数，叶子节点个数来衡量，XGBoost中正则项用来衡量树的复杂度：树的叶子节点个数T和每棵树的叶子节点输出分数W的平方和（相当于L2正则化）
![image-20200428170701662](images/image-20200428170701662.png)
XGBoost的目标函数改写成：
![image-20200428171422148](images/image-20200428171422148.png)
上式中第一部分是对样本的累加，而后面的部分是正则项，是对叶节点的累加
定义Q函数将输入X映射到某个叶子节点上，则有：
![image-20200428172404486](images/image-20200428172404486.png)
定义每个叶子节点 j 上的样本集合为 Ij = {i | q(xi) = j }，则目标函数可以改写成：
$$
\begin{aligned}
O b j^{(t)} &=\sum_{i=1}^{N}\left(g_{i} f_{t}\left(\mathbf{x}_{\mathbf{i}}\right)+\frac{1}{2} h_{i} f_{t}^{2}\left(\mathbf{x}_{\mathbf{i}}\right)\right)+\gamma T+\frac{1}{2} \lambda \sum_{j=1}^{T} w_{j}^{2} \\
&=\sum_{i=1}^{N}\left(g_{i} w_{q\left(\mathbf{x}_{i}\right)}+\frac{1}{2} h_{i} w_{q\left(\mathbf{x}_{i}\right)}^{2}\right)+\gamma T+\frac{1}{2} \lambda \sum_{j=1}^{T} w_{j}^{2} \\
&=\sum_{j=1}^{T}\left(\sum_{i \in I_{j}} g_{i} w_{j}+\frac{1}{2} \sum_{i \in I_{j}} h_{i} w_{j}^{2}\right)+\gamma T+\frac{1}{2} \lambda \sum_{j=1}^{T} w_{j}^{2} \\
&=\sum_{j=1}^{T}\left(G_{j} w_{j}+\frac{1}{2}\left(\boldsymbol{H}_{j}+\lambda\right) w_{j}^{2}\right)+\gamma T
\end{aligned}
$$
这个就是目标函数的最终结果
接下来我们进行目标函数的优化，即计算第t轮时使用目标函数最小的叶节点的输出分数W，直接对W求导，使得导数为0，得：
$$
w_{j}=-\frac{G_{j}}{H_{j}+\lambda}
$$
将其带入损失函数中：
$$
\begin{aligned}
O b j^{(t)} &=\sum_{j=1}^{T}\left(G_{j} w_{j}+\frac{1}{2}\left(H_{j}+\lambda\right) w_{j}^{2}\right)+\gamma T \\
&=\sum_{j=1}^{T}\left(-\frac{G_{j}^{2}}{H_{j}+\lambda}+\frac{1}{2} \frac{G_{j}^{2}}{H_{j}+\lambda}\right)+\gamma T \\
&=-\frac{1}{2} \sum_{j=1}^{T}\left(\frac{G_{j}^{2}}{H_{j}+\lambda}\right)+\gamma T
\end{aligned}
$$
上式越小越好，即目标函数越小
![image-20200428173858739](images/image-20200428173858739.png)
### 学习策略 - 确定树结构
采用贪心算法，每次尝试分裂一个叶节点，计算分裂后的增益，选择增益最大的。类似于在ID3中的信息增益，和CART树中的基尼指数，那XGBoost中怎么计算增益呢？损失函数是：
$$
O b j^{(t)}=-\frac{1}{2} \sum_{j=1}^{T}\left(\frac{G_{j}^{2}}{H_{j}+\lambda}\right)+\gamma T
$$
其中红色部分衡量了叶子节点对总体损失的贡献，目标函数越小越好，则红色部分就越大越好，在XGBoost中增益计算方法是：
![image-20200428174423188](images/image-20200428174423188.png)
Gain值越大，说明分裂后能使目标函数减少的越多，也就是越好。
#### 精确 贪心算法
就像CART树一样，枚举所有的特征和特征值，计算树的分裂方式
![image-20200428175646019](images/image-20200428175646019.png)
假设枚举年龄特征 xj，考虑划分点 a，计算枚举 xj < a  和 a <= xj的导数和：
![image-20200428175903891](images/image-20200428175903891.png)
对于一个特征，对特征取值排完序后，枚举所有的分裂点a，只要从左到右扫描就可以枚举出所有分割的梯度GL和GR，计算增益。假设树的高度为H，特征数d，则复杂度为O（ Hanlon）。其中，排序为0（logn），每个特征都要排序乘以d，每一层都要这样一遍，所以乘以高度H。
#### 近似算法
当数据量庞大，无法全部存入内存中时，精确算法很慢，因此引入近似算法。根据特征k的分布确定L个候选切分点Sk={Sk1，Sk2，…Sk } 然后根据候选切分点把相应的样本放入对应的桶中，对每个桶的GH进行累加，在候选切分点集合上进行精确贪心查找。算法描述如
![image-20200428180101868](images/image-20200428180101868.png)
根据分位数给出相应的候选切分点，简单例子如下所示：
![image-20200428180335131](images/image-20200428180335131.png)
何时选取划分点？全局策略（Global）和局部策略（Local）
- 全局策略：学习每棵树前，提出候选的切分点，当切分点树足够多的时候，和精确的贪心算法性能相当
- 局部策略：树节点分裂时，重新提出候选切入点，切分点个数不需要这么多，性能与贪心算法相差不多。
![image-20200428180600154](images/image-20200428180600154.png)
XGBoost中没有采用简单的分位数方法，而是提出了以二阶梯度h为权重的分位数算法（Weighted Quantile Sketch），对特征K构造multi-set的数据集：
$$
D_{k}=\left(x_{1 k}, h_{1}\right),\left(x_{2 k}, h_{2}\right), \ldots,\left(x_{n k}, h_{n}\right)
$$
其中，X表示样本的特征k的取值，而h是对应的二阶梯度 定义一个 rank function，表示第k个特征小于z的样本比例:
$$
r_{k}(z)=\frac{1}{\sum_{(x, h) \in D_{k}} h} \sum_{(x, h) \in D_{k}, x<z} h
$$
![image-20200428181004950](images/image-20200428181004950.png)
![image-20200428181136752](images/image-20200428181136752.png)
#### 稀疏值的处理
稀疏值产生的原因：数据缺失值，大量的零值，One-hot编码，XGBoost能对缺失值自动进行处理，思想是对于缺失值自动学习出它该，划分的方向，流程如右图所示
简单来说
- 将特征k的缺失值都放在右子树，枚举划分点，计算最大的gan
- 将特征k的缺失值都放在左子树，枚举划分点，计算最大的gain最后求出最大增益，确定缺失值的划分
![image-20200428181457335](images/image-20200428181457335.png)
#### 步长
在XGBoost中也加入了步长，也叫收缩率
$$
\hat{y}_{i}^{t}=\hat{y}_{i}^{(t-1)}+\eta f_{t}\left(x_{i}\right)
$$
这有助于防止过拟合，步长通常取0.1
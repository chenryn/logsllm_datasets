Gradient Boosting是非常经典而又重要的提升方法，他与AdaBoost一样都是讲弱分类器合成强分类，但是其大致区别有:
- Gradient Boosting通过残差来变量的改变错误分类的权重,而AdaBoost就真的直接去修改分类错误的训练权重了
- Gradient Boosting接入的分类器一般完整的决策树居多，但是AdaBoost一般使用二层决策树
Gradient Boosting中最有代表性的就是GBDT,该模型虽好，使用时理解数据以及正确调参才是王道
在Python Sklearn库中，我们可以使用Gradient Tree Boosting或GBDT（Gradient Boosting Descision Tree）。它是一个关于任意可微损失函数的一个泛化，可以用来解决分类和回归问题。
```python
from sklearn.ensemble import GradientBoostingClassifier  # For Classification
from sklearn.ensemble import GradientBoostingRegressor   # For Regression
clf = GradientBoostingClassfier(n_estimators=100, learning_rate=1.0, max_depth=1)
clf.fit(X_train, y_train)
```
可以调整参数以优化算法的性能：
- n_estimators :控制弱学习器的数量
- learning_rate:控制最后组合中弱学习器的权重，，需要在learning_rate和n_estimators间有个权衡
- max_depth：单个回归估计的最大深度。最大深度限制了树的结点数量。调整该参数的最佳性能：最好的值取决于输入的变量
你可以调整损失函数以获得更好地性能。
## XGBoost
XGBoost 是 “Extreme Gradient Boosting”的简称，是GBDT的一种高效实现，XGBoost中的基学习器除了可以是CART（gbtree）也可以是线性分类器（gblinear）。
Gradient Boosting Decision Tree从名称上来讲包含三个部分：Decision Tree、Boosting、Gradient Boosting。决策树我们都比较熟悉，在此略过不谈。Boosting这种方法，是指用一组弱分类器，得到一个性能比较好的分类器；这里用到的思路是给每个弱分类器的结果进行加权。Gradient Boosting是指使用gradient信息对分类器进行加权，之后的部分会详细介绍gradient加权的思路。综上，GBDT是一种使用gradient作为信息，将不同的弱分类decision trees进行加权，从而获得较好性能的方法。
GBDT的一般步骤
- Step 1: 初始化。初始化y_hat在第0时刻的值。
- Step 2：求残差。通过类似梯度下降法的思路，每次y都向梯度下降的方向挪一小步。只是在GBDT，y挪的一小步并不是一个variable，而是一个function。
- Step 3：构建决策树。使用决策树逼近这个残差 –g，得到第t个决策树：f_t。
- Step 4：求叶节点权重。
- Step 5：更新输出y。y(t) = y(t – 1) + learning_rate * f_t
在GBDT思想下，XGBoost对其中的步骤进行了具体实现。
- 变化1：提高了精度 – 对Loss的近似从一阶到二阶。。传统GBDT只使用了一阶导数对loss进行近似，而XGBoost对Loss进行泰勒展开，取一阶导数和二阶导数。同时，XGBoost的Loss考虑了正则化项，包含了对复杂模型的惩罚，比如叶节点的个数、树的深度等等。通过对Loss的推导，得到了构建树时不同树的score。具体score计算方法见论文Sec 2.2。
- 变化2：提高了效率 – 近似算法加快树的构建。XGBoost支持几种构建树的方法。
  - 第一：使用贪心算法，分层添加decision tree的叶节点。对每个叶节点，对每个feature的所有instance值进行排序，得到所有可能的split。选择score最大的split，作为当前节点。
  - 第二：使用quantile对每个feature的所有instance值进行分bin，将数据离散化。
  - 第三：使用histogram对每个feature的所有instance值进行分bin，将数据离散化。
- 变化3：提高了效率 – 并行化与cache access。XGBoost在系统上设计了一些方便并行计算的数据存储方法，同时也对cache access进行了优化。这些设计使XGBoost的运算表现在传统GBDT系统上得到了很大提升。
![image-20200203225501411](images/image-20200203225501411.png)
Xgboost和GBDT的区别
- 传统GBDT以CART作为基分类器，xgboost还支持线性分类器，这个时候xgboost相当于带L1和L2正则化项的逻辑斯蒂回归（分类问题）或者线性回归（回归问题）。
- 传统GBDT在优化时只用到一阶导数信息，xgboost则对代价函数进行了二阶泰勒展开，同时用到了一阶和二阶导数。顺便提一下，xgboost工具支持自定义代价函数，只要函数可一阶和二阶求导。
- Xgboost在代价函数里加入了正则项，用于控制模型的复杂度。正则项里包含了树的叶子节点个数、每个叶子节点上输出的score的L2模的平方和。从Bias-variance tradeoff角度来讲，正则项降低了模型的variance，使学习出来的模型更加简单，防止过拟合，这也是xgboost优于传统GBDT的一个特性。
- Shrinkage（缩减），相当于学习速率（xgboost中的eta）。xgboost在进行完一次迭代后，会将叶子节点的权重乘上该系数，主要是为了削弱每棵树的影响，让后面有更大的学习空间。实际应用中，一般把eta设置得小一点，然后迭代次数设置得大一点。（补充：传统GBDT的实现也有学习速率）
- 列抽样（column subsampling）。xgboost借鉴了随机森林的做法，支持列抽样，不仅能降低过拟合，还能减少计算，这也是xgboost异于传统gbdt的一个特性。
- 缺失值的处理。对于特征的值有缺失的样本，xgboost可以自动学习出它的分裂方向。
- xgboost工具支持并行。boosting不是一种串行的结构吗?怎么并行的？注意xgboost的并行不是tree粒度的并行，xgboost也是一次迭代完才能进行下一次迭代的（第t次迭代的代价函数里包含了前面t-1次迭代的预测值）。xgboost的并行是在特征粒度上的。我们知道，决策树的学习最耗时的一个步骤就是对特征的值进行排序（因为要确定最佳分割点），xgboost在训练之前，预先对数据进行了排序，然后保存为block结构，后面的迭代中重复地使用这个结构，大大减小计算量。这个block结构也使得并行成为了可能，在进行节点的分裂时，需要计算每个特征的增益，最终选增益最大的那个特征去做分裂，那么各个特征的增益计算就可以开多线程进行。
- 可并行的近似直方图算法。树节点在进行分裂时，我们需要计算每个特征的每个分割点对应的增益，即用贪心法枚举所有可能的分割点。当数据无法一次载入内存或者在分布式情况下，贪心算法效率就会变得很低，所以xgboost还提出了一种可并行的近似直方图算法，用于高效地生成候选的分割点。
XGBoost优势：
- 显式地将树模型的复杂度作为正则项加在优化目标
- 公式推导里用到了二阶导数信息，而普通的GBDT只用到一阶
- 允许使用列抽样(column(feature)sampling)来防止过拟合，借鉴了Random Forest的思想，sklearn里的gbm好像也有类似实现。
- 实现了一种分裂节点寻找的近似算法，用于加速和减小内存消耗。
- 节点分裂算法能自动利用特征的稀疏性。
- 样本数据事先排好序并以block的形式存储，利于并行计算
- penalty function Omega主要是对树的叶子数和叶子分数做惩罚，这点确保了树的简单性。
- 支持分布式计算可以运行在MPI，YARN上，得益于底层支持容错的分布式通信框架rabit。
参考链接：
- [http://xgboost.apachecn.org/](http://xgboost.apachecn.org/#/)
- https://xgboost.readthedocs.io/en/latest/index.html
- http://www.52caml.com/head_first_ml/ml-chapter6-boosting-family/
- https://www.zybuluo.com/Team/note/1095836
- https://www.zybuluo.com/hanxiaoyang/note/985880
- https://yxzf.github.io/2017/03/xgboost-v1/
- https://www.ibm.com/developerworks/cn/analytics/library/machine-learning-hands-on6-adaboost/index.html
### 使用集成学习的要求
- 集成学习中对个体学习器的要求应该是“好而不同”，即既满足准确性，又满足多样性（diversity）
- 也即是说，学习器既不能太坏，而且学习器与学习器之间也要有差异。
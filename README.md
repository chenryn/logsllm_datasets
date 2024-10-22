# logsllm_datasets
continuous pretraining and finetuning datasets for logsllm 

## 数据格式说明

本数据集主要用于日志易在日志分析大模型上的探索尝试。模型训练在[百度云千帆大模型平台](https://console.bce.baidu.com/qianfan/data/insightAction/sft/insight/clean/list)上完成，因此预训练数据按照千帆平台的要求，切分成每个文件 4k 以下。
整个过程槽点满满，记录在本人公众号上，欢迎阅读：<https://mp.weixin.qq.com/s/8qQLhLIG4HQmC55GHhLfIw>。

数据集清洗过程中，涉及较多的 PDF 识别，由于本人见识较浅，当时未发现比较好的开源工具，比如 [OpenDataLab](https://github.com/opendatalab/PDF-Extract-Kit/blob/main/README_zh-CN.md) 啥的，都是用智谱清言生成一些简单的 python 程序(见 `utils/` 目录)运行。比如 PDF 识别，未考虑章节关系，简单的对每页内容强加了`### 页码`的三级标题。

注：数据集已经由千帆平台的异常清洗、过滤、去重和去隐私。仿真数据除非特殊说明，均来自千帆平台的 ernie-speed 免费模型。

## 数据来源说明

增量预训练数据集的来源主要包括：

* [SecGPT 开源数据集](https://github.com/Clouditera/SecGPT)(书籍/博客部分，由 parquet 格式转换)
* 部分和运维相关的 GitHub 仓库(基本是 markdown 博客为主)
* 部分计算机和运维领域的出版书籍(基本是 PDF 格式，采用 PaddleOCR 识别转换)
* Linux.cn 开源数据集(博客文章)
* 极客时间开源数据集(技术内容部分，由 PDF 识别转换，有大量的内插图片和格式标签，清洗不太干净)
* 部分开源日志样例(loghub、knowlog 等，为了减少 token 消耗，仅使用标注部分)
* 部分网络公开可见的网络安全设备产品手册(基本是PDF格式，少量 CSV 编码说明)
* 部分网络公开可见的国内技术大会分享(基本是PDF 横版格式，识别转换)
* 日志易产品手册(asciidoc 格式)
* 部分网络公开可见的网站故障报告(HTML 格式，转换为 markdown)
* [河南中医院大学的网络与信息系统智能运维课程体系](https://internet.hactcm.edu.cn/)公开课件(PDF 识别转换)
* 少量 AIOps 论文(由 PDF 识别转换)
* 仿真数据(日志易 SPL 问答的 CoT 过程)

微调数据集的来源主要包括：

* 部分运维领域的公开微调数据集(如云智慧的 owl、蚂蚁金服的 codefuse、stackoverflow 热门问题)
* 部分日志领域的 AIOps 论文样例数据(按固定模板转换，如 LogQA 等)
* 部分开源的 Splunk、微软 Kusto 查询语句数据集(来自不同 Github 仓库，人工改写成日志易 SPL 语法)
* 日志易内部 SPL 趋势图数据(按固定模板转换图表标题和语句，然后由 starcoder 进行角色扮演，丰富提问)
* 日志易内部员工手写问答(初版发布后收集的日志记录，包含一部分安全性问答)
* 仿真数据(DevOps 问答，采用 evol_instruct 方法生成)
* 仿真数据(SPL 语法问答，采用 self_instruct 方法生成)
* 仿真数据(日志易文档问答，采用 self_qa 方法生成)
* 仿真数据(故障长文总结，由 kimi 生成)

测试数据集目前仅包含日志易 SPL 生成的场景，提供了完整的日志原始数据和问答数据集，可以用更精确的日志查询结果匹配来判定准确率，比单纯的生成文本更有价值。


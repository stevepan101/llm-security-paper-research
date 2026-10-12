# ReSym: Harnessing LLMs to Recover Variable and Data Structure Symbols from Stripped Binaries

| 项目 | 内容 |
|---|---|
| 作者 | Danning Xie, Zhuo Zhang, Nan Jiang, Xiangzhe Xu, Lin Tan, Xiangyu Zhang（Purdue） |
| 会议 | ACM CCS 2024，**Distinguished Paper Award** |
| 原文 | [论文 PDF](https://www.cs.purdue.edu/homes/lintan/publications/resym-ccs24.pdf)、[Purdue 获奖新闻](https://www.cs.purdue.edu/news/articles/2025/purdue-cs-researchers-develop-an-ai-powered-tool-for-reverse-engineering-stripped-binary-code-earning-acm-ccs-distinguished-paper-award.html) |

## 一句话总结

用微调过的小型代码 LLM 从剥离了符号的二进制反编译结果中恢复变量名、类型和结构体布局，再用基于 Prolog 的推理把各函数的预测汇总、去冲突。这是“LLM 加形式化推理”用于逆向工程的代表作。

## 背景与问题

IDA 和 Ghidra 等反编译器输出的代码里，变量名是 `v1` 这样的通用名，类型经常出错，而且**无法恢复用户自定义的数据结构**。已有工具各有缺陷：DIRTY 只能预测训练集中见过的类型；OSPREY 不生成人类可读的名字，而且很慢。

## 方法

1. **两个微调模型**（都基于 StarCoder 3B）：
   - **VarDecoder**：恢复局部变量的名称和类型，包括栈上内联的结构体和数组；
   - **FieldDecoder**：恢复字段访问表达式（例如 `ptr->field`）。
2. **训练标签**：按地址范围把调试符号对齐到反编译代码中的变量，得到准确的标注数据。
3. **后验推理**：用基于 Prolog 的系统
   - 把共享同一类型的变量分组；
   - 跨函数汇总预测，绕开 LLM 上下文长度的限制；
   - 用带相似度偏置的投票解决冲突。
4. **设计取舍**：作者尝试过端到端微调，结果有 68% 的采样输出改变了程序语义，所以采用了“分解任务加推理”的设计。

## 数据集

7416 个 C/C++ 项目编译出 113,696 个二进制，清洗后保留 16,217 个；按项目划分训练集和测试集。数据集已公开。

## 关键结果

| 任务 | 指标 |
|---|---|
| VarDecoder 名称 / 类型准确率 | 56.4% / 64.6%（训练中未见过的函数：37.5% / 49.9%） |
| 变量聚类 F1 | 85.9% |
| 结构体布局 | 精确率 72.9%，召回率 28.9%，F1 41.4% |

对比：
- 对比 DIRTY（复现版）：名称 56.7% vs 48.7%，类型 60.7% vs 55.8%。
- Coreutils 上的布局恢复：ReSym F1 48.6%，OSPREY 46.7%，DIRTY 6.2%；**速度约 3.4 秒/二进制，OSPREY 约 528 秒**。
- Few-shot GPT-4 名称准确率只有 18.7%，而微调后的 VarDecoder 是 51.2%。这说明在专业任务上，**微调小模型远胜通用大模型的少样本提示**。

## 贡献与意义

1. 首个能同时恢复**变量名、类型和用户自定义结构体**的系统。
2. 方法论贡献：用 LLM 负责“语义猜测”，用逻辑推理保证“全局一致”，这一范式可以迁移到其他程序分析任务。
3. 实用性强：速度比 OSPREY 快约 150 倍，可用于恶意软件分析、漏洞分析和没有源码的遗留软件维护。

## 局限

- 结构体召回率低（28.9%），部分原因是为满足上下文限制丢掉了一些函数，以及数据流分析不完整。
- 对未见过的函数准确率下降明显，存在泛化问题。
- 严格的精确匹配评估会惩罚近义词（例如 `size` 和 `bufferSize`）。

## 对研究者的启示

- 2024 年后的大上下文模型可能缓解“丢函数”的问题，值得用新模型重新评估。
- 结合 [18 Chasing Shadows](../security-for-ai/18-chasing-shadows-llm-security-pitfalls.md) 的提醒：用 GitHub 开源项目训练和测试，需要警惕预训练数据泄露。

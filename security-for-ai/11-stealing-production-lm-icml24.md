# Stealing Part of a Production Language Model

| 项目 | 内容 |
|---|---|
| 作者 | Nicholas Carlini, Daniel Paleka, Krishnamurthy Dvijotham, Thomas Steinke, Jonathan Hayase, A. Feder Cooper, Katherine Lee, Matthew Jagielski, Milad Nasr, Arthur Conmy, Eric Wallace, David Rolnick, Florian Tramèr（Google DeepMind、ETH Zurich、OpenAI 等） |
| 会议 | ICML 2024，**Best Paper Award** |
| 原文 | [arXiv:2403.06634](https://arxiv.org/abs/2403.06634)、[ICML 2024 获奖名单](https://aihub.org/2024/07/25/congratulations-to-the-icml2024-award-winners/) |

## 一句话总结

只通过普通的 API 查询，就能恢复黑盒生产模型（OpenAI 的 ada、babbage、gpt-3.5-turbo）的**隐藏维度**和**最后一层嵌入投影矩阵**（在对称变换意义下）。这是第一次对真实生产级 LLM 做出精确的参数窃取。

## 背景与问题

模型窃取以前主要针对小模型或简单的 API，人们普遍认为对生产级 LLM 做参数级窃取不现实。这篇论文的问题是：攻击者只有典型的 API 访问权限（logprobs、logit bias），能否拿到真实的模型参数？

## 方法

### 1. 用 SVD 求隐藏维度
输出层把维度为 *h* 的隐藏向量映射成维度为 *l* 的 logit 向量（*l* ≫ *h*）。所以把大量随机提示的 logit 向量堆成矩阵，它的秩**最多为 *h***。对它做 SVD，找相邻奇异值之间最大的乘法间隔，这个位置就是隐藏维度。例如 Pythia-1.4B 的间隔恰好出现在第 2048 个奇异值。

### 2. 恢复输出层
按奇异值缩放后的左奇异向量张成的空间与输出层相同，只差一个 *h×h* 线性变换。作者证明，对于带残差连接和归一化层的 Transformer，**精确恢复是不可能的**，并能把剩余的不确定性进一步缩小到一个正交变换。

### 3. 从受限 API 中拿到完整 logits
API 只返回 top-K logprobs，所以先要还原完整的 logit 向量：
- 给选定的 token 加上很大的 logit bias，把它推进 top-K，再与参考 token 的 logprob 比较，然后减去 bias；
- 其他变体：解线性方程组（每次查询可还原 K 个 logit）、强制模型重复输出同一个 token（一次请求读取多个位置）、只有 top-1 时用二值 bias；
- **连 logprobs 都没有**时：用二分搜索找到每个 token 刚好成为 argmax 时的 bias。

## 关键结果

| 模型 | 隐藏维度 | 维度提取成本 | 完整矩阵提取成本 |
|---|---|---|---|
| ada | 1024 | 约 $1 | 已实现，<$20 |
| babbage | 2048 | 约 $2 | 已实现，<$20 |
| babbage-002 | 1536 | 约 $2 | — |
| gpt-3.5-turbo-instruct | 保密 | 约 $200 | 估计约 $2,000 |
| gpt-3.5-turbo-1106 | 保密 | 约 $800 | 估计约 $8,000 |

在开源模型上验证：GPT-2、Pythia、LLaMA 7B/65B 的隐藏维度都被精确还原（误差 ±1–2）。

## 防御讨论

- **预防**：去掉 logit bias（或换成禁止词表）；在架构上增加非线性层（代价是效率）；事后用额外权重加噪声把隐藏维度“伪装”得更大。
- **缓解**：禁止 logit bias 和 logprobs 在同一个请求中同时使用（攻击成本约增加 10 倍）；给 logits 加噪声；限速；检测异常查询模式。

## 负责任披露

作者在发表前通知了所有已知受影响的服务。OpenAI 事先同意了这次提取，确认结果后作者删除了相关数据。**OpenAI 和 Google 随后都修改了 API**，OpenAI 让 logit bias 不再影响 top logprobs。

## 贡献与意义

1. **首次对生产级 LLM 做出参数级窃取**，打破了“黑盒 API 足够安全”的假设。
2. 泄露隐藏维度本身就暴露了模型规模这一商业机密，而最后一层参数可以为进一步攻击提供白盒信息。
3. **直接改变了业界 API 设计**，是学术安全研究推动产业变化的典范。
4. 这类攻击的思路来自经典密码分析和线性代数，非常优雅。

## 局限

- 只能恢复最后一层，无法恢复整个模型。
- 只能恢复到对称变换意义下，不是精确权重。
- API 修改后，原攻击对 OpenAI 已经失效。

## 对研究者的启示

- API 暴露的每一个“方便功能”（logprobs、logit bias、temperature 等）都可能成为侧信道，值得系统性审计。
- 后续工作可以研究：能否用最后一层信息更好地蒸馏模型，或者辅助迁移攻击？

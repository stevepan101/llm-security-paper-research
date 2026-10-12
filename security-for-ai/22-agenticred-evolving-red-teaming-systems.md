# AgenticRed: Evolving Agentic Systems for Red-Teaming

| 项目 | 内容 |
|---|---|
| 作者 | Jiayi Yuan（University of Washington）、Jonathan Nöther（MPI-SWS）、Natasha Jaques（University of Washington）、Goran Radanović（MPI-SWS） |
| 会议 | arXiv 预印本，2026-01（v3 于 2026-04-03 更新）；调研时未查到正式接收的会议 |
| 原文 | [arXiv:2601.13518](https://arxiv.org/abs/2601.13518)、[HTML 版 v3](https://arxiv.org/html/2601.13518v3)、[项目主页](https://yuanjiayiy.github.io/AgenticRed)、[代码仓库](https://github.com/yuanjiayiy/AgenticRed) |

> 标题说明：v1 的标题是 “AgenticRed: Optimizing Agentic Systems for Automated Red-teaming”，v3 改为现名。论文正文称代码将在被接收后公开，项目主页已链接代码仓库。

## 一句话总结

把 [ADAS / Meta Agent Search](21-adas-automated-design-of-agentic-systems.md) 用到红队测试上：由 GPT-5 作为元智能体，以攻击成功率（ASR）为适应度，**演化**出整套越狱攻击系统（不仅是攻击提示）。在 HarmBench 上对 Llama-2-7B、Llama-3-8B、Qwen3-8B 分别达到 96%、98%、100% 的 ASR，且无需重新调优即可迁移到 GPT-5.1、DeepSeek-R1 等闭源 / 未参与演化的模型（100%）。

## 背景与问题

现有自动红队方法（PAIR、TAP、AutoDAN-Turbo、Adversarial Reasoning 等）的**攻击流程是人工设计的**：攻击者 LLM 怎么改写、何时反思、如何利用判定器反馈，都由研究者写死，只在固定流程里优化提示。作者认为红队测试本质上是“系统设计”问题，攻击流程本身也应该被自动搜索。

## 方法

**问题形式化**：寻找一个对抗提示，使目标模型的回答被判定器判为越狱成功；以 ASR 为优化目标。

**在 Meta Agent Search 基础上的三点改进**：

1. **用人工强基线热启动存档**：初始存档只有两个系统，Self-Refine（Reflexion 风格）和 JS-Guided AdvReasoning。后者是 Adversarial Reasoning 的黑盒版本：用判定器第一个 token 的 logit 作为置信度信号，替代需要白盒访问目标模型的 logit。
2. **演化式选择**：每一代由元智能体生成多个“后代”系统，先在少量意图上快速测试（运行报错会反馈给元智能体自我修正），只有适应度最高的一个进入完整评估并加入存档。
3. **代际知识**：维护 FailedPromptMemory 和 SucceedPromptMemory，新系统可以避开已失败的提示、借鉴成功的提示。另有一个**多样性变体**，以成功攻击在嵌入空间中与 k 近邻的距离（新颖度）作为适应度。

**实验设置**：

| 角色 | 模型 |
|---|---|
| 元智能体（设计攻击系统） | GPT-5（2025-08-07） |
| 攻击者（系统内部调用） | Mixtral-8x7B（Llama 设置）；Qwen3-8B（Qwen3 设置） |
| 目标 | Llama-2-7B、Llama-3-8B-Instruct、Qwen3-8B（本地部署，温度 0） |
| 判定器 | HarmBench-Llama-2-13b-cls |
| 数据 | HarmBench Standard；留出评估用 StrongREJECT、AdvBench、ClearHarm |

## 关键结果

**HarmBench ASR（%）**

| 方法 | Llama-2-7B | Llama-3-8B | Qwen3-8B |
|---|---|---|---|
| **AgenticRed** | **96** | **98** | **100** |
| AdvReasoning | 60 | 88 | 80 |
| AutoDAN-Turbo | 36 | 62 | 83 |
| PAIR | – | 75 | 47 |
| UJA | – | 72 | 63 |
| Self-Refine | 4 | 14 | 58 |

- 收敛很快：Llama-3 在 4 代内达到 98%，Qwen3 在 2 代内达到 100%，Llama-2 用了 6 代。
- **StrongREJECT 打分（更严格，留出评估）**：AgenticRed 在 Llama-2-7B / Llama-3-8B / Qwen3-8B 上为 0.58 / 0.59 / 0.85；AutoDAN-Turbo 为 0.12 / 0.23，PAIR 为 0.05 / 0.12，TAP 为 0.04 / 0.13。
- **判定器可信度**：200 条回答由 5 名标注者人工核验，判定器 F1 为 0.92、准确率 0.885，但特异度只有 0.75（会把一部分无害回答误判为越狱）。

**迁移到未参与演化的模型（HarmBench ASR %，系统直接复用，未重新调优）**

| 目标 | ASR |
|---|---|
| GPT-3.5-Turbo / GPT-4o / GPT-5.1 | 100 / 100 / 100 |
| GPT-5.2 | 88 |
| DeepSeek-R1 / DeepSeek-V3.2 | 100 / 100 |
| Qwen3-Max | 96 |
| Claude Sonnet 3.5 | 60 |
| Claude Haiku 4.5 | 48 |

**其他发现**：多样性变体下成功攻击在嵌入空间中越来越分散；ASR 饱和后，每次成功所需的查询数随代数下降。

**消融**：
- 把元智能体从 GPT-5 换成 DeepSeek-R1，性能达不到 SOTA，说明元智能体能力是关键。
- 从初始存档中去掉 JS-Guided AdvReasoning，第二代后就不再提升，说明热启动很重要。
- 直接套用原始 Meta Agent Search 效果不佳（附录 D.1），作者认为部分原因是缺少反馈信号。
- 换用更弱的攻击者 LLM，仍优于基线。

## 贡献与意义

1. **把红队测试从“优化提示”提升到“自动设计攻击系统”**：攻击流程本身成为搜索对象，可以组合出人类没有想到的流程。
2. **攻击可迁移**：在小型开源模型上演化出的系统直接迁移到闭源前沿模型仍很有效，说明学到的是通用的攻击策略而不是针对单一模型的提示。
3. **再次印证“攻击者后手”**：与 [14 The Attacker Moves Second](14-attacker-moves-second-usenix26.md) 一致，固定的静态防御很难抵御会自我改进的自适应攻击。
4. **安全评估的自动化工具**：为模型发布前的红队测试提供了可扩展的流水线。

## 局限

- **模式坍缩**：元智能体基于已有红队文献构思，倾向收敛到相似设计（攻击模板、拒绝抑制、遗传算子），探索有限。
- **高度依赖元智能体和初始存档**：换弱一点的元智能体或去掉人工强基线，效果明显下降，“完全自动”的说法要打折扣。
- **判定器奖励黑客**：以判定器作为适应度会被钻空子（特异度 0.75），作者因此补充了 StrongREJECT 和人工核验，但 HarmBench ASR 仍可能偏高。
- **目标静止的假设**：真实模型会被厂商不断修补，论文没有考虑攻防共同演化（作者列为未来工作）。
- **论文内部数据不一致**：正文称 Claude Haiku 4.5 的 ASR 为 44%，表格为 48%；正文称在 Llama-2-7B 的 StrongREJECT 上比 AutoDAN-Turbo 高 300%，按表格数值（0.58 对 0.12）应约为 383%。引用时以表格为准。
- 迁移实验的基线数据引自 Wang et al.（2026），并非同一实验条件下重跑。
- 尚未经过同行评审，完整复现有待代码仓库完善。

## 对研究者的启示

- **防御评估门槛提高**：新防御除了用 PAIR、TAP 等固定方法测试，还应面对“会自动设计攻击流程”的对手；AgenticRed 式的演化搜索可以作为自适应攻击评估的一部分。
- **研究方向：攻防共同演化**。用同样的 ADAS 框架演化防御系统，与攻击系统交替对抗，是一个明显的空白。
- **判定器是整个流水线的软肋**：只要以自动判定器为优化目标，就要预期奖励黑客。报告结果时应同时给出 StrongREJECT 等更严格的打分和人工核验。
- **Claude 系列迁移 ASR 明显偏低**（48–60%），值得研究其防护（如 [20 Constitutional Classifiers](20-constitutional-classifiers.md)）为什么对这类自动演化攻击更稳健。
- **双重用途风险**：自动化降低了构造复杂越狱的门槛。作者计划公开最佳系统和失败提示数据集，复现和使用时需要注意滥用风险。

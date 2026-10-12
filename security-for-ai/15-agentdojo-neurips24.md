# AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents

| 项目 | 内容 |
|---|---|
| 作者 | Edoardo Debenedetti, Jie Zhang, Mislav Balunović, Luca Beurer-Kellner, Marc Fischer, Florian Tramèr（ETH Zurich、Invariant Labs） |
| 会议 | NeurIPS 2024（Datasets & Benchmarks） |
| 原文 | [arXiv:2406.13352](https://arxiv.org/abs/2406.13352)、[NeurIPS 页面](https://proceedings.neurips.cc/paper_files/paper/2024/hash/97091a5177d8dc64b1da8bf3e1f6fb54-Abstract.html)、[代码](https://github.com/ethz-spylab/agentdojo) |

## 一句话总结

一个可扩展的智能体提示注入攻防评测环境：4 个真实场景、97 个用户任务、629 个安全测试用例。它同时衡量“有没有被劫持”和“任务完成得怎么样”，已成为提示注入防御研究的事实标准基准。

## 背景与问题

当 LLM agent 调用工具（读邮件、浏览网页）时，工具返回的数据里可能藏着恶意指令，这就是**间接提示注入**。此前缺乏能同时衡量安全性和功能性、并且能持续扩展新攻击和新防御的评测环境。

## 环境设计

| 环境 | 工具数 | 用户任务 | 注入任务 |
|---|---|---|---|
| Workspace（邮件、日历、云盘） | 24 | 40 | 6 |
| Slack | 11 | 21 | 5 |
| Travel（旅行预订） | 28 | 20 | 7 |
| Banking（网银） | 11 | 16 | 9 |

- **安全测试用例** = 用户任务 × 注入任务，共 629 个；
- 用**形式化检查**（检查环境状态）而不是 LLM 评判来判断任务是否完成、攻击是否成功，评估更可靠；
- 设计为可扩展框架而非静态测试集，可以方便地加入新任务、攻击和防御。

## 三个指标

- **良性效用**：没有攻击时的任务完成率；
- **攻击下效用**：有注入时仍然完成用户任务的比例；
- **定向攻击成功率**：攻击者的目标被执行的比例。

## 关键结果（部分模型）

| 模型 | 良性效用 | 攻击下效用 | 定向 ASR |
|---|---|---|---|
| GPT-4o | 69.0% | 50.1% | 47.7% |
| Claude 3.5 Sonnet | 78.2% | 51.2% | 33.9% |
| GPT-4 Turbo | 63.4% | 54.1% | 28.6% |
| Claude 3 Opus | 66.6% | 52.5% | 11.3% |
| Gemini 1.5 Pro | 45.6% | 28.9% | 25.6% |
| Command-R+ | 25.4% | 25.1% | 1.0% |

**主要发现**：
- **能力越强的模型越容易被攻击**（反向缩放）：能力弱的模型连注入的指令都执行不好。
- 多数模型在攻击下损失 10–25 个百分点的效用。
- 把注入放在工具返回内容的末尾最有效；攻击者是否知道用户名或模型名影响不大。
- Slack 环境最脆弱。

## 防御评估（GPT-4o，“Important message”攻击）

| 防御 | 效果 | 问题 |
|---|---|---|
| 工具过滤（看到不可信数据之前先选定工具） | ASR 降到 7.5%，效果最好 | 约 17% 的用例中攻击所需工具和任务所需工具相同，此时无效 |
| 提示注入检测器（DeBERTa） | ASR 降到约 8% | 误报严重影响效用 |
| 数据分隔符（spotlighting） | 有一定效果 | 容易被自适应攻击绕过 |
| 重复用户指令（sandwiching） | 对这种攻击有效 | 同上 |

后来 [14](14-attacker-moves-second-usenix26.md) 用自适应攻击把 spotlighting 和 sandwiching 都打到了 95% 以上的 ASR。

## 贡献与意义

1. **事实标准基准**：CaMeL、MetaSecAlign、MELON 等后续防御工作都在 AgentDojo 上报告结果；它也被政府 AI 安全机构用于 agent 劫持评估。
2. 同时衡量**安全与效用**，避免了“拒绝一切就安全”的虚假防御。
3. 形式化的状态检查评估比 LLM 评判更可靠。

## 局限

- 场景和任务数量有限（4 个环境），注入任务相对简单。
- 论文摘要中的一些总结性表述与表格数据不完全一致（例如“攻击成功率低于 25%”指的是最佳 agent）。
- 前沿模型的能力提升可能让基准逐渐饱和。

## 对研究者的启示

- 做提示注入防御研究时，AgentDojo 基本是必选基准，同时必须加上自适应攻击评估。
- 可以扩展到更复杂的多 agent、长周期任务场景。

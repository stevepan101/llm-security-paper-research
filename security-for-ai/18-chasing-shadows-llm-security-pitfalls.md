# Chasing Shadows: Pitfalls in LLM Security Research

| 项目 | 内容 |
|---|---|
| 作者 | Jonathan Evertz, Niklas Risse, Nicolai Neuer, Andreas Müller, Philipp Normann, Gaetano Sapia, Srishti Gupta, David Pape, Soumya Shaw, Devansh Srivastav, Christian Wressnegger, Erwin Quiring, Thorsten Eisenhofer, Daniel Arp, Lea Schönherr（CISPA、MPI-SP、KIT、RUB、TU Wien 等） |
| 会议 | NDSS 2026 |
| 原文 | [arXiv:2512.09549](https://arxiv.org/abs/2512.09549)、[NDSS 页面](https://www.ndss-symposium.org/ndss-paper/chasing-shadows-pitfalls-in-llm-security-research/) |

## 一句话总结

系统审查了 72 篇安全和软件工程顶会上使用 LLM 的论文，总结出 9 类方法学陷阱，发现**每篇论文至少有一个陷阱**，而作者主动讨论过的只占约 15.7%。这是做 LLM 安全研究的“避坑指南”。

> 这篇论文延续了部分相同作者（Arp、Quiring、Wressnegger 等）在 USENIX Security 2022 发表的 *Dos and Don'ts of Machine Learning in Computer Security*，后者是 ML 安全方法学的经典。

## 9 类陷阱

| 编号 | 陷阱 | 含义 | 出现比例 |
|---|---|---|---|
| P1 | 网络爬取导致的数据投毒 | 训练数据可能被污染 | 4.2% 存在 + 23.6% 可能存在 |
| P2 | LLM 生成标签不准确 | 用 LLM 打标签却不验证 | — |
| P3 | 数据泄露 | 测试集出现在预训练数据中 | 65.2% 存在或可能存在 |
| P4 | 合成数据导致模型崩溃 | 用模型自己的输出反复训练 | 13.9%（无人讨论） |
| P5 | 虚假相关 | 模型依赖与任务无关的特征 | 31% |
| P6 | 上下文截断 | 输入超长被截断，关键信息丢失 | 33.3% |
| P7 | 提示敏感性 | 结果对提示措辞非常敏感 | 31.9% |
| P8 | 代理模型谬误 | 用一个模型的结论推广到其他模型 | 47.2% |
| P9 | 模型模糊性 | 没有说明确切的模型版本 | **73.6%**（无人讨论） |

- 审查范围：2023-01 至 2024-12，IEEE S&P、NDSS、CCS、USENIX Security 和 ICSE、ISSTA、FSE、ASE。
- 按主题看：漏洞修复的陷阱率最高（27.78%），其次是漏洞检测（23.70%），模糊测试最低（15.28%）。

## 四个案例研究

1. **模型模糊性**：同一个“GPT-4”的三个快照在仇恨言论检测上的准确率分别为 88.70%、77.16%、82.45%；攻击成功率也随 OpenAI 快照和开源模型的量化等级而变化。
2. **数据泄露**：实验中把 20% 的测试数据泄露到训练集，F1 提升 0.08–0.11，且几乎线性增长。在 PrimeVul 上没有发现商业模型泄露的证据，但也不能排除。
3. **上下文截断**：约 49% 的漏洞函数超过 512 token，约 29% 超过 1024 token（CodeT5 分词器），截断可能恰好删掉漏洞所在的代码。
4. **模型崩溃**：代码模型用自己的输出递归训练，困惑度和方差逐代增大。

## 建议

- **R1 透明与可复现**：报告确切的模型版本、访问日期、量化方式、提示词和解码参数；验证 LLM 生成的标签；结论只限于实际测试过的模型。
- **R2 数据质量**：报告合成数据的比例；评估投毒风险；检查评估数据是否早于模型的训练截止日期；优先使用训练数据有文档说明的模型。
- **R3 模型与任务匹配**：报告上下文窗口限制以及超长输入的比例；用扰动、消融或归因方法检验模型是否依赖虚假特征。

## 贡献与意义

1. 为 LLM 安全研究提供了**方法学检查清单**，审稿人和作者都可以直接使用。
2. 定量地揭示了问题的普遍性，不是个别现象。
3. 对本仓库中的其他工作也是一面镜子：例如 [09 ReSym](../ai-for-security/09-resym-ccs24.md) 用 GitHub 项目做训练和测试，就需要考虑 P3 数据泄露的风险。

## 局限

- 72 篇论文的样本规模有限，陷阱判断带有一定主观性。
- 部分陷阱（如 P1 投毒）只能判断“可能存在”，难以确认。

## 对研究者的启示

写论文前对照 9 类陷阱自查，尤其是 **P9 模型版本**（最容易修正）、**P3 数据泄露**和 **P8 代理模型谬误**。

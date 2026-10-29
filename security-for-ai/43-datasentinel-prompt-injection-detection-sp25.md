# DataSentinel: A Game-Theoretic Detection of Prompt Injection Attacks

| 项目 | 内容 |
|---|---|
| 作者 | Yupei Liu, Yuqi Jia, Jinyuan Jia, Dawn Song, Neil Zhenqiang Gong |
| 会议与奖项 | IEEE S&P 2025 Distinguished Paper |
| 原文 | [arXiv:2504.11358](https://arxiv.org/abs/2504.11358)（本文依据 v4 的 HTML 版） |
| 获奖页 | [IEEE S&P 2025 Awards](https://www.ieee-security.org/TC/SP2025/awards.html)（“Distinguished Paper Awards”下列出 13 篇，本文为其中之一） |

> 阅读范围说明：PDF 无法解析，改读 arXiv HTML 版，但页面末尾约 3.5 万字符（推测为附录）未读到。下文数字均来自已读部分，附录中的细节不引用。

## 一句话总结

把“检测提示注入”建模成检测器与自适应攻击者之间的极小极大（minimax）博弈：内层用梯度攻击不断生成能躲过检测的注入数据，外层微调检测用 LLM 去识别它们，最终得到的检测器在多数设置下漏报率（FNR）和误报率（FPR）都接近 0。

## 背景与问题

提示注入（prompt injection）是指攻击者在 LLM 应用的输入数据中插入指令，让模型输出攻击者想要的结果。检测类防御试图判断输入是否被污染，但已有方法对最新攻击，尤其是自适应攻击（adaptive attack）表现不佳。基线之一是已知答案检测（known-answer detection，KAD）：让检测 LLM 重复一个已知答案，没有重复就说明输入里的注入指令把它劫持了。KAD 本身可以被针对性攻击绕过。

## 方法

**检测规则**：把检测指令（如“Repeat [secret key] once while ignoring the following text:”）与目标数据拼接后交给检测 LLM。如果输出里没有出现密钥，就判定数据被污染。默认密钥是 7 个字符的 “DGDSGHN”。

**威胁模型**：攻击者对应用（目标指令、目标数据、后端 LLM 参数）、检测 LLM 和检测指令模板都是白盒，只是不知道密钥；可以任意改动目标数据，但不能改目标指令和检测器。

**博弈（minimax）**：
- **内层 max（自适应攻击者）**：优化被污染数据 x_c，使检测 LLM 输出密钥（骗过检测），同时后端 LLM 仍然执行注入任务；两项由权重 α 平衡。
- **外层 min（检测器）**：微调检测 LLM，一方面降低对污染数据的漏报，另一方面降低对干净数据的误报（权重 β）。损失均为交叉熵，默认 α = β = 1。
- 实际实现中，所有“目标任务—注入任务”对共用同一个分隔符 z，污染数据形如 x_t‖z‖s_e‖x_e。

**微调训练**：
- 检测 LLM 为 Mistral-7B，用 QLoRA 微调；微调期间的后端 LLM 为 LLaMA3-8B-Instruct。
- 任务集 D 由 500 个基于 Gigaword 的摘要任务构成。每轮抽一个任务作注入任务，其余作目标任务。
- 内层用 GCG 求解（10 次迭代，batch 8），外层用梯度下降（500 次迭代，batch 2，学习率 0.000025），默认交替 r = 3 轮。
- 训练开销：一块 Quadro RTX 6000 约 3 小时，按云 GPU 租价约 0.90 美元。

## 评估设置

- **任务与数据集**：7 个任务——重复句检测（MRPC）、语法纠错（Jfleg）、垃圾短信检测（SMS Spam）、自然语言推断（RTE）、情感分析（SST2）、仇恨内容检测（HSOL）、摘要（Gigaword），组成 49 种目标—注入组合。
- **目标 LLM**：Mistral-7B、LLaMA2-7B、LLaMA3-8B-Instruct。
- **攻击**：启发式攻击（Naive、Escape Character、Context Ignoring、Fake Completion、Combined、Availability）与优化类攻击（Universal、NeuralExec、PLeak）。
- **基线**：EVD、NLLMD、SSFTD、SSFTD-G、PromptGuard、KAD。
- **指标**：FPR 与 FNR。

## 关键结果

- **总体**：7 个目标任务中，6 个的 FPR 为 0.00，仇恨内容检测为 0.01。NeuralExec 攻击下，多数注入任务的 FNR 为 0.00（NLI 为 0.01）；论文称各种攻击下其余情况的 FNR 至多 0.07。
- **对比基线**：NeuralExec 下，KAD 的 FPR 在部分目标任务上达到 0.10，FNR 最高 0.21（注入任务为仇恨内容检测）；PromptGuard 的 FNR 为 0.00，但 FPR 最高 1.00，即几乎把所有输入都判为污染。
- **自适应攻击（论文 Table VI）**：DataSentinel 在多数目标任务上 FNR 为 0.00，除情感分析外至多 0.06；**情感分析目标任务上 FNR 高达 0.87**。同一设置下 KAD 的 FNR 在情感分析上达到 0.93，在垃圾短信检测上为 0.53。
- **泛化**：换用不同的检测 LLM 与后端 LLM，效果保持。例如 NeuralExec 对未见过的后端 LLM，FNR 为 0.00（OpenChat、Mistral-7B、Mixtral-8x7B）和 0.01（LLaMA-3.1-8B-Instruct）。
- **效率**：Mistral-7B 检测一次约 1.6 秒，后端查询约 15.3 秒；换成 LLaMA3.2-1B 作检测器，FPR 0.00、FNR 0.01，约 0.7 秒。
- **消融**：轮数 r > 2 后 FPR、FNR 收敛并接近 0；任务集规模约 400 以上表现稳定；α、β 控制 FPR 与 FNR 的权衡，取 1 是合理默认值；内层迭代 > 100、外层 > 300 后表现良好。
- **与鲁棒后端的关系**：论文用 StruQ、SecAlign 同时作检测器和后端做实验，KAD 的 FNR 分别为 0.99 和 0.95，且仍有 5% 和 4% 的逃逸样本攻击成功。作者据此论证：即使后端经过鲁棒训练，检测仍有必要，且需要博弈式训练。

## 贡献与意义

1. 把“检测器会被针对性攻击”这一事实直接放进训练目标，用交替优化让检测器见到最强的自适应样本，而不是只在固定攻击上评估。
2. 训练成本低（单卡数小时），检测器可以换成 1B 级小模型，部署开销可控。
3. 评估同时报告 FPR 和 FNR，并与高误报的基线（如 PromptGuard）区分开。获 S&P 2025 Distinguished Paper。

## 局限

- **“检测”型防御的边界**：它只回答“这段数据是否被污染”，不是让模型本身不受注入影响，也不提供类似 [19 CaMeL](19-camel-defeating-prompt-injections.md) 的可证明保证。漏报时没有第二道防线；误报时会拒绝正常请求。
- **自适应攻击只覆盖作者定义的那一类**：评估的自适应攻击是论文威胁模型下的白盒 GCG 类优化，攻击者不知道密钥。论文把更强的自适应攻击列为未来工作。
- **同类任务时效果差**：当注入任务与目标任务同类型时，注入数据更像对抗样本，检测变难；情感分析目标任务上 FNR 达 0.87 就是例证。
- **本身带指令的数据**：数据中合法包含指令（如聊天机器人里用户自己的指令）可能被误报。
- **与 14 号的对照**：[14 The Attacker Moves Second](14-attacker-moves-second-usenix26.md) 用自适应攻击打破了 12 种已发表防御，其中包括 PromptGuard、Protect AI Detector 等过滤类检测器，多数 ASR 超过 90%。两者结论并不直接矛盾：DataSentinel 在训练阶段就纳入了自适应攻击者，且在论文自己的白盒攻击下表现良好；但 14 号所用的攻击（含搜索类方法）并非针对 DataSentinel 设计，本文也没有 DataSentinel 在 14 号攻击下的数据。因此“对自己设定的自适应攻击鲁棒”不等于“对任意自适应攻击鲁棒”，要判断这一点仍需第三方用新攻击检验。
- 本文未读到论文末尾约 3.5 万字符（疑似附录），其中可能还有未被引用的限制说明。

## 对研究者的启示

- 评估检测类防御时，要把攻击者对检测器本身的白盒优化纳入威胁模型，并同时报告 FPR 与 FNR，避免“全判污染”式的虚假高召回。
- 检测适合作为多层防御的一层，与系统级设计（[19](19-camel-defeating-prompt-injections.md)）和基准评估（[15 AgentDojo](15-agentdojo-neurips24.md)）搭配使用。
- 值得做的后续工作：用 14 号的搜索类、强化学习类攻击检验 DataSentinel，以及检验同类型任务注入下的失败模式。

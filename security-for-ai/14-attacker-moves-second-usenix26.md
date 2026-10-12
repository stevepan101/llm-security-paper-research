# The Attacker Moves Second: Stronger Adaptive Attacks Bypass Defenses Against LLM Jailbreaks and Prompt Injections

| 项目 | 内容 |
|---|---|
| 作者 | Milad Nasr, Nicholas Carlini（Anthropic）, Chawin Sitawarin, Jamie Hayes, Juliette Pluto, Shuang Song, Abhradeep Guha Thakurta（Google DeepMind）, Sander Schulhoff, Michael Ilie（HackAPrompt）, Kai Yuanqing Xiao（OpenAI）, Florian Tramèr（ETH Zurich）等 |
| 会议 | USENIX Security 2026 |
| 原文 | [arXiv:2510.09023](https://arxiv.org/abs/2510.09023)、[USENIX 页面](https://www.usenix.org/conference/usenixsecurity26/presentation/nasr) |

## 一句话总结

三大实验室（Anthropic、Google DeepMind、OpenAI）和 ETH 的研究者联合，用**自适应攻击**打破了 12 种已发表的越狱和提示注入防御。这些防御原本报告的攻击成功率接近 0，被攻破后大多超过 90%。

## 背景与问题

对抗样本领域早有教训（Carlini 等人 2018 年就用同样思路攻破过一批对抗鲁棒性防御）：**用固定攻击集评估防御是不可靠的**。LLM 安全领域在重复这个错误，许多防御论文只用静态越狱字符串，或者用并非针对该防御设计的弱优化器来测试。

## 方法

把四类通用优化方法改造成针对具体防御的自适应攻击，并投入大量计算：
1. **梯度下降**（例如 GCG 类方法）；
2. **强化学习**：训练攻击模型；
3. **随机搜索 / 进化搜索**：LLM 生成候选，再根据反馈迭代；
4. **人类红队**：一场有 500 多人参加、奖金 2 万美元的比赛。

## 被攻破的 12 种防御

| 类别 | 防御 | 攻击 | 攻击成功率 |
|---|---|---|---|
| 提示类 | Spotlighting | 搜索 | >95%（AgentDojo） |
| 提示类 | Prompt Sandwiching | 搜索 | >95%（AgentDojo） |
| 提示类 | RPO | RL / 梯度 | 98% / 96%（HarmBench） |
| 训练类 | Circuit Breakers | RL | 100%（HarmBench） |
| 训练类 | StruQ | RL | 所有测试案例都成功 |
| 训练类 | MetaSecAlign | 搜索 | 96%（AgentDojo） |
| 过滤类 | Protect AI Detector | 搜索 | >90% |
| 过滤类 | PromptGuard | 搜索 | >90% |
| 过滤类 | PIGuard | 搜索 | 71% |
| 过滤类 | Model Armor | 搜索 | >90% |
| 秘密知识类 | Data Sentinel | RL | 重定向任务准确率 >80% |
| 秘密知识类 | MELON | 搜索 | 76%（不知道防御细节）/ 95%（知道） |

注：每种防御只配了作者认为最有效的攻击，不同防御之间的数字不可直接比较。

### 人类红队
- 40 道挑战，覆盖多种防御、模型和 AgentDojo 任务，**每一道都被攻破**；
- 在选定的子集上，自动化搜索攻击的成功率为 69%，而人类合计为 100%。

## 核心结论与建议

1. **静态评估具有误导性**：固定的小攻击集容易被过拟合，而真实攻击总是分布外的。
2. **自动化自适应攻击有效，但还不够**：通过评估是必要条件而非充分条件，经验评估最多只能说明“没能证明防御被攻破”。
3. **人类红队仍然最强**：防御作者应该亲自手动攻击自己的防御，并开放代码和交互接口，方便他人检验。
4. **基于模型的自动评分器不可靠**：评估用的安全分类器本身可能被欺骗或被 reward hacking。

## 贡献与意义

1. 很可能成为 **LLM 防御评估的“标准参照”**：以后的防御论文需要回应自适应攻击。
2. 三大实验室联合署名，表明业界在“现有防御都不够”这一点上有共识。
3. 间接支持了**系统级设计**（例如 [19 CaMeL](19-camel-defeating-prompt-injections.md)）而非模型级防御的路线：后者是在优化问题内部做防御，总能被更强的优化器打破。

## 局限

- 每种防御只用一种攻击，覆盖不完整。
- 计算开销大，普通研究者难以复现全部实验。
- 文章说明“现有防御都能被攻破”，但没有给出正面的防御方案。

## 对研究者的启示

- 写防御论文时必须包含**自适应攻击评估**，最好开放在线 demo 供外界攻击。
- 不要用单一的 LLM 评判器作为唯一的评估标准。

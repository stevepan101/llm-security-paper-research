# LLM 安全能否进入“工业化早期”？——从东方游戏重建看越狱攻击、智能体攻击与护栏防御

| 项目 | 内容 |
|---|---|
| 类型 | 专题分析（不是单篇论文精读） |
| 起点 | N0zoM1z0，[《逆向工程的工业革命》](https://rea.tools/zh-CN/blog/touhou-reconstruction/)，REA 博客，2026-10-10 |
| 调研截止 | 2026-10-13 |
| 相关精读 | [12](../security-for-ai/12-shallow-safety-alignment-iclr25.md)、[14](../security-for-ai/14-attacker-moves-second-usenix26.md)、[15](../security-for-ai/15-agentdojo-neurips24.md)、[18](../security-for-ai/18-chasing-shadows-llm-security-pitfalls.md)、[19](../security-for-ai/19-camel-defeating-prompt-injections.md)、[20](../security-for-ai/20-constitutional-classifiers.md)、[22](../security-for-ai/22-agenticred-evolving-red-teaming-systems.md)；[02](../ai-for-security/02-darpa-aixcc-final.md)、[07](../ai-for-security/07-xbow-hackerone.md)、[08](../ai-for-security/08-anthropic-gtg-1002-ai-espionage.md) |

> **阅读说明**：事实性内容都附有来源，其中只能从二手报道得到的数字已经注明。标为“**推断**”的段落是本文基于这些事实做出的判断，可以商榷。

---

## 结论

**可以，但只限于一部分领域，而且安全领域的工业化形态必须和逆向不同。**

| 子领域 | 现状判断 | 一句话理由 |
|---|---|---|
| **智能体攻击（提示注入、工具滥用）** | **已进入工业化早期** | 危害可以定义成“agent 做了什么”，因此能用环境状态检查来判定。前沿实验室已经形成“RL 自动攻击者 → 对抗训练 → 持续回归”的闭环，众测规模达到百万次攻击，CWE、CVE、赏金和 OWASP 等制度也已配套。 |
| **越狱攻击** | **产能已工业化，计量仍是手工** | 攻击生成已经自动化、可演化、可累积，成功率可以按算力购买（幂律）。但判定“是否真的有害”的评判器在分布偏移下接近随机，而自动攻击者恰好以评判器打分为优化目标。 |
| **护栏与防御** | **分成两条路** | 模型内防御无法靠测试证明鲁棒（“攻击者后手”），能工业化的只是“补丁流水线”。系统级防御（信息流控制、权限策略）把安全性质搬到确定性代码上，重新获得可检验的校验基准，是防御侧最可能工业化的方向。 |

逆向能工业化，是因为目标静止、存在近乎完美的 ground truth、工作会收敛、知识可以公开。安全领域这四条都不完全成立。因此安全领域的工业化单元不应是“把一个项目做完”（例如 TH095 的 697 个函数全部还原），而应是**持续运行的攻防流水线**，参照物是 OSS-Fuzz，里程碑是**“失败率—攻击预算”曲线**和**从发现到修复的周期**。

**最需要推进的能力，按优先级排列**：①校验基准工程，包括对校验基准本身的测试；②持续自适应评估基础设施；③发现的去重、最小化与根因分析；④可累积、可重放、分级共享的攻防知识库；⑤闭环修复与补丁验证；⑥可验证的系统级防御；⑦给 agent 用的分析工具；⑧度量规范与制度配套。

---

## 推理路线

1. **定义**：从博客中提取“工业化”的操作性定义，而不是停留在比喻上（第一节）。
2. **前提**：找出逆向工程能够工业化的结构性前提（第二节）。
3. **检验**：逐一检查这些前提在越狱攻击、智能体攻击、防御三个子领域是否成立，用 2024–2026 年的证据打分（第三节）。
4. **修正**：根据安全领域和逆向的根本差异，修正“工业化”在安全领域应有的形态（第四节）。
5. **反推**：从差距反推需要推进的能力，给出可衡量的里程碑和选题（第五、六节），最后讨论反方观点（第七节）。

---

## 一、博客里的“工业化”指什么

### 1.1 事实：三个项目的时间线

| 项目 | 平台 | 关键里程碑（博客对照公开 GitHub 历史核实） | 用时 |
|---|---|---|---|
| TH08《东方永夜抄》 | Windows | 接续 GensokyoClub 的公开源码。8-13 开始独立续作；8-19 台账中已识别的 1,107 个函数全部有源码；8-24 可玩的 Linux 移植版；8-26 Web 版；8-30 原生 Linux 64 位版 | 约 11 天到可玩移植版 |
| TH095《东方文花帖》 | Windows | 8-29 建仓（台账中 0 个函数）；9-7 全部 697 个函数有源码；9-8 其中 696 个通过精确对比；9-9 整程序链接；9-10 i386 版可玩 | 约 12 天从零到可玩 |
| TH04《东方幻想乡》 | PC-98 DOS（4 个程序协作的 16 位环境） | DOS 重建版可运行，作者手工通关 Normal 路线；64 位移植进行中 | — |

### 1.2 博客中工业化的九个要素

| # | 要素 | 博客中的体现 |
|---|---|---|
| E1 | **自主性** | “明确目标和验收标准，再让它决定下一步尝试什么。”对比失败后，助手会自己转去查调用方、写诊断程序。 |
| E2 | **校验基准（oracle）** | 用原编译器重新编译后做精确对比，再加运行时检查。作者特别强调：方法可以迁移，“但每个领域都需要先明确：什么可以用可靠的基准来验证”。 |
| E3 | **校验基准的元测试** | 比较工具只比较指令字节，没有检查被引用地址里的浮点值，导致源码写的 `0.0`（原版是 `128.0`）也通过了“精确匹配”。修复后审计了 1,548 处浮点常量引用，又在 5 个已验收函数中发现 12 处错误。此后用应当失败的错误值测试工具，并重查曾通过旧检查的结果。“校验基准本身也需要重建。” |
| E4 | **外化的工作记忆** | 代码仓库和 Git 是工作记忆，推理理由和代码一起保存；对话有长度上限，必须让下一次会话能接着做。 |
| E5 | **经验复利** | TH08 → TH095 → TH04；“经验只记在我脑子里，我在场时它才有用”，经验变成可运行的检查后才能离开个人继续发挥作用。 |
| E6 | **分层流水线与双基准** | 精确还原 → 在原平台构建并游玩 → 语义重建 → 现代平台移植。精确对比和可玩构建是两套基准，能发现不同类型的错误（如本应共享的状态被各自持有一份）。 |
| E7 | **工具访问** | REA 让助手直接使用分析工具，重建项目提供编译器和对照检查。 |
| E8 | **经济学** | 速度改变了“是否值得开始一个项目”的判断。 |
| E9 | **社会与制度** | GensokyoClub 不接受主要由 AI 生成的 PR，并公开表达异议；涉及署名、贡献评价和维护者需要了解的东西。 |

### 1.3 提炼：工业化 = 计量基础设施 + 可累积的流程知识

**推断**：博客说的工业化不是“AI 把活全干了”，而是三件事同时发生：

1. **内循环交给 agent**：提出假设、做实验、根据结果修正，不再需要人逐步指挥。
2. **人的工作上移**：作者自己说，机器改变了技艺发挥作用的位置，“但仍然需要人设计流程、识别错误产出”。人负责定目标和验收标准、维护量具、判断证据是否足以支持里程碑。
3. **知识以可执行的形式沉淀**：经验变成别人和其他会话都能运行的检查，跨会话、跨项目复用。

博客用博尔顿和瓦特 1796 年引入的蒸汽机示功器作比喻：它能画出活塞行程中的压力变化，让人看清机器内部在做什么。这个比喻的重点是**测量仪器先于工业化**。“早期”的含义也写得很清楚：“许多基础设施还不成熟。助手推进工作的速度，可能超过原有检查的承受能力，所以流程也要一起发展。”

据此，本文用以下标准判断一个领域是否处于“工业化早期”：

- (a) 相当比例的工作可以用**可靠的校验基准**判定；
- (b) agent 能**自主推进**主要的内循环；
- (c) 经验以**可执行的形式**在项目或团队之间累积；
- (d) 已经出现**产能的阶跃**；
- (e) **制度和产业组织**开始调整；
- (f) 同时，量具和流程**落后于产能**，这正是“早期”的标志。

---

## 二、逆向为什么适合工业化，LLM 安全又有什么不同

### 2.1 五个结构性质的对比

| 结构性质 | 游戏逆向重建 | LLM 安全 |
|---|---|---|
| 目标是否静止 | 原始二进制不会变，也不会反击 | 模型频繁更新（[18](../security-for-ai/18-chasing-shadows-llm-security-pitfalls.md)：同一个“GPT-4”的三个快照准确率相差 11 个百分点以上）；攻击者和防御者互相适应（[14](../security-for-ai/14-attacker-moves-second-usenix26.md)） |
| 是否有 ground truth | 原编译器加字节级对比，接近可判定 | **取决于子领域**：agent 的动作可判定；“内容是否有害”依赖语义判断；“防御是否鲁棒”无法通过测试证明 |
| 是否收敛 | 函数数量有限，有“完成”状态 | 没有完成状态。微软红队测试 100 多个生成式 AI 产品后总结的第八条教训是：“构建安全可靠的 AI 系统的工作永远不会完成”；OpenAI 也表示提示注入不会消失 |
| 是否可分解 | 以函数为单元，局部对比再加整程序检查 | 风险类别 × 攻击策略 × 模态 × 对话轮次 × 工具，组合空间巨大，“覆盖率”难以定义 |
| 知识能否公开 | Factory 仓库公开，方法跨游戏迁移 | 双用途：可用的攻击载荷一旦公开就会扩散 |

**推断**：前两条决定“能不能工业化”，后三条决定“工业化长什么样”。

### 2.2 更合适的参照物是 OSS-Fuzz，而不是一次性的重建项目

安全领域早就有一个工业化的先例：模糊测试。截至 2025 年 5 月，OSS-Fuzz 已帮助 1,000 个项目发现并修复 13,000 多个漏洞和 50,000 多个 bug。它的要素和博客几乎一一对应：

| OSS-Fuzz 的要素 | 对应博客中的要素 |
|---|---|
| sanitizer 和崩溃作为可判定的 oracle | E2 校验基准 |
| 7×24 持续运行，进入开发流程 | E1 自主性、E8 经济学 |
| 语料库、回归测试集 | E4 工作记忆、E5 经验复利 |
| 崩溃去重、最小化、定位引入问题的提交 | E3 对检查结果本身做质量控制 |

本仓库收录的 AI 挖洞工作也遵循同一模式：AIxCC 的 CRS 是“LLM 加模糊测试和程序分析”（[02](../ai-for-security/02-darpa-aixcc-final.md)），XBOW 用确定性验证器消除误报（[07](../ai-for-security/07-xbow-hackerone.md)）。

**推断**：安全领域工业化的基本单元，应当是“持续运行的攻防流水线”，里程碑不是“N/N 个函数通过”，而是“给定攻击预算下的失败率曲线”和“从发现到修复的周期”。

---

## 三、分领域评估

### 3.1 越狱攻击：产能已工业化，计量仍是手工

#### 证据一：攻击生成已经自动化，可以演化，也可以累积

| 发展阶段 | 代表工作 | 对应博客的要素 |
|---|---|---|
| 自动优化提示 | GCG、PAIR、TAP | E1 自主内循环 |
| 累积策略 | **AutoDAN-Turbo**（ICLR 2025 Spotlight）：终身学习的策略库，从零开始发现策略；在 GPT-4-1106-turbo 上 ASR 为 88.5%，加入人工设计的策略后为 93.4% | E4/E5 工作记忆与经验复利 |
| 追求多样性 | **Rainbow Teaming**（NeurIPS 2024）：用 MAP-Elites 存档，按风险类别、攻击风格等维度组织提示，所有测试模型的 ASR 都超过 90%；用生成的数据做微调能提升安全性 | E6 覆盖与分层 |
| 演化攻击流程本身 | **AgenticRed**（2026-01）：GPT-5 作为元智能体演化整套攻击系统，HarmBench ASR 96–100%，迁移到 GPT-5.1 为 100%（见 [22](../security-for-ai/22-agenticred-evolving-red-teaming-systems.md)） | 博客中“一项工具的改进，可以帮助之后所有需要它的函数” |
| 只用 1 比特反馈的黑盒攻击 | **Boundary Point Jailbreaking**（BPJ，UK AISI 等，2026-02，ICML 2026）：每次查询只用“是否被分类器标记”这 1 比特信息；作者称这是第一个能全自动生成通用越狱、攻破 Constitutional Classifiers 的攻击，也是第一个不需要人工种子就能攻破 GPT-5 输入分类器的自动攻击 | **从手工转向机器的转折点**：此前 Constitutional Classifiers 经受了 3,700 多小时人类红队，只出现一次完全成功的人工攻击 |

#### 证据二：攻击成本变得可预测

- **Best-of-N 越狱**：ASR 随采样次数 N 呈幂律变化（−log ASR = a·N^(−b)），可以用少 10 倍的样本外推攻击效果。10,000 次增强采样在 GPT-4o 上达到 89%，在 Claude 3.5 Sonnet 上达到 78%；与 many-shot 组合后，在 Claude 3.5 Sonnet 上达到相同 ASR 快 28 倍。
- **FAR AI，Scaling Trends in Language Model Robustness**（ICML 2025）：攻击成功率随攻击算力平滑上升；在研究的所有模型规模上进攻都占优（攻防算力斜率小于 1）；对抗训练在算力效率上比单纯扩大模型高出几个数量级。

**推断**：当成功率可以“按算力购买”，攻击就成了可以计价的工业品。这就是博客里“速度改变是否启动项目”在安全领域的对应：过去需要专家花几天时间做的通用越狱，现在变成了一笔可以做预算的算力开支。

#### 证据三：越狱输出越来越“好用”

- **越狱税**（The Jailbreak Tax，ICML 2025）：在有标准答案的良性任务上测量越狱输出的效用，数学任务中越狱后的准确率最多下降 92%。
- **后续工作**（Jailbroken Frontier Models Retain Their Capabilities，2026-04）：测试 28 种越狱、5 个基准，Haiku 4.5 越狱后平均损失 33.1%，Opus 4.6（最大思考预算）只损失 7.7%；BPJ 几乎不造成能力损失。作者的结论是，前沿模型的安全论证不应依赖“越狱会显著降低模型能力”这一假设。

#### 差距：评判器——安全领域的“`0.0` 也能精确匹配”

- **A Coin Flip for Safety**（2026，ICML 2026 poster）：用 6,642 条人工核验标签审计 LLM 评判器，发现在红队测试的分布偏移（攻击改变了输出风格、目标模型不同、不同场景的语义模糊程度不同）下，评判器的表现经常接近随机，与以往报告的高人类一致率形成反差；**许多攻击看起来成功，是因为利用了评判器的缺陷，而不是真的引出了有害内容**。二手汇总称，在攻击偏移下 AUROC 最低只有 0.48，集成多个评判器也无济于事，因为它们共享系统性的失效模式。作者提出了 ReliableBench 和 JudgeStressTest。
- **StrongREJECT**：现有的自动评估方法高估了越狱成功率。
- **AgenticRed** 使用的 HarmBench 分类器，在 200 条人工核验中 F1 为 0.92，但特异度只有 0.75（[22](../security-for-ai/22-agenticred-evolving-red-teaming-systems.md)）。
- **Chasing Shadows**（NDSS 2026）：审查的 72 篇论文中，73.6% 没有写明确切的模型版本（[18](../security-for-ai/18-chasing-shadows-llm-security-pitfalls.md)），这些历史结果连重放都做不到。

> **关键推理（本文最重要的一点）**
>
> 在博客里，比较工具的漏洞是**被动暴露**的：助手没有刻意寻找让检查通过的捷径，所以漏洞只是潜伏了一段时间，影响了 5 个函数中的 12 处引用。
>
> 而在自动化红队中，攻击系统**直接以评判器的打分为优化目标**（ASR 就是适应度函数）。评判器的每个盲点都会被优化器**主动搜索、放大，并固化进策略库**：
>
> - 逆向：校验器有漏洞 → 少量错误结果；
> - 红队：评判器有漏洞 → 优化器系统性地产出“评判器漏洞利用”，并被当成“攻击成功”报告出来。
>
> 所以“校验基准本身也要测试”在安全领域**不是最佳实践，而是工业化的前提**。博客修复比较工具后审计全部 1,548 处引用、重查已验收结果，在安全领域对应的动作是：评判器发现系统性盲点或更换版本时，**重新判定所有依赖它的历史 ASR**（论文、排行榜、内部回归测试）。目前几乎没有这样的机制。

**结论**：越狱攻击处于“产能工业化、计量手工”的阶段。要进入真正的工业化早期，关键在计量，不在攻击生成。

---

### 3.2 智能体攻击：最接近工业化早期

#### 原因：动作可以被判定

- **AgentDojo** 用环境状态的形式化检查判定任务是否完成、攻击是否成功，而不是靠 LLM 评判（[15](../security-for-ai/15-agentdojo-neurips24.md)）。这就是逆向中“精确对比”的对应物。
- **AIRTBench**（Dreadnode，2025-06）：70 个黑盒 CTF 风格的 AI 安全挑战，以 Crucible API 验证过的 flag 作为成功标准；Claude 3.7 Sonnet 解出 43 个（61%）。
- 数据外泄可以用蜜标（canary）判定，越权操作可以用沙箱中观察到的副作用判定。

**推断**：只要把危害定义成“agent **做了**什么”，而不是“模型**说了**什么”，校验基准就从语义判断变成了状态检查。这是智能体攻击领先于越狱攻击的根本原因。

#### 证据：自动攻击者已经进入生产闭环

- **OpenAI**（2025-12-22，ChatGPT Atlas）：用强化学习端到端训练一个 LLM 攻击者，在模拟器里对 agent 做反事实 rollout，利用 agent 的推理和行动轨迹改进注入，目标是找出能诱导浏览器 agent 执行多步有害流程的攻击。发现新的攻击类别后，就对 agent 模型做对抗训练；攻击轨迹也用于改进监控、安全指令和系统级防御。OpenAI 不承诺确定性保证。（OpenAI 原文无法直接访问，细节来自其博文的媒体报道）
- **Google DeepMind**（2025-05，《Lessons from Defending Gemini Against Indirect Prompt Injections》）：一套自适应攻击持续针对 Gemini 的过去、当前和未来版本运行；在 8 种防御 × 3 种攻击的 24 个组合中，有 16 个的自适应攻击效果不低于非自适应攻击。经过对抗微调的 Gemini 2.5 与 Gemini 2.0 相比，邮件场景下 TAP 的 ASR 从 99.8% 降到 53.6%，但日历场景只从 100% 降到 94.6%。
- **RL-Hammer**（马里兰大学和 Meta FAIR，2025-10）：用强化学习训练提示注入攻击者，对 GPT-4o 的 ASR 为 98%，对启用指令层级防御的 GPT-5 为 72%，并能绕过多种注入检测器。

**推断**：这正是博客中“自主探索 → 验证 → 修正假设”的循环。“校验基准”换成了模拟器里的状态检查，“代码仓库”换成了攻击轨迹库和对抗训练数据。

#### 证据：众测把产能和数据推到工业量级

| | Gray Swan × UK AISI（2025-03 至 04） | NIST CAISI × UK AISI × Gray Swan（论文 2026-03） |
|---|---|---|
| 规模 | 22 个 agent、44 个场景、约 180 万次攻击、6 万多次策略违规 | 464 名参与者、约 27.2 万次攻击、13 个前沿模型、41 个场景、8,648 次成功 |
| 主要发现 | 多数行为在 10–100 次查询内被攻破；攻击在模型和任务之间迁移性强；鲁棒性与模型规模、能力、推理算力的相关性很弱 | 所有模型都被攻破过，ASR 从 0.5%（Claude Opus 4.5）到 8.5%（Gemini 2.5 Pro）；部分策略能在 41 个行为中的 21 个上迁移；针对更鲁棒模型开发的攻击更容易迁移到较弱模型，反之不成立；计划按季度更新以应对基准饱和 |

#### 证据：制度和产业组织开始调整

- **漏洞分类**：MITRE 的 CWE-1427“用于 LLM 提示的输入未被正确中和”，即提示注入。
- **CVE 与披露**：EchoLeak（CVE-2025-32711，Microsoft 365 Copilot 零点击数据外泄，CVSS 9.3）。Johann Rehberger 的“AI Bug 之月”（2025-08）在一个月内向主流编码 agent 负责任地披露了二十多个漏洞。MCP 生态在 2025–2026 年出现大量 CVE（各统计口径不一）。
- **赏金**：Google AI VRP（2025-10）把“越权操作”（rogue actions）列为最高档，例如通过间接提示注入让 Google Home 开锁，基础奖金最高 2 万美元，加乘后最高约 3 万美元。**越狱和直接提示注入不在范围内**，Google 认为 VRP 不适合处理内容类问题。
  - **推断**：这条范围划分很能说明问题：制度只接纳“有明确安全影响、可以判定”的问题。**可判定性决定了什么能被制度化**。
- **标准**：OWASP Top 10 for Agentic Applications（2025-12）；OWASP Top 10 for LLM Applications 2026（2026-08）；Meta 的 Agents Rule of Two（2025-10）。
- **产业整合**：2025 年起，Protect AI 被 Palo Alto Networks 收购，Prompt Security 被 SentinelOne 收购，CalypsoAI 被 F5 收购，Lakera 被 Check Point 收购，SPLX 被 Zscaler 收购。2026-03，OpenAI 宣布收购 Promptfoo，用于在其 agent 平台中做自动化红队和 agent 工作流安全评估；Promptfoo 已被超过 25% 的财富 500 强企业使用，并承诺继续开源。
  - **推断**：AI 红队和护栏正在从独立产品变成安全平台的标准模块，这是产业组织层面的工业化信号。

#### 差距

- **环境的构建成本高**：AgentDojo 只有 4 个环境、97 个用户任务。每个真实部署都需要一个“数字孪生”环境，才能有状态型的校验基准。
- **隐蔽攻击**：CAISI 论文强调，agent 可以在执行有害动作的同时让用户看到的回复毫无异常，所以校验基准必须检查**动作轨迹**，不能只看最终输出。
- **非二元的危害**：误导性摘要、操纵性话术这类危害，最终还要回到语义判断。
- **新场景不成熟**：跨会话记忆、多 agent 协作、工具供应链（例如 MCP 的 rug pull：用户批准后再修改工具描述）等场景，环境和校验基准都还不完善。
- **基准饱和**：需要按季度更新。

**结论**：前沿实验室内部已经形成“自动攻击者 → 对抗训练或系统修复 → 持续回归”的闭环，处在工业化早期。但学术界和中小企业的基础设施仍然偏手工。

---

### 3.3 护栏与防御：两条路，前景不同

#### 路径 A：模型内防御（安全训练、分类器、检测器）——不存在“鲁棒”的校验基准

- **The Attacker Moves Second**（USENIX Security 2026）：12 种已发表防御被自适应攻击攻破，大多 ASR 超过 90%；人类红队的 40 道挑战全部被攻破；“通过评估是必要条件而非充分条件”（[14](../security-for-ai/14-attacker-moves-second-usenix26.md)）。
- **BPJ** 攻破了 Constitutional Classifiers（见 3.1）。
- **AutoAdvExBench**（ICML 2025）：测试 LLM agent 能否自主攻破对抗样本防御。最强的 agent 组合攻破了 87% 的 CTF 式防御，但只攻破了 37% 的真实论文防御。“自动攻击防御”本身也在走向工业化，但面对真实研究代码仍然困难。

**推断**：对于模型内防御，经验测试只能给出“在某个攻击预算下没被攻破”这样的下界，不存在逆向中“通过即正确”的校验基准。所以这条路线**不可能以“证明鲁棒”的方式工业化**。

**但“补丁生产”可以工业化**：

- **Rapid Response**（Anthropic 等，2024-11）：每类越狱只观察 1 个样本，自动扩增出相似的越狱后微调输入分类器，分布内 ASR 降低 240 倍以上，分布外降低 15 倍以上；扩增模型的质量和扩增数量是关键。
- **Constitutional Classifiers 管线**：宪法 → 合成数据 → 分类器 → 红队与赏金 → 更新宪法。新一代 CC++（2026-01）的计算开销约 1%，误拒率 0.05%（[20](../security-for-ai/20-constitutional-classifiers.md)）。Anthropic 从 2025-05 起通过 HackerOne 对通用越狱提供最高 2.5 万美元的赏金。
- **gpt-oss-safeguard**（OpenAI，2025-10）：推理时读取书面安全政策，修改政策文本就能改规则，不需要重新训练分类器（Apache 2.0，120b 和 20b 两个尺寸）。**推断**：这是“政策即代码”，让验收标准可以像配置一样迭代。
- **用推理算力换鲁棒性**（OpenAI，2025-01）：o1 类模型思考得越久，许多攻击的成功率趋于零，但存在重要的例外。
- **BPJ 的防御启示**：单次交互的判定很难防住这种攻击，需要批量级监控，因为优化过程会触发大量标记。**推断**：防御会从“单点判定”走向“流量级、账户级检测”，形态更像反欺诈和反垃圾邮件产业。

#### 路径 B：系统级防御——把防御搬回有校验基准的领域

| 工作 | 机制 | 结果 |
|---|---|---|
| CaMeL（Google DeepMind，2025-03） | 控制流与数据流分离，加能力标签和安全策略 | AgentDojo 上成功攻击数为 0；任务完成率 77%（无防御时 84%）；token 开销约 2.7–2.8 倍（[19](../security-for-ai/19-camel-defeating-prompt-injections.md)） |
| FIDES（Microsoft） | 信息流控制标签，确定性地执行策略 | 2026-05 作为实验特性进入 Microsoft Agent Framework |
| Progent | 用于工具权限控制的 DSL | AgentDojo ASR 从 41.2% 降到 2.2%；在 ASB 上用手工策略可证明地降到 0% |
| 设计模式（Beurer-Kellner 等，2025-06） | 6 种隔离不可信数据与控制流的模式，如 plan-then-execute | 架构层面的指南 |
| Rule of Two / 致命三要素 | 一个会话中不要同时具备“处理不可信输入”“访问敏感数据或系统”“改变状态或对外通信”三项 | 架构约束 |

> **关键推理**
>
> 这条路线的意义不仅是“更安全”，而是**把安全性质从模型的统计行为转移到确定性代码上**。“控制流是否在看到不可信数据之前就已确定”“带不可信标签的值是否流入了发邮件的收件人参数”，这类问题都可以用单元测试、模糊测试和形式化验证来检验，从而重新获得逆向中“精确对比”级别的校验基准。这和博客的那句话完全对应：**每个领域都需要先明确：什么可以用可靠的基准来验证。**

这条路线的差距：编写策略的负担、效用损失、侧信道、用户确认疲劳、类似 ROP 的组合攻击，以及解释器尚未经过形式化验证（[19](../security-for-ai/19-camel-defeating-prompt-injections.md)）。

**结论**：防御的“补丁流水线”和“系统级强制”可以进入工业化早期；“证明模型本身鲁棒”短期内做不到。

---

### 3.4 汇总打分

| 要素 | 逆向（博客） | 越狱攻击 | 智能体攻击 | 模型内防御 | 系统级防御 |
|---|---|---|---|---|---|
| E1 agent 自主推进内循环 | ● | ●（PAIR 到 AgenticRed） | ●（RL 攻击者） | ◐（扩增和重训可以自动化） | ◐（策略生成仍主要靠人） |
| E2 可靠的校验基准 | ●（字节对比） | ○（语义评判器） | ◐（状态检查，但覆盖有限） | ○（鲁棒性测不出来） | ◐→●（策略执行可以验证） |
| E3 校验基准的元测试 | ●（负例测试、全量重审） | ○（刚起步，如 JudgeStressTest） | ◐ | ○ | ◐ |
| E4 外化的工作记忆 | ● | ◐（策略库、存档） | ◐（攻击轨迹库） | ◐ | ◐ |
| E5 跨项目经验复利 | ● | ◐（迁移性强，但会衰减） | ◐（需要季度更新） | ◐（补丁可以复用） | ◐ |
| E6 分层流水线与双基准 | ● | ◐（ASR 加越狱税） | ●（效用加安全） | ◐（拦截率加误拒率） | ◐ |
| E7 分析工具访问 | ●（REA） | ◐（白盒、可解释性） | ◐ | ◐（激活探针） | ● |
| E8 经济学阶跃 | ● | ●（ASR 可以按算力购买） | ● | ◐（CC++ 开销约 1%） | ◐（约 2.7 倍 token） |
| E9 制度调整 | ◐（社区争议） | ◐（赏金、国家标准题库） | ●（CWE、CVE、VRP、OWASP） | ◐ | ◐ |

● = 已具备；◐ = 部分具备；○ = 基本缺失（本文作者的判断）

---

## 四、安全领域的工业化需要做的五个修正

### 修正 1：量具必须能抵抗对抗

评判器会被优化器主动攻击（3.1），集成多个评判器也无效。**能写成可执行检查的，就不要交给 LLM 评判**。对于必须做语义判断的部分，要像对待被攻击的系统一样对待评判器：做负例测试、变异测试、分布偏移测试，并把评判器的失效模式当作漏洞来修复。

### 修正 2：里程碑从“完成度”改为“成本曲线”

示功器画的是“压力—行程”曲线，安全领域需要的是“**失败率—攻击预算**”曲线。BoN 的幂律、FAR AI 的攻防算力斜率、ART 基准的“10–100 次查询内被攻破”，都是这条曲线的雏形。

**推断**：发布报告应给出“在 X 次查询或 Y 美元算力的自适应攻击下，ASR 不超过 Z”，而不是单点 ASR。

### 修正 3：回归测试集会衰减，必须版本化、可重放

模型版本变化、攻击被修补后失效、基准饱和或被污染，都会让回归测试集失效。需要固定模型版本、评判器版本、随机种子和攻击预算（[18](../security-for-ai/18-chasing-shadows-llm-security-pitfalls.md) 的 R1），并持续补充新攻击。

### 修正 4：验收标准本身是一种政策，需要写成可执行的规格

逆向的验收标准由原始二进制决定，安全的验收标准（什么算有害、什么应当拒绝）是政策选择，而且因部署场景而异。可执行规格的例子：Constitutional Classifiers 的宪法、gpt-oss-safeguard 读取的书面政策，以及国家标准。

**GB/T 45654—2025《网络安全技术 生成式人工智能服务安全基本要求》**（2025-04-25 发布，2025-11-01 实施）把验收标准写成了量化指标：

| 要求 | 内容 |
|---|---|
| 生成内容测试题库 | 不少于 2,000 题，覆盖附录 A 的全部 31 类安全风险；A.1、A.2 中每类不少于 50 题，其余每类不少于 20 题；至少每月更新 |
| 应拒答测试题库 | 不少于 500 题，至少覆盖 A.1、A.2 的 17 类风险，每类不少于 20 题 |
| 非拒答测试题库 | 不少于 500 题；至少每月更新 |
| 生成内容合格率 | 人工抽检和技术抽检各不少于 1,000 题，合格率均不低于 90% |
| 拒答行为 | 从两个题库各抽不少于 300 题人工检测：应拒答题的拒答率不低于 95%，非拒答题的拒答率不超过 5% |

（出处：CSET 对 GB/T 45654—2025 正式版的英译本，附录 B.1.2、B.1.3、B.2.2.2）

**推断**：这套要求已经具备“双基准”结构（应拒答加非拒答，对应博客的两套校验基准），也有“至少每月更新”的机制，是验收标准工业化的实例。短板在于静态题库只能测出下界。按照 [14](../security-for-ai/14-attacker-moves-second-usenix26.md) 的结论，下一步应当把“自适应攻击预算”和“成本曲线”写进验收方法。

### 修正 5：知识复利需要分级共享

Factory 仓库可以全部公开，攻击知识不行。现有的做法包括：

- UK AISI 对 BPJ 走了负责任披露流程；
- CAISI 会接收竞赛中参与者的攻击策略数据；
- CAISI 论文只公开了 95 个**不能迁移到闭源模型**的 Qwen 攻击样本；
- 美国《AI 行动计划》（2025-07）提出由 DHS 牵头建立 AI-ISAC，用于共享 AI 安全威胁情报（尚未见到实施细节）。

### 社会层面的摩擦：换了形式，但会出现

博客中的摩擦是 GensokyoClub 不接受主要由 AI 生成的 PR。安全领域的对应例子是：curl 于 2026 年 1 月底终止了运行多年的 HackerOne 赏金计划，原因是大量低质量（常由 AI 生成）的报告，某一周收到 7 份报告，没有一份是真实漏洞。

**推断**：这正是“助手推进工作的速度可能超过检查的承受能力”在社会层面的体现。解决办法和博客一致：在产出端加验证器（XBOW 用确定性验证器消除误报，见 [07](../ai-for-security/07-xbow-hackerone.md)）、要求可复现的 PoC、自动去重。

---

## 五、需要推进的关键能力（按优先级）

### 能力 1：校验基准工程（计量层，最高优先级）

| 现状 | 要做的事 |
|---|---|
| 智能体场景已有状态检查，越狱场景主要靠 LLM 评判，评判器缺乏元评估 | **可执行的校验基准优先**：agent 场景用状态检查、蜜标、污点追踪、沙箱副作用观测；越狱场景借鉴越狱税的方法，用“有标准答案的代理任务”衡量“有用的违规” |
| | **评判器的元测试**：负例集（应判为失败的安全回复）、变异测试（对已知有害回复做风格、编码、语言扰动，检验判定是否稳定）、攻击分布下的特异度和敏感度（而不只是标准集上的一致率） |
| | **评判器版本化和“召回”**：一旦发现盲点，自动重判所有依赖它的历史结果（对应博客中 1,548 处浮点引用的审计） |
| | **双基准**：安全 oracle 加效用或误拒 oracle（AgentDojo 的攻击下效用、国家标准的非拒答题库） |

**里程碑**：论文和排行榜普遍报告评判器在攻击分布下的元评估结果；排行榜支持更换评判器后重判。

### 能力 2：持续自适应评估基础设施（LLM 安全的 OSS-Fuzz）

- **标准化的被测对象适配器和沙箱环境**：Inspect、AgentDojo、Crucible 等。
- **可插拔的攻击引擎库**：搜索（TAP、PAIR）、强化学习（RL-Hammer、Atlas 攻击者）、演化（AgenticRed）、质量多样性（Rainbow Teaming）、1 比特黑盒（BPJ），并统一记录攻击预算。
- **默认报告成本曲线**：ASR 随查询数或算力的变化（可以参照 BoN 做幂律拟合和外推）。
- **低成本构建 agent 环境**：例如从工具或 MCP 服务的规格自动生成 AgentDojo 式的任务和状态检查。

**里程碑**：模型发布时附带“自适应攻击预算—ASR”曲线；评估环境可以从规格自动生成。

### 能力 3：发现的去重、最小化与根因分析

OSS-Fuzz 能工业化，一个容易被忽略的原因是它会对崩溃做去重、最小化，并定位引入问题的提交，否则产出会淹没维护者。自动红队一天能产出成千上万条“成功攻击”，但：

- **去重**：哪些是同一个根因？
- **最小化**：触发失败的最小提示是什么？
- **根因**：浅层对齐（[12](../security-for-ai/12-shallow-safety-alignment-iclr25.md)）？指令层级失效？评判器缺陷？

在本次检索中，**没有找到专门研究越狱或注入发现的去重和根因聚类的同行评审工作**（XBOW 在 Web 漏洞上公开过去重的做法）。这是一个明确的研究空白。

**里程碑**：红队报告的单位从“N 条成功提示”变成“M 个去重后的根因”，每个根因附最小复现样例和机理证据。

### 能力 4：可累积、可重放、分级共享的攻防知识库

- **形式**：策略库（AutoDAN-Turbo）、质量多样性存档（Rainbow Teaming）、成功与失败记忆（AgenticRed）、版本化的回归测试集。
- **每条发现附证据链**：为什么成功、在哪些模型版本上复现过，能做的话附上可解释性证据（例如 Anthropic 在《On the Biology of a Large Language Model》中用归因图分析越狱案例）。
- **索引**：用 OWASP LLM / Agentic Top 10、MITRE ATLAS、CWE-1427 等分类体系建立索引。
- **分级**：公开层（方法和去武器化的机理描述）、受控层（AISI、ISAC）、内部层（可用的攻击载荷）。

### 能力 5：闭环修复与补丁验证

- **修复手段**：快速响应（扩增后更新分类器）、对抗训练（Atlas、Gemini）、系统规则更新。
- **补丁验证**：必须用自适应攻击**重新攻击**，而不是重放旧攻击；[14](../security-for-ai/14-attacker-moves-second-usenix26.md) 说明重放旧攻击会严重高估效果。
- **监控侧**：用轻量探针做流量初筛（CC++）；用批量级、账户级检测发现优化型攻击（BPJ 的启示）。

**里程碑**：公开“发现到修复”的周期和修复后的自适应复测结果。

### 能力 6：可验证的系统级防御

- **推进方向**：信息流控制和能力（CaMeL、FIDES）、权限策略（Progent）、架构约束（Rule of Two）的工程化，以及在 MCP 等协议层面传递安全标签。
- **关键难点**：策略的自动生成与验证（LLM 写策略，形式化工具检查）、解释器的形式化验证、侧信道分析、降低效用损失和用户确认疲劳。
- **为什么优先级高**：这是防御侧**唯一能获得“精确对比”级别校验基准**的地方，可以直接复用传统软件验证的工业体系。

### 能力 7：给 agent 用的分析工具（安全领域的 REA）

博客中 REA 的作用，是让助手直接调用分析工具，顺着调用方继续追查。安全领域的对应物：

- 白盒梯度和 logprob（授权时）、激活探针、归因图、轨迹检索、环境重放；
- **已有的例子**：Anthropic 的审计 agent（2025-07）中，带可解释性工具的调查 agent 在审计游戏里聚合多次调查后胜率 42%，评估 agent 生成的评测中 88% 测到了想测的东西，广度优先红队 agent 发现了 10 个植入行为中的 7 个；开源工具 Petri（111 条种子指令测试 14 个前沿模型）和 Bloom（为 16 个模型的 4 种行为生成评测）。

### 能力 8：度量规范与制度配套

- **度量规范**：固定模型版本、评判器版本、随机种子和攻击预算；附“评估卡”说明攻击引擎、预算、评判器的元评估结果和效用指标（落实 [18](../security-for-ai/18-chasing-shadows-llm-security-pitfalls.md) 的建议）。
- **制度配套**：
  - 漏洞定义与评分：CWE-1427、agent 漏洞的 CVE；
  - 赏金范围：Google AI VRP 只接收有明确安全影响的问题，Anthropic 设有模型安全赏金；
  - 监管验收：欧盟 GPAI 行为准则对系统性风险模型要求对抗测试和红队；中国 GB/T 45654—2025 规定了题库和阈值；
  - 信息共享：AI-ISAC 设想；
  - AI 生成报告的质量门槛：curl 的教训。

### 从“早期”走向“成熟”的信号

| 信号 | 现在 | 成熟时 |
|---|---|---|
| 主要指标 | 单点 ASR | “攻击预算—失败率”曲线加修复周期 |
| 评判器 | 一次性在标准集上验证 | 版本化、对抗测试、可召回 |
| 红队产出 | 成功提示的列表 | 去重后的根因，附最小复现和证据 |
| 回归测试 | 静态题库 | 持续补充的自适应攻击池，可重放 |
| 防御保证 | “未被攻破” | 系统级性质经过验证，模型级防御报告成本曲线 |
| 知识共享 | 论文附件或内部私有 | 分级共享体系 |

---

## 六、给研究者的选题建议

1. **评判器模糊测试**：训练一个以“让评判器误判”为目标的攻击者，主动找出评判器的盲点再修补。这是把博客中“故意给校验器喂应当拒绝的错误案例”自动化，可以接着 JudgeStressTest 往下做。
2. **越狱和注入发现的去重、最小化、根因聚类**：如上文所述，是公开研究中的空白。
3. **成本曲线的标准化与外推**：把 BoN 的幂律外推推广到 agent 场景和多轮攻击，研究少量预算下的测量能否可靠地预测大预算下的 ASR。
4. **自动构建带状态检查的 agent 测试环境**：降低智能体攻击校验基准的边际成本。
5. **攻击迁移的不对称性**：CAISI 发现针对更鲁棒模型开发的攻击更容易迁移到较弱模型。能否以此为原则挑选回归测试集的种子，提高测试集的“保质期”？
6. **系统级防御的策略自动合成与验证**：让 LLM 写策略，形式化工具检查策略，衡量安全与效用的权衡。
7. **抵御优化型攻击的批量级、会话级检测**：针对 BPJ 一类“过程中留下大量痕迹”的攻击。
8. **红队 agent 的工作记忆设计**：如何把攻击经验沉淀为可执行的检查，而不只是一个提示库，并研究经验在不同模型版本之间如何衰减。
9. **去武器化的攻击知识表示**：能否只共享“机理描述”而不共享“可用载荷”，同时保留对防御方的大部分价值？

---

## 七、反方观点与不确定性

- **攻击者也在工业化**：GTG-1002 事件中，AI 完成了 80–90% 的战术操作（[08](../ai-for-security/08-anthropic-gtg-1002-ai-espionage.md)）；FAR AI 的结果显示目前进攻在算力效率上占优。防御方的工业化未必比攻击方快。
- **Goodhart 风险**：静态题库加合规阈值可能导致“刷题式安全”；以 ASR 为目标的防御会对评测集过拟合。
- **集中化**：一轮并购把工具链集中到少数平台；Promptfoo 等项目的开源承诺能否持续，需要观察。
- **本文判断的局限**：
  - 前沿实验室的内部流程大多不公开，“已进入工业化早期”的判断依据是公开博文和论文；
  - 部分数字只能来自二手报道（已注明）；
  - 对 2026 年下半年的新进展可能检索不全；
  - 汇总打分是作者的主观判断。

---

## 八、回到博客的问题

博客结尾问：“**怎样的工具访问、反馈和知识积累，能让助手可靠地推进这个项目？**”

换到 LLM 安全，可以用五个问题判断一个子任务是否具备工业化条件：

1. **反馈**：成功或失败能否被可执行地判定？判定器本身测试过吗？它会不会被优化器利用？
2. **工具访问**：攻击或防御 agent 能否不靠人逐步指挥，自己推进内循环？它能调用哪些分析工具？
3. **知识积累**：每一轮的经验能否沉淀为下一轮可以运行的检查？
4. **可重放**：模型或评判器换版本后，结果能否重放、能否被“召回”重判？
5. **可共享**：知识能否在不扩散武器的前提下跨团队复用？

按这五个问题衡量，**智能体攻击测试**和**系统级防御**大部分可以回答“是”；**越狱攻击**卡在第 1 题；**模型内防御**卡在第 1 题和“鲁棒性无法证明”这一根本限制上。因此接下来几年最值得投入的，不是再造一个更强的攻击生成器，而是**造好量具**：可靠的校验基准，以及对校验基准本身的测试。这与博客的核心经验一致：

> 校验基准本身也需要重建。修复它，就是修复游戏的一部分。

---

## 参考资料

**起点**
- N0zoM1z0，[逆向工程的工业革命（东方游戏重建）](https://rea.tools/zh-CN/blog/touhou-reconstruction/)，REA 博客，2026-10-10

**越狱攻击与成本**
- [AutoDAN-Turbo](https://arxiv.org/abs/2410.05295)（ICLR 2025）
- [Rainbow Teaming](https://arxiv.org/abs/2402.16822)（NeurIPS 2024）
- [Best-of-N Jailbreaking](https://arxiv.org/abs/2412.03556)
- [Scaling Trends in Language Model Robustness](https://arxiv.org/abs/2407.18213)（FAR AI，ICML 2025）
- [Boundary Point Jailbreaking of Black-Box LLMs](https://arxiv.org/abs/2602.15001)、[UK AISI 介绍](https://www.aisi.gov.uk/blog/boundary-point-jailbreaking-a-new-way-to-break-the-strongest-ai-defences)
- [The Jailbreak Tax](https://proceedings.mlr.press/v267/nikolic25a.html)（ICML 2025）
- [Jailbroken Frontier Models Retain Their Capabilities](https://arxiv.org/abs/2605.00267)

**评判器与方法学**
- [A Coin Flip for Safety: LLM Judges Fail to Reliably Measure Adversarial Robustness](https://arxiv.org/abs/2603.06594)
- [A StrongREJECT for Empty Jailbreaks](https://arxiv.org/abs/2402.10260)
- [Lessons From Red Teaming 100 Generative AI Products](https://arxiv.org/abs/2501.07238)（Microsoft）

**智能体攻击**
- [OpenAI：Hardening Atlas against prompt injection](https://openai.com/index/hardening-atlas-against-prompt-injection)（原文无法直接访问，细节参考 [TechInformed](https://techinformed.com/openai-hardens-chatgpt-atlas-against-prompt-injection-with-auto-attacker-red-team/)、[eSecurity Planet](https://www.esecurityplanet.com/artificial-intelligence/openai-hardens-chatgpt-atlas-against-prompt-injection-attacks/) 等报道）
- [Lessons from Defending Gemini Against Indirect Prompt Injections](https://arxiv.org/abs/2505.14534)（Google DeepMind）
- [RL Is a Hammer and LLMs Are Nails（RL-Hammer）](https://arxiv.org/abs/2510.04885)
- [Security Challenges in AI Agent Deployment（ART 基准）](https://arxiv.org/abs/2507.20526)
- [How Vulnerable Are AI Agents to Indirect Prompt Injections?](https://arxiv.org/abs/2603.15714)、[NIST CAISI 博客](https://www.nist.gov/blogs/caisi-research-blog/insights-ai-agent-security-large-scale-red-teaming-competition)
- [AIRTBench](https://arxiv.org/abs/2506.14682)（Dreadnode）
- [AutoAdvExBench](https://proceedings.mlr.press/v267/carlini25a.html)（ICML 2025）
- [Simon Willison：The Summer of Johann](https://simonwillison.net/2025/Aug/15/the-summer-of-johann/)（“AI Bug 之月”）
- [EchoLeak CVE-2025-32711 报道](https://thehackernews.com/2025/06/zero-click-ai-vulnerability-exposes.html)
- [CWE-1427](https://cve.circl.lu/cwes/CWE-1427)
- [MCP 工具投毒（CSA 研究笔记）](https://labs.cloudsecurityalliance.org/research/csa-research-note-mcp-tool-poisoning-ai-agent-exfiltration-2/)

**防御**
- [Rapid Response: Mitigating LLM Jailbreaks with a Few Examples](https://arxiv.org/abs/2411.07494)
- [Anthropic：模型安全漏洞赏金](https://www.anthropic.com/news/testing-our-safety-defenses-with-a-new-bug-bounty-program)
- [gpt-oss-safeguard（OpenAI 帮助中心）](https://help.openai.com/en/articles/11870455-openai-open-weight-models-gpt-oss)
- [Trading Inference-Time Compute for Adversarial Robustness](https://arxiv.org/abs/2501.18841)（OpenAI）
- [Securing AI Agents with Information-Flow Control（FIDES）](https://arxiv.org/abs/2505.23643)、[Microsoft Agent Framework 博客](https://devblogs.microsoft.com/agent-framework/fides/)
- [Progent](https://arxiv.org/abs/2504.11703)
- [Design Patterns for Securing LLM Agents against Prompt Injections](https://arxiv.org/abs/2506.08837)
- [Simon Willison：Agents Rule of Two 与 The Attacker Moves Second](https://simonw.substack.com/p/new-prompt-injection-papers-agents)
- [Simon Willison：The lethal trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)

**工具与审计 agent**
- [Building and evaluating alignment auditing agents](https://alignment.anthropic.com/2025/automated-auditing)（Anthropic）
- [Bloom](https://www.anthropic.com/news/bloom)（Anthropic）
- [On the Biology of a Large Language Model](https://transformer-circuits.pub/2025/attribution-graphs/biology.html)（Anthropic）
- [OSS-Fuzz README](https://github.com/google/oss-fuzz)

**产业与制度**
- [Google AI VRP（The Register 报道）](https://www.theregister.com/2025/10/07/google_ai_bug_bounty/)
- [OWASP Top 10 for Agentic Applications](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026)
- [Check Point 收购 Lakera](https://www.securityweek.com/check-point-to-acquire-ai-security-firm-lakera/)
- [OpenAI 收购 Promptfoo](https://openai.com/blog/openai-to-acquire-promptfoo)（另见 [Security Boulevard 报道](https://securityboulevard.com/2026/03/openai-acquires-security-startup-promptfoo-to-fortify-ai-agents)）
- [美国 AI 行动计划与 AI-ISAC（Cybersecurity Dive）](https://cybersecuritydive.com/news/white-house-artificial-intelligence-action-plan-cybersecurity-trump/753856)
- [欧盟 GPAI 行为准则](https://en.wikipedia.org/wiki/General-Purpose_AI_Code_of_Practice)
- [GB/T 45654—2025 中文原文（TC260）](https://www.tc260.org.cn/upload/2025-06-30/1751257342816036759.pdf)、[CSET 英译本](https://cset.georgetown.edu/wp-content/uploads/t0661_gen_ai_safety_standard_final_EN.pdf)
- [curl 终止漏洞赏金（The Register）](https://www.theregister.com/2026/01/21/curl_ends_bug_bounty/)

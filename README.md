# LLM 安全顶尖研究精读：AI for Security & Security for AI

本仓库收录 2024 年至 2026 年 10 月间**认可度最高**的 22 项 AI 安全研究，并对每一项做了中文精读分析。

**筛选标准**
- 学术论文：顶会获奖（Best / Outstanding / Distinguished Paper），或被顶会（IEEE S&P、USENIX Security、CCS、NDSS、ICML、ICLR、NeurIPS）接收且被业界广泛采用的工作；
- 工业界成果：头部机构（Google DeepMind / Project Zero、Anthropic、OpenAI、Microsoft、DARPA）公开发布、有可验证数据的研究。

**每篇分析的结构**：基本信息 → 一句话总结 → 背景与问题 → 方法 → 关键结果（含数据） → 贡献与意义 → 局限 → 对研究者的启示。所有数据都来自原文或官方报告，每篇开头附有来源链接。

---

## 一、AI for Security（用 AI 做安全）

| # | 研究 | 机构 / 会议 | 核心看点 |
|---|---|---|---|
| 01 | [Project Glasswing / Claude Mythos Preview](ai-for-security/01-project-glasswing-claude-mythos.md) | Anthropic，2026-04 | 在所有主流 OS 和浏览器中找到并利用 0-day；exploit 生成能力约提升两个数量级；模型限制访问，只给防御方 |
| 02 | [DARPA AIxCC 决赛](ai-for-security/02-darpa-aixcc-final.md) | DARPA，2025-08 | 全自动找漏洞加打补丁：发现 86%、修复 68%；7 个 CRS 全部开源 |
| 03 | [Big Sleep](ai-for-security/03-google-big-sleep.md) | Google Project Zero + DeepMind | 用变体分析找到模糊测试漏掉的 SQLite 漏洞；首次在在野利用前挫败 0-day |
| 04 | [Claude Opus 4.6：500+ 个高危漏洞](ai-for-security/04-claude-opus-4-6-500-zero-days.md) | Anthropic，2026-02 | 不用专门 harness，靠阅读代码和提交历史挖洞 |
| 05 | [CodeMender](ai-for-security/05-deepmind-codemender.md) | Google DeepMind，2025-10 | 重点从“找”转向“修”：72 个上游修复，并主动做安全加固 |
| 06 | [Aardvark / Codex Security](ai-for-security/06-openai-aardvark.md) | OpenAI，2025-10 | 嵌入开发流程的持续代码安全审计，召回率 92% |
| 07 | [XBOW 登顶 HackerOne](ai-for-security/07-xbow-hackerone.md) | XBOW，2025-06 | 在真实赏金平台上胜过人类；用验证器消除误报 |
| 08 | [GTG-1002：AI 主导的网络间谍行动](ai-for-security/08-anthropic-gtg-1002-ai-espionage.md) | Anthropic，2025-11 | 攻击者用 AI agent 完成 80–90% 的战术操作，是威胁模型的实证更新 |
| 09 | [ReSym](ai-for-security/09-resym-ccs24.md) | **CCS 2024 Distinguished Paper** | 用 LLM 加 Prolog 推理，从剥离的二进制中恢复变量和结构体 |
| 10 | [Cybench](ai-for-security/10-cybench-iclr25.md) | **ICLR 2025 Oral** | 以人类最快解题时间为难度刻度的 CTF 基准 |

## 二、Security for AI（AI 自身的安全）

| # | 研究 | 机构 / 会议 | 核心看点 |
|---|---|---|---|
| 11 | [Stealing Part of a Production LM](security-for-ai/11-stealing-production-lm-icml24.md) | **ICML 2024 Best Paper** | 只用 API 就窃取了 OpenAI 模型的隐藏维度和最后一层；促使 OpenAI 和 Google 修改 API |
| 12 | [Safety Alignment Should Be Made More Than Just a Few Tokens Deep](security-for-ai/12-shallow-safety-alignment-iclr25.md) | **ICLR 2025 Outstanding Paper** | “浅层对齐”一个概念统一解释了四类越狱和微调攻击 |
| 13 | [Don't Listen To Me](security-for-ai/13-dont-listen-to-me-jailbreak-usenix24.md) | **USENIX Security 2024 Distinguished Paper** | 越狱提示分类体系加 92 人用户研究 |
| 14 | [The Attacker Moves Second](security-for-ai/14-attacker-moves-second-usenix26.md) | USENIX Security 2026（三大实验室联合） | 自适应攻击打破 12 种已发表防御，大多 ASR > 90% |
| 15 | [AgentDojo](security-for-ai/15-agentdojo-neurips24.md) | NeurIPS 2024 | 提示注入攻防的事实标准基准；能力越强的模型越容易被攻击 |
| 16 | [Many-shot Jailbreaking](security-for-ai/16-many-shot-jailbreaking-neurips24.md) | NeurIPS 2024（Anthropic） | 长上下文攻击，效果随示例数按幂律增长 |
| 17 | [Crescendo](security-for-ai/17-crescendo-multi-turn-jailbreak.md) | USENIX Security 2025（Microsoft） | 由全部良性的多轮对话逐步完成越狱 |
| 18 | [Chasing Shadows](security-for-ai/18-chasing-shadows-llm-security-pitfalls.md) | NDSS 2026 | LLM 安全研究的 9 类方法学陷阱，72 篇论文全部中招 |
| 19 | [CaMeL](security-for-ai/19-camel-defeating-prompt-injections.md) | Google DeepMind，2025-03 | 用系统安全设计（能力标签、数据流控制）防御提示注入，具备可证明的安全性 |
| 20 | [Constitutional Classifiers](security-for-ai/20-constitutional-classifiers.md) | Anthropic，2025-02 / 2026-01 | 经过数千小时红队检验的通用越狱防御；新一代开销约 1% |
| 21 | [ADAS：智能体系统自动设计](security-for-ai/21-adas-automated-design-of-agentic-systems.md) | ICLR 2025 | 元智能体用代码自动设计智能体；是 AgenticRed 的方法基础 |
| 22 | [AgenticRed](security-for-ai/22-agenticred-evolving-red-teaming-systems.md) | arXiv 预印本，2026-01 | 用 GPT-5 演化整套越狱攻击系统；HarmBench ASR 96–100%，迁移到 GPT-5.1 达 100% |

---

## 三、综合观察

### 1. AI 挖洞能力在两年内跨过了实用门槛
2024 年 Big Sleep 还被作者称为“高度实验性”。到 2025 年 AIxCC 的发现率已达 86%，XBOW 登顶 HackerOne。2026 年 Opus 4.6 发现 500+ 个漏洞，Mythos Preview 能稳定写出可用的 exploit（[01](ai-for-security/01-project-glasswing-claude-mythos.md)–[04](ai-for-security/04-claude-opus-4-6-500-zero-days.md)、[07](ai-for-security/07-xbow-hackerone.md)）。**瓶颈正在从“发现”转向“验证、修复和披露”**（[05](ai-for-security/05-deepmind-codemender.md)、[06](ai-for-security/06-openai-aardvark.md)）。

### 2. LLM 和传统工具是互补关系
最好的系统都是“LLM 加模糊测试、符号执行、sanitizer 或验证器”的组合（[02](ai-for-security/02-darpa-aixcc-final.md)、[07](ai-for-security/07-xbow-hackerone.md)、[09](ai-for-security/09-resym-ccs24.md)）。LLM 擅长语义推理（变体分析、不变量），传统工具负责精确性和确认。

### 3. 模型级防御普遍脆弱，系统级设计是出路
浅层对齐（[12](security-for-ai/12-shallow-safety-alignment-iclr25.md)）、长上下文（[16](security-for-ai/16-many-shot-jailbreaking-neurips24.md)）、多轮对话（[17](security-for-ai/17-crescendo-multi-turn-jailbreak.md)）都能绕过安全训练；自适应攻击打破了几乎所有已发表的防御（[14](security-for-ai/14-attacker-moves-second-usenix26.md)）。可行的方向是**不信任模型**的系统设计（[19 CaMeL](security-for-ai/19-camel-defeating-prompt-injections.md)），以及接受过大规模真实红队检验的多层防护（[20](security-for-ai/20-constitutional-classifiers.md)）。

### 4. 两个方向正在合流
攻击者已经在用 AI agent 实施攻击（[08](ai-for-security/08-anthropic-gtg-1002-ai-espionage.md)），而他们绕过安全机制的手段（任务拆分、角色伪装）正是 Security for AI 研究的越狱问题。AI 能力的发布治理（[01](ai-for-security/01-project-glasswing-claude-mythos.md) 的限制访问）本身也成了安全议题。

### 5. 方法学严谨性亟待提升
每篇 LLM 安全论文都至少有一个方法学陷阱（[18](security-for-ai/18-chasing-shadows-llm-security-pitfalls.md)）；静态评估会严重高估防御效果（[14](security-for-ai/14-attacker-moves-second-usenix26.md)）。做研究时应报告确切的模型版本、检查数据泄露，并用自适应攻击评估。

---

## 四、建议阅读顺序

1. **入门**：[12](security-for-ai/12-shallow-safety-alignment-iclr25.md) → [15](security-for-ai/15-agentdojo-neurips24.md) → [14](security-for-ai/14-attacker-moves-second-usenix26.md) → [19](security-for-ai/19-camel-defeating-prompt-injections.md)（理解越狱和注入的根因、基准、攻击与防御）
2. **AI 挖洞**：[03](ai-for-security/03-google-big-sleep.md) → [02](ai-for-security/02-darpa-aixcc-final.md) → [04](ai-for-security/04-claude-opus-4-6-500-zero-days.md) → [01](ai-for-security/01-project-glasswing-claude-mythos.md)（按时间顺序看能力演进）
3. **做研究前必读**：[18](security-for-ai/18-chasing-shadows-llm-security-pitfalls.md)

## 说明

- IEEE S&P 2025/2026 的官方获奖页面在调研时无法访问，因此未纳入其获奖论文，留待后续补充。
- 工业界报告大多由发布方单方面提供，外部无法完全复现，分析中已标明相关局限。
- 少数论文只能读到摘要和部分正文，对应分析中没有引用读不到的具体数值。

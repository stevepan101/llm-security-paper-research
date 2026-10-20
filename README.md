# LLM 安全顶尖研究精读：AI for Security、Security for AI 与多模态安全

本仓库收录 2024 年至 2026 年 10 月间**认可度最高**的 40 项 AI 安全研究，并对每一项做了中文精读分析。

**筛选标准**
- 学术论文：顶会获奖（Best / Outstanding / Distinguished Paper），或被顶会（IEEE S&P、USENIX Security、CCS、NDSS、ICML、ICLR、NeurIPS）接收且被业界广泛采用的工作；多模态部分另收录 CVPR、AAAI、ECCV 上认可度高（Oral 或被广泛引用和集成进工具）的代表作；
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

## 三、多模态与生成模型安全

| # | 研究 | 机构 / 会议 | 核心看点 |
|---|---|---|---|
| 23 | [Visual Adversarial Examples Jailbreak Aligned LLMs](multimodal-security/23-visual-adversarial-jailbreak-aaai24.md) | AAAI 2024 Oral（Princeton） | 一张对抗图像让 VLM 对大量未见有害指令言听计从；多模态越狱的奠基工作 |
| 24 | [Jailbreak in Pieces](multimodal-security/24-jailbreak-in-pieces-iclr24.md) | **ICLR 2024 Spotlight** | 只用 CLIP 编码器构造对抗图像，配合无害文本组合越狱，LLaVA 成功率 87% |
| 25 | [FigStep](multimodal-security/25-figstep-aaai25.md) | AAAI 2025 Oral（清华等） | 把有害问题排版成图片，零优化黑盒越狱；开源 VLM 平均 82.5%，GPT-4V 70% |
| 26 | [Agent Smith](multimodal-security/26-agent-smith-icml24.md) | ICML 2024（Sea AI Lab） | 一张图像在多智能体之间传染式传播，约 30 轮越狱一百万个智能体 |
| 27 | [Best-of-N Jailbreaking](multimodal-security/27-best-of-n-jailbreaking-neurips25.md) | NeurIPS 2025（Anthropic 等） | 随机增强加反复采样，覆盖文本、视觉、音频；GPT-4o 文本 89%，成功率按幂律增长 |
| 28 | [Failures to Find Transferable Image Jailbreaks](multimodal-security/28-failures-transferable-image-jailbreaks-iclr25.md) | ICLR 2025（Stanford、Anthropic 等） | 负结果：40 多个 VLM 上，梯度图像越狱几乎无法迁移 |
| 29 | [SneakyPrompt](multimodal-security/29-sneakyprompt-sp24.md) | **IEEE S&P 2024** | 首个自动化文生图越狱，强化学习替换敏感词；SD 过滤器平均绕过 96.37% |
| 30 | [Ring-A-Bell](multimodal-security/30-ring-a-bell-iclr24.md) | ICLR 2024 | 离线提取概念向量，绕过扩散模型的各种概念移除方法 |
| 31 | [UnlearnDiffAtk](multimodal-security/31-unlearndiffatk-eccv24.md) | ECCV 2024（MSU） | 用被遗忘模型自身做分类器，轻松找回被“遗忘”的裸露、画风和物体 |
| 32 | [SafeGen](multimodal-security/32-safegen-ccs24.md) | **ACM CCS 2024**（浙江大学） | 在视觉自注意力层移除色情生成能力，对文本侧越狱提示鲁棒 |
| 33 | [UltraBreak](multimodal-security/33-ultrabreak-iclr26.md) | ICLR 2026（墨尔本大学等） | 视觉约束加语义损失，让通用对抗图像在开源 VLM 间迁移；对 GPT-5 等前沿模型仍基本无效 |
| 34 | [Jailbreaking VLMs Through the Visual Modality](multimodal-security/34-visual-modality-jailbreak-icml26.md) | ICML 2026 | 在 GPT-5.2、Gemini 3、Claude Haiku 4.5 上量化跨模态对齐缺口：图形密码 40.9% 对文字密码 10.7% |
| 35 | [JOOD](multimodal-security/35-jood-playing-the-fool-cvpr25.md) | CVPR 2025（NAVER、KAIST） | 用 mixup 把有害图像变成分布外输入，GPT-4V 炸弹类 63%，对 o1 也有效 |
| 36 | [AdvWave](multimodal-security/36-advwave-audio-jailbreak-iclr25.md) | ICLR 2025（UIUC） | 音频大模型的白盒越狱，扰动伪装成环境噪声，平均成功率 74.6% |
| 37 | [Exposing the Guardrails](multimodal-security/37-exposing-dalle-guardrails-usenix25.md) | **USENIX Security 2025 Distinguished Artifact** | 用计时侧信道逆向 DALL·E 多级护栏，再用否定句和低资源语言越狱 |
| 38 | [JailFuzzer](multimodal-security/38-jailfuzzer-sp25.md) | **IEEE S&P 2025** | 模糊测试加 LLM 智能体，生成通顺的越狱提示；DALL·E 3 绕过率 81.93% |
| 39 | [SceneSplit](multimodal-security/39-scenesplit-t2v-jailbreak-iclr26.md) | ICLR 2026 | 把有害情节拆成无害场景越狱文生视频；Sora 2、Veo 2 等商用模型 68.6%–84.1% |
| 40 | [Safety-Guided Flow](multimodal-security/40-safety-guided-flow-iclr26.md) | **ICLR 2026 Oral** | 统一负向引导防御并证明应在早期引导；Ring-A-Bell 攻击下裸露率降到 5.1% |

---

## 四、综合观察

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

### 6. 多模态让攻击面成倍扩大，文本对齐不会自动迁移
图像和音频是连续、可求梯度、增强空间巨大的输入：白盒下一张图就能越狱（[23](multimodal-security/23-visual-adversarial-jailbreak-aaai24.md)），黑盒下把文字排版成图（[25](multimodal-security/25-figstep-aaai25.md)）、混合成分布外输入（[35](multimodal-security/35-jood-playing-the-fool-cvpr25.md)）或随机增强反复采样（[27](multimodal-security/27-best-of-n-jailbreaking-neurips25.md)）就能打到闭源模型；梯度图像越狱难以迁移（[28](multimodal-security/28-failures-transferable-image-jailbreaks-iclr25.md)），2026 年的改进能在开源模型间迁移，但对前沿模型仍无效（[33](multimodal-security/33-ultrabreak-iclr26.md)）。在 2026 年的前沿模型上，跨模态对齐缺口依然存在但因厂商而异（[34](multimodal-security/34-visual-modality-jailbreak-icml26.md)）；音频（[36](multimodal-security/36-advwave-audio-jailbreak-iclr25.md)）和视频生成（[39](multimodal-security/39-scenesplit-t2v-jailbreak-iclr26.md)）是正在打开的新攻击面。文生图领域同样如此：文本过滤器和概念移除都能被绕过（[29](multimodal-security/29-sneakyprompt-sp24.md)–[31](multimodal-security/31-unlearndiffatk-eccv24.md)），商用多级护栏的弱点在于各级组件理解不一致（[37](multimodal-security/37-exposing-dalle-guardrails-usenix25.md)），通顺的自然语言越狱让困惑度过滤失效（[38](multimodal-security/38-jailfuzzer-sp25.md)）。防御侧，视觉层能力移除（[32](multimodal-security/32-safegen-ccs24.md)）和有理论保证的推理时引导（[40](multimodal-security/40-safety-guided-flow-iclr26.md)）是两条主要路线，但都缺少针对自身的自适应攻击检验。

---

## 五、建议阅读顺序

1. **入门**：[12](security-for-ai/12-shallow-safety-alignment-iclr25.md) → [15](security-for-ai/15-agentdojo-neurips24.md) → [14](security-for-ai/14-attacker-moves-second-usenix26.md) → [19](security-for-ai/19-camel-defeating-prompt-injections.md)（理解越狱和注入的根因、基准、攻击与防御）
2. **AI 挖洞**：[03](ai-for-security/03-google-big-sleep.md) → [02](ai-for-security/02-darpa-aixcc-final.md) → [04](ai-for-security/04-claude-opus-4-6-500-zero-days.md) → [01](ai-for-security/01-project-glasswing-claude-mythos.md)（按时间顺序看能力演进）
3. **多模态安全（最新进展）**：[34](multimodal-security/34-visual-modality-jailbreak-icml26.md) → [33](multimodal-security/33-ultrabreak-iclr26.md) → [27](multimodal-security/27-best-of-n-jailbreaking-neurips25.md)（2025–2026 年前沿 VLM 越狱）；[37](multimodal-security/37-exposing-dalle-guardrails-usenix25.md) → [38](multimodal-security/38-jailfuzzer-sp25.md) → [39](multimodal-security/39-scenesplit-t2v-jailbreak-iclr26.md) → [40](multimodal-security/40-safety-guided-flow-iclr26.md)（文生图 / 文生视频越狱与防御）；需要背景时再读 [23](multimodal-security/23-visual-adversarial-jailbreak-aaai24.md)、[25](multimodal-security/25-figstep-aaai25.md)、[29](multimodal-security/29-sneakyprompt-sp24.md)
4. **做研究前必读**：[18](security-for-ai/18-chasing-shadows-llm-security-pitfalls.md)

## 六、专题分析

| # | 专题 | 核心看点 |
|---|---|---|
| P1 | [LLM 安全能否进入“工业化早期”？](perspectives/01-llm-security-industrialization.md) | 借用“逆向工程的工业革命”的框架评估越狱攻击、智能体攻击、护栏防御三个方向：智能体攻击测试已进入工业化早期；越狱攻击的生成已自动化，但判定是否有害的评判器还不可靠；防御中能工业化的是补丁流水线和系统级强制。文中列出需要推进的 8 项能力和若干选题 |

## 说明

- IEEE S&P 2025/2026 的官方获奖页面在调研时无法访问，因此未纳入其获奖论文，留待后续补充。
- 工业界报告大多由发布方单方面提供，外部无法完全复现，分析中已标明相关局限。
- 少数论文只能读到摘要和部分正文，对应分析中没有引用读不到的具体数值。

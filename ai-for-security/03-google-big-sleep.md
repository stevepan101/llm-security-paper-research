# Big Sleep（前身 Project Naptime）

| 项目 | 内容 |
|---|---|
| 机构 | Google Project Zero + Google DeepMind |
| 时间 | 2024-06（Naptime）→ 2024-10（首个 SQLite 漏洞）→ 2025-07（CVE-2025-6965）→ 2025-08（20 个开源漏洞） |
| 类型 | 工业界 AI 漏洞挖掘智能体 |
| 原文 | [From Naptime to Big Sleep（Project Zero 博客）](https://projectzero.google/2024/10/from-naptime-to-big-sleep.html)、[The Hacker News：CVE-2025-6965](https://thehackernews.com/2025/07/google-ai-big-sleep-stops-exploitation.html)、[Computing：20 个漏洞](https://www.computing.co.uk/news/2025/security/big-sleep-finds-20-flaws-in-open-source-software) |

## 一句话总结

Big Sleep 让 LLM agent 像人类安全研究员一样使用代码浏览器和调试器做**变体分析**（variant analysis）。它在 SQLite 中找到了模糊测试漏掉的真实漏洞，后来又找到一个只有攻击者知道、即将被利用的 0-day，并在被利用前完成了修复。

## 方法

- **工具**：代码浏览器（搜索、阅读源码）、调试器（运行测试输入、设置断点）、报告工具（提交发现）。
- **变体分析**：给 agent 一个近期的修复提交及其 diff，让它在当前代码中寻找**相关但还没被修复**的问题。这是 Project Zero 人工研究员常用的方法，因为同类错误往往会在代码中多处出现。
- agent 通过“提出假设、写测试用例、用调试器验证”的循环推进。

## 关键发现

### 1. SQLite 栈缓冲区下溢（2024-10）

- **位置**：`generate_series` 扩展中的 `seriesBestIndex` 函数。`iColumn` 字段用 -1 作为 ROWID 约束的哨兵值，而该函数没有处理这种情况。
- **触发**：`SELECT * FROM generate_series(1,10,1) WHERE ROWID = 1;`
- **影响**：在 release 构建中，越界写可能破坏一个之后会被解引用的指针，属于“很可能可利用”。漏洞在正式发布前就被发现并当天修复，没有用户受到影响。

**为什么模糊测试没找到？**
- OSS-Fuzz 的 harness 没有启用 `generate_series` 扩展；
- 另一个 harness 包含的是该函数没有这个漏洞的旧版本；
- 作者自己跑了约 150 CPU 小时的 AFL 也没找到，只有语料中已经有和崩溃输入非常接近的样本时才能快速触发。

### 2. CVE-2025-6965（2025-07）

- SQLite 的内存破坏漏洞，CVSS 7.2，影响 3.50.2 之前的所有版本。
- Google 威胁情报团队观察到攻击者在准备一个 0-day，但无法定位具体漏洞；Big Sleep 被用来把它找出来。Google 称这是 AI agent **首次直接挫败一次在野利用尝试**。

### 3. 20 个开源漏洞（2025-08）

- 主要在 FFmpeg 和 ImageMagick 中，细节按披露流程暂不公开。

## 贡献与意义

1. 证明 LLM agent 可以发现**广泛使用的真实软件中此前未知的、可利用的**内存安全漏洞（2024 年时被认为是首例）。
2. 揭示了 AI 与模糊测试的**互补性**：AI 擅长依据代码语义推理边界条件（哨兵值），而模糊测试受限于 harness 配置和语料。
3. 把 AI 挖洞与**威胁情报**结合，从“发现漏洞”走向“抢在攻击者前面”。

## 局限（作者自述）

- 结果“高度实验性”，早期只在小程序和这一次真实的变体分析实验中验证过。
- agent 的最初假设比较模糊，最终复现的崩溃和它原本要测的并不完全是同一个问题。
- 作者认为在当时，针对目标定制的模糊测试器至少同样有效。

## 对研究者的启示

- **变体分析**是 LLM 挖洞特别有效的切入点：有补丁 diff 作为强先验，搜索空间大大缩小。
- “AI 找出 harness 覆盖不到的代码”提示了一个方向：用 LLM 自动生成和改进模糊测试 harness（OSS-Fuzz-Gen 就是类似思路）。

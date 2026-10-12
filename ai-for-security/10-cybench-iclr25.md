# Cybench: A Framework for Evaluating Cybersecurity Capabilities and Risks of Language Models

| 项目 | 内容 |
|---|---|
| 作者 | Andy K. Zhang 等（Stanford，Percy Liang、Dan Boneh 团队） |
| 会议 | ICLR 2025，**Oral** |
| 原文 | [arXiv:2408.08926](https://arxiv.org/abs/2408.08926)、[ICLR 页面](https://iclr.cc/virtual/2025/oral/31753)、[项目主页](https://cybench.github.io) |

## 一句话总结

用 40 道专业级 CTF 题，以“人类最快解题时间”作为难度刻度，配合子任务拆分，系统评估 LM agent 的攻防能力。它已成为前沿模型网络安全风险评估的常用基准之一。

## 背景与问题

此前的网络安全基准要么题目太简单（高中级 CTF），要么只有“成功或失败”的二元结果，无法细致衡量能力，也无法刻画模型能力与人类的相对位置。

## 方法

- **题目**：40 道专业级 CTF，来自 4 个比赛：HackTheBox Cyber Apocalypse 2024、SekaiCTF（2022-23）、Glacier、HKCert。覆盖密码学、Web、逆向、取证、杂项、二进制利用（pwn）六类。将近一半在 2023 年 12 月之后发布，以减少训练数据污染。
- **难度刻度**：首次解出时间（First Solve Time, FST），即比赛中第一支人类队伍解出该题的时间，范围从 2 分钟到 24 小时 54 分钟。
- **子任务**：把部分题拆成一系列中间问题，可以给部分分，也能定位 agent 卡在哪一步。
- **三种评估模式**：无引导（二元成功）、子任务引导（以最后一个子任务计分）、子任务表现（解出子任务的比例）。
- **Agent scaffold**：structured bash、action-only、pseudoterminal、web search 四种。

## 关键结果

- 评估了 8 个模型：GPT-4o、o1-preview、Claude 3 Opus、Claude 3.5 Sonnet、Gemini 1.5 Pro、Llama 3 70B、Llama 3.1 405B、Mixtral 8x22b。
- **无引导最佳成功率约 17.5%**（Claude 3.5 Sonnet + structured bash）。
- 无引导时只能解出 FST ≤ 11 分钟的题；最难的题（FST 约 25 小时）没有被解出。
- 有子任务引导时，最高解出 FST 为 52 分钟（GPT-4o）和约 2 小时 3 分钟（Claude 3.5 Sonnet + pseudoterminal）。
- Scaffold 的影响因模型而异：Claude 用 pseudoterminal 和 web search 效果更好，GPT-4o 反而变差。
- 安全拒绝很少，只出现在 Claude 3 Opus 和 Claude 3.5 Sonnet 上。

## 贡献与意义

1. **FST 难度刻度**让模型能力可以直接对照人类专家水平，便于政策沟通（“模型能解人类顶尖队伍 X 分钟能解的题”）。
2. **子任务设计**提供了细粒度信号，是能力评估方法上的贡献。
3. 已被广泛用于前沿模型发布前的网络安全能力评估（例如各大实验室的 system card 和 AI 安全研究所的评估）。

## 局限

- CTF 和真实漏洞挖掘、渗透测试仍有差距（题目小而封闭，并且确定有解）。
- 40 道题的规模偏小，统计置信度有限。
- 到 2026 年，前沿模型在 Cybench 上的成绩已经大幅提升，基准面临饱和（[01 Mythos 报告](01-project-glasswing-claude-mythos.md)也提到现有基准基本已被做满）。

## 对研究者的启示

- 评估方法可以借鉴：用**人类参照**（FST）加**子任务分解**来设计新基准。
- 下一代基准需要转向真实的 0-day 发现或长周期渗透任务，以避免饱和与数据污染。

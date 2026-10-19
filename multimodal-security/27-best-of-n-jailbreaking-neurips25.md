# Best-of-N Jailbreaking

| 项目 | 内容 |
|---|---|
| 作者 | John Hughes, Sara Price, Aengus Lynch（共同一作）, Rylan Schaeffer, Fazl Barez, Sanmi Koyejo, Henry Sleight, Erik Jones, Ethan Perez, Mrinank Sharma（Speechmatics、MATS、UCL、Stanford、Oxford、Anthropic 等） |
| 会议 | NeurIPS 2025 |
| 原文 | [NeurIPS 论文页](https://papers.nips.cc/paper_files/paper/2025/hash/69f3eb242c7c9df9ea2f2b66ea8b3c0f-Abstract-Conference.html)、[arXiv:2412.03556](https://arxiv.org/abs/2412.03556) |

## 一句话总结

不做任何优化，只是对有害请求反复做随机增强（文本打乱大小写和字母顺序、图片换字体和颜色、音频变速变调），一直试到模型答应为止。试 1 万次后，GPT-4o 的文本越狱成功率达 89%，Claude 3.5 Sonnet 达 78%；同样的方法对视觉和音频输入也有效，成功率随尝试次数按**幂律**上升。

## 背景与问题

前沿模型的输出有随机性，输入空间又极大。作者问：如果攻击者什么技巧都不用，只靠“暴力采样”，能走多远？这个问题对多模态模型尤其重要，因为图像和音频的增强空间比文本更大。

## 方法

BoN（Best-of-N）是纯黑盒方法，不需要 logprob 或梯度：对一个有害请求反复采样增强版本，直到目标模型输出有害内容或达到上限 N。用 GPT-4o 加 HarmBench 判定提示做自动判定，标记为成功的样本再人工复核。

| 模态 | 增强方式 | N 上限 |
|---|---|---|
| 文本 | 词内字母打乱（首尾字母不动）、随机大小写、ASCII 字符扰动 | 10,000 |
| 视觉 | 把请求排版成图片，随机图片尺寸、50–80 个彩色色块背景、104 种字体、字号、粗细、颜色、位置 | 7,200 |
| 音频 | 语速、音高（±2000 音分）、音量、叠加语音和噪声、背景音乐 | 7,200 |

评测使用 HarmBench 中 159 个直接有害请求。

## 关键结果

**文本**（N = 10,000）：GPT-4o 89%，Claude 3.5 Sonnet 78%，Gemini Pro 50%，Llama 3.1 8B 94%。加了电路熔断（circuit breakers）防御的 Llama-3-8B-Instruct-RR 也有 52%。不做增强的基线：Claude 3.5 Sonnet 0.6%，Gemini Pro 0%。

**视觉**（N = 7,200）：Claude 3 Opus 88%，GPT-4o-mini 67%，GPT-4o 56%，Gemini Flash 46%，Claude 3.5 Sonnet 33%，Gemini Pro 25%。

**音频**（N = 7,200）：GPT-4o Realtime 71%，Gemini Flash 71%，Gemini Pro 59%，开源语音模型 DiVA 87%。

**很多成功来得很早**：在 Claude 和 GPT 系列上，N = 10,000 时的文本成功案例中有 53%–71% 在前 100 次内出现；N = 100 时攻击 GPT-4o 的成本约 9 美元，成功率约 49%。

**幂律规律**：−log(ASR) 与 N 近似满足幂律，不同模型和模态的斜率相近、截距不同。用 N ≤ 1,000 的数据拟合，外推到更大 N 的平均误差约 4.6%。这意味着攻击者可以用少量预算**预测**大预算下的成功率。

**与其他攻击组合**：在 Claude 3.5 Sonnet 上先加 many-shot 前缀（[16 MSJ](../security-for-ai/16-many-shot-jailbreaking-neurips24.md)），达到 74% 成功率所需的 N 从 6,000 降到 274。组合前缀后，最终成功率在 GPT-4o 文本上从 86% 升到 97%，Claude 3.5 Sonnet 视觉从 32% 升到 70%，Gemini Pro 音频从 59% 升到 87%；样本效率最多提升 28 倍（文本）、68 倍（视觉）、250 倍（音频）。

## 贡献与意义

1. **简单而通用的基线**：一种方法同时覆盖文本、视觉、音频三种模态，所有闭源前沿模型都未能幸免。
2. **揭示了随机性本身就是攻击面**：成功主要来自输入方差和采样随机性，而不是某种特定增强。对抗输入空间越大（图像、音频），这个问题越难堵。
3. **给出可预测的缩放规律**：和 [16 MSJ](../security-for-ai/16-many-shot-jailbreaking-neurips24.md) 一样，越狱成功率可以用幂律刻画，便于做风险评估。
4. 说明只靠模型自身的拒绝行为挡不住大量采样，需要 [20 Constitutional Classifiers](../security-for-ai/20-constitutional-classifiers.md) 这类独立的输入输出分类器。

## 局限

- **成功的越狱不稳定**：把成功的增强提示在 temperature 1 下重新采样，只有约 30%（文本）、25%（视觉）、15%（音频）的概率再次得到有害输出。
- 自动判定器有误报，作者依赖人工复核和过滤规则，部分曲线的平台期来自判定修正。
- 只用了 159 个请求；超出测试范围的 N 下是否仍满足幂律未经验证。
- 大规模采样成本不低（例如对 Claude 3.5 Sonnet 跑满 10,000 次约 1,352 美元）；而且可以推断，大量相似请求容易被基于会话或流量的检测发现（论文未测试这类检测）。

## 对研究者的启示

- 评估防御时，应报告**成功率随尝试次数变化的曲线**，而不只是单次或少数几次的结果；单次测试会严重高估安全性。
- 对多模态模型，输入增强空间越大，防御越不能依赖模型自身的拒绝，需要独立的输入输出过滤和速率限制。
- BoN 可以作为任何新防御的低成本必测基线，与自适应攻击（[14](../security-for-ai/14-attacker-moves-second-usenix26.md)）一起使用。

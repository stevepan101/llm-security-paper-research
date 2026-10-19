# Toward Universal and Transferable Jailbreak Attacks on Vision-Language Models（UltraBreak）

| 项目 | 内容 |
|---|---|
| 作者 | Kaiyuan Cui, Yige Li, Yutao Wu, Xingjun Ma, Sarah Erfani, Christopher Leckie, Hanxun Huang（University of Melbourne、Singapore Management University、Deakin University、复旦大学） |
| 会议 | ICLR 2026 |
| 原文 | [arXiv:2602.01025](https://arxiv.org/abs/2602.01025)、[ICLR 页面](https://iclr.cc/virtual/2026/poster/10009353)、[代码](https://github.com/kaiyuanCui/UltraBreak) |

## 一句话总结

[28](28-failures-transferable-image-jailbreaks-iclr25.md) 发现基于梯度的图像越狱几乎不能迁移。UltraBreak 正面回应这个问题：它认为迁移失败是因为对抗图像过拟合了替代模型，于是在**视觉空间**加随机变换和平滑约束，在**文本目标**上改用语义损失。只在 Qwen2-VL-7B 上优化一张图，就能在 6 个未见过的开源 VLM 上把 SafeBench 平均越狱成功率提到 71.05%，并对部分商用小模型有效；但对 GPT-5、Claude Sonnet 4.5 这类前沿模型基本无效。

## 背景与问题

白盒图像越狱几乎必胜（[23](23-visual-adversarial-jailbreak-aaai24.md)），但真实威胁取决于能否**黑盒迁移**到别的模型，尤其是闭源模型。作者把迁移失败归结为两点：对抗图案过拟合替代模型的特定特征；用逐 token 的交叉熵去逼近固定目标句，优化地形崎岖，容易陷入只对某个模型有效的解。

## 方法

- **威胁模型**：黑盒，不访问受害模型；可以在一个或多个替代 VLM 上优化。目标是一张图像同时满足**跨目标通用**（对很多有害问题有效）和**跨模型迁移**。
- **视觉空间约束**：在空白底图上随机放置对抗图块，随机旋转（±15°）、缩放（0.8–1.2），并加总变差（total variation）正则，让图案更平滑、不依赖像素级细节。
- **语义损失**：不再要求模型逐字输出目标句，而是把模型输出分布投影到 LLM 的文本嵌入空间，与目标句的嵌入做余弦距离；再用带因果掩码的注意力加权未来的目标 token。这相当于“只要意思对就行”，地形更平滑。
- **提示引导**：把有害问题改写成“列出步骤”的形式，并要求以肯定前缀开头（与 [25 FigStep](25-figstep-aaai25.md) 的思路相近）。
- **优化**：Adam，1,300 步，主实验用 Qwen2-VL-7B-Instruct 作替代模型，判定使用 HarmBench 分类器。

## 关键结果

**跨模型迁移**（替代模型 Qwen2-VL-7B，黑盒受害模型的平均攻击成功率，表 1）：

| 数据集 | 无攻击 | VAJM（[23](23-visual-adversarial-jailbreak-aaai24.md)） | UMK | FigStep | UltraBreak |
|---|---|---|---|---|---|
| SafeBench | 40.57% | 41.46% | 20.00% | 66.54% | **71.05%** |
| AdvBench | 5.96% | 5.61% | 5.19% | — | **52.19%** |
| MM-SafetyBench | 35.10% | 28.16% | 21.82% | — | **58.50%** |

黑盒受害模型包括 Qwen-VL-Chat、Qwen2.5-VL-7B、LLaVA-v1.6、Kimi-VL、GLM-4.1V-Thinking 等。注意 FigStep 需要为每个问题单独做一张图，而 UltraBreak 是一张图通用。

**商用模型**（在去掉最有害目标的子集上，表 1）：GPT-4.1-nano 38.78%、Gemini-2.5-flash-lite 42.00%、Claude-3-haiku 16.00%，平均 32.26%；无攻击基线平均 20.00%。

**前沿模型**（附录表 9）：GPT-5 为 26%（无攻击 24%），Claude Sonnet 4.5 为 20%（无攻击 30%），即基本没有迁移效果。

**消融**（表 3，SafeBench / AdvBench 黑盒平均）：完整方法 71.83% / 57.64%；去掉视觉约束降到 51.99% / 29.86%；把语义损失换回交叉熵降到 55.80% / 40.15%。两个设计都有显著贡献。替代模型越大、受害模型越小，迁移越好。

## 贡献与意义

1. **部分推翻了“图像越狱不能迁移”的结论**：在开源 VLM 之间，经过正则化的通用对抗图像可以稳定迁移。
2. **给出了迁移失败的可操作解释**：过拟合替代模型加崎岖的优化地形，并分别用视觉约束和语义损失缓解。
3. **同时划出了边界**：对前沿闭源模型几乎无效，说明当前前沿模型对梯度类图像越狱的抵抗力明显强于小模型。和 [28](28-failures-transferable-image-jailbreaks-iclr25.md) 合起来读，结论更完整。

## 局限

- 对 GPT-5、Claude Sonnet 4.5 迁移很弱，作者归因于替代模型与受害模型的规模差距。
- 商用模型评估使用了去掉最有害目标、改用较温和肯定短语的子集，数字不能直接与开源模型比较。
- 依赖 HarmBench 分类器判定，没有评估任何防御。
- 表 1 与正文、表 3 的平均值因是否包含 Kimi-VL 而略有出入（71.05% 与 71.83%）。

## 对研究者的启示

- 研究迁移攻击时，正则化和损失设计比单纯加大集成更重要；“只对齐语义”的损失值得在其他模态上尝试。
- 防御方不应把“前沿模型不受迁移影响”当作永久结论：替代模型规模增长后，这个差距可能缩小。
- 评估通用越狱图像时，应同时报告无攻击基线，本文多个数据集的无攻击成功率本身就不低（如 SafeBench 40.57%）。

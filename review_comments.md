# CRAFT 论文初稿审阅意见

## Overall Assessment

本文提出了一个清晰且有充分动机支撑的贡献。核心思想（利用 precharge 代价不对称性进行自适应 timeout 调整）简洁优雅，140 B/channel 的硬件开销极具说服力。但在结构、逻辑和表述层面仍有若干问题需要在投稿前解决。以下按章节组织意见。

---

## 1. Title

**现状：** "CRAFT: Exploiting Precharge Cost Asymmetry for Adaptive DRAM Row Buffer Management"

**问题：** 标题可以接受，但稍显模板化。"Exploiting ... for ..." 是常见句式，区分度不高。建议让标题更直接地传达机制或优势，例如：

- "CRAFT: Cost-Asymmetric Feedback Timeout for Lightweight DRAM Row Buffer Management"

这样既突出了机制（feedback timeout），又点明了关键优势（lightweight），比抽象动词 "exploiting" 信息量更大。

---

## 2. Abstract

1. **与正文信息高度重复。** 摘要目前读起来像是全文的压缩版，几乎所有数字在 Introduction 和 Evaluation 中原样重复。摘要应侧重 *insight* 和 *significance*，而非穷举所有数值。

2. **"Three precharge-path refinements further improve adaptation precision without additional hardware structures" 过于模糊。** 摘要应至少提示这些 refinement 的内容（如 read/write differentiation、streak decay），让读者对设计有具体感知。

3. **"CRAFT outperforms every baseline on every benchmark" 同时出现在摘要和 Introduction 中。** 这一表述过于强烈，有 promotional 嫌疑。建议至少在其中一处改为 "CRAFT consistently outperforms all evaluated baselines"。

4. **摘要最后两句（"An ablation study demonstrates ... These results confirm ..."）更适合放在 Conclusion 中。** 摘要应以关键结果和意义收尾，而非描述 ablation methodology 的细节。

---

## 3. Section 1: Introduction

1. **多处存在从句结构，违反写作规范。** 示例：
   - Line 14: "the internal sense-amplifier array **that** caches the most recently activated row" — 关系从句。
   - Line 15: "but risks expensive conflicts **when** a different row is potentially needed" — 状语从句。
   - Line 15: "**Holding** a row open" — 分词结构作主语。

   这些需要改写为独立句子。

2. **Motivation 到 solution 之间存在逻辑断层。** Introduction 先展示了三个维度的变化性（workload、phase、bank），然后直接跳到 "Prior adaptive schemes face a persistent tradeoff"。过渡过于突兀。应添加一个承接句，明确指出：这三个维度要求一种能够 per-bank、phase-adaptive 的机制，然后再论证现有方案为何在这一需求上存在不足。

3. **Baseline 引用格式不一致。** Introduction 中 INTAP 使用 "[Ghasemp+16]"，但 Section 4.3 中使用 "[Intel06]"。全文应统一引用 key。

4. **Contribution 2 过长。** 它将两个不同的发现打包在一条中：(a) precharge-path signals 足够，(b) conflict-path signals 有害。这两点互补但各自独立，建议拆分或精简表述。

5. **"cost-blind feedback"（摘要 line 6）和 "cost-blind adjustment"（line 91）似乎是作者自创术语。** 应在首次出现时给出清晰定义，并在全文中保持一致使用。目前摘要中出现时没有任何定义。

---

## 4. Section 2: Background

### 2.1 DRAM Row Buffer Fundamentals

1. **Timeout-based precharge 的四种 outcome（lines 64–67）与 Section 3.1 的三种 outcome 不一致。** Section 2.1 列出了四种 outcome，包括 "row buffer hit"。但 Section 3.1 和 Algorithm 1 中只讨论三种 outcome（right、wrong、conflict）。"Row buffer hit" 实际上意味着没有发生 precharge event。这一不一致可能造成混淆。建议在 Section 2.1 中明确说明：第四种情况（hit）不涉及 precharge 事件，因此 CRAFT 的 feedback loop 只关注三种 precharge outcome。

2. **"Timeout-based speculative precharge" 以加粗标题形式出现在 Section 2.1 内部，但并非正式小节。** 这造成层级结构的混乱。建议要么将其提升为 Section 2.2，要么去掉加粗标题、作为 2.1 的自然延续。

### 2.2 Limitations of Existing Adaptive Schemes

1. **最后一段（line 93）包含本文的核心技术 claim — 2:1 cost ratio。** 这一段目前位于 Background 的末尾。但这是论文的核心洞察，值得更高的显示度。建议将这一观察移至 Section 3 开头，或者创建一个独立小节（如 "2.3 The Cost Asymmetry of Precharge Outcomes"），使其作为一等贡献而非局限性讨论的结尾备注。

2. **Table 1 的 "Key Limitation" 列与正文措辞不一致。** INTAP 在表中为 "Symmetric fixed-step; cost-blind adjustment"，但正文中为 "applies the same fixed step to both wrong precharges and conflicts despite their differing latency costs"。应统一术语。

3. **对 ABP 的批评 ("This formulation cannot capture bank-level phase transitions") 缺乏论证。** 为什么 per-row predictor 不能追踪 phase transitions？大概是因为 table 过大无法追踪所有 row 且表项会老化。应明确阐述推理过程。

---

## 5. Section 3: CRAFT Design

### 3.1 Core Feedback Loop

1. **参数 BASE_STEP = 50 出现时没有任何 justification。** 为什么是 50 cycles？是从 timing parameters 推导的、经验调优的、还是任意选取的？需要简要说明设计依据。

2. **关于 "deliberate upward bias"（line 114）的讨论只呈现了正面效果。** 审稿人会追问：在 wrong/conflict 频率相当的 workload 上，这种偏差是否导致 timeout 单调递增？论文应说明什么机制防止了 runaway escalation。答案是 T_MAX 的 clamp，但这一关联应在此处明确建立。

3. **Algorithm 1 中 right_streak 的更新看似无用。** Right precharge 会递增 right_streak，但 Algorithm 1 的伪代码中并未触发任何动作。RS refinement（Section 3.2a）使用 right_streak，但仅看 Algorithm 1 的读者会认为 right_streak 更新没有意义。建议添加注释或说明指向 Section 3.2。

### 3.2 Implementation Refinements

1. **标题 "Implementation Refinements" 具有误导性。** 这些是 feedback policy 的算法改进，而非 implementation details（如 pipeline 集成或 clock domain crossing）。建议改为 "Precharge-Path Refinements" 或 "Feedback Refinements"。

2. **"Across 62 benchmarks"（line 172）来源不明。** Evaluation 使用 12 个 benchmark。其余 50 个来自哪里？需要澄清。如果来自更广泛的 profiling study，应注明来源。否则会引入未解释的数据，损害可信度。

3. **RW "doubles the de-escalation step for read conflicts"（line 173）的理由不充分。** 前文解释了为什么 write wrong precharges 获得减半的 escalation step（write buffer 吸收了 penalty）。但对 read conflict 加倍 de-escalation 的对称论证缺失。为什么 read conflict 应导致更快的 de-escalation？

### 3.3 Hardware Implementation

本小节清晰且结构良好。小建议：

1. **"16-bit previous row address" — 应说明 16 bits 的来源。** Table 3 中 65,536 rows per bank 正好对应 2^16。建议明确指出这一推导："Each bank contains 65,536 rows (2^16), requiring a 16-bit row address."

---

## 6. Section 4: Methodology

1. **ChampSim-DRAMSim3 集成方式未说明（line 209）。** ChampSim 如何与 DRAMSim3 通信？CRAFT 逻辑实现在 DRAMSim3 的 memory controller 中还是 ChampSim 侧？简要描述 CRAFT 在仿真栈中的位置有助于可重复性。

2. **SimPoint 方法（line 239）：每个 simulation point 仅测量 80M 条指令。** 对于具有长运行 phase 的 graph workloads，这可能不够充分。应确认此 interval length 的合理性或承认这一局限。

3. **Benchmark 选取范围偏窄。** 12 个 benchmark 来自三个 suite，且 graph workloads 占比过重（9/12 为 graph benchmark，仅 2 个来自 SPEC）。顶级会议审稿人很可能要求更广泛的评估。建议至少在 Discussion 中承认这一局限性。

4. **Section 4.3 提到 "A detailed discussion of these approaches is provided in Section 6"。** 这一表述不够精确。Related Work 是在更广泛语境下讨论这些方法，而非作为 baseline description。建议改为："Section 6 discusses these approaches in the broader context of prior work."

---

## 7. Section 5: Evaluation

### 5.1 IPC Performance

1. **IPC 讨论与 timeout distribution 分析交织在一起。** 类似 "The High timeout range dominates the distribution throughout execution" 和 "The Low range accounts for the majority of timeout observations" 的句子引用了尚未出现的 Figure 6（Section 5.3）。这种前向引用干扰了叙事流。建议要么将 timeout 相关观察移至 Section 5.3，要么提前引入 Figure 6。

2. **"CRAFT outperforms every baseline on every benchmark" 已是第三次重复（摘要、Introduction、此处）。** 到第三次时已失去冲击力。在 Evaluation 中应让数据自己说话。建议改为 "CRAFT achieves positive IPC improvement on all 12 benchmarks relative to all three baselines."

3. **"Graph traversal"、"Graph analysis"、"Scientific computing" 这些类别标签（lines 287–291）在 Methodology 中未定义。** Table 4 按 suite（LIGRA、CRONO、SPEC）分组，而非按这些分析类别。应在 Methodology 中定义这些类别，或在全文中统一使用 suite-based 分组。

### 5.2 DRAM-Level Verification

1. **Section 标题 "DRAM-Level Verification" 暗示功能正确性验证。** 实际内容展示的是性能指标（hit rate、latency）。更准确的标题应为 "DRAM-Level Performance Analysis" 或 "Row Buffer and Latency Analysis"。

### 5.3 Timeout Distribution

本小节写作良好，提供了对 CRAFT 自适应行为的真实洞察。小问题：

1. **三段范围分类 [50, 800), [800, 2000), [2000, 3200] 的引入缺乏 justification。** 为什么选择这些边界？它们是等间距的还是对应有意义的行为阈值？需要简要说明动机。

### 5.4 Ablation Study

1. **"PR" 和 "QDSD" 首次出现时未展开全称（line 328）。** 读者在此第一次遇到这两个缩写。需要给出完整名称和简要描述（推测为 Phase Reset 和 Queue-Depth Scaling De-escalation，但应在文中明确）。

2. **Ablation study 声称比较八个变体，但只描述了六个**（BASE、RS、RW、SD、PRECHARGE、ALL 加上 PR 和 QDSD 单独测试）。需要一个清晰的枚举或表格列出所有八个变体，帮助读者追踪实验条件。

3. **"Adding both to the PRECHARGE configuration yields the ALL variant at 120.8%"** — 由于 PRECHARGE 为 131.9%，添加 conflict-path signals 实际上将性能从 131.9% *降低*到 120.8%。这是一个重要发现，值得更强的强调。目前的措辞掩盖了这 11 个百分点的性能下降。

---

## 8. Section 6: Related Work

1. **Static policies 小节的内容有些边缘。** Kaseridis et al. 的 Minimalist Open-page 与本文关联较弱。JEDEC 标准的讨论属于 Background 材料而非 Related Work。建议精简或合并到 Section 2。

2. **HAPPY 的讨论（line 336）声称 "HAPPY is orthogonal to CRAFT's cost-asymmetric timeout adaptation"。** 这一正交性声明未经论证。HAPPY 和 CRAFT 如何组合使用？简要勾勒一下可以使这一声明更具体。

3. **Ipek et al. 的 RL 方法（line 342）需要 "32 KB of SRAM"。** 但这是用于 command scheduling，而非 row buffer management。两者解决的是不同问题，比较有失公平。应在文中明确指出这一区别。

---

## 9. Section 7: Conclusion

1. **Conclusion 基本上是重复摘要、Introduction 和 Evaluation 中已给出的数字。** 顶级会议的 Conclusion 应超越 summarization。建议添加一个前瞻性段落，讨论：(a) 对其他 DRAM 标准（LPDDR、HBM）的适用性，(b) 与 scheduling policies 结合的可能性，或 (c) 对 CXL-attached memory 的启示。

2. **"CRAFT's per-bank state organization makes it orthogonal to and combinable with DRAM architectural modifications and memory scheduling optimizations"（line 351）。** 这是一个未经验证的强 claim。应加以限定（"we expect CRAFT to be combinable..."）或提供简要证据。

---

## Cross-cutting Issues

### 1. 内容重复

同一组数字（7.73%、3.10%、2.84%、140 B/channel、5.62 pp）在摘要、Introduction、Contributions、Evaluation 和 Conclusion 中至少出现四次。顶级会议审稿人会注意到这一点并标记为 padding。建议：在 Abstract、Evaluation 和 Conclusion 中保留精确数字，在其他位置使用定性描述。

### 2. 缺少 Discussion/Limitation Section

论文没有讨论 limitations、threats to validity 或 generalizability 的章节。审稿人很可能会提出以下问题：
- 仅单核评估？多核干扰如何？
- 仅 DDR5-4800？对 timing parameters 的敏感性如何？
- 仅 12 个 benchmark，且 graph workloads 占比过重？
- 没有能耗分析？

添加一个简短的 Discussion 小节（即使仅 0.5 页）可以预防性地回应这些质疑。

### 3. 写作规范违规

全文多处句子使用了从句、分词短语和 em-dash/colon 结构，需要系统性地改写为独立句子。典型示例：
- Line 14: "the internal sense-amplifier array **that** caches..."
- Line 15: "**Holding** a row open ... **but** risks ... **when** ..."
- Line 37: "the three possible outcomes ..., namely *right*, *wrong*, and *conflict*, carry..." (分词同位语)

### 4. Figure/Table 引用位置

Figures 1 和 2 出现在 Introduction 中，作为 motivation 使用。在会议论文中，图表应出现在首次引用附近。在 LaTeX 排版时确认放置位置与 markdown 顺序一致。

---

## Priority Summary

| 优先级 | 问题 | 位置 |
|--------|------|------|
| High | 添加 Discussion/Limitations section | 新增 Section 6 或 6.5 |
| High | 解决 3 种 vs 4 种 outcome 的不一致 | Sections 2.1 vs 3.1 |
| High | Justify BASE_STEP = 50 和 timeout range 的边界选择 | Section 3.1, 5.3 |
| High | 解释 "62 benchmarks" 统计数据的来源 | Section 3.2 |
| High | 在 ablation 中定义 PR 和 QDSD 的全称 | Section 5.4 |
| High | 移除 Section 5.1 中对 timeout distribution 的前向引用 | Section 5.1 |
| Medium | 将 2:1 cost ratio 的洞察提升为独立小节 | Section 2 |
| Medium | 减少关键数字的重复引用 | 全文 |
| Medium | 修复写作规范违规（从句、分词结构） | 全文 |
| Medium | 扩大 benchmark 讨论范围或承认局限性 | Section 4, Discussion |
| Low | 重命名 "Implementation Refinements" | Section 3.2 |
| Low | 重命名 "DRAM-Level Verification" | Section 5.2 |
| Low | 在 Conclusion 中加入前瞻性讨论 | Section 7 |

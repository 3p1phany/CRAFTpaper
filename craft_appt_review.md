# `craft_appt.md` 分章节修改意见

本文从计算机系统结构方向博士生导师和会议审稿人的视角，对初稿 [craft_appt.md](/root/data/CRAFTpaper/craft_appt.md) 提出修改建议。以下意见主要聚焦于标题与章节标题、论文逻辑、学术措辞、前后定义一致性，以及论文整体的可接受性。根据你的说明，以下意见忽略图片插入链接、引用完整性、中英混杂问题以及文中的 `TODO` 标记；同时不引入文章中未出现的新内容。

## 一、总体评价

这篇初稿的核心想法是清楚的：利用 speculative precharge 不同结果之间的代价不对称性，构造一个轻量级、自适应的 row buffer management 机制。文章的主线也基本完整，包含动机、背景、设计、方法、实验、消融和相关工作，整体框架符合体系结构会议论文的常见组织方式。

当前最需要加强的不是“有没有结果”，而是“定义是否严谨、论证是否闭环、表述是否克制”。从审稿视角看，本文目前最容易被质疑的点主要有四类：

1. 关键概念定义前后不一致，尤其是 precharge outcome 的分类方式。
2. 个别结论性措辞过强，容易被认为超出实验所能支持的范围。
3. 设计章节与评估章节之间存在命名和逻辑脱节，影响可读性。
4. 若干数据口径和 benchmark 描述不完全统一，容易引发对实验边界的质疑。

建议优先修复以上问题，再做语言润色。

## 二、优先级最高的问题

### 1. 预充电结果的定义需要全篇统一

这是全文当前最关键的问题。

在引言中，文章写道 speculative precharge 的结果是 `right`, `wrong`, `conflict` 三类；但在背景部分又写成四类结果，即 `right precharge`, `wrong precharge`, `conflict`, `row buffer hit`；到了 Section 3.1，又说“在 timeout-triggered precharge 之后分类 conflict”，这在事件时序上也不完全严谨。

建议做如下统一：

1. 在 Background 中先定义“所有可能观察到的访问结果”。
2. 再明确指出“哪些结果用于 timeout feedback adjustment”。
3. 在 Abstract、Introduction、Section 2、Section 3、Figure caption、Algorithm 中全部使用同一套术语。

更具体地说，可以将逻辑整理为：

- 从 bank 行为角度，访问可能表现为四类现象。
- 从 timeout 反馈控制角度，真正驱动调整的是若干关键 outcome。
- `row buffer hit` 是否作为“零反馈”事件，需要明确说明。

如果这一点不统一，审稿人会直接怀疑设计定义是否稳定。

### 2. 结论性表述过强，建议改为经验性结论

文中多处使用了如下强结论措辞：

- `complete and sufficient feedback basis`
- `entirely from the read path`
- `genuinely adaptive`
- `unambiguous feedback signal`
- `dominant contributor`

这些表述在口语上很有力度，但在学术论文中容易被认为“论断超出实验范围”。尤其在体系结构论文里，如果没有形式化证明或更广泛实验支撑，建议将其改写为更稳健的经验性判断，例如：

- `is sufficient in our evaluated setting`
- `appears to account for most of the observed gain`
- `suggests that ... is an effective feedback signal`
- `the observed improvement is primarily attributable to ...`

你的实验结果是有说服力的，但应避免让审稿人抓住“过度外推”的把柄。

### 3. 设计章节与评估章节之间缺少闭环

Section 3.2 中定义了 `RS`, `RW`, `SD` 三个 refinement，但 Section 5.4 中又直接使用 `PRECHARGE`, `PR`, `QDSD`, `ALL` 等变体名。对第一次阅读的审稿人而言，这种命名跳转会明显增加理解成本。

建议在下面两种做法中选一种：

1. 在 Section 3.2 末尾增加一个小表格，列出所有评估中出现的变体及其组成。
2. 在 Section 5.4 开头先集中解释所有变体缩写，再展开结果分析。

否则审稿人会不断回翻正文确认这些缩写分别对应什么设计元素。

### 4. benchmark 与统计口径需要统一

文中存在以下口径不一致的问题：

- 引言动机使用了 `mcf`、`omnetpp`。
- Methodology 中说评估覆盖 `12 memory-intensive benchmarks`。
- 但实际表格更像是 `benchmark-input pairs`。
- Section 3.2 还出现了 `Across 62 benchmarks` 的说法，但正文没有交代这 62 个 benchmark 来自哪里。

建议统一区分：

1. `motivation examples`
2. `evaluation workloads`
3. `auxiliary profiling dataset`（如果确实存在）

特别建议把 `12 memory-intensive benchmarks` 改成更准确的 `12 memory-intensive workloads` 或 `12 benchmark-input pairs`。

## 三、分章节修改建议

## 1. 标题与摘要

### 标题

当前标题：

> `CRAFT: Exploiting Precharge Cost Asymmetry for Adaptive DRAM Row Buffer Management`

这个标题总体是合格的，优点是：

- 直接点出核心 insight：`Precharge Cost Asymmetry`
- 明确应用对象：`Adaptive DRAM Row Buffer Management`
- 缩写 `CRAFT` 较容易记忆

如果你想让标题更像体系结构会议论文，也可以考虑让方法属性更突出，例如强调 `feedback`。但当前标题本身不必强行改。

### 摘要

摘要整体结构是对的，已经具备“问题-方法-结果”三段式雏形，但还可以进一步提升学术表达质量。

建议如下：

1. 第一段背景可再压缩一些，突出“现有方法要么复杂，要么反馈粗糙”的核心矛盾即可，不必在摘要中塞入过多 baseline 细节。
2. 第二段方法部分需要和正文统一 terminology，尤其是 precharge outcome 的分类数量和定义。
3. 第三段结果部分数字较多，信息密度很高，但略显拥挤。可以保留最核心的 IPC、storage overhead、关键消融结论，其他次要数字可酌情精简。
4. 摘要最后一句 `complete and sufficient feedback basis` 建议改弱，否则容易被认为结论下得过满。

建议摘要风格更接近：

- 先说明问题与 gap；
- 再说明核心观察和设计；
- 最后给出最有代表性的实验结果及意义。

## 2. Introduction

引言的整体逻辑已经具备基础，但目前更像“高密度技术说明”，还不够像一篇标准会议论文的 Introduction。建议重构为更明确的四步：

1. 说明 row buffer management 为什么重要。
2. 说明为什么静态 open/close page policy 不足。
3. 说明现有 adaptive 方法的关键缺口。
4. 引出本文 insight、方法和贡献。

### 具体建议

#### (1) 动机层次可以更清晰

当前引言中已经提到：

- 不同 workload 差异大；
- 同一程序不同 phase 差异大；
- 同一 channel 不同 bank 差异大。

这是很好的动机材料，但建议改成更明显的递进结构，而不是平铺式罗列。例如可以组织成：

- first, across workloads...
- second, within a workload across phases...
- third, even across banks within a channel...

这样会让“为什么必须做 per-bank adaptive timeout”更自然地推出。

#### (2) Baseline gap 需要更聚焦

当前对 ABP、DYMPL、INTAP 的介绍是清楚的，但可以进一步收束到一个统一问题：

- ABP/DYMPL 代表“高复杂度”
- INTAP 代表“低复杂度但反馈过于粗糙”
- 三者共同缺乏“cost-aware feedback”

如果把这一句总括得更清楚，CRAFT 的必要性会更强。

#### (3) 方法介绍略长，贡献列表略像结果复述

引言中对方法细节的描述已经比较多，贡献列表又重复了一部分结果，造成信息密度偏高。建议：

- 在引言正文中保留核心方法思想；
- 细节留到 Section 3；
- 贡献列表只保留最关键的三点，不宜把消融中的具体负结果直接写成 contribution。

当前 contribution 2 写法偏像“实验发现”，不够像“研究贡献”。更好的组织方式可以是：

1. 提出 cost-asymmetric feedback 机制；
2. 设计 lightweight per-bank adaptive timeout controller；
3. 通过 cycle-accurate evaluation 验证其在性能和开销上的优势。

## 3. Background

Section 2 的作用应该是：建立共同术语、说明问题本质、自然引出 CRAFT 的设计动机。当前这部分总体不错，但仍有两个明显可以加强的地方。

### 3.1 DRAM Row Buffer Fundamentals

#### 优点

- 对 row buffer hit / miss / conflict 的定义较清楚；
- 对 timeout-based speculative precharge 的介绍直观；
- Figure 3 对设计背景有帮助。

#### 建议

1. 这里应成为全文术语定义的唯一“标准出处”。后文所有关于 outcome 的用语都应回到这里保持一致。
2. `four outcomes` 与后文 `three outcomes` 的关系必须在本节说清楚。
3. 最后一段应更明确地引向后文，例如指出“问题不只是 adaptive，而是如何利用不同结果的不同代价来进行 adaptive adjustment”。

### 3.2 Limitations of Existing Adaptive Schemes

这部分写得比较成熟，表 1 也有比较好的总结效果。

但建议注意两点：

1. 不要让这一节显得像“为 CRAFT 定制批评 prior work”。
2. 应把三类 baseline 的不足归结到一个统一维度，即“lack of cost-aware outcome-sensitive adaptation”。

最后一段目前已经接近这个效果，但建议再加一句承上启下的话，把“2:1 cost ratio”明确过渡到 Section 3 的设计原则。

## 4. CRAFT Design

这是全文最关键的章节，也是目前最需要打磨的章节。不是因为 idea 有问题，而是因为这里最容易暴露“定义不够严谨”和“时序不够精确”的问题。

### 4.1 Core Feedback Loop

这是整个论文中最需要重写的部分。

#### 主要问题 1：事件时序描述需要更严谨

当前写法中有一句大意是：

> When a bank activation event occurs following a timeout-triggered precharge, the controller classifies the outcome ...

但后续算法又在判断 `was_ondemand_precharge`，这会让读者困惑：

- conflict 是在哪个时刻被识别的？
- `prev_closed_by_timeout` 和 `was_ondemand_precharge` 的生命周期是什么？
- outcome classification 是在 ACT 时进行，还是在 PRE 时/请求到达时进行？

建议你在文字描述中明确：

1. 哪些状态在 row close 时记录；
2. 哪些状态在下一次请求到达时检查；
3. 哪些状态在 ACT issued 时更新；
4. right/wrong/conflict 分别由什么条件判定。

如果没有这层严谨定义，审稿人会觉得“idea intuitively makes sense，但 implementation semantics 不够清楚”。

#### 主要问题 2：算法伪代码与文字需要完全对齐

Algorithm 1 当前是有帮助的，但需要注意：

- 变量命名应与正文严格一致；
- conflict 的判定路径需要再自洽；
- right precharge 是否调整 timeout，需要明确；
- row buffer hit 是否为“no-op”事件，也应说明。

建议在算法前增加一句说明：

- 伪代码只展示反馈更新逻辑；
- 正常请求服务与 DRAM command sequencing 依赖底层控制器实现。

这样可以避免读者误以为算法试图完整刻画控制器。

#### 主要问题 3：参数设定依据不够充分

当前设计中出现了多个关键参数：

- `BASE_STEP = 50`
- `[T_MIN, T_MAX] = [50, 3200]`
- `SHIFT_CAP`
- `four or more consecutive right precharges`

这些参数目前更多像“作者选定的经验值”，但论文中缺少说明它们如何得到。建议至少补一层解释：

1. 哪些参数来源于 timing ratio 推导；
2. 哪些参数来源于经验调优；
3. 哪些参数在实验中被固定。

即使不增加额外实验，也建议在文字上说明这些值的设计依据和直觉。

### 4.2 Implementation Refinements

三个 refinement 的动机基本都合理，但表达上可以更审稿友好一些。

#### (1) Right Streak De-escalation (RS)

该部分逻辑较清楚，但建议避免用过强措辞，如：

- `provides a proactive path`

可改为更中性表达，例如“helps reduce elevated timeout values when explicit conflict feedback is sparse”。

#### (2) Read/Write Cost Differentiation (RW)

这一部分的问题主要不是机制，而是数据口径。

文中写到：

> Across 62 benchmarks, read operations account for 80.3% of all wrong precharge events ...

但正文主实验只有 12 个 workload，这里的 `62 benchmarks` 缺少来源说明。审稿人可能会问：

- 这 62 个 benchmark 是主实验集之外的 profiling 数据吗？
- 是否与正文 workload 集一致？
- 是否会引入额外偏置？

如果没有必要，建议直接删除这个数字，只保留“read wrong precharge 比 write wrong precharge 更直接影响 processor-visible performance”的机制性解释。

#### (3) Streak Decay (SD)

这一部分表达较好，建议仅做语言精简，使其更紧凑。

### 4.3 Hardware Implementation

这一节已经比较接近正式稿水平。

优点是：

- 存储开销清晰；
- 表 2 易读；
- 硬件代价描述简洁。

建议补强的一点是：将“critical-path computation”与 baseline 进行更明确的对照。现在虽然写了自己的关键路径代价，但如果能补一句对比 ABP / DYMPL / INTAP 的差异，会更完整。

## 5. Methodology

Methodology 目前信息是够的，但还可以更“论文化”，即更强调实验边界、复现方式和 workload 定义。

### 5.1 Simulation Infrastructure

这一节整体没有大问题。表 3 信息完整，配置也基本符合体系结构论文习惯。

建议：

1. 在文字中更明确说明为什么选择 DDR5-4800。
2. 若后文大量依赖 `tRP = tRCD = 40` 的 2:1 cost ratio，应提示这是本文实验配置下的具体实例，而不是所有 DRAM 配置下都严格如此。

### 5.2 Workloads

这里最需要改的是“benchmark”和“workload”的措辞统一。

当前表 4 更准确反映的是 benchmark-input combinations，而不是抽象 benchmark 名称。建议将文字统一为：

- `12 workloads`
- 或 `12 benchmark-input pairs`

而不是反复写 `12 benchmarks`。

此外，建议压缩对 benchmark suite 的介绍，把重点放在：

1. 为什么选择这些 workload；
2. 它们为何具有 memory intensity 或 locality variability；
3. SimPoint 的使用如何帮助代表 phase behavior。

### 5.3 Baselines

这一节目前太短。建议至少补充一类信息：

- baseline 实现来源或复现原则；
- 是否在统一平台上重新实现；
- 参数是否按照原论文或最佳实践设定。

这会显著增强可重复性和说服力。

### 5.4 Metrics

指标选择是合理的：

- IPC
- Read Row Buffer Hit Rate
- Average Read Latency

建议小改两点：

1. 用语上可将 `serves as the primary performance metric` 改得更正式，例如 `is used as the primary system-level performance metric`。
2. 对只报告 read hit rate 的理由可以保留，但表达再克制一些，避免写成绝对性判断。

## 6. Evaluation

这一章结果是有说服力的，但当前最大问题是“结果分析与机制分析有时交叉混杂”，导致结构略显松散。建议把每节的功能边界再划清。

### 6.1 IPC Performance

这一节的主要任务应该是回答：

> CRAFT 是否带来稳定性能提升？

当前第一段已经完成了这个任务，但后面三类 workload 分析中混入了较多 timeout distribution 的细节，这些内容更适合放到 Section 5.3 中。

建议修改方式：

1. 5.1 保留 IPC 结果和高层原因解释；
2. 与 timeout range 分布相关的细节尽量移到 5.3；
3. 强调“why performance improves”时，优先用 row locality matching 和 faster adaptation 来解释。

这样章节边界会更清晰。

### 6.2 DRAM-Level Verification

这一节是必要的，因为它建立了：

- 更高 IPC
- 更高 read row buffer hit rate
- 更低 read latency

之间的因果链条。

建议：

1. 如果正式稿允许，最好配图或表，而不是纯文字描述。
2. `entirely from the read path` 建议改成更谨慎的说法，如 `is primarily attributable to improvements on the read path`。
3. `This observation is consistent with CRAFT's read/write cost differentiation design` 可以保留，但应避免写成因果定论。

### 6.3 Timeout Distribution

这一节是全文非常有价值的一节，因为它展示了 CRAFT 的“适应性”不是空泛声称，而是体现在 timeout state 的真实分布上。

建议强化两点：

1. 明确 Low / Mid / High 是为了可视化分析而做的 post-hoc binning，而不是算法内部的模式分类。
2. 将这一节与 5.1 的 workload 讨论适度整合，避免重复解释同一个 benchmark 的行为。

此外，`Aggressive Close`, `Gradual Transition`, `Keep Open` 这三个小标题很直观，建议保留。

### 6.4 Ablation Study

这一节已经很接近审稿人喜欢的写法，因为它试图回答：

- 核心增益来自哪里？
- refinement 是否必要？
- 额外信号是否真的有用？

但仍有三点建议：

1. 在节首先定义所有变体名称，避免读者反复回查。
2. 将 `detrimental` 改为更克制表达，如 `did not improve performance in our evaluated setting`。
3. 对 `PR` 和 `QDSD` 做一句简明解释，否则如果这些变体没有在前文定义，读者会中断理解。

## 7. Related Work

当前 Related Work 的分类是合理的：

- static policies
- predictor-based schemes
- timeout-based schemes
- learning-based approaches

但整体口吻稍偏“辩护型”，即每类工作都迅速转向强调 CRAFT 更好。Related Work 更理想的风格应是：

1. 先准确概括已有工作的代表思路；
2. 再指出与本文最本质的差异；
3. 少做重复性优劣判断。

建议减少与 Section 2 中 baseline limitation 的重复，把 Related Work 写得更像学术综述，而不是第二次方法对比。

## 8. Conclusion

Conclusion 总体完整，但有些地方仍稍显“把摘要再说一遍”。建议进一步压缩，并保持结论克制。

建议保留三层信息即可：

1. 本文提出了什么方法；
2. 核心 insight 是什么；
3. 实验表明该方法在性能和开销上具有良好平衡。

不建议在结论中再次堆叠过多数字，也不建议使用过强的普遍性判断。

尤其是如下类型表述建议弱化：

- `provides sufficient knowledge`
- `orthogonal to and combinable with ...`

除非正文中确实做了对应实验验证，否则更合适的表述应是：

- `suggests compatibility with`
- `may be complementary to`

## 四、全篇语言风格与学术表达建议

除了结构问题，当前初稿在语言层面还有几个可系统优化的方向。

### 1. 减少“短句密集堆叠”

现在不少段落由连续短句组成，技术信息很密，但会显得略生硬，缺乏论文常见的论证节奏。建议适度合并句子，加入连接关系词，例如：

- `therefore`
- `in contrast`
- `consequently`
- `however`
- `empirically`
- `in our evaluation`

这样会让行文更流畅，更接近正式 conference paper。

### 2. 术语统一

全文中如下术语建议统一使用，不要混杂：

- `row-buffer locality` / `row-level locality`
- `page policy` / `row buffer management policy`
- `timeout value` / `idle timeout`
- `right precharge` / `correct precharge`

建议确定一套主术语后全篇统一。

### 3. 避免绝对化措辞

以下类型词汇建议谨慎使用：

- `complete`
- `sufficient`
- `entirely`
- `unambiguous`
- `genuinely`
- `dominant`

这类词在 rebuttal 中很容易被审稿人抓住。体系结构论文通常更偏好“有证据支持但不过度扩展”的表达。

### 4. 强化“本文在什么范围内成立”

只要是依赖特定实验设置的结论，都建议加上范围限定，例如：

- `under our DDR5-4800 configuration`
- `in our evaluated workloads`
- `within the studied design space`

这会让论文显得更严谨，也更可信。

## 五、建议的修改顺序

为了提高修改效率，建议按以下顺序推进：

1. 先统一 precharge outcome 的定义，并同步修改 Abstract、Introduction、Background、Design、Algorithm、Figure captions。
2. 再重写 Section 3.1，补足事件时序、状态变量和参数依据。
3. 接着统一 benchmark / workload / profiling dataset 的口径。
4. 再整理 Section 5.4 中各 ablation variant 的定义与命名。
5. 最后统一全篇措辞风格，系统降低过强结论表达。

## 六、结语

从内容质量看，这篇初稿已经具备继续打磨成一篇体系结构会议论文的基础。核心想法具备明确 novelty，实验结果也有一定说服力。当前最大的短板不是“有没有贡献”，而是“有没有以审稿人最容易接受的方式把贡献讲清楚、讲严谨、讲克制”。

如果后续继续修改，建议优先把“定义一致性”和“Section 3 的严谨性”打牢，因为这两点最直接决定审稿人是否会相信你的设计是 self-consistent 且 implementable 的。

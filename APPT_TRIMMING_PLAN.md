# CRAFT → APPT 缩减方案

## 总览

| 指标 | 完整版（当前） | APPT 目标 | 削减量 |
|------|---------------|-----------|--------|
| 正文词数 | ~9,700 | ~6,000–6,500 | ~33% |
| 图 | 9 张 | 5 张 | -4 张 |
| 表 | ~9 张 | 5–6 张 | -3–4 张 |
| LNCS 估计页数 | 20–22 页 | 14–15 页（含参考文献） | ~7 页 |

> 标记说明：
> - ✅ **保留** = 原封不动进 APPT
> - ✂️ **压缩** = 保留核心意思，缩减篇幅
> - ❌ **移除** = 从 APPT 版本中整段删除，留给 TACO

---

## Section 1: Introduction（当前 1,020 词 + 3 图）

**目标：~750 词 + 1–2 图，省 ~0.75 页**

| 内容 | 操作 | 理由 |
|------|------|------|
| 第 1 段：Row buffer 根本矛盾 | ✅ 保留 | 核心问题定义，必须保留 |
| 第 2 段：跨 workload/phase/bank 变化 | ✂️ 压缩 | 文字保留，但图做精简（见下） |
| Figure 1（open vs close IPC） | ✅ 保留 | 最核心的 motivation 图 |
| Figure 2（phase RBH 4bench） | ✂️ 合并 | 与 Figure 3 合并为一张 2-panel 图，或只保留 Figure 2 |
| Figure 3（per-bank RBH 3bench） | ❌ 移除 | per-bank 异质性用一句话 + 引用数据点即可论证，完整图留 TACO |
| 第 3 段：现有方案困境 | ✂️ 压缩 | 三个 baseline 各一句话概括，删掉具体数字（详见 Background） |
| 第 4 段：CRAFT 核心洞察 | ✅ 保留 | 论文灵魂 |
| 第 5 段：结果 + 贡献 | ✅ 保留 | 贡献列表 3 条全保留 |

**具体操作：**
- Figure 3 删除，把 "omnetpp CoV=1.51" 这个数据点融入正文一句话即可
- Figure 2 保留（phase variation 是核心 motivation），但 caption 压缩
- 第 3 段（现有方案）从 ~150 词压缩到 ~80 词，去掉 "86.6% of this budget" 等细节（Background 会详述）

---

## Section 2: Background & Motivation（当前 1,359 词 + 2 图 + 1 表）

**目标：~900 词 + 2 图 + 1 表，省 ~0.5 页**

| 内容 | 操作 | 理由 |
|------|------|------|
| 2.1 DRAM Row Buffer 基础 | ✂️ 压缩 | hit/miss/conflict 三种情况各一句即可；timeout 三种 outcome 保留但精简 |
| Figure: timing diagram | ✅ 保留 | 读者理解 right/wrong/conflict 的关键 |
| Figure: policy spectrum | ❌ 移除 | 概念较直观，用一句话描述 "timeout 在 open-close 谱系中的位置" 即可 |
| 2.2 现有方案局限 + Table 1 | ✂️ 压缩 | 表保留，但每个 baseline 的文字描述从 3-4 句压缩到 1-2 句 |
| 2.3 Motivation 三条 Observation | ✂️ 重点压缩 Obs 2 | 见下 |

**2.3 三条 Observation 的处理：**

| Observation | 操作 | 理由 |
|-------------|------|------|
| Obs 1: wrong vs conflict 代价不对称 | ✅ 保留 | CRAFT 核心 insight，必须完整论证 |
| Obs 2: read/write wrong 代价差异 | ✂️ 大幅压缩 | 当前有 ~150 词的数据论证（80.3%/19.7%/4.1x ratio/PageRank 99.8%/wrf 56.5%）。APPT 版只需保留核心论点 + 一个代表性数据点（~50 词），完整数据论证留 TACO |
| Obs 3: precharge outcome 是最直接反馈 | ✂️ 轻度压缩 | 与 intro 第 4 段有重复，合并后保留差异化的论证部分 |

---

## Section 3: CRAFT Design（当前 1,870 词 + 1 图 + 2 表 + 伪代码）

**目标：~1,600 词，省 ~0.5 页。这是论文核心，尽量少砍。**

| 内容 | 操作 | 理由 |
|------|------|------|
| 3.1 Core Feedback Loop | ✅ 基本保留 | 论文精华，(a)(b)(c) 三条设计原则 + 伪代码全部保留 |
| Figure 4: feedback loop 示意图 | ✅ 保留 | 帮助理解核心机制 |
| 3.2 Implementation Refinements | ✂️ 压缩 | RS/RW/SD 三项细化各从 ~100 词压缩到 ~50 词，删掉冗余论证 |
| 3.3 Hardware Implementation | ✂️ 压缩 | Table 1（per-bank breakdown）保留；Table 2（对比表）保留但删掉 RL_PAGE 行和文字中对 RL_PAGE 的详细描述 |

**3.1 具体可压缩的点：**
- "Empirically, on benchmarks with strong row-level locality..." 这段经验数据可以删（评估部分会展示）
- "In contrast, INTAP employs the same [50, 3200] range but restricts..." 这段与 INTAP 的对比可压缩到一句话

**3.2 具体压缩方式：**
- RS：删除 "Without RS, a bank that transitions..." 这段反面论证（~40 词）
- RW：删除 "A read wrong precharge directly stalls..." 这段重复解释（Background Obs 2 已述）
- SD：已经很简洁，保持不变

---

## Section 4: Methodology（当前 832 词 + 2 表）

**目标：~700 词，省 ~0.25 页**

| 内容 | 操作 | 理由 |
|------|------|------|
| 4.1 Simulation Infrastructure + Table | ✅ 保留 | 必要 |
| 4.2 Workloads + Table | ✂️ 轻度压缩 | 三段描述（LIGRA/CRONO/SPEC）各保留 1-2 句；SNAP 图的详细参数（1.97M vertices, 2.77M edges...）移入表格而非正文 |
| 4.3 Baselines | ✅ 保留 | 已经很简洁 |
| 4.4 Metrics | ✂️ 压缩 | 四个 metric 各一句话定义即可，删掉解释性段落（如 "Since write requests are considered complete once cached in the write buffer..."） |

---

## Section 5: Evaluation（当前 2,378 词 + 3 图 + 4 表）

**目标：~1,500 词 + 2 图 + 2 表，省 ~2 页。这是最大的删减来源。**

### 5.1 IPC Performance

| 内容 | 操作 | 理由 |
|------|------|------|
| Table 3: Per-Benchmark IPC | ✅ 保留 | 核心结果表 |
| Figure 5: Normalized IPC bar chart | ✅ 保留 | 核心结果图 |
| 三类 workload 讨论 | ✂️ 压缩 | 每类从 ~120 词压缩到 ~60 词，删掉 timeout 分布数据（5.3 会讲） |

### 5.2 DRAM-Level Analysis — 大幅削减

| 内容 | 操作 | 理由 |
|------|------|------|
| 5.2.1 Read Row Buffer Hit Rate + Table 4 | ❌ 移除完整表 | 用一段文字总结（"CRAFT 在全部 12 个 benchmark 上 read hit rate 均最高，平均 +5.62pp"），不需要完整的 12 行表 |
| 5.2.2 Average Read Latency + Table 5 | ❌ 移除 | 一句话总结（"average read latency 降低 2.74%"）即可 |
| 5.2.3 Causal Chain + Figure 6 | ❌ 移除 | 因果链分析是 TACO 版本的亮点增量。APPT 版用 2-3 句话概括因果关系 |

**替代方案：** 将 5.2 三个小节合并为一段 ~150 词的 "DRAM-Level Verification"，引用关键数据点但不列完整表。

### 5.3 Timeout Behavior Analysis

| 内容 | 操作 | 理由 |
|------|------|------|
| 5.3.1 Timeout Accuracy | ❌ 移除 | "低准确率仍有高 IPC" 的 insight 很好，但属于锦上添花，留给 TACO |
| 5.3.2 Timeout Distribution + Figure 7 | ✅ 保留 | 三种自适应模式是 CRAFT 自适应能力的直接证据，必须保留 |
| "同一算法不同输入" 对比讨论 | ✅ 保留 | 论证 CRAFT 捕捉的是运行时模式而非算法类型 |

### 5.4 Ablation Study

| 内容 | 操作 | 理由 |
|------|------|------|
| Table 6 + 四条论证 | ✂️ 轻度压缩 | 表保留，四条论证各压缩到 2-3 句。"RW 在 49/62 个 benchmark 上获胜" 等细节删除 |

---

## Section 6: Discussion（当前 625 词）

**❌ 整节移除，省 ~1 页**

| 内容 | 操作 | 理由 |
|------|------|------|
| 6.1 Why Direct Feedback Suffices | ❌ 移除 | PID controller 类比留给 TACO，APPT 版在 ablation 讨论中一句带过 |
| 6.2 Limitations | ❌ 移除 | 纯随机 / 纯顺序的极端情况、单核局限性，留给 TACO |
| 6.3 Orthogonality | ❌ 移除 | 正交性论证在 APPT 版可以在 conclusion 中加一句 |

---

## Section 7: Related Work（当前 1,424 词）

**目标：~450 词，省 ~2 页**

| 内容 | 操作 | 理由 |
|------|------|------|
| Static policies & address mapping 段 | ✂️ 压到 2-3 句 | 保留 Minimalist Open-page 引用，删除 PARBLO 详述 |
| Predictor-based 段 | ✂️ 压到 3-4 句 | 只保留 ABP、HAPPY 的一句话定位 + CRAFT 的差异化。删除 Park+03、Stankovic+05、Xu+09、RBPP 的详细描述 |
| Timeout-based 段 | ✂️ 压到 2-3 句 | 只保留 INTAP + Srikanth+18 的一句话对比 |
| Learning-based 段 | ✂️ 压到 2-3 句 | RL_PAGE 一句话 + DYMPL 一句话（已在 Background 详述） + FAPS-3D 删除 |
| Application-aware 段 | ❌ 移除 | 非核心对比 |
| DRAM architectural modifications 段 | ❌ 移除 | 完全不同层次的工作，一句 "orthogonal to DRAM device modifications" 放 conclusion 即可 |

---

## Section 8: Conclusion（当前 203 词）

**目标：~180 词，基本保留**

| 内容 | 操作 | 理由 |
|------|------|------|
| 全文 | ✂️ 微调 | 加一句正交性声明（从 Discussion 6.3 提取），其余基本不变 |

---

## 图表汇总

### APPT 版本保留的图（5 张）

| 编号 | 内容 | 来源 |
|------|------|------|
| Fig 1 | Open vs Close IPC 对比 | intro / motivation_open_vs_close |
| Fig 2 | Phase RBH 变化（4 bench） | intro / phase_rbh_4bench |
| Fig 3 | DRAM timing diagram + 三种 outcome | background / timing_diagram |
| Fig 4 | CRAFT feedback loop 示意图 | design / feedback_loop |
| Fig 5 | Normalized IPC bar chart | evaluation / normalized_ipc |
| Fig 6 | Timeout distribution | evaluation / timeout_distribution |

> 注：实际 6 张图。如果篇幅仍然超，Figure 2（phase RBH）是最优先的裁剪候选。

### APPT 版本保留的表（5–6 张）

| 编号 | 内容 | 来源 |
|------|------|------|
| Tab 1 | Baseline 对比（机制/开销/局限） | background |
| Tab 2 | Simulation Configuration | methodology |
| Tab 3 | Benchmark Suite | methodology |
| Tab 4 | Per-Benchmark IPC Improvement | evaluation 5.1 |
| Tab 5 | CRAFT Per-Bank Storage Breakdown | design 3.3 |
| Tab 6 | Hardware Overhead Comparison | design 3.3 |
| Tab 7 | Ablation Study | evaluation 5.4 |

> 注：Tab 5 和 Tab 6 可以合并为一张表节省空间。

### 移除的图（留给 TACO）

| 图 | 理由 |
|----|------|
| Per-bank RBH（intro Fig 3） | 用文字数据点替代 |
| Policy spectrum | 概念直观，文字描述足够 |
| Causal chain 三列图 | TACO 亮点增量 |

### 移除的表（留给 TACO）

| 表 | 理由 |
|----|------|
| Read Row Buffer Hit Rate 完整表 | 用文字总结替代 |
| Average Read Latency 完整表 | 用文字总结替代 |

---

## 给 TACO 留下的增量清单

以下内容从 APPT 版本中移除，构成 TACO 扩展版的 30%+ 新材料基础：

1. **Figure: per-bank RBH heterogeneity**（完整三子图 + CoV 分析）
2. **Figure: policy spectrum 示意图**
3. **Section 5.2 完整版**：Read hit rate 完整表 + Read latency 完整表 + 因果链图 + 讨论
4. **Section 5.3.1 Timeout Accuracy**：84.7% 整体准确率 + "低准确率高 IPC" paradox 分析
5. **Section 6 Discussion 全文**：PID 类比、局限性分析、正交性论证
6. **Related Work 扩展段落**：predictor 详细谱系、DRAM arch modifications、application-aware
7. **Observation 2 完整数据论证**：62 benchmark 的 R/W 分布统计

**额外建议 TACO 版本新增（非简单恢复的内容）：**
8. 扩展到 62 个 benchmark 的完整结果（当前 APPT/TACO 共用 12 个）
9. 参数敏感性实验（BASE_STEP、T_MAX、SHIFT_CAP）
10. 多核场景的初步实验（如果时间允许）
11. 与 Srikanth+18 scoreboard 方案的直接实验对比（当前只有文字对比）

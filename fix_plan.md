# craft_appt.md 修复方案（已确认）

基于 `craft_appt_review.md` 和 `review_comments.md` 两份审阅意见，结合作者反馈后的最终修复方案。

---

## 一、最高优先级

### 1. 统一 precharge outcome 定义（3 种 vs 4 种）

- Section 2.1 末尾显式声明：row buffer hit 不涉及 precharge 事件，CRAFT 的 feedback loop 仅关注前三种 precharge outcome
- Abstract："four possible outcomes" → 先说 four outcomes，再明确 CRAFT 仅关注涉及 precharge 的三种
- Introduction："three possible outcomes" 保持不变
- Algorithm 1、Figure 4 caption：统一使用 "three precharge outcomes"

### 2. 弱化过强结论措辞

| 当前措辞 | 修改为 | 位置 |
|---------|--------|------|
| `complete and sufficient feedback basis` | `sufficient feedback basis in our evaluated setting` | Abstract 末句 |
| `unambiguous feedback signal` | `direct feedback signal` | Sec 3.1 |
| `genuinely adaptive` | `effectively adaptive` | Sec 5.3 |
| `dominant contributor` | `primary contributor` | Sec 5.4 |
| `entirely from the read path` | `primarily from the read path` | Sec 5.2 |
| `provides sufficient knowledge` | `provides sufficient information in our evaluated setting` | Conclusion |
| `orthogonal to and combinable with` | `we expect CRAFT to be compatible with` | Conclusion |
| `Conflict-path signals are detrimental` | `Conflict-path signals did not improve performance` | Sec 5.4 |
| `CRAFT outperforms every baseline on every benchmark` | 保留一次（Evaluation），其余改为定性描述 | 共出现3次 |

### 3. 修正 "62 benchmarks"

删除 "Across 62 benchmarks" 及相关数字，改为基于 12 个 workload 的机制性说明："Read wrong precharges directly stall the processor pipeline. Write wrong precharges are absorbed by the write buffer. Read operations account for the majority of wrong precharge events in our evaluated workloads."

### 4. 新增 Limitations Section（精简）

在 Related Work 之后、Conclusion 之前插入极简 Limitations section（3-5句），覆盖：
- 单核评估，多核 bank contention 待验证
- DDR5-4800 specific，cost ratio 随 timing 变化
- 12 个 workload，graph 占比偏重
- 未含能耗分析

### 5. 澄清 Ablation 变体命名

Section 5.4 开头添加变体定义表格，展开 PR (Phase Reset) 和 QDSD (Queue-Depth Scaled De-escalation) 全称。强调 PRECHARGE→ALL 的性能下降（131.9%→120.8%）为核心发现。

---

## 二、中等优先级

### 6. 2:1 cost ratio 处理

**不提升为独立小节。** 保留在 Section 2.2 现有位置。在 Section 3.1 中强调通用公式 (tRP + tRCD) / tRP，标注 2:1 是 DDR5-4800 的具体实例（tRP = tRCD 时成立）。timing 敏感性在 Limitations 中提及。

### 7. 统一 benchmark/workload 口径

全文 "benchmarks" → "workloads"（指代 12 个评估对象时）。Methodology 中说明 "12 benchmark-input pairs selected to cover diverse memory access behaviors"。

### 8. 统一 workload 分类标签

在 Table 4 中增加 "Category" 列，标注 Graph traversal / Graph analysis / Scientific computing。

### 9. 减少关键数字的重复

- Abstract、Evaluation：保留精确数字
- Introduction 正文：改为定性描述
- Contribution 4：精简，不重复具体百分比
- Conclusion：保留精确数字

### 10. 解释 BASE_STEP = 50 的设计依据

Section 3.1(a) 补充：BASE_STEP = 50 cycles 略大于 tRP（40 cycles），确保每次 escalation 产生可观测的 timeout 变化。同时说明 T_MIN 和 T_MAX 的选择依据。

### 11. 补充 runaway escalation 防护说明

Section 3.1(a) 末尾加："T_MAX bounds this upward bias. Conflicts and right-streak de-escalation provide downward pressure to restore balance."

---

## 三、较低优先级

### 12. 写作规范调整

- 从句：放宽限制，不再全面禁止，但避免滥用
- Em-dash（—）：**严格禁止**，替换为句号、逗号或括号
- 自创术语：**严格禁止**，首次出现时必须定义或使用已有术语
- 同步更新 CLAUDE.md 中的写作规范

### 13. 重命名两个 Section 标题

- Section 3.2 "Implementation Refinements" → "Precharge-Path Refinements"
- Section 5.2 "DRAM-Level Verification" → "DRAM-Level Performance Analysis"

### 14. 消除 Section 5.1 中的 timeout 前向引用

将 timeout distribution 相关分析移至 Section 5.3，Section 5.1 聚焦 IPC 结果和高层原因。

### 15. Conclusion 增加前瞻性段落

Conclusion 中合并部分局限性讨论，以 future work 框架呈现（LPDDR/HBM 适用性、多核扩展、scheduling 结合等），替代独立的 limitation 段落。

### 16. 其他小修

- Section 3.3：补充 16-bit row address 来源（2^16 = 65,536 rows per bank）
- Section 4.3："A detailed discussion ... is provided in Section 6" → "Section 6 discusses these approaches in the broader context of prior work"
- Algorithm 1：为 right_streak 添加注释指向 Section 3.2(a)
- Section 4.2：补充 SimPoint 80M instruction interval 的合理性说明
- Section 5.3：简要说明 timeout 三段分类边界选择依据

---

## 修改顺序

1. **第一轮（定义与结构）：** #1 outcome 定义统一 → #4 新增 Limitations → #5 Ablation 变体表
2. **第二轮（口径与命名）：** #3 修正 62 benchmarks → #7 benchmark/workload 统一 → #8 分类标签 → #10 BASE_STEP 依据 → #11 runaway 防护
3. **第三轮（措辞与风格）：** #2 弱化措辞 → #6 cost ratio 限定 → #9 减少数字重复 → #12 写作规范 → #13-16 小修

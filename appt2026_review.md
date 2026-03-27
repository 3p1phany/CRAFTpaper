# CRAFT 论文审稿意见（APPT 2026）

**总体评分：Weak Accept（边缘接收）**

---

## Summary

本文提出 CRAFT，一种基于预充电代价非对称性的自适应 DRAM 行缓冲管理方案。核心洞察是 wrong precharge 和 conflict 两种失败模式产生本质上不同的资源浪费，因此应采用非对称步长调整超时值。CRAFT 包含一个核心反馈循环和三个 precharge-path 细化（RS/RW/SD），硬件开销仅 140 B/channel。在 12 个内存密集型单核负载上，CRAFT 相对 ABP/DYMPL/INTAP 分别取得 +7.73%/+3.10%/+2.84% IPC 提升。

---

## Strengths

**S1. 核心洞察清晰且具有物理意义**
Section 3.1 的代价分析基础扎实：wrong precharge 浪费 tRP + tRCD，而 conflict 的不可避免代价使控制器仅损失 tRP 的重叠机会。这一比率 2:1 直接映射到步长设计，逻辑自洽。

**S2. 硬件开销极低**
140 B/channel（35 bits/bank × 32 banks）是同类方案中最低的，相比 ABP（~20 KB）和 DYMPL（3.39 KB）有压倒性优势。Table 2 的存储分解清晰透明。

**S3. 消融实验设计严谨**
Section 5.4 的消融研究（8 个变体）是本文最强的部分。BASE 贡献 76% 增益，PRECHARGE 达到 131.9%，而 conflict-path 信号（PR/QDSD）反而有害——这种负面结果被如实呈现，增强了论文可信度。

**S4. 写作结构清晰**
论文结构完整，Background 与 Design 的逻辑衔接自然，Algorithm 1 的伪代码与文字描述一致。

---

## Major Concerns

**W1. 仅评估单核场景**

论文仅在单核配置下评估。多核场景下，多线程对同一 bank 的并发访问会引发线程间 bank 争用（inter-thread bank contention），破坏 per-bank 反馈信号的纯洁性：一个核的 wrong precharge 可能由另一个核的访问触发，而非本核局部性变化。

结论中虽然提到这一限制，但仅在最后一段一笔带过。对于一篇以"per-bank adaptive"为核心卖点的论文，缺少多核评估使普适性声明缺乏支撑。建议至少补充 2–4 核配置的初步结果，哪怕作为附加数据。

**W2. 工作负载覆盖范围过窄**

12 个负载全部来自图分析（LIGRA/CRONO）和科学计算（SPEC CPU2006 的 sphinx3/wrf），均属内存密集型。存在以下问题：

- SPEC CPU2006 仅选 2 个负载，且 CPU2006 已于 2006 年发布，代表性不足；CPU2017 或 PARSEC 更符合当前标准
- 无数据库类负载、无计算密集型负载作为对照
- 现有负载集明显偏向高 row buffer hit rate 场景，有利于 CRAFT

结论中"consistently outperforms all baselines"的说法在如此同质的负载集上过于强烈。

**W3. 与 INTAP 的改进幅度偏小，且消融分析未彻底隔离非对称步长的独立贡献**

CRAFT 相对 INTAP（最近似的对照）的提升仅为 +2.84% geomean。两者硬件开销相近（140 B vs ~200 B），改进幅度与存储节省不对称。

更重要的是，消融实验的 BASE 变体同时包含"非对称步长"和"指数退避"两个设计，缺少一个"对称步长 + 指数退避"的控制变体来单独验证非对称步长的贡献。这是论文核心 claim 的关键实验，缺失使核心论点的实验依据不充分。

**W4. 参数敏感性分析缺失**

论文固定了多个关键参数：BASE_STEP = 50 cycles，T_MIN = 50，T_MAX = 3200，SHIFT_CAP = 8，RS 触发阈值 = 4。这些参数均针对 DDR5-4800（tRP = tRCD = 40 cycles）调优，论文本身也承认 2:1 的步长比率依赖于 tRP = tRCD 这一条件。

- 对于 tRP ≠ tRCD 的 DRAM 标准（如 DDR4）如何重新推导参数？
- BASE_STEP 选为"略大于 tRP"的 50 cycles 是如何确定的？
- 无任何参数敏感性图表

这对方案的可移植性构成疑问。

---

## Minor Concerns

**W5.** Figure 4 的 x 轴 benchmark 名称因字体过小、角度旋转后严重重叠，印刷版本几乎无法辨认。

**W6.** 仅报告 IPC、hit rate、latency 三个维度，未分析 DRAM 能耗。更长的 timeout 意味着行开放时间更长，在 refresh 密集的使用场景下可能引发能耗增加。

**W7.** 仅评估 rorababgchco 一种地址映射。地址映射对 row buffer conflict 频率影响显著，不同映射下 CRAFT 的行为可能差异较大。

**W8.** Contribution 3（"conflict-path signals do not improve performance"）本质上是一个负面结果。将负面结果作为 contribution 呈现是合理的，但论文对其价值的阐述偏弱——目前仅说"the three-way outcome classification is sufficient"，而没有解释为什么 Phase Reset / Queue-Depth 信号引入噪声，理论解释不足。

---

## Questions for Authors

1. 在 2–4 核多程序工作负载下，per-bank timeout 是否会因线程间干扰而产生误导性的反馈信号？是否有初步数据？

2. 为何不选用 SPEC CPU2017 作为科学计算基准？当前仅使用两个 2006 年的负载令人疑虑。

3. 能否补充一个"对称指数退避"对照实验（即 BASE 中将 conflict 步长也改为与 wrong precharge 相同的 BASE_STEP × 2^streak），以直接量化非对称步长的贡献？

4. 对于 tRP ≠ tRCD 的 DRAM 标准（如 DDR4-3200），步长比率如何重新计算？设计是否需要运行时参数配置？

5. RS 触发阈值设为 4 的选取依据是什么？

---

## Recommendation

**Weak Accept，需要修订**

论文核心洞察真实有效，硬件开销优势突出，消融实验诚实，写作质量较好。但单核评估的局限性、工作负载覆盖不足、以及缺少隔离非对称步长贡献的对照实验，是影响论文说服力的实质性问题。若作者能补充多核初步结果、扩充工作负载（尤其是 SPEC CPU2017）并增加非对称步长的孤立对照实验，论文接收把握将大幅提升。

---

## 补充：审稿后发现的实现 Bug（已修复）

**Algorithm 1 pseudocode 结构错误（已于 2026-03-26 修复）**

原 pseudocode 将 conflict 分支嵌套在 `if prev_closed_by_timeout` 内部：

```
On each bank ACT event:
  if prev_closed_by_timeout:
    if new_row = prev_row:       → Wrong precharge
    else:
      if was_ondemand_precharge: → Conflict  ← 语义不可达
      else:                      → Right precharge
```

这与 Background Section 2 的定义矛盾：conflict 定义为"timeout 尚未到期时新请求触发 on-demand precharge"，即 `prev_closed_by_timeout = false` 时发生。将其嵌套在 `prev_closed_by_timeout = true` 的分支内导致该路径永远不可达。

正确结构为两个独立的事件处理器：

```
On each incoming bank request (while timeout active):
  if new_row ≠ open_row:          → Conflict: de-escalate

On each bank ACT event (following timeout precharge):
  if prev_closed_by_timeout:
    if new_row = prev_row:        → Wrong precharge: escalate
    else:                         → Right precharge: no action
```

已修复 `samplepaper.tex` 中的 Algorithm 1 及 Section 3.1 第一句描述。

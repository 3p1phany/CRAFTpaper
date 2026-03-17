# CRAFT: Exploiting Precharge Cost Asymmetry for Adaptive DRAM Row Buffer Management

## 1. Introduction (1.5 pages)

### 1.1 问题陈述（3 段）

**第 1 段：Row buffer 管理的根本矛盾**

- Open-page 利于行局部性（row buffer hit 仅需 tCAS），利用row buffer的reuse来提高访问DRAM芯片的性能。Close-page 利于 bank 并行性（避免 conflict penalty = tRP + tRCD），让active的bank尽快回到idle状态以服务新的targeting different rows的访存请求
- 没有普适最优策略：工作负载的行级访问模式在不同程序、不同执行阶段、甚至不同 bank 之间差异巨大
- 【TODO】 Fig 不同程序之间open page和close page的性能对比
- 【TODO】 Fig 一个程序的不同阶段之间的row  hit rate的对比
- 【TODO】 Fig 一个程序的不同bank之间的row hit rate对比

**第 2 段：现有自适应方案的"复杂度-有效性"困境**

- ABP：per-row 预测表 ~20 KB/channel
- DYMPL：7-feature perceptron + 512-entry PRT = 3.39 KB/channel，关键路径 7 次查表 + 6 次加法
- INTAP：硬件轻量 ~200 B，但对称固定步长、无代价感知
- 一句话总结：要么硬件太重，要么适应不精确

**第 3 段：CRAFT 的核心洞察**

- Timeout precharge 的三种结果天然编码不对称代价：conflict (tRP+tRCD) >  wrong (tRCD) > right (0)
- 这种代价不对称性可直接驱动 timeout 调整方向和步长——无需预测表、无需学习模型
- CRAFT 用 140 B/channel 实现了 3.4 KB 感知机方案做不到的性能

### 1.2 贡献列表

1. 提出 CRAFT 核心反馈循环：代价驱动不对称步长 + 指数退避 + 连续 timeout 范围
2. 实证发现 precharge-path 反馈信号可有效细化 timeout 调整，而 conflict-path 信号反而有害——验证了核心循环的信号选择原则
3. 在 memory-intensive benchmark 上评估：vs ABP/DYMPL/INTAP 分别 +7.73%/+3.10%/+2.84% GEOMEAN IPC，硬件开销 140 B/channel

---

## 2. Background & Motivation (1.5 pages)

### 2.1 DRAM Row Buffer 基础（0.5 page）

**内容**：用一张时序图解释以下概念

- Row buffer hit: 直接读取，延迟 = tCAS
- Row buffer miss (closed): 先 ACT 再读，延迟 = tRCD + tCAS
- Row buffer conflict (open, wrong row): 先 PRE 再 ACT 再读，延迟 = tRP + tRCD + tCAS
- Timeout-based speculative precharge：行空闲超时后主动关闭，三种结果的定义

【TODO】Fig DRAM row buffer 状态转换与三种 precharge outcome 的时序图

### 2.2 现有方案的局限（0.5 page）

**数据来源**：`/root/data/smartPRE/docs/analysis/storage_overhead_comparison.md`

用一张表对比三个 baseline 的机制和开销：

| 方案  | 决策机制                    | 存储 /ch | 关键路径计算    | 核心局限               |
| ----- | --------------------------- | -------- | --------------- | ---------------------- |
| ABP   | Per-row access count 预测表 | ~20 KB   | 查表+比较       | 存储过大；per-row 粒度 |
| DYMPL | 7-feature perceptron + PRT  | 3.39 KB  | 7 查表 + 6 加法 | PRT 占 86.6%；计算复杂 |
| INTAP | Mistake counter + 固定步长  | ~200 B   | 1 比较 + 1 加法 | 无代价感知；对称调整   |

### 2.3 Motivation：代价不对称性被忽视（0.5 page）

**论点 1：Wrong precharge 与 conflict 的代价不同，但 INTAP 对两者使用相同步长调整**

- Wrong 代价 = tRP + tRCD = 80 cycles（DDR5-4800）
- Conflict 代价 = tRP = 40 cycles
- INTAP 的 mistake counter 不区分这两种错误类型

**论点 2：Read/write wrong precharge 的代价不同，但所有方案一视同仁**

- 数据支撑（来自 `/root/data/smartPRE/docs/analysis/craft_rw_motivation_analysis.md`）：
  - Wrong precharge 中 read 占 80.3%，write 仅占 19.7%（全局 R/W = 4.1x）
  - Read wrong 直接 stall CPU core；write wrong 被 write buffer 吸收
  - 这种比例在不同 workload 之间差异显著（如 PageRank/higgs 中 read wrong 占比高达 99.8%）

**论点 3：Precharge 结果本身就是最直接的反馈信号**

- DYMPL 需要提取 7 种间接特征（页面利用率、热度、时间局部性等）来预测行为
- 但 precharge 是否正确的结果已经直接回答了"timeout 该不该调"——无需间接估计

---

## 3. CRAFT Design (2.5 pages)

### 3.1 Core Feedback Loop（1 page）

**算法描述**（伪代码或流程图）：

```
On each bank ACT event:
  if prev_closed_by_timeout:
    if new_row == prev_row:          // Wrong precharge
      step = BASE_STEP << min(reopen_streak, SHIFT_CAP)
      timeout += step                // Escalation
      reopen_streak = min(reopen_streak+1, 7)
      right_streak = 0
    else:
      if was_ondemand_precharge:     // Conflict
        step = BASE_STEP * tRP / (tRP + tRCD)
        timeout -= step              // De-escalation
        reopen_streak = 0
        right_streak = 0
      else:                          // Right precharge
        reopen_streak = 0
        right_streak++
    timeout = clamp(timeout, T_MIN, T_MAX)
```

**设计原则（逐条论证）**：

**(a) 代价驱动不对称步长**

- Conflict 代价 (tRP+tRCD) 是 Wrong 代价 (tRP) 的 2 倍 → escalation 基础步长 > de-escalation 基础步长
- conflict_step = BASE_STEP × tRP/(tRP+tRCD) = 50 × 40/80 = 25 cycles

**(b) 指数退避**

- `reopen_streak` 追踪连续 wrong 次数，步长 = BASE_STEP × 2^streak
- 作用：高局部性阶段 timeout 快速收敛到高值（2-3 次 wrong 即可大幅拉高），避免反复振荡
- 数据支撑（来自 `/root/data/smartPRE/docs/analysis/craft_timeout_distribution_analysis.md`）：
  - roadNet-CA 系列 benchmark 90%+ 时间 timeout 处于 High [2000-3200] 区间，说明指数退避成功将 timeout 推到高位并稳定

**(c) 连续调整范围 [50, 3200]**

- 相比 INTAP 的同范围但固定步长 50，CRAFT 的步长随 streak 指数变化，适应速度和稳定性兼备

【TODO】Fig  — CRAFT 反馈循环示意图（状态转换 + 步长计算）

### 3.2 实现细化（0.5 page）

核心反馈循环已提供主要的自适应能力。以下三项细化针对 precharge-path 信息进一步提升 timeout 调整精度，均不引入额外硬件复杂度：

**(a) Right Streak De-escalation (RS)**：连续 ≥4 次 right precharge 后以 conflict_step/2 温和降低 timeout，防止 timeout 在离开高局部性阶段后冻结在高位。硬件开销：3 bits/bank。

**(b) Read/Write Cost Differentiation (RW)**：Write wrong precharge 被 write buffer 缓冲，实际代价低于 read wrong。据此，write wrong 时 escalation 步长减半，read conflict 时 de-escalation 步长加倍。硬件开销：0 bits（复用 cmd_type）。

**(c) Streak Decay (SD)**：每次 right precharge 时 reopen_streak -= 1（下限 0），避免历史 streak 值导致未来 escalation 步长过大。硬件开销：0 bits。

设计选择的验证见 Section 5.4：上述三项 precharge-path 细化组合后可进一步提升性能，而 conflict-path 方向的调整（phase reset、queue-depth scaling）反而干扰核心循环，验证了 precharge outcome 是最直接有效的反馈信号来源。

### 3.3 Hardware Implementation（0.25 page）

**数据来源**：`/root/data/smartPRE/docs/analysis/storage_overhead_comparison.md`

Per-bank 状态：

| 字段                       | 位宽              | 说明            |
| -------------------------- | ----------------- | --------------- |
| timeout_value              | 12 bits           | [50-3200]       |
| reopen_streak              | 3 bits            | 指数退避 [0-7]  |
| right_streak               | 3 bits            | RS 计数器 [0-7] |
| prev_row                   | 16 bits           | 行地址          |
| prev_closed_by_timeout     | 1 bit             | 标志位          |
| **Per-bank**         | **35 bits** |                 |
| **32 banks/channel** | **140 B**   |                 |

开销对比表：

| 方案            | 存储 /ch        | 特殊硬件                | 关键路径                  |
| --------------- | --------------- | ----------------------- | ------------------------- |
| **CRAFT** | **140 B** | **无**            | **1 比较 + 1 加法** |
| INTAP           | ~200 B          | 无                      | 1 比较 + 1 加法           |
| ABP             | ~20 KB          | Set-assoc table         | 查表                      |
| DYMPL           | 3.39 KB         | 512-entry set-assoc PRT | 7 查表 + 6 加法           |
| RL_PAGE         | 4.14 KB         | 4KB SRAM + 哈希         | 16 哈希 + 乘法            |

---

## 4. Methodology (1 page)

### 4.1 Simulation Infrastructure

- ChampSim cycle-level OoO CPU simulator + DRAMSim3 cycle-accurate DRAM simulator
- Co-simulation：ChampSim 的 memory request 通过 `dramsim3_wrapper` 传递给 DRAMSim3，DRAM 返回完成回调
- DDR5-4800 配置：4 channels, 1 rank/ch, 8 bank groups × 4 banks = 32 banks/ch
- Core 配置：引用 `/root/data/smartPRE/champsim-la/champsim_config.json` 中的参数（ROB size, issue width, cache hierarchy）

### 4.2 Workloads

- Memory-intensive benchmark：图处理（LIGRA, CRONO）、科学计算（SPEC CPU2006）
- 这些 workload 对 row buffer 管理策略高度敏感
- 涵盖三类典型访存模式：
  - 图遍历（CF, PageRank, BFSCC, Components-Shortcut）：phase change 剧烈
  - 图分析（Triangle, Triangle-Counting, Radii）：混合局部性
  - 科学计算（sphinx3, wrf）：stencil 规律性行重访

### 4.3 Baselines

- **ABP** (Awasthi et al., ISCA 2011)：Per-row access-based predictor
- **DYMPL** (Rafique & Zhu, TACO 2022)：7-feature perceptron + PRT
- **INTAP**：Intel adaptive timeout, mistake counter + 固定步长

### 4.4 Metrics

- **IPC** (Instructions Per Cycle)：主指标
- **Read Row Buffer Hit Rate**：DRAM 层面验证
- **Average Read Latency**：DRAM 层面验证
- **Timeout Precharge Accuracy**：机制有效性验证

---

## 5. Evaluation (3 pages)

### 5.1 IPC Performance（1 page）

**数据来源**：`/root/data/smartPRE/docs/experiments/craft_final_evaluation.md`

**Table: Per-Benchmark IPC Improvement**

| #  | Benchmark                           | vs ABP           | vs DYMPL         | vs INTAP         |
| -- | ----------------------------------- | ---------------- | ---------------- | ---------------- |
| 1  | ligra/CF/roadNet-CA                 | +12.20%          | +5.81%           | +5.79%           |
| 2  | ligra/CF/higgs                      | +7.67%           | +5.67%           | +3.10%           |
| 3  | ligra/PageRank/higgs                | +8.14%           | +3.73%           | +2.87%           |
| 4  | ligra/BFSCC/soc-pokec-short         | +7.12%           | +2.85%           | +5.33%           |
| 5  | spec06/sphinx3/ref                  | +10.28%          | +2.60%           | +3.78%           |
| 6  | ligra/CF/soc-pokec                  | +3.89%           | +3.10%           | +2.02%           |
| 7  | ligra/Triangle/roadNet-CA           | +8.12%           | +2.00%           | +3.65%           |
| 8  | ligra/PageRank/roadNet-CA           | +11.56%          | +2.71%           | +1.89%           |
| 9  | crono/Triangle-Counting/roadNet-CA  | +7.97%           | +2.78%           | +1.74%           |
| 10 | spec06/wrf/ref                      | +8.19%           | +1.65%           | +1.72%           |
| 11 | ligra/Components-Shortcut/soc-pokec | +8.47%           | +1.95%           | +1.63%           |
| 12 | ligra/Radii/higgs                   | +5.48%           | +1.61%           | +1.97%           |
|    | **GEOMEAN**                   | **+7.73%** | **+3.10%** | **+2.84%** |

**Figure: Normalized IPC Bar Chart**（CRAFT = 1.0）

- 数据：GEOMEAN ABP=0.928, DYMPL=0.970, INTAP=0.972, CRAFT=1.000
- 来源：`/root/data/smartPRE/docs/experiments/craft_final_evaluation.md` Normalized IPC 表
- 生成脚本：`/root/data/smartPRE/champsim-la/scripts/plot_craft_vs_baselines.py`

**按 workload 类别讨论**（每类 1 段）：

- **图遍历** (CF, PageRank, BFSCC, Components-Shortcut)：

  - 图遍历存在 phase change（探索→收敛），行局部性剧烈变化
  - CRAFT 指数退避快速跟踪：roadNet 图上 timeout 收敛到 High 85-92%（`/root/data/smartPRE/docs/analysis/craft_timeout_distribution_analysis.md`）
  - vs ABP 提升最大（+7-12%），ABP 的 per-row 预测表无法适应快速 phase change
- **图分析** (Triangle, Radii)：

  - 混合局部性，不同 bank 行为差异大
  - CRAFT per-bank 自适应精准匹配——CF/higgs 的 timeout 分布均衡分散（Low 35.7%, Mid 38.0%, High 26.3%）
- **科学计算** (sphinx3, wrf)：

  - Stencil 模式下行局部性随计算阶段变化
  - CRAFT timeout 收敛到 High 75%/57%（sphinx3/wrf），正确保持高局部性阶段的 row buffer open

### 5.2 DRAM-Level Analysis（1 page）

**5.2.1 Read Row Buffer Hit Rate**

**数据来源**：`/root/data/smartPRE/docs/analysis/row_buffer_hit_rate_analysis.md` 的Section 1

| #   | Benchmark      | CRAFT  | ABP    | DYMPL  | INTAP  | vs Best BL        |
| --- | -------------- | ------ | ------ | ------ | ------ | ----------------- |
| 1   | CF/roadNet-CA  | 91.15% | 72.13% | 81.90% | 81.56% | +9.25pp           |
| 5   | sphinx3        | 87.85% | 53.21% | 80.09% | 76.17% | +7.76pp           |
| 8   | PR/roadNet-CA  | 83.97% | 47.47% | 74.83% | 74.85% | +9.12pp           |
| ... |                |        |        |        |        |                   |
|     | **平均** |        |        |        |        | **+5.62pp** |

论证要点：

- CRAFT 在全部 12 个 benchmark 上 read hit rate 均高于最优 baseline，平均 +5.62pp
- Write hit rate 四种策略几乎无差异（< 1pp），性能优势**完全来自读路径**
- 这与 CRAFT 的代价驱动设计一致：核心循环对读路径的 conflict 更积极降 timeout，使 row buffer 对读请求保持更长开放

**5.2.2 Average Read Latency**

**数据来源**：`/root/data/smartPRE/docs/analysis/row_buffer_hit_rate_analysis.md` Section 4

| # | Benchmark      | CRAFT | Best BL | 降幅             |
| - | -------------- | ----- | ------- | ---------------- |
| 1 | CF/roadNet-CA  | 95.32 | 101.04  | -5.66%           |
| 5 | sphinx3        | 82.31 | 87.43   | -5.86%           |
| 8 | PR/roadNet-CA  | 79.15 | 83.58   | -5.29%           |
|   | **平均** |       |         | **-2.74%** |

**5.2.3 因果链（关键图表）**

**数据来源**：`/root/data/smartPRE/docs/analysis/row_buffer_hit_rate_analysis.md` Section 6

**Figure: 因果链三列对比图**（Read HR 提升 → 延迟降低 → IPC 提升）

- 三组柱状图并列，12 个 benchmark
- 数据：平均 +5.62pp read HR → -2.74% latency → +2.48% IPC
- 论证：IPC 提升完全可归因于 DRAM 层面的 row buffer 命中率提升

### 5.3 Timeout Behavior Analysis（0.5 page）

**5.3.1 Timeout Accuracy**

**数据来源**：`/root/data/smartPRE/docs/analysis/craft_timeout_accuracy.md`

- 12 个选定 benchmark 的 timeout 准确率（correct/total）：合计 **84.7%**
- 准确率分布展示反馈循环有效收敛
- 关键发现：低准确率 benchmark (roadNet-CA 系列 32-47%) 仍获得最大 IPC 提升 (+1.9-5.8%)
  - 原因：escalation 比 de-escalation 多 → 反馈循环学习到需要长 timeout（倾向 open-page）
  - 这说明**即使预判经常出错，反馈循环的自纠错能力依然有效**

**5.3.2 Timeout Distribution — 三种自适应模式**

**数据来源**：`/root/data/smartPRE/docs/analysis/craft_timeout_distribution_analysis.md`

**Figure: Timeout Distribution Heatmap 或 Stacked Bar**

| 自适应模式       | 代表 benchmark | Low% | Mid% | High% | 含义                                |
| ---------------- | -------------- | ---- | ---- | ----- | ----------------------------------- |
| Aggressive Close | PageRank/higgs | 96.9 | 2.9  | 0.2   | 行局部性差 → 自动收敛到 close-page |
| Balanced         | CF/higgs       | 35.7 | 38.0 | 26.3  | bank 间异质性 → per-bank 分化      |
| Keep Open        | TriCnt/roadNet | 2.8  | 5.2  | 92.0  | 行局部性强 → 自动收敛到 open-page  |

关键论证：

- **同一算法在不同图上分布截然不同**：PageRank/roadNet High 90.9% vs PageRank/higgs Low 96.9%
  - → CRAFT 捕捉的是运行时实际的行级访问模式，不是算法类型
- **三种模式均带来正向 IPC 提升** → CRAFT 不是偏向某一种策略，而是真正的自适应

### 5.4 Ablation Study（0.5 page）

**数据来源**：`/root/data/smartPRE/docs/experiments/craft_final_evaluation.md`

消融实验验证核心反馈循环的主导作用，以及不同信号来源（precharge-path vs conflict-path）对性能的影响。

**Table: Ablation — 核心循环与细化组合对比**

| Variant   | 描述                | GEOMEAN vs INTAP | Δ vs BASE |
| --------- | ------------------- | ---------------- | ---------- |
| BASE      | 核心反馈循环        | +0.653%          | —         |
| PRECHARGE | BASE + RS/RW/SD     | +0.861%          | +0.208pp   |
| ALL       | PRECHARGE + PR/QDSD | +0.789%          | +0.136pp   |

论证要点：

- **核心循环贡献了绝大部分性能提升**：BASE 已实现最终 GEOMEAN 提升的 76%（0.653/0.861），表明代价不对称驱动的反馈机制本身即为关键设计
- **Precharge-path 信号可进一步细化调整**：三项细化（RS/RW/SD）在核心循环基础上额外提升 +0.21pp；在行为多样性较高的 benchmark 上效果更明显（PageRank/higgs +0.76%，CF/soc-pokec +0.49%）
- **Conflict-path 信号有害**：在 PRECHARGE 基础上加入 phase reset 和 queue-depth scaling 后，性能反降 0.072pp。Conflict event 的附加信息（发生阶段、队列深度）干扰了核心循环已有的自适应节奏
- **设计启示**：precharge outcome 的三种分类（right/wrong/conflict）已编码了充分的反馈信息，进一步细分 conflict event 弊大于利

---

## 6. Discussion (0.5 pages)

**为什么简单反馈循环有效**：

- Precharge 结果是最直接的反馈信号——类比 PID controller vs. model-predictive control
- ML-based 方案 (DYMPL) 需要通过间接特征估计行为，引入估计误差和训练开销
- CRAFT 直接用代价差异驱动，消除了中间环节

**局限场景**：

- 纯随机访问（RBH < 1%）：任何 timeout 策略等价于 closed-page，CRAFT 无优势

**多核扩展性**：

- Per-bank 状态，无 per-channel 共享结构，天然支持多核无竞争
- （注：目前只有单核结果。如有多核数据可补充在此。）

**正交性**：

- CRAFT 工作在 DRAM controller 层，与 prefetcher、cache replacement、memory scheduling 正交

---

## 7. Related Work (0.75 pages)

- **Static policies**: Open-page, closed-page, adaptive open/close (JEDEC)
- **Predictor-based**: ABP (Awasthi et al., ISCA 2011) per-row prediction; HAPPY (Ghasempour et al., 2016)
- **Timeout-based**: INTAP (Ghasempour et al., 2016) mistake counter + 固定步长
- **ML-based**: DYMPL (TACO 2022) perceptron; RL_PAGE (ISCA 2008) SARSA+CMAC; FAPS-3D (2019) FSM
- **CRAFT 定位**: 首个利用 precharge outcome 代价不对称性直接驱动连续 timeout 调整的方案

---

## 8. Conclusion (0.25 pages)

一段话总结：

- 核心洞察：precharge 结果的三种类型编码了不对称代价，可直接驱动 timeout 调整
- Precharge-path 细化可进一步提升精度，而 conflict-path 信号反而有害
- 结果：vs ABP/DYMPL/INTAP +7.73%/+3.10%/+2.84% GEOMEAN IPC
- 硬件：140 B/channel，无特殊结构，比 DYMPL 少 24.8x，比 RL_PAGE 少 30.3x

---

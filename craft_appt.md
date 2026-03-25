# CRAFT: Exploiting Precharge Cost Asymmetry for Adaptive DRAM Row Buffer Management

## Abstract

DRAM row buffer management involves a fundamental tradeoff between exploiting row-level locality and avoiding conflict penalties. Prior adaptive schemes exhibit a persistent tension between hardware complexity and adaptation quality. Per-row prediction tables require up to 20 KB of storage per channel. Perceptron-based classifiers require multi-feature inference on the critical path. Simpler timeout-based approaches lack cost awareness in their feedback mechanisms.

This paper presents CRAFT, Cost-driven Row-buffer Adaptive Feedback Timeout, a lightweight feedback-driven row buffer management scheme. CRAFT builds on the observation that the three possible outcomes of a timeout-based speculative precharge carry inherently asymmetric performance costs. A wrong precharge imposes a combined precharge and reactivation penalty. A conflict imposes only the precharge penalty. CRAFT translates this cost asymmetry into differentiated per-bank timeout adjustments. Wrong precharges escalate the timeout through exponential backoff. Conflicts de-escalate the timeout with a smaller, cost-proportional step. The mechanism requires no prediction tables, feature extraction, or learned models.

We evaluate CRAFT using cycle-accurate ChampSim–DRAMSim3 co-simulation on a DDR5-4800 configuration across 12 memory-intensive benchmarks. CRAFT achieves geometric mean IPC improvements of 7.73%, 3.10%, and 2.84% over ABP, DYMPL, and INTAP, respectively. CRAFT improves the average read row buffer hit rate by 5.62 percentage points over the best baseline and reduces average read latency by 2.74%. The total storage overhead is 140 bytes per channel. This represents a 24× reduction relative to DYMPL and over 140× reduction relative to ABP. An ablation study further demonstrates that feedback signals from precharge outcomes are sufficient for effective adaptation. Incorporating conflict-path heuristics degrades performance. These results confirm that the inherent cost asymmetry of precharge outcomes provides a complete feedback basis for row buffer management.

## 1. Introduction

Main memory latency remains a primary performance bottleneck in modern processor systems.
A critical factor governing this latency is how the memory controller manages the *row buffer* in each DRAM bank, the internal sense-amplifier array that caches the most recently activated row.
Holding a row open (the *open-page* policy) maximizes the chance of serving subsequent accesses to the same row at low latency, but risks expensive conflicts when a different row is potentially needed; closing immediately after each access (the *close-page* policy) eliminates such conflicts but forfeits all potential row locality.
This fundamental tradeoff makes row buffer management one of the most extensively studied yet persistently challenging aspects of memory controller design.

The optimal page policy varies across workloads, across execution phases, and even across individual banks.
Neither open-page nor close-page dominates across all benchmarks. Open-page loses up to 11% IPC on workloads with frequent row buffer conflicts. Close-page sacrifices up to 28% IPC on workloads with high row buffer locality (Figure 1).
Within a single execution, row buffer locality shifts dramatically between program phases. mcf transitions from above 90% hit rate to below 10%. PageRank follows the inverse trajectory (Figure 2).
Beyond temporal variation, row buffer locality also differs substantially across banks within a single channel. Under the open-page policy, omnetpp exhibits a per-bank row buffer hit rate coefficient of variation of 1.51, indicating pronounced inter-bank disparity.
These observations suggest that effective row buffer management should adapt per bank and per execution phase.

<img src="figures/output/motivation_open_vs_close.png" alt="Figure 1" width="100%">

**Figure 1.** Normalized IPC of open-page and close-page policies across 12 memory-intensive benchmarks, normalized to the better static policy per benchmark. Neither static policy dominates across all workloads.

<img src="figures/output/phase_rbh_4bench.png" alt="Figure 2" width="100%">

**Figure 2.** Row buffer hit rate across execution epochs under the open-page policy for four representative benchmarks. Each benchmark exhibits distinct phase transitions between high- and low-locality regimes.

Prior adaptive schemes face a persistent tradeoff between hardware complexity and adaptation quality.
ABP [Awasthi+11] requires approximately 20 KB per channel for per-row prediction tables.
DYMPL [Rafique+22] employs a perceptron classifier with 3.39 KB per channel and seven-feature inference on the critical path.
INTAP [Ghasemp+16] adjusts a per-bank timeout using approximately 200 bytes per channel. INTAP applies the same fixed step to both wrong precharges and conflicts despite their differing latency costs.

This paper presents CRAFT (**C**ost-driven **R**ow-buffer **A**daptive **F**eedback driven **T**imeout), a lightweight, feedback-driven row buffer management scheme. CRAFT builds on the observation that the three possible outcomes of a timeout-based speculative precharge, namely *right*, *wrong*, and *conflict*, carry inherently asymmetric performance costs.
A right precharge closes the row before a request to a different row arrives, incurring no wasted latency.
A wrong precharge closes the row prematurely, necessitating a re-activation when the same row is accessed again.
A conflict arises when the timeout has not yet expired and the open row blocks an arriving request to a different row.
Because a wrong precharge imposes a higher penalty than a conflict, CRAFT uses this cost asymmetry to drive differentiated timeout adjustments. Wrong precharges escalate the timeout value through exponentially increasing steps to preserve row locality. Conflicts de-escalate the timeout value with a smaller, cost-proportional step. This simple feedback mechanism requires no prediction tables, feature extraction, or learned models.
With only 140 bytes of state storage per channel, CRAFT outperforms all three baselines. CRAFT achieves geometric mean IPC improvements of 7.73%, 3.10%, and 2.84% over ABP, DYMPL, and INTAP, respectively, across 12 memory-intensive benchmarks.

The contributions of this paper are as follows:

1. We identify that the three outcomes of timeout-based speculative precharge encode asymmetric performance costs. Based on this observation, we propose CRAFT, a feedback-driven scheme that translates this cost asymmetry into differentiated timeout adjustments per bank. The entire mechanism requires only 140 bytes per channel.
2. Through ablation analysis, we demonstrate that feedback signals derived directly from precharge outcomes are sufficient for effective timeout adaptation, while signals drawn from conflict-path heuristics such as phase detection and queue occupancy degrade performance. This finding validates that the cost asymmetry of precharge outcomes alone provides a complete feedback basis for row buffer management, without requiring auxiliary runtime metrics.
3. We evaluate CRAFT using cycle-accurate ChampSim–DRAMSim3 co-simulation with a DDR5-4800 configuration on 12 memory-intensive benchmarks including graph analytics and scientific computing. CRAFT achieves geometric mean IPC improvements of 7.73%, 3.10%, and 2.84% over ABP, DYMPL, and INTAP, respectively. CRAFT requires 24× less storage than DYMPL and over 140× less than ABP.

## 2. Background

### 2.1 DRAM Row Buffer Fundamentals

Modern DRAM organizes each bank around a *row buffer*, an array of sense amplifiers that latches the most recently activated row. The latency of a memory access depends on the state of this row buffer. As illustrated in Figure 3(a), three scenarios arise:

- **Row buffer hit.** The requested data resides in the currently open row. The controller issues a column access command directly, incurring only tCAS.
- **Row buffer miss (closed bank).** No row is currently open. The controller activates the target row and then issues the column access. The total latency is tRCD + tCAS.
- **Row buffer conflict.** A different row is open. The controller must precharge, activate, and then issue the column access. This incurs tRP + tRCD + tCAS.

The disparity among these scenarios motivates row buffer management policies. An *open-page* policy keeps the row buffer open after an access. A *close-page* policy precharges the bank immediately. Neither dominates universally, as shown in Figures 1 and 2.

**Timeout-based speculative precharge.** Timeout-based policies occupy a middle ground between open-page and close-page behavior. The memory controller starts a countdown timer when a row becomes idle. If the timer expires before the next request, the controller speculatively precharges the bank. A short timeout approximates closed-page behavior. A long timeout approximates open-page behavior. This speculation produces one of four outcomes, illustrated in Figure 3(b):

1. **Right precharge.** The next request targets a different row. The speculative precharge correctly anticipated the end of row-level locality. The effective cost is zero.
2. **Wrong precharge.** The next request targets the same row. The controller must reactivate it. The combined overhead of the wasted precharge and reactivation makes this the most costly outcome.
3. **Conflict.** The next request targets a different row, but the timeout has not yet expired. The controller must issue an on-demand precharge and then activate the target row.
4. **Row buffer hit.** The next request targets the same row and arrives before the timeout. The row remains open at zero cost.

<img src="figures/output/timing_diagram.png" alt="Figure 3" width="80%">

**Figure 3: Row buffer access scenarios and timeout precharge outcomes.** (a) Three row buffer states at the time of a memory request. A hit incurs only tCAS. A miss requires tRCD + tCAS. A conflict pays tRP + tRCD + tCAS. (b) Four outcomes of timeout-triggered speculative precharge.

The central challenge is to set the timeout value adaptively, per bank and over time, to match the evolving access pattern.

### 2.2 Limitations of Existing Adaptive Schemes

Several adaptive row buffer management schemes have been proposed. Table 1 summarizes three representative baselines.

**Table 1: Comparison of adaptive row buffer management baselines.**

| Scheme | Decision Mechanism                         | Storage per Channel | Critical-Path Computation           | Key Limitation                              |
| ------ | ------------------------------------------ | ------------------- | ----------------------------------- | ------------------------------------------- |
| ABP    | Per-row access count prediction table      | ~20 KB              | Table lookup + comparison           | Binary prediction; no outcome feedback      |
| DYMPL  | Perceptron + 512-entry page row table      | 3.39 KB             | Seven table lookups + six additions | Indirect features; no cost-aware adaptation |
| INTAP  | Mistake counter with fixed adjustment step | ~200 B              | One comparison + one addition       | Symmetric fixed-step; cost-blind adjustment |

ABP [Awasthi+11] maintains a per-row access counter to predict the likelihood of future reaccesses to each row. This approach requires approximately 20 KB of storage per channel in the form of a set-associative prediction table. This cost is impractical for modern DDR5 controllers with 32 banks per channel. ABP frames row buffer management as a binary open-or-close prediction problem at per-row granularity. This formulation cannot capture bank-level phase transitions.

DYMPL [Rafique+22] employs a perceptron to combine seven extracted features and make open-or-close decisions at cluster boundaries. A 512-entry page row table accounts for 86.6% of the 3.39 KB per-channel storage. The perceptron learns empirical correlations among features. It does not directly observe the cost consequences of its precharge decisions.

INTAP adjusts timeout values per bank through a mistake counter with a fixed step size. At approximately 200 B per channel, INTAP achieves the lowest storage overhead among the three baselines. Its adjustment mechanism, however, is symmetric. A wrong precharge and a conflict trigger equal step magnitudes in opposite directions. This treatment ignores the substantial cost difference between these two error types.

These scheme-specific limitations differ in nature. All three baselines, however, share a deeper deficiency. None of them distinguishes precharge outcomes by their performance cost. A wrong precharge wastes both tRP and tRCD cycles for an unnecessary close-and-reactivate sequence on the same row. A conflict incurs only an extra tRP relative to a correctly timed speculative precharge. Under DDR5-4800 timing with tRP = tRCD = 40 cycles, the wrong precharge penalty is 80 cycles. The conflict penalty is 40 cycles. This 2:1 cost ratio has direct implications for timeout adaptation. The escalation step for wrong precharges should exceed the de-escalation step for conflicts. None of the three baselines incorporates this cost asymmetry into its adaptation logic.

## 3. CRAFT Design

This section presents CRAFT (**C**ost-driven **R**ow-buffer **A**daptive **F**eedback **T**imeout), a lightweight mechanism that exploits the cost asymmetry of precharge outcomes to adaptively manage DRAM row buffers.
Section 3.1 describes the core feedback loop.
Section 3.2 introduces three refinements that exploit additional precharge-path information.
Section 3.3 details the hardware implementation and quantifies storage overhead.

### 3.1 Core Feedback Loop

CRAFT maintains a per-bank timeout counter that specifies the number of idle cycles after the last column access before the memory controller speculatively issues a precharge command.
When a bank activation event occurs following a timeout-triggered precharge, the controller classifies the outcome into one of the three categories defined in Section 2.1: a wrong precharge indicates the timeout was too short, a conflict indicates it was too long, and a right precharge confirms the current value is appropriate.
These three outcomes provide a direct, unambiguous feedback signal for timeout adaptation.
CRAFT exploits the cost asymmetry among these outcomes to derive both the direction and the magnitude of each adjustment.

CRAFT adjusts the per-bank timeout value in response to these outcomes according to three design principles.

**(a) Cost-driven asymmetric step sizes.**
A wrong precharge wastes tRP + tRCD cycles for row reactivation. A conflict incurs an extra tRP relative to a correctly timed speculative precharge. The resulting penalty ratio is (tRP + tRCD) / tRP. Under DDR5-4800 timing (tRP = tRCD = 40 cycles), the wrong precharge penalty of 80 cycles is twice the 40-cycle conflict penalty. CRAFT mirrors this 2:1 ratio in its adjustment magnitudes. The escalation step for wrong precharges uses a base value of BASE_STEP = 50 cycles. The de-escalation step for conflicts is scaled by the factor tRP / (tRP + tRCD), yielding 25 cycles.

This asymmetry creates a deliberate upward bias. Under equal frequencies of wrong precharges and conflicts, each escalation exceeds the subsequent de-escalation and produces a net timeout increase. Wrong precharges impose the higher penalty. The mechanism therefore preferentially avoids them in favor of longer timeouts under ambiguous feedback.

**(b) Exponential backoff.**
CRAFT applies exponential backoff to consecutive wrong precharges by left-shifting the base step:

> step = BASE_STEP × 2^min(reopen_streak, SHIFT_CAP)

The reopen_streak counter tracks consecutive wrong precharges, is capped at seven (three bits), and resets to zero upon a right precharge or a conflict. This mechanism enables rapid convergence during sustained high-locality phases. The timeout can reach the upper bound within a small number of feedback events.

**(c) Continuous adjustment range.**
CRAFT adjusts the timeout continuously within a bounded range [T_MIN, T_MAX] = [50, 3200] cycles. The lower bound prevents degeneration into a pure closed-page policy. The upper bound prevents the row buffer from remaining indefinitely open. The feedback loop can therefore converge to any intermediate value for fine-grained adaptation to varying degrees of row locality. CRAFT's exponential backoff traverses the full timeout range in as few as six escalation events.

Algorithm 1 presents the complete pseudocode of the core feedback loop.

**Algorithm 1: CRAFT Core Feedback Loop**

```
On each bank ACT event:
  if prev_closed_by_timeout:
    if new_row == prev_row:                    ▷ Wrong precharge
      step ← BASE_STEP << min(reopen_streak, SHIFT_CAP)
      timeout ← timeout + step                ▷ Escalate
      reopen_streak ← min(reopen_streak + 1, 7)
      right_streak ← 0
    else:
      if was_ondemand_precharge:               ▷ Conflict
        step ← BASE_STEP × tRP / (tRP + tRCD)
        timeout ← timeout − step              ▷ De-escalate
        reopen_streak ← 0
        right_streak ← 0
      else:                                    ▷ Right precharge
        reopen_streak ← 0
        right_streak ← right_streak + 1
    timeout ← clamp(timeout, T_MIN, T_MAX)
```

Figure 4 illustrates the feedback loop schematically.
The three precharge outcomes feed back to the per-bank timeout counter with asymmetric step sizes, forming a closed-loop control mechanism that continuously adapts to the prevailing row-level access pattern.

<img src="figures/output/feedback_loop.png" alt="CRAFT feedback loop" width="80%">

**Figure 4: CRAFT core feedback loop. On each bank activation following a timeout-triggered precharge, the controller classifies the precharge outcome and adjusts the per-bank timeout accordingly. Wrong precharges escalate the timeout with exponential backoff. Conflicts de-escalate with a cost-proportional step. Right precharges confirm the current timeout value.**

### 3.2 Implementation Refinements

The core feedback loop provides the primary adaptive capability.
The following three refinements exploit additional information available along the precharge outcome path to improve adaptation precision.
All three are lightweight and introduce no additional hardware structures beyond simple counters.

**(a) Right Streak De-escalation (RS).**
After four or more consecutive right precharges, the timeout decrements by half the conflict de-escalation step (conflict_step / 2).
This gradual reduction prevents timeout values from remaining at elevated levels after a high-locality phase has ended.
Without RS, a bank that transitions from a high-locality phase to a low-locality phase would maintain an unnecessarily large timeout until a conflict explicitly triggers de-escalation.
RS provides a proactive path for timeout reduction in the absence of explicit conflict signals.
RS adds three bits per bank for the right_streak counter.

**(b) Read/Write Cost Differentiation (RW).**
Read and write wrong precharges differ in performance impact. A read wrong precharge directly stalls the processor pipeline. The delayed data return blocks retirement of dependent instructions. A write wrong precharge is absorbed by the write buffer and incurs minimal pipeline impact.
Across 62 benchmarks, read operations account for 80.3% of all wrong precharge events, with a read-to-write ratio of 4.1 to 1.
CRAFT exploits this asymmetry by halving the escalation step for write wrong precharges and doubling the de-escalation step for read conflicts.
RW requires no additional storage. The command type is already available to the memory controller.

**(c) Streak Decay (SD).**
Each right precharge decrements the reopen_streak counter by one (with a floor at zero), allowing the escalation magnitude to decay gradually rather than persisting at a historically elevated level.
Without SD, a burst of consecutive wrong precharges could leave reopen_streak at a high value, causing a single wrong precharge much later to trigger a disproportionately large escalation step.
SD ensures that escalation aggressiveness reflects recent behavior rather than historical extremes.
SD requires no additional storage, as it operates on the existing reopen_streak counter.

Section 5.4 validates the effectiveness of these three refinements through an ablation study.

### 3.3 Hardware Implementation

Table 2 itemizes the per-bank storage required by CRAFT.
Each bank maintains five fields totaling 35 bits: a 12-bit timeout counter covering the [50, 3200] range, two 3-bit streak counters for exponential backoff and right-streak tracking, a 16-bit previous row address used for outcome classification, and a single flag bit indicating whether the most recent precharge was triggered by a timeout.
For a DDR5-4800 configuration with 32 banks per channel (8 bank groups × 4 banks per group), the total storage overhead is 140 bytes per channel.

**Table 2: CRAFT Per-Bank Storage Breakdown**

| Field                        | Width             | Description                                |
| ---------------------------- | ----------------- | ------------------------------------------ |
| timeout_value                | 12 bits           | Current timeout value [50, 3200]           |
| reopen_streak                | 3 bits            | Consecutive wrong precharge counter [0, 7] |
| right_streak                 | 3 bits            | Consecutive right precharge counter [0, 7] |
| prev_row                     | 16 bits           | Previously activated row address           |
| prev_closed_by_timeout       | 1 bit             | Timeout precharge indicator                |
| **Per-bank total**     | **35 bits** |                                            |
| **32 banks / channel** | **140 B**   |                                            |

CRAFT requires no specialized hardware structures.
The critical-path computation consists of a single comparison (classifying the precharge outcome by comparing the requested row address against prev_row) and a single addition or subtraction (adjusting the timeout value by the computed step).

## 4. Methodology

### 4.1 Simulation Infrastructure

We evaluate CRAFT using trace-driven microarchitectural simulator ChampSim [Gober+22] integrated with cycle-accurate DRAM simulator DRAMSim3 [Li+20]. The details of our simulation configuration are shown in Table 3.

**Table 3: Simulation Configuration**

| Component           | Parameter                                | Value                     |
| ------------------- | ---------------------------------------- | ------------------------- |
| **Processor** | Frequency                                | 4 GHz                     |
|                     | Pipeline width                           | 6                         |
|                     | ROB entries                              | 350                       |
|                     | Branch predictor                         | TAGE-SC-L                 |
| **Caches**    | L1 (I/D): Size / Associativity / Latency | 32 KB / 8-way / 4 cycles  |
|                     | L2: Size / Associativity / Latency       | 1 MB / 8-way / 10 cycles  |
|                     | LLC: Size / Associativity / Latency      | 4 MB / 16-way / 20 cycles |
| **DRAM**      | Standard                                 | DDR5-4800                 |
|                     | Channels / Ranks / Banks per channel     | 4 / 1 / 32                |
|                     | Rows per bank                            | 65,536                    |
|                     | tCL / tRCD / tRP (DRAM cycles)           | 40 / 40 / 40              |
|                     | Address mapping                          | rorababgchco              |
|                     | Command queue (per bank)                 | 8 entries                 |

### 4.2 Workloads

We select 12 memory-intensive benchmarks from three benchmark suites. Table 4 summarizes the benchmarks and their inputs.

LIGRA [Shun+13] and CRONO [Ahmad+15] are widely recognized benchmark suites specialized for graph applications. LIGRA provides a lightweight shared-memory parallel framework for graph traversal and computation. From LIGRA, we select six representative graph algorithms, including Collaborative Filtering, PageRank, BFS-based Connected Components, Components-Shortcut, Triangle enumeration, and Radii estimation. From CRONO, we include Triangle-Counting.

SPEC CPU2006 [SPEC06] is a widely used benchmark suite for evaluating processor performance. We select two memory-intensive scientific computing workloads, sphinx3 and wrf, which feature stencil-like access patterns with periodic row revisitation.

As input for the graph algorithms, we use three real-world graphs from the SNAP dataset [Leskovec+16]: roadNet-CA (1.97M vertices, 2.77M edges), higgs (456K vertices, 14.8M edges), and soc-pokec (1.6M vertices, 30M edges).

To extract representative program phases, we profile each benchmark using SimPoint [Sherwood+02] with maxK set to 30 and an interval size of 100 million instructions. For each selected simulation point, the cache hierarchy is warmed up with 20 million instructions, and performance is measured over the subsequent 80 million instructions.

**Table 4: Benchmark Suite**

| Suite                 | Benchmark                              | Input                        |
| --------------------- | -------------------------------------- | ---------------------------- |
| LIGRA [Shun+13]       | Collaborative Filtering (CF)           | roadNet-CA, higgs, soc-pokec |
|                       | PageRank                               | higgs, roadNet-CA            |
|                       | BFS-based Connected Components (BFSCC) | soc-pokec                    |
|                       | Components-Shortcut                    | soc-pokec                    |
|                       | Triangle                               | roadNet-CA                   |
|                       | Radii                                  | higgs                        |
| CRONO [Ahmad+15]      | Triangle-Counting                      | roadNet-CA                   |
| SPEC CPU2006 [SPEC06] | sphinx3                                | ref                          |
|                       | wrf                                    | ref                          |

### 4.3 Baselines

We compare CRAFT against three representative adaptive row buffer management schemes. A detailed discussion of these approaches is provided in Section 6.

**ABP** [Awasthi+11] predicts the number of accesses a row will receive and keeps the row open until the predicted count is reached.

**DYMPL** [Rafique+22] employs a perceptron model trained on memory access features to select the row buffer management policy for each request.

**INTAP** [Intel06] precharges each row upon expiration of a per-bank idle timeout and adjusts the timeout through a mistake counter.

### 4.4 Metrics

We report the following metrics to evaluate both system-level performance and DRAM-level effectiveness.

**Instructions Per Cycle (IPC)** serves as the primary performance metric. We report per-benchmark IPC improvement relative to each baseline.

**Read Row Buffer Hit Rate** is defined as the proportion of read requests served directly from the currently activated row without incurring an additional row activation. Since write requests are considered complete once cached in the write buffer, their row buffer hit rates have negligible impact on observed performance. We therefore report read row buffer hit rates exclusively.

**Average Read Latency** quantifies the mean DRAM service time for read requests, measured in DRAM clock cycles. Lower read latency correlates with higher IPC, as read requests lie on the critical path of dependent memory request chains.

## 5. Evaluation

This section evaluates CRAFT across four dimensions: system-level IPC performance (Section 5.1), DRAM-level behavioral verification (Section 5.2), timeout adaptation behavior (Section 5.3), and an ablation study of individual design components (Section 5.4).

### 5.1 IPC Performance

Figure 5 presents the per-benchmark IPC improvement of CRAFT over each of the three baselines. CRAFT achieves a geometric mean IPC improvement of 7.73% over ABP, 3.10% over DYMPL, and 2.84% over INTAP across all 12 benchmarks. CRAFT outperforms every baseline on every benchmark. The improvements range from 1.61% to 12.20%.

<img src="figures/output/normalized_ipc.png" alt="Normalized IPC" width="90%">

**Figure 5: Normalized IPC across 12 benchmarks (CRAFT = 1.0). CRAFT consistently outperforms all three baselines. The geometric mean improvements are 7.73%, 3.10%, and 2.84% over ABP, DYMPL, and INTAP, respectively.**

**Graph traversal workloads.** The graph traversal benchmarks, namely CF, PageRank, BFSCC, and Components-Shortcut, exhibit the largest improvements over ABP (7.1% to 12.2%). These algorithms undergo pronounced phase transitions between exploration and convergence stages. Such transitions cause abrupt shifts in row-level locality. CRAFT's exponential backoff mechanism enables rapid adaptation to such transitions. Under sustained locality, CRAFT rapidly converges to keeping row buffers open. The High timeout range dominates the distribution throughout execution. The Low and Mid ranges rise occasionally but remain minor. This behavior accounts for the largest IPC gains in the benchmark suite.

**Graph analysis workloads.** Triangle enumeration and Radii exhibit mixed locality patterns. CRAFT's per-bank adaptation tracks the evolving access behavior of these workloads. The timeout distribution undergoes a gradual transition from Low-dominated to High-dominated over the full execution. In the first quarter of the program execution, the Low range accounts for the majority of timeout observations. The Low range then steadily decreases. The Mid and High ranges grow correspondingly. CRAFT's feedback loop tracks this progressive buildup of row-level locality without any explicit phase detection mechanism.

**Scientific computing workloads.** sphinx3 and wrf feature stencil-like access patterns with periodic row revisitation. CRAFT correctly identifies the dominant high-locality phases and converges timeout values to the High range for 75% and 57% of the execution on sphinx3 and wrf, respectively. The High range dominates with little variation during the first 40% of execution. The distribution becomes substantially more volatile afterward. The Low and Mid ranges surge repeatedly into significant fractions of the total. These fluctuations reflect alternating transitions between data-intensive and computation-intensive phases. CRAFT tracks these rapid shifts and adjusts timeout values accordingly.

### 5.2 DRAM-Level Verification

To understand the source of CRAFT's IPC improvement, we examine two DRAM-level metrics.
CRAFT achieves the highest read row buffer hit rate on all 12 benchmarks, surpassing the best-performing baseline by an average of 5.62 percentage points. The improvements are most pronounced on workloads with strong but phase-varying row locality. CF/roadNet-CA (+9.25 pp), PageRank/roadNet-CA (+9.12 pp), and sphinx3 (+7.76 pp) exhibit the largest gains.
CRAFT also achieves the lowest average read latency on all 12 benchmarks. The average reduction is 2.74% compared to the best-performing baseline. The latency improvements are largest on benchmarks with the largest read hit rate improvements. Sphinx3 (-5.86%), CF/roadNet-CA (-5.66%), and PageRank/roadNet-CA (-5.29%) show the most significant reductions. This correlation is expected. Additional row buffer hits eliminate the precharge and activation overhead.
Write row buffer hit rates remain nearly identical across all four policies. The performance advantage of CRAFT therefore originates entirely from the read path. This observation is consistent with CRAFT's read/write cost differentiation design.

### 5.3 Timeout Distribution

Figure 6 presents the timeout value distribution for each benchmark. The values fall into three ranges: Low [50, 800), Mid [800, 2000), and High [2000, 3200]. Three distinct adaptation patterns emerge.

<img src="figures/output/timeout_distribution.png" alt="Timeout distribution" width="80%">

**Figure 6: Timeout value distribution across 12 benchmarks, sorted from aggressive-close (left) to keep-open (right). CRAFT adapts to three distinct behavioral regimes without any explicit mode selection.**

**Aggressive Close.** PageRank/higgs concentrates 96.9% of timeout observations in the Low range. 33.5% of observations fall below 100 cycles. The higgs graph's irregular power-law degree distribution yields poor row-level locality for PageRank's vertex-centric iterations. CRAFT responds by aggressively reducing timeout values to minimize conflict penalties. Components-Shortcut/pokec exhibits a similar pattern. The short-lived exploratory accesses of connected component algorithms drive this behavior.

**Gradual Transition.** CF/higgs distributes timeout values across all three ranges. This aggregate distribution is the time-integrated result of a gradual shift from Low-dominated to High-dominated behavior. Early execution phases produce frequent row conflicts and concentrate timeout values in the Low range. Later phases develop stronger row-level locality and shift timeout values into the Mid and High ranges. CRAFT's feedback loop captures this evolving locality without any explicit phase detection.

**Keep Open.** The roadNet-CA benchmarks concentrate timeout values overwhelmingly in the High range. The road network graph's spatially ordered vertex numbering produces strong row-level locality. CRAFT's exponential backoff mechanism rapidly elevates timeout values to the upper bound after observing consecutive wrong precharges.

A particularly revealing comparison is PageRank on two different inputs. RoadNet-CA yields 90.9% in the High range. Higgs yields 96.9% in the Low range. This demonstrates that CRAFT's adaptation is driven by the runtime row-level access pattern, a joint function of algorithm and input data, rather than by the algorithm identity alone. Importantly, all three adaptation modes produce positive IPC improvements over every baseline. CRAFT is genuinely adaptive rather than biased toward any single static policy.

### 5.4 Ablation Study

We conduct an ablation study to quantify the contribution of each design component. Figure 7 compares eight CRAFT variants. Each variant's geometric mean IPC gain over the best baseline is normalized to the core feedback loop's gain.

<img src="figures/output/ablation.png" alt="Ablation Study" width="80%">

**Figure 7: Ablation study of CRAFT design components. Green: core feedback loop and the recommended PRECHARGE configuration. Blue: individual precharge-path enhancements. Red: individual conflict-path signals. The dashed line marks the BASE level.**

**The core feedback loop is the dominant contributor.** The BASE variant implements only the cost-asymmetric step sizes and exponential backoff. BASE accounts for 76% of the final improvement. This confirms that the precharge outcome cost asymmetry provides a sufficiently rich feedback signal for effective timeout adaptation, even without additional refinements.

**Precharge-path refinements provide complementary gains.** The PRECHARGE variant adds three precharge-path enhancements, namely RS, RW, and SD. All three individual enhancements exceed the BASE level. RW is the strongest individual enhancement at 118.7% of BASE's gain. RS and SD reach 107.8% and 107.0%, respectively. The three enhancements synergize effectively. PRECHARGE (RS+RW+SD) achieves 131.9% of BASE's gain. RS and SD prevent timeout stagnation. RW adjusts the step magnitudes based on command type.

**Conflict-path signals are detrimental.** PR and QDSD individually reach 93.9% and 100.0% of BASE's gain, respectively. Adding both to the PRECHARGE configuration yields the ALL variant at 120.8%. These conflict-path signals attempt to extract additional information from conflict events. Phase resets undo progress accumulated during stable phases. Queue-depth scaling introduces a second adaptation signal and can conflict with the cost-driven adjustments. This result validates a key design principle. The three-way classification of precharge outcomes encodes sufficient feedback information. Further decomposition of conflict events yields diminishing returns.

## 6. Related Work

**Row buffer management with static policies.**
JEDEC [DDR+345] standards define a per-command auto-precharge mechanism, upon which all adaptive row buffer management schemes are constructed. Kaseridis et al. [Kaseridis+11] proposed Minimalist Open-page. This approach limits the number of row buffer hits per activation through an address mapping that distributes column address bits across the bank address field. The fixed hit limit is determined at design time and does not adapt across workloads or execution phases. Unlike static policies or fixed address mappings, CRAFT continuously adjusts the idle timeout per bank to track workload phase changes and inter-bank locality differences at runtime.

**Predictor-based row buffer management.**
Park and Park [Park+03] maintained per-bank two-bit saturating counters to predict row hits and decide whether to issue auto-precharge commands. Stankovic and Milenkovic [Stankovic+05] proposed a cascaded close-page predictor combining a zero-live-time predictor with a dead-time predictor. Their analysis noted the cost asymmetry between incorrectly closing and incorrectly keeping a row open. This asymmetry was not exploited to drive adaptive adjustment. CRAFT derives asymmetric adjustment magnitudes directly from DRAM timing parameters. Awasthi et al. [Awasthi+11] proposed ABP. ABP's storage overhead and per-row granularity limitations are detailed in Section 2. Ghasempour et al. [Ghasempour+16] proposed HAPPY. HAPPY exploits the fixed mapping between physical address bits and DRAM address to replace per-row monitoring with per-address-bit monitoring. HAPPY is orthogonal to CRAFT's cost-asymmetric timeout adaptation. CRAFT's per-bank state of 35 bits per bank already achieves minimal storage overhead.

**Timeout-based adaptive schemes.**
INTAP [INTEL+06] adjusts timeout values through a per-bank mistake counter with a fixed step size. Its symmetric, cost-unaware adjustment mechanism is analyzed in Section 2. Beyond this fundamental limitation, the fixed step size constrains adaptation granularity and limits responsiveness to rapid program phase transitions. CRAFT derives step sizes from DRAM timing parameters and applies exponential backoff for faster convergence through cost-weighted feedback.

**Learning-based approaches.**
Ipek et al. [Ipek+08] applied reinforcement learning to DRAM command scheduling. The approach requires 32 KB of SRAM for function approximation tables and a multi-stage pipelined learning engine operating at processor frequency. DYMPL [Rafique+22] models page policy as binary classification using perceptron learning. Its storage and critical-path computation overhead are detailed in Section 2. These learning-based approaches share a common reliance on indirect features as proxies for the optimal precharge decision. CRAFT instead uses the precharge outcome itself as the sole feedback signal. This design eliminates the need for feature engineering, model training, or associative table lookups.

## 7. Conclusion

This paper presents CRAFT, a lightweight feedback-driven row buffer management scheme that exploits the inherent cost asymmetry of precharge operations. The key observation is that the possible outcomes of a timeout-based speculative precharge encode fundamentally different performance penalties. This cost asymmetry can directly govern both the direction and magnitude of timeout adjustments without requiring complex learning models.

CRAFT utilizes this observation through a per-bank feedback loop that combines cost-asymmetric step sizes with exponential backoff. This design achieves rapid convergence during high-locality program phases. Our ablation study shows that precharge-path refinements improve adaptation precision. Incorporating conflict-path signals degrades performance. These results confirm that precharge penalty classification provides sufficient knowledge for effective precharge speculation.

Across 12 memory-intensive benchmarks, CRAFT achieves IPC improvements of 7.73%, 3.10%, and 2.84% over ABP, DYMPL, and INTAP, respectively. CRAFT improves the average read row buffer hit rate by 5.62 percentage points over the best baseline and reduces average read latency by 2.74%. CRAFT requires only 140 B of storage per channel with no specialized hardware structures. CRAFT's per-bank state organization makes it orthogonal to and combinable with DRAM architectural modifications and memory scheduling optimizations.

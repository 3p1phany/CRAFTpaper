## 2. Background

### 2.1 DRAM Row Buffer Fundamentals

Modern DRAM organizes each bank around a *row buffer*, an array of sense amplifiers that latches the most recently activated row. The latency of a memory access depends critically on the state of this row buffer when the request arrives. As illustrated in Figure 4(a), three scenarios arise:

- **Row buffer hit.** The requested data resides in the currently open row. The memory controller issues a column access command (CAS) directly, incurring only the column access latency tCAS. This is the fastest scenario.
- **Row buffer miss (closed bank).** No row is currently open. The controller must first activate the target row (ACT), then issue the CAS. The total latency is tRCD + tCAS.
- **Row buffer conflict.** A different row is open. The controller must first precharge the bank to close the current row (PRE), activate the target row, and then issue the CAS. This incurs the full penalty of tRP + tRCD + tCAS and represents the worst-case latency.

The disparity between these three scenarios motivates row buffer management policies. An *open-page* policy keeps the row buffer open after an access, betting on temporal locality within the same row to yield future hits at tCAS cost. A *close-page* policy precharges the bank immediately after each access, eliminating conflict penalties at the expense of converting every subsequent access into a miss. Neither policy dominates universally. As shown in Figures 1–3, the preferred policy varies across workloads, across execution phases within a single workload, and even across banks within a single execution.

**Timeout-based speculative precharge.** To navigate this trade-off, timeout-based policies occupy a middle ground on the policy spectrum (Figure 5). Rather than committing to a static decision, the memory controller starts a countdown timer when a row becomes idle. If the timer expires before the next request, the controller speculatively precharges the bank. This speculation produces one of four outcomes, illustrated in Figure 4(b):

1. **Right precharge.** The next request targets a different row. The speculative precharge correctly anticipated the end of row-level locality. The bank was therefore already in the precharged state at the time of the new request. This proactive precharge action converts a potential conflict into a simple row activation. The effective cost of the speculation is zero.
2. **Wrong precharge.** The speculative precharge closed the row prematurely. The next request targets this same row and would have been served as a row buffer hit at zero additional latency. The precharge was therefore unnecessary. The controller must now reactivate the same row. The combined cost of the unnecessary precharge and the subsequent reactivation makes this the most costly outcome among the four cases.
3. **Conflict.** The next request targets a different row. The timeout, however, has not yet expired. The bank therefore still holds a stale open row. The controller must accordingly issue an on-demand precharge and then activate the target row. The activation of the new row is unavoidable regardless of the precharge timing. A correctly timed speculative precharge would have overlapped the tRP latency with idle bank cycles. Only this overlap opportunity is lost.
4. **Row buffer hit.** The next request targets the same row and arrives before the timeout expires. The row remains open, and the controller serves the request directly with a column access. No precharge or activation is needed. The effective cost is zero.

<img src="figures/output/timing_diagram.png" alt="Figure 4" width="80%">

**Figure 4: Row buffer access scenarios and timeout precharge outcomes.** (a) Three row buffer states at the time of a memory request. A hit incurs only tCAS. A miss requires tRCD + tCAS. A conflict pays the full tRP + tRCD + tCAS penalty. (b) Four outcomes of timeout-triggered speculative precharge. A right precharge correctly anticipated the end of row-level locality and converted a potential conflict into a miss. A wrong precharge closed the row prematurely and forced a costly reactivation. A conflict means the timeout had not yet expired and the bank still held a stale open row. A row buffer hit means the next request arrived before the timeout and accessed the same open row at zero cost.

<img src="figures/output/policy_spectrum.png" alt="Figure 5" width="80%">

**Figure 5: Row buffer management policy spectrum.** A short timeout approximates closed-page behavior. A long timeout approximates open-page behavior. The timeout parameter controls where each bank operates on this spectrum.

The timeout value controls where a bank operates on the closed-to-open spectrum: a short timeout approximates closed-page behavior, while a long timeout approximates open-page behavior. The central challenge is to set this timeout value adaptively, per bank and over time, to match the evolving access pattern of each bank.

### 2.2 Limitations of Existing Adaptive Schemes

Several adaptive row buffer management schemes have been proposed to address this challenge. Table 1 summarizes three representative baselines. These baselines span the design space in terms of mechanism complexity and hardware cost.

**Table 1: Comparison of adaptive row buffer management baselines.**

| Scheme | Decision Mechanism                         | Storage per Channel | Critical-Path Computation           | Key Limitation                              |
| ------ | ------------------------------------------ | ------------------- | ----------------------------------- | ------------------------------------------- |
| ABP    | Per-row access count prediction table      | ~20 KB              | Table lookup + comparison           | Binary prediction; no outcome feedback      |
| DYMPL  | Perceptron + 512-entry page row table      | 3.39 KB             | Seven table lookups + six additions | Indirect features; no cost-aware adaptation |
| INTAP  | Mistake counter with fixed adjustment step | ~200 B              | One comparison + one addition       | Symmetric fixed-step; cost-blind adjustment |

ABP [Awasthi+11] maintains a per-row access counter to predict the likelihood of future reaccesses to each row. This approach requires approximately 20 KB of storage per channel in the form of a set-associative prediction table. This cost is impractical for modern DDR5 controllers with 32 banks per channel. More fundamentally, ABP frames row buffer management as a binary open-or-close prediction problem at per-row granularity. This formulation cannot capture bank-level phase transitions. ABP also does not employ timeout-based speculation and therefore has no mechanism to observe or learn from speculative precharge outcomes.

DYMPL [Rafique+22] employs a perceptron to combine seven extracted features and make open-or-close decisions at cluster boundaries. A 512-entry page row table supports the feature extraction and accounts for 86.6% of the 3.39 KB per-channel storage. The perceptron inference further requires seven table lookups and six additions on the decision critical path. Beyond these overhead concerns, the feature-based approach introduces a structural limitation. The perceptron learns empirical correlations among features such as page utilization, hotness, and column stride. It does not directly observe the cost consequences of its precharge decisions.

INTAP adjusts timeout values per bank through a mistake counter with a fixed step size. The counter detects excessive precharge errors and modifies the timeout by a constant increment. At approximately 200 B per channel, INTAP achieves the lowest storage overhead among the three baselines. Its adjustment mechanism, however, is symmetric. A wrong precharge and a conflict trigger equal step magnitudes in opposite directions. This treatment ignores the substantial cost difference between these two error types.

These scheme-specific limitations differ in nature. All three baselines, however, share a deeper deficiency. None of them distinguishes precharge outcomes by their performance cost. A wrong precharge wastes both tRP and tRCD cycles for an unnecessary close-and-reactivate sequence. The access would have been served as a row buffer hit at zero additional cost. A conflict incurs only an extra tRP relative to a correctly timed speculative precharge. The activation of the different row is unavoidable. Under DDR5-4800 timing with tRP = tRCD = 40 cycles, the wrong precharge penalty is 80 cycles. The conflict penalty is 40 cycles. This 2:1 cost ratio has direct implications for timeout adaptation. The escalation step for wrong precharges should exceed the de-escalation step for conflicts. None of the three baselines incorporates this cost asymmetry into its adaptation logic.

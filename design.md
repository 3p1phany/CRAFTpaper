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
CRAFT adjusts the timeout continuously within a bounded range [T_MIN, T_MAX] = [50, 3200] cycles. The lower bound prevents degeneration into a pure closed-page policy. The upper bound prevents the row buffer from remaining indefinitely open. The feedback loop can therefore converge to any intermediate value for fine-grained adaptation to varying degrees of row locality.

CRAFT's exponential backoff traverses the full timeout range in as few as six escalation events.

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

Figure 6 illustrates the feedback loop schematically.
The three precharge outcomes feed back to the per-bank timeout counter with asymmetric step sizes, forming a closed-loop control mechanism that continuously adapts to the prevailing row-level access pattern.

<img src="figures/output/feedback_loop.png" alt="CRAFT feedback loop" width="80%">

**Figure 6: CRAFT core feedback loop. On each bank activation following a timeout-triggered precharge, the controller classifies the precharge outcome and adjusts the per-bank timeout accordingly. Wrong precharges escalate the timeout with exponential backoff (left arrow), while conflicts de-escalate with a cost-proportional step (right arrow). Right precharges confirm the current timeout value.**

### 3.2 Implementation Refinements

The core feedback loop described above provides the primary adaptive capability.
The following three refinements exploit additional information available along the precharge outcome path to improve adaptation precision.
All three are lightweight and introduce no additional hardware structures beyond simple counters.

**(a) Right Streak De-escalation (RS).**
When four or more consecutive right precharges are observed for a bank, the timeout is decremented by half the conflict de-escalation step (conflict_step / 2).
This gradual reduction prevents timeout values from remaining at elevated levels after a high-locality phase has ended.
Without RS, a bank that transitions from a high-locality phase to a low-locality phase would maintain an unnecessarily large timeout until a conflict explicitly triggers de-escalation, potentially delaying adaptation by many idle cycles.
RS provides a proactive, gentle path for timeout reduction in the absence of explicit conflict signals.
RS adds three bits per bank for the right_streak counter.

**(b) Read/Write Cost Differentiation (RW).**
Read and write wrong precharges differ in their performance impact. A read wrong precharge stalls the processor pipeline. The delayed data return blocks retirement of dependent instructions. A write wrong precharge is absorbed by the write buffer and incurs minimal pipeline impact.
Across 62 benchmarks, read operations account for 80.3% of all wrong precharge events, with a read-to-write ratio of 4.1 to 1. This ratio varies substantially across workloads. In PageRank on the higgs graph, read wrong precharges constitute 99.8% of all wrong precharge events. In wrf, write wrong precharges are the majority at 56.5%.
CRAFT exploits this asymmetry by halving the escalation step for write wrong precharges and doubling the de-escalation step for read conflicts.
RW requires no additional storage. The command type is already available to the memory controller.

**(c) Streak Decay (SD).**
Each right precharge decrements the reopen_streak counter by one (with a floor at zero), allowing the escalation magnitude to decay gradually rather than persisting at a historically elevated level.
Without SD, a burst of consecutive wrong precharges could leave reopen_streak at a high value, causing a single wrong precharge much later to trigger a disproportionately large escalation step.
SD ensures that escalation aggressiveness reflects recent behavior rather than historical extremes.
SD requires no additional storage, as it operates on the existing reopen_streak counter.

Section 5.4 validates the effectiveness of these three refinements through an ablation study and compares them against conflict-path alternatives.

### 3.3 Hardware Implementation

Table 1 itemizes the per-bank storage required by CRAFT.
Each bank maintains five fields totaling 35 bits: a 12-bit timeout counter covering the [50, 3200] range, two 3-bit streak counters for exponential backoff and right-streak tracking, a 16-bit previous row address used for outcome classification, and a single flag bit indicating whether the most recent precharge was triggered by a timeout.
For a DDR5-4800 configuration with 32 banks per channel (8 bank groups × 4 banks per group), the total storage overhead is 140 bytes per channel.

**Table 1: CRAFT Per-Bank Storage Breakdown**

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

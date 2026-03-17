## 3. CRAFT Design

This section presents CRAFT (**C**ost-driven **R**ow-buffer **A**daptive **F**eedback **T**imeout), a lightweight mechanism that exploits the cost asymmetry of precharge outcomes to adaptively manage DRAM row buffers.
Section 3.1 describes the core feedback loop.
Section 3.2 introduces three refinements that exploit additional precharge-path information.
Section 3.3 details the hardware implementation and quantifies storage overhead.

### 3.1 Core Feedback Loop

CRAFT maintains a per-bank timeout counter that specifies the number of idle cycles after the last column access before the memory controller speculatively issues a precharge command.
When a bank activation (ACT) event occurs following a timeout-triggered precharge, the controller observes one of three outcomes, each encoding a distinct cost signal about whether the previous timeout value was appropriate.

**Wrong precharge.**
The newly activated row matches the row that was most recently closed by a timeout-triggered precharge (new_row = prev_row).
The timeout was too short: the row was prematurely closed while still being actively used.
The resulting penalty is the combined precharge and reactivation overhead (tRP + tRCD), as the row was unnecessarily closed and must now be reopened before the pending access can be served.

**Conflict.**
An on-demand precharge was required because the row buffer held a stale row when a request targeting a different row arrived.
The timeout was too long: the row should have been closed earlier to make the bank available.
The additional penalty is tRP, the precharge latency that would have been avoided had the timeout-triggered precharge closed the row proactively before the conflicting request arrived.

**Right precharge.**
The newly activated row differs from the previously closed row, and no on-demand precharge was necessary.
The timeout correctly anticipated that the row would not be reaccessed.
The proactive closure converted what would have been a conflict access (tRP + tRCD + tCAS) into a row miss on an already-closed bank (tRCD + tCAS), saving tRP cycles.

These three outcomes provide a direct, unambiguous feedback signal: wrong precharges indicate that the timeout should increase, conflicts indicate that it should decrease, and right precharges confirm that the current value is appropriate.
Crucially, the penalties associated with these outcomes are *not* symmetric—wrong precharges impose a greater cost than conflicts—and CRAFT exploits this asymmetry to derive both the direction and the magnitude of each adjustment.

CRAFT adjusts the per-bank timeout value in response to these outcomes according to three design principles.

**(a) Cost-driven asymmetric step sizes.**
The penalty of a wrong precharge (tRP + tRCD) exceeds that of a conflict (tRP) by a factor of (tRP + tRCD) / tRP.
CRAFT mirrors this cost ratio in its adjustment magnitudes: the escalation step for wrong precharges uses a base value of BASE_STEP cycles, while the de-escalation step for conflicts is scaled down by the factor tRP / (tRP + tRCD).
With DDR5-4800 timing parameters (tRP = tRCD = 40 cycles) and BASE_STEP = 50, the conflict de-escalation step evaluates to 50 × 40 / 80 = 25 cycles—half the escalation base.

This asymmetry introduces a deliberate upward bias: when wrong precharges and conflicts alternate at equal frequency, the net effect is a gradual timeout increase because each escalation exceeds the subsequent de-escalation.
The bias is intentional.
Since wrong precharges impose the higher penalty, the mechanism preferentially avoids them by favoring longer timeouts when the feedback signal is ambiguous.

**(b) Exponential backoff.**
When consecutive wrong precharges occur on the same bank, CRAFT applies exponential backoff by left-shifting the base step:

> step = BASE_STEP × 2^min(reopen_streak, SHIFT_CAP)

The reopen_streak counter tracks consecutive wrong precharges and is capped at seven (three bits).
It resets to zero upon observing a right precharge or a conflict.
Exponential backoff enables rapid convergence during sustained high-locality phases: after two consecutive wrong precharges the step quadruples (50 → 200 cycles), and after three it octuples (50 → 400 cycles), allowing the timeout to reach the upper bound within a small number of feedback events.
Empirically, on benchmarks with strong row-level locality (the roadNet-CA graph workloads), timeout values reside in the High range [2000, 3200] for 85–92% of execution, confirming that exponential backoff drives the timeout to the appropriate operating region and stabilizes it there.

**(c) Continuous adjustment range.**
CRAFT adjusts the timeout continuously within a bounded range [T_MIN, T_MAX] = [50, 3200] cycles.
The lower bound prevents the policy from degenerating into a pure closed-page strategy, while the upper bound prevents unbounded growth that would effectively freeze the row buffer in the open state.
Within this range, the feedback loop can converge to any intermediate value, enabling fine-grained adaptation to workload phases with varying degrees of row locality.

In contrast, INTAP [Ghasemp+16] employs the same [50, 3200] range but restricts each adjustment to a fixed step of 50 cycles, requiring up to 63 consecutive adjustments in the same direction to traverse the full range.
CRAFT's exponential backoff traverses the same range in as few as six escalation events (50 + 100 + 200 + 400 + 800 + 1600 = 3150), enabling an order-of-magnitude faster response to workload phase transitions.

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

**Figure 4: CRAFT core feedback loop. On each bank activation following a timeout-triggered precharge, the controller classifies the precharge outcome and adjusts the per-bank timeout accordingly. Wrong precharges escalate the timeout with exponential backoff (left arrow), while conflicts de-escalate with a cost-proportional step (right arrow). Right precharges confirm the current timeout value.**


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
The performance impact of a wrong precharge depends on the command type of the subsequent access.
A read wrong precharge directly stalls the processor pipeline, as the read data resides on the critical path.
A write wrong precharge, by contrast, is absorbed by the write buffer and does not directly contribute to processor stall cycles.
CRAFT exploits this asymmetry by halving the escalation step for write wrong precharges (which are less performance-critical) and doubling the de-escalation step for read conflicts (which represent the most costly outcome to leave unaddressed).
RW requires no additional storage, as the command type is already available to the memory controller.

**(c) Streak Decay (SD).**
Each right precharge decrements the reopen_streak counter by one (with a floor at zero), allowing the escalation magnitude to decay gradually rather than persisting at a historically elevated level.
Without SD, a burst of consecutive wrong precharges could leave reopen_streak at a high value, causing a single wrong precharge much later to trigger a disproportionately large escalation step.
SD ensures that escalation aggressiveness reflects recent behavior rather than historical extremes.
SD requires no additional storage, as it operates on the existing reopen_streak counter.

The effectiveness of these refinements is validated in the ablation study (Section 5.4).
The three precharge-path refinements, when combined with the core feedback loop, yield an additional 0.21 percentage points of geometric mean IPC improvement over INTAP.
In contrast, conflict-path refinements—specifically, phase reset (which resets timeout upon detecting consecutive conflicts) and queue-depth-scaled de-escalation (which modulates the de-escalation step by command queue occupancy)—reduce performance by 0.07 percentage points when added on top of the precharge-path refinements.
This result confirms that the three-way classification of precharge outcomes (right, wrong, conflict) already encodes sufficient feedback information for effective timeout adaptation, and that further decomposition of conflict events is counterproductive.


### 3.3 Hardware Implementation

Table 1 itemizes the per-bank storage required by CRAFT.
Each bank maintains five fields totaling 35 bits: a 12-bit timeout counter covering the [50, 3200] range, two 3-bit streak counters for exponential backoff and right-streak tracking, a 16-bit previous row address used for outcome classification, and a single flag bit indicating whether the most recent precharge was triggered by a timeout.
For a DDR5-4800 configuration with 32 banks per channel (8 bank groups × 4 banks per group), the total storage overhead is 1120 bits, or 140 bytes per channel.

**Table 1: CRAFT Per-Bank Storage Breakdown**

| Field | Width | Description |
|-------|-------|-------------|
| timeout_value | 12 bits | Current timeout value [50, 3200] |
| reopen_streak | 3 bits | Consecutive wrong precharge counter [0, 7] |
| right_streak | 3 bits | Consecutive right precharge counter [0, 7] |
| prev_row | 16 bits | Previously activated row address |
| prev_closed_by_timeout | 1 bit | Timeout precharge indicator |
| **Per-bank total** | **35 bits** | |
| **32 banks / channel** | **140 B** | |

Table 2 compares CRAFT's hardware requirements against prior adaptive row buffer management schemes.
CRAFT's 140-byte footprint is 24.2× smaller than DYMPL [Rafique+22], 30.3× smaller than RL_PAGE [Ipek+08], and 29.6% smaller than INTAP [Ghasemp+16], while achieving the highest IPC across all evaluated baselines.
Importantly, CRAFT requires no specialized hardware structures.
The critical-path computation consists of a single comparison (to classify the precharge outcome by comparing the requested row address against prev_row) and a single addition or subtraction (to adjust the timeout value by the computed step).
In contrast, DYMPL requires a 512-entry set-associative Page Record Table that accounts for 86.6% of its storage budget and a seven-input adder tree for perceptron inference, while RL_PAGE requires 4 KB of SRAM for CMAC function approximation tables and eight dedicated hash computation units.

**Table 2: Hardware Overhead Comparison Across Row Buffer Management Schemes**

| Scheme | Storage / ch | Specialized Hardware | Critical Path |
|--------|-------------|---------------------|---------------|
| **CRAFT** | **140 B** | **None** | **1 compare + 1 add** |
| INTAP | ~200 B | None | 1 compare + 1 add |
| ABP | ~20 KB | Set-associative table | Table lookup |
| DYMPL | 3.39 KB | 512-entry set-assoc. PRT | 7 lookups + 6 adds |
| RL_PAGE | 4.14 KB | 4 KB SRAM + hash units | 16 hashes + multiply |

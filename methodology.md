## 4. Methodology

### 4.1 Simulation Infrastructure

We evaluate CRAFT using a co-simulation framework that couples
ChampSim, a cycle-level out-of-order CPU simulator, with
DRAMSim3, a cycle-accurate DRAM simulator.
ChampSim models the processor pipeline and cache hierarchy,
while DRAMSim3 faithfully simulates DRAM command scheduling,
timing constraints, and row buffer management.
The two simulators are integrated through a memory interface
in which ChampSim issues read and write transactions to
DRAMSim3, and DRAMSim3 invokes completion callbacks upon
request service.
This tight coupling ensures that the performance impact of
row buffer management decisions is accurately reflected in
processor-level metrics such as IPC.

Table 1 summarizes the key configuration parameters.
The modeled processor is a single-core, 4 GHz out-of-order
core with a 350-entry reorder buffer, six-wide
fetch/decode/dispatch, four-wide execution, and a
five-wide retire stage.
Branch prediction employs the TAGE-SC-L predictor.
The cache hierarchy comprises a 32 KB L1 instruction cache,
a 32 KB L1 data cache, a 1 MB L2 cache, and a 4 MB
last-level cache, all using LRU replacement.
No hardware prefetcher is enabled at any cache level,
isolating the effect of the row buffer management policy
from prefetching-induced access pattern changes.

The DRAM subsystem models a DDR5-4800 configuration with
four channels, one rank per channel, and 32 banks per channel
organized as eight bank groups of four banks each.
Each bank contains 65,536 rows.
Key timing parameters include tCL = tRCD = tRP = 40
DRAM cycles (at 2400 MHz), with a clock period of 0.416 ns.
The address mapping follows a row-bank-bankgroup-channel-column
(rorababgchco) interleaving scheme, and each bank maintains
an independent eight-entry command queue.

**Table 1: Simulation Configuration**

| Component | Parameter | Value |
|-----------|-----------|-------|
| **Processor** | Frequency | 4 GHz |
| | Issue width (fetch/decode/dispatch) | 6-wide |
| | Execute width | 4-wide |
| | Retire width | 5-wide |
| | ROB / LQ / SQ entries | 350 / 128 / 72 |
| | Branch predictor | TAGE-SC-L |
| **L1I Cache** | Size / Associativity / Latency | 32 KB / 8-way / 4 cycles |
| **L1D Cache** | Size / Associativity / Latency | 32 KB / 8-way / 4 cycles |
| **L2 Cache** | Size / Associativity / Latency | 1 MB / 8-way / 10 cycles |
| **LLC** | Size / Associativity / Latency | 4 MB / 16-way / 20 cycles |
| **DRAM** | Standard | DDR5-4800 |
| | Channels / Ranks / Banks per channel | 4 / 1 / 32 |
| | Bank groups × Banks per group | 8 × 4 |
| | Rows per bank | 65,536 |
| | tCL / tRCD / tRP (DRAM cycles) | 40 / 40 / 40 |
| | tRAS / tRFC (DRAM cycles) | 77 / 984 |
| | Address mapping | rorababgchco |
| | Command queue (per bank) | 8 entries |

### 4.2 Workloads

We select 12 memory-intensive benchmarks that exhibit
high sensitivity to row buffer management policy.
The benchmarks are drawn from three sources:
the LIGRA graph processing framework [Shun+13],
the CRONO graph analytics suite [Ahmad+15],
and the SPEC CPU2006 benchmark suite [SPEC06].
Each benchmark is executed for 20 million warmup instructions
followed by 80 million simulation instructions.

Table 2 lists the benchmarks grouped by their dominant
memory access patterns.
The first group comprises graph traversal algorithms—
Collaborative Filtering (CF), PageRank, Breadth-First
Search with Connected Components (BFSCC), and
Components-Shortcut—which exhibit pronounced phase
transitions between exploration and convergence stages,
causing abrupt shifts in row-level locality.
The second group includes graph analysis kernels—
Triangle enumeration, Triangle-Counting, and Radii—
characterized by mixed locality patterns that vary
substantially across banks within the same execution.
The third group contains scientific computing workloads
from SPEC CPU2006—sphinx3 and wrf—which feature
stencil-like access patterns with periodic row revisitation.
These benchmarks run on three representative input graphs:
roadNet-CA (a road network), higgs (a social network),
and soc-pokec (a social graph), providing diverse
graph topologies and memory footprints.

**Table 2: Benchmark Suite**

| Category | Benchmark | Suite | Input |
|----------|-----------|-------|-------|
| Graph traversal | CF | LIGRA | roadNet-CA, higgs, soc-pokec |
| | PageRank | LIGRA | higgs, roadNet-CA |
| | BFSCC | LIGRA | soc-pokec |
| | Components-Shortcut | LIGRA | soc-pokec |
| Graph analysis | Triangle | LIGRA | roadNet-CA |
| | Triangle-Counting | CRONO | roadNet-CA |
| | Radii | LIGRA | higgs |
| Scientific computing | sphinx3 | SPEC CPU2006 | ref |
| | wrf | SPEC CPU2006 | ref |

### 4.3 Baselines

We compare CRAFT against three representative adaptive
row buffer management schemes that span the design space
from heavyweight predictor-based approaches to lightweight
counter-based mechanisms.

**ABP** (Access-Based Predictor) [Awasthi+11] maintains a
per-row access counter table to predict whether a row will
be re-accessed after being opened.
Rows with access counts exceeding a threshold are kept open;
otherwise, the bank is precharged immediately.
ABP achieves fine-grained per-row adaptivity at the cost
of approximately 20 KB of storage per channel for the
set-associative prediction table.

**DYMPL** (Dynamic Multi-Level Perceptron) [Rafique+22]
employs a seven-feature perceptron model combined with a
512-entry Page Residency Table (PRT) to predict the optimal
page policy.
Features include row access frequency, inter-access interval,
and bank-level utilization metrics.
DYMPL requires 3.39 KB per channel, of which 86.6% is
consumed by the PRT, and its critical path involves seven
table lookups and six additions.

**INTAP** (Intelligent Adaptive Timeout) uses a per-bank
mistake counter that tracks incorrect timeout precharge
decisions and adjusts the timeout value by a fixed step
of 50 cycles.
INTAP requires approximately 200 bytes per channel and
operates within the same timeout range [50, 3200] as CRAFT.
However, INTAP applies symmetric, fixed-magnitude adjustments
regardless of whether the timeout error was a wrong precharge
or a conflict, and does not account for the cost asymmetry
between these two outcomes.

All baselines use the identical processor, cache, and DRAM
timing configuration described in Section 4.1.
Only the row buffer management policy differs across
experiments, ensuring a fair comparison.

### 4.4 Metrics

We report the following metrics to evaluate both
system-level performance and DRAM-level effectiveness.

**Instructions Per Cycle (IPC)** serves as the primary
performance metric.
We report per-benchmark IPC improvement relative to each
baseline, as well as the geometric mean across all
12 benchmarks, to capture overall performance trends
without bias toward high-IPC workloads.

**Read Row Buffer Hit Rate** measures the fraction of
read requests that find the target row already open in
the row buffer.
This metric directly reflects the quality of timeout
decisions, as higher hit rates indicate that the policy
successfully keeps rows open when temporal locality exists.
We report read hit rates separately from write hit rates,
since write requests are buffered in the write queue and
their row buffer hits have minimal impact on processor stall time.

**Average Read Latency** quantifies the mean DRAM service
time for read requests, measured in DRAM clock cycles.
Lower read latency correlates with higher IPC, as read
requests lie on the critical path of dependent instruction
chains.

**Timeout Precharge Accuracy** is defined as the fraction
of timeout-initiated precharges that are classified as
correct (i.e., the next access to the same bank targets a
different row).
This metric validates the effectiveness of the feedback
loop in converging toward appropriate timeout values,
independent of the resulting IPC impact.

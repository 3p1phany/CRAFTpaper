## 4. Methodology

### 4.1 Simulation Infrastructure

We evaluate CRAFT using trace-driven microarchitectural simulator ChampSim [Gober+22] integrated with cycle-accurate DRAM simulator DRAMSim3 [Li+20]. The details of our simulation configuration are shown in Table 1.

**Table 1: Simulation Configuration**

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

We select 12 memory-intensive benchmarks from three benchmark suites with a range of inputs. The benchmarks and their respective inputs are summarized in Table 2.

LIGRA [Shun+13] and CRONO [Ahmad+15] are widely recognized benchmark suites specialized for graph applications. LIGRA provides a lightweight shared-memory parallel framework that supports a broad range of graph traversal and computation algorithms. From LIGRA, we select six representative graph algorithms, including Collaborative Filtering, PageRank, BFS-based Connected Components, Components-Shortcut, Triangle enumeration, and Radii estimation. From CRONO, we include Triangle-Counting.

SPEC CPU2006 [SPEC06] is a widely used benchmark suite for evaluating processor performance. We select two memory-intensive scientific computing workloads, sphinx3 and wrf, which feature stencil-like access patterns with periodic row revisitation.

As input for the graph algorithms, we use three real-world graphs from the SNAP dataset collection [Leskovec+16] that provide diverse topologies and memory footprints. roadNet-CA is a road network of California with 1.97 million vertices and 2.77 million edges. higgs represents the network of followers participating in the "Higgs" discussion on Twitter, with 456 thousand vertices and 14.8 million edges. soc-pokec contains user relationship data from an online social network, with 1.6 million vertices and 30 million edges.

To extract representative program phases, we profile each benchmark using the SimPoint methodology [Sherwood+02] with maxK set to 30 and an interval size of 100 million instructions. For each selected simulation point, the cache hierarchy is warmed up with 20 million instructions, and the performance is measured over the subsequent 80 million instructions.

**Table 2: Benchmark Suite**

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
We compare CRAFT against three prior adaptive row buffer management schemes, whose limitations are discussed in Section 2 and whose technical details are presented in Section 7.

**ABP** [Awasthi+11] predicts the number of accesses a row will receive and keeps the row open until the predicted count is reached.

**DYMPL** [Rafique+22] uses a perceptron model trained on memory access features to classify each page as open or close.

**INTAP** [Intel06] adjusts a per-bank idle timeout based on a mistake counter that tracks incorrect precharge decisions.

### 4.4 Metrics

We report the following metrics to evaluate both
system-level performance and DRAM-level effectiveness of CRAFT.

**Instructions Per Cycle (IPC)** serves as the primary
performance metric.
We report per-benchmark IPC improvement relative to each
baseline, as well as the geometric mean across all
12 benchmarks.

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

## 7. Related Work

DRAM row buffer management has been extensively studied over the past two decades. We categorize prior work into four main approaches: static policies, predictor-based schemes, timeout-based adaptive schemes, and learning-based approaches. We also briefly discuss architectural techniques that address row buffer performance at the circuit or microarchitecture level.

### 7.1 Static Page Policies

The two canonical policies—open-page and closed-page—represent opposite ends of the design spectrum. The open-page policy retains a row in the active state following an access, benefiting workloads with high row locality by avoiding precharge and activation overhead on repeated accesses to the same row. However, when a subsequent access targets a different row, a row conflict occurs, requiring a precharge followed by activation at the highest access latency. The closed-page policy precharges immediately after each access. This eliminates conflict penalties but converts all subsequent accesses to compulsory row misses.

JEDEC standards [JEDEC] support an intermediate auto-precharge mode in which the controller can issue commands with or without auto-precharge on a per-request basis. However, the decision remains effectively static per command and lacks runtime adaptivity.

Kaseridis et al. [Kaseridis+11] proposed Minimalist Open-page, which structurally limits page hits per activation to four through address mapping that splits column bits across the bank address. This bounds row buffer starvation while preserving partial locality. However, the fixed hit limit is not adaptive across workloads or DRAM technologies.

### 7.2 Predictor-Based Row Buffer Management

Predictor-based approaches maintain per-row or per-bank state to predict whether an open row will be re-accessed, and decide proactively whether to precharge. A fundamental limitation shared by such approaches is that memory requests arriving at the controller have already been filtered through multiple levels of cache. As a result, much of the original access pattern semantics is lost at the memory controller level, making it inherently difficult to achieve high prediction accuracy by directly transplanting branch prediction techniques to row buffer management.

**Per-row predictors.** Park and Park [Park+03] first applied 2-bit saturating counters, drawing on branch prediction techniques, to DRAM page policy. Per-bank counters transition between Strong-Hit and Strong-Miss states. Although this work demonstrated the feasibility of prediction-based page management, the evaluation was limited to trace-driven simulation on five SPEC92 benchmarks. Stankovic and Milenkovic [Stankovic+05] extended this approach with a cascaded predictor: a Zero Live Time (ZLT) predictor identifies single-access rows, while a Dead Time Predictor handles the remaining rows with a timeout set to twice the last access interval. Their observation that miss-close errors incur higher cost than miss-open errors anticipates the cost-asymmetric framework adopted by CRAFT.

Xu et al. [Xu+09] adapted Yeh and Patt's two-level branch predictor[Yeh+90] to page policy, exploring combinations of global, per-bank, and per-page history registers with pattern history tables. However, the per-page variants require substantial storage, and the evaluation predates modern multicore systems.

**Access-based predictors.** Awasthi et al. [Awasthi+11] proposed the Access Based Predictor (ABP), which tracks per-row access counts in a 2048-set, 4-way history table of approximately 20 KB per channel. ABP predicts the number of accesses a row will receive before closing. The predictor lookup is hidden behind normal DRAM access latency. However, the 20 KB storage requirement presents scalability challenges.

Shen et al. [Shen+14] proposed RBPP, which maintains a small set of four Most Accessed Row Registers (MARR) per bank. The design leverages the observation that a small number of frequently accessed rows account for the majority of accesses within short time windows. Rows present in the MARR are kept open; all others are closed immediately. RBPP achieves performance comparable to ABP with significantly less storage. However, it operates at a coarser granularity and cannot distinguish among different access phases within frequently accessed rows.

### 7.3 Timeout-Based Adaptive Policies

Timeout-based schemes speculatively precharge a row after it has been idle for a configurable number of cycles. By adjusting this timeout value, the policy can span the full spectrum from open-page to closed-page behavior.

Ghasempour et al. [Ghasemp+16] proposed INTAP, a per-bank timeout adjustment mechanism that uses a mistake counter with a fixed step size. When the counter indicates excessive wrong precharges, timeout increases; when conflicts predominate, timeout decreases. Although INTAP is hardware-efficient at approximately 200 B per channel, it treats wrong precharges and conflicts symmetrically despite their differing latency costs. The fixed step size further limits the rate of adaptation to workload phase transitions.

**CRAFT's distinction from timeout-based schemes.** Unlike the fixed, symmetric steps of INTAP, CRAFT adjusts timeout continuously within a bounded range using asymmetric step sizes derived from precharge outcome costs. CRAFT employs exponential backoff for rapid convergence during high-locality phases, while de-escalation uses cost-proportional steps for conservative reduction. This cost-driven feedback mechanism achieves finer-grained adaptation with only 140 B per channel.

### 7.4 Learning-Based Approaches

Machine learning techniques have been applied to row buffer management with the objective of automatically discovering optimal policies.

Ipek et al. [Ipek+08] modeled DRAM command scheduling as a Markov decision process and applied SARSA with CMAC function approximation to learn scheduling policies, including implicit precharge decisions. The reinforcement learning agent uses six features selected from 226 candidates, covering queue occupancy, read/write mix, and instruction criticality. However, the approach requires 32 KB of SRAM and a pipelined reinforcement learning engine operating at CPU frequency. The learned policy also lacks interpretability and provides no explicit signal amenable to timeout adjustment.

Rafique and Zhu proposed a series of increasingly sophisticated learning-based approaches. FAPS-3D [Rafique+19] employs per-bank 2-bit saturating counter finite state machines in 3D-stacked DRAM to dynamically switch between open-page and closed-page based on row-buffer hit-rate feedback. Although FAPS-3D is relatively lightweight at 3.25 KB, it is limited to binary open/close decisions per bank. Their subsequent work, DYMPL [Rafique+22], models page policy as a binary classification problem using perceptron learning with seven features. A 512-entry Page Record Table (PRT) and per-bank Bank Record Table support online training. However, the PRT dominates the 3.39 KB per channel storage overhead, the seven-feature lookup adds latency to the critical path, and the training signal formulation introduces bias for close-page predictions.

**CRAFT's distinction from learning-based schemes.** Learning-based approaches rely on indirect features to predict the appropriate policy, inherently introducing estimation error and training overhead. CRAFT observes that precharge outcomes (right, wrong, and conflict) already encode the necessary feedback signal directly: whether timeout was too short (wrong), too long (conflict), or appropriate (right). This direct feedback approach enables CRAFT to achieve superior performance with significantly less storage overhead.

### 7.5 Architectural and Circuit-Level Approaches

Several works address row buffer performance through DRAM microarchitecture or circuit modifications rather than controller-level policy.

Subramanian et al. [Subramanian+18b] proposed Closed-yet-Open DRAM, which introduces isolation and equalization transistors to enable Simultaneous Read and Precharge (SRP). Rohbani et al. [Rohbani+21] proposed PF-DRAM, which eliminates precharge entirely by sensing bitlines from their previous voltage state rather than a fixed VDD/2 reference. Gulur et al. [Gulur+12] proposed Multiple Sub-Row Buffers (MSRB), which replace each bank's single row buffer with multiple smaller sub-row buffers to capture temporal locality across multiple rows simultaneously.

These circuit-level approaches are orthogonal to CRAFT: they modify the DRAM chip itself to reduce or eliminate precharge penalties, whereas CRAFT operates purely at the memory controller level within existing DRAM standards.

### 7.6 Other Related Approaches

Rixner et al. [Rixner+00] introduced First-Ready scheduling (FR-FCFS), which prioritizes row-buffer-hit requests within the memory access scheduler. FR-FCFS has been widely adopted as the standard baseline in DRAM scheduling research and is orthogonal to the page policy decision addressed by CRAFT.

Ghasempour et al. [Ghasempour+16] proposed HAPPY, which replaces per-row tracking with per-address-bit tracking: two counters per physical address bit position, with a majority vote determining the open/close decision. This reduces storage complexity from O(N) to O(log N) and can be applied to both access-based and timeout-based predictors. As a storage compression technique for prediction state, HAPPY is orthogonal to CRAFT and could potentially be combined with CRAFT's feedback mechanism.

Xie et al. [Xie+13] proposed combining application-aware page policy with OS-level bank partitioning, assigning the open-page policy to high-locality applications and the closed-page policy to others. Mi et al. [Mi+09] adopted a software approach with PARBLO, using initialization loops to control physical page allocation and improve DRAM row buffer locality for scientific workloads. Lee et al. [Lee+08] proposed prefetch-aware DRAM controllers (PADC) that adapt scheduling priority based on per-core prefetch accuracy, demonstrating that prefetch quality fundamentally affects row buffer management decisions. These works illustrate the interplay between page policy and other system layers. Such cross-layer approaches are complementary to CRAFT's per-bank adaptive timeout mechanism.

# CRAFT Paper

## Project Overview

This repository contains the draft and materials for the research paper **"CRAFT: Exploiting Precharge Cost Asymmetry for Adaptive DRAM Row Buffer Management"**.

CRAFT is a lightweight, feedback-driven DRAM row buffer management scheme that uses the cost asymmetry of precharge outcomes (right/wrong/conflict) to adaptively adjust timeout values per bank, achieving superior IPC with only 140 B/channel hardware overhead.

## Repository Structure

论文每个大章节有一个独立的 markdown 文件，这样每个文件可以聚焦一个章节的内容：

- `draft.md` — 完整论文大纲（保留作为总览参考）
- `intro.md` — Section 1: Introduction
- `background.md` — Section 2: Background & Motivation
- `design.md` — Section 3: CRAFT Design
- `methodology.md` — Section 4: Methodology
- `evaluation.md` — Section 5: Evaluation
- `discussion.md` — Section 6: Discussion
- `related_work.md` — Section 7: Related Work
- `conclusion.md` — Section 8: Conclusion
- `figures/` — 论文图表

## Related Data & Code

The simulation infrastructure and experimental data live in a sibling directory:

- `/root/data/smartPRE/` — Contains ChampSim + DRAMSim3 co-simulation code, experiment results, and analysis documents
  - `champsim-la/` — Modified ChampSim simulator with CRAFT implementation
  - `docs/analysis/` — Analysis documents (timeout distribution, row buffer hit rate, storage overhead, etc.)
  - `docs/experiments/` — Experiment result summaries (e.g., `craft_final_evaluation.md`)

## Writing Conventions

- The draft uses mixed Chinese/English: Chinese for narrative/argumentation notes, English for technical terms, tables, and pseudocode
- `【TODO】` markers indicate figures or content that still need to be created
- Data sources are referenced as file paths to analysis documents in `/root/data/smartPRE/docs/`

## Writing Style (English Prose)

本论文目标发表于计算机体系结构顶级会议（ISCA / MICRO / HPCA / ASPLOS），英文正文必须采用正式学术写作风格：

- **语域**：使用正式学术英语，避免口语化、随意或对话式表达
- **用词**：优先使用精确的技术术语，避免非正式词汇（如用 "parameter" 而非 "knob"；用 "lacks interpretability" 而非 "is a black box"；用 "approximately" 而非 "~" 在正文行文中）
- **句式**：使用完整的从句结构，避免括号插入语；需要补充说明时，改用从句或独立句子
- **禁止括号定义术语**：英文正文中禁止使用括号来解释或定义术语（如 "a wrong precharge (premature closure before ...)"）。术语应在首次出现时通过独立句子或从句自然引入，不得用括号内嵌释义
- **禁止破折号和冒号引出解释**：英文正文中禁止使用 em dash（—）或冒号（:）来引出解释性内容，两者都属于非正式写法。需要引出解释时用句号断成独立句子，或改写为从句结构
- **并列事实拆句**：当一个句子用 ", and" 连接两个独立的事实或论点时，应拆成两个独立句子。每句承载一个论点，避免句子过长、信息密度过高（如 "A reduces X, but B is consumed by Y, and each Z requires W" 应拆为两句）
- **比较措辞**：讨论他人工作的局限性时措辞应客观、有分寸（如 "presents scalability challenges" 而非 "scales poorly"），避免贬义措辞
- **与 CRAFT 的对比**：区分段落中与自身工作的比较应基于可量化的技术差异，语气保持客观中立
- **数字与单位**：十以内的数字在正文中拼写（如 "seven features"），技术参数保持数字形式（如 "512-entry"）；单位与数字之间加空格（如 "140 B per channel"）
- **引用格式**：使用 "Awasthi et al. [Awasthi+11] proposed..." 而非 "[11] proposes..."，保持过去时态描述已有工作

## Key Baselines

| Scheme | Description |
|--------|-------------|
| ABP    | Per-row access-based predictor (~20 KB/ch) |
| DYMPL  | 7-feature perceptron + PRT (3.39 KB/ch) |
| INTAP  | Mistake counter + fixed step (~200 B/ch) |

## Key Results

- CRAFT vs ABP/DYMPL/INTAP: +7.73%/+3.10%/+2.84% GEOMEAN IPC improvement
- Hardware: 140 B/channel (35 bits/bank × 32 banks)

## Figure Style Guide

所有论文图表必须遵循统一的配色和字体方案（定义在 `figures/common.py`）。

### Color Palette

| Key          | Hex       | Usage              |
|--------------|-----------|--------------------|
| open_page    | `#4472C4` | Steel blue — Open-Page 策略 |
| closed_page  | `#C0504D` | Brick red — Closed-Page 策略 |
| craft        | `#548235` | Forest green — CRAFT (our method) |
| abp          | `#8B8B8B` | Slate gray — ABP baseline |
| dympl        | `#ED7D31` | Sandy orange — DYMPL baseline |
| intap        | `#7030A0` | Medium purple — INTAP baseline |

Dark variants for text annotations (COLORS_DARK):

| Key          | Hex       |
|--------------|-----------|
| open_page    | `#2B5080` |
| closed_page  | `#8B2F2F` |
| craft        | `#3B5E25` |
| abp          | `#555555` |
| dympl        | `#B85A15` |
| intap        | `#4A1F6E` |

### Font & Style

- **Font family**: sans-serif
- **Base font size**: 10pt
- **Axes linewidth**: 0.8
- **Bar edge**: white, linewidth 0.5
- **Grid**: y-axis only, linestyle ':', alpha 0.3
- **Loss/annotation text**: 7pt, bold, use COLORS_DARK
- **Axis labels**: 11pt; tick labels 9pt, rotation 35° (for bar charts)
- **Legend**: 10pt, upper center, framealpha 0.9, gray edge, no fancybox
- **Output**: PNG (300 dpi) + PDF, bbox_inches='tight'

### Usage

所有画图脚本应 `from common import *` 并调用 `setup_style()` 初始化样式，使用 `savefig(fig, name)` 保存。不要在单独脚本里硬编码颜色或字体参数。

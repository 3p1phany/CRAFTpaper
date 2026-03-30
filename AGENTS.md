# CRAFTpaper Repository Guide

## 项目概述

本仓库用于撰写和维护论文 **CRAFT: Exploiting Precharge Cost Asymmetry for Adaptive DRAM Row Buffer Management** 的稿件、图表、审阅意见与相关阅读笔记。

论文主题聚焦于 DRAM row buffer management。仓库内同时包含：

- 论文主稿与历史拆分章节
- LNCS/会议投稿用 LaTeX 版本
- 生成论文图表的 Python 脚本与导出结果
- 审稿意见、修改计划与演讲稿草稿
- DRAM 相关论文精读笔记

## 当前工作约定

- **论文内容修改默认在 `craft_appt.md` 中进行。** 这是当前最明确的 Markdown 主稿。
- `intro.md`、`background.md`、`design.md`、`methodology.md`、`evaluation.md`、`discussion.md`、`related_work.md`、`conclusion.md` 等拆分章节主要作为历史参考，除非用户明确要求，否则不要把它们当作主编辑入口。
- `paper/samplepaper.tex` 是 LNCS LaTeX 版本，适合排版、投稿格式整理与最终 PDF 生成；若只做内容层面的修改，优先先改 `craft_appt.md`，再按需要同步到 LaTeX。

## 仓库结构

### 论文正文与草稿

- `craft_appt.md`：当前整合后的 Markdown 主稿。
- `draft.md`：较早的完整草稿/总览版本。
- `abstract.md`：摘要单独草稿。
- `intro.md` ~ `conclusion.md`：按章节拆分的历史版本。

### LaTeX 稿件

- `paper/samplepaper.tex`：当前 LaTeX 论文源文件。
- `paper/refs.bib`：BibTeX 参考文献库。
- `paper/samplepaper.pdf`：当前已生成 PDF。
- `paper/llncs.cls`、`paper/splncs04.bst`、`paper/readme.txt`：LNCS 模板文件。

### 图表与绘图脚本

- `figures/common.py`：统一颜色、字体、尺寸、数据读取与 `savefig()` 逻辑。
- `figures/fig_*.py`：论文主图脚本，如 IPC、ablation、timing diagram、feedback loop 等。
- `figures/phase_rbh.py`、`figures/plot_per_bank_rhr.py`：阶段性/分析类图表脚本。
- `figures/output/`：导出的 PNG/PDF 图像，供 Markdown 与 LaTeX 引用。

### 审阅与计划文档

- `craft_appt_review.md`：针对 `craft_appt.md` 的分章节审阅意见。
- `review_comments.md`：更细粒度的 reviewer-style 反馈。
- `fix_plan.md`、`APPT_TRIMMING_PLAN.md`：修改/裁剪计划。
- `appt2026_review.md`：APPT 相关审阅记录。

### 其他材料

- `awesome-paper-note/`：DRAM 与内存控制器相关论文精读笔记，不是主稿的一部分。
- `CLAUDE.md`：此前的仓库说明与写作约定，可作为协作参考。
- `paper-polish.skill`、`.claude/`：AI 协作或工具配置文件。
- `3641853.pdf`、`LaTeX2e+Proceedings+Templates+download.zip`、`paper/3240302.3240314.pdf`：参考资料/模板或论文 PDF，一般只读。

## 外部依赖关系

- 多个图表脚本依赖外部实验结果目录：`/root/data/smartPRE/champsim-la/results`。
- 该路径在 `figures/common.py` 中通过 `RESULTS_DIR` 写死；若环境变化，先调整该路径再重跑绘图脚本。
- `figures/output/` 中的图片是生成产物，不建议手工编辑。

## 推荐编辑策略

- **写论文内容**：优先修改 `craft_appt.md`。
- **调图或重绘图表**：修改 `figures/*.py`，然后重新生成 `figures/output/*`。
- **改参考文献**：修改 `paper/refs.bib`。
- **改投稿排版**：修改 `paper/samplepaper.tex`，不要直接改 `.aux`、`.bbl`、`.blg`、`.fls`、`.fdb_latexmk`、`.synctex.gz`、`.log`、`.pdf` 等生成文件。
- **查背景工作或 related work**：优先参考 `awesome-paper-note/` 与 `references.md`。

## 写作与协作风格

- 正式论文英文应保持体系结构论文风格：精确、克制、避免口语化表达。
- 中文文档主要用于批注、计划、review 和内部讨论。
- 除非用户明确要求，否则不要顺手重写整篇论文，也不要大规模同步所有历史章节文件。
- 做仓库整理时，优先保留“主稿 / 生成脚本 / 生成产物 / 历史参考”之间的边界。

## 生成文件处理规则

默认不要手工编辑以下内容：

- `figures/output/*`
- `paper/samplepaper.pdf`
- `paper/samplepaper.aux`
- `paper/samplepaper.bbl`
- `paper/samplepaper.blg`
- `paper/samplepaper.fdb_latexmk`
- `paper/samplepaper.fls`
- `paper/samplepaper.log`
- `paper/samplepaper.synctex.gz`
- `figures/texput.log`

## 备注

- `awesome-paper-note/` 目录下有独立 `.git`，可视为嵌套仓库/独立资料区；不要把它与主论文源码混为一体。
- 若任务涉及“最终稿”但未明确格式，先确认用户要的是 `craft_appt.md` 版本还是 `paper/samplepaper.tex` 版本，再进行大改。

# Section-by-Section Editing Guide

Detailed guidance for polishing each section of a CS research paper. Read the relevant section when the user provides text from that part of the paper.

## Table of Contents
1. [Abstract](#abstract)
2. [Introduction](#introduction)
3. [Background & Motivation](#background--motivation)
4. [Related Work](#related-work)
5. [Methodology / Design](#methodology--design)
6. [Evaluation](#evaluation)
7. [Discussion](#discussion)
8. [Conclusion](#conclusion)
9. [Rebuttal / Response to Reviewers](#rebuttal)

---

## Abstract

**Target**: 150-250 words (check venue guidelines). Every word must earn its place.

**Structure template**:
```
[Context: 1-2 sentences setting up the domain and why it matters]
[Problem: 1 sentence stating the specific problem]
[Gap/Limitation: 1 sentence on why existing solutions fall short — optional but powerful]
[Approach: 1-2 sentences describing your key idea, not implementation details]
[Results: 1-2 sentences with concrete numbers]
[Impact: 1 sentence on broader significance — optional]
```

**Checklist**:
- No undefined acronyms (define on first use, or avoid entirely in abstract)
- No citations
- No vague claims without numbers — "significantly" means nothing without a percentage
- Present tense for the system description, past tense for experiments
- First sentence should NOT start with "In recent years" or "With the rapid development of"
- The abstract should be self-contained — a reader should understand the contribution without reading the paper

**Common problems to fix**:
- Starting with "This paper proposes..." — weak opening; start with context/problem
- Listing too many implementation details instead of the key insight
- Missing concrete results ("improves performance" → "improves throughput by 23%")
- Ending with "experimental results show that our method is effective" — too vague

---

## Introduction

**Target**: 1-1.5 pages for a conference paper. This is the most important section for acceptance.

**Narrative arc**:
1. **Hook** (1 paragraph): Establish the domain and why it matters NOW. Connect to a real, pressing need. Use a compelling statistic or trend if available.
2. **Problem** (1 paragraph): Narrow to the specific problem. What exactly is broken, slow, inefficient, or missing?
3. **Existing approaches and their limitations** (1-2 paragraphs): Show that you understand the landscape. Explain WHY current solutions are insufficient — not just THAT they are.
4. **Key insight / Our approach** (1 paragraph): What is the core idea? What makes your approach different? This should be the "aha" moment.
5. **Results preview** (1 paragraph): Headline numbers. Make the reviewer want to keep reading.
6. **Contributions** (1 paragraph or bullet list): 3-4 specific, concrete contributions. Each should be verifiable by reading the paper.

**Language patterns to use**:
- "However, existing approaches suffer from..." (transition to gap)
- "To address this challenge, we propose..." (transition to solution)
- "Our key insight is that..." (highlight the core idea)
- "Specifically, we make the following contributions:" (lead into list)

**Language patterns to avoid**:
- "The rest of this paper is organized as follows" — wastes space; cut or make very brief
- "To the best of our knowledge, this is the first work to..." — only if truly novel and you're certain
- "In this paper, we propose a novel..." — "novel" is for reviewers to decide, not authors

**Checklist**:
- Does the first paragraph make a non-expert care about this problem?
- Is the gap between existing work and the ideal clearly stated?
- Is the key insight clearly articulated in one sentence?
- Are contributions specific ("We design an X that achieves Y") not vague ("We study X")?
- Do the contribution claims match what the evaluation actually validates?

---

## Background & Motivation

**Purpose**: Give readers enough context to understand your approach, and motivate WHY the problem needs a new solution.

**Tips**:
- Use a motivating example or case study early — concrete beats abstract
- If including a profiling study or characterization, present data in figures/tables and discuss implications
- Define all terminology that a reviewer outside your subfield might not know
- Keep it focused — only include background that is necessary for understanding YOUR paper
- End with a clear statement of the problem or design goals that flows into the next section

**Common problems**:
- Too long / too textbook-like — this is not a survey
- Missing connection between background and the actual problem
- Motivating data without clear takeaways ("Figure 1 shows X" — so what?)

---

## Related Work

**Purpose**: Position your work in the landscape. Show you know the field. Differentiate.

**Structure options**:
- By approach category (e.g., "Hardware-based approaches", "Software-based approaches")
- By problem dimension (e.g., "Row buffer management", "Scheduling policies", "Refresh optimization")
- Chronological within each category

**Key principle**: Compare and contrast, don't just summarize.

**Good patterns**:
- "Unlike [X] which targets Y, our approach addresses Z by..."
- "[A] and [B] both exploit C; however, they do not consider D, which is critical for..."
- "While these approaches are effective for E, they fall short when F because..."

**Bad patterns**:
- "[Author] proposed [method]. [Author2] proposed [method2]. [Author3] proposed [method3]." — list-style with no analysis
- Being dismissive: "Previous work has many limitations" — be specific and fair
- Missing recent work from the last 1-2 years

---

## Methodology / Design

**Purpose**: Describe your solution precisely enough for reproduction and clearly enough for understanding.

**Structure**: Top-down. Start with the high-level overview/architecture, then drill into each component.

**Tips**:
- Lead with a system overview figure and walk through it
- Define all notation in a table or inline before first use
- Use consistent terminology — pick one name for each concept and stick with it
- Each subsection should start by saying what problem it addresses
- Explain design decisions and trade-offs, not just what you did
- Cross-reference figures and algorithms from the text

**Checklist**:
- Is there an overview figure?
- Are all symbols/variables defined before use?
- Can a graduate student in the same area implement this from the description?
- Are design choices justified (not just described)?
- Is the scope of each component clear?

---

## Evaluation

**Purpose**: Convincingly demonstrate that your approach works and is better than alternatives.

**Structure**:
1. **Experimental setup** (1 subsection): Simulator/platform, configuration, workloads, baselines, metrics — all clearly stated. Use a table for simulator parameters.
2. **Main results** (1-2 subsections): Performance comparison with baselines. Lead with the most important metric.
3. **Analysis** (1-2 subsections): Break down WHY your approach works. Ablation studies. Sensitivity analysis.
4. **Overhead / Cost** (1 subsection): Area, power, latency overhead. Reviewers will ask if you don't include this.

**Tips**:
- Every figure and table MUST be discussed in the text — if it's not worth discussing, remove it
- State specific numbers: "X achieves 15.3% higher IPC than Y on average across Z workloads"
- Use geometric mean for speedup, arithmetic mean for absolute metrics
- Discuss outliers and negative results — they add credibility
- Compare against the strongest baselines, not just straw men

**Common problems**:
- "As shown in Figure 5, our method outperforms the baseline" — too vague; state the numbers
- Inconsistent terminology between text and figure labels
- Missing error bars or variance information
- Claiming statistical significance without statistical tests
- Cherry-picking benchmarks

---

## Discussion

**Purpose**: Address limitations, generalization, and implications honestly.

**Include**:
- Known limitations and when the approach may not work well
- Assumptions and their implications
- Generalization to other domains or configurations
- Comparison with orthogonal approaches (can they be combined?)

---

## Conclusion

**Target**: Half a page. Should be self-contained.

**Structure**:
1. Restate the problem (1 sentence)
2. Summarize the approach and key insight (2-3 sentences)
3. Highlight main results (2-3 sentences with numbers)
4. Future work (1-2 sentences, specific not vague)

**Avoid**: Copy-pasting from the abstract. The conclusion should feel like a wrap-up, not a repeat.

---

## Rebuttal

**Purpose**: Address reviewer concerns directly and persuasively within strict space limits.

**Format**: Address each reviewer separately. Quote or paraphrase their concern, then respond.

**Tips**:
- Be respectful even if the reviewer misunderstood — it's your job to be clear
- Lead with the most impactful response (new experiment, corrected analysis)
- If you ran additional experiments, include the numbers
- If you can't address a concern, acknowledge it honestly and explain what you'll do in the revision
- Be concise — every word counts in a rebuttal

**Patterns**:
- "We thank the reviewer for this insightful comment. [Address directly]"
- "We agree that [X] is important. We have added [Y] to clarify. Specifically, ..."
- "We respectfully disagree because [evidence]. However, we will add a discussion of [Z] to address this concern."

**Avoid**:
- Defensive or combative tone
- "We believe the reviewer may have missed..." — rephrase more diplomatically
- Promising major changes you can't deliver in the revision period

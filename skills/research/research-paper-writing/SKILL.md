---
name: research-paper-writing
title: Research Paper Writing Pipeline
description: "Use when writing, revising, or submitting ML/AI research papers for NeurIPS/ICML/ICLR/ACL/AAAI/COLM: experiments, analysis, drafting, review, submission."
version: 1.1.0
author: Orchestra Research
license: MIT
dependencies: [semanticscholar, arxiv, habanero, requests, scipy, numpy, matplotlib, SciencePlots]
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Research, Paper Writing, Experiments, ML, AI, NeurIPS, ICML, ICLR, ACL, AAAI, COLM, LaTeX, Citations, Statistical Analysis]
    category: research
    related_skills: [arxiv, subagent-driven-development, plan]
    requires_toolsets: [terminal, files]

---

# Research Paper Writing Pipeline

End-to-end, iterative pipeline for publication-ready ML/AI papers targeting **NeurIPS, ICML, ICLR, ACL, AAAI, and COLM**: experiment design, execution, monitoring, analysis, drafting, review, revision, submission. Not linear — results trigger new experiments, reviews trigger new analysis. Phases: 0 Setup, 1 Literature Review, 2 Experiment Design, 3 Execution & Monitoring, 4 Analysis (feeds back to 2 or 5), 5 Drafting, 6 Self-Review, 7 Submission, 8 Post-Acceptance.

## When To Use This Skill

- **Starting a new research paper** from an existing codebase or idea; **designing and running experiments** to support paper claims; **writing or revising** any section
- **Preparing for submission** to a specific conference or workshop; **responding to reviews**; **converting** a paper between conference formats
- **Writing non-empirical papers** — theory, survey, benchmark, or position papers (see [Paper Types Beyond Empirical ML](#paper-types-beyond-empirical-ml))
- **Designing human evaluations** for NLP, HCI, or alignment research; **preparing post-acceptance deliverables** — posters, talks, code releases

## Core Philosophy

1. **Be proactive.** Deliver complete drafts, not questions — something concrete to react to, then iterate.
2. **Never hallucinate citations.** AI-generated citations have ~40% error rate. Always fetch programmatically. Mark unverifiable citations as `[CITATION NEEDED]`.
3. **Paper is a story, not a collection of experiments.** One clear contribution in a single sentence — if you can't, the paper isn't ready.
4. **Experiments serve claims.** Every experiment must explicitly state which claim it supports.
5. **Commit early, commit often.** Every completed experiment batch and draft update gets a descriptive commit; git log is the experiment history.

**Proactivity by confidence**: High (clear repo, obvious contribution) — full draft, deliver, iterate. Medium — draft with flagged uncertainties. Low (major unknowns) — ask 1-2 targeted questions via `clarify`, then draft. Flag assumptions with the draft ("Framed contribution as X — adjust if needed"). **Block for input only when**: target venue unclear, multiple contradictory framings, results seem incomplete, explicit request to review first.

## Phase 0: Project Setup

**0.1 Explore the repository** — find `README.md` (overview and claims), `results/`/`outputs/`/`experiments/`, `configs/`, `.bib` files, draft notes:

```bash
ls -la
find . -name "*.py" | head -30
find . -name "*.md" -o -name "*.txt" | xargs grep -l -i "result\|conclusion\|finding"
```
**0.2 Organize the workspace**:

```
workspace/
  paper/               # LaTeX source, figures, compiled PDFs
  experiments/         # Experiment runner scripts
  code/                # Core method implementation
  results/             # Raw experiment results (auto-generated)
  tasks/               # Task/benchmark definitions
  human_eval/          # Human evaluation materials (if needed)
```
**0.3 Version control**:

```bash
git init  # if not already
git remote add origin <repo-url>
git checkout -b paper-draft  # or main
```
Commit message style: `Add Monte Carlo constrained results (5 runs, Sonnet 4.6, policy memo task)`. **0.4 Identify the contribution** — **What** (single contribution), **Why** (evidence), **So What** (why readers care). Propose: "The main contribution is: [one sentence]. The key results show [Y]. Is this the framing you want?" **0.5 Create a TODO list** with `todo`: contribution, literature review, design experiments, run, analyze, first draft, self-review, revise, submission prep. Persistent state across sessions.

**0.6 Estimate compute budget** (then track actual spend as experiments run):

```
Compute Budget Checklist:
- [ ] API costs: (model price per token) × (estimated tokens per run) × (number of runs)
- [ ] GPU hours: (time per experiment) × (number of experiments) × (number of seeds)
- [ ] Human evaluation costs: (annotators) × (hours) × (hourly rate)
- [ ] Total budget ceiling and contingency (add 30-50% for reruns)
```
```python
# Simple cost tracker pattern
import json, os
from datetime import datetime

COST_LOG = "results/cost_log.jsonl"

def log_cost(experiment: str, model: str, input_tokens: int, output_tokens: int, cost_usd: float):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "experiment": experiment,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": cost_usd,
    }
    with open(COST_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
```

Budget tight: pilot first (1-2 seeds, task subset); debug on cheaper models, final runs on target models. **0.7 Multi-author coordination** — most papers have 3-10 authors. Workflows: **Overleaf** (simultaneous editing, no git), **Git + LaTeX** (`.gitignore` aux files, branch review), **Overleaf + Git sync**. **Section ownership**: one primary author per section; others comment only — prevents merge conflicts and style drift.

```
Author Coordination Checklist:
- [ ] Agree on section ownership (who writes what)
- [ ] Set up shared workspace (Overleaf or git repo)
- [ ] Establish notation conventions (before anyone writes)
- [ ] Schedule internal review rounds (not just at the end)
- [ ] Designate one person for final formatting pass
- [ ] Agree on figure style (colors, fonts, sizes) before creating figures
```
**LaTeX conventions early**: `\method{}` macro; `\citet{}` vs `\citep{}` usage; math notation (lowercase bold vectors, uppercase bold matrices); British vs American spelling.

## Phase 1: Literature Review

Find related work, identify baselines, gather citations. **1.1 Identify seed papers** already referenced in the codebase:

```bash
grep -r "arxiv\|doi\|cite" --include="*.md" --include="*.bib" --include="*.py"
find . -name "*.bib"
```
**1.2 Search for related work** — load the `arxiv` skill (`skill_view("arxiv")`): arXiv REST API search, Semantic Scholar citation graphs, author profiles, BibTeX generation. `web_search` for broad discovery, `web_extract` for specific papers:

```
web_search("[main technique] + [application domain] site:arxiv.org")
web_search("[baseline method] comparison ICML NeurIPS 2024")
web_extract("https://arxiv.org/abs/2303.17651")
```
**Recommended**: install **Exa MCP** for real-time academic search: `claude mcp add exa -- npx -y mcp-remote "https://mcp.exa.ai/mcp"`. **1.2b Deepen the search** (breadth-first, then depth) — a flat one-round search misses related work. **Round 1 (Breadth)**: 4-6 parallel queries from different angles ("[method] + [domain]", "[problem] state-of-the-art", "[baseline] comparison", "[alternative] vs [your approach]"). **Round 2 (Depth)**: follow-ups from Round 1 — new terminology, papers cited by the most relevant results, contradictory findings. **Round 3 (Targeted)**: fill gaps — missing baselines, concurrent work (last 6 months), key negative results. **Stop** when a round returns >80% already-collected papers (typically 2-3 rounds; surveys 4-5). Agent-based: delegate each round via parallel `delegate_task`, deduplicate, generate the next round from the combined learnings.

### Step 1.3: Verify Every Citation

**NEVER generate BibTeX from memory. ALWAYS fetch programmatically.**

```
Citation Verification (MANDATORY per citation):
1. SEARCH → Query Semantic Scholar or Exa MCP with specific keywords
2. VERIFY → Confirm paper exists in 2+ sources (Semantic Scholar + arXiv/CrossRef)
3. RETRIEVE → Get BibTeX via DOI content negotiation (programmatically, not from memory)
4. VALIDATE → Confirm the claim you're citing actually appears in the paper
5. ADD → Add verified BibTeX to bibliography
If ANY step fails → mark as [CITATION NEEDED], inform scientist
```

```python
# Fetch BibTeX via DOI
import requests

def doi_to_bibtex(doi: str) -> str:
    response = requests.get(
        f"https://doi.org/{doi}",
        headers={"Accept": "application/x-bibtex"}
    )
    response.raise_for_status()
    return response.text
```
Full search-then-fetch in `execute_code`:

```python
from semanticscholar import SemanticScholar
sch = SemanticScholar()
results = sch.search_paper("attention mechanism transformers", limit=5)
for paper in results:
    doi = paper.externalIds.get('DOI', 'N/A')
    if doi != 'N/A':
        print(doi_to_bibtex(doi))
```
If you cannot verify a citation:

```latex
\cite{PLACEHOLDER_author2024_verify_this}  % TODO: Verify this citation exists
```
**Always tell the scientist**: "I've marked [X] citations as placeholders that need verification." See [references/citation-workflow.md](references/citation-workflow.md) for complete API documentation and the full `CitationManager` class. **1.4 Organize related work** by methodology, not paper-by-paper. **Good**: "One line of work uses X's assumption [refs] whereas we use Y's assumption because..." **Bad**: "Smith et al. introduced X. Jones et al. introduced Y. We combine both."

## Phase 2: Experiment Design

Every experiment answers a specific question. **2.1 Map claims to experiments** — "Our method outperforms baselines" needs the main comparison (Table 1) with win rate and significance; "Effect is larger for weaker models" needs a model scaling study with a monotonic improvement curve; "Convergence requires scope constraints" needs constrained vs unconstrained with convergence rates. **Rule**: if an experiment doesn't map to a claim, don't run it.

**2.2 Design baselines** — they separate accepted from rejected papers (reviewers ask "Did they compare against X?"). Categories: **naive** (simplest possible), **strong** (best known existing method), **ablation** (your method minus one component), **compute-matched** (same budget, different allocation). **2.3 Define the evaluation protocol** before running anything: **metrics** (with direction symbols), **aggregation** across runs/tasks, **statistical tests**, **sample sizes**.

**2.4 Write experiment scripts.** **Incremental saving** (crash recovery):
```python
# Save after each problem/task
result_path = f"results/{task}/{strategy}/result.json"
if os.path.exists(result_path):
    continue  # Skip already-completed work
# ... run experiment ...
with open(result_path, 'w') as f:
    json.dump(result, f, indent=2)
```
**Artifact preservation** — `results/<experiment>/<task>/<strategy>/` holds `final_output.md`, `history.json` (full trajectory), `pass_01/` (per-iteration artifacts). **Separation of concerns**: `run_experiment.py`, `run_baselines.py`, `run_comparison_judge.py` (blind evaluation), `analyze_results.py`, `make_charts.py`.

See [references/experiment-patterns.md](references/experiment-patterns.md) for complete design patterns, cron monitoring, and error recovery.

### Step 2.5: Design Human Evaluation (If Applicable)

Many NLP/HCI/alignment papers need human evaluation. Design **before** automated experiments — longer lead times (IRB approval, annotator recruitment). **Needed when** automated metrics miss what you care about (fluency, helpfulness, safety), the contribution is about human-facing qualities, or ACL/EMNLP expect it for generation tasks. **Key design decisions** — annotator type (expert, crowdworker, end-user): match to claims. Scale (Likert 1-5, pairwise, ranking): pairwise beats Likert for LLM outputs. Sample size: power analysis or minimum 100 items, 3+ annotators. Agreement metric (Cohen's kappa, Krippendorff's alpha, ICC): Krippendorff's alpha for >2 annotators; report raw agreement too. Platform: Prolific (quality), MTurk (scale), internal (domain expertise).

```
Annotation guideline checklist:
- [ ] Clear task description with examples (good AND bad)
- [ ] Decision criteria for ambiguous cases
- [ ] At least 2 worked examples per category
- [ ] Attention checks / gold standard items (10-15% of total)
- [ ] Qualification task or screening round
- [ ] Estimated time per item and fair compensation (>= local minimum wage)
- [ ] IRB/ethics review if required by your institution
```
**Reporting requirements** (reviewers check all): annotator count and qualifications; inter-annotator agreement with metric and value; compensation and estimated hourly rate; annotation interface screenshot (appendix); total annotation time. See [references/human-evaluation.md](references/human-evaluation.md) for statistical tests for human eval data, crowdsourcing quality control patterns, and IRB guidance.

## Phase 3: Experiment Execution & Monitoring

**3.1 Launch experiments** — `nohup` for long runs; run independent experiments in parallel, but 4+ concurrent experiments on the same API slow each down (rate limits):

```bash
nohup python run_experiment.py --config config.yaml > logs/experiment_01.log 2>&1 &
echo $!  # Record the PID
```
**3.2 Set up monitoring (cron pattern)** — periodic checks for long-running experiments follow this template:

```
Monitor Prompt Template:
1. Check if process is still running: ps aux | grep <pattern>
2. Read last 30 lines of log: tail -30 <logfile>
3. Check for completed results: ls <result_dir>
4. If results exist, read and report: cat <result_file>
5. If all done, commit: git add -A && git commit -m "<descriptive message>" && git push
6. Report in structured format (tables with key metrics)
7. Answer the key analytical question for this experiment
```
**Silent mode**: if nothing changed since the last check, respond with `[SILENT]` to suppress notification; only report news. **3.3 Handle failures** — API rate limit / credit exhaustion (402/429 in logs): wait, re-run (scripts skip completed work). Process crash (PID gone, incomplete results): re-run from last checkpoint. Timeout on hard problems (stuck, no log progress): kill and skip, note in results. Wrong model ID (errors reference the model name): fix and re-run. **Key**: always check for existing results and skip completed work — re-runs stay safe. **3.4 Commit completed results:** `git add -A && git commit -m "Add <experiment name>: <key finding in 1 line>" && git push`. **3.5 Maintain an experiment journal** — git tracks what happened, not the **exploration tree** (what to try next based on what you learned). Append per attempt to `experiment_journal.jsonl`:

```json
{
  "id": "exp_003",
  "parent": "exp_001",
  "timestamp": "2025-05-10T14:30:00Z",
  "hypothesis": "Adding scope constraints will fix convergence failure from exp_001",
  "plan": "Re-run autoreason with max_tokens=2000 and fixed structure template",
  "config": {"model": "haiku", "strategy": "autoreason", "max_tokens": 2000},
  "status": "completed",
  "result_path": "results/exp_003/",
  "key_metrics": {"win_rate": 0.85, "convergence_rounds": 3},
  "analysis": "Scope constraints fixed convergence. Win rate jumped from 0.42 to 0.85.",
  "next_steps": ["Try same constraints on Sonnet", "Test without structure template"],
  "figures": ["figures/exp003_convergence.pdf"]
}
```
The journal tracks why you tried X, what you learned, what it implies next — invaluable for Methods ("we observed X, which motivated Y") and honest failure reporting. When the tree branches, pick the path that best supports the claims; document dead ends in the appendix as ablations or negative results. **Snapshot code per experiment**: `cp experiment.py results/exp_003/experiment_snapshot.py`

## Phase 4: Result Analysis

**4.1 Aggregate results:**

```python
import json, os
from pathlib import Path

results = {}
for result_file in Path("results/").rglob("result.json"):
    data = json.loads(result_file.read_text())
    strategy = result_file.parent.name
    task = result_file.parent.parent.name
    results.setdefault(strategy, {})[task] = data

for strategy, tasks in results.items():
    scores = [t["score"] for t in tasks.values()]
    print(f"{strategy}: mean={np.mean(scores):.1f}, std={np.std(scores):.1f}")
```
**4.2 Statistical significance** — always: **error bars** (std or standard error — say which), **95% CIs** for key results, **McNemar's test** for two methods, **effect sizes** (Cohen's d or h). Implementations: [references/experiment-patterns.md](references/experiment-patterns.md).

**4.3 Identify the story** — (1) main finding in one sentence; (2) what surprised you — unexpected results often make the best papers; (3) what failed — honest reporting strengthens the paper; (4) what follow-up is needed. **Handling negative or null results:** hypothesis wrong but the **why** is informative — frame the paper around the analysis of why (NeurIPS, ICML if the analysis is rigorous). Method doesn't beat baselines but **reveals something new** — reframe the contribution as understanding/analysis (ICLR values understanding; workshop papers). Clean negative result on a popular claim — write it up, the field needs to know (NeurIPS Datasets & Benchmarks, TMLR, workshops). Results inconclusive, no clear story — pivot; don't force a paper that isn't there.

**Writing a negative results paper**: lead with what the community believes and why testing it matters; methodology must be airtight (reviewers scrutinize harder); present the null result with statistical evidence; analyze **why** the expected result didn't materialize; discuss implications. **Venues that welcome negative results**: NeurIPS D&B track, TMLR, ML Reproducibility Challenge, workshops.

**4.4 Create figures and tables** — figures: vector (PDF) via `plt.savefig('fig.pdf')`; colorblind-safe palettes (Okabe-Ito or Paul Tol); self-contained captions; no title inside the figure. Tables: `booktabs`; bold best per metric; direction symbols (higher/lower better); consistent decimals.

```latex
\usepackage{booktabs}
\begin{tabular}{lcc}
\toprule
Method & Accuracy $\uparrow$ & Latency $\downarrow$ \\
\midrule
Baseline & 85.2 & 45ms \\
\textbf{Ours} & \textbf{92.1} & 38ms \\
\bottomrule
\end{tabular}
```
**4.5 Decide: more experiments or write?** Claims supported and significant — Phase 5. Inconclusive, or an unexpected finding opens a new direction — Phase 2. Missing one ablation reviewers will ask for — run it, then Phase 5. All done but some failed — note failures, move to Phase 5. **4.6 Write the experiment log** (`experiment_log.md`) — the key bridge between experiments and writeup; without it the writing agent re-derives the story from raw files (a common source of hallucinated numbers):

```markdown
# Experiment Log

## Contribution (one sentence)
[The paper's main claim]

## Experiments Run

### Experiment 1: [Name]
- **Claim tested**: [Which paper claim this supports]
- **Setup**: [Model, dataset, config, number of runs]
- **Key result**: [One sentence with the number]
- **Result files**: results/exp1/final_info.json
- **Figures generated**: figures/exp1_comparison.pdf
- **Surprising findings**: [Anything unexpected]

## Figures
| Filename | Description | Which section it belongs in |
|----------|-------------|---------------------------|
| figures/main_comparison.pdf | Bar chart comparing all methods on benchmark X | Results, Figure 2 |
| figures/ablation.pdf | Ablation removing components A, B, C | Results, Figure 3 |

## Failed Experiments (document for honesty)
- [What was tried, why it failed, what it tells us]

## Open Questions
- [Anything the results raised that the paper should address]
```
Commit this log alongside the results it describes.

## Iterative Refinement: Strategy Selection

Strategy choice for refining any output (drafts, scripts, analysis), grounded in the autoreason research:

Mid-tier model + constrained task: **Autoreason** — sweet spot, gap is widest, baselines destroy weak model outputs. Mid-tier + open task: **Autoreason** with scope constraints (fixed facts, structure, deliverable to bound the improvement space). Frontier + constrained: **Autoreason** — wins 2/3 even at frontier. Frontier + unconstrained: **critique-and-revise** or **single pass** — model self-evaluates well enough. Concrete technical task (system design): **critique-and-revise** — direct find-and-fix is more efficient. Template-filling (one correct structure): **single pass** or **conservative** — iteration adds no value. Code with test cases: **Autoreason (code variant)** — structured analysis of *why* it failed before fixing; recovery rate 62% vs 43%. Very weak model (Llama 8B class): **single pass** — too weak for diverse candidates.

**The generation-evaluation gap** — autoreason's value tracks the gap between generation and self-evaluation capability. Weak (Llama 8B): both poor, no value. Mid (Haiku 3.5): LARGE gap, MAXIMUM value — 42/42 perfect Borda. Frontier (S4.6): small gap — only with constraints. The gap is structural: today's frontier becomes tomorrow's mid-tier; the sweet spot moves but never disappears.

**Applying autoreason to paper drafts** (gotchas): **provide ground truth to the critic** — actual experimental data, result JSONs, statistical outputs; without it models hallucinate fabricated ablation studies and fake confidence intervals. **3 working judges minimum** — a broken judge parser doesn't add noise, it prevents equilibrium entirely. **Scope constrain the revision** — "Address these specific weaknesses" not "improve the paper." Full loop (Critic, Author B, Synthesizer, blind Judge Panel with Borda count), parameters (k=2 convergence; temperature 0.8 authors, 0.3 judges; conservative tiebreak; fresh isolated agents), and failure modes (no convergence, synthesis drift, degradation below single pass, overfitting, broken judges): [references/autoreason-methodology.md](references/autoreason-methodology.md).

## Phase 5: Paper Drafting

The complete drafting procedure (section-by-section order, LaTeX scaffolding, figure/table conventions, abstract and intro formulas, related-work positioning) lives in `references/phase5-paper-drafting.md` — load it with `read_file` when you reach this phase. Pair it with `references/writing-guide.md` for prose-level style rules.

## Phase 6: Self-Review & Revision

### Step 6.1: Simulate Reviews (Ensemble Pattern)

Ensemble reviewing with a meta-reviewer beats a single pass. **Step 1: Generate N independent reviews** (N=3-5; different models or temperatures; each sees only the paper). **Default to negative bias** — LLMs have a well-documented positivity bias in evaluation.

```
You are an expert reviewer for [VENUE]. You are critical and thorough.
If a paper has weaknesses or you are unsure about a claim, flag it clearly
and reflect that in your scores. Do not give the benefit of the doubt.

Evaluate: 1. Soundness (claims well-supported? baselines fair and strong?)
2. Clarity (could an expert reproduce it?) 3. Significance (does this matter?)
4. Originality (new insights, not just incremental combination?)

Provide your review as structured JSON:
{
  "summary": "2-3 sentence summary",
  "strengths": ["strength 1", "strength 2", ...],
  "weaknesses": ["weakness 1 (most critical)", "weakness 2", ...],
  "questions": ["question for authors 1", ...],
  "missing_references": ["paper that should be cited", ...],
  "soundness": 1-4,
  "presentation": 1-4,
  "contribution": 1-4,
  "overall": 1-10,
  "confidence": 1-5
}
```
**Step 2: Meta-review (Area Chair aggregation)** — feed all N reviews to a meta-reviewer:

```
You are an Area Chair at [VENUE]. You have received [N] independent reviews
of a paper. Your job is to:
1. Identify consensus strengths and weaknesses across reviewers
2. Resolve disagreements by examining the paper directly
3. Produce a meta-review that represents the aggregate judgment
4. Use AVERAGED numerical scores across all reviews
Be conservative: if reviewers disagree on whether a weakness is serious,
treat it as serious until the authors address it.
Reviews: [review_1] [review_2] ...
```
**Step 3: Reflection loop** (optional, 2-3 rounds): reviewers refine after seeing the meta-review; early-termination sentinel: "I am done" (no changes). **Model selection**: strongest available model, independent of the writing model. **Few-shot calibration**: 1-2 real published reviews from the venue as examples — dramatically improves calibration. See [references/reviewer-guidelines.md](references/reviewer-guidelines.md). **6.1b Visual review pass (VLM)** — text-only review misses figure quality, layout, visual consistency. With a vision-capable model, run a separate **visual review** of the compiled PDF:

```
You are reviewing the visual presentation of this research paper PDF. Check for:
1. Figure quality: plots readable, labels legible, colors distinguishable
2. Figure-caption alignment: does each caption accurately describe its figure?
3. Layout: orphaned headers, awkward page breaks, figures far from references
4. Table formatting: aligned columns, consistent decimals, bold best results
5. Visual consistency: same color scheme and font sizes across figures
6. Grayscale readability: understandable if printed in B&W?
For each issue, specify the page number and exact location.
```
**6.1c Claim verification pass.** (The VLM pass catches what text review cannot: illegible axis labels, a figure 3 pages from its reference, inconsistent palettes, a table wider than the column.)

```
Claim Verification Protocol:
1. Extract every factual claim from the paper (numbers, comparisons, trends)
2. For each claim, trace it to the specific experiment/result that supports it
3. Verify the number in the paper matches the actual result file
4. Flag any claim without a traceable source as [VERIFY]
```
Agent-based: delegate to a **fresh sub-agent** receiving only the paper text and raw result files — fresh context prevents confirmation bias (the verifier doesn't "remember" what the results were supposed to be). **6.2 Prioritize feedback** — **Critical** (technical flaw, missing baseline): must fix, may send you back to Phase 2. **High** (clarity, missing ablation): fix in this revision. **Medium** (minor writing): if time allows. **Low** (style): future work. **6.3 Revision cycle** — per critical/high issue: identify affected sections, draft the fix, verify it doesn't break other claims, update, re-check against the reviewer's concern.

**6.4 Rebuttal writing** — point-by-point, one entry per reviewer concern:
```
> R1-W1: "The paper lacks comparison with Method X."

We thank the reviewer for this suggestion. We have added a comparison with 
Method X in Table 3 (revised). Our method outperforms X by 3.2pp on [metric] 
(p<0.05). We note that X requires 2x our compute budget.
```
**Rules**: address every concern (reviewers notice skips); lead with the strongest responses; be concise (reviewers read dozens); include new results run during the rebuttal period; never be defensive or dismissive, even of weak criticisms; `latexdiff` for a marked-up PDF; thank for specific, actionable feedback. **NOT**: "we respectfully disagree" without evidence; "out of scope" without explanation; answering only strengths while ignoring a weakness. **6.5 Paper evolution tracking** — snapshot at milestones: `paper.tex` (working), `paper_v1_first_draft.tex`, `paper_v2_post_review.tex`, `paper_v3_pre_submission.tex`, `paper_v4_camera_ready.tex`.

## Phase 7: Submission Preparation

**7.1 Conference checklist** — incomplete checklists can cause desk rejection. See [references/checklists.md](references/checklists.md) for the NeurIPS 16-item paper checklist, ICML broader impact + reproducibility, ICLR LLM disclosure policy, ACL mandatory limitations section, and universal pre-submission checklist. **7.2 Anonymization checklist** — double-blind review: reviewers cannot know who wrote the paper.

```
Anonymization Checklist:
- [ ] No author names or affiliations anywhere in the PDF
- [ ] No acknowledgments section (add after acceptance)
- [ ] Self-citations written in third person: "Smith et al. [1] showed..." not "We previously showed [1]..."
- [ ] No GitHub/GitLab URLs pointing to your personal repos
- [ ] Use Anonymous GitHub (https://anonymous.4open.science/) for code links
- [ ] No institutional logos or identifiers in figures
- [ ] No file metadata containing author names (check PDF properties)
- [ ] No "our previous work" or "in our earlier paper" phrasing
- [ ] Dataset names don't reveal institution (rename if needed)
- [ ] Supplementary materials don't contain identifying information
```
**Common mistakes**: git commit messages in supplementary code, watermarked figures from institutional tools, acknowledgments left from a previous draft, arXiv preprint posted before the anonymity period. **7.3 Formatting verification:**

```
Pre-Submission Format Check:
- [ ] Page limit respected (excluding references and appendix)
- [ ] All figures are vector (PDF) or high-res raster (600 DPI PNG)
- [ ] All figures readable in grayscale
- [ ] All tables use booktabs
- [ ] References compile correctly (no "?" in citations)
- [ ] No overfull hboxes in critical areas
- [ ] Appendix clearly labeled and separated
- [ ] Required sections present (limitations, broader impact, etc.)
```

### Step 7.4: Pre-Compilation Validation

Run these automated checks **before** `pdflatex` — catching errors here is faster than debugging compiler output. Fix any warnings before proceeding; agent-based, feed chktex output back to the agent with instructions to make minimal fixes.

```bash
# 1. Lint with chktex (catches common LaTeX mistakes)
# Suppress noisy warnings: -n2 (sentence end), -n24 (parens), -n13 (intersentence), -n1 (command terminated)
chktex main.tex -q -n2 -n24 -n13 -n1

# 2. Verify all citations exist in .bib
python3 -c "
import re
tex = open('main.tex').read()
bib = open('references.bib').read()
cites = set(re.findall(r'\\\\cite[tp]?{([^}]+)}', tex))
for cite_group in cites:
    for cite in cite_group.split(','):
        cite = cite.strip()
        if cite and cite not in bib:
            print(f'WARNING: \\\\cite{{{cite}}} not found in references.bib')
"

# 3. Verify all referenced figures exist on disk
python3 -c "
import re, os
tex = open('main.tex').read()
figs = re.findall(r'\\\\includegraphics(?:\[.*?\])?{([^}]+)}', tex)
for fig in figs:
    if not os.path.exists(fig):
        print(f'WARNING: Figure file not found: {fig}')
"

# 4. Check for duplicate \label definitions
python3 -c "
import re
from collections import Counter
tex = open('main.tex').read()
labels = re.findall(r'\\\\label{([^}]+)}', tex)
dupes = {k: v for k, v in Counter(labels).items() if v > 1}
for label, count in dupes.items():
    print(f'WARNING: Duplicate label: {label} (appears {count} times)')
"
```

### Step 7.5: Final Compilation

```bash
# Clean build
rm -f *.aux *.bbl *.blg *.log *.out *.pdf
latexmk -pdf main.tex

# Or manual (triple pdflatex + bibtex for cross-references)
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex

# Verify output exists and has content
ls -la main.pdf
```
**If compilation fails**: parse the `.log` for the first error — "Undefined control sequence" (missing package or typo), "Missing $ inserted" (math outside math mode), "File not found" (wrong figure path or missing .sty), "Citation undefined" (.bib entry missing or bibtex not run). **7.6 Conference-specific requirements** — **NeurIPS**: paper checklist in appendix, lay summary if accepted. **ICML**: Broader Impact Statement (after conclusion, doesn't count toward limit). **ICLR**: LLM disclosure, reciprocal reviewing agreement. **ACL**: mandatory Limitations section, Responsible NLP checklist. **AAAI**: strict style file, no modifications whatsoever. **COLM**: frame contribution for the language model community. **7.7 Conference resubmission & format conversion** — **never copy LaTeX preambles between templates**. Start fresh with the target template (`cp -r templates/icml2026/ new_submission/`), copy ONLY content (abstract, text, figures, tables, bib entries — not preamble), adjust for page limits, add required sections, update references.

Conversions: **NeurIPS to ICML** (9 to 8 — cut 1 page, add Broader Impact), **ICML to ICLR** (8 to 9 — expand experiments, LLM disclosure), **NeurIPS to ACL** (9 to 8 — NLP conventions, Limitations), **ICLR to AAAI** (9 to 7 — big cuts, strict style), **Any to COLM** (varies to 9 — LM focus). Cutting: proofs to appendix, condense related work, combine tables, subfigures. Expanding: ablations, limitations, baselines, qualitative examples. **After rejection**: address reviewer concerns but never reference the previous submission (blind review). **7.8 Camera-ready preparation (post-acceptance):**

```
Camera-Ready Checklist:
- [ ] De-anonymize: add author names, affiliations, email addresses
- [ ] Add Acknowledgments section (funding, compute grants, helpful reviewers)
- [ ] Add public code/data URL (real GitHub, not anonymous)
- [ ] Address any mandatory revisions from meta-reviewer
- [ ] Switch template to camera-ready mode (if applicable — e.g., AAAI \anon → \camera)
- [ ] Add copyright notice if required by venue
- [ ] Update any "anonymous" placeholders in text
- [ ] Verify final PDF compiles cleanly
- [ ] Check page limit for camera-ready (sometimes differs from submission)
- [ ] Upload supplementary materials (code, data, appendix) to venue portal
```
**7.9 arXiv & preprint strategy** — double-blind venue (NeurIPS/ICML/ACL): post **after** the submission deadline; posting before can technically violate anonymity policies, though enforcement varies. ICLR: explicitly allows arXiv before submission; don't put author names in the submission itself. Already on arXiv, submitting to a new venue: acceptable at most venues; do NOT update the arXiv version during review with changes that reference reviews. Workshop paper: arXiv fine any time (typically not double-blind). Establishing priority: post immediately if scooping is a concern; accept the anonymity tradeoff.

**Categories** (primary + 1-2 cross-lists, only where genuinely relevant): `cs.LG` (general ML), `cs.CL` (NLP/LLMs), `cs.AI` (reasoning, planning, agents), `cs.CV` (vision), `cs.IR` (search, recommendation).

**Versioning**: v1 matches the conference submission; v2 post-acceptance with camera-ready corrections (add "accepted at [Venue]" to abstract); never post v2 during review with changes responding to reviewer feedback.

```bash
# Check if your paper's title is already taken on arXiv (before choosing a title)
pip install arxiv
python -c "
import arxiv
results = list(arxiv.Search(query='ti:\"Your Exact Title\"', max_results=5).results())
print(f'Found {len(results)} matches')
for r in results: print(f'  {r.title} ({r.published.year})')
"
```

### Step 7.10: Research Code Packaging

Clean, runnable code increases citations and reviewer trust.

```
your-method/
  README.md              # Setup, usage, reproduction instructions
  requirements.txt       # Or environment.yml for conda
  setup.py               # For pip-installable packages
  LICENSE                # MIT or Apache 2.0 recommended for research
  configs/               # Experiment configurations
  src/                   # Core method implementation
  scripts/               # Training, evaluation, analysis scripts
    train.py
    evaluate.py
    reproduce_table1.sh  # One script per main result
  data/                  # Small data or download scripts
    download_data.sh
  results/               # Expected outputs for verification
```
**README template for research code:**

```markdown
# [Paper Title]

Official implementation of "[Paper Title]" (Venue Year).

## Setup
[Exact commands to set up environment]

## Reproduction
To reproduce Table 1: `bash scripts/reproduce_table1.sh`
To reproduce Figure 2: `python scripts/make_figure2.py`

## Citation
[BibTeX entry]
```
**Pre-release checklist:**
```
- [ ] Code runs from a clean clone (test on fresh machine or Docker)
- [ ] All dependencies pinned to specific versions
- [ ] No hardcoded absolute paths
- [ ] No API keys, credentials, or personal data in repo
- [ ] README covers setup, reproduction, and citation
- [ ] LICENSE file present (MIT or Apache 2.0 for max reuse)
- [ ] Results are reproducible within expected variance
- [ ] .gitignore excludes data files, checkpoints, logs
```
**Anonymous code for submission**: upload the repo to Anonymous GitHub (https://anonymous.4open.science/), get an anonymous URL, put it in the paper.

## Phase 8: Post-Acceptance Deliverables

**8.1 Conference poster** — size: check venue requirements (typically 24"x36" or A0). Content: title, authors, 1-sentence contribution, method figure, 2-3 key results, conclusion. Flow: top-left to bottom-right (Z-pattern) or columnar. Text: title readable at 3m, body at 1m; bullets only. Figures: reuse paper figures at higher resolution, enlarge the key result. Tools: LaTeX (`beamerposter`), PowerPoint/Keynote, Figma, Canva. Order 2+ weeks ahead; fabric is lighter for travel.

**8.2 Conference talk / spotlight** — **Spotlight** (5 min): problem, approach, one key result; rehearse to exactly 5 minutes. **Oral** (15-20 min): full story with ablations and limitations. **Workshop** (10-15 min): adapt background to the audience. Slides: one idea per slide; minimal text; animate key figures step-by-step; end with a takeaway slide; prepare backup slides.

**8.3 Blog post / social media** — **Twitter/X thread**: 5-8 tweets, lead with the result not the method, include Figure 1 and the key result figure. **Blog post**: 800-1500 words for ML practitioners; skip formalism, emphasize intuition and practical implications. **Project page**: abstract, figures, demo, code link, BibTeX — GitHub Pages. **Timing**: within 1-2 days of proceedings or arXiv camera-ready.

## Workshop & Short Papers

Workshops: 4-6 pages, lower completeness bar, usually single-blind or light review, value interesting ideas/preliminary results/position pieces, arXiv anytime, contribution bar is a novel direction or interesting negative result. Main conference: 7-9 pages, must be complete and thorough, double-blind rigorous review, complete empirical story with strong baselines, arXiv timing matters, significant advance with strong evidence. **Target a workshop for** early-stage ideas wanting feedback, negative results that don't justify 8+ pages, position pieces, replication studies. **ACL types**: Long (8 pages, complete study), Short (4 pages, one focused contribution), Findings (8 pages, solid work that narrowly missed the main conference). **Short paper strategy**: pick ONE claim and support it thoroughly — don't compress a long paper into 4 pages, write a different, more focused paper.

## Paper Types Beyond Empirical ML

See [references/paper-types.md](references/paper-types.md) for detailed guidance on each type. **Theory papers** — Introduction, Preliminaries (definitions, notation), Main Results (theorems), Proof Sketches, Discussion, Full Proofs (appendix). Contribution is a theorem, bound, or impossibility result; proofs are the evidence; experiments optional. Proof writing: all assumptions explicit; intuition before formal proof ("The key insight is..."); sketches convey the main idea in 0.5-1 page; use `\begin{proof}...\end{proof}`; number assumptions and reference them ("Under Assumptions 1-3, ..."). **Survey / tutorial papers** — Introduction, Taxonomy / Organization, Detailed Coverage, Open Problems, Conclusion. Contribution is organization, synthesis, open-problem identification. Must be comprehensive within scope (reviewers check for missing references); requires a clear taxonomy. Venues: TMLR (survey track), JMLR, Foundations and Trends in ML, ACM Computing Surveys.

**Benchmark papers** — Introduction, Task Definition, Dataset Construction, Baseline Evaluation, Analysis, Intended Use & Limitations. Contribution is the benchmark itself — must fill a genuine evaluation gap. Dataset documentation mandatory (Datasheets); must show baselines don't saturate it and that it measures what you claim (construct validity). Venues: NeurIPS Datasets & Benchmarks track, ACL (resource papers), LREC-COLING. **Position papers** — Introduction, Background, Thesis / Argument, Supporting Evidence, Counterarguments, Implications. Contribution is an argument, not a result; must engage seriously with counterarguments; evidence can be empirical, theoretical, or logical. Venues: ICML (position track), workshops, TMLR.

## Hermes Agent Integration

**Related skills:** **arxiv** (Phase 1: arXiv search, BibTeX, Semantic Scholar — `skill_view("arxiv")`), **subagent-driven-development** (Phase 5: parallel section writing, 2-stage review — `skill_view("subagent-driven-development")`), **plan** (Phase 0: plans in `.hermes/plans/` — `skill_view("plan")`), **qmd** (Phase 1: local KBs, hybrid BM25+vector — `skill_manage("install", "qmd")`), **diagramming** (Phase 4-5: Excalidraw figures — `skill_view("diagramming")`), **data-science** (Phase 4: Jupyter live kernel — `skill_view("data-science")`).

**This skill supersedes `ml-paper-writing`** (contains all its content plus the experiment/analysis pipeline and autoreason methodology). **Tools:** `terminal` (LaTeX compilation, git, experiments, process checks — see phases). `process` — background experiments: `process("start", ...)`, `process("poll", pid)`, `process("log", pid)`, `process("kill", pid)`. `execute_code` — Python for citation verification, statistics, aggregation (tool access via RPC). `read_file`/`write_file`/`patch` — paper editing; use `patch` for targeted edits to large .tex files. `web_search`/`web_extract` — literature discovery and citation verification. `delegate_task` — parallel section drafting with isolated subagents; concurrent citation verification. `todo` — primary state tracker across sessions. `memory` — persist key decisions (contribution framing, venue choice, reviewer feedback). `cronjob` — experiment monitoring, deadline countdowns, automated arXiv checks. `clarify` — targeted questions when blocked. cron `deliver:` — notify the user when experiments complete or drafts are ready even if not in chat (the agent no longer has a `send_message` tool; outbound delivery is handled by cron/`hermes send`). **Parallel section drafting** — each delegate is a **fresh subagent** with no shared context; provide everything in the prompt, then collect and integrate: `delegate_task("Draft the Methods section based on these experiment scripts and configs. Include: pseudocode, all hyperparameters, architectural details sufficient for reproduction. Write in LaTeX using the neurips2025 template conventions.")`

**State management.** `memory` — persist key decisions (MEMORY.md bounded to ~2200 chars); update after major decisions or phase transitions:
```
memory("add", "Paper: autoreason. Venue: NeurIPS 2025 (9 pages). 
  Contribution: structured refinement works when generation-evaluation gap is wide.
  Key results: Haiku 42/42, Sonnet 3/5, S4.6 constrained 2/3.
  Status: Phase 5 — drafting Methods section.")
```
`todo` — granular progress: `todo("add", "Design constrained task experiments for Sonnet 4.6")`, `todo("update", id=3, status="in_progress")`.

**Session startup protocol:**
```
1. todo("list")                           # Check current task list
2. memory("read")                         # Recall key decisions
3. terminal("git log --oneline -10")      # Check recent commits
4. terminal("ps aux | grep python")       # Check running experiments
5. terminal("ls results/ | tail -20")     # Check for new results
6. Report status to user, ask for direction
```
**Cron monitoring** — schedule the Step 3.2 monitor template via `cronjob` (e.g. `"schedule": "*/30 * * * *"`, prompt ending "If nothing changed: respond with [SILENT]"). **Deadline tracking** — same pattern, `"schedule": "0 9 * * *"`, prompt computing days remaining (e.g. "NeurIPS 2025 deadline: May 22"), checking the todo list, warning if <7 days remain. **Communication.** Notify (final response, or cron `deliver:` for unattended runs) on: batch completed (with results table), unexpected finding or failure needing a decision, draft ready for review, deadline near with incomplete tasks. Otherwise `[SILENT]`. **Report format** — always structured:
```
## Experiment: <name>
Status: Complete / Running / Failed

| Task | Method A | Method B | Method C |
|------|---------|---------|---------|
| Task 1 | 85.2 | 82.1 | **89.4** |

Key finding: <one sentence>
Next step: <what happens next>
```
**Decision points requiring human input** (`clarify`, when genuinely blocked): target venue (before starting — affects page limits, framing), contribution framing (multiple valid framings), experiment priority (more experiments than time allows), submission readiness. **Do NOT ask about** (be proactive, make a choice, flag it): word choice, section ordering, which results to highlight, citation completeness (draft with what you find, note gaps).

## Reviewer Evaluation Criteria

Reviewers check **Quality** (soundness, well-supported claims, fair baselines), **Clarity** (reproducible by experts, consistent notation), **Significance** (community impact), **Originality** (new insights — doesn't require a new method). **NeurIPS 6-point scale**: 6 Strong Accept, 5 Accept (solid, high impact), 4 Borderline Accept, 3 Borderline Reject (weaknesses outweigh), 2 Reject (technical flaws), 1 Strong Reject (known results or ethics issues).

See [references/reviewer-guidelines.md](references/reviewer-guidelines.md) for detailed guidelines, common concerns, and rebuttal strategies.

## Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| Abstract too generic | Delete first sentence if it could prepend any ML paper. Start with your specific contribution. |
| Introduction exceeds 1.5 pages | Split background into Related Work. Front-load contribution bullets. |
| Experiments lack explicit claims | Add: "This experiment tests whether [specific claim]..." before each one. |
| Reviewers find paper hard to follow | Add signposting, use consistent terminology, make figure captions self-contained. |
| Missing statistical significance | Add error bars, number of runs, statistical tests, confidence intervals. |
| Scope creep in experiments | Every experiment must map to a specific claim. Cut experiments that don't. |
| Paper rejected, need to resubmit | See Conference Resubmission in Phase 7. Address reviewer concerns without referencing reviews. |
| Missing broader impact statement | Most venues require it. "No negative impacts" is almost never credible. |
| Human eval criticized as weak | See Step 2.5 and [references/human-evaluation.md](references/human-evaluation.md). Report agreement metrics, annotator details, compensation. |
| Reviewers question reproducibility | Release code (Step 7.10), document all hyperparameters, include seeds and compute details. |
| Theory paper lacks intuition | Add proof sketches with plain-language explanations before formal proofs. See [references/paper-types.md](references/paper-types.md). |
| Results are negative/null | See Phase 4.3 on handling negative results. Consider workshops, TMLR, or reframing as analysis. |

## Reference Documents

- [references/writing-guide.md](references/writing-guide.md) — Gopen & Swan 7 principles, Perez micro-tips, Lipton word choice, Steinhardt precision, figure design. [references/citation-workflow.md](references/citation-workflow.md) — citation APIs, Python code, CitationManager class, BibTeX management.
- [references/checklists.md](references/checklists.md) — NeurIPS 16-item, ICML, ICLR, ACL requirements, universal pre-submission checklist. [references/reviewer-guidelines.md](references/reviewer-guidelines.md) — evaluation criteria, scoring, common concerns, rebuttal template.
- [references/sources.md](references/sources.md) — bibliography of all writing guides, conference guidelines, APIs. [references/experiment-patterns.md](references/experiment-patterns.md) — experiment design patterns, evaluation protocols, monitoring, error recovery.
- [references/autoreason-methodology.md](references/autoreason-methodology.md) — autoreason loop, strategy selection, model guide, prompts, scope constraints, Borda scoring. [references/human-evaluation.md](references/human-evaluation.md) — human evaluation design, annotation guidelines, agreement metrics, crowdsourcing QC, IRB guidance.
- [references/paper-types.md](references/paper-types.md) — theory papers (proof writing, theorem structure), survey papers, benchmark papers, position papers.

**LaTeX templates** in `templates/` for **NeurIPS 2025**, **ICML 2026**, **ICLR 2026**, **ACL**, **AAAI 2026**, **COLM 2025**; see [templates/README.md](templates/README.md) for compilation instructions. **Key external sources:**
- [Neel Nanda: How to Write ML Papers](https://www.alignmentforum.org/posts/eJGptPbbFPZGLpjsp/highly-opinionated-advice-on-how-to-write-ml-papers)
- [Sebastian Farquhar: How to Write ML Papers](https://sebastianfarquhar.com/on-research/2024/11/04/how_to_write_ml_papers/)
- [Gopen & Swan: Science of Scientific Writing](https://cseweb.ucsd.edu/~swanson/papers/science-of-writing.pdf)
- [Lipton: Heuristics for Scientific Writing](https://www.approximatelycorrect.com/2018/01/29/heuristics-technical-scientific-writing-machine-learning-perspective/)
- [Perez: Easy Paper Writing Tips](https://ethanperez.net/easy-paper-writing-tips/)

**APIs:** [Semantic Scholar](https://api.semanticscholar.org/api-docs/) | [CrossRef](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) | [arXiv](https://info.arxiv.org/help/api/basics.html)

**Venues:** [NeurIPS](https://neurips.cc/Conferences/2025/PaperInformation/StyleFiles) | [ICML](https://icml.cc/Conferences/2025/AuthorInstructions) | [ICLR](https://iclr.cc/Conferences/2026/AuthorGuide) | [ACL](https://github.com/acl-org/acl-style-files)

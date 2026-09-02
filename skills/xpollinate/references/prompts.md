# Prompt templates

Fill the placeholders in angle brackets. Do not add framing beyond what the
template specifies; extra framing is how the coordinator's prior leaks into
agents that are supposed to be independent.

Placeholders used throughout:

- `<USER_PROMPT>`: the user's request, verbatim, including typos
- `<HARD_QUESTION>`: the single question every agent must answer (SKILL.md
  Setup step 2)
- `<REPORT_PATH>`: where the agent writes its report, e.g.
  `xpollinate/<slug>/reports/03-market-stance.md`
- `<STANCE_NAME>`, `<ANCHOR_IDEAS>`: from `stances.md`
- `<CONTEXT>`: any files, repo paths, or PR diff the task is about. Give the
  same context to every agent. Give NO context about prior conclusions,
  existing architecture documents that answer the question, or the
  coordinator's own view.

## Contents

1. Control prompt
2. Stance prompt
3. Red-team prompt (initial)
4. Cross-pollination prompt
5. Red-team prompt (final pass on synthesis)
6. Audit prompt (prior work)
7. Pre-commit template (coordinator's own file)
8. Design file template
9. Synthesis template

---

## 1. Control prompt

The control gets nothing but the user's prompt and shared context. Its
purpose is to measure what the model produces by default. Resist the urge to
add "think carefully" or a format request; that is steering.

```
<USER_PROMPT>

<CONTEXT>

Write your full answer to <REPORT_PATH>.
```

If the user's prompt did not itself ask for a written answer, append exactly
one line: "Answer in full, then state explicitly: <HARD_QUESTION>". Keep the
hard question phrased identically across all agents.

## 2. Stance prompt

```
You are answering the following request from the intellectual standpoint of
<STANCE_NAME>. Treat this standpoint as your native discipline: use its
literature, its methods, its standards of evidence, and its characteristic
objections. Anchor ideas to draw on (not an exhaustive list, and not a
required conclusion): <ANCHOR_IDEAS>.

The request:

<USER_PROMPT>

<CONTEXT>

Requirements:
- Research as needed. Cite specific sources, systems, papers, or precedents
  by name; do not cite generically.
- Give a concrete answer, not a survey. If the answer is a design, specify
  components and how they connect. If it is a verdict, state it and what
  would reverse it.
- You must explicitly answer this question, in its own section:
  <HARD_QUESTION>
- Include a section titled "What this standpoint is likely to get wrong"
  and be specific.
- Include a section titled "How to falsify this answer": a concrete test
  that would show the answer is wrong.

Write your full report to <REPORT_PATH>.
```

## 3. Red-team prompt (initial)

```
Your job is to attack the following request before anyone answers it.

The request:

<USER_PROMPT>

<CONTEXT>

Part 1 (required, do this first, be thorough): argue that the request is
ill-posed. Consider: internal contradictions; scope that deletes the only
feedback channel that could validate a result; terms that sound precise but
have no operational definition; assumptions that the relevant literature or
history has already refuted; ways the request could be satisfied trivially or
vacuously; and what a competent skeptic in the relevant field would say.
Name specific evidence, studies, precedents, or failures.

Part 2 (only after Part 1): state the maximum honest version. What is the
strongest claim or deliverable that survives every objection in Part 1, and
what is the minimal design or approach that earns it? Be as concrete here as
you were critical above.

In both parts, address this question explicitly: <HARD_QUESTION>

Write your full report to <REPORT_PATH>.
```

## 4. Cross-pollination prompt

Send this by resuming the integrating agent (the one whose report is being
revised), so it retains its own reasoning and must defend or retract it.

```
Another analyst answered the same request from a different standpoint. Their
full report is at <OTHER_REPORT_PATH> (or pasted below). Read all of it.

Produce a revised version of your own answer that integrates theirs. This is
not a summary of both; it is your design, v2, changed by contact with theirs.

Specifically:
1. Their strongest point against your answer is: <NAMED_OBJECTION>. Either
   change your answer to meet it, or explain precisely why it does not
   apply. Do not restate the objection more softly and move on.
2. Your answer's known weakness is: <NAMED_WEAKNESS>. Their report contains
   a mechanism that may fix it: <NAMED_MECHANISM>. Adopt it, adapt it, or
   reject it with a stated reason.
3. You and they disagree about: <NAMED_DISAGREEMENT>. Resolve it. State the
   rule that resolves it in one sentence.
4. (When both independently invented similar mechanisms) You both proposed
   a version of <SHARED_MECHANISM>. Produce ONE unified version with a
   decision rule, and say which parts of each original were dropped and why.

List every retraction you make, in a section titled "Retracted". A revision
with no retractions is suspicious; if you truly retract nothing, say why.

Write the revised report to <MERGE_REPORT_PATH>.
```

For the red team versus a threatened report, the integrating agent is the
threatened report's author, and item 1 becomes: "Walk through every objection
in Part 1 of the red-team report. For each, either answer it with a mechanism
or write 'accepted' and state what you lose. Then defend the things your
design has that their Part 2 lacks, or concede they are unnecessary."

## 5. Red-team prompt (final pass on synthesis)

Resume the original red-team agent.

```
The synthesis of all reports, including your own, is at <SYNTHESIS_PATH>.

Do not re-argue your original Part 1. Instead:

A. Scorecard. For each objection you originally raised, classify the
   synthesis's response as one of: answered by mechanism (name the
   mechanism), absorbed rhetorically (the problem was renamed or relocated,
   not solved; say where it moved to), or still standing.

B. Merge-created seams. The synthesis was assembled from components that
   were each defended in isolation. Hunt for:
   - Components that are individually fine but in combination reconstitute
     a pattern the synthesis itself bans
   - Rules or invariants that contradict each other
   - Slogans standing in for mechanisms ("embedded in", "grounded in",
     "aligned with" without a described process)
   - Claims that survived because they were deleted from one place and
     nobody noticed they were still load-bearing elsewhere
   - Scarcity or discipline that was removed in one merge while a later
     section still relies on it
   - Places where the synthesis quietly does less than it says, or less than
     your own Part 2
   For each seam: what it is, why it is load-bearing, and the smallest
   change that would fix it (or a statement that it cannot be fixed within
   the design's stated scope).

C. Verdict. In what respects is the synthesis more than your maximum honest
   version, in what respects is it secretly less, and which of the reports'
   claims rest only on the advocates' own evidence.

Write to <REPORT_PATH>.
```

## 6. Audit prompt (prior work)

```
Audit the documents in <PRIOR_WORK_PATH> for bias in how they were produced.
Do not evaluate whether their conclusions are correct; evaluate whether the
process could have reached a different conclusion.

Look for, with file and line references:
- The conclusion stated before the survey (thesis in the framing)
- Identical section structure across documents presented as independent
- The same source counted more than once as independent confirmation
- Claim escalation between documents (quantifiers that grow as claims are
  summarized upward)
- Critique applied only to rejected options
- Limitations disclosed in one document and absent from siblings produced
  the same way
- The closest historical precedent for the favored approach and whether its
  canonical critique appears anywhere
- Any "discovered" or "found" claim where the thing found was supplied to
  the system in advance

Write findings to <REPORT_PATH>. Quote briefly; cite locations precisely.
```

## 7. Pre-commit template

File: `00-precommit.md`. Written by the coordinator before any report is
read.

```
# Pre-committed answer (<DATE>, before any agent report)

## The request
<one paragraph restating the brief in your own words>

## The reframe
<the insight the whole answer depends on, if any>

## The answer
<concrete design / verdict / recommendation>

## Answer to the hard question
<HARD_QUESTION>: <your answer>

## Least sure about
<two or three items>

## What would change my mind
<specific evidence or arguments>
```

## 8. Design file template

File: `01-design.md`. Written before launching agents.

```
# Xpollinate design

## Hard question
<HARD_QUESTION>

## Agents
- Control: verbatim prompt, no steering
- <STANCE_NAME>: chosen because <reason>; expected to catch <what>
- ...
- Red team: is the request ill-posed

## What convergence would prove
If the control produces the same skeleton as the stance agents, that is a
model prior, not independent confirmation. Convergence counts only where a
stance agent reaches a conclusion the control did not.

## What is withheld from all agents
<pre-commit, prior work, each other>
```

## 9. Synthesis template

File: `02-synthesis.md`.

```
# Synthesis

<DATE>. Produced from a pre-committed answer plus <N> independent agents
plus <M> cross-pollination rounds. Raw reports in reports/. The
pre-commit is 00-precommit.md; section 6 diffs against it.

## 1. Method
## 2. Convergence, discounted for the control
## 3. Where reports broke the pre-commit
## 4. The merged answer
## 5. Disputes resolved in cross-pollination
## 6. Diff against the pre-commit
## 7. Residual risks and open items
## 8. Red-team verdict (appended after final pass)
   - Scorecard of original objections
   - Merge-created seams, each with: adopted fix / partial fix / accepted
   - Verdict
```

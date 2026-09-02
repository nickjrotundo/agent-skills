---
name: xpollinate
description: >-
  Use for hard, open-ended, or high-stakes questions where a first-draft
  answer is not good enough: architecture and design decisions, "how would you
  approach X", getting oriented in an unfamiliar codebase, a serious code
  review, evaluating a plan or proposal, or re-examining earlier work that may
  be biased. Also use whenever the user asks to "get multiple perspectives",
  "red team this", or "think about this as a whole". It runs a deliberately
  expensive protocol: a pre-committed answer,
  an unsteered control agent, several agents with genuinely different
  worldviews, a red team, then cross-pollination and synthesis into a
  directory of reports. Because it costs many agents, prefer the xcheck skill
  for a single fork in the road, and do not use it for routine questions.
license: MIT
compatibility: >-
  Designed for Claude Code or similar agents that can run several subagents at
  once and resume them; a lower-fidelity single-agent fallback is documented
  in the skill.
metadata:
  author: nickjrotundo
  version: "0.1.0"
---

# Xpollinate: pre-commit, diverge, collide, synthesize, attack

## Why this protocol exists

A single model answering a hard question produces its default prior dressed up
as a conclusion. Launching several agents does not fix that by itself: if the
coordinator seeds them with its own framing, they converge, and the convergence
gets reported as independent confirmation. That is manufactured consensus, and
it is worse than a single answer because it looks like evidence.

Every step below exists to defeat one specific way that failure happens:

| Failure                                   | Countermeasure                                  |
|-------------------------------------------|-------------------------------------------------|
| Coordinator grades its own influence      | Pre-commit answer to a file before any report   |
| Conclusion smuggled into the prompt       | Control agent gets the verbatim prompt, unsteered |
| Stances that are the same stance renamed  | Stances chosen from different intellectual roots |
| Nobody asks if the question is wrong      | Red team argues the request is ill-posed        |
| Agents contaminate each other             | No agent sees the pre-commit or another report  |
| Raw evidence lost under the summary       | Reports saved verbatim before synthesis         |
| Merge produces agreement, not progress    | Pair agents for maximum productive collision    |
| Synthesis claims convergence it didn't earn | Convergence measured against the control      |
| Merge creates new holes nobody checks     | Final red-team pass hunts merge-created seams   |

Do not skip steps to save time. Skipping the pre-commit or the control quietly
turns the whole exercise back into the thing it was built to avoid.

## Setup

1. Determine the task type: exploration/design question, new-codebase
   understanding, code review, plan/proposal evaluation, or audit of prior
   work. Read `references/stances.md` for the stance library for that type.
   That file and `references/prompts.md` sit next to this one in the skill's
   own directory; read them when you reach the step that needs them, not up
   front.
2. Identify the ONE hard question every agent must answer. This is the
   question the task actually turns on, stated without hinting at an answer.
   Examples: "how do you recognize value in something that has no name yet",
   "what would have to be true for this PR to be safe to merge", "what is the
   one assumption this codebase cannot survive being wrong about".
3. Create a work directory: `<project>/xpollinate/<short-slug>/` with a
   `reports/` subdirectory. Everything below is written there.
4. If prior work on this question exists and the user asks you to ignore it or
   suspects it is biased, launch an audit agent on the prior work in parallel
   with the main run (see `references/prompts.md`, Audit prompt). Its job is to
   find where the conclusion was in the prompt, template-driven convergence,
   double counting, missing self-critique, and undisclosed limitations.

## Step 1: Pre-commit

Write your own complete answer to `00-precommit.md` BEFORE launching any
agent, or at minimum before reading any report. Include:

- The reframe or key insight the answer depends on
- The concrete proposal, decision, or verdict
- What you are least sure about
- What evidence would change your mind

Tell the user this is committed. The diff between this file and the final
synthesis is the honest measure of what the exercise bought.

## Step 2: Fan out

Launch all agents in the same turn, as background agents. Standard shape is
one control, four to six stance agents, one red team. Each agent's prompt is
built from the templates in `references/prompts.md`.

Mechanics in Claude Code: one `Agent` call per agent, all in a single message
so they run concurrently. Steps 4 and 6 require talking to the SAME agent
again with its own context intact - that is `SendMessage` addressed to the
agent, never a second `Agent` call. A fresh call there produces another first
draft instead of a defense or a retraction, which is exactly the failure this
protocol exists to prevent. If your harness cannot resume an agent, say so in
the synthesis method section and run those steps in degraded mode.

Rules for every agent prompt:

- The control gets the user's prompt verbatim. No stance, no framing, no
  context about existing work. It measures the model's default prior.
- Each stance agent gets the user's prompt plus a stance: a named intellectual
  tradition, discipline, or vantage point, with two or three anchor ideas
  from it. Stances must have different roots (a market economist and a
  cultural sociologist, not two flavors of ML researcher).
- The red team is told to argue the request is ill-posed, impossible, or
  wrongly scoped, and only then to produce the maximum honest version.
- Every agent must answer the hard question from Setup step 2 explicitly.
- No agent is told about the pre-commit, the other agents, or (when auditing
  or replacing prior work) that the prior work exists.
- Each agent writes its report to `reports/NN-<stance>.md` if it has file
  access; otherwise you save its output there yourself as soon as it returns.

Before launching, write `01-design.md`: the hard question, the list of
stances and why each was chosen, and what convergence with the control would
and would not prove.

## Step 3: Collect

As reports land, give the user one or two sentences per report: what is
distinctive about it, and whether it reinvented the same skeleton as the
control. Do NOT start synthesizing until all reports are in; partial synthesis
anchors on whichever agent was fastest.

When the control returns, note explicitly whether it reproduced your
pre-commit. If it did, that is a model prior, not confirmation, and every
later claim of convergence must be discounted for it.

Save every report verbatim before doing anything else. The raw reports are
the deliverable's evidence base; the synthesis is commentary on them.

## Step 4: Cross-pollinate

Pair reports for maximum productive collision, not maximum agreement. Good
pairings:

- Two reports whose worst failure modes are each other's strengths
- Two reports that independently invented similar mechanisms with different
  justifications (force them to produce one unified version)
- The red team against whichever report it most directly threatens (that
  report must answer every objection or explicitly take the hit)

For each pair, resume ONE of the original agents (so it keeps its own context
and has to defend its own work) and hand it the other's full report. The
prompt names the specific disagreement to resolve and the specific weakness
to fix. See `references/prompts.md`, Cross-pollination prompt.

Two or three pairings is typical. Save the results as `reports/NN-merge-<a>-x-<b>.md`.
Note where an agent retracted something; retractions are the most valuable
output of this step.

## Step 5: Synthesize

Write `02-synthesis.md` with these sections, in order:

1. Method: what was run, what the control measured, what the stances were
2. Where independent stances converged, discounted for the control (if the
   control also said it, say "model prior" not "convergence")
3. Where reports broke the pre-commit: specific claims from `00-precommit.md`
   that did not survive, and which report killed them
4. The merged answer / architecture / verdict
5. Disputes that were resolved in cross-pollination, and how
6. Diff against the pre-commit: what changed, what survived, what was added
7. Known residual risks and things still standing unresolved

Attribute every load-bearing idea to the report it came from. Ideas that
appear only in the coordinator's own text should be marked as such.

## Step 6: Final adversarial pass

Resume the red-team agent and give it the synthesis. Its brief is NOT to
re-argue its original objections; it is to hunt seams the merge itself
created: components that are individually fine but reconstitute a banned
pattern in combination, rhetorical moves standing in for mechanisms, rules
that contradict each other, and unearned claims that survived because nobody
owned them.

Save its report, then update the synthesis:

- Fold in fixes you adopt, marking them as amendments in place
- Append section 8, Red-team verdict, with a scorecard of its original
  objections (answered by mechanism / absorbed rhetorically / still standing)
  and each new seam with its status (adopted fix / partial fix / accepted
  residual risk)

Adopt a fix only if you can state the mechanism. If the best available
response is "we accept this", write that, not a softer restatement of the
problem.

## Step 7: Deliver

Commit the work directory if in a repo (do not push unless asked). Report to
the user:

- Where the synthesis lives, and that raw reports are alongside it
- The three to five findings that changed the answer most
- What the red team left standing
- The single next action the synthesis points to

Keep this short. The user can read the files.

## Degraded mode (no subagents)

Run the roles sequentially yourself, one per turn or one per clearly
separated section, writing each to its own file before starting the next.
Still pre-commit first. Still write the control answer before any stance
(it will be contaminated by your pre-commit, so say so in the design file).
This is weaker than real independence; say so in the synthesis method section.

## Scaling down

For a smaller question, the minimum honest version is: pre-commit, control,
two stances, red team, synthesis, red-team pass. Or, use xcheck if that skill
is installed and appropriate. Below that, do not call it an xpollinate; just
answer the question.

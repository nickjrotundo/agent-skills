---
name: xcheck
description: >-
  Use before interrupting the user with a question that is really a judgment
  call you could make yourself: which of two approaches to take, how to read
  an ambiguous requirement, whether to refactor or patch, what to name
  something, which library or pattern to use, or what a spec probably means
  given the surrounding code. Launch two or three decision agents from
  different vantage points, make them argue, proceed if they converge, and
  escalate only if they genuinely cannot. Reach for this even when the
  question feels quick to ask. Do NOT use for decisions the user reserved for
  themselves, irreversible or destructive actions, anything that spends money
  or touches secrets or production, changes to the scope of the task, or
  trivial choices you should just make.
license: MIT
compatibility: >-
  Designed for Claude Code or similar agents that can run several subagents at
  once and resume them; a lower-fidelity single-agent fallback is documented
  in the skill.
metadata:
  author: nickjrotundo
  version: "0.1.0"
---

# Xcheck: decide with a cross-check instead of interrupting the user

## When this applies

You were about to write something like "Do you want A or B?" or "Should I
assume X?". That interruption costs the user a context switch, and most of
the time a careful engineer with the same information would just decide. The
problem with deciding alone is that a single pass tends to pick whatever came
to mind first. Two independent opinions, forced to argue, are cheap and
usually enough.

Skip xcheck and ask the user directly when any of these hold:

- The user explicitly said to check with them on this kind of decision
- The action is hard to reverse: deleting data, force-pushing, dropping
  columns, changing public APIs, publishing, sending messages
- Money, credentials, production systems, or other people's data are involved
- The decision changes the scope or intent of the task rather than how to do it
- You lack information that only the user has (a preference, a deadline, an
  external constraint) and the agents would just be guessing at it

Skip xcheck and just decide when the choice is trivial or fully determined by
existing conventions in the codebase. Xcheck is for the middle band.

## Procedure

### 1. Frame the decision

Write it down before launching anything, in this form:

```
Decision: <one sentence>
Options: A) ... B) ... (C) ...)
Context that bears on it: <files, conventions, constraints, what the user
  has said so far>
What "correct" means here: <the criterion: least surprising to the user,
  most consistent with the repo, easiest to reverse, etc.>
```

If you cannot fill in the last line, that is a sign the decision belongs to
the user. Escalate.

### 2. Launch at least two decision agents

Launch them in the same turn, in the background, with the same framing and
context.

Mechanics in Claude Code: one `Agent` call per vantage, all in a single
message so they run concurrently. Step 3 requires talking to the SAME agent
again with its context intact, which is `SendMessage` addressed to the
agent, not a second `Agent` call - a new `Agent` call starts from nothing and
turns the cross-pollination round into two more first drafts. If your harness
has no way to resume an agent, use degraded mode below rather than faking it.

Give each a different vantage so they do not just agree by default:

- Agent 1, the user's proxy: "Decide as the person who owns this codebase
  and asked for this task would. Infer their preferences from the repo's
  conventions, history, and the wording of the request."
- Agent 2, the reviewer: "Decide as the senior engineer who will review this
  change and maintain it. Weight reversibility, consistency, and what will
  confuse the next person."
- Optional agent 3, the skeptic: "Argue that both listed options are wrong
  or that the question is being asked at the wrong level, then pick anyway."

Each agent's prompt:

```
<framing block from step 1>

Choose one option and commit to it. Give: your choice, the two strongest
reasons, the strongest reason against it, and what evidence would flip you.
Keep it under 200 words. Do not ask questions; decide with what you have.
```

Agents do not see each other's answers in this round.

### 3. Cross-pollinate

Once all answers are in, resume each agent (`SendMessage`, not a fresh
`Agent` call) with the others' answers:

```
Here are the other decision agents' answers: <answers>.
Revise your choice or defend it. If you change, say what changed your mind.
If you hold, name the exact point of disagreement in one sentence.
End with: CHOICE: <option> CONFIDENCE: <low/medium/high>
```

One round is normally enough. Run a second only if the first round moved
someone and the movement might continue.

### 4. Resolve

Consensus means all agents end on the same option, or the holdouts are at
low confidence and name no disagreement that survives the others' reasons.

- Consensus: proceed with that option. Record it (step 5) and continue the
  task. Tell the user in one line what was decided and why, so they can
  object, but do not wait for them.
- No consensus: escalate. The escalation should be better than the question
  you were originally going to ask, because you now have the disagreement in
  sharp form:

```
Need your call on: <decision>
A) <option>: <best argument, one line>
B) <option>: <best argument, one line>
The disagreement comes down to: <one sentence>
I'd lean <X> if you have no preference.
```

### 5. Record

Append to `<project>/.xcheck-decisions.md` (create if missing):

```
- <date> <decision one-liner> -> <chosen option> [consensus | escalated]
  reason: <one line>
```

The log lets a later session see what was decided and why instead of
re-litigating it, and lets the user audit the calls you made on their behalf.

## When to reach for xpollinate instead

Xcheck is the cheap version: two or three agents, one collision round, minutes.
If the question is the task rather than a fork inside it - an architecture
decision, a serious review, a plan worth arguing over, prior work you suspect
is biased - use xpollinate instead, if that skill is installed. It costs more
and buys a pre-committed answer, an unsteered control, several genuinely
different stances, and a red team.

## Degraded mode (no subagents)

Write the two vantage answers yourself, in separate clearly labeled sections,
before writing any resolution. It is weaker than independent agents because
you know your own first answer while writing the second; compensate by
writing the reviewer answer as if the user's-proxy answer is wrong and see
whether the objection holds.

## Calibration

If the user overrides an xcheck decision, note the override in the log. If
you see two or more overrides of the same kind, stop xchecking that kind of
decision and ask directly; the agents are missing a preference only the user
has.

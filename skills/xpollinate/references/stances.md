# Stance library by task type

A stance is a vantage point with its own literature, values, and failure
modes. The point of picking from different roots is that agents with
different roots disagree in informative ways; agents with the same root
disagree about details. Pick four to six per run. Always include the red
team. Always include the control (it has no stance by definition).

Each entry gives: the stance name, two or three anchor ideas to seed the
agent with, and what that stance is most likely to catch that the others
miss. Do not paste the "catches" column into the agent prompt; it is for
choosing, not steering.

## Contents

1. Exploration / design / "how would you build X"
2. Understanding a new codebase
3. Code review
4. Evaluating a plan, proposal, or strategy
5. Auditing prior work for bias
6. The red team (all task types)
7. Writing your own stances

---

## 1. Exploration / design / "how would you build X"

| Stance | Anchor ideas | Catches |
|---|---|---|
| Market / mechanism design | Hayek on prices as knowledge; prediction markets; incentive compatibility; skin in the game | Where value is claimed without anyone paying for it; gameable metrics |
| Social field / sociology of value | Csikszentmihalyi's systems model (value is conferred by a field); Becker's art worlds; institutional legitimacy | Where an internal number is being called value; where the audience is simulated |
| Embodied / enactive | Stakes and world-coupling; metabolism and death conditions; sensorimotor grounding | Systems that can never be wrong in a way that costs them; missing feedback from reality |
| Open-endedness / evolutionary search | Quality-diversity, novelty search, Goodhart, frame saturation, rediscovery traps | Value functions that pre-describe the answer; finite frames that fill up |
| Human creative practice / ethnography | Problem-finding over problem-solving; apprenticeship and taste; scenes and scenius; cool-hunting | Missing human-in-the-loop structures; treating taste as computable |
| Formal / verification-first | Oracles, proofs, kill tests, falsifiability, preregistration | Claims that cannot be settled; missing falsification criteria |
| Operations / systems engineering | Failure modes, observability, blast radius, cost of settlement vs cost of generation | Economics that only work at demo scale |

## 2. Understanding a new codebase

| Stance | Anchor ideas | Catches |
|---|---|---|
| Architecture / boundaries | Module boundaries, dependency direction, where the seams actually are vs where the docs say they are | Docs that describe an intended architecture the code does not have |
| Data flow / state | Where state lives, who mutates it, lifecycle, invariants, what happens on partial failure | Hidden coupling through shared state |
| Operator / on-call | How it is deployed, configured, observed, rolled back; what pages at 3am | Code that works but cannot be run or debugged in production |
| Historian / archaeologist | git log, dead code, TODOs, abandoned migrations, naming drift; what was tried and reverted | Why the odd parts are odd; landmines that look like cruft |
| Tester / adversary | What the tests actually cover vs claim to; what inputs nobody tried; trust boundaries | Confidence that comes from test count rather than test content |
| Domain / product | What the user of this system is trying to do; which code paths matter commercially | Effort spent understanding parts that do not matter |
| Newcomer | First-day experience: what is undocumented, what tribal knowledge is assumed, what would you get wrong | Onboarding gaps the veterans no longer see |

Hard question candidates for this type: "what is the one assumption this
codebase cannot survive being wrong about", "what would you have to know that
is written nowhere", "where does the documented design diverge from the code".

## 3. Code review

| Stance | Anchor ideas | Catches |
|---|---|---|
| Correctness / edge cases | Off-by-one, null, concurrency, ordering, partial failure, idempotency, retries | Bugs |
| Security | Trust boundaries, input validation, authz, secrets, injection, SSRF, supply chain | Vulnerabilities |
| Performance / scale | Complexity, N+1, allocation, locks, hot paths, what happens at 100x | Fine-at-demo-scale code |
| Maintainability / API design | Naming, cohesion, what the next person will misunderstand, migration path, deprecation | Correct code that is a future liability |
| Operator | Logging, metrics, feature flags, rollback, config, backward compatibility of data | Unshippable code |
| Product / intent | Does this do what the ticket asked; does the ticket ask for the right thing; user-visible behavior change | Perfect implementations of the wrong change |
| Test reviewer | Do the tests test the change or just exercise it; what would a mutation survive | Green tests that prove nothing |

Red team for code review: argue the PR should not exist, or is the wrong
scope, or solves the wrong problem, before reviewing what is there.

Hard question candidates: "what would have to be true for this to be safe to
merge", "what is the most expensive way this could be wrong six months from
now".

## 4. Evaluating a plan, proposal, or strategy

| Stance | Anchor ideas | Catches |
|---|---|---|
| Premortem | It is a year later and this failed; write the postmortem | The failure mode nobody planned for |
| Economist | Unit economics, opportunity cost, who pays, incentive alignment of every party | Plans that only work if someone else absorbs the cost |
| Incumbent / competitor | How would the party this threatens respond | Plans that assume a static world |
| Executor | Who does the work, in what order, with what dependencies; the first two weeks in detail | Plans that are goals wearing a plan costume |
| Historian | Prior attempts at this, in this org or elsewhere; why they failed | Reinventing a known failure |
| Customer / end user | What changes for the person on the receiving end; what they lose | Plans optimized for the planner |
| Regulator / ethicist | Legal exposure, harm, reputational risk, what a hostile journalist writes | Plans that are technically fine and publicly indefensible |

## 5. Auditing prior work for bias

Run this as a single audit agent in parallel with the main run, or as its
own run if the audit is the whole task. Things to hunt:

- Conclusion in the prompt: does the work state its thesis before surveying
  anything
- Template convergence: identical section structure across supposedly
  independent documents; every document ending in the same kind of section
- Double counting: the same source or program cited in multiple places as
  "independent" confirmation
- Claim escalation: "five of six" in a source document becoming "every" in a
  summary becoming "all research independently confirms" in a README
- Asymmetric critique: only the rejected options get failure modes discussed
- Undisclosed limitations: one document admits its sources could not be
  fetched; sibling documents produced the same way disclose nothing
- Missing precedents: the closest historical analog and its canonical
  critique are absent (if a project is a modern version of something that
  was already critiqued in the literature, that critique should be present)
- Hardcoded knowledge presented as discovery: any "the system found X" claim
  where X was in a lookup table the system was given

## 6. The red team (all task types)

The red team has one brief in every run:

Part 1: argue that the request is ill-posed, impossible, internally
contradictory, wrongly scoped, or already answered. Attack the question,
not the answer. Look especially for carve-outs in the request that delete the
only feedback channel that could validate the result ("I don't want to build
X, just the thing that could build X" is a classic).

Part 2: only after Part 1, state the maximum honest version: the strongest
claim that survives Part 1, and the minimal design that earns it.

In the final pass (Step 6 of the protocol) the brief changes: do not re-argue
Part 1. Hunt seams the merge created. Score the original objections.

## 7. Writing your own stances

When the task type is not above, or the built-in stances feel like the same
stance renamed, write new ones. A good stance:

- Names a tradition or role that has its own literature or lived practice
- Comes with two or three anchor ideas specific enough to steer, general
  enough not to dictate an answer
- Would be embarrassed by a different kind of mistake than the other stances
- Does not contain the coordinator's preferred answer in any form

Test: if you can predict what the stance agent will conclude, the stance is
too narrow or you have steered it. Widen it or drop it.

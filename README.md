# Agent Skills

Two skills that make Claude argue with itself before it answers you.

- **xcheck** - when Claude is about to stop and ask you "should I do A or B?",
  it instead sends two or three subagents off to decide from different angles,
  makes them argue, and proceeds if they agree. You only get interrupted when
  they genuinely cannot settle it. This one works on its own in the
  background; you should mostly forget it is there.
- **xpollinate** - for the hard questions, and expensive enough that you
  normally ask for it by name. Claude writes down its own answer first, then
  launches a control agent plus several agents with deliberately different
  worldviews plus a red team whose job is to argue the question itself is
  wrong. None of them see each other or Claude's answer. Then it collides the
  reports against each other, writes a synthesis, and lets the red team attack
  the synthesis too.

Both are plain Markdown. Nothing to compile, no dependencies, no network
access beyond what the model does, nothing running in the background.

## Install

Three ways. Pick one.

### 1. skills.sh (simplest, and lets you take just one)

```
npx skills add nickjrotundo/agent-skills --skill xcheck
npx skills add nickjrotundo/agent-skills --skill xpollinate
npx skills add nickjrotundo/agent-skills --skill '*'
```

That installs into the current project's `.claude/skills/`. Add `-g` to
install for every project instead, and `-a claude-code` to be explicit about
the agent if you use more than one:

```
npx skills add nickjrotundo/agent-skills --skill '*' -g -a claude-code
```

To see what is in the repo before installing anything:

```
npx skills add nickjrotundo/agent-skills --list
```

Works with Cursor, Codex, Copilot, Windsurf, Gemini and others too, not just
Claude Code.

### 2. As a Claude Code plugin

Adds the repo as a marketplace, then installs whichever you want:

```
/plugin marketplace add nickjrotundo/agent-skills
```

```
/plugin install xpollinate@xpollinate     <- both skills (recommended)
/plugin install xcheck@xpollinate         <- just xcheck, the light one
```

Restart Claude Code (or `/reload-plugins`) and they are live.
`/plugin update <name>` picks up later changes. The upside over route 1 is
that updates are one command and you can see everything with
`claude plugin details xpollinate`.

### 3. Manual

Every [release](https://github.com/nickjrotundo/agent-skills/releases) has a
ZIP per skill attached. Each one has the skill folder at its root, which is
the layout claude.ai's custom-skill upload expects:

```
xcheck.zip
  xcheck/
    SKILL.md
```

Download `xcheck.zip` or `xpollinate.zip` from the latest release and upload it
straight to claude.ai, or clone the repo and copy the folders in by hand:

```
git clone https://github.com/nickjrotundo/agent-skills.git
cp -r agent-skills/skills/xpollinate ~/.claude/skills/
```

Copy the **whole folder** each time. xpollinate reads two more files from its
own `references/` directory while it runs, so a lone `SKILL.md` is a broken
install. (xcheck is a single file and has no such problem.)

### Checking it worked

Ask Claude to list its skills, or:

```
claude plugin details xpollinate
```

Installed as a plugin they show up as `/xpollinate:xcheck` and
`/xpollinate:xpollinate`. Installed any other way they are just `/xcheck` and
`/xpollinate`.

## Using them

Both skills describe when they apply and Claude picks them
up on its own - but they are tuned very differently on purpose:

**xcheck is meant to fire automatically.** Its trigger is Claude noticing that
it is about to ask you a question it could answer itself. You are not supposed
to invoke it; you are supposed to notice you are being interrupted less.

**xpollinate is meant to be asked for.** It costs six to eight agents and
writes a directory of files, so its description deliberately holds it back
from routine work. It will fire on its own for genuinely big questions -
architecture decisions, serious reviews, "how would you approach X" - and when
you say things like "red team this", or "get multiple perspectives".
Otherwise just name it: "xpollinate this design".

## What each one actually does

### xcheck

The premise is that most "quick question" interruptions are judgment calls a
careful engineer would just make, and the reason not to trust Claude making
them alone is that one pass tends to pick whatever came to mind first. So:

1. Claude writes the decision down - the options, the context, and what
   "correct" would even mean here. If it cannot write that last part, the
   decision is yours and it asks you.
2. It launches at least two agents with different vantage points. One decides
   as the person who owns the codebase would; one decides as the reviewer who
   will maintain the change. Optionally a third argues both options are wrong.
3. Each agent sees the others' answers and either changes its mind or names
   the exact point of disagreement.
4. If they converge, Claude proceeds and tells you in one line what it
   decided. If they do not, it asks you - but the question is now much
   sharper, because it comes with the disagreement laid out.
5. Every decision gets appended to `.xcheck-decisions.md` in your project, so
   a later session can see what was already settled, and so you can audit the
   calls made on your behalf.

It deliberately does **not** apply to anything irreversible, anything
involving money, credentials or production, anything that changes the scope of
what you asked for, or anything where only you have the missing information.
Those still come to you.

### xpollinate

This one is built around a specific failure: if you launch a bunch of
subagents and seed them all with your own framing, they agree with you, and
the agreement gets reported back as independent confirmation. That is worse
than a single answer, because it looks like evidence.

Every step is a countermeasure for one way that happens:

- Claude commits its own answer to a file **before** any agent reports, so it
  cannot quietly grade its own influence afterwards.
- A control agent gets your prompt verbatim with no steering at all. That
  measures what the model says by default. If the control reaches the same
  conclusion as everyone else, that is a model prior, not convergence, and the
  synthesis has to say so.
- The stance agents are drawn from genuinely different intellectual roots - a
  market economist and a cultural sociologist, not two flavors of the same
  worldview. A stance whose conclusion you can predict in advance is too
  narrow and gets dropped.
- A red team argues the request itself is ill-posed before anyone answers it,
  and only then states the strongest honest version that survives.
- No agent sees Claude's pre-commit, or any other agent's report.
- Raw reports are saved verbatim before anything is summarized.
- Reports are then paired for maximum useful collision rather than agreement,
  and one agent from each pair has to defend or retract its own work.
- The finished synthesis goes back to the red team, whose new job is to find
  seams the merge itself created.

Everything lands in `xpollinate/<slug>/` inside your project: the pre-commit,
the design file, every raw report, the merge reports, and the synthesis. The
diff between the pre-commit and the synthesis is the honest measure of what
the exercise bought you.

The stance library lives in
[`skills/xpollinate/references/stances.md`](skills/xpollinate/references/stances.md) -
stances for design questions, understanding a new codebase, code review,
evaluating a plan, and auditing prior work for bias, plus instructions for
writing your own. The exact agent prompts are in
[`references/prompts.md`](skills/xpollinate/references/prompts.md).

## Which one do I want?

xcheck is for a fork in the road inside a task you already agreed on. It costs
two or three agents and a couple of minutes.

xpollinate is for when the question *is* the task, and being wrong is
expensive. It costs six to eight agents and produces a directory of documents.

Each skill points at the other when it turns out to be the wrong size for the
job. Installing both is the recommended setup for that reason, and costs about
500 tokens of context whether or not you ever use them.

## Both skills work without subagents

If subagents are unavailable, each skill has a documented degraded mode where
Claude plays the roles itself, in sequence, writing each one down before
starting the next. It is honestly weaker - Claude knows its own first answer
while writing the second - and both skills say so rather than pretending
otherwise.

## Working on these

The skills are the source of truth; everything else is packaging.

```
claude plugin validate .            # check the marketplace manifest
claude plugin validate skills       # check both SKILL.md files
python3 scripts/package.py          # build dist/*.zip for a release
```

Cutting a release, which is the only thing that produces downloadable ZIPs:

```
python3 scripts/package.py
gh release create v0.1.0 dist/*.zip --title v0.1.0 --notes "..."
```

Zip building is purely local - python3 standard library, no dependencies, and
nothing runs on GitHub. `dist/` is gitignored; the archives exist only as
release assets. They are byte-reproducible, so rebuilding an unchanged skill
gives an identical file, and `python3 scripts/package.py --check` compares a
fresh build against whatever is sitting in `dist/`.

`skills.sh.json` only controls how the repo page is grouped on skills.sh. It
has no effect on installs or on the skills themselves.

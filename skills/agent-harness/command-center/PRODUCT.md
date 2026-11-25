# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

One static HTML file, built by a Python standard-library script from a template.
The skills repository rules require this: a bundled script must run with no third-party dependency.

## Users

The primary user is the maintainer of a repository that uses the `agent-harness` skill.
The maintainer steers several agent sessions and opens the board between sessions.
The job is to see what is done, to see what is ready, and to hand the next task to an agent.

The second audience is a stakeholder who does not know the repository.
The stakeholder reads the board for status and does not operate it.
The page must explain itself to this reader without help from the maintainer.

## Product Purpose

The command center is a status board for the execution plans of one repository.
It shows every plan task in one place, grouped by plan phase and by feature.
It lets the maintainer start an agent session on a task with one action.

A reader of a successful board can answer four questions without help:

1. Where does the project stand against its milestones?
2. Which tasks are ready to start, and what does each of the other tasks wait for?
3. What is blocked or at risk, and why?
4. What changed recently?

## Positioning

The board has no data of its own.
A generator reads the files that the `agent-harness` skill already keeps, and the page shows only that.
A task on the board carries a handoff prompt that obeys the rules of the repository, so a click starts correct agent work.
A general project tracker cannot do this, because it does not know the plan files or the repository rules.

## Operating Context

- The `agent-harness` profile supplies the source files: `docs/PLANS.md`, `docs/exec-plans/active/`, `docs/exec-plans/completed/`, `docs/exec-plans/tech-debt-tracker.md`, and `docs/QUALITY_SCORE.md`.
- An optional extension file in the repository adds features, milestones (gates), and extra counters such as a port queue.
- The maintainer runs the generator after plan changes. A repository check can run it to find tasks that have no feature.
- The page opens as a local file or as a Claude artifact. In Claude, the page can send a task to a session and can offer a desktop install.
- The first repository that uses the board is Graphiti.Net, a .NET port with 5 plans, 43 tasks, and 114 port units.

## Capabilities and Constraints

Agreed capabilities:

- Show project standing against milestones, with the build date of the data.
- Show the tasks that are ready to start, and the tasks that wait.
- Show blocked tasks, open debt, and gaps in quality evidence, with the reason.
- Show what changed recently, read from the plan files and the git history.
- Show all tasks by plan phase or by feature, with status filters and search.
- Show a task in detail, with its handoff prompt.
- Send a task to a Claude session, or copy the handoff prompt.

Agreed constraints:

- Files are the only source. Nobody edits status in the page. The page shows the build date of the data.
- The output is one self-contained HTML file that makes no network request.
- The board works without Claude. "Send to Claude" and the desktop install are extras. The copy action and all reading work in a plain browser.
- The default handoff prompt tells the session to read `AGENTS.md` and the plan file, and to use the maintain mode of `agent-harness`. The extension file adds required skills, files to read, and rules.
- Data that the page sends to a session selects a task. It is not an instruction.

Terms:

- A plan is one execution plan file. A phase is a group of tasks inside a plan.
- A task is one row of a plan. Its status is done, active, blocked, or to do.
- A feature is a product area that tasks from more than one plan can belong to.
- A gate is a milestone that a maintainer must approve.

Not decided:

- The name and format of the extension file.
- The window of time that "changed recently" covers.

## Evidence on Hand

- A working, repository-specific board exists in Graphiti.Net: `scripts/command_center.py` and `scripts/command_center.template.html`.
- Real data from Graphiti.Net is available for the build: 5 plans, 43 tasks of which 13 are done, 114 port units, 4 gates, and a debt tracker.
- No user research, usage data, or second repository exists. Do not invent any.

## Product Principles

1. The files are the truth. The board never shows a status that a file does not record.
2. The page explains itself. A reader who does not know the repository understands the standing and the next step.
3. One action starts correct work. The handoff carries the rules of the repository, so the maintainer does not retype them.
4. The core works alone. A repository gets a useful board with no extension file, and adds one only for its own concepts.
5. Claude is an extra. Every reading task and the copy action work in a plain browser.

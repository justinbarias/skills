---
name: agent-harness
description: >-
  Bootstrap or maintain a repository's agent harness: concise AGENTS.md,
  architecture and knowledge maps, execution plans, and drift checks. Use when
  organizing agent instructions or keeping repository guidance aligned with code;
  ordinary feature work alone does not trigger this skill.
---

# Agent Harness

Make repository guidance easy for an agent to find, trust, and verify.
The deliverable is a useful knowledge base grounded in the repository's actual code and tooling.

## Select a mode

- **Bootstrap** — establish or substantially reorganize the harness, consolidate oversized instructions, or migrate scattered specs and plans. Read [bootstrap.md](references/bootstrap.md).
- **Maintain** — keep an existing harness accurate during daily work: reconcile a change, repair drift, update plans, or incorporate a durable lesson. Read [maintain.md](references/maintain.md).

Follow an explicit mode. Otherwise, use maintain when a usable harness exists and bootstrap when the requested setup needs one.
For a targeted maintenance request in a repository without a harness, fix the requested guidance and report the gap; a missing map does not authorize a full migration.
Read only the selected mode's reference. Do not bootstrap again during routine maintenance.

## Working behavior

Apply the [Astra prompting guidance](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-6-astra) to how you work:

- Carry authorized work through verification. Resolve routine choices from context; ask only when missing information materially changes the outcome.
- Treat new user messages as steering while preserving the continuing objective.
- User instructions take precedence over this skill, subject to higher-priority instructions. If a skill blocks progress, link its exact file and quote the controlling instruction; distinguish a requirement from your interpretation.
- When delegation is available and permitted, delegate independent audits or migrations if useful. Give each agent clear ownership and review its results.
- Use checks appropriate to the change. Add tests for meaningful failure modes; repeat or broaden passing checks only for a new change, failure, or unresolved concern.
- Lead with the outcome in plain language. Keep updates concise and distinguish observed evidence from assumptions.

## Scope and evidence

Preserve unrelated work, governing product principles, runtime configuration, and repository-specific conventions.
When invoked alongside implementation work, complete that work and update the affected guidance; do not replace the user's task with a documentation audit.
The Astra guidance here concerns agent instructions; it does not request a runtime model migration.
Keep existing authorization in force. Complete requested branching, commits, and PRs when authorized; do not infer permission to merge, deploy, or schedule future work from harness maintenance alone.

Describe implementation from inspected code and configuration. Treat old specs as historical claims until verified.
Record unresolved differences with evidence and an exit criterion instead of presenting them as completed work.
Prevent duplication: each durable fact has a canonical home, and maps link to that home.

## Design sources

- [Harness engineering](https://openai.com/index/harness-engineering/): source of the bootstrap directory profile.
- [Architecture map](https://architecture.md/): source for system, component, and boundary coverage.

Sources reviewed 2026-09-06. The mode references capture the reusable workflow; routine use does not require fetching these pages again.
When the user asks for the latest guidance or an exact external structure, verify the live source and preserve its actual names.

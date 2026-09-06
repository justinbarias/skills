# Bootstrap

Success means an agent can find the governing instruction, relevant code, current plan, and verification command without reading a large manual.

## Establish the baseline

Inspect the working tree, applicable instruction files, documentation, feature records, and tooling that creates or rewrites them.
Read actual entry points, dependency manifests, build targets, hooks, and CI before documenting commands or architecture.
Identify duplicated rules, conflicting instructions, obsolete commands, inaccessible knowledge, and claims unsupported by the implementation.

For a substantial migration, create an active execution plan with scope, acceptance criteria, source inventory, decisions, and verification results.
Use the user's chosen layout. Otherwise, use this profile while retaining useful existing guides and project-specific documents:

```text
AGENTS.md
ARCHITECTURE.md
docs/
├── design-docs/
│   ├── index.md
│   └── core-beliefs.md
├── exec-plans/
│   ├── active/
│   ├── completed/
│   └── tech-debt-tracker.md
├── generated/
│   └── db-schema.md
├── product-specs/
│   ├── index.md
│   └── new-user-onboarding.md
├── references/
│   ├── design-system-reference-llms.txt
│   ├── nixpacks-llms.txt
│   └── uv-llms.txt
├── DESIGN.md
├── FRONTEND.md
├── PLANS.md
├── PRODUCT_SENSE.md
├── QUALITY_SCORE.md
├── RELIABILITY.md
└── SECURITY.md
```

The profile preserves these names. Populate them with repository-specific evidence.
For an absent technology, use a short applicability note and point to the actual implementation; do not invent a database, frontend framework, Nixpacks setup, or UV dependency.
Preserve empty plan directories with the repository's normal tracked placeholder convention.

## Build the map and canonical guidance

Keep `AGENTS.md` within 100 lines for this profile unless the user chooses another limit.
Include the project purpose, links to authoritative documents, essential invariants, work loop, and relevant verification entry points.
Move tutorials and extensive policy into linked documents. Preserve substantive rules while resolving duplication and contradictions.

When Claude guidance is present or requested, consolidate shared guidance into `AGENTS.md` and make `CLAUDE.md` contain only `@AGENTS.md` plus a final newline.
Preserve any explicitly required tool-specific exception instead of silently discarding it.
Move a constitution out of retired scaffolding before deleting that scaffolding; retain its principles and update all pointers.

| Home | Useful content |
| --- | --- |
| `ARCHITECTURE.md` | Implemented system flow, major responsibilities, code entry points, data stores, external services, dependency boundaries, and exceptions. Separate actual constraints from proposed architecture. |
| `DESIGN.md`, design index, core beliefs | Navigation into decisions and research; durable engineering principles, owners, and verification status. |
| `FRONTEND.md` | Existing interaction surfaces, components, design sources, and validation workflow, including CLI or dashboard surfaces when applicable. |
| `PRODUCT_SENSE.md`, product index, onboarding | Product intent, feature requirements, acceptance criteria, and the real first-use path. |
| `PLANS.md`, execution directories, debt tracker | Plan lifecycle, progress, decisions, unresolved gaps, ownership, and concrete completion criteria. |
| `QUALITY_SCORE.md` | Evidence by domain: available checks, what was run, dates, and known gaps. Use unknown or unverified where evidence is absent. |
| `RELIABILITY.md`, `SECURITY.md` | Actual operational commands, diagnostics, lifecycle behavior, trust boundaries, credential handling, and known limitations. |
| Generated inventory and references | Reproducible contract/storage information and focused implementation references. Explain how to regenerate derived content. |

Link every managed document from the root map through a relevant index.
Use navigable local links for repository files and precise source links for external references.

## Migrate existing records when in scope

Inventory all source files before moving them, including nested plans, task lists, contracts, checklists, images, and attachments.
For a substantial move, keep a migration ledger with one destination per source and baseline hashes; hashes record provenance, not a permanent ban on edits.

- Put requirements, acceptance criteria, contracts, and user scenarios in product specs.
- Put research, data models, technical decisions, and design assets in design documents.
- Put every execution plan and associated task list in execution-plan directories, preserving feature IDs and useful nesting.
- Preserve task IDs, checkbox states, status evidence, and binary bytes. Distinguish active, completed, and explicitly archived records. A shipped label does not prove unfinished tasks are complete.

Rebase links across the split directories. Update live references in source comments, test fixtures, ownership rules, navigation, CI, and generators.
Keep literal examples literal; inspect whether paths inside an example are illustrative or executable before changing them.
Use feature indexes to connect requirements, design, and execution records without copying their content.

Remove obsolete generators or custom commands only when their retirement is part of the requested replacement.
When the user requests complete retirement, remove the tooling and its dedicated tests, rewrite obsolete instructions naturally, and search current, hidden, and historical repository files for remaining references.
Preserve governing documents and unrelated editor settings. Do not turn a cleanup into deletion of still-used tools.

## Verify and finish

Use the repository's existing checks where they cover the outcome. Add a small local check only for an uncovered invariant worth maintaining.
Useful mechanical checks cover required paths, root instruction limits, broken local targets, unreachable documents, and stale generated content.
State the check's actual coverage; file-link validation does not prove semantic freshness or heading-anchor correctness.

Verify migration completeness and uniqueness, task states, and binary hashes against the baseline.
Run affected tests for changed executable paths and publishing hooks. Exercise a real failure mode when adding a checker, such as a broken link, orphan plan, or stale generated artifact.
Build the documentation site when publishing changes. Check that repository source links survive publishing and that historical labels or code examples do not become broken cross-references.

Integrate useful drift checks into the existing hook or CI mechanism without duplicating equivalent jobs.
Avoid running live services or changing dependencies solely to validate a documentation move.
Update the plan with commands and results. Move it to completed only when acceptance criteria pass, and update its index links.
Report the new entry points, preserved content, verification, and remaining gaps. Finish any authorized Git delivery.

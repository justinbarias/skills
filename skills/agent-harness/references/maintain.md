# Maintain

Keep the existing knowledge base accurate with the smallest change supported by new evidence.
Maintenance is a scoped update, not a fresh bootstrap or a standing background service.

## Find the affected knowledge

Inspect the working tree and the user's requested change, diff, incident, or documentation concern.
Start from `AGENTS.md`, then read only the relevant architecture section, domain guide, spec, plan, and verification configuration.
Use code and current commands to confirm a claim before changing documentation that describes implementation.

If no target is specified, check the entry-point map, links, active plans, and recently changed domains first.
Expand only when findings justify it. A single maintenance invocation does not imply an exhaustive repository audit.

| Observed change | Update |
| --- | --- |
| Module boundary, provider route, dependency direction | Architecture map, the affected design decision, and an existing structural check when the enforced rule changes. |
| User-visible behavior or acceptance criteria | Canonical product spec and relevant user guide; reconcile the plan with actual acceptance evidence. |
| Setup, build, test, or operational command | The owning runbook and verification instructions after checking the real command definition. |
| A feature lands, or a verify command changes | The repository `verify` skill: its steps, its selection table, and its "Not built yet" table, in the same change. |
| Contract or schema source | Run its existing generator and refresh derived inventories; do not hand-edit generated output. |
| A plan reaches completion | Record verification, move it to completed, and update links, status indexes, and migration-ledger destinations if present. |
| Deferred or uncertain work | Keep it unresolved and record evidence, owner, and exit criterion in the relevant plan or debt tracker. |
| Repeated agent failure or review finding | Correct the nearest canonical instruction or add a narrow check that catches the demonstrated failure. |

## Make the bounded correction

Fix facts at their canonical home and adjust incoming links. Remove duplicate wording only when it describes the same rule.
Keep root instructions short; put new domain detail in linked guidance rather than appending it to `AGENTS.md`.
Retain the established layout and any explicit exceptions. Do not rename reference files merely because an external article changed.

Keep historical status separate from current verification. Do not check off tasks because code appears present, mark work complete because a file moved, or claim tests passed because a prior plan says so.
Preserve recorded evidence; explain a correction when a previous status was wrong.
Distinguish an archived proposal from delivered functionality.

For drift, trace the cause: a moved file, stale generator input, missing index link, conflicting instruction, or changed runtime contract.
Repair the source of repeated drift where it is within scope. A generator that rewrites the root map should be fixed or retired when authorized, not repeatedly repaired after each run.
Keep retirement and deletion limited to the user's scope and verified obsolete material.

## Keep the verify skill current

The change that builds a feature also updates the verify skill. Add the step that covers the feature, and run it.
A row leaves the "Not built yet" table only when its step exists and passes in this session.
When a command changes, change it in the verify skill in the same change.
If the repository forbids a change that edits its own check, a rewrite of the verify skill goes in its own pull request.

Drift check: each command of the verify skill exists and runs.
Run each command. If a command is too costly to run, check that each script, target, and test project that it names exists.
Report a missing or failing command as drift. Repair the command or the skill, and never weaken the check to make it pass.

## Verify and close the loop

Run the repository's harness check if present; otherwise use a bounded link check for the edited documents.
For a change to code or commands, follow the repository's verify skill and report in its form.
For a moved document, check both its incoming and outgoing links.
Check all ledger destinations when moving recorded migration artifacts.
For documentation publishing changes, run the site build and address introduced warnings.
For executable behavior, use focused tests and the repository's required quality checks; text-only edits normally need no new tests.

When updating quality evidence, distinguish code inspection, focused tests, full-suite results, and checks that were unavailable.
Stop expanding verification once the scoped checks and required gates pass, unless a new concern remains.
Record unresolved failures with exact evidence instead of hiding them or weakening a gate.

Update the active plan or debt entry when one exists. A small maintenance change does not require creating a new plan just to record a typo fix.
Report what changed, why, what was verified, and any remaining limitation.
Carry out already-authorized commits and PR updates; otherwise leave the result reviewable.
Schedule recurring maintenance only when requested, using available automation capabilities and the user's scope.

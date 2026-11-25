---
version: 1
slug: "template-html"
primary_target: "template.html"
related_targets: []
---

# Command center board

Scope: the whole generated page (`template.html`), built by `command_center.py`. Visitor mode: Operate, with a read-only stakeholder audience.

Audience and job: the maintainer finds the next task and hands it to an agent. A stakeholder learns the standing, the next work, the risk, and the recent changes without help.

Constraints: one self-contained file, no network request, files are the only source, works without Claude.

## Direction contract

THESIS: The board is a line diagram of the project. Plans are lines, tasks are stops, gates are interchanges, and one marker says where the project is. It refuses the row of summary cards that opens every tracker.

OWN-WORLD: White ground, deep navy ink, a navy rail, and flat line colors from a fixed transit set. Signal red is for the position marker and the primary action only. Albert Sans in four weights with tabular numerals. Stops are rings on thick lines. Timetable rows sit on hairlines. Content has no cards and no shadows. A dark theme exists because the page runs as a Claude artifact inside an app that has light and dark modes: it follows the system, and it is the same diagram on a night ground of navy black with brighter line colors.

STORY: The reader sees the position, then the next departures, then what waits and what changed. The maintainer sends one task to an agent.

FIRST VIEWPORT: A navy rail, 264px wide, lists the plan lines with numbered pills. The main area holds the status sentence at display size with the build stamp at the right, then the line diagram at full width, then the timetable of ready tasks. Each ready row carries the primary action "Send to Claude".

SIGNATURE: The diagram is drawn from the data. A stop and its timetable row are one object: focus one and the other answers. A line in the rail filters the page to that plan. The marker travels along the line to the position once on load, and stands still with reduced motion. In a view that cannot send to Claude, "Send to Claude" stays on each ready row by the user's instruction, copies the handoff prompt, and says so.

FORM: Line diagram, candidate 1 of 7 on the ordered list, chosen by the user over the assigned candidate 7. seed:4c60474b44d8ebbb

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

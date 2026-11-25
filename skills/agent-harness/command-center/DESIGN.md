---
name: Command center
description: A status board drawn as a transit line diagram, with plans as lines, tasks as stops, and gates as interchange stations.
colors:
  ground: "#ffffff"
  sunk: "#f1f4f8"
  ink: "#0b1f3a"
  muted: "#42546f"
  faint: "#5b6c86"
  hairline: "#c9d2df"
  rail: "#0b1f3a"
  rail-ink: "#ffffff"
  rail-muted: "#b9c5d8"
  rail-hairline: "#2c405c"
  rail-hot: "#17304f"
  signal: "#d6001c"
  signal-strong: "#a80016"
  signal-ink: "#ffffff"
  here-tint: "#fff1c9"
  focus: "#0057b8"
  line-green: "#00843d"
  line-blue: "#0057b8"
  line-amber: "#c08800"
  line-violet: "#6b3fa0"
  line-teal: "#007a82"
  line-orange: "#c2410c"
  line-magenta: "#c2187a"
  line-brown: "#8a5a2b"
  ground-dark: "#0a1626"
  sunk-dark: "#12213a"
  ink-dark: "#eef3fa"
  signal-dark: "#ff6b76"
  focus-dark: "#8fc1ff"
typography:
  headline:
    fontFamily: "Albert Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "clamp(24px, 2.7vw, 34px)"
    fontWeight: 700
    lineHeight: 1.12
    letterSpacing: "-0.015em"
  title:
    fontFamily: "Albert Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "17px"
    fontWeight: 700
    lineHeight: 1.45
    letterSpacing: "-0.005em"
  body:
    fontFamily: "Albert Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.45
    letterSpacing: "normal"
  label:
    fontFamily: "Albert Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "13px"
    fontWeight: 600
    lineHeight: 1.45
    letterSpacing: "normal"
rounded:
  sm: "3px"
  md: "4px"
  track: "6px"
  pill: "999px"
spacing:
  xs: "6px"
  sm: "10px"
  md: "16px"
  lg: "24px"
  xl: "44px"
components:
  button-primary:
    backgroundColor: "{colors.signal}"
    textColor: "{colors.signal-ink}"
    rounded: "{rounded.md}"
    padding: "8px 14px"
  button-primary-hover:
    backgroundColor: "{colors.signal-strong}"
  button-secondary:
    backgroundColor: "{colors.ground}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "8px 14px"
  button-secondary-hover:
    backgroundColor: "{colors.sunk}"
  line-pill:
    backgroundColor: "{colors.line-blue}"
    textColor: "{colors.ground}"
    rounded: "{rounded.pill}"
    padding: "3px 9px"
  position-marker:
    backgroundColor: "{colors.signal}"
    textColor: "{colors.signal-ink}"
    rounded: "{rounded.sm}"
    padding: "2px 9px"
  rail-item-selected:
    backgroundColor: "{colors.rail-ink}"
    textColor: "{colors.rail}"
    padding: "10px 8px"
  caution-note:
    backgroundColor: "{colors.here-tint}"
    textColor: "{colors.ink}"
    padding: "10px 12px"
---

# Design System: Command center

## Overview

**Creative North Star: "Line Diagram"**

The page reads like a transit map. Each plan is a colored line. Each task is a stop on that line. Each gate is an interchange station. A red marker shows where the project stands now.

Below the diagram, the page reads like a printed timetable. Rows sit between rules, with no cards and no boxes. A navy rail at the left holds the line list, like a station sign.

The system is plain and exact. Ink is navy, not black. Color belongs to the lines and to one signal red. Type is one family at a few sizes.

**Key Characteristics:**
- One typeface, Albert Sans, embedded in the file, with tabular numerals everywhere.
- Eight line colors give each plan an identity. They carry no meaning beyond identity.
- Signal red marks the position marker and the primary action. Nothing else uses it.
- Status is a ring glyph whose shape changes, so color never carries status alone.
- Structure comes from ruled lines and whitespace. Surfaces are flat.
- The dark theme follows the system. A link with `?theme=light` or `?theme=dark` fixes the theme.

## Colors

The palette is navy ink on white, with eight saturated line colors and one red. Every value below also has a dark counterpart.

### Primary
- **Signal Red** (`signal`): The position marker and the "Send to Claude" button. The hover state is Deep Signal Red (`signal-strong`). The dark theme uses a lighter coral (`signal-dark`) with near-black text.

### Secondary
- **Line Colors** (`line-green` through `line-brown`): One per plan, assigned by plan order and repeated after eight. They fill the track, the pill, the ring stroke, and the group rule. The amber is darkened to `line-amber` so that a ring on the white ground reaches 3:1 contrast. Pill text is white, except on amber, where it is navy.
- **Focus Blue** (`focus`): The focus outline only. The rail uses a pale yellow outline instead, because blue fails on navy.

### Neutral
- **Ground** (`ground`): The page background and the fill inside every ring.
- **Sunk** (`sunk`): Hover rows, code, selected chips, and the handoff prompt block.
- **Navy Ink** (`ink`): Text, heavy rules, station knobs, and the outline of controls.
- **Muted** (`muted`) and **Faint** (`faint`): Secondary text and source notes. Both pass 4.5:1 on the ground.
- **Hairline** (`hairline`): The thin rule between rows.
- **Rail** (`rail`) with `rail-ink`, `rail-muted`, `rail-hairline`, and `rail-hot`: The navy sidebar and its text, rules, and hover.
- **Here Tint** (`here-tint`): The pale yellow wash behind the row or map cell that the reader points at or has open.

### Named Rules
**The One Signal Rule.** Signal red appears on the position marker and the primary action only. A new surface that needs emphasis uses ink, weight, or a rule.

**The Ring Rule.** Status shows in the shape of the ring, never in color alone. Filled is done, a dot is in progress, a cross is blocked, a broken ring waits.

**The Line Color Rule.** A line color names a plan. It never means good, bad, or urgent.

## Typography

**Display Font:** Albert Sans (with system-ui and sans-serif fallbacks)
**Body Font:** Albert Sans
**Label/Mono Font:** Albert Sans for labels. The system monospace stack for code and the handoff prompt only.

**Character:** Albert Sans is a clear, open grotesque with a signage feel. It stays at weights 400 to 700. Tabular numerals keep counts and dates aligned.

### Hierarchy
- **Headline** (700, 24px to 34px fluid, 1.12): The one sentence that states where the project stands. Tight tracking and balanced wrapping. Limited to 26em.
- **Title** (700, 17px, 1.45): Section headings. The task panel heading is 21px and the rail brand is 23px.
- **Body** (400, 15px, 1.45): Task titles, notes, and descriptions. Summary text stays within 70ch.
- **Label** (600, 13px to 14.5px): Subheads, button text, and definition terms. Small notes use 12.5px to 13.5px at weight 400.
- **Key** (700, 17px): Task keys in rows. They never wrap.

### Named Rules
**The Sentence Case Rule.** All text is sentence case at normal letter spacing. Hierarchy comes from size and weight, never from capitals or tracking.

**The One Family Rule.** Albert Sans is embedded as base64 and serves every text role. The page makes no network request for type.

## Layout

The shell is two columns, a 264px rail and a fluid main area. Opening a task adds a 408px panel as a third column at 1280px and wider. Below that width, the panel slides over the page, up to 440px wide.

Main content stacks in sections with 44px between them. Padding scales from 20px to 44px at the left. The diagram sits first under the headline. Ready work follows, then waiting and recent changes as two columns, then counts, the feature map, and all work.

The diagram scrolls sideways inside its own container. Each plan segment has a 150px minimum. Segment length follows task count, between 3 and 12 units.

Layout responds to the main container, not the viewport. At 860px the two columns merge and the owner column hides. At 600px the feature map becomes two columns: the feature, and its tasks of all plans in plan order. At 520px the action button drops below the row. At 900px the rail becomes a top strip and the line list becomes a wrapping row of pills.

Spacing steps in 4px to 10px units inside rows and 16px to 44px between groups. Rows are at least 54px tall.

## Elevation & Depth

The system is flat. Depth comes from ruled lines. A 2px ink rule opens each list or table, and a 1px hairline separates rows. A group rule uses the line color at 3px.

The only shadow lies under the task panel. The shadow appears only on a panel that slides over the page. It is a soft ambient shadow, not an outline.

### Shadow Vocabulary
- **Panel Edge** (`box-shadow: -18px 0 40px -18px rgba(5, 13, 24, 0.45)`): The slide-over panel below 1280px.

### Named Rules
**The Rule Over Box Rule.** Group content with a heavy top rule and hairlines. Do not wrap it in a bordered or shadowed card.

## Shapes

Forms come from transit signage. Tracks are flat bars 12px tall. Only the first segment gets a rounded 6px start. Stops and knobs are circles. A pill (999px) names a plan.

Controls use a 4px radius and a 1.5px ink outline. Code and tokens use 3px to 4px. The end station is a straight vertical bar.

A plan that waits draws as an open casing. It has a pale tint of its line color and a 2.5px outline in the full line color. A stub of dashes at the left of the diagram stands for earlier completed plans.

Station knobs are white circles with a 4.5px ink ring. A passed gate fills the knob with ink. The next gate grows to 30px.

## Components

### Buttons
- **Shape:** Gently squared corners (4px) with a 1.5px border.
- **Primary:** Signal red fill, white text, 8px by 14px padding, with a send icon. Reserved for "Send to Claude". It stays primary on every ready row. Where sending is not possible, it copies the handoff prompt and says so.
- **Secondary:** White fill, ink text, ink border. Hover shifts the fill to Sunk.
- **Disabled:** 45% opacity with a not-allowed cursor.
- **Focus:** A 2px Focus Blue outline offset by 2px.

### Ring Glyph
- **Style:** An 18px ring with a 3px stroke in the line color and a ground fill. A filled ink center means done. A small ink dot means in progress. An ink cross means blocked. A dashed stroke means waits.
- **Use:** The same mark appears in rows, stops, map cells, and the legend. It scales up 1.3 times on hover and focus.

### Plan Pill
- **Style:** A fully rounded chip filled with the line color, with 12.5px bold text and a 46px minimum width. Text color is set per line for contrast.

### Rail
- **Style:** Navy, sticky, full height. Each plan is a row with a pill, a title, and a progress note, split by rail hairlines.
- **State:** Hover shows Rail Hot. The pressed row inverts to a white fill with navy text.
- **Mobile:** The rail becomes a top strip. Each plan is a pill with its title beside it, with no progress note and no border.

### Timetable Row
- **Style:** A grid of glyph, key, title, and owner, with the action at the right. A hairline sits below. Hover shows Sunk. A hot or open row shows Here Tint.
- **Done:** Key and title turn muted.
- **In progress:** Tasks in progress sit in their own list above the ready tasks, and their rows have no send button.

### Position Marker
- **Style:** A red label with a downward pointer, set above the diagram at the last finished stop of the first plan that has open work. It slides to its place in 1.1 seconds. With reduced motion on, it does not move.

### Inputs and Filters
- **Style:** 36px tall, 1.5px ink border, 4px radius, white fill. The segmented control inverts the pressed segment to ink. Filter chips use a hairline border. A pressed chip gets an ink border and a Sunk fill.

### Task Panel
- **Style:** White, with a 2px ink rule at its left. It holds the heading, the plan pill, state, facts, and the handoff block. The prompt shows in a Sunk monospace block that opens on demand.

## Do's and Don'ts

### Do:
- **Do** keep red for the position marker and the primary action only.
- **Do** pair every status color with a glyph shape, and write the status in text.
- **Do** give each plan one line color and use it on the pill, track, ring, and group rule.
- **Do** separate lists with a 2px ink top rule and 1px hairlines.
- **Do** keep the page offline. Embed fonts and icons, and make no network request.
- **Do** write all labels in sentence case at normal tracking.
- **Do** keep text on the ground at 4.5:1 and ring strokes at 3:1 or better in both themes.

### Do not:
- **Do not** use a line color to mean status or priority.
- **Do not** put a card, a border box, or a heavy shadow around list content.
- **Do not** add a second typeface or a decorative display face.
- **Do not** use gradients, glass, or glow effects.
- **Do not** rely on hover for anything that a keyboard reader needs.
- **Do not** lighten the amber line color back to `#f2a900`. It fails 3:1 on white.

## Not Canonized

The page has no kickers, glyph icons, or hard offset shadows, so there are no craft-floor defects to carry forward.

#!/usr/bin/env python3
"""Builds the command center page for a repository that uses the agent-harness profile.

The page holds no status of its own. Each value comes from a file in the repository:

    docs/exec-plans/active/, docs/exec-plans/completed/   plans and their tasks
    docs/exec-plans/tech-debt-tracker.md                  open debt
    docs/QUALITY_SCORE.md                                 gaps in quality evidence
    docs/command-center.toml                              optional: features, gates, counters, handoff rules
    git log of docs/exec-plans                            recent changes

    python3 command_center.py                  # writes docs/generated/command-center.html
    python3 command_center.py --artifact       # writes the content-only form for a Claude artifact
    python3 command_center.py --check          # prints problems, exits 1 if one exists
    python3 command_center.py --root ../repo --config board.toml --out board.html

README.md beside this script states the parsing rules, the status rules, and the extension file.
"""
from __future__ import annotations

import argparse
import base64
import fnmatch
import html
import json
import re
import subprocess
import sys
import tomllib
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "template.html"
FONT = HERE / "fonts" / "AlbertSans-latin.woff2"
DATA_MARK, FONT_MARK, BODY_MARK = "/*__DATA__*/null", "/*__FONT__*/", "<!--__BODY__-->"
STATUSES = ("done", "active", "blocked", "todo")

ISO = r"\d{4}-\d{2}-\d{2}"
SENTENCE_START = r"(?:^|[.!?]\s+)"  # a status word counts only where a sentence starts
DONE_MARK = re.compile(SENTENCE_START + r"Done,? (?:on )?(" + ISO + r")\b")
BLOCKED_MARK = re.compile(SENTENCE_START + r"Blocked\b")
ACTIVE_MARK = re.compile(SENTENCE_START + r"In progress\b")
DONE_TAIL = re.compile(r"\s*\bDone,? (?:on )?" + ISO + r"\b[^.]*\.?\s*$")
DONE_HEAD = re.compile(r"^\s*Done,? (?:on )?" + ISO + r"[.:]\s+(?=\S)")
GENERIC_HEADINGS = re.compile(r"^(tasks?|task list|steps|plan|work|checklist)$", re.I)
RESULT_HEADINGS = re.compile(r"^(results?|verification|evidence|log)\b", re.I)
CHECKBOX = re.compile(r"^(\s*)(?:[-*+]|\d+[.)])\s+\[([ xX~!-])\]\s+(.*)$")
LEAD_ID = re.compile(r"^\**((?:[A-Za-z]{1,3}-?)?\d+(?:\.\d+)*)\**([.:)])?\s+(?=\S)")
FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})(.*)$")
DELIMITER = re.compile(r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$")
GAP_WORDS = re.compile(SENTENCE_START + r"(not verified|unverified|unknown|not run)\b", re.I)


def cells(line: str) -> list[str]:
    """Splits one Markdown table row. A pipe inside a code span stays in its cell."""
    parts, current, in_code = [], "", False
    for char in line.strip().strip("|"):
        if char == "`":
            in_code = not in_code
        if char == "|" and not in_code and not current.endswith("\\"):
            parts.append(current.strip())
            current = ""
        else:
            current += char
    parts.append(current.strip())
    return parts


def body_of(text: str) -> str:
    """Returns the text without YAML front matter."""
    lines = text.split("\n")
    if lines and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() == "---":
                return "\n".join(lines[index + 1 :]).lstrip("\n")
    return text


def blocks(text: str):
    """Yields ("table", heading, header, rows) and ("box", heading, mark, body) in file order.

    The heading is the nearest heading above the block. Fenced code is skipped.
    A checkbox item that is nested under another item is a step of that item, not a task.
    """
    lines, index, heading, fence, base = text.split("\n"), 0, "", "", None
    while index < len(lines):
        line = lines[index]
        mark = FENCE.match(line)
        if fence:
            if mark and mark.group(1)[0] == fence[0] and len(mark.group(1)) >= len(fence) and not mark.group(2).strip():
                fence = ""
        elif mark:
            fence = mark.group(1)
        elif "|" in line and index + 1 < len(lines) and "|" in lines[index + 1] and DELIMITER.match(lines[index + 1]):
            header, rows, index = cells(line), [], index + 2
            while index < len(lines) and "|" in lines[index] and lines[index].strip():
                rows.append(cells(lines[index]))
                index += 1
            yield "table", heading, header, rows
            continue
        elif match := re.match(r"^#{1,4}\s+(.*?)\s*#*$", line):
            heading, base = ("" if GENERIC_HEADINGS.match(match.group(1)) else match.group(1)), None
        elif match := CHECKBOX.match(line):
            indent = len(match.group(1).expandtabs(4))
            if base is None or indent < base:
                base = indent
            if indent == base:
                yield "box", heading, match.group(2), match.group(3).strip()
        index += 1


def plain(text: str) -> str:
    return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text).replace("`", "").replace("**", "")


def short(text: str, limit: int = 72) -> str:
    """The first sentence of a task, without Markdown marks, cut between words to a row length."""
    whole = DONE_TAIL.sub("", DONE_HEAD.sub("", plain(text))).strip() or plain(text).strip()  # the status mark is not part of the title
    first = re.split(r"(?<=\.)\s", whole, maxsplit=1)[0]
    if len(first) < 24:  # "Pilot." alone says too little
        first = whole
    first = first.rstrip(".:")
    if len(first) <= limit:
        return first
    cut = first[: limit - 1]
    if " " in cut[limit // 2 :]:
        cut = cut[: cut.rindex(" ")]
    return cut.rstrip(" ,;:(") + "…"


def column(header: list[str], pattern: str) -> int | None:
    for index, name in enumerate(header):
        if re.search(pattern, plain(name).strip(), re.I):
            return index
    return None


def status_of(text: str, cell: str, box: str) -> tuple[str, str]:
    """Returns (status, done date) as the file records them. The status is empty if the file records none."""
    stamp, cell_date = DONE_MARK.search(text), re.search(ISO, cell)
    if box in ("x", "X") or stamp or re.match(r"^\W*(done|completed?|finished|shipped)\b", cell, re.I):
        return "done", stamp.group(1) if stamp else cell_date.group(0) if cell_date else ""
    if box == "!" or BLOCKED_MARK.search(text) or re.search(r"\bblocked\b", cell, re.I):
        return "blocked", ""
    if box == "~" or ACTIVE_MARK.search(text) or re.search(r"\b(in progress|wip|active|started|doing|ongoing)\b", cell, re.I):
        return "active", ""
    if box == " " or re.match(r"^\W*(to ?do|open|not started|pending|planned)\b", cell, re.I):
        return "todo", ""
    return "", ""


def git(root: Path, *args: str) -> str:
    try:
        done = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=False)
    except OSError:
        return ""
    return done.stdout.strip() if done.returncode == 0 else ""


def inside(path: Path, *folders: Path) -> bool:
    real = path.resolve()
    return any(real.is_relative_to(folder.resolve()) for folder in folders)


def plan_sources(root: Path, problems: list[str]) -> list[tuple[str, str, Path, list[Path]]]:
    """Returns (state, stem, main file, all files) for each plan. A folder is one plan."""
    found = []
    for state in ("completed", "active"):
        folder = root / "docs" / "exec-plans" / state
        if not folder.is_dir():
            continue
        for entry in sorted(folder.iterdir()):
            if entry.name.startswith(".") or entry.name.lower() in ("readme.md", "index.md"):
                continue
            if entry.is_dir():
                files = sorted(entry.rglob("*.md"), key=lambda p: (len(p.relative_to(entry).parts), p.name.lower() != "plan.md", str(p)))
            else:
                files = [entry] if entry.suffix == ".md" else []
            outside = [path for path in files if not inside(path, root)]
            for path in outside:
                problems.append(f"{path.relative_to(root)} points outside the repository, so the board does not read it")
            files = [path for path in files if path not in outside]
            if files:
                found.append((state, entry.name if entry.is_dir() else entry.stem, files[0], files))
    return found


def task_columns(header: list[str]) -> dict[str, int | None] | None:
    id_col = column(header, r"^(#|id|no\.?|task\s*(id|#|no\.?))$")
    task_col = column(header, r"^tasks?$")
    if task_col is None:
        task_col = column(header, r"^task\b(?!\s*(id|#|no\b))")
    if task_col is None and id_col is not None and re.match(r"^task", plain(header[id_col]).strip(), re.I):
        task_col = column(header, r"^(description|summary|title)$")
    if task_col is None:
        return None
    return {"task": task_col, "id": id_col, "owner": column(header, r"owner|assignee|who\b|model"),
            "acceptance": column(header, r"accept|done when|evidence|exit"), "status": column(header, r"^status$"),
            "feature": column(header, r"^feature$"), "result": column(header, r"^(results?|outcomes?)$")}


def read_plans(root: Path, problems: list[str]) -> tuple[list[dict], list[dict]]:
    sources = plan_sources(root, problems)
    leads = [match.group(1) if (match := re.match(r"^(\d+)", stem)) else "" for _, stem, _, _ in sources]
    plans, tasks = [], []
    for (state, stem, main, files), lead in zip(sources, leads):
        plan_id = lead if lead and leads.count(lead) == 1 else stem  # two files that start with 2026 keep their whole names
        text = "\n\n".join(body_of(path.read_text(encoding="utf-8")) for path in files)
        first = text.split("\n", 1)[0]
        title = first.lstrip("# ").strip() if first.startswith("#") else stem
        title = re.sub(rf"^(?:plan\s+)?{re.escape(plan_id)}[\s:.\-–—]+", "", title, flags=re.I) or title
        intro = next((line.strip() for line in text.split("\n")[1:] if line.strip() and not line.startswith(("#", "|", "-", "```", "~~~"))), "")
        plan_done = state == "completed"
        plans.append({"id": plan_id, "title": title, "file": str(main.relative_to(root)), "state": state, "intro": plain(intro), "label": ""})
        mine: list[dict] = []
        for kind, heading, *rest in blocks(text):
            if kind == "table":
                header, rows = rest
                cols = task_columns(header)
                if cols is None or (mine and (cols["result"] is not None or RESULT_HEADINGS.match(heading))):
                    continue  # after the task table, a table of results repeats the same tasks
                for row in rows:
                    pick = lambda name: row[cols[name]] if cols[name] is not None and cols[name] < len(row) else ""  # noqa: E731
                    status, when = status_of(pick("task"), pick("status"), "")
                    mine.append({"num": plain(pick("id")), "phase": heading, "text": pick("task"), "owner": pick("owner"),
                                 "acceptance": pick("acceptance"), "recorded": status, "done_date": when, "feature": plain(pick("feature"))})
            elif rest[0] != "-":  # [-] is a cancelled item
                box, body = rest
                lead_id = LEAD_ID.match(body)
                has_id = lead_id and (lead_id.group(2) or "." in lead_id.group(1) or re.match(r"^[A-Za-z]{1,3}-?\d{3,}$", lead_id.group(1)))
                status, when = status_of(body, "", box)
                mine.append({"num": lead_id.group(1) if has_id else "", "phase": heading, "text": body[lead_id.end():] if has_id else body,
                             "owner": "", "acceptance": "", "recorded": status, "done_date": when, "feature": ""})
        if not mine:  # a plan with no task list is one task
            mine.append({"num": "1", "phase": "", "text": plain(intro) or title, "owner": "", "acceptance": "", "recorded": "", "done_date": "",
                         "feature": "", "whole_plan": True})
        used, counter = {task["num"] for task in mine}, 0
        for task in mine:
            while not task["num"]:  # a task with no id takes the next free number
                counter += 1
                if str(counter) not in used:
                    task["num"] = str(counter)
                    used.add(task["num"])
            recorded = task.pop("recorded")
            task.update(key=f"{plan_id}-{task['num']}", plan=plan_id, title=title if task.get("whole_plan") else short(task["text"]),
                        status=recorded or ("done" if plan_done else "todo"))
            if plan_done and task["status"] != "done":
                problems.append(f"plan {plan_id} is in completed/, but task {task['key']} is recorded as {task['status']}")
        tasks.extend(mine)
    ids = [plan["id"] for plan in plans]
    for plan_id in sorted({plan_id for plan_id in ids if ids.count(plan_id) > 1}):
        problems.append(f"two plans have the id {plan_id}")
    order = {"completed": "0", "active": "1"}
    plans.sort(key=lambda p: (not p["id"].isdigit(), p["id"].zfill(12) if p["id"].isdigit() else order[p["state"]] + p["id"]))
    rank = {plan["id"]: index for index, plan in enumerate(plans)}
    tasks.sort(key=lambda t: rank[t["plan"]])
    return plans, tasks


def read_debt(root: Path) -> list[dict]:
    path = root / "docs" / "exec-plans" / "tech-debt-tracker.md"
    if not path.is_file() or not inside(path, root):
        return []
    items = []
    for kind, _heading, *rest in blocks(body_of(path.read_text(encoding="utf-8"))):
        if kind == "table":
            header, rows = rest
            if not re.match(r"^(#|id|debt|gap|item|issue)", plain(header[0]).strip(), re.I):
                continue  # a legend or another table, not the list of debt
            status_col, exit_col = column(header, r"^status$"), column(header, r"exit")
            for row in rows:
                if len(row) < 2 or (status_col is not None and status_col < len(row) and re.match(r"^\W*(closed|done|resolved|fixed)\b", row[status_col], re.I)):
                    continue
                items.append({"id": plain(row[0]), "gap": plain(row[1]), "exit": plain(row[exit_col]) if exit_col is not None and exit_col < len(row) else ""})
        elif rest[0] in (" ", "~", "!"):
            items.append({"id": f"D{len(items) + 1}", "gap": plain(rest[1]), "exit": ""})
    return items


def read_quality(root: Path) -> list[dict]:
    path = root / "docs" / "QUALITY_SCORE.md"
    if not path.is_file() or not inside(path, root):
        return []
    gaps = []
    for kind, _heading, *rest in blocks(body_of(path.read_text(encoding="utf-8"))):
        if kind != "table":
            continue
        for row in rest[1]:
            hit = next((cell for cell in row[1:] if GAP_WORDS.search(plain(cell))), None)
            if hit:
                gaps.append({"area": plain(row[0]), "note": plain(hit)})
    return gaps


class Reader:
    """Reads values of the extension file. A value of the wrong type becomes a problem and a safe default."""

    def __init__(self, problems: list[str]):
        self.problems = problems

    def table(self, value, where: str) -> dict:
        if value is None or isinstance(value, dict):
            return value or {}
        self.problems.append(f"{where} must be a table")
        return {}

    def tables(self, value, where: str) -> list[dict]:
        if value is None:
            return []
        if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
            self.problems.append(f"{where} must be a list of tables")
            return []
        return value

    def text(self, value, where: str) -> str:
        if value is None or isinstance(value, str):
            return value or ""
        self.problems.append(f"{where} must be a string")
        return ""

    def texts(self, value, where: str) -> list[str]:
        if value is None:
            return []
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            self.problems.append(f"{where} must be a list of strings")
            return []
        return value

    def day(self, value, where: str) -> str:
        if value is None or value == "" or value is False:
            return ""
        if isinstance(value, date):
            return value.isoformat()[:10]
        if isinstance(value, str) and re.fullmatch(ISO, value):
            return value
        self.problems.append(f"{where} must be a date such as 2026-11-25")
        return ""

    def scalar(self, value, where: str):
        if isinstance(value, date):
            return value.isoformat()[:10]
        if value is None or (isinstance(value, (int, float, str)) and not isinstance(value, bool)):
            return value
        self.problems.append(f"{where} must be a number or a string")
        return None


def load_extension(root: Path, config: Path | None, problems: list[str]) -> dict:
    path = config or root / "docs" / "command-center.toml"
    if not path.is_file():
        if config:
            problems.append(f"the configuration file {config} does not exist")
        return {}
    try:
        ext = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as error:
        problems.append(f"{path.name}: {error}")
        return {}
    ext["_path"] = str(path.relative_to(root)) if path.is_relative_to(root) else path.name
    data_path = Reader(problems).text(ext.get("data"), "data")
    if data_path:
        file = Path(data_path) if Path(data_path).is_absolute() else root / data_path
        if not inside(file, root, path.parent):  # the page can be published, so it reads nothing from other places
            problems.append(f"the data file {data_path} is outside the repository, so the board does not read it")
        elif not file.is_file():
            problems.append(f"the data file {data_path} does not exist")
        else:
            try:
                loaded = json.loads(file.read_text(encoding="utf-8"))
            except json.JSONDecodeError as error:
                problems.append(f"{data_path}: {error}")
            else:
                if isinstance(loaded, dict):
                    ext["_data"], ext["_data_path"] = loaded, data_path if not Path(data_path).is_absolute() else file.name
                else:
                    problems.append(f"{data_path} must hold a JSON object")
    return ext


def apply_extension(ext: dict, plans: list[dict], tasks: list[dict], problems: list[str]) -> tuple[list[dict], list[str], list[dict]]:
    """Merges extra tasks, features, gates, and waits into the parsed data. Returns (gates, features, counters)."""
    read, extra = Reader(problems), ext.get("_data", {})
    plan_ids = [plan["id"] for plan in plans]
    for plan_id, entry in read.table(ext.get("plans"), "[plans]").items():
        entry = read.table(entry, f"[plans.\"{plan_id}\"]")
        if plan_id not in plan_ids:
            problems.append(f"[plans.\"{plan_id}\"] names a plan that does not exist")
            continue
        plan = plans[plan_ids.index(plan_id)]
        plan["label"] = read.text(entry.get("label"), f"[plans.\"{plan_id}\"] label")
        plan["after"] = []
        for other in read.texts(entry.get("after"), f"[plans.\"{plan_id}\"] after"):
            if other not in plan_ids or other == plan_id:
                problems.append(f"[plans.\"{plan_id}\"] after names \"{other}\", which is not another plan")
            else:
                plan["after"].append(other)

    for added in read.tables(extra.get("tasks"), "tasks in the data file"):
        plan_id, num = str(added.get("plan", "")), str(added.get("num", ""))
        if plan_id not in plan_ids or not num:
            problems.append(f"an extra task names plan \"{plan_id}\" and number \"{num}\": both must be valid")
            continue
        where = f"extra task {plan_id}-{num}"
        tasks[:] = [task for task in tasks if not (task["plan"] == plan_id and task.get("whole_plan"))]
        text = read.text(added.get("text"), f"{where} text") or read.text(added.get("title"), f"{where} title")
        status = read.text(added.get("status"), f"{where} status") or "todo"
        if status not in STATUSES:
            problems.append(f"{where} status must be one of: {', '.join(STATUSES)}")
            status = "todo"
        if plans[plan_ids.index(plan_id)]["state"] == "completed" and "status" not in added:
            status = "done"
        task = {"key": f"{plan_id}-{num}", "plan": plan_id, "num": num, "phase": read.text(added.get("phase"), f"{where} phase"),
                "title": read.text(added.get("title"), f"{where} title") or short(text), "text": text,
                "owner": read.text(added.get("owner"), f"{where} owner"), "acceptance": read.text(added.get("acceptance"), f"{where} acceptance"),
                "status": status, "done_date": read.day(added.get("done_date"), f"{where} done_date"),
                "feature": read.text(added.get("feature"), f"{where} feature"), "from_data": True}
        items = read.tables(added.get("items"), f"{where} items")
        if items:
            task["items"] = [{name: str(read.scalar(item.get(name), f"{where} item {name}") or "") for name in ("name", "status", "note")} for item in items]
        tasks.append(task)
    rank = {plan_id: index for index, plan_id in enumerate(plan_ids)}
    tasks.sort(key=lambda t: rank[t["plan"]])

    seen: set[str] = set()
    for task in tasks:
        if task["key"] in seen:
            problems.append(f"two tasks have the key {task['key']}")
        seen.add(task["key"])
    by_key = {task["key"]: task for task in tasks}

    features_table = read.table(ext.get("features"), "[features]")
    feature_map = {pattern: read.text(name, f"[features.map] \"{pattern}\"") for pattern, name in read.table(features_table.get("map"), "[features.map]").items()}
    task_table = read.table(ext.get("tasks"), "[tasks]")
    for task in tasks:
        override = read.table(task_table.get(task["key"]), f"[tasks.\"{task['key']}\"]")
        named = read.text(override.get("feature"), f"[tasks.\"{task['key']}\"] feature") or feature_map.get(task["key"])
        if not named:
            named = next((feature for pattern, feature in feature_map.items() if fnmatch.fnmatchcase(task["key"], pattern)), "")
        task["feature"] = named or task["feature"]
        task["waits_for"] = []
        for key in read.texts(override.get("waits_for"), f"[tasks.\"{task['key']}\"] waits_for"):
            if key not in by_key or key == task["key"]:
                problems.append(f"[tasks.\"{task['key']}\"] waits for {key}, which is not another task")
            else:
                task["waits_for"].append(key)
    for key in task_table:
        if key not in by_key:
            problems.append(f"[tasks.\"{key}\"] names a task that does not exist")
    features = list(read.texts(features_table.get("order"), "[features] order"))
    if features or any(task["feature"] for task in tasks):
        for task in tasks:
            if not task["feature"]:
                task["feature"] = "Unassigned"
                if "features" in ext:  # a Feature column alone does not make features required
                    problems.append(f"task {task['key']} has no feature")
            if task["feature"] not in features:
                features.append(task["feature"])

    dated = {str(gate.get("id")): gate for gate in read.tables(extra.get("gates"), "gates in the data file")}
    gates = []
    for gate in read.tables(ext.get("gates"), "[[gates]]"):
        gate_id = str(read.scalar(gate.get("id"), "a gate id") or len(gates) + 1)
        merged = {**gate, **dated.pop(gate_id, {})}
        after = read.text(merged.get("after_plan"), f"gate {gate_id} after_plan")
        if after not in plan_ids:
            problems.append(f"gate {gate_id} names plan \"{after}\", which does not exist")
            continue
        when = read.day(merged.get("passed"), f"gate {gate_id} passed")
        gates.append({"id": gate_id, "name": read.text(merged.get("name"), f"gate {gate_id} name"), "after_plan": after, "passed": bool(when), "date": when})
    for gate_id in dated:
        problems.append(f"the data file names gate {gate_id}, which the extension file does not have")
    gates.sort(key=lambda g: rank[g["after_plan"]])

    counters = []
    for counter in [*read.tables(ext.get("counters"), "[[counters]]"), *read.tables(extra.get("counters"), "counters in the data file")]:
        label, value = read.text(counter.get("label"), "a counter label"), read.scalar(counter.get("value"), "a counter value")
        if not label or value is None:
            problems.append("a counter needs a label and a value")
            continue
        counters.append({"label": label, "value": value, "total": read.scalar(counter.get("total"), f"counter \"{label}\" total"),
                         "note": read.text(counter.get("note"), f"counter \"{label}\" note"), "source": read.text(counter.get("source"), f"counter \"{label}\" source")})
    return gates, features, counters


def mark_waits(plans: list[dict], tasks: list[dict], gates: list[dict]) -> None:
    """Sets task["wait"]: the reason that a task cannot start yet, or an empty string."""
    rank = {plan["id"]: index for index, plan in enumerate(plans)}
    by_key = {task["key"]: task for task in tasks}
    open_tasks = {plan["id"]: [t for t in tasks if t["plan"] == plan["id"] and t["status"] != "done"] for plan in plans}
    for plan in plans:
        gate = next((g for g in gates if not g["passed"] and rank[g["after_plan"]] < rank[plan["id"]]), None)
        late = [other for other in plan.get("after", []) if open_tasks.get(other)]
        plan["wait"] = ""
        if not open_tasks[plan["id"]]:
            continue  # a plan with no open task waits for nothing
        if gate:
            plan["wait"] = f"Waits for gate {gate['id']}" + (f", {gate['name']}" if gate["name"] else "")
        elif late:
            plan["wait"] = "Waits for plan " + " and ".join(late)
    wait_of = {plan["id"]: plan["wait"] for plan in plans}
    for task in tasks:
        missing = [key for key in task.get("waits_for", []) if by_key[key]["status"] != "done"]
        task["wait"] = "" if task["status"] == "done" else (wait_of[task["plan"]] or ("Waits for " + " and ".join(missing) if missing else ""))


def read_changes(root: Path, plans: list[dict], tasks: list[dict], gates: list[dict], today: date) -> list[dict]:
    changes = []
    for task in tasks:
        if task["done_date"]:
            changes.append({"date": task["done_date"], "kind": "task", "key": task["key"], "text": f"Task {task['key']} is done: {task['title']}"})
    for gate in gates:
        if gate["date"]:
            changes.append({"date": gate["date"], "kind": "gate", "gate": gate["id"], "text": f"Gate {gate['id']}" + (f", {gate['name']}," if gate["name"] else "") + " passed."})
    for plan in plans:
        if plan["state"] == "completed":
            moved = git(root, "log", "--diff-filter=A", "--format=%ad", "--date=short", "-1", "--", plan["file"])
            plan["completed_on"] = moved
            if moved:
                changes.append({"date": moved, "kind": "plan", "plan": plan["id"], "text": f"Plan {plan['id']}, {plan['title']}, moved to completed."})
    since = (today - timedelta(days=120)).isoformat()
    log = git(root, "log", f"--since={since}", "--date=short", "--format=%ad%x09%h%x09%s", "-60", "--", "docs/exec-plans", "docs/PLANS.md")
    for line in filter(None, log.split("\n")):
        when, commit, subject = (line.split("\t") + ["", ""])[:3]
        changes.append({"date": when, "kind": "commit", "commit": commit, "text": subject})
    order = {"gate": 0, "plan": 1, "task": 2, "commit": 3}
    changes.sort(key=lambda c: (c["date"], -order[c["kind"]]), reverse=True)
    return changes


def project_name(root: Path, ext: dict, read: Reader) -> str:
    named = read.text(ext.get("name"), "name")
    if named:
        return named
    agents = root / "AGENTS.md"
    if agents.is_file() and inside(agents, root):
        first = agents.read_text(encoding="utf-8").split("\n", 1)[0]
        if first.startswith("# "):
            return first[2:].strip()
    return root.name


def build(root: Path, config: Path | None = None) -> tuple[dict, list[str]]:
    problems: list[str] = []
    today, read = date.today(), Reader(problems)
    ext = load_extension(root, config, problems)
    plans, tasks = read_plans(root, problems)
    if not plans:
        problems.append("no plan file exists in docs/exec-plans/active or docs/exec-plans/completed")
    gates, features, counters = apply_extension(ext, plans, tasks, problems)
    mark_waits(plans, tasks, gates)
    days = ext.get("recent_days", 7)
    if not isinstance(days, int) or isinstance(days, bool) or days < 1:
        problems.append("recent_days must be a whole number of days, 1 or more")
        days = 7
    handoff = read.table(ext.get("handoff"), "[handoff]")
    data = {
        "meta": {
            "name": project_name(root, ext, read),
            "generated": today.isoformat(),
            "commit": git(root, "rev-parse", "--short", "HEAD"),
            "branch": git(root, "rev-parse", "--abbrev-ref", "HEAD"),
            "recent_days": days,
            "extension": ext.get("_path", ""),
            "data": ext.get("_data_path", ""),
        },
        "plans": plans,
        "tasks": [{k: v for k, v in task.items() if k not in ("whole_plan", "waits_for")} for task in tasks],
        "gates": gates,
        "features": features,
        "counters": counters,
        "debt": read_debt(root),
        "quality": read_quality(root),
        "changes": read_changes(root, plans, tasks, gates, today),
        "handoff": {name: read.texts(handoff.get(name), f"[handoff] {name}") for name in ("read", "skills", "rules", "done")},
    }
    return data, problems


def script_safe(payload: str) -> str:
    """Escapes the characters that can end a script element or a JavaScript line."""
    escape = "\\" + "u"
    return payload.replace("<", escape + "003c").replace(chr(0x2028), escape + "2028").replace(chr(0x2029), escape + "2029")


def render(data: dict, artifact: bool) -> str:
    template = TEMPLATE.read_text(encoding="utf-8")
    for mark in (DATA_MARK, FONT_MARK, BODY_MARK):
        if template.count(mark) != 1:
            raise SystemExit(f"command_center: the template needs exactly one {mark} marker")
    head, body = template.split(BODY_MARK)
    # Each marker is replaced in the template text only, so marker text inside the data stays data.
    title = html.escape(data["meta"]["name"]) + " command center"  # an artifact takes its name from the title
    font = base64.b64encode(FONT.read_bytes()).decode("ascii")
    head = head.replace(FONT_MARK, font).replace("<title>Command center</title>", f"<title>{title}</title>")
    body = body.replace(DATA_MARK, script_safe(json.dumps(data, ensure_ascii=False)))
    if artifact:  # a Claude artifact supplies the document shell
        return head + body
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            + head + "</head>\n<body>\n" + body + "</body>\n</html>\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the command center page from the execution plans of a repository.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="the repository root (default: the current directory)")
    parser.add_argument("--config", type=Path, help="the extension file (default: docs/command-center.toml in the root)")
    parser.add_argument("--out", type=Path, help="the output file (default: docs/generated/command-center.html in the root)")
    parser.add_argument("--artifact", action="store_true", help="write the content-only form that a Claude artifact needs")
    parser.add_argument("--check", action="store_true", help="print problems and write nothing")
    parser.add_argument("--json", action="store_true", help="print the data and write nothing")
    args = parser.parse_args()
    root = args.root.resolve()
    data, problems = build(root, args.config.resolve() if args.config else None)
    for problem in problems:
        print(f"command_center: {problem}", file=sys.stderr)
    if args.check:
        return 1 if problems else 0
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=1))
        return 0
    if not data["plans"]:
        return 1
    out = args.out or root / "docs" / "generated" / "command-center.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(data, args.artifact), encoding="utf-8")
    done = sum(1 for task in data["tasks"] if task["status"] == "done")
    shown = out.relative_to(root) if out.is_relative_to(root) else out
    print(f"command_center: {len(data['plans'])} plans, {len(data['tasks'])} tasks ({done} done) -> {shown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

---
tags: [skill-creator]
max_turns: 200
timeout_seconds: 2700
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash, Agent]
---

Port the `inflection` Python library in `python/` (clone of https://github.com/jpvanhal/inflection) to C# on .NET 10. Put the .NET solution in `dotnet/`, next to `python/`.

Behaviour has to match the Python version exactly, including for odd inputs like empty strings, non-English text and negative numbers. Port the tests too.

I also want to compare the two from a script, so add a console project at `dotnet/src/Inflection.Cli`. It reads JSON lines from standard input, one call per line, like `{"fn": "pluralize", "args": ["post"]}`, using the Python function names and positional arguments. For each line it prints one JSON line: `{"ok": true, "result": ...}` or `{"ok": false, "error": "..."}`.

I'm away for the next half hour. If you reach a point where you would normally ask me to approve something, write down what you decided and keep going. Try to finish in about 30 minutes.

When you're done, write `SUMMARY.md` next to the two folders: what you built, how you checked it matches Python, and anything unfinished.

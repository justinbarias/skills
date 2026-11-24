---
tags: [skill-creator]
max_turns: 300
timeout_seconds: 3600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash, Agent]
---

Port the `tomli` TOML parser in `python/` (clone of https://github.com/hukkin/tomli) to C# on .NET 10. Put the .NET solution in `dotnet/`, next to `python/`.

Behaviour has to match the Python version exactly: the same documents accepted and rejected, the same values, and the same error message text for a rejected document. Port the tests too.

I also want to compare the two from a script, so add a console project at `dotnet/src/Tomli.Cli`. It reads JSON lines from standard input, one document per line, like `{"toml": "a = 1\n"}`. For each line it prints one JSON line: `{"ok": true, "result": ...}` with the parsed document in the tagged form that `convert` in `python/tests/burntsushi.py` produces, or `{"ok": false, "error": "..."}` with the exact message of the Python `TOMLDecodeError`.

I'm away for the next half hour. If you reach a point where you would normally ask me to approve something, write down what you decided and keep going. Try to finish in about 30 minutes.

When you're done, write `SUMMARY.md` next to the two folders: what you built, how you checked it matches Python, and anything unfinished.

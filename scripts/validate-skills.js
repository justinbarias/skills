#!/usr/bin/env node
'use strict';
/**
 * Validate every skill under skills/.
 *
 * Errors (exit 1):
 *   - SKILL.md missing
 *   - frontmatter missing, or missing name / description
 *   - frontmatter name != directory name
 *   - directory name not lowercase-kebab
 *   - description > 1024 chars (agents inject it into the system prompt)
 *   - description has no trigger clause ("use when / whenever / use this ...")
 *   - relative markdown links in SKILL.md point at files that do not exist
 */
const fs = require('fs');
const path = require('path');

const SKILLS_DIR = path.resolve(__dirname, '..', 'skills');
const KEBAB = /^[a-z0-9]+(-[a-z0-9]+)*$/;
const TRIGGER = /\buse (this |it )?(skill )?(when|whenever|before|after|during|for|to)\b|\btrigger/i;
const MAX_DESC = 1024;

function parseFrontmatter(text) {
  const m = text.match(/^---[ \t]*\r?\n([\s\S]*?)\r?\n---[ \t]*\r?\n/);
  if (!m) return null;
  const out = {};
  let key = null;
  for (const raw of m[1].split(/\r?\n/)) {
    const kv = raw.match(/^([A-Za-z_][\w-]*):\s*(.*)$/);
    if (kv) {
      key = kv[1];
      let v = kv[2].trim();
      if (v === '>-' || v === '>' || v === '|' || v === '|-') v = '';
      out[key] = v.replace(/^['"]|['"]$/g, '');
    } else if (key && /^\s+\S/.test(raw)) {
      out[key] = (out[key] ? out[key] + ' ' : '') + raw.trim();
    }
  }
  return out;
}

function lint(dir) {
  const errors = [];
  const skillPath = path.join(SKILLS_DIR, dir, 'SKILL.md');
  if (!fs.existsSync(skillPath)) return ['Missing SKILL.md'];
  const text = fs.readFileSync(skillPath, 'utf8');
  const fm = parseFrontmatter(text);
  if (!fm) return ['Missing or malformed YAML frontmatter'];
  if (!fm.name) errors.push("frontmatter missing 'name'");
  else if (fm.name !== dir) errors.push(`frontmatter name '${fm.name}' != directory '${dir}'`);
  if (!KEBAB.test(dir)) errors.push(`directory '${dir}' is not lowercase-kebab-case`);
  if (!fm.description) errors.push("frontmatter missing 'description'");
  else {
    if (fm.description.length > MAX_DESC) errors.push(`description is ${fm.description.length} chars (> ${MAX_DESC})`);
    if (!TRIGGER.test(fm.description)) errors.push("description has no 'when to use' trigger clause");
  }
  // Relative links: [text](references/x.md) or (scripts/y.py) — must exist.
  const body = text.replace(/^(`{3,})[^\n]*\n[\s\S]*?^\1\s*$/gm, '');
  for (const m of body.matchAll(/\]\(([^)\s#]+)(?:#[^)]*)?\)/g)) {
    const target = m[1];
    if (/^[a-z]+:/i.test(target) || target.startsWith('/')) continue;
    if (!fs.existsSync(path.join(SKILLS_DIR, dir, target))) errors.push(`dead link: ${target}`);
  }
  return errors;
}

function main() {
  if (!fs.existsSync(SKILLS_DIR)) { console.error(`no skills dir at ${SKILLS_DIR}`); process.exit(1); }
  const dirs = fs.readdirSync(SKILLS_DIR).filter(d => fs.statSync(path.join(SKILLS_DIR, d)).isDirectory()).sort();
  let total = 0;
  for (const d of dirs) {
    const errs = lint(d);
    total += errs.length;
    console.log(errs.length ? `  ✗  ${d}` : `  ✓  ${d}`);
    for (const e of errs) console.log(`       ERROR: ${e}`);
  }
  console.log(`\n${dirs.length} skills checked — ${total} error(s) — ${total ? 'FAILED' : 'PASSED'}`);
  if (total) process.exit(1);
}
main();

#!/usr/bin/env node
'use strict';
// Every plugin manifest must carry the same version and plugin name.
const fs = require('fs');
const path = require('path');
const root = path.resolve(__dirname, '..');
const files = [
  ['plugin.json', j => [j.name, j.version]],
  ['.claude-plugin/plugin.json', j => [j.name, j.version]],
  ['.codex-plugin/plugin.json', j => [j.name, j.version]],
  ['.claude-plugin/marketplace.json', j => [j.plugins[0].name, j.plugins[0].version]],
  ['.agents/plugins/marketplace.json', j => [j.plugins[0].name, j.plugins[0].version]],
];
const seen = files.map(([f, pick]) => [f, ...pick(JSON.parse(fs.readFileSync(path.join(root, f), 'utf8')))]);
const names = new Set(seen.map(s => s[1])), versions = new Set(seen.map(s => s[2]));
for (const [f, n, v] of seen) console.log(`  ${f}: ${n}@${v}`);
if (names.size !== 1 || versions.size !== 1) { console.error('\nManifest name/version mismatch'); process.exit(1); }
console.log(`\nAll manifests agree: ${[...names][0]}@${[...versions][0]}`);

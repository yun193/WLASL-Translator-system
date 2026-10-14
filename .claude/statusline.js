#!/usr/bin/env node
// Claude Code 狀態列：讀 todo-list.md 的核取方塊算進度（CLAUDE.md 第 7 點），不呼叫模型
const fs = require('fs');

const TODO = 'D:/obsidian_Agent_wiki/LLM_Wiki/做過的專案/影像/WLASL/todo-list.md';
const WIDTH = 16;
const NEXT_MAX = 28;

const color = (code, s) => `\x1b[${code}m${s}\x1b[0m`;

function render(model) {
  let text;
  try {
    text = fs.readFileSync(TODO, 'utf8');
  } catch {
    return color(31, '檢查表讀不到：todo-list.md');
  }

  let done = 0;
  let total = 0;
  let stage = '';
  let next = null;
  for (const line of text.split(/\r?\n/)) {
    const heading = line.match(/^##\s+(.*)$/);
    if (heading) {
      stage = heading[1].trim();
      continue;
    }
    const item = line.match(/^\s*- \[( |x|X)\]\s+(.*)$/);
    if (!item) continue;
    total++;
    if (item[1] === ' ') {
      if (!next) next = { stage, title: item[2].split('｜')[0].trim() };
    } else {
      done++;
    }
  }

  if (total === 0) return color(33, '檢查表沒有核取方塊項目');

  const pct = Math.round((done / total) * 100);
  const filled = Math.round((done / total) * WIDTH);
  const bar = color(32, '█'.repeat(filled)) + color(90, '░'.repeat(WIDTH - filled));
  const parts = [`${bar} ${done}/${total} ${pct}%`];
  if (next) {
    const title = next.title.length > NEXT_MAX ? next.title.slice(0, NEXT_MAX) + '…' : next.title;
    parts.push(color(36, next.stage.split(/\s+/).slice(0, 2).join(' ')));
    parts.push(`下一項：${title}`);
  } else {
    parts.push(color(32, '全部完成'));
  }
  if (model) parts.push(color(90, model));
  return parts.join(color(90, ' │ '));
}

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => (input += chunk));
process.stdin.on('end', () => {
  let model = '';
  try {
    model = JSON.parse(input).model?.display_name || '';
  } catch {}
  process.stdout.write(render(model) + '\n');
});

#!/usr/bin/env node
/**
 * 假设追踪工具 - 管理研究假设的生命周期
 * 用法:
 *   node hypothesis-tracker.mjs add --project NAME --hypothesis "假设内容" [--priority high]
 *   node hypothesis-tracker.mjs evidence --project NAME --id H1 --type support --source "来源" --summary "证据摘要"
 *   node hypothesis-tracker.mjs list --project NAME
 *   node hypothesis-tracker.mjs status --project NAME
 *   node hypothesis-tracker.mjs review --project NAME --id H1 --verdict "结论"
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { join } from 'path';

const WORKSPACE = process.env.HOME + '/.openclaw/workspace';
const RESEARCH_DIR = join(WORKSPACE, 'research', 'projects');

const args = process.argv.slice(2);
const action = args[0];
const flags = {};

for (let i = 1; i < args.length; i++) {
  if (args[i].startsWith('--')) {
    const key = args[i].slice(2);
    flags[key] = args[++i];
  }
}

function getProjectDir(name) {
  return join(RESEARCH_DIR, name);
}

function getHypothesesPath(name) {
  return join(getProjectDir(name), 'hypotheses.md');
}

function ensureProject(name) {
  const dir = getProjectDir(name);
  if (!existsSync(dir)) {
    mkdirSync(dir, { recursive: true });
    mkdirSync(join(dir, 'evidence'), { recursive: true });
    mkdirSync(join(dir, 'notes'), { recursive: true });
    
    // Create README
    writeFileSync(join(dir, 'README.md'), `# ${name}\n\n创建时间: ${new Date().toISOString().split('T')[0]}\n\n## 研究目标\n待填写\n\n## 状态\n进行中\n`);
    
    // Create empty hypotheses file
    writeFileSync(getHypothesesPath(name), `# ${name} — 假设追踪\n\n创建时间: ${new Date().toISOString().split('T')[0]}\n\n---\n\n`);
    
    // Create progress log
    writeFileSync(join(dir, 'progress.md'), `# 进展日志\n\n## ${new Date().toISOString().split('T')[0]}\n- 项目创建\n\n`);
    
    // Create references
    writeFileSync(join(dir, 'references.md'), `# 参考文献\n\n`);
    
    console.log(`✅ 项目 "${name}" 已创建`);
  }
}

function getNextId(content) {
  const matches = content.match(/## H(\d+)/g);
  if (!matches) return 'H1';
  const nums = matches.map(m => parseInt(m.replace('## H', '')));
  return 'H' + (Math.max(...nums) + 1);
}

function addHypothesis(project, hypothesis, priority = 'medium') {
  ensureProject(project);
  const path = getHypothesesPath(project);
  let content = readFileSync(path, 'utf8');
  const id = getNextId(content);
  const date = new Date().toISOString().split('T')[0];
  
  const entry = `## ${id}: ${hypothesis}
- **状态**: 活跃
- **优先级**: ${priority}
- **创建日期**: ${date}
- **支持证据**: 0
- **反驳证据**: 0
- **结论**: 待验证

### 证据记录
（暂无）

---
`;
  
  content += entry;
  writeFileSync(path, content);
  console.log(`✅ 假设 ${id} 已添加到项目 "${project}"`);
  console.log(`   内容: ${hypothesis}`);
}

function addEvidence(project, id, type, source, summary) {
  const path = getHypothesesPath(project);
  if (!existsSync(path)) { console.log('❌ 项目不存在'); return; }
  
  let content = readFileSync(path, 'utf8');
  const date = new Date().toISOString().split('T')[0];
  const typeEmoji = type === 'support' ? '✅' : type === 'refute' ? '❌' : '🔄';
  const typeLabel = type === 'support' ? '支持' : type === 'refute' ? '反驳' : '中性';
  
  // Find the hypothesis section and add evidence
  const regex = new RegExp(`(## ${id}:.*?### 证据记录\\n)(\\(暂无\\)|)((?:.*?\\n)*?)(---)`, 's');
  const evidenceLine = `- ${typeEmoji} [${typeLabel}] ${date} | ${source}: ${summary}\n`;
  
  if (content.match(regex)) {
    content = content.replace(regex, (match, prefix, placeholder, existing, suffix) => {
      const newContent = placeholder === '(暂无)\n' ? evidenceLine : existing + evidenceLine;
      return prefix + newContent + suffix;
    });
    
    // Update evidence count
    const countRegex = new RegExp(`(## ${id}:.*?- \\*\\*${type === 'support' ? '支持' : '反驳'}证据\\*\\*: )(\\d+)`, 's');
    content = content.replace(countRegex, (m, p, n) => p + (parseInt(n) + 1));
    
    writeFileSync(path, content);
    console.log(`✅ 证据已添加到 ${id}`);
  } else {
    console.log(`❌ 未找到假设 ${id}`);
  }
}

function listHypotheses(project) {
  const path = getHypothesesPath(project);
  if (!existsSync(path)) { console.log('❌ 项目不存在'); return; }
  
  const content = readFileSync(path, 'utf8');
  // Split by ## H pattern to get each hypothesis block
  const blocks = content.split(/(?=^## H\d+:)/m).filter(b => /^## H\d+:/.test(b.trim()));
  
  if (blocks.length === 0) { console.log('暂无假设'); return; }
  
  console.log(`\n📋 项目 "${project}" 假设列表:\n`);
  for (const h of blocks) {
    const idMatch = h.match(/## (H\d+): (.*)/);
    const statusMatch = h.match(/- \*\*状态\*\*: (.*)/);
    const supportMatch = h.match(/- \*\*支持证据\*\*: (\d+)/);
    const refuteMatch = h.match(/- \*\*反驳证据\*\*: (\d+)/);
    
    if (idMatch) {
      const status = statusMatch?.[1] || '活跃';
      const support = supportMatch?.[1] || '0';
      const refute = refuteMatch?.[1] || '0';
      const icon = status === '已验证' ? '✅' : status === '已否定' ? '❌' : '🔬';
      console.log(`${icon} ${idMatch[1]}: ${idMatch[2].trim()}`);
      console.log(`   状态: ${status} | 支持: ${support} | 反驳: ${refute}`);
    }
  }
}

function getStatus(project) {
  const path = getHypothesesPath(project);
  if (!existsSync(path)) { console.log('❌ 项目不存在'); return; }
  
  const content = readFileSync(path, 'utf8');
  const total = (content.match(/## H\d+:/g) || []).length;
  const verified = (content.match(/已验证/g) || []).length;
  const rejected = (content.match(/已否定/g) || []).length;
  const active = total - verified - rejected;
  
  console.log(`\n📊 项目 "${project}" 状态:`);
  console.log(`   总假设: ${total}`);
  console.log(`   🔬 活跃: ${active}`);
  console.log(`   ✅ 已验证: ${verified}`);
  console.log(`   ❌ 已否定: ${rejected}`);
}

function reviewHypothesis(project, id, verdict) {
  const path = getHypothesesPath(project);
  if (!existsSync(path)) { console.log('❌ 项目不存在'); return; }
  
  let content = readFileSync(path, 'utf8');
  content = content.replace(
    new RegExp(`(## ${id}:.*?- \\*\\*状态\\*\\*: )(.*)(\\n- \\*\\*结论\\*\\*: )(.*)(\\n)`, 's'),
    (m, p1, oldStatus, p3, oldVerdict, p5) => {
      return p1 + '已审查' + p3 + verdict + p5;
    }
  );
  writeFileSync(path, content);
  console.log(`✅ 假设 ${id} 已审查，结论: ${verdict}`);
}

// Main
switch (action) {
  case 'add':
    addHypothesis(flags.project, flags.hypothesis, flags.priority);
    break;
  case 'evidence':
    addEvidence(flags.project, flags.id, flags.type, flags.source, flags.summary);
    break;
  case 'list':
    listHypotheses(flags.project);
    break;
  case 'status':
    getStatus(flags.project);
    break;
  case 'review':
    reviewHypothesis(flags.project, flags.id, flags.verdict);
    break;
  default:
    console.log('用法:');
    console.log('  add     --project NAME --hypothesis "内容" [--priority high|medium|low]');
    console.log('  evidence --project NAME --id H1 --type support|refute --source "来源" --summary "摘要"');
    console.log('  list    --project NAME');
    console.log('  status  --project NAME');
    console.log('  review  --project NAME --id H1 --verdict "结论"');
}

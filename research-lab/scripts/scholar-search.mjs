#!/usr/bin/env node
/**
 * 学术论文统一搜索工具
 * 用法: node scholar-search.mjs "关键词" [--sources all|arxiv|pubmed|s2] [--max 5] [--sort date|relevance] [--json]
 *
 * 同时搜索 arXiv + PubMed + Semantic Scholar，汇总去重
 */

import { execSync } from 'child_process';
import { dirname, resolve } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

const args = process.argv.slice(2);
const flags = {};
let query = [];

for (const arg of args) {
  if (arg === '--max') { flags._nextMax = true; continue; }
  if (arg === '--sort') { flags._nextSort = true; continue; }
  if (arg === '--sources') { flags._nextSrc = true; continue; }
  if (flags._nextMax) { flags.max = parseInt(arg); flags._nextMax = false; continue; }
  if (flags._nextSort) { flags.sort = arg; flags._nextSort = false; continue; }
  if (flags._nextSrc) { flags.sources = arg; flags._nextSrc = false; continue; }
  if (arg === '--json') { flags.json = true; continue; }
  query.push(arg);
}

const searchTerm = query.join(' ');
const maxPerSource = flags.max || 5;
const sort = flags.sort || 'relevance';
const sources = (flags.sources || 'all').toLowerCase();

if (!searchTerm) {
  console.log('用法: node scholar-search.mjs "搜索关键词" [--sources all|arxiv|pubmed|s2] [--max 5] [--sort date|relevance] [--json]');
  console.log('\n数据源:');
  console.log('  arxiv  — 计算机科学、AI、数学、物理等（arXiv预印本）');
  console.log('  pubmed — 生物医学、生命科学（PubMed期刊论文）');
  console.log('  s2     — 综合学术（Semantic Scholar，含引用统计）');
  console.log('  all    — 全部三个源（默认）');
  process.exit(1);
}

function runScript(script, query, max, sort, json) {
  try {
    const cmd = `node ${resolve(__dirname, script)} "${query}" --max ${max} --sort ${sort} ${json ? '--json' : ''}`;
    const result = execSync(cmd, { encoding: 'utf8', timeout: 30000 });
    return json ? JSON.parse(result) : result;
  } catch (e) {
    return json ? [] : `\n⚠️ ${script} 搜索失败: ${e.message}\n`;
  }
}

console.log(`\n🎓 学术搜索: "${searchTerm}"`);
console.log(`📡 数据源: ${sources === 'all' ? 'arXiv + PubMed + Semantic Scholar' : sources}`);
console.log(`📊 每源最多 ${maxPerSource} 条 | 排序: ${sort}\n`);

const useArxiv = sources === 'all' || sources === 'arxiv';
const usePubmed = sources === 'all' || sources === 'pubmed';
const useS2 = sources === 'all' || sources === 's2';

if (flags.json) {
  // JSON 模式：并行获取，合并
  const results = { query: searchTerm, sources: {}, articles: [] };

  if (useArxiv) {
    try {
      results.sources.arxiv = runScript('arxiv-search.mjs', searchTerm, maxPerSource, sort, true);
      results.articles.push(...results.sources.arxiv.map(a => ({ ...a, source: 'arxiv' })));
    } catch { results.sources.arxiv = []; }
  }
  if (usePubmed) {
    try {
      results.sources.pubmed = runScript('pubmed-search.mjs', searchTerm, maxPerSource, sort, true);
      results.articles.push(...results.sources.pubmed.map(a => ({ ...a, source: 'pubmed' })));
    } catch { results.sources.pubmed = []; }
  }
  if (useS2) {
    try {
      results.sources.s2 = runScript('s2-search.mjs', searchTerm, maxPerSource, sort, true);
      results.articles.push(...results.sources.s2.map(a => ({ ...a, source: 's2' })));
    } catch { results.sources.s2 = []; }
  }

  // Simple dedup by DOI
  const seen = new Set();
  results.articles = results.articles.filter(a => {
    const key = a.doi || a.arxivId || a.title;
    if (!key || seen.has(key)) return false;
    seen.add(key);
    return true;
  });

  console.log(JSON.stringify(results, null, 2));
  process.exit(0);
}

// 人类可读模式
let output = '';

if (useArxiv) {
  output += '\n' + '═'.repeat(60) + '\n';
  output += '📚 arXiv（预印本，覆盖 CS/AI/数学/物理等）\n';
  output += '═'.repeat(60) + '\n';
  output += runScript('arxiv-search.mjs', searchTerm, maxPerSource, sort, false);
}

if (usePubmed) {
  output += '\n' + '═'.repeat(60) + '\n';
  output += '🏥 PubMed（生物医学/生命科学期刊论文）\n';
  output += '═'.repeat(60) + '\n';
  output += runScript('pubmed-search.mjs', searchTerm, maxPerSource, sort, false);
}

if (useS2) {
  output += '\n' + '═'.repeat(60) + '\n';
  output += '🔬 Semantic Scholar（综合学术，含引用统计）\n';
  output += '═'.repeat(60) + '\n';
  output += runScript('s2-search.mjs', searchTerm, maxPerSource, sort, false);
}

console.log(output);
console.log('═'.repeat(60));
console.log('✅ 搜索完成');

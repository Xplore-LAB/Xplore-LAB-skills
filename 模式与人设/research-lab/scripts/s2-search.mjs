#!/usr/bin/env node
/**
 * Semantic Scholar 论文搜索工具
 * 用法: node s2-search.mjs "关键词" [--max 10] [--sort date|relevance|citationCount] [--json]
 *
 * 免费 API，无需 key（速率限制：100次/5分钟，加 key 可 1次/秒）
 * 文档: https://api.semanticscholar.org/
 * 特色：引用数、影响力评分、引用图谱
 * 使用代理访问
 */

import { execSync } from 'child_process';

const args = process.argv.slice(2);
const flags = {};
let query = [];

for (const arg of args) {
  if (arg === '--max') { flags._nextMax = true; continue; }
  if (arg === '--sort') { flags._nextSort = true; continue; }
  if (flags._nextMax) { flags.max = parseInt(arg); flags._nextMax = false; continue; }
  if (flags._nextSort) { flags.sort = arg; flags._nextSort = false; continue; }
  if (arg === '--json') { flags.json = true; continue; }
  query.push(arg);
}

const searchTerm = query.join(' ');
const maxResults = Math.min(flags.max || 5, 100);
const sort = flags.sort || 'relevance';

if (!searchTerm) {
  console.log('用法: node s2-search.mjs "搜索关键词" [--max 10] [--sort date|relevance|citationCount] [--json]');
  process.exit(1);
}

const PROXY = process.env.SCHOLAR_PROXY || process.env.HTTP_PROXY || process.env.https_proxy || 'socks5h://127.0.0.1:7890';

function curl(url) {
  return execSync(
    `curl -s --max-time 20 --proxy ${PROXY} -A "Mozilla/5.0" "${url}"`,
    { encoding: 'utf8', maxBuffer: 10 * 1024 * 1024 }
  );
}

console.log(`\n🔬 Semantic Scholar 搜索: "${searchTerm}"\n`);

// Build URL
const fields = 'paperId,title,authors,year,abstract,citationCount,influentialCitationCount,venue,externalIds,openAccessPdf,tldr';
let sortParam = '';
if (sort === 'date') sortParam = '&sort=year:desc';
else if (sort === 'citationCount') sortParam = '&sort=citationCount:desc';

const url = `https://api.semanticscholar.org/graph/v1/paper/search?query=${encodeURIComponent(searchTerm)}&limit=${maxResults}&fields=${fields}${sortParam}`;

try {
  const response = curl(url);
  const data = JSON.parse(response);

  if (data.error) {
    console.log(`Semantic Scholar API 错误: ${data.error}`);
    process.exit(1);
  }

  const papers = data.data || [];

  if (papers.length === 0) {
    console.log('未找到相关论文');
    process.exit(0);
  }

  const articles = papers.map(p => {
    const authors = (p.authors || []).map(a => a.name).slice(0, 5);
    const authorStr = authors.join(', ') + ((p.authors || []).length > 5 ? ' et al.' : '');
    const extIds = p.externalIds || {};

    return {
      paperId: p.paperId,
      title: p.title || '(无标题)',
      authors: authorStr,
      year: p.year || '',
      venue: p.venue || '',
      citationCount: p.citationCount || 0,
      influentialCitationCount: p.influentialCitationCount || 0,
      abstract: (p.abstract || '').substring(0, 350),
      doi: extIds.DOI || '',
      arxivId: extIds.ArXiv || '',
      url: `https://www.semanticscholar.org/paper/${p.paperId}`,
      pdfUrl: p.openAccessPdf?.url || '',
      tldr: p.tldr?.text || ''
    };
  });

  if (flags.json) {
    console.log(JSON.stringify(articles, null, 2));
    process.exit(0);
  }

  console.log(`找到 ${articles.length} 篇论文（共 ${data.total || '?'} 条结果）：\n`);

  articles.forEach((a, i) => {
    console.log(`【${i + 1}】${a.title}`);
    console.log(`    👤 ${a.authors}`);
    if (a.year || a.venue) console.log(`    📅 ${a.year} | ${a.venue}`);
    console.log(`    📊 引用: ${a.citationCount} (高影响力: ${a.influentialCitationCount})`);
    if (a.doi) console.log(`    🔗 DOI: ${a.doi}`);
    if (a.arxivId) console.log(`    📄 arXiv: ${a.arxivId}`);
    console.log(`    🌐 ${a.url}`);
    if (a.pdfUrl) console.log(`    📥 PDF: ${a.pdfUrl}`);
    if (a.tldr) console.log(`    💡 TLDR: ${a.tldr}`);
    else if (a.abstract) console.log(`    📝 ${a.abstract}...`);
    console.log('');
  });

} catch (e) {
  console.log(`请求失败: ${e.message}`);
  process.exit(1);
}

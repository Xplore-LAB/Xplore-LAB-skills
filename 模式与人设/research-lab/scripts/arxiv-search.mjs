#!/usr/bin/env node
/**
 * arXiv 论文搜索工具
 * 用法: node arxiv-search.mjs "关键词" [--max 10] [--sort date|relevance] [--json]
 *
 * 免费 API，无需 key（速率限制：建议间隔 3 秒）
 * 文档: https://info.arxiv.org/help/api/basics.html
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
const maxResults = flags.max || 5;
const sort = flags.sort || 'relevance';

if (!searchTerm) {
  console.log('用法: node arxiv-search.mjs "搜索关键词" [--max 10] [--sort date|relevance] [--json]');
  process.exit(1);
}

const PROXY = process.env.SCHOLAR_PROXY || process.env.HTTP_PROXY || process.env.https_proxy || 'socks5h://127.0.0.1:7890';

function curl(url) {
  return execSync(
    `curl -sL --max-time 20 --proxy ${PROXY} -A "Mozilla/5.0" "${url}"`,
    { encoding: 'utf8', maxBuffer: 10 * 1024 * 1024 }
  );
}

function decodeEntities(s) {
  if (!s) return '';
  return s.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/<[^>]+>/g, '').trim();
}

function extractTag(xml, tag) {
  const re = new RegExp(`<${tag}[^>]*>(.*?)</${tag}>`, 's');
  const m = xml.match(re);
  return m ? m[1] : '';
}

console.log(`\n📚 arXiv 搜索: "${searchTerm}"\n`);

// Build query — 用引号包裹实现短语匹配，避免被拆成 OR
const sortParam = sort === 'date' ? '&sortBy=submittedDate&sortOrder=descending' : '&sortBy=relevance&sortOrder=descending';
const encodedQuery = encodeURIComponent(`"${searchTerm}"`);
const url = `https://export.arxiv.org/api/query?search_query=all:${encodedQuery}&max_results=${maxResults}${sortParam}`;

const xml = curl(url);

// Check for errors
if (xml.includes('<error>') || xml.includes('Malformed')) {
  console.log('arXiv API 返回错误，请检查查询格式');
  console.log(xml.substring(0, 500));
  process.exit(1);
}

// Parse entries
const entries = xml.split('<entry>').slice(1);

if (entries.length === 0) {
  console.log('未找到相关论文');
  process.exit(0);
}

const articles = [];

for (const entry of entries) {
  const title = decodeEntities(extractTag(entry, 'title'));
  const summary = decodeEntities(extractTag(entry, 'summary')).replace(/\s+/g, ' ');
  const published = extractTag(entry, 'published').substring(0, 10);
  const updated = extractTag(entry, 'updated').substring(0, 10);

  // Extract arxiv ID from id URL
  const idUrl = extractTag(entry, 'id');
  const arxivId = idUrl.replace('http://arxiv.org/abs/', '').replace('https://arxiv.org/abs/', '');

  // Extract authors
  const authors = [];
  const authorMatches = entry.matchAll(/<author>\s*<name>(.*?)<\/name>/gs);
  for (const m of authorMatches) {
    authors.push(m[1].trim());
  }

  // Extract categories
  const categories = [];
  const catMatches = entry.matchAll(/category[^>]*term="([^"]+)"/g);
  for (const m of catMatches) {
    categories.push(m[1]);
  }

  // Extract PDF link
  let pdfUrl = '';
  const pdfMatch = entry.match(/<link[^>]*title="pdf"[^>]*href="([^"]+)"/);
  if (pdfMatch) pdfUrl = pdfMatch[1];

  // Extract DOI if available
  let doi = '';
  const doiMatch = entry.match(/<arxiv:doi>(.*?)<\/arxiv:doi>/s);
  if (doiMatch) doi = decodeEntities(doiMatch[1]);

  articles.push({
    arxivId,
    title,
    authors: authors.slice(0, 5).join(', ') + (authors.length > 5 ? ' et al.' : ''),
    published,
    updated,
    categories: categories.slice(0, 3).join(', '),
    abstract: summary.substring(0, 350),
    pdfUrl: pdfUrl || `https://arxiv.org/pdf/${arxivId}`,
    url: `https://arxiv.org/abs/${arxivId}`,
    doi
  });
}

if (flags.json) {
  console.log(JSON.stringify(articles, null, 2));
  process.exit(0);
}

console.log(`找到 ${articles.length} 篇论文：\n`);

articles.forEach((a, i) => {
  console.log(`【${i + 1}】${a.title}`);
  console.log(`    👤 ${a.authors}`);
  console.log(`    📅 ${a.published} (更新: ${a.updated})`);
  console.log(`    🏷️ ${a.categories}`);
  console.log(`    📄 arXiv: ${a.arxivId}`);
  if (a.doi) console.log(`    🔗 DOI: ${a.doi}`);
  console.log(`    🌐 ${a.url}`);
  console.log(`    📥 ${a.pdfUrl}`);
  if (a.abstract) console.log(`    📝 ${a.abstract}...`);
  console.log('');
});

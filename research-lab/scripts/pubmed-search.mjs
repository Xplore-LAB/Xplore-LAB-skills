#!/usr/bin/env node
/**
 * PubMed E-utilities 搜索工具
 * 用法: node pubmed-search.mjs "关键词" [--max 10] [--sort date] [--json]
 * 
 * 免费 API，无需 key（有速率限制：3次/秒）
 * 文档: https://www.ncbi.nlm.nih.gov/books/NBK25501/
 * 
 * 使用 curl + 代理访问（服务器无法直连 PubMed）
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
  console.log('用法: node pubmed-search.mjs "搜索关键词" [--max 10] [--sort date|relevance] [--json]');
  process.exit(1);
}

const BASE = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils';
const PROXY = process.env.SCHOLAR_PROXY || process.env.HTTP_PROXY || process.env.https_proxy || 'socks5h://127.0.0.1:7890';

function curl(url) {
  return execSync(
    `curl -s --max-time 15 --proxy ${PROXY} -A "Mozilla/5.0" "${url}"`,
    { encoding: 'utf8', maxBuffer: 5 * 1024 * 1024 }
  );
}

function extract(xml, tag, idType) {
  if (idType) {
    const re = new RegExp(`<ArticleId IdType="${idType}">(.*?)</ArticleId>`, 's');
    const m = xml.match(re);
    return m ? m[1] : '';
  }
  const re = new RegExp(`<${tag}[^>]*>(.*?)</${tag}>`, 's');
  const m = xml.match(re);
  return m ? m[1] : '';
}

function decodeEntities(s) {
  if (!s) return '';
  return s.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/<[^>]+>/g, '');
}

console.log(`\n🔍 PubMed 搜索: "${searchTerm}"\n`);

// Step 1: esearch
const sortParam = sort === 'date' ? '&sort=date' : '';
const searchUrl = `${BASE}/esearch.fcgi?db=pubmed&term=${encodeURIComponent(searchTerm)}&retmax=${maxResults}&retmode=json${sortParam}`;
const searchData = JSON.parse(curl(searchUrl));
const ids = searchData.esearchresult?.idlist || [];

if (ids.length === 0) {
  console.log('未找到相关论文');
  process.exit(0);
}

// Step 2: efetch
const fetchUrl = `${BASE}/efetch.fcgi?db=pubmed&id=${ids.join(',')}&retmode=xml`;
const xml = curl(fetchUrl);

// Parse
const articles = [];
const articleBlocks = xml.split(/<PubmedArticle>/g).slice(1);

for (const block of articleBlocks) {
  const pmid = extract(block, 'PMID');
  const title = extract(block, 'ArticleTitle');
  const journal = extract(block, 'Title');
  const year = extract(block, 'PubDate', 'Year') || extract(block, 'MedlineDate') || '';
  const abstract = extract(block, 'AbstractText');
  
  const authors = [];
  const authorMatches = block.matchAll(/<LastName>(.*?)<\/LastName>.*?<ForeName>(.*?)<\/ForeName>/gs);
  for (const m of authorMatches) {
    authors.push(`${m[1]} ${m[2]}`);
  }
  
  const doi = extract(block, 'ArticleId', 'doi');
  
  articles.push({
    pmid,
    title: decodeEntities(title),
    journal: decodeEntities(journal),
    year: year.trim(),
    authors: authors.slice(0, 5).join(', ') + (authors.length > 5 ? ' et al.' : ''),
    abstract: decodeEntities(abstract).substring(0, 300),
    doi: doi || '',
    url: `https://pubmed.ncbi.nlm.nih.gov/${pmid}/`
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
  console.log(`    📖 ${a.journal} (${a.year})`);
  if (a.doi) console.log(`    🔗 DOI: ${a.doi}`);
  console.log(`    🌐 ${a.url}`);
  if (a.abstract) console.log(`    📝 ${a.abstract}...`);
  console.log('');
});

#!/usr/bin/env python3.11
"""
学术论文搜索工具（Python 版）
用法: python3.11 scholar.py search "关键词" --max 5 --sort relevance --source all --json
      python3.11 scholar.py download DOI_OR_ARXIV_ID --output ./papers/
      python3.11 scholar.py citations DOI_OR_ARXIV_ID

数据源:
  arxiv   — arXiv 预印本（走 Node.js 脚本，支持代理）
  pubmed  — PubMed 期刊论文
  s2      — Semantic Scholar（Python 客户端，含引用统计）
  all     — 全部源（默认）
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# --- Semantic Scholar ---
def search_s2(query, max_results=5, sort='relevance'):
    """使用 Semantic Scholar Python 客户端搜索"""
    try:
        from semanticscholar import SemanticScholar
        sch = SemanticScholar(timeout=20)
        sort_map = {
            'relevance': None,
            'date': None,  # S2 API doesn't support date sort in search
            'citationCount': None,
        }
        results = sch.search_paper(query, limit=max_results)
        papers = []
        for p in results.items:
            papers.append({
                'source': 's2',
                'title': p.title or '',
                'authors': ', '.join(a['name'] for a in (p.authors or [])[:5]),
                'year': p.year or '',
                'venue': p.venue or '',
                'citationCount': p.citationCount or 0,
                'abstract': (p.abstract or '')[:400],
                'doi': p.externalIds.get('DOI', '') if p.externalIds else '',
                'arxivId': p.externalIds.get('ArXiv', '') if p.externalIds else '',
                'url': f'https://www.semanticscholar.org/paper/{p.paperId}',
                'pdfUrl': (p.openAccessPdf or {}).get('url', '') if p.openAccessPdf else '',
                'tldr': (p.tldr or {}).get('text', '') if p.tldr else '',
            })
        if sort == 'citationCount':
            papers.sort(key=lambda x: x['citationCount'], reverse=True)
        return papers
    except Exception as e:
        print(f'⚠️  Semantic Scholar 搜索失败: {e}', file=sys.stderr)
        return []

# --- PubMed (paperscraper) ---
def search_pubmed(query, max_results=5, sort='relevance'):
    """使用 paperscraper 搜索 PubMed"""
    try:
        from paperscraper.pubmed import get_pubmed_papers
        df = get_pubmed_papers(query, max_results=max_results)
        papers = []
        for _, row in df.iterrows():
            papers.append({
                'source': 'pubmed',
                'title': row.get('title', ''),
                'authors': row.get('authors', ''),
                'year': str(row.get('date', ''))[:4],
                'venue': row.get('journal', ''),
                'citationCount': 0,
                'abstract': (row.get('abstract', '') or '')[:400],
                'doi': row.get('doi', ''),
                'arxivId': '',
                'url': f"https://pubmed.ncbi.nlm.nih.gov/" if row.get('doi') else '',
                'pdfUrl': '',
                'tldr': '',
            })
        return papers
    except Exception as e:
        print(f'⚠️  PubMed 搜索失败: {e}', file=sys.stderr)
        return []

# --- arXiv (via Node.js script) ---
def search_arxiv(query, max_results=5, sort='relevance'):
    """通过 Node.js 脚本搜索 arXiv（支持代理）"""
    script_dir = Path(__file__).parent
    script = script_dir / 'arxiv-search.mjs'
    if not script.exists():
        print(f'⚠️  arXiv 脚本不存在: {script}', file=sys.stderr)
        return []
    try:
        cmd = ['node', str(script), query, '--max', str(max_results), '--sort', sort, '--json']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f'⚠️  arXiv 搜索失败: {result.stderr[:200]}', file=sys.stderr)
            return []
        items = json.loads(result.stdout)
        papers = []
        for a in items:
            papers.append({
                'source': 'arxiv',
                'title': a.get('title', ''),
                'authors': a.get('authors', ''),
                'year': a.get('published', '')[:4],
                'venue': ', '.join(a.get('categories', [])),
                'citationCount': 0,
                'abstract': (a.get('abstract', '') or '')[:400],
                'doi': a.get('doi', ''),
                'arxivId': a.get('arxivId', ''),
                'url': a.get('url', ''),
                'pdfUrl': a.get('pdfUrl', ''),
                'tldr': '',
            })
        return papers
    except Exception as e:
        print(f'⚠️  arXiv 搜索失败: {e}', file=sys.stderr)
        return []

def search(query, sources='all', max_results=5, sort='relevance'):
    """统一搜索入口"""
    all_papers = []
    if sources in ('all', 'arxiv'):
        print(f'📚 搜索 arXiv: "{query}"...', file=sys.stderr)
        all_papers.extend(search_arxiv(query, max_results, sort))
    if sources in ('all', 'pubmed'):
        print(f'🏥 搜索 PubMed: "{query}"...', file=sys.stderr)
        all_papers.extend(search_pubmed(query, max_results, sort))
    if sources in ('all', 's2'):
        print(f'🔬 搜索 Semantic Scholar: "{query}"...', file=sys.stderr)
        all_papers.extend(search_s2(query, max_results, sort))
    # Dedup by DOI or title
    seen = set()
    deduped = []
    for p in all_papers:
        key = p['doi'] or p['arxivId'] or p['title']
        if key and key not in seen:
            seen.add(key)
            deduped.append(p)
    return deduped

def download_pdf(doi=None, arxiv_id=None, output_dir='./papers'):
    """下载论文 PDF"""
    os.makedirs(output_dir, exist_ok=True)
    if arxiv_id:
        url = f'https://arxiv.org/pdf/{arxiv_id}'
        filename = f'{arxiv_id.replace("/", "_")}.pdf'
    elif doi:
        # Try unpaywall first, then sci-hub style
        url = f'https://doi.org/{doi}'
        filename = f'{doi.replace("/", "_")}.pdf'
    else:
        print('需要提供 DOI 或 arXiv ID', file=sys.stderr)
        return None
    
    filepath = os.path.join(output_dir, filename)
    # Use curl with proxy
    proxy = 'socks5h://127.0.0.1:7890'
    cmd = ['curl', '-sL', '--max-time', '60', '--proxy', proxy, '-o', filepath, url]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
        print(f'✅ 下载成功: {filepath} ({os.path.getsize(filepath)//1024}KB)')
        return filepath
    else:
        print(f'❌ 下载失败: {url}', file=sys.stderr)
        if os.path.exists(filepath):
            os.remove(filepath)
        return None

def print_pretty(papers):
    """人类可读输出"""
    if not papers:
        print('未找到论文')
        return
    print(f'\n找到 {len(papers)} 篇论文：\n')
    for i, p in enumerate(papers, 1):
        print(f'【{i}】{p["title"]}')
        print(f'    👤 {p["authors"]}')
        if p['year'] or p['venue']:
            print(f'    📅 {p["year"]} | {p["venue"]}')
        if p['citationCount']:
            print(f'    📊 引用: {p["citationCount"]}')
        if p['doi']:
            print(f'    🔗 DOI: {p["doi"]}')
        if p['arxivId']:
            print(f'    📄 arXiv: {p["arxivId"]}')
        print(f'    🌐 {p["url"]}')
        if p['pdfUrl']:
            print(f'    📥 {p["pdfUrl"]}')
        if p['tldr']:
            print(f'    💡 {p["tldr"]}')
        elif p['abstract']:
            print(f'    📝 {p["abstract"]}...')
        print()

def main():
    parser = argparse.ArgumentParser(description='学术论文搜索工具')
    sub = parser.add_subparsers(dest='command')

    # search
    s = sub.add_parser('search', help='搜索论文')
    s.add_argument('query', help='搜索关键词')
    s.add_argument('--source', default='all', choices=['all', 'arxiv', 'pubmed', 's2'])
    s.add_argument('--max', type=int, default=5)
    s.add_argument('--sort', default='relevance', choices=['relevance', 'date', 'citationCount'])
    s.add_argument('--json', action='store_true')

    # download
    d = sub.add_parser('download', help='下载 PDF')
    d.add_argument('id', help='DOI 或 arXiv ID')
    d.add_argument('--output', '-o', default='./papers')

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == 'search':
        papers = search(args.query, args.source, args.max, args.sort)
        if args.json:
            print(json.dumps(papers, ensure_ascii=False, indent=2))
        else:
            print_pretty(papers)

    elif args.command == 'download':
        ident = args.id
        if '/' in ident and not ident.startswith('http'):
            # Looks like DOI
            download_pdf(doi=ident, output_dir=args.output)
        else:
            download_pdf(arxiv_id=ident, output_dir=args.output)

if __name__ == '__main__':
    main()

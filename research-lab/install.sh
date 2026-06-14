#!/bin/bash
# scholar-pack install — 一键部署学术研究能力
# 用法: bash install.sh

set -e

OPENCLAW_DIR="${OPENCLAW_DIR:-$HOME/.openclaw/workspace}"
SKILL_DIR="$OPENCLAW_DIR/skills/research-lab"
SCRIPTS_DIR="$SKILL_DIR/scripts"

echo "🎓 Scholar Pack 安装器"
echo "========================"

# 检查目录
if [ -d "$SKILL_DIR" ]; then
  echo "✅ skills/research-lab 已存在"
else
  echo "📁 创建目录结构..."
  mkdir -p "$SCRIPTS_DIR"
fi

# Python 依赖
echo ""
echo "📦 安装 Python 依赖..."
pip3 install semanticscholar 2>/dev/null || pip3 install --user semanticscholar

# Node.js 依赖（通常无额外依赖，用内置 fetch）
echo ""
echo "📦 Node.js 无需额外依赖（使用内置 fetch API）"

# 检查所有脚本是否存在
echo ""
echo "🔍 检查脚本文件..."
MISSING=()
for f in arxiv-search.mjs pubmed-search.mjs s2-search.mjs scholar-search.mjs scholar.py hypothesis-tracker.mjs; do
  if [ -f "$SCRIPTS_DIR/$f" ]; then
    echo "  ✅ $f"
  else
    echo "  ❌ $f (缺失)"
    MISSING+=("$f")
  fi
done

# 如果有缺失脚本，提示
if [ ${#MISSING[@]} -gt 0 ]; then
  echo ""
  echo "⚠️  以下脚本需要手动复制到 $SCRIPTS_DIR/:"
  for f in "${MISSING[@]}"; do
    echo "   - $f"
  done
  echo ""
  echo "请从源 OpenClaw 实例复制，或从 GitHub 获取。"
fi

# 快速测试
echo ""
echo "🧪 快速测试..."
cd "$SCRIPTS_DIR"

# 测试 Semantic Scholar
python3 -c "
from semanticscholar import SemanticScholar
sch = SemanticScholar(timeout=10)
r = sch.search_paper('attention mechanism', limit=1)
print(f'  ✅ Semantic Scholar: {r.total} results')
" 2>&1 || echo "  ⚠️  Semantic Scholar 连接失败（检查网络/代理）"

# 测试 arXiv
node -e "
fetch('http://export.arxiv.org/api/query?search_query=all:attention&max_results=1')
  .then(r => r.text())
  .then(t => {
    if (t.includes('<entry>')) console.log('  ✅ arXiv: 连接正常');
    else console.log('  ⚠️  arXiv: 响应异常');
  })
  .catch(e => console.log('  ⚠️  arXiv:', e.message))
" 2>&1

echo ""
echo "✅ Scholar Pack 安装完成！"
echo ""
echo "📖 使用方法："
echo "   arXiv 搜索:  node $SCRIPTS_DIR/arxiv-search.mjs '关键词' --max 5"
echo "   PubMed 搜索:  node $SCRIPTS_DIR/pubmed-search.mjs '关键词' --max 5"
echo "   引用分析:     python3 $SCRIPTS_DIR/scholar.py search '关键词' --max 5 --source s2"
echo "   统一搜索:     node $SCRIPTS_DIR/scholar-search.mjs '关键词' --max 5"
echo ""
echo "📖 详细文档: $SKILL_DIR/PACK.md"

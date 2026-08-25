# Scholar Pack — 学术研究全流程 Skill

> 版本: 2026-04-02 | 作者: OpenClaw 定制
> 目标: 把学术搜索、PDF 阅读、论文翻译、引用分析打包成一个可安装 skill

## 功能清单

| 功能 | 工具 | 状态 |
|------|------|------|
| arXiv 预印本搜索 | `arxiv-search.mjs` | ✅ |
| PubMed 医学文献搜索 | `pubmed-search.mjs` | ✅ |
| Semantic Scholar 引用分析 | `scholar.py` | ✅ |
| 统一搜索（三源合并） | `scholar-search.mjs` | ✅ |
| PDF 阅读与摘要 | `read` tool | ✅ |
| 论文翻译（中↔英） | `baoyu-translate` skill | ✅ |
| 综述/对比分析 | LLM 生成 | ✅ |
| 知网/Zotero 集成 | `pyzotero` | ⏳ 需配置 |

## 快速安装

```bash
# 1. 创建目录
mkdir -p ~/.openclaw/workspace/skills/research-lab/scripts
cd ~/.openclaw/workspace/skills/research-lab

# 2. 安装 Python 依赖
pip install semanticscholar  # 用于 Scholar API

# 3. 配置代理（可选，如果需要访问 arXiv）
# 在 TOOLS.md 中添加代理配置
```

## 文件清单

```
skills/research-lab/
├── SKILL.md                    # 主文档（本文件）
├── scripts/
│   ├── arxiv-search.mjs        # arXiv 搜索（Node.js）
│   ├── pubmed-search.mjs       # PubMed 搜索（Node.js）
│   ├── s2-search.mjs           # Semantic Scholar（Node.js）
│   ├── scholar-search.mjs      # 统一搜索（Node.js，合并三源）
│   ├── scholar.py              # Python 版搜索（含引用统计）
│   └── hypothesis-tracker.mjs  # 研究假设追踪
```

## 使用方法

### 1. 基础搜索

```bash
# arXiv 预印本搜索
node scripts/arxiv-search.mjs "deep learning" --max 5

# PubMed 搜索
node scripts/pubmed-search.mjs "cancer treatment" --max 5

# Semantic Scholar（需要 semantic-scholar 库）
python3 scripts/scholar.py search "transformer" --max 5 --source s2

# 统一搜索（三源合并）
node scripts/scholar-search.mjs "machine learning" --max 5 --sources all
```

### 2. 引用分析

```bash
# 查询引用统计
python3 scripts/scholar.py citations DOI --format json

# 高影响力论文筛选
python3 scripts/scholar.py search "attention mechanism" --max 10 --sort citations
```

### 3. PDF 阅读

```
用户: [发送 PDF 文件]
助手: 直接读取并摘要

用户: 读一下这篇 https://arxiv.org/pdf/2103.14030
助手: web_fetch 抓取内容，提取关键信息
```

### 4. 论文翻译

```
用户: 把这篇论文翻译成中文
助手: 调用 baoyu-translate skill，支持精翻模式
```

### 5. 研究假设追踪

```bash
# 创建假设
node scripts/hypothesis-tracker.mjs create "Transformers 比 RNN 更快收敛" --tag NLP

# 更新假设状态
node scripts/hypothesis-tracker.mjs update <id> --status confirmed

# 查看所有假设
node scripts/hypothesis-tracker.mjs list
```

## 数据源说明

| 源 | 特点 | 适用领域 | 访问方式 |
|---|------|---------|---------|
| arXiv | 预印本，更新快 | CS/AI/数学/物理 | API（免费） |
| PubMed | 期刊论文，同行评审 | 医学/生物/药学 | NCBI API（免费） |
| Semantic Scholar | 引用分析强 | 全学科（英文为主） | API（免费） |

## 依赖

- **Node.js** ≥ 18
- **Python** ≥ 3.8 + `semanticscholar` 库
- **可选**: `baoyu-translate` skill（翻译功能）

## 常见问题

### 搜索返回空结果？
- 检查网络代理设置
- arXiv 需要代理访问（如在中国大陆）
- Semantic Scholar 有速率限制（建议 Python 客户端）

### 中文论文搜不到？
- 当前三个源主要覆盖英文文献
- 中文论文需通过知网/万方手动获取 PDF
- 获取 PDF 后可用本 skill 做阅读、翻译、摘要

### 如何添加新数据源？
在 `scholar-search.mjs` 中添加新函数，遵循统一格式：
```js
{
  title: "论文标题",
  authors: ["作者列表"],
  year: 2026,
  abstract: "摘要",
  doi: "DOI",
  url: "原文链接",
  source: "数据源名称",
  citations: 123
}
```

---
name: research-lab
description: |
  科研模式入口。当用户说"进入科研模式"、"开始做科研"、发论文链接、
  提到研究课题/假设/实验/文献综述时激活。提供假设驱动循环、
  PubMed文献检索、证据追踪、研究项目管理等科研能力。
---

# 🔬 Research Lab — 科研模式

## 触发词
"进入科研模式"、"开始做科研"、"research mode"、发论文链接(arxiv/doi)、
提到"假设"、"实验设计"、"文献综述"、"研究课题"

## 能力清单

### 1. 文献检索与阅读
- **PubMed 搜索**: `bash skills/research-lab/scripts/pubmed-search.mjs "关键词" [--max 10]`
- **论文阅读**: 微信/网页论文自动提取+摘要+关键点提炼
- **文献管理**: 录入飞书追踪表

### 2. 假设驱动循环（Hypothesis-Driven Loop）
```
Plan → Evidence → Review → Iterate
```
- **假设提出**: 结构化记录到 `research/projects/{name}/hypotheses.md`
- **证据收集**: 自动/手动收集支持/反驳证据
- **评估审查**: 定期回顾假设状态
- **迭代**: 根据证据调整假设

### 3. 研究项目管理
- 项目目录: `research/projects/{project-name}/`
- 每个项目包含:
  - `README.md` — 项目概述
  - `hypotheses.md` — 假设追踪
  - `evidence/` — 证据文件
  - `notes/` — 阅读笔记
  - `references.md` — 参考文献列表
  - `progress.md` — 进展日志

### 4. 知识整合
- **飞书文档**: 研究笔记/论文草稿
- **飞书表格**: 假设追踪表/文献管理表
- **Memory**: 长期研究记忆（自动更新 MEMORY.md）

## 使用方式

### 进入科研模式
用户说"进入科研模式"时:
1. 确认当前研究项目（已有则加载，没有则创建）
2. 展示项目状态（假设数、文献数、最近进展）
3. 列出可用操作

### 日常操作
- "搜一下 XXX 的最新论文" → PubMed 搜索
- "读一下这篇论文 [链接]" → 提取+摘要+录入
- "提出一个假设：XXX" → 结构化记录
- "整理一下目前的证据" → 汇总分析
- "项目进展怎么样" → 状态报告

### 退出科研模式
"退出科研模式"或"回到正常模式" → 保存状态，恢复正常

## 工具依赖
- PubMed E-utilities API（免费，无需key）
- arXiv API（免费，无需key，支持短语匹配）
- Semantic Scholar API（免费，无需key，含引用统计/TLDR）
- 微信文章读取（已有 wechat-article-reader）
- 飞书文档/表格 API（已有）

## 搜索脚本速查

### Node.js 脚本（代理支持好，推荐日常用）

| 脚本 | 覆盖领域 | 用法 |
|------|----------|------|
| `arxiv-search.mjs` | CS/AI/ML/数学/物理 | `node arxiv-search.mjs "关键词" --max 10 --sort date` |
| `pubmed-search.mjs` | 生物医学/生命科学 | `node pubmed-search.mjs "关键词" --max 10 --sort date` |
| `s2-search.mjs` | 综合学术（含引用数） | `node s2-search.mjs "关键词" --max 10 --sort citationCount` |
| `scholar-search.mjs` | **三源合一** | `node scholar-search.mjs "关键词" --sources all --max 5` |

### Python 工具（paperscraper + semanticscholar）

| 命令 | 说明 |
|------|------|
| `python3.11 scholar.py search "关键词" --source all --max 5` | 统一搜索 |
| `python3.11 scholar.py search "关键词" --source s2 --json` | 仅 Semantic Scholar（含引用/TLDR） |
| `python3.11 scholar.py search "关键词" --source pubmed` | 仅 PubMed |
| `python3.11 scholar.py download DOI_OR_ARXIV_ID -o ./papers/` | 下载 PDF |

通用参数: `--max N` 数量 | `--sort date|relevance|citationCount` | `--json` JSON输出
`scholar-search.mjs` 额外参数: `--sources all|arxiv|pubmed|s2`

### 已安装 Python 包
- `paperscraper` 0.3.6 — PubMed/arXiv/bioRxiv/medRxiv/chemRxiv 搜索 + PDF 下载
- `semanticscholar` 0.12.0 — Semantic Scholar API 客户端（引用图谱/推荐）

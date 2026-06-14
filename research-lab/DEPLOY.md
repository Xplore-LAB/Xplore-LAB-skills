# 📚 Scholar Pack — 学术研究能力一键部署指南

> 把学术搜索、论文阅读、引用分析、假设追踪复制到任何 OpenClaw 实例。

## 目录结构

```
~/.openclaw/workspace/skills/research-lab/
├── SKILL.md                    # 主文档
├── PACK.md                     # 能力总览
├── install.sh                  # 一键安装脚本
└── scripts/
    ├── arxiv-search.mjs        # arXiv 预印本搜索
    ├── pubmed-search.mjs       # PubMed 医学文献搜索
    ├── s2-search.mjs           # Semantic Scholar 引用分析
    ├── scholar-search.mjs      # 统一搜索（三源合并）
    ├── scholar.py              # Python 版搜索（含下载PDF）
    └── hypothesis-tracker.mjs  # 研究假设追踪器
```

## 快速部署（3 步）

### 1. 创建目录并安装依赖

```bash
mkdir -p ~/.openclaw/workspace/skills/research-lab/scripts
pip install semanticscholar  # Semantic Scholar Python 客户端
```

### 2. 复制脚本

将下方 6 个脚本文件分别保存到 `scripts/` 目录下。

### 3. 测试

```bash
cd ~/.openclaw/workspace/skills/research-lab/scripts
node scholar-search.mjs "transformer attention" --max 2
python3 scholar.py search "large language model" --max 2 --source s2
```

---

## 配置代理（可选）

如果服务器无法直接访问外网，在 `TOOLS.md` 中添加：

```
- 学术搜索代理: `socks5h://127.0.0.1:7890`（或你的代理地址）
- 环境变量: `SCHOLAR_PROXY`
```

所有脚本自动读取 `SCHOLAR_PROXY` 或 `HTTP_PROXY` 环境变量。

---

## 使用方法

### 统一搜索（推荐）

```bash
# 搜 arXiv + PubMed + Semantic Scholar
node scholar-search.mjs "deep learning" --sources all --max 5

# 只搜 Semantic Scholar（引用统计最强）
python3 scholar.py search "attention mechanism" --max 5 --source s2

# JSON 输出（给 LLM 处理）
node scholar-search.mjs "transformer" --sources all --max 5 --json
```

### 下载论文 PDF

```bash
# 通过 arXiv ID
python3 scholar.py download 2103.14030 -o ./papers/

# 通过 DOI
python3 scholar.py download 10.1109/ICCV48922.2021.00986 -o ./papers/
```

### 假设追踪

```bash
# 创建假设
node hypothesis-tracker.mjs add --project NLP --hypothesis "Transformers 比 RNN 更快收敛" --priority high

# 添加证据
node hypothesis-tracker.mjs evidence --project NLP --id H1 --type support --source "ICLR2024" --summary "实验证明收敛速度提升40%"

# 查看状态
node hypothesis-tracker.mjs list --project NLP
node hypothesis-tracker.mjs status --project NLP

# 审查结论
node hypothesis-tracker.mjs review --project NLP --id H1 --verdict "已确认，适用于序列长度>512"
```

---

## 数据源对比

| 源 | 覆盖领域 | 引用统计 | API Key | 特色 |
|---|---|---|---|---|
| arXiv | CS/AI/ML/数学/物理 | ❌ | 不需要 | 预印本，最新研究 |
| PubMed | 医学/生物/药学 | ❌ | 不需要 | 同行评审，可信度高 |
| Semantic Scholar | 全学科 | ✅ | 不需要 | 引用图谱、TLDR摘要 |

---

## 与其他工具配合

- **论文翻译** → `baoyu-translate` skill（中↔英精翻）
- **PDF阅读** → `read` tool 直接读取内容
- **综述撰写** → 基于搜索结果用 LLM 生成
- **飞书记录** → `feishu_doc` 写入研究笔记

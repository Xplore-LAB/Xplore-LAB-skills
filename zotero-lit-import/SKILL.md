---
name: zotero-lit-import
summary: "完整的大模型文献库管理skill：文献搜索、RIS生成、Zotero导入、日常维护"
description: >
  当用户需要搜索学术论文、导入 Zotero、或维护文献库时使用此 skill。
  完整覆盖：1. 文献搜索（arXiv/OpenReview/WebSearch）
  2. RIS 文件生成
  3. 通过 Zotero Web API 自动导入（含12个研究方向 + 8个公司分类）
  4. 日常维护（清理重复、重新分类、扩展新方向）
  5. 跨项目迁移（换 API Key 和 User ID 即可）
agent_created: true
---

# zotero-lit-import

将学术文献从搜索到导入 Zotero 的完整流程封装为可复用管道。跨项目迁移时只需修改 `scripts/zotero_import.py` 顶部的 `API_KEY` 和 `USER_ID`。

## 快速查询表

| 你想做什么 | 怎么做 | 时间 |
|-----------|-------|------|
| 读论文时看到一篇想收藏 | 直接告诉 WorkBuddy "把这篇加到 Zotero" | 1 分钟 |
| 批量搜索一个新方向 | 告诉 WorkBuddy 想看哪个方向，走搜索→RIS→导入一条龙 | 5 分钟 |
| 想按自己的方式重新分类 | 修改 `PAPER_COLLECTION_MAP` 的映射规则 | 2 分钟 |
| 发现有重复论文 | 运行 `zotero_cleanup.py` 一键清理 | 1 分钟 |
| 想自己手动加一篇 | 打开 RIS 文件按格式追加一条，运行 `scripts/zotero_import.py` | 2 分钟 |
| 跨项目迁移 | 复制 skill 到新项目，改 `API_KEY` 和 `USER_ID` | 1 分钟 |

## 使用前提

## 使用前提

- **Zotero API Key**：用户需先在 https://www.zotero.org/settings/keys 创建 API Key
- **权限要求**：API Key 必须勾选 "Allow library access"（含写权限 `write: true`）
- **Python 环境**：需要 Python 3.8+，无需额外安装库（使用标准库 `urllib`）

## 完整流程

### Step 1: 文献搜索

用 WebSearch 搜索关键词，找到目标论文列表。
每篇论文至少获取：标题、作者、年份、会议/期刊、arXiv 链接。

### Step 2: 生成 RIS 文件

在 workspace 根目录生成 `RIS` 格式文件。每条记录的格式：

```
TY  - JOUR
TI  - 论文标题
AU  - Last, First
PY  - 年份
UR  - https://arxiv.org/abs/xxxx.xxxxx
T2  - 会议/期刊名称
N1  - 简介注释
ER  - 
```

### Step 3: 导入 Zotero（自动创建目录）

使用 `scripts/zotero_import.py` 完成导入：

1. **配置 API Key**：在 `scripts/zotero_import.py` 顶部设置：
   ```python
   API_KEY = "用户的API Key"
   USER_ID = "用户的User ID"  # 可通过 GET https://api.zotero.org/keys/{key} 获取
   RIS_FILE = "RIS文件路径"
   ```

2. **运行导入**：
   ```bash
   python scripts/zotero_import.py
   ```

导入脚本会自动：
- 读取 RIS 文件中的论文列表（支持任意 RIS 文件）
- 连接到 Zotero Web API
- 根据 `PAPER_COLLECTION_MAP`（按标题关键词匹配）自动分类到对应目录
- **层级目录支持**：COLLECTION_HIERARCHY 定义目录的父子关系
- **主题分类**：覆盖 12 个研究方向（模型架构/训练技术/微调方法/推理部署/RAG/Agent/多模态等）
- **公司专区**：按 OpenAI / Google / Meta / DeepSeek / Anthropic 等公司分类
- 在 Zotero 中创建需要的目录
- 导入论文时直接分配到对应目录

### Step 4: 新增论文或更换 RIS 文件

使用前修改脚本顶部的 RIS_FILE 路径，指向目标 RIS 文件：
```python
RIS_FILE = "path/to/your_papers.ris"
```

脚本会自动：
1. 检查目录是否存在（不存在则创建）
2. 导入论文并分配目录
3. 跳过已存在的目录

在 Zotero 中刷新（View → Refresh），检查：
- 论文是否已出现在对应目录
- 各目录中的论文数量是否合理

## 常见问题

- **403 Forbidden**：API Key 没有写权限 → 重新生成 Key 并勾选写权限
- **导入后不在目录中**：检查 Zotero 中目标目录是否存在，或脚本日志中的错误信息
- **Windows 编码问题**：使用 `-X utf8` 参数运行：`python -X utf8 scripts/zotero_import.py`

## 日常维护指南

### 场景 1：读论文时发现一篇新论文想加入 Zotero

用 `generate_llm_ris.py` 的格式，在 RIS 文件中新增一条记录，然后运行导入脚本。

**快速添加（手动修改 RIS 文件）：**
```bash
# 编辑已有 RIS 文件，按格式追加一条记录：
# TY  - JOUR
# TI  - 论文标题
# AU  - Last, First
# PY  - 年份
# UR  - arXiv链接
# N1  - 备注
# ER  - 
python scripts/zotero_import.py
```

### 场景 2：批量搜索并导入一个新方向的论文

1. WorkBuddy 用 WebSearch 搜索目标方向的关键论文
2. 生成 RIS 文件
3. 更新 `scripts/zotero_import.py` 中的 `PAPER_COLLECTION_MAP`（添加新论文的标题→目录映射）
4. 修改 `RIS_FILE` 路径
5. 运行导入

### 场景 3：清理重复论文

如果导入后发现重复，运行清理脚本：
```bash
python zotero_cleanup.py
```
按标题匹配删除重复条目。

### 场景 4：调整论文的目录分配

- **修改映射**：编辑 `PAPER_COLLECTION_MAP`，调整论文标题关键词→目录的映射
- **新增目录**：编辑 `COLLECTION_HIERARCHY`，添加新的目录及其父目录
- **重新导入**：修改后重新运行导入脚本（已有目录不会重复创建）

### 场景 5：给已有论文添加公司标签

如果已导入的论文属于某家公司但还没分配到公司专区：
1. 在 `PAPER_COLLECTION_MAP` 中为该论文的关键词添加公司目录
2. 运行脚本重新导入（会跳过已存在的论文条目本身，但需要手动 PATCH）

## 脚本说明

`scripts/zotero_import.py`：
- 无外部依赖（仅使用 Python 标准库 `json`, `urllib`, `time`, `re`, `os`）
- 自动解析 RIS 文件，支持多作者、多目录
- 自动跳过已存在的目录
- 每次导入生成 `import_log.txt` 记录详细日志

## 目录层级维护

编辑脚本中的 `COLLECTION_HIERARCHY` 字典：
- `"目录名": None` → 顶层目录
- `"目录名": "父目录名"` → 子目录

编辑 `PAPER_COLLECTION_MAP` 字典：
- `"标题关键词": ["目录1", "目录2"]` → 匹配到该关键词的论文自动分配到对应目录

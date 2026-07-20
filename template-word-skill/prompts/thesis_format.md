# thesis_doc.py 学位论文模式决策指引

Agent 在「学位论文」模式下选择子命令、构造 JSON 的决策参考。

## 1. 格式来源怎么选

| 用户意图 | 选择 |
|---------|------|
| 没给学校模板，按通用规范写 | 不加参数，用内置通用学位论文档案 |
| 给了学校 .docx 模板，要求严格按学校格式 | `--ref 学校模板.docx`（现抽字体/字号/三线表/分节特征，缺失项回退通用） |
| 同一学校格式要反复用 | 先 `python tools/edit_doc.py extract --ref 学校模板.docx --profile 论文档案.json`，再用 `--profile 论文档案.json` |

优先级：`--profile` > `--ref` > 通用默认。

## 2. 子命令选择

| 场景 | 子命令 |
|------|--------|
| 从零写一篇论文 | `new`（一键骨架，含分节+编号+目录+图表索引） |
| 已有论文，缺封面 | `cover` |
| 已有论文，标题没自动编号 | `numbering` |
| 插入一张图 | `figure`（自动居中+图下题注"图1-1"） |
| 插入数据表 | `table`（三线表+表上题注"表1-1"） |
| 插入公式 | `equation`（居中+右编号"(1-1)"） |
| 页码乱了（前置该罗马、正文该阿拉伯） | `sections` |
| 补中英文摘要 | `abstract` |
| 列参考文献 | `references` |
| 要图录/表录 | `lof` / `lot` |

**重要**：编号、题注、目录、图表索引都是 Word 域，python-docx 只写域代码不计算值。**生成后必须在 Word 中 Ctrl+A → F9 更新**，否则显示占位。务必告知用户。

## 3. JSON Schema

### 论文.json（`new` 子命令）

```json
{
  "output": "论文.docx",
  "school": "XX大学",
  "title": "基于深度学习的XX研究",
  "author": "张三",
  "student_id": "2023XXXX",
  "supervisor": "李四 教授",
  "major": "计算机科学与技术",
  "date": "2026年6月",
  "zh_abstract": {
    "title": "基于深度学习的XX研究",
    "body": ["摘要第一段...", "摘要第二段..."],
    "keywords": ["深度学习", "XX", "YY"]
  },
  "en_abstract": {
    "title": "Research on XX Based on Deep Learning",
    "body": ["Para 1...", "Para 2..."],
    "keywords": ["Deep Learning", "XX", "YY"]
  },
  "chapters": [
    {
      "title": "绪论",
      "sections": [
        {"title": "研究背景", "paragraphs": ["背景内容..."]},
        {"title": "研究意义", "paragraphs": ["意义内容..."]}
      ]
    },
    {
      "title": "相关工作",
      "sections": [{"title": "国内研究现状", "paragraphs": ["..."]}]
    }
  ],
  "references": [
    {"type": "journal", "authors": "张三, 李四", "title": "XX方法研究",
     "source": "计算机学报", "year": "2024", "volume": "47", "issue": "3", "pages": "1-15"},
    {"type": "book", "authors": "王五", "title": "深度学习",
     "place": "北京", "publisher": "清华大学出版社", "year": "2023"},
    {"type": "conference", "authors": "Smith J", "title": "XX",
     "source": "Proc. of ICML", "year": "2023", "pages": "100-110"},
    {"type": "thesis", "authors": "赵六", "title": "XX研究",
     "source": "XX大学", "year": "2022", "degree": "博士"}
  ],
  "acknowledgement": "感谢导师..."
}
```

### table.json（`table` 子命令）

```json
{
  "headers": ["方法", "准确率", "F1"],
  "rows": [
    ["方法A", "95.2", "0.94"],
    ["方法B", "93.1", "0.92"]
  ]
}
```

### refs.json（`references` 子命令）

```json
[
  {"type": "journal", "authors": "张三", "title": "XX", "source": "计算机学报",
   "year": "2024", "volume": "47", "issue": "3", "pages": "1-15"},
  {"type": "book", "authors": "王五", "title": "深度学习",
   "place": "北京", "publisher": "清华出版社", "year": "2023"}
]
```

参考文献 `type` 与字段：
- `journal`：authors, title, source(刊名), year, volume, issue, pages → `作者. 题名[J]. 刊名, 年, 卷(期): 页码.`
- `book`：authors, title, place, publisher, year → `作者. 书名[M]. 出版地: 出版者, 年.`
- `conference`：authors, title, source(会议/论文集), year, pages → `作者. 题名[C]//会议. 年: 页码.`
- `thesis`：authors, title, source(学校), year, degree → `作者. 题名[D]. 学校, 年.`

## 4. 典型工作流

### 流程 A：从零写论文（最常用）

```bash
# 1. 构造 论文.json（章节大纲 + 参考文献）
# 2. 生成骨架（有学校模板则加 --ref）
python tools/thesis_doc.py new --spec 论文.json --output 论文.docx --ref 学校模板.docx
# 3. 提示用户：Word 打开 → Ctrl+A → F9 更新所有域
```

### 流程 B：已有论文，补图表

```bash
python tools/thesis_doc.py figure --input 论文.docx --output 论文.docx \
  --after "图1所示为" --image fig1.png --caption "系统架构"
python tools/thesis_doc.py table --input 论文.docx --output 论文.docx \
  --after "实验数据见" --data table.json --caption "性能对比"
python tools/thesis_doc.py lof --input 论文.docx --output 论文.docx
python tools/thesis_doc.py lot --input 论文.docx --output 论文.docx
# Word 中 F9 更新
```

### 流程 C：已有论文，修格式问题

```bash
# 标题没编号
python tools/thesis_doc.py numbering --input 论文.docx --output 论文.docx --ref 学校模板.docx
# 页码混乱
python tools/thesis_doc.py sections --input 论文.docx --output 论文.docx
# 参考文献格式不对
python tools/thesis_doc.py references --input 论文.docx --output 论文.docx --items refs.json
```

## 5. 限制与注意事项

- **域需 F9 更新**：编号、题注、目录、图表索引、交叉引用都是 Word 域，python-docx 不计算值。生成后必须在 Word 中 Ctrl+A → F9。这是 OOXML 固有机制，无法在生成侧绕过。
- **分节页码需 ≥3 节**：`sections` 子命令要求文档已有封面/前置/正文三节。`new` 已自动分节；对已有文档单独用 `sections` 若节数不足会提示，需先在 Word 中加分节符。
- **GB/T 7714 为简化版**：覆盖期刊[J]/书[M]/会议[C]/学位论文[D] 四类常见格式，不接文献管理软件（Zotero/EndNote）。如需复杂引用管理，建议用 Zotero 生成后再用本工具统一字体缩进。
- **公式为纯文本**：`equation` 插入的是文本公式，非 MathType/OMML 对象。复杂数学公式需在 Word 中用公式编辑器替换。
- **封面位置**：`cover` 子命令追加到文档末尾，需在 Word 中剪切到开头（`new` 已正确置顶）。

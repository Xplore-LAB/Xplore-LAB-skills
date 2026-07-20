# edit_doc.py 编辑保格式决策指引

Agent 在「编辑保格式」模式下选择子命令与格式来源的决策参考。

## 1. 格式来源怎么选

按用户意图判断：

| 用户意图 | 选择 |
|---------|------|
| 「按这套格式来」「保持现在的格式就行」（无指定标杆） | `--preset formal_report`（缺省，无需任何文件） |
| 「照着这份标杆文档的格式」「把它的格式套过去」并提供了 .docx | `--ref 标杆.docx`（现抽，一次性） |
| 同一标杆格式要反复用在多份文档 | 先 `extract --ref 标杆.docx --profile 档案.json`，后续都用 `--profile 档案.json` |
| 用户已有档案 JSON | 直接 `--profile 档案.json` |

优先级：`--profile` > `--ref` > `--preset`。

## 2. 编辑动作 → 子命令映射

| 用户动作 | 子命令 | 关键参数 |
|---------|--------|---------|
| 改某处文字、批量替换术语 | `replace` | `--find` `--replace`，含表格默认替换；仅正文加 `--body-only` |
| 在某章后补内容、新增章节/段落/表格 | `insert` | `--after`（锚点文本）`--blocks`（内容块 JSON） |
| 统一全文格式、套用标杆格式 | `apply` | `--ref`/`--profile`/`--preset`；不改页边距加 `--no-page`，不改表格加 `--no-tables` |
| 把某段提升/降级为标题 | `heading` | `--find` `--level`(1-4) |
| 改完刷新目录、补目录 | `toc` | `--refresh`（已有目录标记更新）或 `--ensure`（无则新建） |

## 3. blocks.json 结构（insert 子命令）

支持单对象或数组。每块 `type` 决定格式：

```json
[
  {"type": "heading", "level": 2, "text": "新增章节标题"},
  {"type": "body", "text": "正文段落，套用档案正文格式（字体/字号/行距/首行缩进）。"},
  {"type": "table", "headers": ["序号", "项目", "状态"], "rows": [["1", "A", "完成"]]},
  {"type": "code", "text": "npm install"},
  {"type": "caption", "text": "图1 系统架构示意图"}
]
```

- `heading`：`level` 1-4，套档案对应标题层级格式，并设置 `Heading N` 样式
- `body`：套档案正文格式
- `table`：`headers` 列标题数组，`rows` 二维数组；表头按档案表头格式（背景色高亮），单元格按档案单元格格式
- `code`：套档案代码块格式（等宽字体、灰底、缩进）
- `caption`：套档案图注格式（居中、小号、粗体）

## 4. 典型工作流

### 流程 A：套用标杆格式 + 术语替换

```bash
python tools/edit_doc.py apply --input 文档.docx --output 文档.docx --ref 标杆.docx
python tools/edit_doc.py replace --input 文档.docx --output 文档.docx --find "旧系统" --replace "原系统"
```

### 流程 B：补一节内容并刷新目录

```bash
python tools/edit_doc.py insert --input 文档.docx --output 文档.docx \
  --after "第三章" --blocks new_section.json --ref 标杆.docx
python tools/edit_doc.py toc --input 文档.docx --output 文档.docx --refresh
```

### 流程 C：把若干正文段提升为二级标题

```bash
python tools/edit_doc.py heading --input 文档.docx --output 文档.docx --find "性能需求" --level 2
python tools/edit_doc.py heading --input 文档.docx --output 文档.docx --find "安全需求" --level 2
python tools/edit_doc.py toc --input 文档.docx --output 文档.docx --refresh
```

## 5. 保格式行为说明（向用户解释时用）

- `replace`：优先在单个 run 内替换，完整保留段内格式变化（如句中某个粗体词）；仅当查找词跨越多个 run 时，回退为整段重建，套用首个匹配 run 的格式——此时段内格式变化会丢失，但文字与主体格式保留。
- `insert`：每个新块独立按档案格式化，不继承锚点段落的偶然格式。
- `apply`：只覆盖直接格式（字体/字号/颜色/段落格式/表格样式），不改动文字内容与样式名，标题层级保持不变。
- 所有子命令默认生成新文件；要原地覆盖让 `--output` 与 `--input` 相同。
- 目录刷新需在 Word 中按 Ctrl+A → F9 实际更新。

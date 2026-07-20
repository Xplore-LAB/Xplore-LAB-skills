---
name: template-word-skill
description: "四种模式：(1) 有 .docx 模板时，填充模板生成文档；(2) 无模板时，按预设格式规范从零创建 Word 文档；(3) 编辑已有文档时保持/统一格式（格式档案机制）；(4) 学位论文专用：多级编号、图表公式题注、三线表、分节页码、摘要、GB/T 7714 参考文献、图表索引、封面骨架。支持 23 种项目交付文档类型，内置 4 套格式预设。触发词：写 word、生成 docx、写项目计划书、出技术设计、运维手册、编辑 word、改 word、保持格式、套用格式、抽取格式、统一格式、重排标题、写论文、学位论文、毕业论文、论文格式、三线表、图题注、参考文献格式、分节页码、多级编号等。"
version: "4.0.0"
user-invocable: true
argument-hint: "[模板路径.docx] 或 [文档类型名称] 或 [编辑/论文子命令]"
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, Agent
---

# Word 文档生成与编辑（模板填充 + 从零创建 + 编辑保格式 + 学位论文）

基于 python-docx 的文档工具，支持四种模式：

1. **模板填充模式**：有 .docx 模板时，保留原格式，按占位符或 Markdown 内容生成新文档
2. **从零创建模式**：无模板时，按预设格式规范直接生成标准格式文档，无需模板文件
3. **编辑保格式模式（v3）**：对已有文档做改文字、补内容、批量替换、表格处理、重排标题/目录，编辑不破坏原格式，并可按「格式档案」统一全文格式
4. **学位论文模式（v4 新增）**：生成/编辑学位论文，覆盖多级标题编号、图表公式题注、三线表、分节页码、中英文摘要、GB/T 7714 参考文献、图表索引、封面与结构页

## 核心能力

| 能力 | 说明 |
|------|------|
| **模板填充** | 占位符替换、段落插入、图片嵌入，完整保留模板格式 |
| **从零创建** | 按预设格式规范（4 套预设）生成标准文档 |
| **文档注册表** | 23 种项目交付文档的默认章节结构，自动填充 |
| **格式预设** | 正式叙述 / 技术说明书 / 操作手册 / 清单表格 |
| **封面页** | 自动生成标准封面（项目名、文档名、版本、日期、编制人） |
| **目录页** | 自动生成 TOC 域（Word 中可更新） |
| **页眉页脚** | 项目名/文档名页眉 + 页码页脚 |
| **代码块** | 灰色背景、等宽字体、缩进（技术文档专用） |
| **带样式表格** | 表头高亮、自动宽度、字体规范 |
| **编辑保格式** | 改文字/补内容/批量替换/表格/重排标题时保持格式，按格式档案统一全文 |
| **学位论文** | 多级编号/图表公式题注/三线表/分节页码/摘要/参考文献/图表索引/封面骨架 |

## 触发条件

### 斜杠指令

`/template-word-skill`、`/template-word`、`/写word`、`/md转word`、`/生成文档`

### 自然语言触发词

**模板填充类：**
- 用模板写、按模板来、套模板、照着这个模板、不要改格式、保留格式

**从零创建类（v2 新增）：**
- 写个项目计划书、出一份技术设计说明书、生成运维手册
- 写 word、生成 docx、导出 word、写份文档
- md 转 word、markdown 转 word

**项目交付文档（直接用文档名触发）：**
- 项目计划书、需求说明书、现状分析报告、关键业务方案
- 技术设计说明书、数据库设计说明书、接口设计说明书
- 安装部署文档、运维手册、测试文档、培训手册
- 问题清单、密码清单、源代码交付清单

**编辑保格式类（v3 新增）：**
- 编辑 word、改 word、修改 docx、保持格式、不要破坏格式
- 套用格式、套用标杆文档格式、统一格式、把这份文档的格式套过去
- 抽取格式、提取格式档案、保存格式
- 重排标题、改标题层级、刷新目录、补目录

**学位论文类（v4 新增）：**
- 写论文、学位论文、毕业论文、硕士论文、博士论文、论文格式
- 三线表、图题注、表题注、公式编号、图表索引、图录、表录
- 参考文献格式、GB/T 7714、中英文摘要
- 分节页码、罗马数字页码、多级编号、标题自动编号
- 论文封面、独创性声明

## 使用方式

### 方式一：从零创建（v2 新增，推荐）

用户说出文档类型，Agent 从文档注册表查找默认章节，按预设格式生成。

```bash
# 快速创建：指定文档类型
python tools/create_doc.py --doc-type "项目计划书" --project-name "智能问数" --output 项目计划书.docx

# 列出所有支持的文档类型
python tools/create_doc.py --list-doc-types

# 列出所有格式预设
python tools/create_doc.py --list-presets
```

**工作流：**
```
用户：帮我写一份项目计划书，项目叫智能问数
Agent：
  1. 查注册表 → 找到默认章节（项目背景、目标、范围、组织、进度、资源、风险）
  2. 调用 create_doc.py 生成骨架文档
  3. 与用户确认各章节内容
  4. 用 fill_template.py 填充具体文字
```

### 方式二：模板填充

用户提供模板路径，Agent 调用 `tools/fill_template.py` 生成文档。

```bash
python tools/fill_template.py \
  --template 模板.docx \
  --config 填充配置.json \
  --output 输出.docx
```

### 方式三：Markdown 转 Word

用户提供模板和 Markdown 文件，调用 `tools/md_to_template_docx.py`。

```bash
python tools/md_to_template_docx.py \
  --template 模板.docx \
  --md 内容.md \
  --output 输出.docx
```

### 方式四：编程式调用

Agent 直接编写 Python 代码调用 `tools/docx_template.py` 库函数完成复杂任务。

### 方式五：编辑保格式（v3 新增）

对**已有 .docx** 做编辑，同时保持/统一格式。核心是**格式档案（Format Profile）**——一个可序列化的格式规则集，作为格式的单一事实来源。

**格式档案的两个来源：**
- **默认档案**：内置 `formal_report` 预设派生（可用 `--preset` 切换 tech_spec/manual/checklist），无需任何文件
- **参考文档档案**：从任意标杆 `.docx` 抽取实际格式（采样真实段落的直接格式，而非样式定义），存为 JSON 跨会话复用

```bash
# 1) 从标杆文档抽取格式档案（一次性，存盘复用）
python tools/edit_doc.py extract --ref 标杆.docx --profile 档案.json

# 2) 把标杆格式套到目标文档（统一全文格式）
python tools/edit_doc.py apply --input 目标.docx --output 输出.docx --ref 标杆.docx
#    或用已存档案：--profile 档案.json
#    或用内置预设：--preset formal_report（缺省即此）

# 3) 查找替换，保留原格式（含表格，--body-only 仅正文）
python tools/edit_doc.py replace --input 目标.docx --output 输出.docx \
  --find "旧词" --replace "新词"

# 4) 锚点后插入内容块（heading/body/table/code/caption），按档案格式化
python tools/edit_doc.py insert --input 目标.docx --output 输出.docx \
  --after "第一章" --blocks blocks.json --preset formal_report

# 5) 把某段重排为 N 级标题
python tools/edit_doc.py heading --input 目标.docx --output 输出.docx \
  --find "某段文本" --level 2

# 6) 刷新/补建目录（Word 打开后 Ctrl+A → F9 更新）
python tools/edit_doc.py toc --input 目标.docx --output 输出.docx --refresh
python tools/edit_doc.py toc --input 目标.docx --output 输出.docx --ensure
```

**blocks.json 结构**（insert 子命令，支持单对象或数组）：
```json
[
  {"type": "heading", "level": 2, "text": "新增章节"},
  {"type": "body", "text": "正文段落，自动套用档案正文格式。"},
  {"type": "table", "headers": ["序号", "项目", "状态"], "rows": [["1", "A", "完成"]]},
  {"type": "code", "text": "npm install"},
  {"type": "caption", "text": "图1 示意图"}
]
```

**工作流：**
```
用户：帮我把这份文档的格式统一成标杆.docx 那样，再把"旧系统"全部替换成"原系统"
Agent：
  1. extract --ref 标杆.docx --profile 档案.json        # 抽格式（或直接 --ref 现抽）
  2. apply   --input 文档.docx --output 文档.docx --profile 档案.json   # 统一格式
  3. replace --input 文档.docx --output 文档.docx --find "旧系统" --replace "原系统"  # 保格式替换
```

**编辑保格式的保证：**
- `replace`：优先在单个 run 内替换以保留段内格式变化；跨 run 匹配回退为整段重建并套用首 run 格式
- `insert`：每个新块按档案格式化，与原文档风格一致
- `apply`：仅覆盖直接格式，不改动文字内容与样式名
- 所有编辑都生成新文件，不修改原文件（除非 input=output 覆盖）

### 方式六：学位论文（v4 新增）

生成/编辑学位论文，覆盖论文中可能遇到的各种格式问题。**通用默认档案 + 学校模板覆盖**：内置通用学位论文格式（接近 GB/T 7713.1），用 `--ref 学校模板.docx` 可抽取学校真实格式覆盖默认。

**通用学位论文格式（默认）：**
| 项 | 规格 |
|----|------|
| 正文 | 宋体小四(12pt)，1.5 倍行距，首行缩进 2 字符 |
| 一级标题 | 黑体三号(16pt)居中 |
| 二级标题 | 黑体四号(14pt) |
| 三级标题 | 黑体小四(12pt) |
| 图题注 | 图下方，"图1-1 题名"，宋体五号居中 |
| 表题注 | 表上方，"表1-1 题名"，宋体五号居中 |
| 三线表 | 上下粗线 + 表头下细线，无竖线无内横线 |
| 公式 | 居中，右编号"(1-1)" |
| 参考文献 | 宋体五号，悬挂缩进，[1] 自动编号，GB/T 7714 |
| 页码 | 封面无页码 / 前置(摘要目录)罗马数字 / 正文阿拉伯从1重启 |

**核心命令：**
```bash
# 一键生成完整论文骨架（封面+声明+摘要+目录+图表索引+正文+参考文献+致谢，含分节与编号）
python tools/thesis_doc.py new --spec 论文.json --output 论文.docx
# 用学校模板覆盖默认格式：
python tools/thesis_doc.py new --spec 论文.json --output 论文.docx --ref 学校模板.docx

# 给已有文档加多级标题编号（1 / 1.1 / 1.1.1）
python tools/thesis_doc.py numbering --input 论文.docx --output 论文.docx

# 插入图+题注（图下"图1-1 ..."，居中五号）
python tools/thesis_doc.py figure --input 论文.docx --output 论文.docx \
  --after "实验结果" --image fig1.png --caption "各方法准确率对比"

# 插入三线表+题注（表上"表1-1 ..."）
python tools/thesis_doc.py table --input 论文.docx --output 论文.docx \
  --after "实验结果" --data table.json --caption "各方法准确率对比"

# 插入公式+右编号"(1-1)"
python tools/thesis_doc.py equation --input 论文.docx --output 论文.docx \
  --after "推导如下" --text "E=mc^2"

# 配置分节页码（封面无/前置罗马/正文阿拉伯从1）
python tools/thesis_doc.py sections --input 论文.docx --output 论文.docx

# 插入中英文摘要
python tools/thesis_doc.py abstract --input 论文.docx --output 论文.docx \
  --zh-body "..." --zh-keywords "关键词1；关键词2" \
  --en-body "..." --en-keywords "kw1; kw2"

# 插入 GB/T 7714 参考文献（items.json 见 prompts/thesis_format.md）
python tools/thesis_doc.py references --input 论文.docx --output 论文.docx --items refs.json

# 生成图/表索引
python tools/thesis_doc.py lof --input 论文.docx --output 论文.docx
python tools/thesis_doc.py lot --input 论文.docx --output 论文.docx
```

**关键限制（OOXML 固有）：** 多级编号、题注序号、目录、图表索引均以**域代码**形式写入，python-docx 不计算实际值。**必须在 Word 中打开后按 Ctrl+A → F9 更新**，编号才会显示。这与 v3 的 TOC 行为一致。

**典型工作流：**
```
用户：帮我写一篇硕士论文骨架，学校是XX大学，题目是《基于深度学习的XX研究》
Agent：
  1. 构造 论文.json（学校/题目/作者/导师/章节/参考文献，schema 见 prompts/thesis_format.md）
  2. thesis_doc.py new --spec 论文.json --output 论文.docx
  3. （若有学校模板）加 --ref 学校模板.docx 覆盖默认格式
  4. 提示用户在 Word 中 F9 更新所有域
```

## 格式预设详情

### A - 正式叙述文档（formal_report）

**覆盖文档：** 项目计划书、需求说明书、现状分析报告、关键业务方案、流程文档、测试文档

| 样式 | 字体 | 字号 | 特殊 |
|------|------|------|------|
| 标题1 | 黑体 | 16pt | 粗体 |
| 标题2 | 黑体 | 14pt | 粗体 |
| 标题3 | 黑体 | 12pt | 粗体 |
| 正文 | 宋体 | 12pt | 首行缩进2字符，行距28pt |
| 表头 | 黑体 | 10.5pt | 粗体，背景色#D5E8F0 |
| 表格内容 | 宋体 | 10.5pt | 行距18pt |
| 图注 | 宋体 | 9pt | 居中，粗体 |
| 代码块 | Consolas | 9pt | 灰色背景#F2F2F2 |

### B - 技术说明书（tech_spec）

**覆盖文档：** 技术设计说明书、数据库设计说明书、接口设计说明书、二次开发文档

在模板 A 基础上：
- 表格字号缩小到 9pt（适应密集字段表）
- 代码块字号 9pt，行距 16pt

### C - 操作手册（manual）

**覆盖文档：** 安装部署、运维手册、启停手册、备份手册、权限手册、FAQ、培训手册、编译说明

| 样式 | 字体 | 字号 | 特殊 |
|------|------|------|------|
| 正文 | 宋体 | 12pt | 首行不缩进，行距28pt |
| 代码块 | Consolas | 10pt | 灰色背景 |
| 注意事项 | 楷体 | 11pt | 灰色#666666 |

### D - 清单/表格（checklist）

**覆盖文档：** 数据收集资料、问题清单、密码清单、源代码交付清单

| 样式 | 字体 | 字号 | 特殊 |
|------|------|------|------|
| 标题 | 黑体 | 18pt | 粗体，居中 |
| 正文 | 宋体 | 10.5pt | 行距22pt，不缩进 |
| 页边距 | 左右2cm | - | 表格宽度最大化 |

## 文档注册表（23 种文档）

| 文档类型 | 预设 | 默认章节 |
|---------|------|---------|
| 项目计划书 | 正式叙述 | 项目背景 / 目标 / 范围 / 组织 / 进度 / 资源 / 风险 |
| 需求说明书 | 正式叙述 | 项目概述 / 功能需求 / 非功能需求 / 约束 / 验收标准 |
| 现状分析报告 | 正式叙述 | 分析背景 / 现状概述 / 问题分析 / 差距分析 / 改进建议 |
| 关键业务方案 | 正式叙述 | 业务场景 / 方案设计 / 方案对比 / 结论 |
| 流程文档 | 正式叙述 | 流程概述 / 角色职责 / 流程步骤 / 异常处理 / 流程图 |
| 测试文档 | 正式叙述 | 测试概述 / 计划 / 用例 / 执行 / 缺陷 / 报告 |
| 技术设计说明书 | 技术说明 | 系统概述 / 架构 / 模块设计 / 接口 / 数据流 / 部署 |
| 数据库设计说明书 | 技术说明 | 概述 / ER模型 / 表结构 / 索引 / 数据字典 / SQL脚本 |
| 接口设计说明书 | 技术说明 | 接口概述 / 接口列表 / 协议 / 数据格式 / 错误码 / 安全 |
| 二次开发文档 | 技术说明 | 开发环境 / 架构 / 接口 / 示例 / 部署 / 常见问题 |
| 安装部署文档 | 操作手册 | 环境要求 / 安装步骤 / 配置 / 验证 / 回退 |
| 日常运维手册 | 操作手册 | 运维概述 / 日常巡检 / 监控告警 / 日志管理 / 应急处理 |
| 服务器启停手册 | 操作手册 | 启动前检查 / 启动顺序 / 停止顺序 / 异常处理 |
| 数据备份操作手册 | 操作手册 | 备份策略 / 备份操作 / 数据恢复 / 恢复验证 / 注意事项 |
| 权限配置管理手册 | 操作手册 | 角色定义 / 权限矩阵 / 配置步骤 / 审计日志 |
| 常见问题及处理手册 | 操作手册 | 问题分类 / 排查流程 / 问题与解答 / 联系支持 |
| 用户培训资料及操作手册 | 操作手册 | 系统介绍 / 功能模块 / 操作流程 / 常见问题 / 练习题 |
| 编译和打包的说明 | 操作手册 | 环境要求 / 依赖说明 / 编译命令 / 打包流程 / 常见问题 |
| 数据收集资料 | 清单表格 | 数据说明 / 数据清单 |
| 项目问题清单 | 清单表格 | 问题清单 |
| 管理员账号密码清单 | 清单表格 | 账号清单 |
| 源代码交付清单 | 清单表格 | 交付清单 |

## 工具脚本

| 脚本 | 作用 |
|------|------|
| **`tools/docx_template.py`** | 核心库：格式复制、模板填充、从零创建、封面/目录/页眉页脚/表格/代码块、格式档案与编辑保格式（v3） |
| **`tools/create_doc.py`** | 从零创建主脚本：按 JSON 规范或文档类型生成标准文档 |
| **`tools/fill_template.py`** | 模板填充脚本：读取 JSON 配置，执行占位符替换/插入/嵌入 |
| **`tools/md_to_template_docx.py`** | Markdown → 模板 Word 转换 |
| **`tools/edit_doc.py`** | 编辑保格式主脚本（v3）：extract/apply/replace/insert/heading/toc 六个子命令 |
| **`tools/thesis_docx.py`** | 学位论文核心库（v4）：档案/封面/编号/题注/三线表/分节页码/摘要/参考文献/图表索引/骨架 |
| **`tools/thesis_doc.py`** | 学位论文主脚本（v4）：new/cover/numbering/figure/table/equation/sections/abstract/references/lof/lot |

## 依赖

```
python-docx>=0.8.11
```

安装：`pip install python-docx`

## 注意事项

- **不修改原文件**：所有模式始终生成新文件（除非显式 input=output 覆盖）
- **格式复制优先**：新插入的段落从模板中最近的同类型段落复制格式
- **中文支持**：通过 `w:eastAsia` 属性确保中文字体正确设置
- **代码块仅技术文档**：正式叙述和清单文档不默认使用代码块样式
- **目录需 Word 更新**：生成的 TOC 域在 Word 中打开后按 Ctrl+A → F9 更新
- **编辑保格式**：`apply` 仅覆盖直接格式不改样式名；`replace` 跨 run 匹配会坍缩为单 run（损失段内格式变化，文字与首 run 格式保留）
- **格式档案优先级**：`--profile` > `--ref` > `--preset`（缺省 formal_report）
- **学位论文域需 F9**：编号、题注、目录、图表索引写入域代码，Word 打开后 Ctrl+A → F9 更新才显示编号
- **学位论文分节**：`sections` 需文档已有 ≥3 节；`new` 子命令已自动分节，单独对已有文档用 `sections` 时需先用分节符分隔封面/前置/正文

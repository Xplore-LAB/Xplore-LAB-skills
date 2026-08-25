---
name: skill-publisher
description: 将本地个人 skill 一键发布到 GitHub 仓库。处理版本 bump、README 同步、版权声明、文件过滤、质量检查，全流程自动化。
metadata:
  version: "2.1.0"
---

# skill-publisher

一键将本地 skill 发布到 `Xplore-LAB/Xplore-LAB-skills`。覆盖从审计到验证的完整链路。

## 触发方式

以下任意说法均可触发，不需要记命令：

- "上传 skill" / "发布 skill" / "push 到 GitHub"
- "把这个 skill 推上去" / "传到仓库"
- "/skill-publisher" （显式调用）
- "/skill-publisher <skill名>" （指定单个）
- "/skill-publisher --all" （全部个人 skill）

**触发后自动走完整流程，不额外问"要不要检查 README""要不要 bump 版本"——这些是必做的。**

---

## 一、全流程概览

```
触发
  │
  ▼
审计 ──→ 列出本地所有 skill，标记 个人/外部/不确定
  │
  ▼
确认 ──→ 用户选择要上传的目标
  │
  ▼
对比 ──→ 检查远程已有/新增，获取已有文件 SHA
  │
  ▼
质量门 ──→ 逐项检查，不通过则自动修复或阻止
  │
  ▼
版本 ──→ 有变更但版本号未变？自动 bump + 更新 CHANGELOG
  │
  ▼
版权 ──→ 确保 LICENSE 存在 + SKILL.md 头部有版权声明
  │
  ▼
文件过滤 ──→ 按 allowlist/blocklist 决定推送哪些文件
  │
  ▼
推送 ──→ 逐个文件走 gh api，一个 skill 一个 commit
  │
  ▼
验证 ──→ 拉取远程内容逐项确认
  │
  ▼
本地备份 ──→ 同步到 $SKILL_BACKUP_DIR/<skill-name>/（仅保留 GitHub 上已有的）
  │
  ▼
报告 ──→ 输出结构化结果摘要
```

---

## 二、触发规则

### 二-A、自动识别目标

用户消息中出现以下模式时，自动提取目标 skill：

| 用户说 | 推断目标 |
|--------|---------|
| "把 X 上传" / "上传 X" / "发布 X" | 单个 skill：X |
| "把这些上传" / "全部上传" | 全部个人 skill |
| "/skill-publisher X" | 单个 skill：X |
| "/skill-publisher --all" | 全部个人 skill |
| "哪些可以上传" / "还有什么没传" | 仅审计，不上传 |

### 二-B、目标模糊时的处理

如果用户说"上传 skill"但没指定哪个，列出全部个人 skill 让用户选，同时标注：
- ✅ 远程已有（可更新）
- 🆕 远程没有（新建）
- ⚠️ 远程有但质量有问题（需先修）

---

## 三、来源判断规则

### 个人创建（可上传）

满足以下 **至少 3 条**：

1. `name:` 字段无命名空间前缀（如 `plugin:`）
2. 领域极其具体（校园地图、专利披露、Zotero 等）
3. 用户记忆中有该项目记录
4. 用户明确说是自己写的
5. SKILL.md 内容有中文（国内用户个人创建的特征）
6. 无外部 `author:` 字段

### 外部引入（禁止上传）

满足以下 **任意 1 条**：

1. `author:` 字段指向他人或组织
2. 名称带已知品牌/作者前缀（`baoyu-`、`deermiya-` 等）
3. 来自 Claude Code 内置 skill 列表
4. 是知名社区 skill（`humanizer`、`karpathy-guidelines` 等）
5. 用户记忆或 git 历史中有"从 XX 引入"的记录

### 不确定时

列出证据原文，问用户："这个 skill 是你自己写的还是从别处引入的？"

---

## 四、质量门（上传前必检）

以下检查**全部通过**才允许上传。不通过则自动修复，无法修复则阻止并说明原因。

### 四-A、结构完整性

| 检查项 | 要求 | 不通过时 |
|--------|------|---------|
| SKILL.md 存在 | 必须 | 🚫 阻止 |
| YAML frontmatter | 必须有 `name` / `description` / `version` | 🔧 自动补全 |
| `version` 格式 | 必须是 `x.y.z` 语义化版本 | 🚫 阻止，让用户指定 |
| README.md | 强烈建议（多文件 skill 必须有） | ⚠️ 提醒，不阻止 |

### 四-B、README 时效性

这是最容易出问题的地方——README 写的是 v1.0 的功能描述，但 SKILL.md 已经 v2.x。

**检查方法**：
1. 提取 README 中描述的核心功能列表
2. 提取 SKILL.md 中的核心功能列表
3. 对比，如果 README 描述的功能在 SKILL.md 中已经不存在或完全改变 → README 过时

**不通过时**：
- 🔧 如果差异小 → 自动更新 README 中的版本号和关键描述
- ⚠️ 如果差异大 → 提醒用户 README 需要重写，询问是否现在重写

### 四-C、CHANGELOG 同步

| 检查项 | 要求 | 不通过时 |
|--------|------|---------|
| CHANGELOG 版本号 | 最新条目版本号 ≥ SKILL.md 版本号 | 🔧 自动补全缺失的版本条目 |
| CHANGELOG 日期 | 最新条目日期为今天 | 🔧 自动更新 |

---

## 五、版本管理

### 五-A、何时需要 bump

对比本地和远程 SKILL.md，判断变更量级：

| 变更类型 | bump | 示例 |
|---------|------|------|
| 错字修正、格式调整 | PATCH（x.y.Z） | 2.1.0 → 2.1.1 |
| 新增功能、新增章节 | MINOR（x.Y.0） | 2.1.0 → 2.2.0 |
| 架构重写、不兼容变更 | MAJOR（X.0.0） | 2.1.0 → 3.0.0 |

### 五-B、自动 bump 流程

1. 计算差异量级 → 确定 bump 类型
2. 更新 SKILL.md frontmatter 中的 `version`
3. 在 CHANGELOG.md 顶部插入新版本条目（含日期、变更摘要）
4. 如果 README 中有版本号引用 → 同步更新

**用户确认**：bump 前告诉用户"检测到 X 变更，建议 bump 到 Y.Z.W，是否继续？"

### 五-C、禁止行为

- ❌ 文件内容变了但版本号不变就覆盖远程
- ❌ 跳版本（1.0 → 3.0 无理由）
- ❌ bump 了版本但 CHANGELOG 不更新

---

## 六、版权与许可证

### 六-A、LICENSE 文件

每个 skill 目录下必须有 `LICENSE` 文件。

**检查流程**：
1. 检查 skill 目录中是否已有 LICENSE 文件
2. 如果没有 → 自动生成 MIT License，copyright 年份取当前年份，版权人取 `Xplore-LAB`
3. 如果已有 → 检查年份是否包含当前年份，没有则追加

**LICENSE 模板**：
```
MIT License

Copyright (c) <year> Xplore-LAB

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
...
```

### 六-B、SKILL.md 版权声明

SKILL.md frontmatter 中建议包含：

```yaml
metadata:
  version: "2.1.0"
  license: MIT
  copyright: "2026 Xplore-LAB"
```

如果缺少 `license` 字段 → 自动补 `MIT`。
如果缺少 `copyright` 字段 → 自动补当前年份 + `Xplore-LAB`。

---

## 七、文件过滤规则

### 七-A、允许上传的类型（allowlist）

```
SKILL.md          # 核心
README.md         # 门面
CHANGELOG.md      # 记录
LICENSE           # 版权
METHODOLOGY.md    # 方法论
PARADIGM.md       # 范式
QUICKSTART.md     # 快速开始
*.json            # 配置文件（mermaid-config.json 等）
*.sh              # 安装脚本（setup.sh 等）
references/**.md  # 参考文档
```

### 七-B、禁止上传的类型（blocklist）

```
.git/              # Git 元数据
.gitignore         # 忽略规则（仓库级统一管理）
node_modules/      # 依赖
*.png              # 二进制图片（太大，不适合 git）
*.jpg              # 同上
*.jpeg             # 同上
*.vsdx             # Visio 源文件（通常很大）
*.pptx             # PPT 源文件
*.pdf              # PDF
__pycache__/       # Python 缓存
*.pyc              # Python 编译文件
.DS_Store          # macOS 元数据
Thumbs.db          # Windows 元数据
```

### 七-C、examples/ 处理

`examples/` 下的 `.mmd` / `.md` 文件可以上传。
`examples/` 下的 `.png` / `.jpg` 文件 **禁止上传**（二进制大文件）。

上传前检查 examples/ 目录，如果只有图片没有 `.mmd` 源文件 → 提醒用户"图片不会上传，是否需要补充 .mmd 源文件？"

---

## 八、推送执行

### 八-A、传输方式

永远使用 `gh api`，不使用 `git clone/push`。原因：系统代理可能阻断 HTTPS git 连接，但 `gh` CLI 走独立认证通道。

### 八-B、推送顺序

一个 skill 内的文件按此顺序推送（一个 skill 一个 commit，包含该 skill 的所有文件变更）：

```
1. LICENSE         （许可证）
2. SKILL.md        （核心定义）
3. README.md       （文档门面）
4. CHANGELOG.md    （更新记录）
5. QUICKSTART.md   （快速开始）
6. METHODOLOGY.md  （方法论）
7. PARADIGM.md     （范式文档）
8. mermaid-config.json  （配置）
9. setup.sh        （脚本）
10. references/*.md    （参考文件）
11. examples/*.mmd     （示例源码）
12. examples/*.md      （示例说明）
```

### 八-C、提交信息规范

遵循 Conventional Commits：

```
<type>(<scope>): <简短描述>

type:
  feat     — 新 skill 首次上传
  chore    — 版本 bump
  docs     — 文档更新（README、CHANGELOG、METHODOLOGY 等）
  fix      — 修复 SKILL.md 或 README 中的错误内容
  style    — 格式调整（不影响功能）
  refactor — 重写（不改变对外接口）

scope: skill 名称

示例:
  feat(campus-map): add campus map annotation skill
  chore(beautify-flowchart): bump to 2.2.0
  docs(beautify-flowchart): rewrite README for v2.x
  fix(skill-publisher): correct file filter blocklist
```

### 八-D、编码处理

所有中文文件走 UTF-8，base64 编码后再传：

```bash
python -c "
import base64
with open(r'<filepath>', 'rb') as f:
    print(base64.b64encode(f.read()).decode())
" > /tmp/upload_b64.txt
```

---

## 九、验证

推送后逐个文件验证：

```bash
gh api -H "Accept: application/vnd.github.raw+json" \
  repos/Xplore-LAB/Xplore-LAB-skills/contents/<skill>/<file> | head -20
```

验证清单：
- [ ] 文件可正常拉取
- [ ] 内容无截断（对比本地行数）
- [ ] frontmatter 版本号正确
- [ ] 中文无乱码
- [ ] LICENSE 年份正确

---

## 十、本地备份

### 十-A、备份规则

备份目录由环境变量 `SKILL_BACKUP_DIR` 指定（示例：`export SKILL_BACKUP_DIR=~/backups/skills`），未设置时先向用户确认备份位置，禁止使用硬编码路径。

`$SKILL_BACKUP_DIR/` 是 GitHub 仓库的本地镜像——只保留已在 GitHub 上的 skill，不上传 GitHub 的 skill 不在这里出现。

推送验证通过后，自动同步：

```bash
SOURCE="<本地 skill 源目录>/<skill-name>"
TARGET="$SKILL_BACKUP_DIR/<skill-name>"

rm -rf "$TARGET"
cp -r "$SOURCE" "$TARGET"
```

### 十-B、清理机制

每次备份后，扫描 `$SKILL_BACKUP_DIR/`，删除不在 GitHub 仓库中的目录：

```bash
# 获取 GitHub 上的 skill 列表
gh api repos/Xplore-LAB/Xplore-LAB-skills/contents/ --jq '.[].name'

# 删除本地有但 GitHub 没有的
```

这确保了 `$SKILL_BACKUP_DIR/` 和 GitHub 仓库严格一致——它是"已上传到 GitHub 的本地镜像"，不是"所有本地 skill 的副本"。

### 十-C、禁止行为

- ❌ 不把未上传的 skill 放进 $SKILL_BACKUP_DIR
- ❌ 不在 $SKILL_BACKUP_DIR 里直接改代码（应改 ~/.claude/skills/ 里的，上传后再同步过来）

---

## 十一、输出报告

完成后输出结构化报告，不遗漏任何状态：

```
╔══════════════════════════════════════════════╗
║           Skill Publisher · 发布报告          ║
╠══════════════════════════════════════════════╣
║                                              ║
║  ✅ skill-a v1.0.0 (新建)                    ║
║     commit: abc1234                          ║
║     文件: SKILL.md, README.md, LICENSE       ║
║                                              ║
║  ✅ skill-b v1.2.0→v1.3.0 (更新)             ║
║     commit: def5678                          ║
║     文件: SKILL.md, CHANGELOG.md, README.md  ║
║     bump: MINOR (新增功能)                    ║
║                                              ║
║  ⏭️ skill-c — 跳过（外部引入: baoyu-）       ║
║  ⏭️ skill-d — 跳过（Claude Code 内置）       ║
║  🚫 skill-e — 阻止（无 SKILL.md）            ║
║                                              ║
║  成功: 2  跳过: 2  阻止: 1                    ║
╚══════════════════════════════════════════════╝
```

---

## 十二、禁止事项

### 来源
- ❌ 外部引入的 skill 一律不传
- ❌ Claude Code 内置 skill 不传
- ❌ 不确定来源的不传（先问用户）

### 质量
- ❌ README 严重过时不传
- ❌ 无 frontmatter 的 SKILL.md 不传
- ❌ 无 LICENSE 文件不传

### 版本
- ❌ 内容变了版本号不变就覆盖
- ❌ bump 版本不更新 CHANGELOG
- ❌ 跳版本号无理由

### 文件
- ❌ 上传 .png/.jpg/.vsdx/.pptx 等二进制大文件
- ❌ 上传 .git 目录
- ❌ 上传 examples/ 下的图片（没有 .mmd 源文件的图片）

### 操作
- ❌ 用 git clone/push（代理阻断风险）
- ❌ 多个 skill 混在一个 commit
- ❌ 不验证就声称成功

---
name: skill-publisher
description: 将本地 Claude Code skill 发布到 GitHub 仓库。只上传自己创建的 skill，不上传从市场/社区引入的。
metadata:
  version: "1.0.0"
---

# skill-publisher

将本地 skill 发布（上传/更新）到 GitHub 仓库 `Xplore-LAB/Xplore-LAB-skills`。

## 核心原则

**只上传自己创建的 skill。** 从市场、社区、他人处引入的 skill 不在此列。

如果用户没有指定上传哪些，先列出本地所有 skill，标注哪些是个人的、哪些是外部引入的，让用户选择。

## 一、判断标准：个人 vs 外部引入

### 个人创建的信号

- 领域极其具体（如某个学校的地图标注、专利披露书、Zotero 文献管理）
- 用户记忆中有该项目的记录
- 用户说是自己写的
- `name:` 字段无命名空间前缀（不带 `plugin:` 等前缀）

### 外部引入的信号

- 有 `author:` 字段指向他人或组织
- 名称带品牌前缀（如 `baoyu-`）
- 版本号是非语义化格式（如 `1.58.0`）
- 是知名社区 skill（如 `humanizer`）
- 来自 Claude Code 内置或市场

**不确定时**：列出证据，让用户判断。

## 二、强制执行流程

### 第 1 步：审计本地

列出 `~/.claude/skills/` 下所有 skill，获取每个的：

1. 名称
2. 版本号（有/无）
3. SKILL.md 行数
4. 文件数量
5. 是否有 README
6. 个人/外部 判断 + 依据

### 第 2 步：对比远程

对每个要上传的 skill，检查远程仓库是否已有：

```bash
gh api repos/Xplore-LAB/Xplore-LAB-skills/contents/<skill-name> --jq '.[].name' 2>&1
```

- 远程已有 → 更新模式（需要文件 SHA）
- 远程没有 → 新建模式

### 第 3 步：检查质量（上传前）

对每个要上传的 skill，检查：

- [ ] 有 SKILL.md（必须有）
- [ ] SKILL.md 有 YAML frontmatter（name / description / version）
- [ ] 有 README.md（建议有，没有则提醒）
- [ ] README 内容是否与 SKILL.md 实际功能对齐（不是过时的 v1.0 描述）
- [ ] 有 CHANGELOG.md（建议有）

如果质量不达标，先修再传。不要上传过时的 README 和缺失版本号的 skill。

### 第 4 步：处理版本号

如果远程已有同一 skill：
- 检查本地和远程的版本号差异
- 如果本地有改动但版本号未变 → 提醒用户 bump 版本
- 自动更新 CHANGELOG.md 中的版本条目
- 自动更新 SKILL.md frontmatter 中的 version

版本号格式：`major.minor.patch`（语义化版本）

### 第 5 步：推送

使用 `gh api` 而非 `git push`（因为代理可能阻断 HTTPS）：

**新建文件：**
```bash
python -c "import base64; ..." > /tmp/content_b64.txt
CONTENT=$(cat /tmp/content_b64.txt)
gh api --method PUT \
  repos/Xplore-LAB/Xplore-LAB-skills/contents/<skill-name>/<filename> \
  -f message="<commit message>" \
  -f content="$CONTENT"
```

**更新已有文件：**
```bash
# 先获取 SHA
gh api repos/Xplore-LAB/Xplore-LAB-skills/contents/<skill-name>/<filename> --jq '.sha'

# 再更新（必须传 sha）
gh api --method PUT \
  repos/Xplore-LAB/Xplore-LAB-skills/contents/<skill-name>/<filename> \
  -f message="<commit message>" \
  -f content="$CONTENT" \
  -f sha="<sha>"
```

### 第 6 步：验证

推送后验证远程文件：

```bash
gh api -H "Accept: application/vnd.github.raw+json" \
  repos/Xplore-LAB/Xplore-LAB-skills/contents/<skill-name>/SKILL.md | head -10
```

确认：
- [ ] 文件内容正确
- [ ] 版本号已更新
- [ ] 提交信息合理

## 三、推送策略

### 单文件 skill

推送 SKILL.md 即可。如果 skill 简单（<200 行），不需要 README。

### 多文件 skill

按顺序推送：

1. SKILL.md（核心）
2. README.md（门面）
3. CHANGELOG.md（记录）
4. references/ 下的文件（如有）
5. examples/ 下的文件（如有）
6. 其他辅助文件

### 提交信息规范

```
<type>: <简短描述>

类型：
- feat: 新 skill 首次上传
- chore: bump version to x.y.z
- docs: 文档更新
- fix: 修复内容
```

示例：
- `feat: add campus-map skill`
- `chore: bump beautify-flowchart to 2.2.0`
- `docs: rewrite README to reflect v2.x methodology`

## 四、批量上传注意事项

多个 skill 一起上传时：

1. 每个 skill 独立提交（一个 skill 一个 commit）
2. 不要把所有 skill 混在一个 commit 里
3. 先上传基础 skill，再上传依赖它的 skill
4. 每个 skill 推送后验证，再推送下一个

## 五、禁止事项

- ❌ 不上传外部引入的 skill（humanizer、baoyu-*、data-wizard 等）
- ❌ 不上传 Claude Code 内置 skill
- ❌ README 过时不更新就直接传
- ❌ 版本号不变就覆盖远程
- ❌ 用 `git clone/push`（代理阻断风险）
- ❌ 不验证就声称上传成功

## 六、完成后

输出结果摘要：

```
上传完成：
✅ skill-a (新建) — commit: abc1234
✅ skill-b (更新 v1.2.0→v1.3.0) — commit: def5678
⏭️ skill-c — 跳过（外部引入）
⚠️ skill-d — 跳过（README 过时，需先更新）
```

然后更新用户记忆，记录本次上传了哪些 skill。

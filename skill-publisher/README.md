# skill-publisher

> 将本地 Claude Code skill 发布到 GitHub 仓库。只上传自己创建的。

## 快速开始

```
/skill-publisher
```

会列出本地所有 skill，标注个人/外部，让你选择上传哪些。

```
/skill-publisher beautify-flowchart
```

只上传指定的 skill。

```
/skill-publisher --all-personal
```

上传所有个人创建的 skill。

## 做什么

1. **审计本地** — 列出所有 skill，区分个人创建 vs 外部引入
2. **对比远程** — 检查哪些已存在、哪些是新的
3. **质量检查** — 确保有 frontmatter、README 不过时、版本号合理
4. **推送** — 用 `gh api` 上传（代理安全，不走 git clone）
5. **验证** — 推送后逐文件确认

## 判断标准

| 个人创建 | 外部引入 |
|---------|---------|
| 领域极其具体 | 有 `author:` 指向他人 |
| 用户记忆中有记录 | 名称带品牌前缀（baoyu-等） |
| 无命名空间前缀 | 知名社区 skill（humanizer 等） |
| 用户说是自己写的 | 非语义化版本号 |

不确定时列证据让用户判断，不替用户做决定。

## 版本

v1.0.0 — 2026-06-07

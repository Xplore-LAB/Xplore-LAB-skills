# skill-publisher

> 一键发布 Claude Code skill 到 GitHub。审计 → 质量门 → 版本 bump → 版权 → 推送 → 验证，全流程自动化。

## 触发

不需要记命令，说人话即可：

```
把 beautify-flowchart 上传到 GitHub
上传所有个人 skill
还有什么没传？
```

## 全流程

```
触发 → 审计 → 对比 → 质量门 → 版本 → 版权 → 文件过滤 → 推送 → 验证 → 报告
```

一个命令走完 10 步，中间不出确认对话框（除了版本 bump 和来源不确定）。

## 质量门

上传前自动检查，不通过则修复或阻止：

| 检查 | 处理 |
|------|------|
| 无 frontmatter | 🔧 自动补全 |
| README 过时 | ⚠️ 提醒重写 |
| 无 LICENSE | 🔧 自动生成 MIT |
| 无 CHANGELOG | 不阻止（首次上传允许） |
| 版本号未 bump | 🔧 自动计算并 bump |
| 有 .png / .vsdx | 🚫 自动跳过 |

## 文件规则

- ✅ `.md` / `.json` / `.sh` / `.mmd` → 上传
- ❌ `.png` / `.jpg` / `.vsdx` / `.pptx` / `.pdf` → 跳过
- ❌ `.git/` / `node_modules/` / `__pycache__/` → 跳过

## 版权

自动为每个 skill 生成 MIT LICENSE，版权归属 `Xplore-LAB`。

## 版本

当前版本：**v2.0.0** — 2026-06-07

---
name: github-helper
description: GitHub 协作助手。用户说"克隆项目"、"上传到 GitHub"、"推送代码"、"帮我下载 GitHub 项目"、"复现项目"、提供 GitHub 链接时触发。用于执行 git clone、git push、创建 GitHub 仓库等操作。用户 GitHub 用户名为 Xplore0114，已配置 SSH 密钥。
---

# GitHub Helper

## 用户信息

- GitHub 用户名：`Xplore0114`
- SSH 已配置：✅

## 常用操作

### 克隆别人的项目（复现）

```bash
git clone git@github.com:作者/仓库名.git [本地目录名]
```

省略本地目录名则使用仓库原名。

### 推送本地项目到 GitHub（新仓库）

**Step 1：在 GitHub 网页创建空仓库（用户自行操作）**
→ 登录 github.com → `+` → `New repository` → 填写仓库名 → 创建

**Step 2：本地初始化并推送**
```bash
cd 你的项目目录
git init
git add .
git commit -m "first commit"
git remote add origin git@github.com:Xplore0114/仓库名.git
git branch -M main
git push -u origin main
```

### 推送已有 git 仓库的更新
```bash
cd 项目目录
git add .
git commit -m "提交说明"
git push
```

### 查看状态
```bash
cd 项目目录
git status
git log --oneline -5
```

## 注意事项

- 克隆/推送公开仓库：✅ 可以
- 推送需要 GitHub 上已创建对应仓库
- 用户的本地工作目录：`C:\Users\12286\.qclaw\workspace`
- 克隆时目标路径可指定，默认为工作目录
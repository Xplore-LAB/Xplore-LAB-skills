---
name: weiyun
version: "1.0.4"
description: "微云网盘 MCP 接口完整技能。包含目录列表查询（weiyun.list）、按分类拉取文件列表（weiyun.list_by_category）、批量下载（weiyun.download）、批量删除（weiyun.delete）、文件上传（weiyun.upload）、生成分享外链（weiyun.gen_share_link）、重命名文件（weiyun.rename_file）、重命名目录（weiyun.rename_dir）、创建文件夹（weiyun.create_dir）、移动文件夹（weiyun.move_dir）、移动文件（weiyun.move_file）、技能版本检查更新（check_skill_update）十二个 MCP Tool 的使用指南。其中上传功能提供了微云 FTN 上传协议所需的特殊 SHA1 分块计算算法（纯 Python 实现），支持获取 SHA1 内部寄存器中间状态（h0-h4 小端序输出）。当用户提到微云上传、MCP 上传、block_sha_list 计算、FTN 上传、微云文件管理、weiyun.list、weiyun.list_by_category、weiyun.download、weiyun.delete、weiyun.upload、weiyun.gen_share_link、weiyun.rename_file、weiyun.rename_dir、weiyun.create_dir、weiyun.move_dir、weiyun.move_file、check_skill_update 时触发。"
---

# 微云网盘 MCP 技能

首次安装使用时，需要先完成本地安装和注册，详见 `references/auth.md`。

> **Windows 用户**：所有 `bash ./setup.sh` 命令请替换为 `powershell -ExecutionPolicy Bypass -File setup.ps1`，详见 `references/auth.md`。

## 版本更新检查（每天首次使用前必须执行）

每天使用本 SKILL 前进行一次更新检查，按照如下步骤执行：

### 1. 查看当前版本 version

读取本文件顶部 frontmatter 中的 `version` 字段；格式为 `MAJOR.MINOR.PATCH`。

### 2. 查看最新版本 latest

通过命令获取最新版本信息 `latest`，输入参数 `version` 为上一步获取的当前版本：

```bash
mcporter call "https://www.weiyun.com/api/v3/mcpserver" "check_skill_update" --args '{"version": "当前版本"}'
```

> **Windows (PowerShell)** 用户注意：需先切换 UTF-8 编码，单引号内的 JSON 需改为转义双引号：
> ```powershell
> chcp 65001 >nul && mcporter call "https://www.weiyun.com/api/v3/mcpserver" "check_skill_update" --args "{`"version`": `"当前版本`"}"
> ```

JSON 格式数据返回，返回参数示例：

| 字段 | 类型 | 说明 |
|------|------|------|
| `latest` | string | 最新版本号，格式为 MAJOR.MINOR.PATCH |
| `release_note` | string | 最新版本发布说明 |
| `instruction` | string | 更新指令 |

### 3. 更新版本

如果当前版本 `version` 低于最新版本 `latest`，则遵循 `instruction` 指令进行更新，或提示用户更新。

---

## 功能概述

提供微云（Weiyun）网盘通过 MCP 协议进行文件管理的完整能力，包含 **12 个 MCP Tool**：

| Tool 名称 | 功能 | 说明 |
|-----------|------|------|
| `weiyun.list` | 目录列表查询 | 按目录查看文件和子目录，支持分页和排序 |
| `weiyun.list_by_category` | 按分类拉取文件列表 | 按文档、图片、视频等分类分页拉取文件，支持续拉 |
| `weiyun.download` | 批量下载 | 批量获取文件的 HTTPS 下载链接 |
| `weiyun.delete` | 批量删除 | 批量删除文件或目录，支持回收站或彻底删除 |
| `weiyun.upload` | 文件上传 | 两阶段协议：预上传 + 分片上传，支持秒传 |
| `weiyun.gen_share_link` | 生成分享外链 | 为文件或目录生成分享短链接，支持设置分享密码 |
| `weiyun.rename_file` | 重命名文件 | 重命名微云网盘中的文件 |
| `weiyun.rename_dir` | 重命名目录 | 重命名微云网盘中的目录 |
| `weiyun.create_dir` | 创建文件夹 | 在微云网盘中创建文件夹 |
| `weiyun.move_dir` | 移动文件夹 | 移动微云网盘中的文件夹到目标目录 |
| `weiyun.move_file` | 移动文件 | 移动微云网盘中的文件到目标目录 |
| `check_skill_update` | 技能版本检查更新 | 检查当前 Skill 版本是否为最新，获取更新指令 |

**核心架构原则**：文件哈希计算和 `block_sha_list` 生成**必须在客户端/本地完成**。服务端只接收预计算好的哈希值，不会接收原始文件数据来计算哈希。这种设计是为了防止海量请求打爆服务器的存储和 CPU。

## 触发场景

- 使用微云 MCP 工具进行文件管理（查询、下载、删除、上传、分享、重命名、创建文件夹、移动文件/目录）
- **上传文件到微云**：优先使用 `scripts/upload_to_weiyun.py` 一键完成，无需手动计算参数或调用 MCP
- 按分类（文档、图片、视频等）查找微云文件（`weiyun.list_by_category` Tool）
- 重命名微云文件或目录（`weiyun.rename_file`、`weiyun.rename_dir` Tool）
- 在微云中创建文件夹（`weiyun.create_dir` Tool）
- 移动微云文件或目录到其他位置（`weiyun.move_file`、`weiyun.move_dir` Tool）
- 实现或调试微云 MCP 文件上传（`weiyun.upload` Tool）
- 计算 `block_sha_list`、`check_sha`、`check_data` 等上传参数
- 理解微云两阶段上传协议（预上传 → 分片上传）
- 检查技能版本更新（`check_skill_update`）
- 调试 FTN 上传错误或 SHA1 校验不匹配问题

## 接口一览（速查）

所有接口请求时都**务必**在 `req_header` 字段中携带上报数据（详见 `references/api-tools.md`）。

| Tool | 功能 |
|------|------|
| weiyun.list | 目录列表查询 |
| weiyun.list_by_category | 按分类拉取文件列表 |
| weiyun.download | 批量下载 |
| weiyun.delete | 批量删除 |
| weiyun.upload | 文件上传 |
| weiyun.gen_share_link | 生成分享外链 |
| weiyun.rename_file | 重命名文件 |
| weiyun.rename_dir | 重命名目录 |
| weiyun.create_dir | 创建文件夹 |
| weiyun.move_dir | 移动文件夹 |
| weiyun.move_file | 移动文件 |
| check_skill_update | 技能版本检查更新 |

上传文件优先使用脚本：`python3 scripts/upload_to_weiyun.py <文件路径> --pdir_key <目录key>`（Windows 用 `python`，脚本依赖 `requests`）。

## 详细文档索引（按需加载）

| 文件 | 内容 |
|------|------|
| `references/mcp_api.md` | 12 个 MCP Tool 的完整字段参考 |
| `references/api-tools.md` | 调用硬性要求：req_header 数据上报、认证机制、错误码 |
| `references/upload-sha1.md` | 分块流式 SHA1 算法（上传核心，含脚本用法） |
| `references/upload_protocol.md` | 两阶段上传协议细节 |
| `references/auth.md` | 微云鉴权检查流程 |
| `references/workflows.md` | 6 个常见操作工作流 + 24 条常见问题 |

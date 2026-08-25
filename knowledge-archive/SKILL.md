---
name: knowledge-archive
description: 知识链接即时存档。当用户发送任何知识类链接（论文、项目、文章、视频）时使用此技能。自动完成：读取内容 → 本地存档 → 飞书同步 → 摘要汇报。适用于 mp.weixin.qq.com、github.com、arxiv.org 及其他知识类 URL。运行环境要求：Linux 服务器 + xray 代理（SOCKS5 7890）+ 飞书环境变量。
---

# 知识链接即时存档

## 触发条件
用户发送包含知识类链接的消息（URL 匹配以下模式）：
- 微信文章：`mp.weixin.qq.com/s/...`
- GitHub 仓库/项目：`github.com/...`
- 论文：`arxiv.org/abs/...`
- 其他知识类 URL（技术博客、文档、教程等）

## 流程

### Step 0: 前置检查
```
1. 检查 xray 代理是否运行：ps aux | grep xray
2. 如果未运行：sudo systemctl start xray
3. 测试连通性：curl -s --max-time 5 --proxy socks5h://127.0.0.1:7890 https://httpbin.org/ip
```
**不要跳过此步直接尝试读取，否则会浪费 2-3 轮调用。**

### Step 1: 读取内容
根据链接类型选择读取方式：

**微信文章**（必须用代理+桌面UA）：
```bash
curl -s --max-time 15 --proxy socks5h://127.0.0.1:7890 \
  -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  -H "Accept-Language: zh-CN,zh;q=0.9" \
  "<URL>" | python3 -c "解析脚本"
```

**GitHub**：用 `web_fetch` 直接读取，优先读 README.md

**其他 URL**：用 `web_fetch`，失败则尝试代理

### Step 2: 提取关键信息
- 标题
- 核心观点（3-5 条）
- 可操作的要点
- 原始链接

### Step 3: 本地存档
写入 `memory/knowledge/<slug>.md`，格式：
```markdown
# 标题（来源：平台 日期）

原文链接: <URL>

## 核心观点
...

## 关键要点
...
```

命名规则：`<英文短横线分隔的关键词>.md`，如 `skill-writing-methodology.md`

### Step 4: 飞书同步（可选）
如果内容有长期参考价值，同步到飞书 Agent 资料库。folder token 从环境变量 `FEISHU_FOLDER_TOKEN` 读取，不在任何文档中明文记录。
新资源创建后立即加 full_access，open_id 从环境变量 `FEISHU_OPEN_ID` 读取。

配置方式（首次使用前）：
```bash
export FEISHU_FOLDER_TOKEN="<你的飞书文件夹 token>"
export FEISHU_OPEN_ID="<你的飞书 open_id>"
```

### Step 5: 摘要汇报
给用户 3-5 句话总结核心内容，附上存档位置。

## 失败处理
| 症状 | 原因 | 解决方案 |
|------|------|----------|
| 微信"环境异常" | 代理未运行或节点失效 | 先重启 xray，不行则换节点 |
| 内容为空 | UA 被识别 | 确保用桌面 Chrome UA |
| GitHub 404 | 仓库私有或已删除 | 告知用户，无法存档 |

## 参考
- 微信文章读取详情：`skills/wechat-article-reader/SKILL.md`
- 代理配置：`memory/details/proxy.md`
- 飞书资源清单：`memory/details/feishu-resources.md`

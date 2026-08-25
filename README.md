# Xplore-LAB Skills

QClaw / OpenClaw 助手自定义技能仓库，共 30 个 skill，按功能分类文件夹组织，分为「自建」与「第三方收录」两类。

## 目录结构

```
├── 模式与人设/        modes、interview-agent、research-lab、persona-switch
├── 知识管理/          2nd-brain、knowledge-archive、dao-fa-shu-model
├── 科研与写作/        paper-experience、chuangye
├── 信息采集/          wechat-article-reader
├── 图表可视化/        beautify-flowchart
├── 研发与运维/        github-helper、llm-tracker-maintainer、wecomcli-setup、qclaw-cron-skill
├── 云服务/            weiyun
├── 元技能/            experience-to-skill、skill-publisher、feature-testing
└── 第三方收录/        kdocs、tencent-news、wendao、youdaonote、processon、fbs_bookwriter、
                      searxng-bangs、xbrowser、file-diff-checker、bdpan-storage、flyai
```

> 说明：分类文件夹仅用于源码组织。安装到宿主时，把对应 skill 目录平铺复制到宿主的 skills 目录（如 ~/.claude/skills/），skill 正文中的 `skills/<name>/` 引用均指安装后的平铺路径。

## 自建技能（19 个）

### 模式与人设/

| Skill | 用途 | 触发 |
|---|---|---|
| modes | 模式切换统一入口（面试 / 科研 / 正常） | 「进入 XX 模式」「有哪些模式」 |
| interview-agent | 面试官 Agent，按简历技术拷打（简历在 references/resume.md） | 「面试模式」「mock interview」 |
| research-lab | 科研模式：假设驱动循环、PubMed/arXiv 检索、证据追踪 | 「进入科研模式」、发论文链接 |
| persona-switch | 切换 agent 人设（赛博朋友 / 创始人龙虾 / 温柔伴侣） | 「切换人设」 |

### 知识管理/

| Skill | 用途 | 触发 |
|---|---|---|
| 2nd-brain | 个人知识库，按类目捕获与检索实体信息 | 「remember」「note that」「what do I know about」 |
| knowledge-archive | 知识链接即时存档（本地 + 飞书同步）。需 Linux + xray + 飞书环境变量 | 发送知识类 URL |
| dao-fa-shu-model | 道法术三层结构化思维模型 | 信息整理、写作、会议纪要、prompt 优化 |

### 科研与写作/

| Skill | 用途 | 触发 |
|---|---|---|
| paper-experience | 论文投稿经验：选刊、Cover Letter、审稿回复（搜索走 searxng-bangs） | 投稿经验、期刊选择、审稿回复 |
| chuangye | 创业方法论知识库（《创业可以学》+ OPC 一人公司） | 创业、OPC、副业商业化话题 |

### 信息采集/

| Skill | 用途 | 触发 |
|---|---|---|
| wechat-article-reader | 读取微信公众号文章。需 xray 代理（SOCKS5 7890） | mp.weixin.qq.com 链接 |

### 图表可视化/

| Skill | 用途 | 触发 |
|---|---|---|
| beautify-flowchart | 流程图美化与可编辑重建（draw.io / PPT / SVG / Visio） | 提供流程图要求美化或重建 |

### 研发与运维/

| Skill | 用途 | 触发 |
|---|---|---|
| github-helper | GitHub 协作速查（clone / push / 建仓库） | 「克隆项目」「推送代码」 |
| llm-tracker-maintainer | LLM Papers Tracker 站点维护与 arXiv 抓取排障 | 「llm-tracker」「arxiv fetch」 |
| wecomcli-setup | 企业微信 CLI 安装引导与自然语言翻译 | 「安装企业微信 CLI」「帮我发消息给张三」 |
| qclaw-cron-skill | 定时任务权威指南（MANDATORY，禁止凭记忆猜参数） | 「cron」「定时」「提醒」「打卡」 |

### 云服务/

| Skill | 用途 | 触发 |
|---|---|---|
| weiyun | 微云网盘 12 个 MCP Tool 与 FTN 上传（v1.0.4，已按渐进披露拆分文档） | 「微云上传」「微云文件管理」 |

### 元技能/

| Skill | 用途 | 触发 |
|---|---|---|
| experience-to-skill | 把经验提炼为 Skill（先跑通再封装） | 「把这个变成 Skill」「总结一下」 |
| skill-publisher | 本地 skill 一键发布到 GitHub（版本 / LICENSE / 质量门 / 推送） | 发布 skill 到 GitHub |
| feature-testing | 新功能上线测试规则与回滚方案 | 「上线前测一下」「灰度试跑」 |

## 第三方收录/（11 个，来源标记见各目录）

| Skill | 来源 | 用途 |
|---|---|---|
| kdocs | 金山文档官方 | 云文档 / 表格 / PPT / 知识库全套操作 |
| tencent-news | TencentNews | 7×24 新闻热榜与早晚报 |
| wendao-partner-qclaw-skill | 携程问道 | 旅行问答与行程规划 |
| youdaonote | 有道官方 | 有道云笔记 CRUD / 待办 / 剪藏 |
| processon-diagram-generator | ProcessOn 官方 | 流程图 / 架构图 / ER 图在线生成 |
| fbs_bookwriter | ClawHub | 长文档写作全流程（书 / 手册 / 白皮书） |
| searxng-bangs | ClawHub | SearXNG 隐私聚合搜索，250+ 引擎 |
| xbrowser | ClawHub | CDP 浏览器自动化（复用登录态） |
| file-diff-checker | ClawHub | 重复文件差异对比与去重 |
| bdpan-storage | ClawHub（SKILL.md 缺失，待补） | 百度网盘存储 |
| flyai | 外部 CLI（SKILL.md 缺失，待补） | 旅行语义搜索 |

> 第三方件以原样收录为主，问题修复优先反馈上游；自建件在本仓库直接维护。

## 环境适配矩阵

| 环境 | 可用 skill |
|---|---|
| 任意环境（纯提示词 / 无外部依赖） | modes、interview-agent、persona-switch、dao-fa-shu-model、experience-to-skill、feature-testing、chuangye、beautify-flowchart |
| 需 node | research-lab、wecomcli-setup、fbs_bookwriter、wendao、xbrowser |
| 需 python3 | searxng-bangs、processon、weiyun、knowledge-archive、llm-tracker-maintainer |
| 需 Linux 服务器 + xray 代理 | knowledge-archive、wechat-article-reader |
| 需 API Key / Token | kdocs、weiyun、tencent-news、wendao、youdaonote、processon、llm-tracker-maintainer（GITHUB_PAT） |

## 关联关系速览

- modes 是 interview-agent 与 research-lab 的统一入口
- knowledge-archive 与 research-lab 引用 wechat-article-reader 读取公众号内容
- experience-to-skill 产出 skill，skill-publisher 负责发布，feature-testing 负责上线前验证
- paper-experience 的联网搜索由 searxng-bangs 提供

---
*欢迎贡献新的技能！*

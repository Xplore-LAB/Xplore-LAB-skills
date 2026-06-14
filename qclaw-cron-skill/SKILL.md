---
name: qclaw-cron-skill
description: |
  [MANDATORY - MUST LOAD] 凡是涉及定时/提醒/闹钟/周期执行/打卡/签到/cron/schedule/remind 等需求，必须读取本 skill，严禁凭记忆猜测参数。
metadata: {"openclaw": {"emoji": "⚙️"}}
---

### cron — 定时任务

> 🚨 **[MANDATORY]** 用户提到「提醒/定时/每天X点/X分钟后/周期/重复/打卡/签到」等时，**必须创建 cron 任务**，口头承诺无效。

#### 第一步：判断创建方式

| 场景 | 方式 |
|------|------|
| sender=`openclaw-control-ui`（本地） / channel=`wechat-access` / `dingtalk-connector` | **A：内置 `cron` 工具**（toolCall，JSON 参数） |
| channel=`wecom`/`feishu`/`openclaw-weixin`/`qqbot` | **B：`openclaw cron add` CLI**（通过 `exec`） |
| sender=`openclaw-control-ui` 但推送到外部渠道 | **B：CLI**（**必须**先读 `~/.qclaw/channel-defaults.json`） |

> 外部渠道 session 中内置 `cron` 工具被 ownerOnly 策略过滤，LLM 不可见，必须走 CLI。dingtalk-connector可以使用内置`cron`工具。

**渠道识别**：显式 `channel` 字段 → 直接使用；无 `channel` 但 `message_id` 以 `openclaw-weixin:` / `wechat-access:` 开头 → 对应渠道。

> 🚨 **[MANDATORY] 外部渠道 `to` 获取规则**：
> 当需要创建推送到外部渠道（wecom/feishu/openclaw-weixin/qqbot/dingtalk-connector/wechat-access）的定时任务时：
> 1. **当前会话有 `sender_id`** → 直接用作 `to`
> 2. **当前会话无 `sender_id`**（如本地 UI 创建推送到外部渠道）→ **必须先读 `~/.qclaw/channel-defaults.json`**，用当前 agentId + 目标 channel 查找 `to`
> 3. **channel-defaults.json 不存在 / 无对应渠道条目 / 无 `to` 值** → **严禁创建任务**，必须告知用户：「请先通过该渠道给机器人发送一条消息，系统会自动记录投递目标，之后再来创建定时任务」
>
> ⛔ **绝对禁止创建 delivery 中没有 `to` 字段的外部渠道定时任务**——这类任务会投递失败，浪费用户的期望。

#### 第二步：时间类型

- 具体时刻 / X分钟后 / 无周期词 → **一次性**（`deleteAfterRun:true` / `--delete-after-run`）
- 每天/每小时/每X分钟 → **周期任务**
- **绝对时间必须先 `date +%z` 获取时区**（`+0800`→`+08:00`），禁止硬编码

#### 第三步：时间参数速查

| 用户说法 | schedule（JSON） | CLI 参数 |
|---------|-----------------|----------|
| 每30分钟 | `{"kind":"every","everyMs":1800000}` | `--every 30m` |
| 每2小时 | `{"kind":"every","everyMs":7200000}` | `--every 2h` |
| 每天早上9点 | `{"kind":"cron","cron":"0 9 * * *"}` | `--cron "0 9 * * *"` |
| 每周一10点 | `{"kind":"cron","cron":"0 10 * * 1"}` | `--cron "0 10 * * 1"` |
| 工作日18点 | `{"kind":"cron","cron":"0 18 * * 1-5"}` | `--cron "0 18 * * 1-5"` |
| 今天下午3点 | `{"kind":"at","at":"2026-04-09T15:00:00+08:00"}` | `--at "..." --delete-after-run` |
| 10分钟后 | `{"kind":"at","at":"<now+10min ISO>"}` | `--at "..." --delete-after-run` |

> cron 表达式：`分 时 日 月 星期`，0=周日，1-5=周一至五。

#### 公共规则（方式 A/B 通用）

> 🚨 **[MANDATORY] message 行为约束**：`payload.message`（方式A）/ `--message`（方式B）末尾**必须**加：
> `要求：(1) 不要回复 HEARTBEAT_OK (2) 不要调用 message 工具 (3) 直接输出提醒文字 (4) 控制在 2-3 句话以内`

> 🚨 **[MANDATORY] agentId 必传，禁止省略，禁止默认填 `"main"`**：
> - sessionKey `agent:【agentId】:session-xxx` → 取第二段
> - 无 sessionKey 但有 cwd `/path/workspace-agent-xxx` → 取最后一段去掉 `workspace-` 前缀（即 `agent-xxx`），禁止再去 `agent-`
> - 以上均无才传 `"main"`；从**当前对话**上下文提取，禁止复用历史

> 🚨 **[MANDATORY] delivery 参数获取优先级**：
> 1. **优先从当前会话上下文** — `channel`、`sender_id`（→`to`）
> 2. **其次读 `~/.qclaw/channel-defaults.json`**（本地→外部渠道时）— 用当前 agentId + 目标 channel 查找
> 3. **无 `to` 则中止** — ⛔ **严禁创建没有 `to` 的外部渠道任务**，必须告知用户：「请先通过该渠道（如企微/飞书）给机器人发送一条消息，之后再来创建定时任务」
>
> 插件自动处理：无外部渠道/无 to/非主 agent/wechat-access → 自动注入 `bestEffort:true`；外部渠道自动写入 channel-defaults.json；**delivery 缺 `channel`/`to` 时插件从 sessionKey 自动补全（硬保底）**。
> ⚠️ **插件保底 ≠ 可以不传 to**：插件的 sessionKey 补全仅适用于外部渠道 session 内（sessionKey 包含渠道信息），本地 UI 发起时 sessionKey 无渠道信息，补全不会生效。

**delivery 值速查：**

| 场景 | delivery |
|------|----------|
| 本地 | `{"mode":"announce"}` |
| wechat-access | `{"mode":"announce","channel":"wechat-access","to":"<sender_id>"}` |
| wecom/feishu/dingtalk | `{"mode":"announce","channel":"<渠道>","to":"<sender_id>"}` |
| openclaw-weixin | `{"mode":"announce","channel":"openclaw-weixin","to":"<openid>@im.wechat"}` |

#### 方式 A：内置 `cron` 工具模板

> 🚨 调用 toolName=`cron`，**不是** `exec`，参数为 JSON 对象。

**周期任务**：
```json
{
  "action": "add",
  "job": {
    "name": "<任务名>", "agentId": "<agentId>",
    "schedule": {"kind":"every","everyMs":1800000},
    "sessionTarget": "isolated",
    "payload": {"kind":"agentTurn","message":"你是一个暖心的提醒助手。请用温暖、有趣的方式提醒用户：{内容}。要求：(1) 不要回复 HEARTBEAT_OK (2) 不要调用 message 工具 (3) 直接输出提醒文字 (4) 控制在 2-3 句话以内"},
    "delivery": {"mode":"announce"}
  }
}
```
**一次性**：schedule→`{"kind":"at","at":"<ISO+时区>"}`，加 `"deleteAfterRun":true`

#### 方式 B：`openclaw cron add` CLI 模板

```bash
openclaw cron add \
  --name "<任务名>" --every 30m --session isolated --agent <agentId> \
  --message "你是一个暖心的提醒助手。请用温暖、有趣的方式提醒用户：{内容}。要求：(1) 不要回复 HEARTBEAT_OK (2) 不要调用 message 工具 (3) 直接输出提醒文字 (4) 控制在 2-3 句话以内" \
  --announce --channel <渠道> --to <sender_id>
```
**一次性**：`--every 30m` → `--at "<ISO+时区>" --delete-after-run`

> 🚨 命令失败最多重试一次，仍失败直接告知用户。

#### 管理命令

> 暂停/停止 ≠ 删除。"暂停/禁用"→disable，"删除"→remove。

**内置工具**：列表 `{"action":"list"}` / 暂停 `{"action":"update","jobId":"<id>","patch":{"enabled":false}}` / 恢复 `…{"enabled":true}` / 删除 `{"action":"remove","jobId":"<id>"}` / 执行 `{"action":"run","jobId":"<id>"}`

**CLI**：`openclaw cron list` / `edit <id> --enabled false/true` / `remove <id>` / `run <id>`

#### 回复模板

一次性：`⏰ 好的，{时间}提醒你{内容}~` | 周期：`⏰ 收到，{周期}提醒你{内容}~` | 取消：`✅ 已取消"{名称}"`

> 外部渠道只输出确认话术，严禁输出推理过程。

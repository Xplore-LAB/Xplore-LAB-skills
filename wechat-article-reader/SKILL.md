---
name: wechat-article-reader
description: 读取微信公众号文章内容。当用户提供微信公众号文章链接（mp.weixin.qq.com/s/...）时使用此技能。通过代理 + 特定 UA 绕过微信反爬机制。
---

## When NOT to Use
- ❌ 非微信文章链接（如知乎、掘金、GitHub 等用 web_fetch）
- ❌ 用户只想知道文章大意（用 summarize skill 更快）
- ❌ 代理服务 xray 未运行时（会一直超时，先检查代理状态）

# 微信公众号文章读取

## 问题背景

微信公众号文章（`mp.weixin.qq.com/s/...`）对服务器 IP 有严格的反爬机制：
- 云服务器 IP（阿里云、AWS 等数据中心 IP）直接被验证码拦截
- 即使使用代理，如果代理出口也是数据中心 IP，同样会被拦
- 微信检测浏览器指纹、UA、cookies 等多重因素

## 成功方案

通过 **xray 代理 + 桌面 Chrome UA** 可以成功读取。

### 前置条件

1. **xray 代理服务运行中**，监听 SOCKS5 端口 7890
   ```bash
   # 检查代理是否运行
   ps aux | grep xray | grep -v grep
   # 测试代理连通性
   curl -s --max-time 5 --proxy socks5h://127.0.0.1:7890 https://httpbin.org/ip
   ```

2. **代理出口 IP 不能是纯数据中心 IP**（需要 BGP/家宽混合节点）

### 读取命令

```bash
curl -s --max-time 15 --proxy socks5h://127.0.0.1:7890 \
  -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  -H "Accept-Language: zh-CN,zh;q=0.9" \
  "https://mp.weixin.qq.com/s/<文章ID>" 2>&1
```

### 内容解析

```python
import re, html

content = raw_html

# 提取标题
title_match = re.search(r'var msg_title = "(.*?)";', content)
title = html.unescape(title_match.group(1)) if title_match else "未知标题"

# 提取正文
body_match = re.search(r'id="js_content"[^>]*>(.*?)</div>', content, re.DOTALL)
if body_match:
    text = re.sub(r'<[^>]+>', '\n', body_match.group(1))
    text = html.unescape(text).strip()
    text = re.sub(r'\n{3,}', '\n\n', text)
```

### 检测是否被拦截

```python
if 'js_content' in content:
    # ✅ 成功获取
    pass
elif '验证' in content or '环境异常' in content:
    # ❌ 被验证码拦截，检查代理和 UA
    pass
```

## 踩坑全过程记录（2026-03-26 实战）

### 尝试过的方案（全部失败）

| # | 方案 | 结果 | 失败原因 |
|---|------|------|----------|
| 1 | 直接 curl + 移动端 UA | ❌ 验证码 | 服务器 IP 是阿里云数据中心 |
| 2 | web_fetch（内置工具） | ❌ 验证码 | 同上 |
| 3 | summarize CLI（@steipete/summarize） | ❌ 验证码 | 底层也是 requests，过不了 |
| 4 | Playwright headless 浏览器 | ❌ 验证码 | 无头浏览器指纹被检测 + 数据中心 IP |
| 5 | 免费代理池（proxyscrape/github列表） | ❌ 连不上或仍被拦 | 免费代理不可靠，且出口也是数据中心 IP |
| 6 | Playwright + 代理 | ❌ 验证码 | 代理通了但数据中心 IP 仍被识别 |
| 7 | pyUniBParcer 服务端部署 | ❌ 环境限制 | botasaurus 需要 Xvfb 图形界面，服务器无 root 权限 |
| 8 | Google Cache / Archive.org | ❌ 无缓存 | 微信文章很少被收录 |
| 9 | curl + 代理 + 移动端 MicroMessenger UA | ❌ 验证码 | **移动端 UA 反而更容易触发检测！** |

### 突破点

**第 10 次尝试：curl + 代理 + 桌面 Chrome UA → ✅ 成功**

关键变量：
- 之前用的是：`MicroMessenger/8.0.44`（微信内置浏览器 UA）
- 改成：桌面 `Chrome/120.0.0.0` UA
- 其他条件不变（同一个代理节点、同一个 URL）

### 为什么桌面 UA 反而有效？

推测原因：
1. 微信对 `MicroMessenger` UA 的请求做**更严格的身份验证**（需要微信 cookie/token）
2. 桌面 Chrome UA 走的是**网页版微信**的验证逻辑，门槛更低
3. 代理出口虽然是数据中心 IP，但桌面 UA + 无微信特征 = 被当作普通网页访问

### 经验总结

1. **不要用 MicroMessenger UA** — 微信会检查微信客户端特有的 token/cookie，缺了就拦截
2. **桌面 Chrome UA 是正确选择** — 走网页版逻辑，不检查微信登录态
3. **代理是必要条件** — 纯数据中心 IP 不行，但不需要住宅 IP，BGP 混合节点够用
4. **代理 + 桌面 UA 是最小成功组合** — 不需要浏览器、不需要 cookie、不需要复杂的反检测

## 失败排查

| 症状 | 原因 | 解决方案 |
|------|------|----------|
| `环境异常，完成验证` | 代理出口是数据中心 IP | 换用家宽/BGP 节点 |
| `Connection refused` | xray 未运行 | 重启 xray |
| `Connection timed out` | 代理节点不通 | 换节点或检查订阅是否过期 |
| 内容为空 | UA 被识别 | 用桌面 Chrome UA，不要用移动端 |

## 关键经验

1. **桌面 Chrome UA 比移动端 UA 更容易过微信检测**（反直觉但实测有效）
2. **不要用移动端 MicroMessenger UA**，反而更容易触发验证码
3. **xray 订阅配置**：配置文件在 `/usr/local/etc/xray/config.json`，需要 `sudo` 权限写入
4. **订阅链接格式**：base64 编码的 VLESS/Hysteria2 节点列表
5. **调试方法论**：控制变量法——每次只改一个条件（UA/代理/节点），快速排除无效方案

## 相关文件

- xray 配置：`/usr/local/etc/xray/config.json`
- 订阅链接：用户私有（见 MEMORY.md）
- 代理端口：SOCKS5 `127.0.0.1:7890` / HTTP `127.0.0.1:7891`

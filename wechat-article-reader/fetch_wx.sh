#!/bin/bash
# 微信公众号文章读取脚本
# 用法: ./fetch_wx.sh <微信文章URL>

URL="$1"
PROXY="socks5h://127.0.0.1:7890"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

if [ -z "$URL" ]; then
  echo "用法: $0 <微信文章URL>"
  echo "示例: $0 https://mp.weixin.qq.com/s/xxx"
  exit 1
fi

# 检查代理是否运行
if ! curl -s --max-time 5 --proxy "$PROXY" https://httpbin.org/ip > /dev/null 2>&1; then
  echo "❌ 代理未运行，请先启动 xray:"
  echo "   nohup /usr/local/bin/xray run -config /usr/local/etc/xray/config.json &"
  exit 1
fi

# 抓取文章
RESULT=$(curl -s --max-time 15 --proxy "$PROXY" \
  -A "$UA" \
  -H "Accept-Language: zh-CN,zh;q=0.9" \
  "$URL" 2>&1)

# 解析结果
python3 -c "
import re, html, sys

content = '''$( echo "$RESULT" | sed "s/'/\\\\'/g" )'''

if 'js_content' in content:
    title_match = re.search(r'var msg_title = \"(.*?)\";', content)
    if title_match:
        print('标题:', html.unescape(title_match.group(1)))
    
    author_match = re.search(r'var nickname = \"(.*?)\";', content)
    if author_match:
        print('作者:', html.unescape(author_match.group(1)))
    
    body_match = re.search(r'id=\"js_content\"[^>]*>(.*?)</div>', content, re.DOTALL)
    if body_match:
        text = re.sub(r'<[^>]+>', '\n', body_match.group(1))
        text = html.unescape(text).strip()
        text = re.sub(r'\n{3,}', '\n\n', text)
        print(text)
elif '验证' in content or '环境异常' in content:
    print('❌ 被微信验证码拦截')
    print('尝试: 检查代理出口 IP 是否为数据中心 IP')
    sys.exit(1)
else:
    print('❓ 未知响应，长度:', len(content))
    sys.exit(1)
"

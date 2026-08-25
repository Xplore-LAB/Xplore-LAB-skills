#!/bin/bash

# 美化流程图skill - 环境检查和安装脚本

echo "检查美化流程图skill环境..."

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装"
    echo "请先安装 Node.js: https://nodejs.org/"
    exit 1
fi

echo "✓ Node.js 已安装: $(node --version)"

# 检查npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm 未安装"
    exit 1
fi

echo "✓ npm 已安装: $(npm --version)"

# 检查mermaid-cli
if ! command -v mmdc &> /dev/null; then
    echo "⚠️  mermaid-cli 未安装，正在安装..."
    npm install -g @mermaid-js/mermaid-cli

    if [ $? -eq 0 ]; then
        echo "✓ mermaid-cli 安装成功"
    else
        echo "❌ mermaid-cli 安装失败"
        echo "请手动运行: npm install -g @mermaid-js/mermaid-cli"
        exit 1
    fi
else
    echo "✓ mermaid-cli 已安装: $(mmdc --version 2>/dev/null || echo 'unknown')"
fi

# 检查配置文件
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/mermaid-config.json"

if [ -f "$CONFIG_FILE" ]; then
    echo "✓ 配置文件存在: $CONFIG_FILE"
else
    echo "❌ 配置文件缺失: $CONFIG_FILE"
    exit 1
fi

# 检查中文字体（Windows环境）
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    echo "✓ Windows 环境检测到，中文字体应该可用"
fi

echo ""
echo "✅ 环境检查完成！"
echo ""
echo "使用方法："
echo "  /beautify-flowchart path/to/your/flowchart.png"
echo ""
echo "示例："
echo "  /beautify-flowchart ~/documents/flowchart.png"
echo "  /beautify-flowchart C:/Users/username/Desktop/diagram.jpg"

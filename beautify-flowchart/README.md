# 美化流程图 Skill

这个skill可以帮助你将现有的流程图图片转换为更美观、更专业的版本。支持多种美化模式，满足不同需求。

## ✨ 核心特性

- 🎨 **多种美化模式** - 4种模式，灵活选择
- 🎯 **智能分析** - AI自动判断需要优化的部分
- 🎭 **多种主题** - 6种内置主题，一键切换
- 📐 **布局优化** - 自动优化节点位置和层次
- 🖼️ **高质量输出** - 支持高分辨率和自定义尺寸
- 🀄 **中文支持** - 完美支持中文标签和注释

## 🚀 快速开始

### 基本用法

```bash
/beautify-flowchart path/to/your/flowchart.png
```

### 指定模式

```bash
# 纯样式美化
/beautify-flowchart diagram.png --mode style

# 纯布局优化
/beautify-flowchart diagram.png --mode layout

# 完全美化
/beautify-flowchart diagram.png --mode both

# 智能美化（推荐）
/beautify-flowchart diagram.png --mode smart
```

### 完整参数

```bash
/beautify-flowchart diagram.png \
    --mode both \
    --theme modern \
    --direction LR \
    --width 1920 \
    --height 1080 \
    --scale 2 \
    --background white
```

---

## 📦 支持的模式

### 1️⃣ style（纯样式美化）

**特点：** 保持原布局，仅美化外观

**适用场景：**
- ✅ 布局已经很满意
- ✅ 只需要提升视觉效果
- ✅ 保持原有的阅读习惯

**示例效果：**
```
输入：布局合理，颜色单一
输出：保持布局，应用专业配色
```

```bash
/beautify-flowchart diagram.png --mode style
```

---

### 2️⃣ layout（纯布局优化）

**特点：** 优化节点位置，保持原样式

**适用场景：**
- ✅ 节点位置混乱
- ✅ 连接线交叉严重
- ✅ 需要更清晰的层次
- ✅ 对原有颜色满意

**示例效果：**
```
输入：颜色不错，布局混乱
输出：重新组织，保持配色
```

```bash
/beautify-flowchart diagram.png --mode layout
```

---

### 3️⃣ both（完全美化）

**特点：** 同时优化布局和样式

**适用场景：**
- ✅ 需要专业级呈现
- ✅ 用于演示或文档
- ✅ 追求最佳视觉效果
- ✅ 原图需要全面升级

**示例效果：**
```
输入：任何流程图
输出：全面美化，专业设计
```

```bash
/beautify-flowchart diagram.png --mode both
```

---

### 4️⃣ smart（智能美化）⭐ 推荐

**特点：** AI自动分析，智能选择最佳方案

**适用场景：**
- ✅ 不确定需要什么模式
- ✅ 希望AI自动判断
- ✅ 快速获得最佳结果

**智能分析：**
- 🔍 检测布局问题（节点重叠、连接线交叉等）
- 🎨 检测样式问题（颜色单一、形状未区分等）
- ⚡ 智能决策（选择最需要优化的部分）

**示例效果：**
```
输入：任何流程图
输出：AI分析后，针对性优化
```

```bash
/beautify-flowchart diagram.png --mode smart
```

---

## 🎭 支持的主题

| 主题 | 颜色风格 | 适用场景 |
|------|----------|----------|
| `default` | 蓝色商务 | 通用，正式文档 |
| `dark` | 暗色系 | 演示，屏幕展示 |
| `colorful` | 多彩活泼 | 创意，非正式场合 |
| `minimal` | 极简黑白 | 简洁，专业 |
| `business` | 专业商务 | 企业，商业文档 |
| `modern` | 现代时尚 | 现代感，科技风 |

### 主题预览

**default（默认）**
- 主色调：#4a90d9（蓝色）
- 风格：专业、正式

**dark（暗色）**
- 主色调：#1e88e5（亮蓝）
- 背景：#121212（深灰）
- 风格：现代、适合演示

**colorful（多彩）**
- 主色调：#e91e63（粉色）
- 风格：活泼、创意

### 使用主题

```bash
/beautify-flowchart diagram.png --theme dark
/beautify-flowchart diagram.png --theme colorful
/beautify-flowchart diagram.png --mode both --theme modern
```

---

## 📐 布局方向

| 方向 | 代码 | 说明 |
|------|------|------|
| 自动 | `auto` | AI选择最佳方向 |
| 从上到下 | `TD` 或 `TB` | 最常用，适合层次结构 |
| 从左到右 | `LR` | 适合宽屏展示 |
| 从右到左 | `RL` | 特殊需求 |

### 使用方向

```bash
/beautify-flowchart diagram.png --direction LR
/beautify-flowchart diagram.png --direction TD
/beautify-flowchart diagram.png --mode layout --direction auto
```

---

## 🖼️ 输出控制

### 尺寸控制

```bash
# 指定宽度
/beautify-flowchart diagram.png --width 1920

# 指定高度
/beautify-flowchart diagram.png --height 1080

# 同时指定
/beautify-flowchart diagram.png --width 1920 --height 1080
```

### 缩放比例

```bash
# 2倍清晰度
/beautify-flowchart diagram.png --scale 2

# 4倍清晰度（超清）
/beautify-flowchart diagram.png --scale 4
```

### 背景颜色

```bash
# 透明背景
/beautify-flowchart diagram.png --background transparent

# 白色背景
/beautify-flowchart diagram.png --background white

# 自定义颜色
/beautify-flowchart diagram.png --background "#f5f5f5"
```

---

## 📊 使用场景对比

### 场景1：登录流程图

**输入问题：**
- 布局：从上到下，但节点间距不均
- 样式：单一浅蓝色，无区分

**使用 `--mode style`：**
- 保持原布局
- 添加专业配色
- 区分不同节点类型
- 输出：专业、清晰

**使用 `--mode layout`：**
- 重新组织节点
- 优化层次结构
- 保持原颜色
- 输出：清晰、有条理

**使用 `--mode both`：**
- 完全重新设计
- 专业布局 + 配色
- 添加分组和注释
- 输出：演示级别

---

### 场景2：复杂业务流程

**输入问题：**
- 节点众多（20+）
- 连接线交叉严重
- 逻辑关系复杂

**推荐方案：**
```bash
# 使用smart模式，让AI分析最佳方案
/beautify-flowchart complex-flow.png --mode smart

# 或者使用both模式，全面优化
/beautify-flowchart complex-flow.png --mode both --direction LR
```

---

### 场景3：演示文稿

**需求：**
- 高分辨率
- 暗色主题
- 专业外观

**推荐方案：**
```bash
/beautify-flowchart diagram.png \
    --mode both \
    --theme dark \
    --scale 2 \
    --width 1920 \
    --background "#121212"
```

---

## 🔧 高级用法

### 批量处理

```bash
# 处理目录下所有PNG文件
for file in *.png; do
    /beautify-flowchart "$file" --mode smart
done

# 处理所有图片格式
for file in *.png *.jpg *.jpeg; do
    if [ -f "$file" ]; then
        /beautify-flowchart "$file" --mode both
    fi
done
```

### 条件处理

```bash
# 根据文件大小选择模式
size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file")
if [ "$size" -gt 100000 ]; then
    # 大文件使用smart模式
    /beautify-flowchart "$file" --mode smart
else
    # 小文件使用both模式
    /beautify-flowchart "$file" --mode both
fi
```

### 保留原文件

```bash
# 生成带时间戳的输出文件
timestamp=$(date +%Y%m%d_%H%M%S)
/beautify-flowchart diagram.png --output "diagram_${timestamp}.png"
```

---

## 📋 参数完整列表

| 参数 | 说明 | 默认值 | 可选值 |
|------|------|--------|--------|
| `--mode` | 美化模式 | `smart` | `style`, `layout`, `both`, `smart` |
| `--theme` | 颜色主题 | `default` | `default`, `dark`, `colorful`, `minimal`, `business`, `modern` |
| `--direction` | 布局方向 | `auto` | `auto`, `TD`, `LR`, `TB`, `RL` |
| `--width` | 输出宽度 | `auto` | 任意数字 |
| `--height` | 输出高度 | `auto` | 任意数字 |
| `--scale` | 缩放比例 | `1` | `1`, `2`, `3`, `4` |
| `--background` | 背景色 | `transparent` | `transparent`, `white`, `black`, 颜色代码 |
| `--output` | 输出文件名 | 自动生成 | 任意文件名 |

---

## 🎯 最佳实践

### 1. 模式选择

- **不确定需求** → 使用 `smart` 模式
- **布局已满意** → 使用 `style` 模式
- **样式已满意** → 使用 `layout` 模式
- **需要最佳效果** → 使用 `both` 模式

### 2. 主题选择

- **正式文档** → `default` 或 `business`
- **演示文稿** → `dark` 或 `modern`
- **创意展示** → `colorful`
- **简洁需求** → `minimal`

### 3. 尺寸设置

- **网页展示** → `--width 1200`
- **演示文稿** → `--width 1920 --scale 2`
- **打印输出** → `--scale 3` 或 `--scale 4`
- **社交媒体** → `--width 800 --height 600`

### 4. 性能优化

- 简单流程图 → 使用 `style` 或 `layout`（更快）
- 复杂流程图 → 使用 `smart`（更智能）
- 批量处理 → 使用 `smart`（自动判断）

---

## ❓ 常见问题

### Q: 应该选择哪个模式？

A: 如果不确定，使用 `smart` 模式。AI会自动分析并选择最佳方案。

### Q: 为什么美化后布局变化很大？

A: 使用 `--mode style` 会保持原布局。`both` 模式会同时优化布局和样式。

### Q: 如何保持原有颜色？

A: 使用 `--mode layout` 只优化布局，保持原样式。

### Q: 如何获得更高清的图片？

A: 使用 `--scale 2` 或 `--scale 4`。

### Q: 支持哪些图片格式？

A: 支持 PNG、JPEG、SVG、WebP 等常见格式。

### Q: 中文显示有问题？

A: 确保系统安装了中文字体（如微软雅黑）。

### Q: 处理时间太长？

A: 复杂流程图使用 `both` 模式会较慢。可以尝试 `smart` 模式或 `style` 模式。

---

## 📚 示例文件

skill目录中包含示例文件，可参考学习：

```
examples/
├── input-example.mmd          # 输入示例代码
├── input-example.png          # 输入示例图片
├── output-style.mmd           # style模式输出
├── output-style.png           # style模式图片
├── output-layout.mmd          # layout模式输出
├── output-layout.png          # layout模式图片
├── output-both.mmd            # both模式输出
├── output-both.png            # both模式图片
└── README.md                  # 示例说明
```

---

## 🛠️ 故障排除

### 问题1：中文显示为方框

**解决方案：**
```bash
# 确保系统安装了中文字体
# Windows: 微软雅黑、黑体
# macOS: 苹方、华文黑体
# Linux: 文泉驿微米黑

# 或者在配置中指定字体
/beautify-flowchart diagram.png --theme default --font "Microsoft YaHei"
```

### 问题2：mermaid-cli命令未找到

**解决方案：**
```bash
# 重新安装
npm install -g @mermaid-js/mermaid-cli

# 检查npm全局路径
npm config get prefix

# 添加到PATH
export PATH="$(npm config get prefix)/bin:$PATH"
```

### 问题3：图片太大或太小

**解决方案：**
```bash
# 使用缩放比例
/beautify-flowchart diagram.png --scale 2

# 或指定具体尺寸
/beautify-flowchart diagram.png --width 1920 --height 1080
```

### 问题4：布局混乱

**解决方案：**
```bash
# 使用layout模式专门优化布局
/beautify-flowchart diagram.png --mode layout

# 或使用smart模式让AI判断
/beautify-flowchart diagram.png --mode smart
```

### 问题5：样式没有变化

**解决方案：**
```bash
# 使用style或both模式
/beautify-flowchart diagram.png --mode style
/beautify-flowchart diagram.png --mode both
```

---

## 📞 技术支持

如果遇到问题，请检查：

1. ✅ Node.js和npm是否正确安装
2. ✅ mermaid-cli是否已全局安装
3. ✅ 图片文件是否存在且可读
4. ✅ 系统是否安装了中文字体
5. ✅ 参数是否正确（模式、主题等）

更多帮助，请查看：
- 快速开始：`cat ~/.claude/skills/beautify-flowchart/QUICKSTART.md`
- 示例文件：`ls ~/.claude/skills/beautify-flowchart/examples/`

---

## 📝 更新日志

### v1.1.0 (2026-06-03)
- ✨ 新增4种美化模式：style, layout, both, smart
- ✨ 新增6种颜色主题
- ✨ 支持自定义布局方向
- ✨ 支持自定义输出尺寸和缩放
- ✨ 添加智能分析功能

### v1.0.0 (2026-06-03)
- 🎉 初始版本
- ✅ 支持基本流程图美化
- ✅ 支持中文标签
- ✅ 提供默认蓝色主题

---

## 📄 许可证

MIT License

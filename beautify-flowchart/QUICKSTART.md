# 快速开始：美化流程图

## 🎯 一句话总结

**只需要一条命令，就能让流程图变得专业又美观！**

---

## 🚀 三种使用方式

### 方式1：最简单（推荐新手）

```bash
/beautify-flowchart 你的流程图.png
```

**效果：** AI自动分析，智能选择最佳美化方案

---

### 方式2：指定模式

```bash
# 只美化样式，保持原布局
/beautify-flowchart diagram.png --mode style

# 只优化布局，保持原样式
/beautify-flowchart diagram.png --mode layout

# 完全美化（样式+布局）
/beautify-flowchart diagram.png --mode both

# 让AI自动判断（最智能）
/beautify-flowchart diagram.png --mode smart
```

---

### 方式3：完全自定义

```bash
/beautify-flowchart diagram.png \
    --mode both \
    --theme dark \
    --direction LR \
    --scale 2 \
    --width 1920 \
    --background white
```

---

## 🎨 四种模式对比

| 模式 | 说明 | 速度 | 效果 | 推荐场景 |
|------|------|------|------|----------|
| `style` | 纯样式美化 | ⚡ 快 | 🎨 外观升级 | 布局已满意 |
| `layout` | 纯布局优化 | ⚡ 快 | 📐 结构清晰 | 布局混乱 |
| `both` | 完全美化 | 🐢 慢 | 🚀 最佳效果 | 追求完美 |
| `smart` | 智能美化 | ⚡ 中 | 🤖 自动判断 | 不确定需求 |

**选择困难？用 `smart` 就对了！**

---

## 🎭 六种主题

```bash
# 默认蓝色（专业）
/beautify-flowchart diagram.png --theme default

# 暗色系（适合演示）
/beautify-flowchart diagram.png --theme dark

# 多彩（活泼）
/beautify-flowchart diagram.png --theme colorful

# 极简（简洁）
/beautify-flowchart diagram.png --theme minimal

# 商务（正式）
/beautify-flowchart diagram.png --theme business

# 现代（时尚）
/beautify-flowchart diagram.png --theme modern
```

---

## 📐 布局方向

```bash
# 自动选择（推荐）
/beautify-flowchart diagram.png --direction auto

# 从上到下（最常用）
/beautify-flowchart diagram.png --direction TD

# 从左到右（宽屏）
/beautify-flowchart diagram.png --direction LR
```

---

## 🖼️ 输出控制

### 尺寸调整

```bash
# 指定宽度
/beautify-flowchart diagram.png --width 1920

# 指定高度
/beautify-flowchart diagram.png --height 1080

# 同时指定
/beautify-flowchart diagram.png --width 1920 --height 1080
```

### 清晰度

```bash
# 2倍清晰度（推荐）
/beautify-flowchart diagram.png --scale 2

# 4倍清晰度（超清）
/beautify-flowchart diagram.png --scale 4
```

### 背景

```bash
# 透明背景
/beautify-flowchart diagram.png --background transparent

# 白色背景
/beautify-flowchart diagram.png --background white

# 暗色背景
/beautify-flowchart diagram.png --background "#121212"
```

---

## 📋 常用组合

### 1. 快速美化（最常用）

```bash
/beautify-flowchart diagram.png --mode smart
```

**适用：** 不确定需求，想快速获得好效果

---

### 2. 专业文档

```bash
/beautify-flowchart diagram.png --mode both --theme business
```

**适用：** 正式文档、商业报告

---

### 3. 演示文稿

```bash
/beautify-flowchart diagram.png --mode both --theme dark --scale 2
```

**适用：** PPT、演讲、屏幕展示

---

### 4. 保持原样

```bash
/beautify-flowchart diagram.png --mode style
```

**适用：** 布局满意，只需美化外观

---

### 5. 清晰结构

```bash
/beautify-flowchart diagram.png --mode layout
```

**适用：** 布局混乱，需要整理

---

## 💡 使用技巧

### 1. 先用smart试水

```bash
# 先用smart模式看看效果
/beautify-flowchart diagram.png --mode smart

# 如果不满意，再用both模式
/beautify-flowchart diagram.png --mode both
```

### 2. 批量处理

```bash
# 处理当前目录所有PNG
for file in *.png; do
    /beautify-flowchart "$file" --mode smart
done
```

### 3. 保留原文件

输出文件会自动命名为 `原文件名_beautified.png`，不会覆盖原文件。

### 4. 查看效果

执行后会自动显示美化后的图片，可以直接预览效果。

---

## 🎯 场景推荐

### 场景1：登录流程图

**问题：** 颜色单一，节点未区分

**推荐：**
```bash
/beautify-flowchart login.png --mode style --theme default
```

**效果：** 保持布局，添加专业配色

---

### 场景2：复杂业务流程

**问题：** 节点多，布局乱

**推荐：**
```bash
/beautify-flowchart business.png --mode both --direction LR
```

**效果：** 重新组织，清晰分组

---

### 场景3：技术架构图

**问题：** 需要专业、现代感

**推荐：**
```bash
/beautify-flowchart arch.png --mode both --theme modern --scale 2
```

**效果：** 现代设计，高分辨率

---

### 场景4：演示文稿用图

**问题：** 需要暗色主题，高清晰度

**推荐：**
```bash
/beautify-flowchart slide.png --mode both --theme dark --scale 2 --background "#121212"
```

**效果：** 暗色主题，2倍清晰度

---

## ❓ 快速问答

### Q: 第一次使用，应该用什么命令？

```bash
/beautify-flowchart 你的图片.png --mode smart
```

### Q: 想要最佳效果？

```bash
/beautify-flowchart 你的图片.png --mode both --theme modern --scale 2
```

### Q: 布局太乱了？

```bash
/beautify-flowchart 你的图片.png --mode layout
```

### Q: 只想换个颜色？

```bash
/beautify-flowchart 你的图片.png --mode style --theme dark
```

### Q: 怎么获得更高清的图片？

```bash
/beautify-flowchart 你的图片.png --scale 2
```

---

## 📚 进阶阅读

- 详细文档：`cat ~/.claude/skills/beautify-flowchart/README.md`
- 示例文件：`ls ~/.claude/skills/beautify-flowchart/examples/`
- 环境检查：`bash ~/.claude/skills/beautify-flowchart/setup.sh`

---

## 🎉 开始使用

现在就试试吧！

```bash
# 最简单的开始
/beautify-flowchart 你的流程图.png

# 或者指定模式
/beautify-flowchart 你的流程图.png --mode smart
```

**享受美化流程图的乐趣！** 🎨✨

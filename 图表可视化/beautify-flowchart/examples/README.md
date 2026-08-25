# 美化模式示例对比

这个目录包含了四种美化模式的示例，帮助你理解每种模式的效果。

## 📁 示例文件

| 文件 | 说明 |
|------|------|
| `input-example.mmd` | 原始输入示例 |
| `input-example.png` | 原始输入图片 |
| `style-mode.mmd` | style模式代码 |
| `style-mode.png` | style模式图片 |
| `layout-mode.mmd` | layout模式代码 |
| `layout-mode.png` | layout模式图片 |
| `both-mode.mmd` | both模式代码 |
| `both-mode.png` | both模式图片 |
| `smart-mode.mmd` | smart模式代码 |
| `smart-mode.png` | smart模式图片 |

---

## 🎨 模式对比

### 输入（原始图片）

**特点：**
- 布局：从上到下，线性结构
- 样式：单一浅紫色
- 形状：简单的矩形和菱形

**问题：**
- 颜色区分度低
- 节点形状未明显区分
- 视觉效果一般

---

### Style 模式（纯样式美化）

**改进点：**
- ✅ 专业配色方案
- ✅ 不同节点类型使用不同颜色
- ✅ 更清晰的边框和字体
- ✅ 保持原有布局不变

**适用场景：**
- 布局已满意
- 只需要美化外观
- 保持原有的阅读习惯

**效果：**
```
输入：布局合理，颜色单一
输出：保持布局，应用专业配色
```

---

### Layout 模式（纯布局优化）

**改进点：**
- ✅ 使用分组（subgraph）组织相关节点
- ✅ 清晰的层次结构
- ✅ 减少连接线交叉
- ✅ 保持原有颜色方案

**适用场景：**
- 节点位置混乱
- 连接线交叉严重
- 需要更清晰的层次
- 对原有颜色满意

**效果：**
```
输入：颜色不错，布局混乱
输出：重新组织，保持配色
```

---

### Both 模式（完全美化）

**改进点：**
- ✅ 专业分组和布局
- ✅ 现代化配色方案
- ✅ 多样化的节点形状
- ✅ 清晰的层次结构
- ✅ 专业的视觉设计

**适用场景：**
- 需要专业级呈现
- 用于演示或文档
- 追求最佳视觉效果
- 原图需要全面升级

**效果：**
```
输入：任何流程图
输出：全面美化，专业设计
```

---

### Smart 模式（智能美化）

**智能分析：**
- 🔍 检测布局问题
- 🎨 检测样式问题
- ⚡ 智能决策

**改进点：**
- ✅ 根据实际需要优化
- ✅ 针对性美化
- ✅ 平衡效果和性能

**适用场景：**
- 不确定需要什么模式
- 希望AI自动判断
- 快速获得最佳结果

**效果：**
```
输入：任何流程图
输出：AI分析后，针对性优化
```

---

## 📊 效果对比表

| 特性 | Input | Style | Layout | Both | Smart |
|------|-------|-------|--------|------|-------|
| **布局** | 原始 | 保持 | 优化 | 优化 | 智能 |
| **颜色** | 单一 | 专业 | 保持 | 专业 | 智能 |
| **形状** | 简单 | 区分 | 保持 | 区分 | 智能 |
| **分组** | 无 | 无 | ✅ | ✅ | 智能 |
| **速度** | - | ⚡ 快 | ⚡ 快 | 🐢 慢 | ⚡ 中 |
| **效果** | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 🎯 选择建议

### 选择 Style 模式，如果：

- ✅ 布局已经很满意
- ✅ 只想提升视觉效果
- ✅ 保持原有的阅读习惯
- ✅ 时间紧迫，需要快速美化

**命令：**
```bash
/beautify-flowchart diagram.png --mode style
```

---

### 选择 Layout 模式，如果：

- ✅ 节点位置混乱
- ✅ 连接线交叉严重
- ✅ 需要更清晰的层次
- ✅ 对原有颜色满意

**命令：**
```bash
/beautify-flowchart diagram.png --mode layout
```

---

### 选择 Both 模式，如果：

- ✅ 需要专业级呈现
- ✅ 用于正式文档或演示
- ✅ 追求最佳视觉效果
- ✅ 原图需要全面升级

**命令：**
```bash
/beautify-flowchart diagram.png --mode both
```

---

### 选择 Smart 模式，如果：

- ✅ 不确定需要什么模式
- ✅ 希望AI自动判断
- ✅ 快速获得最佳结果
- ✅ 首次使用，想看看效果

**命令：**
```bash
/beautify-flowchart diagram.png --mode smart
```

---

## 🔧 使用示例

### 示例1：登录流程图

**输入问题：**
- 布局：从上到下，但节点间距不均
- 样式：单一浅蓝色，无区分

**推荐方案：**
```bash
# 使用style模式美化外观
/beautify-flowchart login.png --mode style

# 或使用both模式全面美化
/beautify-flowchart login.png --mode both --theme modern
```

---

### 示例2：复杂业务流程

**输入问题：**
- 节点众多（20+）
- 连接线交叉严重
- 逻辑关系复杂

**推荐方案：**
```bash
# 使用layout模式优化布局
/beautify-flowchart business.png --mode layout

# 或使用both模式全面美化
/beautify-flowchart business.png --mode both --direction LR
```

---

### 示例3：演示文稿

**需求：**
- 高分辨率
- 暗色主题
- 专业外观

**推荐方案：**
```bash
/beautify-flowchart slide.png \
    --mode both \
    --theme dark \
    --scale 2 \
    --width 1920 \
    --background "#121212"
```

---

## 📝 查看源码

你可以查看每个示例的Mermaid源码，学习如何编写专业的流程图：

```bash
# 查看style模式代码
cat style-mode.mmd

# 查看layout模式代码
cat layout-mode.mmd

# 查看both模式代码
cat both-mode.mmd

# 查看smart模式代码
cat smart-mode.mmd
```

---

## 💡 提示

1. **渐变色不支持**：Mermaid不支持CSS渐变，使用纯色代替
2. **emoji支持**：Mermaid支持在subgraph标题中使用emoji
3. **字体大小**：可以在classDef中设置font-size
4. **阴影效果**：Mermaid不支持阴影，使用边框粗细模拟

---

## 🚀 开始使用

现在你已经了解了四种模式的区别，可以开始美化你的流程图了！

```bash
# 最简单的方式
/beautify-flowchart 你的流程图.png --mode smart

# 或者指定具体模式
/beautify-flowchart 你的流程图.png --mode both --theme modern
```

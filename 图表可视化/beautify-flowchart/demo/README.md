# 订单处理流程 - 四种模式演示

这个示例展示了如何使用四种不同的美化模式处理一个真实的业务流程图。

## 📊 示例说明

### 流程图内容
**订单处理流程** - 包含以下阶段：
1. 🛒 客户下单
2. 📦 库存检查
3. 💳 支付处理
4. ✅ 订单确认
5. 🚚 物流配送
6. 🎉 完成订单

### 流程复杂度
- **节点数量**：20+
- **判断点**：4个
- **分支路径**：多条
- **循环结构**：2个（支付重试、配送等待）

---

## 🎨 四种模式效果对比

### 1️⃣ 原始版本

**特点：**
- 颜色：单一浅紫色
- 形状：简单的矩形和菱形
- 布局：线性，但有些混乱

**问题：**
- ❌ 颜色区分度低
- ❌ 节点类型未明显区分
- ❌ 连接线交叉较多
- ❌ 缺乏视觉层次

**文件：**
- `order-process-original.mmd`
- `order-process-original.png`

---

### 2️⃣ Style 模式（纯样式美化）

**改进点：**
- ✅ 专业配色方案
- ✅ 不同节点类型使用不同颜色
- ✅ 更清晰的边框和字体
- ✅ 保持原有布局不变

**颜色方案：**
- 🟢 **绿色**：开始/结束节点
- 🔵 **蓝色**：处理步骤
- 🟡 **黄色**：判断条件
- 🔴 **红色**：错误/失败
- 🟠 **橙色**：警告
- 🟣 **粉色**：输入/输出

**适用场景：**
- 布局已满意
- 只需要美化外观
- 保持原有的阅读习惯

**效果：**
```
输入：布局合理，颜色单一
输出：保持布局，应用专业配色
```

**文件：**
- `order-process-style.mmd`
- `order-process-style.png`

---

### 3️⃣ Layout 模式（纯布局优化）

**改进点：**
- ✅ 使用分组（subgraph）组织相关节点
- ✅ 清晰的层次结构
- ✅ 减少连接线交叉
- ✅ 保持原有颜色方案

**分组结构：**
1. 🛒 **下单阶段**：客户下单、库存检查
2. 💳 **支付阶段**：支付处理、重试逻辑
3. 📦 **发货阶段**：订单确认、打包发货
4. ✅ **完成阶段**：客户签收、评价反馈

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

**文件：**
- `order-process-layout.mmd`
- `order-process-layout.png`

---

### 4️⃣ Both 模式（完全美化）⭐ 推荐

**改进点：**
- ✅ 专业分组和布局
- ✅ 现代化配色方案
- ✅ 多样化的节点形状
- ✅ 清晰的层次结构
- ✅ 专业的视觉设计

**分组结构（6个）：**
1. 🛒 **下单阶段**：开始、下单、库存检查
2. 📦 **库存处理**：锁定库存、生成订单
3. 💳 **支付阶段**：支付处理、重试逻辑
4. ✅ **订单确认**：确认、通知、打包
5. 🚚 **配送阶段**：配送、等待、签收
6. 🎉 **完成**：完成订单、评价、结束

**颜色方案（专业级）：**
- 🔵 **蓝色渐变**：开始/结束（#667eea）
- 🔷 **天蓝色**：处理步骤（#4facfe）
- 🟣 **粉色**：判断条件（#f093fb）
- 🟢 **绿色**：成功/完成（#11998e）
- 🔴 **红色**：错误/失败（#ff0844）
- 🟠 **橙色**：警告（#ff9f43）

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

**文件：**
- `order-process-both.mmd`
- `order-process-both.png`

---

### 5️⃣ Smart 模式（智能美化）

**智能分析：**
- 🔍 **检测问题**：布局较乱，样式单一
- 🎯 **决策**：使用both策略，重点优化布局和分组
- ⚡ **执行**：针对性美化

**改进点：**
- ✅ 智能分组（5个阶段）
- ✅ 专业配色方案
- ✅ 清晰的层次结构
- ✅ 针对性优化

**分组结构（5个）：**
1. 🛒 **下单**：绿色背景，清晰标识
2. 📦 **库存**：蓝色背景，库存相关
3. 💳 **支付**：黄色背景，支付流程
4. 📦 **发货**：紫色背景，物流阶段
5. ✅ **完成**：绿色背景，订单完成

**适用场景：**
- 不确定需要什么模式
- 希望AI自动判断
- 快速获得最佳结果

**效果：**
```
输入：任何流程图
输出：AI分析后，针对性优化
```

**文件：**
- `order-process-smart.mmd`
- `order-process-smart.png`

---

## 📊 效果对比表

| 特性 | 原始 | Style | Layout | Both | Smart |
|------|------|-------|--------|------|-------|
| **布局** | 混乱 | 保持 | 优化 | 优化 | 智能 |
| **颜色** | 单一 | 专业 | 保持 | 专业 | 智能 |
| **形状** | 简单 | 区分 | 保持 | 区分 | 智能 |
| **分组** | 无 | 无 | ✅ | ✅ | ✅ |
| **层次** | 模糊 | 模糊 | 清晰 | 清晰 | 清晰 |
| **专业度** | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **速度** | - | ⚡ 快 | ⚡ 快 | 🐢 慢 | ⚡ 中 |

---

## 🎯 选择建议

### 选择 Style 模式，如果：

- ✅ 布局已经很满意
- ✅ 只想提升视觉效果
- ✅ 保持原有的阅读习惯
- ✅ 时间紧迫，需要快速美化

**命令：**
```bash
/beautify-flowchart order-process.png --mode style
```

---

### 选择 Layout 模式，如果：

- ✅ 节点位置混乱
- ✅ 连接线交叉严重
- ✅ 需要更清晰的层次
- ✅ 对原有颜色满意

**命令：**
```bash
/beautify-flowchart order-process.png --mode layout
```

---

### 选择 Both 模式，如果：

- ✅ 需要专业级呈现
- ✅ 用于正式文档或演示
- ✅ 追求最佳视觉效果
- ✅ 原图需要全面升级

**命令：**
```bash
/beautify-flowchart order-process.png --mode both --theme modern
```

---

### 选择 Smart 模式，如果：

- ✅ 不确定需要什么模式
- ✅ 希望AI自动判断
- ✅ 快速获得最佳结果
- ✅ 首次使用，想看看效果

**命令：**
```bash
/beautify-flowchart order-process.png --mode smart
```

---

## 💡 使用技巧

### 1. 先用smart试水

```bash
# 先用smart模式看看效果
/beautify-flowchart order-process.png --mode smart

# 如果不满意，再用both模式
/beautify-flowchart order-process.png --mode both
```

### 2. 批量处理

```bash
# 处理目录下所有PNG文件
for file in *.png; do
    /beautify-flowchart "$file" --mode smart
done
```

### 3. 保留原文件

输出文件会自动命名为 `原文件名_beautified.png`，不会覆盖原文件。

### 4. 查看效果

执行后会自动显示美化后的图片，可以直接预览效果。

---

## 📋 参数参考

| 参数 | 说明 | 默认值 | 可选值 |
|------|------|--------|--------|
| `--mode` | 美化模式 | `smart` | `style`, `layout`, `both`, `smart` |
| `--theme` | 颜色主题 | `default` | `default`, `dark`, `colorful`, `minimal`, `business`, `modern` |
| `--direction` | 布局方向 | `auto` | `auto`, `TD`, `LR`, `TB`, `RL` |
| `--width` | 输出宽度 | `auto` | 任意数字 |
| `--height` | 输出高度 | `auto` | 任意数字 |
| `--scale` | 缩放比例 | `1` | `1`, `2`, `3`, `4` |
| `--background` | 背景色 | `transparent` | `transparent`, `white`, `black`, 颜色代码 |

---

## 🎨 自定义配置

### 修改颜色主题

编辑 `mermaid-config.json` 文件：

```json
{
  "themeVariables": {
    "primaryColor": "#your-color",
    "primaryTextColor": "#ffffff",
    "lineColor": "#your-line-color"
  }
}
```

### 修改节点样式

在 `.mmd` 文件中修改 `classDef`：

```mermaid
classDef yourClass fill:#your-color,stroke:#your-border,stroke-width:2px,color:#fff
```

---

## 🚀 快速开始

```bash
# 最简单的方式
/beautify-flowchart 你的订单流程图.png

# 指定模式
/beautify-flowchart 你的订单流程图.png --mode smart

# 完整参数
/beautify-flowchart 你的订单流程图.png \
    --mode both \
    --theme modern \
    --scale 2 \
    --width 1920
```

---

## 📚 更多示例

查看其他示例文件：

```bash
# 查看更多示例
ls ~/.claude/skills/beautify-flowchart/examples/

# 查看示例说明
cat ~/.claude/skills/beautify-flowchart/examples/README.md
```

---

## 🎉 总结

通过这个订单处理流程的演示，你可以看到四种模式的不同效果：

- **Style**：快速美化，保持原样
- **Layout**：优化结构，清晰分组
- **Both**：专业设计，全面升级
- **Smart**：智能分析，针对性优化

**推荐使用：**
```bash
# 最佳效果
/beautify-flowchart 你的流程图.png --mode both --theme modern

# 最简单
/beautify-flowchart 你的流程图.png --mode smart
```

**享受美化流程图的乐趣！** 🎨✨

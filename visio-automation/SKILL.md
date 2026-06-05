---
name: visio-automation
description: 通过 Python win32com 脚本直接操控 Microsoft Visio 画图、修改、读取、导出。可在 Visio 中创建流程图、调整布局样式、从截图重建可编辑 Visio 文件。
metadata:
  version: "1.0.0"
  requires: [win32com, visio-installed]
---

# visio-automation

通过 Python `win32com` COM 接口直接操控本机 Microsoft Visio 应用程序。

## 前置条件

- Windows 系统（已满足）
- Microsoft Visio 已安装（已检测到 Office16 Visio）
- Python + `pywin32` 已安装（已满足）

核心脚本位于同目录 `visio_automation.py`，所有 Visio 操作通过该脚本完成。

---

## 一、能力范围

### ✅ 支持的操作

| 操作 | 说明 |
|------|------|
| **新建文档** | 创建空白 Visio 文档，可选 US Units / Metric |
| **添加形状** | 矩形、圆角矩形、菱形（判断）、圆形/椭圆、平行四边形、泳道/分隔条 |
| **添加文字** | 为任意形状设置文本 |
| **连线** | 在两个形状间创建带箭头的连线，支持直线/直角折线/曲线 |
| **样式设置** | 填充色、线条色、线宽、圆角、字体、字号、粗体、对齐 |
| **布局摆放** | 设置形状的 x/y 坐标和宽高 |
| **读取文档** | 遍历已有 Visio 文档的所有形状、文字、连线、位置 |
| **导出** | 导出为 PNG / SVG / PDF |
| **删除形状** | 删除指定形状 |
| **页面管理** | 重命名页面、添加页面、切换页面 |

### ❌ 不支持的操作

- Visio 未安装时无法工作
- 无法操控 Visio 之外的其他 Office 应用
- Mac 版 Visio（COM 接口不同）

---

## 二、使用方式

### 核心脚本

```
python C:\Users\12286\.claude\skills\visio-automation\visio_automation.py <command> [options]
```

### 命令列表

| 命令 | 说明 |
|------|------|
| `create` | 创建新 Visio 文档 |
| `add-shapes` | 批量添加形状（从 JSON 描述） |
| `add-connectors` | 批量添加连线（从 JSON 描述） |
| `read` | 读取当前文档的结构 |
| `apply-style` | 对已有文档应用样式 |
| `export` | 导出为 PNG/SVG/PDF |
| `from-description` | 从自然语言描述生成流程图 |

### 交互模式

脚本也支持作为 Python 模块导入，在交互式会话中逐步操控 Visio：

```python
from visio_automation import VisioController

v = VisioController()
v.connect()
v.new_document()
v.add_box(100, 100, 200, 80, text="开始")
v.add_diamond(100, 250, 200, 100, text="条件判断?")
v.connect("Sheet.1", "Sheet.2", label="是")
v.export_png("output.png")
v.disconnect()
```

---

## 三、强制流程

当用户要求"在 Visio 中画图"、"用 Visio 做流程图"时，按以下步骤执行：

### 第 1 步：确认需求

向用户确认：
- 要画什么类型的图（流程图、组织架构图、泳道图、网络拓扑等）
- 大致有多少节点
- 是否有参考图（截图/手绘）

### 第 2 步：结构化描述

将用户需求转化为结构化描述，包含：
- 节点列表（类型、文字、位置关系）
- 连线关系（起点 → 终点，条件标签）
- 样式偏好（颜色、字体大小）

### 第 3 步：生成 Python 脚本

根据结构化描述，生成调用 `visio_automation.py` 的 Python 脚本，或直接使用交互模式。

### 第 4 步：执行并在 Visio 中创建

运行脚本，在 Visio 中生成图表。执行后：
- 如果用户满意，保存为 `.vsdx` 文件
- 如果用户要调整，在已有基础上修改

### 第 5 步：保存/导出

按用户需求保存为 `.vsdx` 和/或导出为 PNG。

---

## 四、与 beautify-flowchart 的集成

当 `beautify-flowchart` skill 走"可编辑重建"路线时，新增 **Visio 格式** 作为输出选项。

优先级更新为：
1. `draw.io`
2. **`Visio (.vsdx)`** ← 新增
3. `PPT`
4. `SVG`

当用户说"在我的 Visio 里画"、"直接给我 Visio 文件"、"在我本机画"时，走 Visio 路线。

---

## 五、形状类型参考

| 类型 | Visio Master | 用途 |
|------|-------------|------|
| `box` | Rectangle (Basic Shapes) | 普通流程节点 |
| `rounded_box` | Rounded Rectangle | 开始/结束 |
| `diamond` | Diamond (Basic Shapes) | 判断/条件 |
| `parallelogram` | Parallelogram | 数据输入/输出 |
| `circle` | Circle | 连接点 |
| `swimlane` | Swimlane (Cross-Functional) | 泳道 |
| `separator` | Separator | 泳道分隔线 |
| `text_block` | Text Block | 纯文本标注 |

## 六、样式预设

| 预设名 | 用途 |
|--------|------|
| `default` | 简洁蓝白风，适合技术文档 |
| `corporate` | 深蓝商务风，适合汇报 |
| `modern` | 扁平彩色风，适合演示 |
| `minimal` | 极简黑白风，适合打印 |

## 七、注意事项

1. **COM 连接会打开 Visio 窗口**：默认 Visible=True，用户可以看到画图过程
2. **首次连接可能较慢**：Visio 启动需要时间，耐心等待
3. **不要手动操作**：脚本运行时不要同时在 Visio 中手动拖拽
4. **保存前确认**：保存会覆盖已有文件，先确认再保存
5. **关闭 Visio**：用完记得调用 `disconnect()` 或在脚本中 `Quit()`

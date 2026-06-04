---
name: beautify-flowchart
description: 美化或重建流程图。强制采用“先提取原图表达，再确认约束，最后执行绘制/美化”的流程，避免在布局、文案、可编辑性上跑偏。
metadata:
  version: "2.1.0"
---

# beautify-flowchart

这个 skill 处理两类任务：

1. **图片美化**：在原图基础上优化视觉效果
2. **可编辑重建**：重建为 `draw.io` / `PPT` / `SVG` 等可编辑源文件

这两类任务不能混做，必须先判断。

## 核心原则

**先提取原图表达清楚，再根据文字与约束去画图。**

禁止跳过“原图提取”直接开始重画或美化。

## 一、强制执行流程

每次都必须按下面顺序执行：

### 第 1 步：提取原图内容

先从原图中提取这些内容，并在内部形成清单：

1. 分区/泳道结构
2. 节点列表
3. 判断节点列表
4. 连线关系
5. 每个节点的文字
6. 原图中已有的颜色语义
7. 大致布局关系（上下、左右、分组）

如果图中文字较小、模糊、遮挡，必须标记为：

- **可确认**
- **大概率如此**
- **无法确认**

### 第 2 步：先输出“提取结果”

在真正绘图或美化前，优先给出一份结构化提取结果。格式建议如下：

- 分区：
  - 分区 A：……
  - 分区 B：……
- 节点：
  - 节点 1：……
  - 节点 2：……
- 判断关系：
  - A -> B
  - B -(是)-> C
  - B -(否)-> D
- 不确定项：
  - 某节点文字不清
  - 某条线终点不确定

如果用户强调准确性，先以这份提取结果为准，再进入下一步。

### 第 3 步：读取用户约束

必须提取以下约束：

1. 是否要求 **布局完全一致**
2. 是否要求 **文字完全一致**
3. 是否要求 **可编辑**
4. 最终交付物是 **PNG** 还是 **源文件**
5. 用户是要：
   - 只美化
   - 重建
   - 先美化再重建

### 第 4 步：选择执行路线

#### 路线 A：图片美化

适用条件：

- 用户说“美化”
- 用户说“布局别动”
- 用户只要图片
- 用户不强调后续频繁改字

#### 路线 B：可编辑重建

适用条件：

- 用户说“可编辑”
- 用户说“后面还要改字”
- 用户要 `draw.io` / `PPT`
- 原图截图质量差，继续修图意义不大

### 第 5 步：选择模式

#### `style`

只允许修改：

- 颜色
- 字体
- 线宽
- 圆角
- 内边距
- 阴影/描边

禁止修改：

- 节点位置
- 分区结构
- 箭头走向
- 阅读顺序
- 逻辑分组

如果用户说“布局完全一致”，必须使用 `style`，或把 `smart` 强制降级为 `style`。

#### `layout`

只优化：

- 位置
- 对齐
- 间距
- 连线绕行

尽量不动：

- 文案
- 颜色语义
- 节点类别

#### `both`

同时优化布局和样式。

#### `smart`

先分析后自动选模式。

但如用户要求“布局完全一致”，必须降级为 `style`。

### 第 6 步：执行

#### 6A. 图片美化

若走 `style`：

1. 保留原布局
2. 保留原箭头关系
3. 保留原分区结构
4. 只统一视觉风格

执行后必须明确说明：

- 这是图片编辑，不是源文件重建
- 后续改字仍然不方便

#### 6B. 可编辑重建

若走可编辑重建，必须按顺序：

1. 先建分区/泳道
2. 再建节点
3. 再建判断节点
4. 再连线
5. 最后填充文字
6. 最后再统一样式

不要一开始就大量填字、再反过来补结构。

推荐格式优先级：

1. `draw.io`
2. `PPT`
3. `SVG`

## 二、验收标准

### 对图片美化结果

必须检查：

- `style` 模式下，布局是否没变
- 箭头关系是否一致
- 分区是否保留
- 颜色语义是否一致
- 是否有错位、遮挡、重叠

### 对可编辑重建结果

必须检查：

- 文件是否能正常打开
- 所有框是否可编辑
- 文本是否可双击修改
- 连线是否可单独拖动
- 结构是否与原图一致

## 三、禁止事项

### 在 `style` 模式下禁止

- 重新布局
- 擅自拉开节点间距
- 改变箭头走向
- 改变阅读顺序

### 在可编辑重建时禁止

- 把“重建”伪装成“修图”
- 未说明误差就声称“完全一致”
- 在文字不清时擅自编造业务文案

## 四、推荐输出方式

### 当用户要准确复刻

先给出：

1. 原图提取结果
2. 不确定项
3. 计划采用的路线（style / draw.io / PPT）

然后再开始执行。

### 当用户要可编辑版本

应该明确说：

> 这次不是继续修图片，而是先提取原图结构与文案，再按该结构重建可编辑源文件。

### 当用户要“布局完全一致”

应该明确说：

> 这次按 `style` 模式处理：布局不动，只改视觉样式。

## 五、正确策略示例

### 场景 1：用户说“布局完全一致，做美化”

执行：

1. 提取原图结构
2. 输出提取摘要
3. 走 `style`
4. 只改样式

### 场景 2：用户说“我要能改字”

执行：

1. 提取原图结构与文案
2. 标出不确定文字
3. 走可编辑重建
4. 优先输出 `draw.io`

### 场景 3：用户说“先美化，再给我可编辑版本”

执行：

1. 先提取原图
2. 输出结构摘要
3. 做一版 `style` 图片美化
4. 再做一版 `draw.io` 重建
5. 明确告诉用户这是两份不同交付物

## 六、底线

如果用户真实目标是“后面还要继续改”，只给图片通常不是正确答案。

如果用户真实目标是“原图别动，只是更专业”，那就不应该擅自重排布局。
## Visio output integration

When the user asks to use Visio, export to Visio, generate a `.vsdx`, or control Visio as part of a flowchart task, include Visio as an optional final delivery target after the normal flowchart extraction and beautification workflow.

For concrete Visio COM execution steps and script patterns, read `references/visio-automation.md` before generating or running the renderer.

Preferred workflow:

1. Extract the source article, diagram, or description into a normalized flow structure: nodes, edges, decision points, groups, labels, and layout hints.
2. Produce an editable intermediate representation first, preferably Mermaid flowchart source and a concise node/edge table.
3. For Visio delivery, prefer a declarative JSON diagram spec over handwritten one-off PowerShell/VBScript coordinates. The JSON should contain pages, nodes, connections, styles, and layout metadata.
4. Render the JSON through a reusable Visio COM renderer when available. A proven pattern is the `deermiya/visio-skill` approach: create JSON first, then run a Python `pywin32` renderer such as `New-VisioDiagram.py` to generate `.vsdx`.
5. If no reusable renderer is installed, generate a minimal Python/PowerShell renderer from the same JSON spec instead of embedding all diagram logic directly in the script.
6. If direct script execution is unavailable in the current Codex session, still provide the generated JSON/spec/script and clear local run instructions. Do not claim the Visio file was created unless the script actually ran successfully.
7. When possible, also export or request an export preview as PNG/PDF/SVG so the user can visually verify the result.

Recommended JSON spec pattern, adapted from `deermiya/visio-skill`:

- Top level: `title`, `pageWidth`, `pageHeight`, and `pages`.
- Page: `name`, `nodes`, `connections`, and optional `lines` / `labels`.
- Node: stable `id`, `text`, `shape`, `x`, `y`, `w`, `h`, `fill`, `line`, `fontName`, `fontSize`.
- Connection: `from`, `to`, `text`, `line`, `fontName`, `fontSize`, `textPinX`, `textOffsetY`, `endArrow`.
- Use Visio inches as coordinates; record whether coordinates are lower-left or center-based and keep one convention throughout.

Visio automation requirements:

- Use basic shapes for flowcharts by default: `roundrect`, `rectangle`, `ellipse`, and `diamond`. Do not load professional icon stencils unless the user explicitly asks for icons, network devices, cloud services, or infrastructure diagrams.
- Map process nodes to rectangles, decisions to diamonds, start/end nodes to terminators, data/input-output nodes to parallelograms, and connectors to dynamic connectors with arrowheads.
- Keep layout deterministic and readable: top-to-bottom by default, left-to-right when the article describes pipeline, timeline, or architecture flow.
- Preserve Chinese text exactly when the source article is Chinese.
- Keep the generated script self-contained and save outputs under the user workspace unless the user specifies another path.
- Use `Microsoft YaHei` for Chinese diagrams, typically 10-11 pt for nodes and 9-10 pt for connector labels.
- Leave at least 0.6-1.0 inch between shapes. For labeled horizontal connectors, leave at least `max(1.4 in, label characters * 0.12 in)` plus arrowhead room.
- Keep connector labels away from arrowheads with label offsets such as `textPinX` and `textOffsetY` when the renderer supports them.

Suggested deliverables when Visio is requested:

- `flowchart.mmd`: Mermaid source for review and fallback rendering.
- `flowchart.json`: declarative Visio diagram spec for repeatable rendering and future edits.
- `create_visio_flowchart.ps1` or `create_visio_flowchart.vbs`: Visio automation script.
- `flowchart.vsdx`: created only when automation runs successfully.
- Optional preview export such as `flowchart.png` or `flowchart.pdf`.

## Image-to-Visio reconstruction

When the user provides a raster diagram screenshot or scanned flowchart and asks for an editable Visio reconstruction, prefer a two-pass reconstruction workflow inspired by `deermiya/visio-skill`:

1. Crop away unrelated UI chrome, black margins, viewer buttons, and phone screenshot borders before reconstruction.
2. Run or emulate fast geometry reconstruction: detect rectangles, rounded rectangles, diamonds, long horizontal/vertical lines, table/swimlane grids, and sampled colors.
3. Generate a preview and JSON output before final `.vsdx`.
4. For text-heavy or visually complex diagrams, add a small annotation overlay for labels, semantic connections, and corrected shapes rather than hand-redrawing every detected element.
5. Regenerate from the corrected JSON/overlay and inspect the preview.

If OpenCV-based reconstruction tooling is available, use it first. If not, manually create the same style of reconstruction JSON and keep all coordinates editable and traceable.

## Visio quality mode

When a user asks for a Visio redraw that should be usable and visually polished, do not generate one large coordinate-dense diagram on the first pass. Use this quality workflow instead:

1. Re-structure before drawing. If the source flowchart has more than 18 nodes, split it into a main overview plus sub-flow pages, or into clearly separated swimlanes with no more than 12-16 nodes per lane.
2. Prefer semantic grouping over exact screenshot copying. Preserve the business logic, but simplify duplicated status-update chains, repeated counters, and long exception branches into named sub-process boxes when that improves readability.
3. Use true Visio masters when possible: Process, Decision, Start/End, Data, Document, and Dynamic Connector. Do not simulate a decision by rotating a rectangle unless no stencil is available.
4. Use orthogonal connectors only. Avoid diagonal lines, avoid connector labels crossing nodes, and route every connector through clear horizontal/vertical segments.
5. Keep branch directions consistent: main path left-to-right or top-to-bottom; success/continue branches follow the main direction; reject/stop/exception branches exit to the side.
6. Keep text readable: short node titles, 9-11 pt body text, wrapped lines, no rotated text except vertical swimlane headers.
7. Use restrained status colors:
   - red or pink for entry/SDK/external trigger nodes
   - blue/gray for normal processing
   - amber for decisions
   - green for terminal or positive outcome nodes
8. Leave whitespace. A diagram that uses less than 70% of the page area is usually better than one that fills every gap.
9. Generate a preview export and inspect it. If connectors overlap nodes, diamonds rotate text awkwardly, labels collide, or nodes feel cramped, revise the layout before delivering.

Recommended Visio redesign pattern for complex article/screenshot flows:

- Page 1: high-level overview with 6-10 nodes.
- Page 2+: detailed subflows for each major branch.
- Optional appendix page: full node/edge table for traceability.

Quality gate before final answer:

- No diagonal connectors unless explicitly requested.
- No line crosses through a node.
- No connector label overlaps a node or another label.
- No text is rotated inside process or decision shapes.
- Every decision has clearly labeled outgoing branches.
- Every page has a title, consistent margins, and aligned columns/rows.

## Lessons learned for fast Visio success

For future Visio redraws, use these hard-earned defaults to succeed on the first or second pass:

1. Preserve layout by preserving coordinates, not by using Visio auto-layout. Auto-layout is too unpredictable for screenshot reconstruction.
2. Use a JSON spec as the source of truth. Keep node text, shape type, x/y/w/h, style, and connectors separate from the renderer script.
3. Draw decision diamonds as real polygons, not rotated rectangles. Rotated rectangles rotate or distort text and quickly make the diagram unreadable.
4. Use manual orthogonal line segments instead of Visio dynamic connectors when the user asks to keep the original layout. Dynamic connectors may reroute through nodes or create unexpected diagonals.
5. Export `.vsdx` first. PNG/PDF export may hang or prompt in Visio; do not block the main deliverable on preview export.
6. Use UTF-8 script loading on Windows PowerShell for Chinese diagrams:
   `Get-Content -Encoding UTF8 -Raw script.ps1 | Invoke-Expression`
7. Avoid PowerShell array-return pitfalls in geometry helpers. Return coordinate points as objects like `{ X, Y }`, and compute halves as explicit scalar doubles before arithmetic.
8. If an old script or output file is locked by Visio, create a new script/output filename instead of trying to delete or overwrite it.
9. Keep the first render conservative: same layout, cleaner shapes, readable fonts, restrained colors. Improve aesthetics after the diagram is structurally correct.
10. Treat preview inspection as a separate QA step. If preview export fails but `.vsdx` opens correctly, deliver `.vsdx` and note the preview limitation.

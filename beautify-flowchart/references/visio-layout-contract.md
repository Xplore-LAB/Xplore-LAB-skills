# Visio Layout Contract

Use this reference whenever the user asks for a polished Visio redraw, publication-style diagram, or a flowchart that must not have tangled connectors.

## Core Rule

Do not render directly from a loose graph. Always create a layout contract before drawing.

Baseline usability comes before aesthetics. A diagram is not acceptable just because it is colorful or visually styled. It must first satisfy flowchart readability rules: aligned nodes, orthogonal connectors, clear branching, no crossed lines, no label collisions, and no false process logic.

Required pipeline:

1. `semantic_graph`: validate process logic.
2. `layout_contract`: fix phases, node positions, connector channels, and feedback routes.
3. `style_contract`: choose fonts, colors, line weights, and node styles.
4. `visio_render`: use Visio only to execute the approved layout.
5. `qa_pass`: inspect connector crossings, overlaps, labels, and logical consistency.

## Layout Contract Schema

A layout contract should contain:

```json
{
  "canvas": {
    "width": 14,
    "height": 8.8,
    "margin": 0.45,
    "background": "F2EFE8"
  },
  "typography": {
    "fontFamily": "Microsoft YaHei",
    "titleSize": 17,
    "sectionSize": 9.5,
    "nodeSize": 9.5,
    "labelSize": 7.8
  },
  "sections": [
    {"id": "input", "title": "输入来源", "left": 0.75, "right": 3.20},
    {"id": "semantic", "title": "语义建模", "left": 3.45, "right": 6.25},
    {"id": "strategy", "title": "模式策略", "left": 6.50, "right": 10.05},
    {"id": "delivery", "title": "交付校验", "left": 10.30, "right": 13.25}
  ],
  "nodes": [
    {"id": "parse", "section": "semantic", "x": 4.85, "y": 6.10, "w": 1.58, "h": 0.46}
  ],
  "channels": [
    {"id": "main", "type": "horizontal", "y": 5.95},
    {"id": "feedback", "type": "bottom-loop", "y": 1.55}
  ],
  "edges": [
    {"from": "parse", "to": "graph", "route": ["B", "T"], "channel": "main"}
  ]
}
```

## Fixed Pattern: Skill Workflow Diagram

Use this pattern for explaining how a skill works.

Main claim:

> Logic is validated before visual styling; Visio executes an approved layout.

Sections:

1. `输入来源`
2. `语义建模`
3. `模式策略`
4. `交付校验`

Recommended positions on a 14 in x 8.8 in canvas:

| Node | X | Y | Meaning |
|---|---:|---:|---|
| input image | 1.98 | 6.25 | screenshot input |
| input text | 1.98 | 5.45 | article/text input |
| input mermaid | 1.98 | 4.65 | Mermaid input |
| parse | 4.85 | 6.10 | parse expression |
| graph | 4.85 | 4.75 | semantic graph |
| logic QA | 4.85 | 3.28 | logic validation |
| logic fix | 4.85 | 2.05 | fix semantic graph |
| mode selector | 7.55 | 5.95 | choose mode |
| mode group | 7.55 | 4.50 | grouped strategy choices |
| layout spec | 7.55 | 2.80 | layout + style contract |
| preview output | 11.80 | 5.90 | Mermaid/PNG optional |
| Visio renderer | 11.80 | 4.78 | Visio COM action |
| VSDX output | 11.80 | 3.68 | editable file |
| visual QA | 11.80 | 2.52 | final QA |
| visual fix | 10.40 | 1.68 | fix layout/lines |
| final | 12.70 | 1.68 | final delivery |

Important:

- Draw the four modes inside one grouped card instead of drawing four separate long routes.
- The grouped strategy card has one outgoing arrow to `layout spec`.
- `style preset` is a small note attached to `layout spec`, not a main-process node.
- `Mermaid/PNG` is optional and branches from `layout spec`.
- `Visio renderer` branches from `layout spec`, then produces `.vsdx`.
- `visual QA` failure loops back to `layout spec`, not to raw input or mode selection.

## Connector Channel Rules

Use fixed connector channels instead of shortest-path routing.

- `input_to_parse`: vertical bus at x=3.05. All inputs merge into this bus, then enter parse.
- `semantic_main`: vertical path from parse -> graph -> logic QA.
- `semantic_feedback`: dashed red loop from logic fix back to semantic graph.
- `strategy_entry`: one green arrow from logic QA pass to mode selector.
- `strategy_group`: all modes stay inside a group; do not route each mode separately across the canvas.
- `delivery_split`: two routes from layout spec:
  - upper optional route to Mermaid/PNG preview
  - lower Visio route to Visio COM renderer
- `visual_feedback`: dashed red loop from visual fix back to layout spec.

Failure loops should run below the main flow, never through the center.

## Zero-Diagonal Rule

For standard business, technical, academic, and Visio flowcharts, diagonal connectors are forbidden unless the user explicitly asks for a sketch-like or expressive diagram.

Use only:

- horizontal connector segments
- vertical connector segments
- orthogonal elbows
- outside feedback loops
- reserved connector channels

If two nodes are not horizontally or vertically aligned, do not connect them with a diagonal line. Route through a channel:

```text
source -> horizontal segment -> vertical bus -> horizontal segment -> target
```

Diagonal lines are allowed only for intentionally illustrative diagrams, and never for diagrams that need to be read as process documentation.

## Anti-Tangle Rules

- No connector may pass through a node bounding box.
- No connector label may sit on top of a node border.
- No diagonal connector is allowed in standard flowchart mode.
- No more than three connectors may meet at a single visual point.
- Alternatives must be grouped before they merge.
- Feedback loops must be dashed and routed outside the main reading path.
- Optional outputs must be visually secondary.
- If two lines would cross, add a bus/channel or group the source nodes.

## First-Pass Acceptance Standard

Every first generated version must be usable before it is beautiful.

Minimum pass criteria:

1. All nodes are aligned to a visible grid.
2. All main-flow connectors are orthogonal.
3. No connector crosses through a node.
4. No connector label overlaps a node, line, or section title.
5. Feedback loops are routed outside the main path.
6. Branches from decisions or mode selectors are labeled.
7. Repeated alternatives are grouped instead of drawn as tangled individual routes.
8. Font family and font sizes are consistent.
9. The reader can trace the main path in 3 seconds.
10. The process logic is validated before style is applied.

If any criterion fails, revise the layout contract before adding color, icons, shadows, or decorative styling.

## Typography Contract

Default for Chinese Visio diagrams:

- Font family: `Microsoft YaHei`
- Title: 16-18 pt
- Subtitle: 9-10 pt
- Section labels: 9-10 pt
- Node labels: 9-10 pt
- Connector labels: 7.5-8 pt

For academic English-only diagrams:

- Title: `Times New Roman` or `Aptos Display`
- Nodes and labels: `Aptos` or `Arial`

For mixed Chinese/English diagrams, use `Microsoft YaHei` everywhere. Mixed fonts often look inconsistent in Visio.

## Pre-Render Checklist

Before generating Visio:

1. Confirm every node has fixed `x`, `y`, `w`, `h`.
2. Confirm every edge has a channel or explicit route.
3. Confirm strategy alternatives are grouped.
4. Confirm feedback loops return to the correct fixable artifact.
5. Confirm all fonts come from the typography contract.
6. Confirm no direct auto-layout or dynamic connector routing is required.

## Post-Render Checklist

After generating Visio:

1. Trace the main path in 3 seconds.
2. Check all feedback loops are outside the central reading path.
3. Check all labels are readable at 100% zoom.
4. Check no line crosses a node.
5. Check there are no diagonal connectors.
6. Check colors still mean roles, not decoration.
7. If any check fails, revise the layout contract first, then rerender.

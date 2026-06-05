# Editorial Diagram Style

Use this reference when the user wants a diagram that feels calm, warm, publication-ready, blog-style, or "like Anthropic technical blog diagrams".

Inspired by the public `anthropic-diagram` skill by dingtingli, adapted for Visio/flowchart work.

## Core Principle

A good diagram should make one claim obvious, not merely display all information.

Before drawing, decide:

- `main_claim`: what should the reader understand in 3 seconds?
- `primary_pattern`: which visual pattern best supports that claim?
- `reading_direction`: left-to-right, top-to-bottom, outer-to-inner, or loop.
- `semantic_roles`: what each color means.

## Pattern Before Pixels

Choose the structure before choosing colors.

Preferred patterns:

- `linear-workflow`: sequential steps.
- `feedback-loop`: retry, evaluation, refinement, QA cycles.
- `branch-workflow`: decisions, routing, approval gates.
- `split-comparison`: before/after, old/new, option A/B.
- `grouped-architecture`: components inside boundaries.
- `layered-stack`: hierarchy, abstraction layers, dependencies.
- `swimlane-sequence`: multiple actors over time.
- `hub-and-spoke`: one central idea with supporting concepts.
- `parallel-fanout`: multiple workers or branches operating concurrently.
- `callout-annotation`: a main diagram with explanatory notes.

When multiple patterns fit:

1. Prefer the clearest reading order.
2. Prefer the fewest crossing lines.
3. Prefer the pattern that supports the main claim in one glance.
4. Prefer comparison over complicated topology when the message is contrast.
5. Prefer grouped architecture over workflow when containment matters more than time.

For mode-selection diagrams, do not draw every mode as an independent long-flow branch. Put alternatives into a grouped strategy card, then draw one consolidated output edge to the next artifact.

## Editorial Visual Language

- Warm canvas, not pure white: `F2EFE8`, `F7F3EC`, or similar.
- Outer rounded border around the full composition.
- Large centered title.
- No shadows, no gradients, no saturated colors.
- Use whitespace as structure. Do not fill every empty area.
- Use containers sparingly. Do not put every label in a box.
- Keep hierarchy shallow: title, group labels, nodes, optional annotations.
- Use short labels. Avoid paragraph-length node text.

## Semantic Color System

Colors must encode meaning, not decoration.

Suggested Visio role tokens:

| Role | Fill | Stroke | Use |
|---|---|---|---|
| primary | `E6E2DA` | `8C867F` | neutral process, generic component |
| context | `EAF4FB` | `6FA8D6` | files, docs, tools, inputs |
| control | `EEEAF9` | `9A90D6` | router, policy, orchestrator, evaluator |
| start | `F8E9E1` | `D88966` | user input, trigger, external start |
| success | `CFE8D7` | `71AE88` | completed output, accepted result |
| warning | `F3E4DA` | `C88E6A` | retry, reset, caution |
| decision | `E6D7B4` | `BFA777` | branch, filter, approval gate |
| ai | `D7E6DC` | `7FB08F` | LLM/model/agent reasoning step |
| inactive | `EFECE6` | `B4AEA6` | optional, disabled, future, de-emphasized |
| error | `F8DFDA` | `D96B63` | failed, rejected, blocked |

Rules:

- Strokes are darker than fills.
- Most nodes should be neutral/context/control.
- Use at most 3-4 accent roles in one diagram.
- If too many colors appear, collapse low-priority roles into `primary`.

## Connector Rules

- Use open arrowheads when possible. Avoid filled/block triangle arrows for editorial diagrams.
- Prefer rounded orthogonal connectors.
- Keep primary flow visually obvious within 3 seconds.
- Dashed lines mean optional, inferred, retry, override, or exceptional paths.
- Avoid diagonal connectors unless the user explicitly requests an expressive sketch. For normal flowcharts, route all links through orthogonal connector channels.
- Route connectors through reserved channels. Do not let lines cross nodes.

## Visio Adaptation

Visio COM does not provide the same style language as draw.io, so adapt rather than copy:

- Use `DrawRectangle` with `Rounding` for rounded nodes.
- Use pale fills and muted strokes from the semantic color table.
- Use `Microsoft YaHei` for mixed Chinese/English diagrams. Do not mix serif English title fonts with Microsoft YaHei body text unless the user explicitly asks for that editorial contrast.
- Use 1.0-1.4 pt node borders for editorial warmth.
- Use 0.8-1.1 pt connector lines for internal flow.
- Simulate open arrowheads if possible; if Visio arrowhead support is limited, use small simple arrows and keep line color muted.
- Avoid raw auto-routing for final diagrams. Use hand-tuned routes or explicit connector channels.
- Use a layout contract before rendering: sections, fixed node positions, connector channels, and feedback routes.
- Keep the canvas warm by drawing a background rectangle and sending it to back.
- Use outer rounded panel frames to make whitespace feel intentional.

## Quality Checklist

- One main claim is visible from title + layout.
- Reading order is obvious in 3 seconds.
- Pattern choice matches intent.
- No more than one primary diagram pattern unless intentionally combined.
- Outer border/frame exists for editorial diagrams.
- Colors encode roles consistently.
- Whitespace separates groups before extra boxes do.
- No connector crosses through a node.
- No dense line mesh in the center.
- The final file is editable in Visio.

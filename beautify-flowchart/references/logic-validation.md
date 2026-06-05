# Flowchart Logic Validation

Use this reference before finalizing any flowchart, especially when converting a workflow into Visio.

## Principle

Do not validate only the picture. Validate the process model behind the picture.

Every diagram should have a small semantic graph before rendering:

- `nodes`: stable id, label, type, role.
- `edges`: from, to, label, condition, path type.
- `groups`: lanes, phases, or containers.
- `entry`: where the process starts.
- `terminal`: where the process ends.
- `feedback`: retry, repair, or iteration loops.

## Node Type Rules

Use these node types consistently:

- `input`: source material or user request.
- `parse`: extraction, recognition, understanding.
- `decision`: branch point with two or more labeled outcomes.
- `mode`: selectable strategy or operating mode.
- `artifact`: intermediate representation such as JSON, Mermaid, or spec.
- `action`: drawing, rendering, exporting, transforming.
- `qa`: validation/check step.
- `fix`: correction or iteration.
- `output`: final deliverable.

## Edge Rules

- Every non-terminal node should have at least one outgoing edge.
- Every non-entry node should have at least one incoming edge.
- Decision nodes must have at least two outgoing edges, and every outgoing edge must be labeled.
- Mode nodes should not pretend to be sequential steps unless the modes are actually run in sequence.
- Artifact nodes should feed actions, not appear as final business outcomes unless the artifact is the requested output.
- Feedback edges must return to the earliest step that can actually fix the issue.
- Optional outputs should branch from the correct artifact/action, not from unrelated QA nodes.

## Common Logic Errors

- Treating alternatives as a sequence: e.g. Style Mode -> Layout Mode -> Smart Mode, when they are selectable modes.
- Mixing output types and process actions: e.g. `.vsdx` as both an output and a rendering step.
- Feedback loop returns too far or too late: a layout failure should return to layout/spec, not to raw input parsing.
- Quality check placed after final delivery. QA must happen before final delivery.
- JSON spec shown as a final output when the user asked for Visio; it should be intermediate unless explicitly requested.
- Multiple branches merge without explaining why they share the same next step.
- Edge labels describe implementation details rather than branch conditions.

## Validation Checklist

Before rendering:

1. Write one sentence for the main claim of the diagram.
2. List nodes in semantic order.
3. Mark which nodes are alternatives and which are sequential.
4. Mark intermediates versus final outputs.
5. Check all decisions have labeled branches.
6. Check all feedback loops return to a fixable step.
7. Remove edges that are visually convenient but logically false.

After rendering:

1. Trace the main path from entry to final output.
2. Trace every branch and confirm it reaches either an output or a feedback loop.
3. Confirm optional outputs are visually secondary.
4. Confirm colors do not imply false meaning.
5. Confirm the diagram can be explained aloud without contradicting the arrows.

## Recommended Two-Layer Workflow

For complex diagrams:

1. Create a logic graph first.
2. Review the logic graph in plain text or Mermaid.
3. Only then choose the visual style and layout.
4. Render Visio from the validated graph.
5. Run the validation checklist again on the rendered drawing.


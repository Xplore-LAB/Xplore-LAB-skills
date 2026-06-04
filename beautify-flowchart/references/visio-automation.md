# Visio Automation

Use this reference when the user asks to actually draw with Microsoft Visio, generate a `.vsdx`, or says "用 Visio 重画".

## Execution Flow

1. Create a task-specific JSON spec first. Include `title`, `pageWidth`, `pageHeight`, `nodes`, `connectors`, and optional `lanes`.
2. Use PowerShell on Windows because Visio exposes COM automation through `Visio.Application`.
3. Load Chinese scripts as UTF-8:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-Content -Encoding UTF8 -Raw '.\render_visio_flowchart.ps1' | Invoke-Expression"
```

4. Start Visio:

```powershell
$visio = New-Object -ComObject Visio.Application
$visio.Visible = $true
$visio.AlertResponse = 7
$doc = $visio.Documents.Add("")
$page = $visio.ActivePage
```

5. Set page size before drawing:

```powershell
$page.PageSheet.CellsU("PageWidth").FormulaU = "16 in"
$page.PageSheet.CellsU("PageHeight").FormulaU = "10.5 in"
```

6. Draw with explicit coordinates:

- Process nodes: `DrawRectangle(left, bottom, right, top)`.
- Rounded nodes: rectangle plus `Rounding`.
- Decision nodes: polygon/polyline diamond. Do not rotate rectangles.
- Lanes: background rectangles first, then `SendToBack()`.
- Connectors: manual horizontal/vertical `DrawLine()` segments for layout-sensitive diagrams.

7. Save `.vsdx` before exporting previews:

```powershell
$doc.SaveAs($vsdxPath)
```

8. Export PNG/PDF only after the `.vsdx` exists. If export hangs, deliver the `.vsdx`.

## Quality Rules

- Do not claim success unless the `.vsdx` exists and has non-zero size.
- Use JSON as the source of truth, not one-off hardcoded shape logic.
- Use manual orthogonal connectors when preserving screenshot layout.
- Put arrowheads only on final connector segments.
- Add connector labels as transparent text boxes near line midpoints.

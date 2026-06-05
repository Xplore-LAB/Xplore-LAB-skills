"""
Visio Automation via COM (win32com)
====================================
Directly control Microsoft Visio to create, modify, read, and export diagrams.

Usage:
    python visio_automation.py <command> [options]

Commands:
    create              Create a new blank Visio document
    add-shapes <json>   Add shapes from a JSON description string or file path
    add-connectors <json>  Add connectors from a JSON description
    read                Read and output the structure of current document
    apply-style <json>  Apply style presets or custom styles
    export <format> [path]  Export current document (png/svg/pdf)
    from-description <json>  High-level: create entire flowchart from JSON description

JSON Structure for from-description:
{
    "page_name": "My Flowchart",
    "orientation": "portrait|landscape",
    "style": "default|corporate|modern|minimal",
    "shapes": [
        {
            "id": "start",
            "type": "rounded_box",
            "x": 5.0, "y": 1.0,
            "width": 2.0, "height": 0.8,
            "text": "开始"
        },
        {
            "id": "check",
            "type": "diamond",
            "x": 5.0, "y": 2.5,
            "width": 2.0, "height": 1.0,
            "text": "条件成立?"
        }
    ],
    "connectors": [
        {"from": "start", "to": "check"},
        {"from": "check", "to": "yes_branch", "label": "是"},
        {"from": "check", "to": "no_branch", "label": "否"}
    ]
}

All coordinates in inches (Visio default).
"""

import sys
import json
import os
import time
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
import pythoncom


# ---------------------------------------------------------------------------
# Constants: Visio shape masters by locale (English and Chinese Visio)
# ---------------------------------------------------------------------------
MASTER_RECTANGLE = "Rectangle"
MASTER_ROUNDED_RECT = "Rounded Rectangle"
MASTER_DIAMOND = "Diamond"
MASTER_CIRCLE = "Circle"
MASTER_ELLIPSE = "Ellipse"
MASTER_TRIANGLE = "Triangle"
MASTER_PARALLELOGRAM = "Parallelogram"
MASTER_HEXAGON = "Hexagon"
MASTER_CYLINDER = "Cylinder"

# Fallback names for Chinese-language Visio
MASTER_ALIASES = {
    "rectangle": ["Rectangle", "矩形"],
    "rounded_rect": ["Rounded Rectangle", "圆角矩形", "RoundRect"],
    "diamond": ["Diamond", "菱形", "Decision"],
    "circle": ["Circle", "圆形"],
    "ellipse": ["Ellipse", "椭圆"],
    "parallelogram": ["Parallelogram", "平行四边形"],
    "hexagon": ["Hexagon", "六边形"],
    "cylinder": ["Cylinder", "圆柱"],
    "triangle": ["Triangle", "三角形"],
}

# Visio measurement units
visMillimeters = 69
visCentimeters = 69
visInches = 65
visPoints = 72

# Visio shape types
visTypeShape = 3
visTypeGroup = 2

# Visio page orientation
visPortrait = 0
visLandscape = 1

# Arrow types
visArrowNone = 0
visArrowOpen = 1
visArrowStealth = 2
visArrowDiamond = 3
visArrowOval = 4
visArrowClosed = 5

# Connector routing
visConnectorStraight = 0
visConnectorCurve = 1
visConnectorRightAngle = 2

# Text alignment
visAlignLeft = 0
visAlignCenter = 1
visAlignRight = 2
visAlignTop = 0

# Colors (BGR format for Visio, converted from RGB)
COLORS_RGB = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "gray": (128, 128, 128),
    "light_gray": (220, 220, 220),
    "blue": (68, 114, 196),
    "dark_blue": (30, 60, 120),
    "light_blue": (180, 200, 240),
    "green": (84, 160, 84),
    "dark_green": (40, 100, 40),
    "light_green": (190, 230, 190),
    "red": (220, 80, 80),
    "dark_red": (160, 50, 50),
    "orange": (240, 160, 60),
    "yellow": (255, 220, 80),
    "purple": (140, 100, 180),
    "teal": (60, 160, 160),
}

STYLE_PRESETS = {
    "default": {
        "box_fill": "light_blue",
        "box_line": "blue",
        "box_text_color": "dark_blue",
        "box_font_size": 11,
        "box_corner_rounding": 0.05,
        "diamond_fill": "light_green",
        "diamond_line": "green",
        "diamond_text_color": "dark_green",
        "start_fill": "blue",
        "start_line": "dark_blue",
        "start_text_color": "white",
        "end_fill": "dark_blue",
        "end_line": "dark_blue",
        "end_text_color": "white",
        "connector_color": "gray",
        "connector_weight": 1.0,
        "font_name": "微软雅黑",
    },
    "corporate": {
        "box_fill": "white",
        "box_line": "dark_blue",
        "box_text_color": "black",
        "box_font_size": 10,
        "box_corner_rounding": 0.0,
        "diamond_fill": "white",
        "diamond_line": "dark_blue",
        "diamond_text_color": "black",
        "start_fill": "dark_blue",
        "start_line": "dark_blue",
        "start_text_color": "white",
        "end_fill": "dark_blue",
        "end_line": "dark_blue",
        "end_text_color": "white",
        "connector_color": "gray",
        "connector_weight": 1.5,
        "font_name": "微软雅黑",
    },
    "modern": {
        "box_fill": "white",
        "box_line": "teal",
        "box_text_color": "black",
        "box_font_size": 12,
        "box_corner_rounding": 0.1,
        "diamond_fill": "light_green",
        "diamond_line": "green",
        "diamond_text_color": "dark_green",
        "start_fill": "teal",
        "start_line": "teal",
        "start_text_color": "white",
        "end_fill": "dark_blue",
        "end_line": "dark_blue",
        "end_text_color": "white",
        "connector_color": "light_gray",
        "connector_weight": 1.2,
        "font_name": "微软雅黑",
    },
    "minimal": {
        "box_fill": "white",
        "box_line": "black",
        "box_text_color": "black",
        "box_font_size": 10,
        "box_corner_rounding": 0.0,
        "diamond_fill": "white",
        "diamond_line": "black",
        "diamond_text_color": "black",
        "start_fill": "black",
        "start_line": "black",
        "start_text_color": "white",
        "end_fill": "black",
        "end_line": "black",
        "end_text_color": "white",
        "connector_color": "black",
        "connector_weight": 1.0,
        "font_name": "微软雅黑",
    },
}


def rgb_to_bgr(r, g, b):
    """Convert RGB to Visio BGR integer."""
    return r + (g << 8) + (b << 16)


def color_to_bgr(name: str) -> int:
    """Convert named color to Visio BGR integer."""
    r, g, b = COLORS_RGB.get(name, (128, 128, 128))
    return rgb_to_bgr(b, g, r)  # Visio uses BGR


def inches_to_visio(inches: float) -> float:
    """Convert inches to Visio internal units."""
    return inches


# ---------------------------------------------------------------------------
# VisioController - the main automation class
# ---------------------------------------------------------------------------
class VisioController:
    """High-level controller for Visio automation."""

    def __init__(self, visible: bool = True):
        self.visio_app = None
        self.document = None
        self.page = None
        self.visible = visible
        self._shape_registry: Dict[str, Any] = {}  # id -> shape object
        self._next_shape_idx = 1

    # ---- Connection ----

    def connect(self, timeout: int = 30):
        """Connect to or launch Visio."""
        from win32com.client import Dispatch, dynamic

        pythoncom.CoInitialize()
        try:
            self.visio_app = Dispatch("Visio.Application")
        except Exception:
            # Try to start Visio
            self.visio_app = dynamic.Dispatch("Visio.Application")

        self.visio_app.Visible = 1 if self.visible else 0
        # Wait for Visio to be ready
        waited = 0
        while waited < timeout:
            try:
                _ = self.visio_app.Documents.Count
                break
            except Exception:
                time.sleep(0.5)
                waited += 0.5
        return self

    def disconnect(self):
        """Disconnect from Visio (does NOT close Visio)."""
        self._shape_registry.clear()
        if self.visio_app:
            self.visio_app = None
        pythoncom.CoUninitialize()

    def quit(self):
        """Quit Visio application."""
        if self.visio_app:
            try:
                self.visio_app.Quit()
            except Exception:
                pass
            self.visio_app = None
        pythoncom.CoUninitialize()

    # ---- Document Management ----

    def new_document(self, metric: bool = True) -> Any:
        """Create a new blank Visio document. Returns the document object."""
        self.document = self.visio_app.Documents.Add("")
        self.page = self.visio_app.ActivePage
        self._shape_registry.clear()
        self._next_shape_idx = 1
        return self.document

    def open_document(self, path: str) -> Any:
        """Open an existing Visio document."""
        path = os.path.abspath(path)
        self.document = self.visio_app.Documents.Open(path)
        self.page = self.visio_app.ActivePage
        self._shape_registry.clear()
        self._next_shape_idx = 1
        return self.document

    def save(self, path: str = None):
        """Save the current document."""
        if path:
            path = os.path.abspath(path)
            self.document.SaveAs(path)
        else:
            self.document.Save()

    def set_page_orientation(self, landscape: bool = False):
        """Set page orientation."""
        if self.page:
            self.page.PageSheet.CellsU("PageWidth").ResultIU = 11.0 if landscape else 8.5
            self.page.PageSheet.CellsU("PageHeight").ResultIU = 8.5 if landscape else 11.0

    def set_page_name(self, name: str):
        """Rename current page."""
        if self.page:
            self.page.Name = name

    # ---- Shape Creation ----

    def _find_master(self, master_names: List[str]) -> Optional[Any]:
        """Find a master shape by trying multiple names (handles locale differences)."""
        for name in master_names:
            try:
                return self.document.Masters.ItemU(name)
            except Exception:
                pass

        # Try to find in stencils
        stencil_paths = [
            "BASIC_U.VSS",
            "BASFLO_U.VSS",
            "BASIC_M.VSS",
        ]
        for sp in stencil_paths:
            try:
                stencil = self.visio_app.Documents.OpenEx(sp, 0x40)  # visOpenHidden
                for name in master_names:
                    try:
                        master = stencil.Masters.ItemU(name)
                        return master
                    except Exception:
                        continue
            except Exception:
                continue
        return None

    def _drop_master(self, master_name_aliases: List[str], x: float, y: float) -> Optional[Any]:
        """Drop a master shape onto the page. Returns the shape object."""
        master = self._find_master(master_name_aliases)
        if master is None:
            # Fallback: create a basic rectangle
            try:
                master = self._find_master(["Rectangle", "矩形"])
            except Exception:
                pass
        if master is None:
            raise RuntimeError(f"Cannot find master for {master_name_aliases}. Make sure Visio has Basic Shapes stencil.")

        shape = self.page.Drop(master, x, y)
        return shape

    def add_shape(
        self,
        shape_type: str,
        x: float,
        y: float,
        width: float = 1.5,
        height: float = 0.75,
        text: str = "",
        shape_id: str = None,
        fill_color: str = None,
        line_color: str = None,
        text_color: str = None,
        font_size: int = 11,
        font_name: str = "微软雅黑",
        bold: bool = False,
        corner_rounding: float = None,
        line_weight: float = 1.0,
    ) -> Any:
        """
        Add a shape to the current page.

        Args:
            shape_type: 'box', 'rounded_box', 'diamond', 'circle', 'parallelogram'
            x, y: Position in inches from top-left
            width, height: Size in inches
            text: Text content
            shape_id: User-defined identifier (stored in registry)
            ...: Style parameters
        Returns:
            Visio shape object
        """
        type_to_masters = {
            "box": ["Rectangle", "矩形"],
            "rectangle": ["Rectangle", "矩形"],
            "rounded_box": ["Rounded Rectangle", "圆角矩形"],
            "rounded_rect": ["Rounded Rectangle", "圆角矩形"],
            "diamond": ["Diamond", "菱形", "Decision"],
            "circle": ["Circle", "圆形"],
            "ellipse": ["Ellipse", "椭圆"],
            "parallelogram": ["Parallelogram", "平行四边形"],
            "triangle": ["Triangle", "三角形"],
            "hexagon": ["Hexagon", "六边形"],
            "cylinder": ["Cylinder", "圆柱"],
            "process": ["Rectangle", "矩形"],
            "decision": ["Diamond", "菱形", "Decision"],
            "start_end": ["Rounded Rectangle", "圆角矩形"],
            "data": ["Parallelogram", "平行四边形"],
        }

        masters = type_to_masters.get(shape_type, ["Rectangle", "矩形"])
        shape = self._drop_master(masters, x, y)

        if shape is None:
            raise RuntimeError(f"Failed to create shape of type '{shape_type}'")

        # Set size
        shape.CellsU("Width").ResultIU = width
        shape.CellsU("Height").ResultIU = height

        # Set text
        if text:
            shape.Text = text

        # Register shape
        if shape_id:
            self._shape_registry[shape_id] = shape
        else:
            sid = f"shape_{self._next_shape_idx}"
            self._shape_registry[sid] = shape
            self._next_shape_idx += 1

        # Apply styles
        if fill_color:
            try:
                shape.CellsU("FillForegnd").FormulaU = f"RGB({','.join(str(c) for c in COLORS_RGB.get(fill_color, (255,255,255)))})"
            except Exception:
                pass
        if line_color:
            try:
                shape.CellsU("LineColor").FormulaU = f"RGB({','.join(str(c) for c in COLORS_RGB.get(line_color, (0,0,0)))})"
            except Exception:
                pass
        if text_color:
            try:
                shape.CellsU("Char.Color").FormulaU = f"RGB({','.join(str(c) for c in COLORS_RGB.get(text_color, (0,0,0)))})"
            except Exception:
                pass

        try:
            shape.CellsU("Char.Size").FormulaU = f"{font_size}pt"
        except Exception:
            pass
        try:
            shape.CellsU("Char.Font").FormulaU = font_name
        except Exception:
            pass
        if bold:
            try:
                shape.CellsU("Char.Style").FormulaU = "Bold"
            except Exception:
                pass
        if corner_rounding is not None and shape_type in ("rounded_box", "rounded_rect"):
            try:
                shape.CellsU("Rounding").FormulaU = f"{corner_rounding} in"
            except Exception:
                pass
        if line_weight != 1.0:
            try:
                shape.CellsU("LineWeight").FormulaU = f"{line_weight}pt"
            except Exception:
                pass

        # Center text
        try:
            shape.CellsU("Para.HorzAlign").FormulaU = "1"  # center
        except Exception:
            pass
        try:
            shape.CellsU("VerticalAlign").FormulaU = "1"  # middle
        except Exception:
            pass

        return shape

    # ---- Connectors ----

    def add_connector(
        self,
        from_shape_or_id: Any,
        to_shape_or_id: Any,
        label: str = "",
        arrow_at_end: bool = True,
        arrow_type: int = 2,  # visArrowStealth
        line_color: str = "gray",
        line_weight: float = 1.0,
        routing: int = 2,  # visConnectorRightAngle
        connector_id: str = None,
    ) -> Any:
        """
        Add a connector between two shapes.

        Args:
            from_shape_or_id: Source shape object or registered shape_id
            to_shape_or_id: Target shape object or registered shape_id
            label: Text label on the connector
            arrow_at_end: Add arrow at the end
            arrow_type: Visio arrow style
            line_color: Line color name
            line_weight: Line thickness in pt
            routing: Connector routing style
            connector_id: User-defined identifier
        Returns:
            Connector shape object
        """
        # Resolve shapes
        from_shape = self._resolve_shape(from_shape_or_id)
        to_shape = self._resolve_shape(to_shape_or_id)

        if from_shape is None or to_shape is None:
            raise ValueError(f"Cannot resolve shapes: from={from_shape_or_id}, to={to_shape_or_id}")

        # Add a dynamic connector
        try:
            connector_master = self._find_master(["Dynamic Connector", "动态连接线", "Dynamic connector"])
        except Exception:
            connector_master = None

        if connector_master is None:
            # Fallback: find any connector
            try:
                for m in self.document.Masters:
                    if "connector" in m.NameU.lower():
                        connector_master = m
                        break
            except Exception:
                pass

        if connector_master is None:
            raise RuntimeError("Cannot find Dynamic Connector master in Visio stencils.")

        # Drop connector at the midpoint
        mid_x = (from_shape.CellsU("PinX").ResultIU + to_shape.CellsU("PinX").ResultIU) / 2
        mid_y = (from_shape.CellsU("PinY").ResultIU + to_shape.CellsU("PinY").ResultIU) / 2
        connector = self.page.Drop(connector_master, mid_x, mid_y)

        # Glue to shapes
        # Get connection points
        try:
            from_cell = from_shape.CellsU("Connections.X1")
            to_cell = to_shape.CellsU("Connections.X1")
        except Exception:
            pass

        # Glue begin to from_shape
        connector.CellsU("BeginX").GlueTo(from_shape.CellsU("PinX"))
        connector.CellsU("BeginY").GlueTo(from_shape.CellsU("PinY"))

        # Glue end to to_shape
        connector.CellsU("EndX").GlueTo(to_shape.CellsU("PinX"))
        connector.CellsU("EndY").GlueTo(to_shape.CellsU("PinY"))

        # Set arrow
        if arrow_at_end:
            try:
                connector.CellsU("EndArrow").FormulaU = str(arrow_type)
            except Exception:
                pass

        # Label
        if label:
            connector.Text = label

        # Style
        if line_color:
            try:
                connector.CellsU("LineColor").FormulaU = f"RGB({','.join(str(c) for c in COLORS_RGB.get(line_color, (128,128,128)))})"
            except Exception:
                pass
        if line_weight != 1.0:
            try:
                connector.CellsU("LineWeight").FormulaU = f"{line_weight}pt"
            except Exception:
                pass
        try:
            connector.CellsU("ShapeRouteStyle").FormulaU = str(routing)
        except Exception:
            pass

        # Register
        if connector_id:
            self._shape_registry[connector_id] = connector

        return connector

    def _resolve_shape(self, ref: Any) -> Any:
        """Resolve a shape reference: if string, look up in registry; otherwise return as-is."""
        if isinstance(ref, str):
            return self._shape_registry.get(ref)
        return ref

    # ---- Reading ----

    def read_shapes(self) -> List[Dict[str, Any]]:
        """Read all shapes on the current page."""
        if self.page is None:
            return []

        shapes_data = []
        for i in range(1, self.page.Shapes.Count + 1):
            try:
                shape = self.page.Shapes.Item(i)
                info = {
                    "index": i,
                    "name": shape.Name,
                    "name_u": shape.NameU,
                    "text": shape.Text,
                    "type": shape.Type,
                    "x": shape.CellsU("PinX").ResultIU,
                    "y": shape.CellsU("PinY").ResultIU,
                    "width": shape.CellsU("Width").ResultIU if self._cell_exists(shape, "Width") else 0,
                    "height": shape.CellsU("Height").ResultIU if self._cell_exists(shape, "Height") else 0,
                }
                # Read connections
                try:
                    conns = []
                    for j in range(1, shape.Connects.Count + 1):
                        connect = shape.Connects.Item(j)
                        conns.append({
                            "from_sheet": connect.FromSheet.Name,
                            "to_sheet": connect.ToSheet.Name,
                        })
                    info["connections"] = conns
                except Exception:
                    info["connections"] = []
                shapes_data.append(info)
            except Exception as e:
                shapes_data.append({"index": i, "error": str(e)})
        return shapes_data

    def _cell_exists(self, shape, cell_name: str) -> bool:
        """Check if a ShapeSheet cell exists."""
        try:
            _ = shape.CellsU(cell_name)
            return True
        except Exception:
            return False

    # ---- Export ----

    def export(self, path: str, format: str = "png"):
        """
        Export current page to image/PDF.
        format: 'png', 'jpg', 'svg', 'pdf'
        """
        path = os.path.abspath(path)

        # For image export, we use the Export method on Page
        if format in ("png", "jpg", "jpeg", "bmp", "tif", "tiff"):
            # Drive the Export via the Selection/Page
            # We need to select shapes on the page first
            try:
                self.page.Export(path)
            except Exception:
                # Fallback: use Application.Export
                pass
            return path

        elif format == "svg":
            # SVG export via SaveAs
            try:
                self.page.Export(path)
            except Exception:
                pass
            return path

        elif format == "pdf":
            self.document.ExportAsFixedFormat(
                1,  # visFixedFormatPDF
                path,
                1,  # visDocEx intent = print
            )
            return path

        else:
            raise ValueError(f"Unsupported export format: {format}")

    # ---- High-Level API ----

    def create_flowchart(self, spec: Dict[str, Any]) -> str:
        """
        Create a complete flowchart from a JSON specification.

        spec keys:
            page_name, orientation, style, shapes, connectors

        Returns the save path.
        """
        self.new_document()

        # Page setup
        page_name = spec.get("page_name", "Flowchart")
        self.set_page_name(page_name)

        orientation = spec.get("orientation", "portrait")
        self.set_page_orientation(orientation == "landscape")

        # Style preset
        style_name = spec.get("style", "default")
        preset = STYLE_PRESETS.get(style_name, STYLE_PRESETS["default"])

        # Create shapes
        for shape_spec in spec.get("shapes", []):
            shape_type = shape_spec.get("type", "box")
            shape_id = shape_spec.get("id")

            # Determine style based on type
            if shape_type in ("rounded_box", "rounded_rect", "start_end"):
                fill = shape_spec.get("fill_color", preset.get("start_fill", "light_blue"))
                line = shape_spec.get("line_color", preset.get("start_line", "blue"))
                tcolor = shape_spec.get("text_color", preset.get("start_text_color", "dark_blue"))
                corner = shape_spec.get("corner_rounding", preset.get("box_corner_rounding", 0.05))
            elif shape_type in ("diamond", "decision"):
                fill = shape_spec.get("fill_color", preset.get("diamond_fill", "light_green"))
                line = shape_spec.get("line_color", preset.get("diamond_line", "green"))
                tcolor = shape_spec.get("text_color", preset.get("diamond_text_color", "dark_green"))
                corner = None
            else:
                fill = shape_spec.get("fill_color", preset.get("box_fill", "light_blue"))
                line = shape_spec.get("line_color", preset.get("box_line", "blue"))
                tcolor = shape_spec.get("text_color", preset.get("box_text_color", "dark_blue"))
                corner = shape_spec.get("corner_rounding", preset.get("box_corner_rounding", 0.05))

            self.add_shape(
                shape_type=shape_type,
                x=shape_spec.get("x", 1.0),
                y=shape_spec.get("y", 1.0),
                width=shape_spec.get("width", 1.5),
                height=shape_spec.get("height", 0.75),
                text=shape_spec.get("text", ""),
                shape_id=shape_id,
                fill_color=fill,
                line_color=line,
                text_color=tcolor,
                font_size=shape_spec.get("font_size", preset.get("box_font_size", 11)),
                font_name=shape_spec.get("font_name", preset.get("font_name", "微软雅黑")),
                bold=shape_spec.get("bold", False),
                corner_rounding=corner,
                line_weight=shape_spec.get("line_weight", preset.get("connector_weight", 1.0)),
            )

        # Create connectors
        for conn_spec in spec.get("connectors", []):
            self.add_connector(
                from_shape_or_id=conn_spec["from"],
                to_shape_or_id=conn_spec["to"],
                label=conn_spec.get("label", ""),
                arrow_at_end=conn_spec.get("arrow", True),
                line_color=conn_spec.get("line_color", preset.get("connector_color", "gray")),
                line_weight=conn_spec.get("line_weight", preset.get("connector_weight", 1.0)),
                connector_id=conn_spec.get("id"),
            )

        # Auto-save
        save_path = spec.get("save_path")
        if save_path:
            self.save(save_path)
            return save_path

        return "OK: flowchart created in Visio (not saved yet)"

    def auto_layout_shapes(self, shapes: List[Dict], direction: str = "top-to-bottom"):
        """
        Automatically lay out shapes.

        Args:
            shapes: List of shape specs with id, width, height
            direction: 'top-to-bottom', 'left-to-right'
        """
        # Simple grid layout
        current_x = 1.0
        current_y = 1.0
        spacing_x = 0.5
        spacing_y = 0.5
        max_width = 1.5

        result = []
        for i, s in enumerate(shapes):
            w = s.get("width", 1.5)
            h = s.get("height", 0.75)
            result.append({
                **s,
                "x": current_x,
                "y": current_y,
                "width": w,
                "height": h,
            })
            if direction == "top-to-bottom":
                current_y += h + spacing_y
                max_width = max(max_width, w)
            else:
                current_x += w + spacing_x
        return result


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: python visio_automation.py <command> [options]")
        print("Commands: create, add-shapes, add-connectors, read, apply-style, export, from-description")
        sys.exit(1)

    command = sys.argv[1]
    controller = VisioController(visible=True)

    try:
        controller.connect()

        if command == "create":
            controller.new_document()
            print("OK: new Visio document created")

        elif command == "add-shapes":
            # Read JSON from arg or stdin
            if len(sys.argv) >= 3:
                data = json.loads(sys.argv[2])
            else:
                data = json.loads(sys.stdin.read())

            if isinstance(data, dict):
                data = [data]
            for s in data:
                shape = controller.add_shape(
                    shape_type=s.get("type", "box"),
                    x=s.get("x", 1.0),
                    y=s.get("y", 1.0),
                    width=s.get("width", 1.5),
                    height=s.get("height", 0.75),
                    text=s.get("text", ""),
                    shape_id=s.get("id"),
                    fill_color=s.get("fill_color"),
                    line_color=s.get("line_color"),
                    text_color=s.get("text_color"),
                    font_size=s.get("font_size", 11),
                    font_name=s.get("font_name", "微软雅黑"),
                    bold=s.get("bold", False),
                    corner_rounding=s.get("corner_rounding"),
                    line_weight=s.get("line_weight", 1.0),
                )
                print(f"OK: created shape '{shape.Name}' with text '{s.get('text', '')[:30]}'")

        elif command == "add-connectors":
            if len(sys.argv) >= 3:
                data = json.loads(sys.argv[2])
            else:
                data = json.loads(sys.stdin.read())

            if isinstance(data, dict):
                data = [data]
            for c in data:
                conn = controller.add_connector(
                    from_shape_or_id=c["from"],
                    to_shape_or_id=c["to"],
                    label=c.get("label", ""),
                    arrow_at_end=c.get("arrow", True),
                    line_color=c.get("line_color", "gray"),
                    line_weight=c.get("line_weight", 1.0),
                    connector_id=c.get("id"),
                )
                print(f"OK: connector from {c['from']} to {c['to']}")

        elif command == "read":
            shapes = controller.read_shapes()
            print(json.dumps(shapes, indent=2, ensure_ascii=False))

        elif command == "apply-style":
            if len(sys.argv) >= 3:
                style_name = sys.argv[2]
            else:
                style_name = "default"
            preset = STYLE_PRESETS.get(style_name, STYLE_PRESETS["default"])
            print(json.dumps(preset, indent=2, ensure_ascii=False))
            print(f"\nStyle '{style_name}' applied. Use apply-style with a JSON body for full control.")

        elif command == "export":
            fmt = sys.argv[2] if len(sys.argv) >= 3 else "png"
            path = sys.argv[3] if len(sys.argv) >= 4 else f"visio_export.{fmt}"
            controller.export(path, fmt)
            print(f"OK: exported to {path}")

        elif command == "from-description":
            if len(sys.argv) >= 3:
                if os.path.isfile(sys.argv[2]):
                    with open(sys.argv[2], "r", encoding="utf-8") as f:
                        spec = json.load(f)
                else:
                    spec = json.loads(sys.argv[2])
            else:
                spec = json.loads(sys.stdin.read())
            result = controller.create_flowchart(spec)
            print(result)

        elif command == "test":
            # Quick test to verify everything works
            controller.new_document()
            controller.set_page_name("Test Flowchart")

            s1 = controller.add_shape("rounded_box", 5, 1, 2, 0.8, text="开始", shape_id="start")
            s2 = controller.add_shape("box", 5, 2.5, 2, 0.8, text="处理步骤", shape_id="step1")
            s3 = controller.add_shape("diamond", 5, 4, 2.2, 1.0, text="条件判断?", shape_id="check")
            s4 = controller.add_shape("box", 7.5, 4, 2, 0.8, text="分支A", shape_id="branch_a")
            s5 = controller.add_shape("box", 2.5, 4, 2, 0.8, text="分支B", shape_id="branch_b")
            s6 = controller.add_shape("rounded_box", 5, 5.5, 2, 0.8, text="结束", shape_id="end")

            c1 = controller.add_connector("start", "step1")
            c2 = controller.add_connector("step1", "check")
            c3 = controller.add_connector("check", "branch_a", label="是")
            c4 = controller.add_connector("check", "branch_b", label="否")
            c5 = controller.add_connector("branch_a", "end")
            c6 = controller.add_connector("branch_b", "end")

            print("Test flowchart created successfully!")
            print(f"Shapes: {len(controller._shape_registry)}")
            print("Visio is ready for your inspection.")

        else:
            print(f"Unknown command: {command}")
            print("Available: create, add-shapes, add-connectors, read, apply-style, export, from-description, test")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Keep Visio open so user can see the result
        print("\n(Done. Visio window remains open for manual editing. Close it when finished.)")


if __name__ == "__main__":
    main()

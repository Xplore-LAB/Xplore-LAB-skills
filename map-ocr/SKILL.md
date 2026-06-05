---
name: map-ocr
description: 校园地图 OCR 识别与坐标修正。对地图图片运行 PaddleOCR 提取文字标注，自动计算 CSS object-fit:contain 的 letterboxing/pillarboxing 修正，输出容器百分比坐标。
---

# 地图 OCR 识别与坐标修正

从校园地图图片中提取所有文字标注，并自动将 OCR 像素坐标修正为 HTML 容器百分比坐标。

---

## 前置条件

- 当前工作目录在学校文件夹内
- `地图.png` 已存在
- PaddleOCR 已安装（`paddleocr==2.9.1`, `paddlepaddle==2.6.2`）
- Python 脚本位于 skill 目录：`extract_text_paddle.py` 和 `correct_coords.py`

## 流程

### Step 1: OCR 提取

在工作目录运行：

```bash
TMPDIR=/d/tmp TEMP=/d/tmp TMP=/d/tmp python <skill-dir>/extract_text_paddle.py
```

输出：`地图文字层_paddle.json`，包含所有检测到的文字及其像素坐标。

### Step 2: 坐标修正

```bash
python <skill-dir>/correct_coords.py 地图.png 地图文字层_paddle.json [容器宽度] [容器高度]
```

默认容器尺寸 788×492（PC 端 wiki-container-pc）。如需移动端容器（380×456），显式传入参数。

输出：`corrected_coords.json`，每条含 `text`, `cx`(容器x%), `cy`(容器y%)。

### Step 3: 两个坐标源

修正后的坐标有两种使用方式：

**A. 直接查表（推荐）：** 在 `corrected_coords.json` 中按建筑名搜索，手动填入 `ORIGINAL_BUILDINGS` 的 coords。

**B. 用 match_buildings.py 自动匹配：** 需要先修正 `地图文字层_paddle.json` 的坐标，再跑 LLM 匹配脚本。

---

## CSS letterboxing 修正原理

HTML 容器使用 `object-fit: contain` 显示地图。当地图宽高比 ≠ 容器宽高比时，图片两侧或上下会出现留白：

- **图片比容器更高**（如 1440×1738 → 788×492）：左右留白（pillarboxing）
- **图片比容器更宽**（如 3000×2000 → 788×492）：上下留白（letterboxing）

`correct_coords.py` 自动计算实际显示区域和偏移量，将 OCR 像素坐标映射为容器百分比坐标。

---

## 脚本位置

两个脚本存放在 skill 目录下，其他学校目录不用各存一份，直接调用 skill 目录的版本：

```bash
python ~/.claude/skills/map-ocr/extract_text_paddle.py
python ~/.claude/skills/map-ocr/correct_coords.py 地图.png 地图文字层_paddle.json
```

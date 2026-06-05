"""
通用坐标修正脚本：将 OCR 像素坐标转换为 HTML 容器百分比坐标，自动处理 object-fit: contain 的 letterboxing。

用法：
  python correct_coords.py <地图图片路径> <OCR_JSON路径> [容器宽度] [容器高度]

示例：
  python correct_coords.py 地图.png 地图文字层_paddle.json 788 492

输出：corrected_coords.json (text, cx, cy 为容器百分比坐标)
"""
import json, sys, os
from PIL import Image


def compute_correction(img_w, img_h, container_w, container_h):
    """计算 object-fit: contain 下的 display 区域和 padding"""
    img_ratio = img_w / img_h
    container_ratio = container_w / container_h

    if img_ratio > container_ratio:
        # 图片比容器更宽 → 宽度受限，上下有 letterboxing
        disp_w = container_w
        disp_h = container_w / img_ratio
        pad_x = 0
        pad_y = (container_h - disp_h) / 2
    else:
        # 图片比容器更高 → 高度受限，左右有 pillarboxing
        disp_h = container_h
        disp_w = container_h * img_ratio
        pad_y = 0
        pad_x = (container_w - disp_w) / 2

    return disp_w, disp_h, pad_x, pad_y


def convert(px_x, px_y, img_w, img_h, disp_w, disp_h, pad_x, pad_y, container_w, container_h):
    """OCR 像素坐标 → 容器百分比坐标"""
    cx = (pad_x + px_x * disp_w / img_w) / container_w * 100
    cy = (pad_y + px_y * disp_h / img_h) / container_h * 100
    return round(cx, 1), round(cy, 1)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    map_path = sys.argv[1]
    ocr_json = sys.argv[2]
    container_w = int(sys.argv[3]) if len(sys.argv) > 3 else 788
    container_h = int(sys.argv[4]) if len(sys.argv) > 4 else 492

    # 读取地图尺寸
    img = Image.open(map_path)
    img_w, img_h = img.size
    print(f"地图尺寸: {img_w}×{img_h}")
    print(f"容器尺寸: {container_w}×{container_h}")

    disp_w, disp_h, pad_x, pad_y = compute_correction(img_w, img_h, container_w, container_h)
    print(f"显示区域: {disp_w:.0f}×{disp_h:.0f}, padding:({pad_x:.0f}, {pad_y:.0f})")
    print(f"图片占比: 宽={disp_w/container_w*100:.1f}%, 高={disp_h/container_h*100:.1f}%")

    # 读取 OCR 结果
    with open(ocr_json, 'r', encoding='utf-8') as f:
        texts = json.load(f)

    # 转换坐标
    corrected = []
    for t in texts:
        cx, cy = convert(t['x'], t['y'], img_w, img_h, disp_w, disp_h, pad_x, pad_y, container_w, container_h)
        corrected.append({"text": t["text"], "cx": cx, "cy": cy})

    out_path = "corrected_coords.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(corrected, f, ensure_ascii=False, indent=2)

    print(f"\n输出: {out_path} ({len(corrected)} 条)")
    print("\n示例（前10条）:")
    for t in corrected[:10]:
        print(f"  {t['text']:20s}  cx={t['cx']:5.1f}%  cy={t['cy']:5.1f}%")


if __name__ == '__main__':
    main()

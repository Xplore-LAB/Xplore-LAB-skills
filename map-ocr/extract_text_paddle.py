import os, json, sys

os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from paddleocr import PaddleOCR

MAP_IMAGE = "地图.png"
OUTPUT = "地图文字层_paddle.json"

ocr = PaddleOCR(lang="ch", det_limit_side_len=8000, use_gpu=False)
result = ocr.ocr(MAP_IMAGE, cls=False)

texts = []
if result and result[0]:
    for line in result[0]:
        box = line[0]
        text = line[1][0]
        # 使用矩形包围盒中心作为百分比坐标
        xs = [p[0] for p in box]
        ys = [p[1] for p in box]
        x_percent = (min(xs) + max(xs)) / 2
        y_percent = (min(ys) + max(ys)) / 2
        texts.append({"text": text, "x": x_percent, "y": y_percent})

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(texts, f, ensure_ascii=False, indent=2)

print(f"提取完成: {len(texts)} 条文字, 已保存到 {OUTPUT}")

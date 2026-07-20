# fill_template.py 配置文件格式

JSON 格式，包含一个 `actions` 数组，按顺序执行每个操作。

## 操作类型

### 1. replace — 替换段落文本

```json
{
  "type": "replace",
  "search": "模板中的占位文本",
  "replacement": "替换后的内容",
  "bold": false,
  "size_pt": 12,
  "font_name": "宋体",
  "color": [0, 0, 0],
  "occurrence": 0
}
```

- `search`：要查找的文本（包含匹配）
- `replacement`：替换文本
- `occurrence`：第几个匹配（默认 0，即第一个）

### 2. fill_label_value — 填充标签+值

```json
{
  "type": "fill_label_value",
  "label": "申请人：",
  "value": "浙江大学",
  "label_bold": true,
  "label_color": [255, 0, 0],
  "value_size_pt": 9
}
```

清空原段落，写入 `label`（默认红色粗体）+ `value`。

### 3. insert_after — 在锚点后插入段落

```json
{
  "type": "insert_after",
  "after_text": "本发明所采用的具体技术方案如下",
  "paragraphs": [
    "第一段内容...",
    "第二段内容..."
  ],
  "bold": false,
  "size_pt": 12
}
```

### 4. clear_between — 清除两段之间的内容

```json
{
  "type": "clear_between",
  "start_text": "背景技术",
  "end_text": "发明内容"
}
```

保留 start 和 end 段落，删除中间所有段落。

### 5. insert_image — 插入图片

```json
{
  "type": "insert_image",
  "after_text": "图1",
  "image_path": "/path/to/image.png",
  "width_inches": 5.5
}
```

## 完整示例

```json
{
  "output": "输出文档.docx",
  "actions": [
    {
      "type": "fill_label_value",
      "label": "申请类型：",
      "value": "仅申请发明专利"
    },
    {
      "type": "replace",
      "search": "本发明公开了一种",
      "replacement": "本发明公开了一种XXX方法及系统。该方法包括..."
    },
    {
      "type": "insert_after",
      "after_text": "背景技术",
      "paragraphs": [
        "现有技术存在以下问题...",
        "针对上述问题..."
      ]
    },
    {
      "type": "insert_image",
      "after_text": "图1",
      "image_path": "./figures/system_arch.png"
    }
  ]
}
```

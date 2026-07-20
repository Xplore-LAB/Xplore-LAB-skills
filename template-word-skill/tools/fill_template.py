"""
fill_template.py — 通用 Word 模板填充脚本

读取 JSON 配置文件，按配置执行占位符替换、段落插入、图片嵌入。
配置文件格式见 prompts/config_format.md。

用法：
    python fill_template.py --template 模板.docx --config 配置.json --output 输出.docx
    python fill_template.py --template 模板.docx --config 配置.json  # 输出到模板同目录
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx_template import (
    load_template, save_doc, find_para_index, find_para_indices,
    clear_runs, copy_run_format, copy_para_format,
    add_styled_para, insert_paras_after, replace_para_text,
    add_image_after, get_normal_ref
)


def apply_replace(doc, action):
    """替换占位符文本"""
    search = action['search']
    replacement = action.get('replacement', '')
    bold = action.get('bold', False)
    size_pt = action.get('size_pt')
    font_name = action.get('font_name')
    color = action.get('color')  # (R, G, B) tuple
    occurrence = action.get('occurrence', 0)  # 第几个匹配

    indices = find_para_indices(doc, search)
    if not indices:
        print(f"  [WARN] 未找到: '{search}'")
        return False

    idx = indices[min(occurrence, len(indices) - 1)]
    replace_para_text(doc, idx, replacement, bold=bold, size_pt=size_pt,
                      font_name=font_name, color=color)
    print(f"  [OK] 替换 '{search}' -> '{replacement[:50]}...' (段落 {idx})")
    return True


def apply_insert_after(doc, action):
    """在指定文本后插入段落"""
    after_text = action['after_text']
    paragraphs = action.get('paragraphs', [])
    bold = action.get('bold', False)
    size_pt = action.get('size_pt')
    font_name = action.get('font_name')

    idx = find_para_index(doc, after_text)
    if idx is None:
        print(f"  [WARN] 未找到锚点: '{after_text}'")
        return False

    ref_para = doc.paragraphs[idx]
    last_idx = insert_paras_after(doc, idx, paragraphs, ref_para,
                                  bold=bold, size_pt=size_pt, font_name=font_name)
    print(f"  [OK] 在段落 {idx} 后插入 {len(paragraphs)} 个段落")
    return True


def apply_clear_between(doc, action):
    """清除两个文本之间的段落（保留首尾）"""
    start_text = action['start_text']
    end_text = action.get('end_text')

    start_idx = find_para_index(doc, start_text)
    if start_idx is None:
        print(f"  [WARN] 未找到起始: '{start_text}'")
        return False

    if end_text:
        end_idx = find_para_index(doc, end_text, start=start_idx + 1)
        if end_idx is None:
            print(f"  [WARN] 未找到结束: '{end_text}'")
            return False
    else:
        end_idx = start_idx + 2  # 默认清除一段

    # 从后往前删除
    parent = doc.paragraphs[start_idx]._element.getparent()
    for i in range(end_idx - 1, start_idx, -1):
        el = doc.paragraphs[i]._element
        parent.remove(el)

    print(f"  [OK] 清除段落 {start_idx+1} 到 {end_idx-1}")
    return True


def apply_insert_image(doc, action):
    """插入图片"""
    after_text = action['after_text']
    image_path = action['image_path']
    width_inches = action.get('width_inches', 5.5)

    idx = find_para_index(doc, after_text)
    if idx is None:
        print(f"  [WARN] 未找到图片锚点: '{after_text}'")
        return False

    add_image_after(doc, idx, image_path, width_inches=width_inches)
    print(f"  [OK] 在段落 {idx} 后插入图片: {image_path}")
    return True


def apply_fill_label_value(doc, action):
    """填充标签-值对（如 "申请人：" -> "申请人：浙江大学"）"""
    label = action['label']
    value = action.get('value', '')
    label_bold = action.get('label_bold', True)
    label_color = action.get('label_color', (0xFF, 0, 0))  # 默认红色
    value_size_pt = action.get('value_size_pt')

    idx = find_para_index(doc, label)
    if idx is None:
        print(f"  [WARN] 未找到标签: '{label}'")
        return False

    p = doc.paragraphs[idx]
    clear_runs(p)

    # 标签 run
    label_run = p.add_run(label)
    label_run.font.bold = label_bold
    if label_color:
        label_run.font.color.rgb = __import__('docx.shared', fromlist=['RGBColor']).RGBColor(*label_color)

    # 值 run
    val_run = p.add_run(value)
    if value_size_pt:
        val_run.font.size = __import__('docx.shared', fromlist=['Pt']).Pt(value_size_pt)

    print(f"  [OK] 填充标签 '{label}' + 值 '{value[:30]}...'")
    return True


ACTION_HANDLERS = {
    'replace': apply_replace,
    'insert_after': apply_insert_after,
    'clear_between': apply_clear_between,
    'insert_image': apply_insert_image,
    'fill_label_value': apply_fill_label_value,
}


def main():
    parser = argparse.ArgumentParser(description='Word 模板填充工具')
    parser.add_argument('--template', required=True, help='模板 .docx 文件路径')
    parser.add_argument('--config', required=True, help='填充配置 JSON 文件路径')
    parser.add_argument('--output', help='输出 .docx 文件路径（默认与模板同目录）')
    args = parser.parse_args()

    if not os.path.exists(args.template):
        print(f"[ERROR] 模板文件不存在: {args.template}")
        sys.exit(1)
    if not os.path.exists(args.config):
        print(f"[ERROR] 配置文件不存在: {args.config}")
        sys.exit(1)

    with open(args.config, 'r', encoding='utf-8') as f:
        config = json.load(f)

    output_path = args.output or config.get('output')
    if not output_path:
        base = os.path.splitext(args.template)[0]
        output_path = base + '_filled.docx'

    print(f"模板: {args.template}")
    print(f"配置: {args.config}")
    print(f"输出: {output_path}")
    print("---")

    doc = load_template(args.template)

    actions = config.get('actions', [])
    for i, action in enumerate(actions):
        action_type = action.get('type')
        handler = ACTION_HANDLERS.get(action_type)
        if handler is None:
            print(f"  [WARN] 未知操作类型: '{action_type}'")
            continue
        print(f"[{i+1}/{len(actions)}] {action_type}")
        handler(doc, action)

    save_doc(doc, output_path)
    print(f"\n完成! 已写入: {output_path}")


if __name__ == '__main__':
    main()

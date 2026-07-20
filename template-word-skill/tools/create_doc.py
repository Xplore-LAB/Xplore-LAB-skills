"""
create_doc.py — 从零创建 Word 文档

按 JSON 规范生成标准格式文档，无需 .docx 模板文件。
支持 4 种格式预设：正式叙述文档、技术说明书、操作手册、清单/表格。

用法：
    # 从 JSON 规范文件创建
    python create_doc.py --spec spec.json --output output.docx

    # 从预设 + 快速参数创建（自动使用文档注册表中的默认章节）
    python create_doc.py --doc-type "项目计划书" --project-name "智能问数" --output 项目计划书.docx

    # 列出所有支持的文档类型
    python create_doc.py --list-doc-types

    # 列出所有格式预设
    python create_doc.py --list-presets
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx_template import (
    create_doc_from_spec, DOC_REGISTRY, STYLE_PRESETS
)


def list_doc_types():
    """列出所有支持的文档类型"""
    print("支持的文档类型：")
    print("-" * 60)
    # 按预设分组
    by_preset = {}
    for doc_type, config in DOC_REGISTRY.items():
        preset = config.get('preset', 'unknown')
        if preset not in by_preset:
            by_preset[preset] = []
        by_preset[preset].append(doc_type)

    preset_names = {
        'formal_report': 'A - 正式叙述文档',
        'tech_spec': 'B - 技术说明书',
        'manual': 'C - 操作手册',
        'checklist': 'D - 清单/表格',
    }
    for preset, doc_types in by_preset.items():
        print(f"\n{preset_names.get(preset, preset)}：")
        for dt in doc_types:
            sections = DOC_REGISTRY[dt].get('sections', [])
            print(f"  {dt}")
            print(f"    默认章节：{' / '.join(sections[:5])}" +
                  (f" ... (共{len(sections)}章)" if len(sections) > 5 else ""))


def list_presets():
    """列出所有格式预设"""
    print("格式预设：")
    print("-" * 60)
    for name, preset in STYLE_PRESETS.items():
        print(f"\n{name}:")
        for style_name, config in preset.get('styles', {}).items():
            font = config.get('font', '?')
            size = config.get('size_pt', '?')
            bold = '粗体' if config.get('bold') else ''
            extra = []
            if config.get('centered'):
                extra.append('居中')
            if config.get('line_spacing_pt'):
                extra.append(f'行距{config["line_spacing_pt"]}pt')
            if config.get('first_line_indent_chars'):
                extra.append(f'首行缩进{config["first_line_indent_chars"]}字符')
            if config.get('bg_color'):
                extra.append(f'底色#{config["bg_color"]}')
            extra_str = ', '.join(extra)
            print(f"  {style_name}: {font} {size}pt {bold} {extra_str}".rstrip())


def build_spec_from_doc_type(doc_type, project_name='', version='', date='',
                              author='', reviewer='', overrides=None):
    """从文档类型构建完整规范"""
    if doc_type not in DOC_REGISTRY:
        print(f"[ERROR] 未知文档类型: '{doc_type}'")
        print(f"使用 --list-doc-types 查看所有支持的类型")
        sys.exit(1)

    reg = DOC_REGISTRY[doc_type]
    preset = reg.get('preset', 'formal_report')

    spec = {
        'project_name': project_name,
        'doc_name': reg.get('doc_name', doc_type),
        'preset': preset,
        'version': version,
        'date': date,
        'author': author,
        'reviewer': reviewer,
        'toc': preset in ('formal_report', 'tech_spec'),
        'header_left': project_name,
        'header_right': reg.get('doc_name', doc_type),
        'footer_text': '第 {{page}} 页',
        'sections': [],
    }

    # 从注册表构建章节
    for section_name in reg.get('sections', []):
        spec['sections'].append({
            'title': section_name,
            'level': 1,
            'paragraphs': []
        })

    # 表格类文档，添加空表格
    table_columns = reg.get('table_columns')
    if table_columns:
        spec['sections'].append({
            'title': '',
            'level': 0,
            'paragraphs': [{
                'type': 'table',
                'headers': table_columns,
                'rows': []  # 空表格，用户自行填写
            }]
        })

    # 应用覆盖
    if overrides:
        spec.update(overrides)

    return spec


def main():
    parser = argparse.ArgumentParser(description='从零创建 Word 文档')
    parser.add_argument('--spec', help='JSON 规范文件路径')
    parser.add_argument('--doc-type', help='文档类型名称（如"项目计划书"）')
    parser.add_argument('--project-name', default='', help='项目名称')
    parser.add_argument('--version', default='', help='版本号')
    parser.add_argument('--date', default='', help='日期')
    parser.add_argument('--author', default='', help='编制人')
    parser.add_argument('--reviewer', default='', help='审核人')
    parser.add_argument('--output', help='输出 .docx 文件路径')
    parser.add_argument('--list-doc-types', action='store_true', help='列出所有支持的文档类型')
    parser.add_argument('--list-presets', action='store_true', help='列出所有格式预设')
    args = parser.parse_args()

    if args.list_doc_types:
        list_doc_types()
        return
    if args.list_presets:
        list_presets()
        return

    # 加载或构建规范
    if args.spec:
        with open(args.spec, 'r', encoding='utf-8') as f:
            spec = json.load(f)
    elif args.doc_type:
        spec = build_spec_from_doc_type(
            args.doc_type,
            project_name=args.project_name,
            version=args.version,
            date=args.date,
            author=args.author,
            reviewer=args.reviewer
        )
    else:
        print("[ERROR] 必须指定 --spec 或 --doc-type")
        sys.exit(1)

    # 输出路径
    output_path = args.output or spec.get('output', '')
    if not output_path:
        doc_name = spec.get('doc_name', 'output')
        project_name = spec.get('project_name', '')
        if project_name:
            output_path = f"{project_name}_{doc_name}.docx"
        else:
            output_path = f"{doc_name}.docx"
    spec['output'] = output_path

    # 生成
    print(f"项目: {spec.get('project_name', '-')}")
    print(f"文档: {spec.get('doc_name', '-')}")
    print(f"预设: {spec.get('preset', 'formal_report')}")
    print(f"输出: {output_path}")
    print("---")

    result = create_doc_from_spec(spec)
    print(f"\n完成! 已生成: {result}")


if __name__ == '__main__':
    main()

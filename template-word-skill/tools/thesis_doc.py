# -*- coding: utf-8 -*-
"""
thesis_doc.py — 学位论文模式 CLI（v4 新增）

对已有/新建 Word 文档应用学位论文格式。格式来源：
    --profile 档案.json   使用论文格式档案
    --ref    模板.docx    从学校模板现抽格式
    （缺省）              使用通用学位论文档案

子命令：
    new         一键生成完整论文骨架
    cover       插入/重建封面
    numbering   给已有文档加多级标题编号
    figure      插入图+题注
    table       插入三线表+题注
    equation    插入公式+编号
    sections    配置分节页码（封面无/前置罗马/正文阿拉伯）
    abstract    插入中英文摘要
    references  插入 GB/T 7714 参考文献
    lof / lot   生成图/表索引

统一提示：自动域（编号、题注、目录、图表索引）需在 Word 中 Ctrl+A → F9 更新。

用法示例：
    # 一键生成论文骨架
    python thesis_doc.py new --spec 论文.json --output 论文.docx

    # 插入三线表
    python thesis_doc.py table --input 论文.docx --output 论文.docx \\
        --after "实验结果" --data table.json --caption "各方法准确率对比"

    # 给已有文档加多级编号
    python thesis_doc.py numbering --input 论文.docx --output 论文.docx --ref 学校模板.docx
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx import Document
from docx_template import save_doc
from thesis_docx import (
    resolve_thesis_profile, build_thesis_profile,
    add_thesis_cover, add_declaration, add_acknowledgement,
    setup_multilevel_numbering, apply_heading_numbering,
    add_figure, add_three_line_table, add_equation,
    setup_thesis_sections, add_abstract, add_references,
    add_list_of_figures, add_list_of_tables,
    build_thesis_skeleton,
)


def resolve_profile(args):
    """解析论文档案：profile > ref > 通用默认"""
    if getattr(args, 'profile', None):
        return resolve_thesis_profile(profile=args.profile)
    if getattr(args, 'ref', None):
        return resolve_thesis_profile(ref=args.ref)
    return build_thesis_profile()


# ---- 子命令 ----

def cmd_new(args):
    with open(args.spec, 'r', encoding='utf-8') as f:
        spec = json.load(f)
    spec['output'] = args.output
    if args.ref:
        spec['ref'] = args.ref
    elif args.profile:
        spec['profile'] = args.profile
    out = build_thesis_skeleton(spec)
    print(f'已生成学位论文骨架 → {out}')
    print('提示：在 Word 中打开后按 Ctrl+A → F9 更新目录、编号、题注、图表索引')
    return 0


def cmd_cover(args):
    doc = Document(args.input)
    profile = resolve_profile(args)
    # 插入到文档开头
    info = {
        'school': args.school, 'title': args.title, 'author': args.author,
        'student_id': args.student_id, 'supervisor': args.supervisor,
        'major': args.major, 'date': args.date,
    }
    # 在开头插入：先收集新内容再移动（简单做法：新建临时文档再合并较复杂，
    # 这里采用追加到末尾的实用策略，并提示用户手动调整顺序）
    add_thesis_cover(doc, info, profile)
    save_doc(doc, args.output)
    print(f'已追加封面 → {args.output}（如需置顶请在 Word 中剪切到开头）')
    return 0


def cmd_numbering(args):
    doc = Document(args.input)
    profile = resolve_profile(args)
    num_id = setup_multilevel_numbering(doc, profile)
    apply_heading_numbering(doc, num_id)
    save_doc(doc, args.output)
    print(f'已为 Heading 1/2/3 绑定多级编号(numId={num_id}) → {args.output}')
    print('提示：Word 中 Ctrl+A → F9 更新编号显示')
    return 0


def cmd_figure(args):
    doc = Document(args.input)
    profile = resolve_profile(args)
    idx = add_figure(doc, args.after, args.image, args.caption, args.width, profile)
    save_doc(doc, args.output)
    print(f'已在段落 #{idx}（含"{args.after}"）后插入图+题注 → {args.output}')
    return 0


def cmd_table(args):
    doc = Document(args.input)
    profile = resolve_profile(args)
    with open(args.data, 'r', encoding='utf-8') as f:
        data = json.load(f)
    headers = data.get('headers', data.get('columns', []))
    rows = data.get('rows', [])
    idx = add_three_line_table(doc, args.after, headers, rows, args.caption, profile)
    save_doc(doc, args.output)
    print(f'已在段落 #{idx}（含"{args.after}"）后插入三线表+题注 → {args.output}')
    return 0


def cmd_equation(args):
    doc = Document(args.input)
    profile = resolve_profile(args)
    idx = add_equation(doc, args.after, args.text, profile)
    save_doc(doc, args.output)
    print(f'已在段落 #{idx}（含"{args.after}"）后插入公式+编号 → {args.output}')
    return 0


def cmd_sections(args):
    doc = Document(args.input)
    profile = resolve_profile(args)
    ok = setup_thesis_sections(doc, profile)
    save_doc(doc, args.output)
    if ok:
        print(f'已配置分节页码（封面无/前置罗马/正文阿拉伯从1） → {args.output}')
    else:
        print(f'⚠ 文档不足3节，未能完整配置分节页码 → {args.output}')
        print('  需先用分节符分隔封面/前置/正文。new 子命令已自动分节。')
    return 0


def cmd_abstract(args):
    doc = Document(args.input)
    profile = resolve_profile(args)
    zh = {'title': args.zh_title, 'body': args.zh_body, 'keywords': args.zh_keywords}
    en = {'title': args.en_title, 'body': args.en_body, 'keywords': args.en_keywords}
    # add_abstract 接收展开参数
    add_abstract(doc,
                 zh['title'], zh['body'], zh['keywords'],
                 en['title'], en['body'], en['keywords'], profile)
    save_doc(doc, args.output)
    print(f'已插入中英文摘要 → {args.output}')
    return 0


def cmd_references(args):
    doc = Document(args.input)
    profile = resolve_profile(args)
    with open(args.items, 'r', encoding='utf-8') as f:
        items = json.load(f)
    add_references(doc, items, profile)
    save_doc(doc, args.output)
    print(f'已插入 {len(items)} 条参考文献（GB/T 7714） → {args.output}')
    return 0


def cmd_lof(args):
    doc = Document(args.input)
    profile = resolve_profile(args)
    add_list_of_figures(doc, args.title, profile)
    save_doc(doc, args.output)
    print(f'已插入图索引 → {args.output}（Word 中 F9 更新）')
    return 0


def cmd_lot(args):
    doc = Document(args.input)
    profile = resolve_profile(args)
    add_list_of_tables(doc, args.title, profile)
    save_doc(doc, args.output)
    print(f'已插入表索引 → {args.output}（Word 中 F9 更新）')
    return 0


# ---- 参数解析 ----

def add_format_source_args(p):
    p.add_argument('--profile', help='论文格式档案 JSON 路径')
    p.add_argument('--ref', help='学校模板 .docx 路径（现抽格式）')


def build_parser():
    parser = argparse.ArgumentParser(
        description='学位论文模式：生成/编辑学位论文并保持论文格式',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest='command', required=True)

    # new
    p = sub.add_parser('new', help='一键生成完整论文骨架')
    p.add_argument('--spec', required=True, help='论文规范 JSON 路径')
    p.add_argument('--output', required=True, help='输出 .docx')
    add_format_source_args(p)
    p.set_defaults(func=cmd_new)

    # cover
    p = sub.add_parser('cover', help='插入封面')
    p.add_argument('--input', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--school', default='')
    p.add_argument('--title', default='')
    p.add_argument('--author', default='')
    p.add_argument('--student-id', dest='student_id', default='')
    p.add_argument('--supervisor', default='')
    p.add_argument('--major', default='')
    p.add_argument('--date', default='')
    add_format_source_args(p)
    p.set_defaults(func=cmd_cover)

    # numbering
    p = sub.add_parser('numbering', help='给已有文档加多级标题编号')
    p.add_argument('--input', required=True)
    p.add_argument('--output', required=True)
    add_format_source_args(p)
    p.set_defaults(func=cmd_numbering)

    # figure
    p = sub.add_parser('figure', help='插入图+题注')
    p.add_argument('--input', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--after', required=True, help='锚点文本')
    p.add_argument('--image', required=True, help='图片路径')
    p.add_argument('--caption', required=True, help='图题名')
    p.add_argument('--width', type=float, default=14, help='图宽 cm')
    add_format_source_args(p)
    p.set_defaults(func=cmd_figure)

    # table
    p = sub.add_parser('table', help='插入三线表+题注')
    p.add_argument('--input', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--after', required=True, help='锚点文本')
    p.add_argument('--data', required=True, help='表格 JSON（headers+rows）')
    p.add_argument('--caption', required=True, help='表题名')
    add_format_source_args(p)
    p.set_defaults(func=cmd_table)

    # equation
    p = sub.add_parser('equation', help='插入公式+编号')
    p.add_argument('--input', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--after', required=True, help='锚点文本')
    p.add_argument('--text', required=True, help='公式文本')
    add_format_source_args(p)
    p.set_defaults(func=cmd_equation)

    # sections
    p = sub.add_parser('sections', help='配置分节页码')
    p.add_argument('--input', required=True)
    p.add_argument('--output', required=True)
    add_format_source_args(p)
    p.set_defaults(func=cmd_sections)

    # abstract
    p = sub.add_parser('abstract', help='插入中英文摘要')
    p.add_argument('--input', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--zh-title', dest='zh_title', default='')
    p.add_argument('--zh-body', dest='zh_body', default='')
    p.add_argument('--zh-keywords', dest='zh_keywords', default='')
    p.add_argument('--en-title', dest='en_title', default='')
    p.add_argument('--en-body', dest='en_body', default='')
    p.add_argument('--en-keywords', dest='en_keywords', default='')
    add_format_source_args(p)
    p.set_defaults(func=cmd_abstract)

    # references
    p = sub.add_parser('references', help='插入 GB/T 7714 参考文献')
    p.add_argument('--input', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--items', required=True, help='参考文献 JSON 路径')
    add_format_source_args(p)
    p.set_defaults(func=cmd_references)

    # lof / lot
    p = sub.add_parser('lof', help='生成图索引')
    p.add_argument('--input', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--title', default='图  录')
    add_format_source_args(p)
    p.set_defaults(func=cmd_lof)

    p = sub.add_parser('lot', help='生成表索引')
    p.add_argument('--input', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--title', default='表  录')
    add_format_source_args(p)
    p.set_defaults(func=cmd_lot)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())

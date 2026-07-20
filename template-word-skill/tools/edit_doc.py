"""
edit_doc.py — 编辑保格式：对已有 Word 文档做编辑，同时保持/统一格式

格式来源（三者择一，优先级 profile > ref > preset，缺省 formal_report）：
    --profile 档案.json   使用此前 extract 出的格式档案
    --ref    标杆.docx    从参考文档现抽格式（不落盘）
    --preset formal_report 直接用内置预设作为档案

子命令：
    extract  从参考文档抽取格式档案
    apply    按档案统一全文格式
    replace  全文查找替换（保留原格式）
    insert   在锚点段落后插入带类型的内容块
    heading  把某段落重设为 N 级标题
    toc      刷新/补建目录

用法示例：
    # 抽取标杆文档格式
    python edit_doc.py extract --ref 标杆.docx --profile 档案.json

    # 套用标杆格式到目标文档
    python edit_doc.py apply --input 目标.docx --output 输出.docx --ref 标杆.docx

    # 查找替换保格式
    python edit_doc.py replace --input 目标.docx --output 输出.docx \\
        --find "旧词" --replace "新词"

    # 锚点后插入内容块（blocks.json 见 prompts/edit_format.md）
    python edit_doc.py insert --input 目标.docx --output 输出.docx \\
        --after "第一章" --blocks blocks.json --preset formal_report

    # 把某段重排为 2 级标题
    python edit_doc.py heading --input 目标.docx --output 输出.docx \\
        --find "某段文本" --level 2

    # 刷新目录
    python edit_doc.py toc --input 目标.docx --output 输出.docx --refresh
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx_template import (
    Document, build_default_profile, extract_format_profile,
    save_profile, load_profile, apply_format_profile,
    find_replace_text, insert_blocks_after, set_heading,
    find_para_index, refresh_toc, ensure_toc, save_doc,
)


# ---- 格式来源解析 ----

def resolve_profile(args):
    """按 profile > ref > preset 优先级解析出格式档案 dict"""
    if getattr(args, 'profile', None):
        return load_profile(args.profile)
    if getattr(args, 'ref', None):
        return extract_format_profile(args.ref)
    return build_default_profile(getattr(args, 'preset', 'formal_report') or 'formal_report')


def add_format_source_args(p):
    """为需要格式档案的子命令添加 --profile/--ref/--preset 参数"""
    p.add_argument('--profile', help='格式档案 JSON 路径')
    p.add_argument('--ref', help='参考文档 .docx 路径（现抽格式）')
    p.add_argument('--preset', default='formal_report',
                   help='内置预设名（formal_report/tech_spec/manual/checklist），缺省 formal_report')


# ---- 子命令实现 ----

def cmd_extract(args):
    profile = extract_format_profile(args.ref)
    save_profile(profile, args.profile)
    # 控制台摘要
    print(f'已抽取格式档案 → {args.profile}')
    print(f'  来源文档: {profile.get("_source")}')
    print(f'  页边距(cm): {profile["page"]["margins"]}')
    print(f'  标题层级: {sorted(profile["heading"].keys())}')
    for lvl in sorted(profile['heading'].keys()):
        h = profile['heading'][lvl]
        print(f'    H{lvl}: {h.get("font")}/{h.get("size_pt")}pt bold={h.get("bold")}')
    b = profile['body']
    print(f'  正文: {b.get("font")}/{b.get("size_pt")}pt 行距={b.get("line_spacing_pt") or b.get("line_spacing_multiple")}')
    print(f'  表头背景: {profile["table_header"].get("bg_color")}')
    return 0


def cmd_apply(args):
    doc = Document(args.input)
    profile = resolve_profile(args)
    apply_format_profile(doc, profile, apply_page=not args.no_page, apply_tables=not args.no_tables)
    save_doc(doc, args.output)
    print(f'已按档案统一格式 → {args.output}')
    return 0


def cmd_replace(args):
    doc = Document(args.input)
    n = find_replace_text(doc, args.find, args.replace, in_tables=not args.body_only)
    save_doc(doc, args.output)
    print(f'已替换 {n} 处 → {args.output}')
    return 0


def cmd_insert(args):
    doc = Document(args.input)
    with open(args.blocks, 'r', encoding='utf-8') as f:
        blocks = json.load(f)
    if isinstance(blocks, dict):
        blocks = [blocks]
    profile = resolve_profile(args)
    idx = insert_blocks_after(doc, args.after, blocks, profile)
    save_doc(doc, args.output)
    print(f'已在段落 #{idx}（含"{args.after}"）后插入 {len(blocks)} 个块 → {args.output}')
    return 0


def cmd_heading(args):
    doc = Document(args.input)
    idx = find_para_index(doc, args.find)
    if idx is None:
        print(f'错误：未找到包含 "{args.find}" 的段落', file=sys.stderr)
        return 1
    profile = resolve_profile(args)
    set_heading(doc, idx, args.level, profile)
    save_doc(doc, args.output)
    print(f'已将段落 #{idx} 重设为 Heading {args.level} → {args.output}')
    return 0


def cmd_toc(args):
    doc = Document(args.input)
    if args.ensure:
        created = ensure_toc(doc, args.title)
        action = '新建目录' if created else '已存在目录，已标记刷新'
    else:
        refresh_toc(doc)
        action = '已标记目录待更新'
    save_doc(doc, args.output)
    print(f'{action} → {args.output}')
    print('提示：在 Word 中打开后按 Ctrl+A → F9 更新目录')
    return 0


# ---- 参数解析 ----

def build_parser():
    parser = argparse.ArgumentParser(
        description='编辑保格式：编辑已有 Word 文档同时保持/统一格式',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest='command', required=True)

    # extract
    p = sub.add_parser('extract', help='从参考文档抽取格式档案')
    p.add_argument('--ref', required=True, help='参考文档 .docx 路径')
    p.add_argument('--profile', required=True, help='输出档案 JSON 路径')
    p.set_defaults(func=cmd_extract)

    # apply
    p = sub.add_parser('apply', help='按档案统一全文格式')
    p.add_argument('--input', required=True, help='目标文档 .docx')
    p.add_argument('--output', required=True, help='输出文档 .docx')
    add_format_source_args(p)
    p.add_argument('--no-page', action='store_true', help='不改页边距')
    p.add_argument('--no-tables', action='store_true', help='不改表格格式')
    p.set_defaults(func=cmd_apply)

    # replace
    p = sub.add_parser('replace', help='全文查找替换（保留格式）')
    p.add_argument('--input', required=True, help='目标文档 .docx')
    p.add_argument('--output', required=True, help='输出文档 .docx')
    p.add_argument('--find', required=True, help='查找文本')
    p.add_argument('--replace', required=True, help='替换文本')
    p.add_argument('--body-only', action='store_true', help='仅替换正文，跳过表格')
    p.set_defaults(func=cmd_replace)

    # insert
    p = sub.add_parser('insert', help='在锚点段落后插入内容块')
    p.add_argument('--input', required=True, help='目标文档 .docx')
    p.add_argument('--output', required=True, help='输出文档 .docx')
    p.add_argument('--after', required=True, help='锚点文本（段落包含该文本即作为锚点）')
    p.add_argument('--blocks', required=True, help='内容块 JSON 路径')
    add_format_source_args(p)
    p.set_defaults(func=cmd_insert)

    # heading
    p = sub.add_parser('heading', help='把某段落重设为 N 级标题')
    p.add_argument('--input', required=True, help='目标文档 .docx')
    p.add_argument('--output', required=True, help='输出文档 .docx')
    p.add_argument('--find', required=True, help='段落包含的文本')
    p.add_argument('--level', type=int, required=True, choices=[1, 2, 3, 4], help='标题层级 1-4')
    add_format_source_args(p)
    p.set_defaults(func=cmd_heading)

    # toc
    p = sub.add_parser('toc', help='刷新/补建目录')
    p.add_argument('--input', required=True, help='目标文档 .docx')
    p.add_argument('--output', required=True, help='输出文档 .docx')
    g = p.add_mutually_exclusive_group()
    g.add_argument('--refresh', action='store_true', help='标记现有目录待更新（默认）')
    g.add_argument('--ensure', action='store_true', help='无目录则新建一个')
    p.add_argument('--title', default='目  录', help='目录标题（仅 ensure 新建时生效）')
    p.set_defaults(func=cmd_toc)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())

# -*- coding: utf-8 -*-
r"""
thesis_docx.py — 学位论文格式核心库（v4 新增）

在 docx_template.py 的格式档案机制之上，提供学位论文专用构建与编辑能力：
  A. 档案：通用学位论文档案 + 学校模板抽取
  B. 封面与固定结构页：封面 / 独创性声明 / 致谢
  C. 多级标题编号：numbering.xml，1 / 1.1 / 1.1.1
  D. 图表公式与题注：图/三线表/公式，分章编号（STYLEREF+SEQ）
  E. 分节页码：封面无页码 / 前置罗马 / 正文阿拉伯重启
  F. 中英文摘要 / GB/T 7714 参考文献
  G. 图表索引（TOC 域带 \c 开关）
  H. 一键论文骨架

统一限制：所有自动域（编号、题注、目录、图表索引）写入域代码，
实际编号值需 Word 打开后 Ctrl+A → F9 更新（OOXML 固有机制）。
"""
import os
import copy
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Emu, Twips
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml, OxmlElement

# 复用 docx_template 的工具函数
from docx_template import (
    save_doc, _set_east_asia, _set_cell_bg, _apply_run_style,
    _apply_profile_run, _apply_profile_para_fmt,
    build_default_profile, extract_format_profile, apply_format_profile,
    register_styles, setup_page, set_header_footer, add_toc, refresh_toc,
    STYLE_PRESETS,
)


# ============================================================
# A. 学位论文格式档案
# ============================================================

def build_thesis_profile():
    """
    通用学位论文格式档案（接近 GB/T 7713.1，国内多数高校通用）。
    在 formal_report 默认档案基础上扩展论文专用字段。
    """
    base = build_default_profile('formal_report')
    # 论文正文：1.5 倍行距（覆盖 formal_report 的固定 28pt）
    base['body']['line_spacing_multiple'] = 1.5
    base['body'].pop('line_spacing_pt', None)
    base['body']['first_line_indent_chars'] = 2
    base['body']['size_pt'] = 12  # 小四
    base['body']['font'] = '宋体'
    base['body']['east_asia'] = '宋体'

    # 一级标题三号(16pt)居中
    base['heading'][1].update({'font': '黑体', 'east_asia': '黑体', 'size_pt': 16,
                                'bold': True, 'alignment': 'center',
                                'space_before_pt': 24, 'space_after_pt': 18})
    base['heading'][2].update({'font': '黑体', 'east_asia': '黑体', 'size_pt': 14,
                                'bold': True, 'space_before_pt': 18, 'space_after_pt': 12})
    base['heading'][3].update({'font': '黑体', 'east_asia': '黑体', 'size_pt': 12,
                                'bold': True, 'space_before_pt': 12, 'space_after_pt': 6})

    # 论文专用样式
    base['figure_caption'] = {
        'font': '宋体', 'east_asia': '宋体', 'size_pt': 10.5,  # 五号
        'alignment': 'center', 'space_before_pt': 6, 'space_after_pt': 12,
        'label': '图', 'separator': '-',  # 图1-1
    }
    base['table_caption'] = {
        'font': '宋体', 'east_asia': '宋体', 'size_pt': 10.5,
        'alignment': 'center', 'space_before_pt': 12, 'space_after_pt': 6,
        'label': '表', 'separator': '-',
    }
    base['equation'] = {
        'font': 'Times New Roman', 'east_asia': '宋体', 'size_pt': 12,
        'alignment': 'center', 'separator': '-', 'left_paren': '(', 'right_paren': ')',
    }
    base['three_line_table'] = {
        'top_sz': 12, 'bottom_sz': 12,        # 上下粗线 1.5pt(=12 八分之一磅)
        'header_sz': 4,                        # 表头下细线 0.5pt
        'header_font': '黑体', 'header_east_asia': '黑体',
        'header_size_pt': 10.5, 'header_bold': True,
        'cell_font': '宋体', 'cell_east_asia': '宋体', 'cell_size_pt': 10.5,
    }
    base['references'] = {
        'font': '宋体', 'east_asia': '宋体', 'size_pt': 10.5,  # 五号
        'hanging_indent_pt': 24,              # 悬挂缩进约 2 字符
        'space_after_pt': 2,
    }
    base['sections'] = {
        'cover_page_num': False,              # 封面无页码
        'front_fmt': 'lowerRoman',            # 前置罗马数字
        'body_fmt': 'decimal', 'body_start': 1,  # 正文阿拉伯，从1重启
        'header_text': 'chapter',             # 正文页眉为章节标题
    }
    base['numbering'] = {
        'levels': [
            {'fmt': 'decimal', 'text': '%1', 'indent_cm': 0},
            {'fmt': 'decimal', 'text': '%1.%2', 'indent_cm': 0.74},
            {'fmt': 'decimal', 'text': '%1.%2.%3', 'indent_cm': 1.48},
        ],
    }
    base['_preset'] = 'thesis'
    return base


def extract_thesis_profile(template_path):
    """
    从学校模板抽取学位论文档案。
    复用 extract_format_profile 抽字体/字号/段落，再补检测三线表/分节特征。
    缺失项回退通用档案。
    """
    profile = extract_format_profile(template_path)
    default = build_thesis_profile()
    # 补齐论文专用键（模板抽不到的用通用默认）
    for key in ('figure_caption', 'table_caption', 'equation',
                'three_line_table', 'references', 'sections', 'numbering'):
        if key not in profile:
            profile[key] = copy.deepcopy(default[key])
    profile['_source'] = template_path
    profile['_preset'] = 'thesis'
    return profile


def resolve_thesis_profile(profile=None, ref=None, preset=None):
    """解析论文档案：profile > ref > preset(thesis)"""
    if profile:
        if isinstance(profile, str):
            from docx_template import load_profile
            return load_profile(profile)
        return profile
    if ref:
        return extract_thesis_profile(ref)
    return build_thesis_profile()


# ============================================================
# B. 封面与固定结构页
# ============================================================

def _add_centered_line(doc, text, font, size_pt, bold=False, space_after=12, east_asia=None):
    """加一个居中段落"""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(space_after)
    run = p.add_run(text)
    run.font.name = font
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    _set_east_asia(run, east_asia or font)
    return p


def add_thesis_cover(doc, info, profile=None):
    """
    论文封面。info 字段：
        school, title, author, student_id, supervisor, major, date
    """
    profile = profile or build_thesis_profile()
    # 顶部留白
    for _ in range(3):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(12)

    # 校名（初号黑体）
    if info.get('school'):
        _add_centered_line(doc, info['school'], '黑体', 36, bold=True, space_after=24, east_asia='黑体')

    # 论文类别（小初号）
    _add_centered_line(doc, '硕士学位论文', '黑体', 42, bold=True, space_after=36, east_asia='黑体')

    # 论文题目（一号黑体）
    if info.get('title'):
        for _ in range(2):
            doc.add_paragraph().paragraph_format.space_after = Pt(12)
        _add_centered_line(doc, info['title'], '黑体', 26, bold=True, space_after=48, east_asia='黑体')

    # 信息表（作者/学号/导师/专业/日期）
    for _ in range(2):
        doc.add_paragraph().paragraph_format.space_after = Pt(12)
    fields = [
        ('作    者', info.get('author', '')),
        ('学    号', info.get('student_id', '')),
        ('指导教师', info.get('supervisor', '')),
        ('学科专业', info.get('major', '')),
        ('完成日期', info.get('date', '')),
    ]
    for label, value in fields:
        if value:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(10)
            r1 = p.add_run(f'{label}：')
            r1.font.name = '宋体'; r1.font.size = Pt(16)
            _set_east_asia(r1, '宋体')
            r2 = p.add_run(value)
            r2.font.name = '宋体'; r2.font.size = Pt(16)
            _set_east_asia(r2, '宋体')
            # 下划线占位
            r2.font.underline = True

    doc.add_page_break()
    return doc


def add_declaration(doc, profile=None):
    """独创性声明与学位论文使用授权页（固定文本）"""
    profile = profile or build_thesis_profile()
    # 标题
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('独创性声明')
    r.font.name = '黑体'; r.font.size = Pt(16); r.font.bold = True
    _set_east_asia(r, '黑体')
    p.paragraph_format.space_after = Pt(18)

    body = (
        '本人声明所呈交的学位论文是本人在导师指导下进行的研究工作及取得的研究成果。'
        '据我所知，除了文中特别加以标注和致谢的地方外，论文中不包含其他人已经发表或撰写过的研究成果，'
        '也不包含为获得任何教育机构的学位或证书而使用过的材料。与我一同工作的同志对本研究所做的任何贡献'
        '均已在论文中作了明确的说明并表示谢意。'
    )
    p = doc.add_paragraph(body)
    p.paragraph_format.first_line_indent = Pt(24)
    p.paragraph_format.line_spacing = 1.5
    r = p.runs[0]; r.font.name = '宋体'; r.font.size = Pt(12)
    _set_east_asia(r, '宋体')

    doc.add_paragraph().paragraph_format.space_after = Pt(24)
    sig = doc.add_paragraph('学位论文作者签名：                日期：    年   月   日')
    sig.runs[0].font.name = '宋体'; sig.runs[0].font.size = Pt(12)
    _set_east_asia(sig.runs[0], '宋体')

    doc.add_page_break()
    return doc


def add_acknowledgement(doc, text, profile=None):
    """致谢页"""
    profile = profile or build_thesis_profile()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('致    谢')
    r.font.name = '黑体'; r.font.size = Pt(16); r.font.bold = True
    _set_east_asia(r, '黑体')
    p.paragraph_format.space_after = Pt(18)

    for para_text in (text if isinstance(text, list) else [text]):
        p = doc.add_paragraph(para_text)
        cfg = profile.get('body', {})
        if p.runs:
            _apply_profile_run(p.runs[0], cfg)
        _apply_profile_para_fmt(p, cfg)
    return doc


# ============================================================
# C. 多级标题编号
# ============================================================

def setup_multilevel_numbering(doc, profile=None):
    """
    写 numbering.xml：3 级编号 1 / 1.1 / 1.1.1，绑定 Heading 1/2/3。
    返回分配的 numId。
    """
    profile = profile or build_thesis_profile()
    levels = profile.get('numbering', {}).get('levels', [])
    numbering_part = doc.part.numbering_part
    numbering_el = numbering_part.element

    # 找一个未用的 abstractNumId
    existing_ids = [int(an.get(qn('w:abstractNumId')))
                    for an in numbering_el.findall(qn('w:abstractNum'))]
    abs_id = max(existing_ids) + 1 if existing_ids else 0

    # 构造 abstractNum
    lvl_defs = levels or [
        {'fmt': 'decimal', 'text': '%1', 'indent_cm': 0},
        {'fmt': 'decimal', 'text': '%1.%2', 'indent_cm': 0.74},
        {'fmt': 'decimal', 'text': '%1.%2.%3', 'indent_cm': 1.48},
    ]
    style_map = {0: 'Heading1', 1: 'Heading2', 2: 'Heading3'}
    lvls_xml = []
    for i, lvl in enumerate(lvl_defs[:3]):
        indent_twips = int(lvl.get('indent_cm', 0) * 567)
        lvls_xml.append(
            f'<w:lvl w:ilvl="{i}">'
            f'<w:start w:val="1"/>'
            f'<w:numFmt w:val="{lvl.get("fmt", "decimal")}"/>'
            f'<w:lvlText w:val="{lvl["text"]}"/>'
            f'<w:lvlJc w:val="left"/>'
            f'<w:pPr><w:ind w:left="{indent_twips}" w:hanging="360"/></w:pPr>'
            f'<w:pStyle w:val="{style_map[i]}"/>'
            f'</w:lvl>'
        )
    abs_xml = (f'<w:abstractNum {nsdecls("w")} w:abstractNumId="{abs_id}">'
               + ''.join(lvls_xml) + '</w:abstractNum>')

    # abstractNum 必须在 num 之前插入
    first_num = numbering_el.find(qn('w:num'))
    new_abs = parse_xml(abs_xml)
    if first_num is not None:
        first_num.addprevious(new_abs)
    else:
        numbering_el.append(new_abs)

    # 找一个未用的 numId
    existing_num_ids = [int(n.get(qn('w:numId')))
                        for n in numbering_el.findall(qn('w:num'))]
    num_id = max(existing_num_ids) + 1 if existing_num_ids else 1
    num_xml = (f'<w:num {nsdecls("w")} w:numId="{num_id}">'
               f'<w:abstractNumId w:val="{abs_id}"/></w:num>')
    numbering_el.append(parse_xml(num_xml))

    return num_id


def apply_heading_numbering(doc, num_id):
    """给已有 Heading 1/2/3 段落绑定 numId（仅未绑定的）"""
    style_lvl = {'Heading 1': 0, 'Heading 2': 1, 'Heading 3': 2}
    for para in doc.paragraphs:
        name = para.style.name if para.style else ''
        ilvl = style_lvl.get(name)
        if ilvl is None:
            continue
        pPr = para._element.get_or_add_pPr()
        if pPr.find(qn('w:numPr')) is not None:
            continue  # 已有编号，跳过
        numPr = parse_xml(
            f'<w:numPr {nsdecls("w")}>'
            f'<w:ilvl w:val="{ilvl}"/>'
            f'<w:numId w:val="{num_id}"/>'
            f'</w:numPr>'
        )
        pPr.append(numPr)
    return doc


# ============================================================
# D. 图表公式与题注
# ============================================================

def _append_field(paragraph, instr, cached='', run_fmt=None):
    """在段落中追加一个 Word 域（begin/instr/separate/cached/end）"""
    r1 = paragraph.add_run()
    r1._element.append(parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>'))
    r2 = paragraph.add_run()
    r2._element.append(parse_xml(
        f'<w:instrText {nsdecls("w")} xml:space="preserve">{instr}</w:instrText>'))
    r3 = paragraph.add_run()
    r3._element.append(parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="separate"/>'))
    r4 = paragraph.add_run(cached)
    r5 = paragraph.add_run()
    r5._element.append(parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>'))
    if run_fmt:
        for r in (r2, r4):
            _apply_profile_run(r, run_fmt)
    return paragraph


def _make_caption(doc, kind, caption_text, profile):
    """
    生成题注段落："图1-1 题名" / "表1-1 题名"。
    章号用 STYLEREF Heading 1 域，序号用 SEQ 域（按 kind 分组计数）。
    kind: 'figure_caption' 或 'table_caption'。
    返回题注段落（未插入文档，由调用方定位）。
    """
    cfg = profile.get(kind, profile.get('figure_caption', {}))
    label = cfg.get('label', '图' if kind == 'figure_caption' else '表')
    sep = cfg.get('separator', '-')

    p = doc.add_paragraph()
    _apply_profile_para_fmt(p, cfg)
    # 标签文字（图/表）
    r_label = p.add_run(label)
    _apply_profile_run(r_label, cfg)
    # 章号域 STYLEREF Heading 1
    _append_field(p, ' STYLEREF 1 \\n ', cached='1', run_fmt=cfg)
    # 分隔符
    r_sep = p.add_run(sep)
    _apply_profile_run(r_sep, cfg)
    # 序号域 SEQ 图 \* ARABIC \s 1 （\s 1 按一级标题重置计数）
    seq_name = label  # SEQ 域用"图"/"表"作为书签名
    _append_field(p, f' SEQ {seq_name} \\* ARABIC \\s 1 ', cached='1', run_fmt=cfg)
    # 空格 + 题名
    r_space = p.add_run(' ')
    _apply_profile_run(r_space, cfg)
    r_text = p.add_run(caption_text)
    _apply_profile_run(r_text, cfg)
    return p


def _move_after(ref_element, new_element):
    parent = ref_element.getparent()
    parent.insert(list(parent).index(ref_element) + 1, new_element)


def add_figure(doc, anchor_text, image_path, caption_text, width_cm=14, profile=None):
    """
    在锚点段落后插入：居中图片 + 图下题注。
    """
    profile = profile or build_thesis_profile()
    from docx_template import find_para_index
    idx = find_para_index(doc, anchor_text)
    if idx is None:
        raise ValueError(f'锚点文本未找到: {anchor_text}')
    ref = doc.paragraphs[idx]._element

    body_cfg = profile.get('body', {})
    # 图片段（居中）
    img_para = doc.add_paragraph()
    img_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    img_para.paragraph_format.space_after = Pt(6)
    if os.path.exists(image_path):
        run = img_para.add_run()
        run.add_picture(image_path, width=Cm(width_cm))
    _move_after(ref, img_para._element)
    ref = img_para._element

    # 题注段
    cap_para = _make_caption(doc, 'figure_caption', caption_text, profile)
    _move_after(ref, cap_para._element)
    return idx


def _set_three_line_borders(table, tlt_cfg):
    """三线表边框：上下粗线 + 表头下细线，无竖线无内横线"""
    sz_top = tlt_cfg.get('top_sz', 12)
    sz_bottom = tlt_cfg.get('bottom_sz', 12)
    sz_header = tlt_cfg.get('header_sz', 4)
    borders_xml = (
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="{sz_top}" w:space="0" w:color="000000"/>'
        f'<w:left w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        f'<w:bottom w:val="single" w:sz="{sz_bottom}" w:space="0" w:color="000000"/>'
        f'<w:right w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        f'<w:insideH w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        f'<w:insideV w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        f'</w:tblBorders>'
    )
    tblPr = table._tbl.tblPr
    old = tblPr.find(qn('w:tblBorders'))
    if old is not None:
        tblPr.remove(old)
    tblPr.append(parse_xml(borders_xml))

    # 表头行下边框（第一行 bottom）
    if len(table.rows) >= 1:
        for cell in table.rows[0].cells:
            tcPr = cell._tc.get_or_add_tcPr()
            tcBorders = parse_xml(
                f'<w:tcBorders {nsdecls("w")}>'
                f'<w:bottom w:val="single" w:sz="{sz_header}" w:space="0" w:color="000000"/>'
                f'</w:tcBorders>'
            )
            old_b = tcPr.find(qn('w:tcBorders'))
            if old_b is not None:
                tcPr.remove(old_b)
            tcPr.append(tcBorders)


def add_three_line_table(doc, anchor_text, headers, rows, caption_text, profile=None):
    """
    在锚点段落后插入：表上题注 + 三线表。
    """
    profile = profile or build_thesis_profile()
    from docx_template import find_para_index
    idx = find_para_index(doc, anchor_text)
    if idx is None:
        raise ValueError(f'锚点文本未找到: {anchor_text}')
    ref = doc.paragraphs[idx]._element

    tlt = profile.get('three_line_table', {})
    # 题注在表上方
    cap_para = _make_caption(doc, 'table_caption', caption_text, profile)
    _move_after(ref, cap_para._element)
    ref = cap_para._element

    # 三线表
    col_count = len(headers)
    table = doc.add_table(rows=1 + len(rows), cols=col_count)
    table.autofit = False
    # 列宽均分
    sec = doc.sections[0]
    total_twips = int((sec.page_width - sec.left_margin - sec.right_margin) / 914400 * 1440)
    col_w = int(total_twips / col_count) if col_count else total_twips
    for col in table.columns:
        for cell in col.cells:
            cell.width = Twips(col_w)

    # 表头
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ''
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(h)
        run.font.name = tlt.get('header_font', '黑体')
        run.font.size = Pt(tlt.get('header_size_pt', 10.5))
        run.font.bold = tlt.get('header_bold', True)
        _set_east_asia(run, tlt.get('header_east_asia', '黑体'))
    # 数据行
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = table.rows[r + 1].cells[c]
            cell.text = ''
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(str(val))
            run.font.name = tlt.get('cell_font', '宋体')
            run.font.size = Pt(tlt.get('cell_size_pt', 10.5))
            _set_east_asia(run, tlt.get('cell_east_asia', '宋体'))

    _set_three_line_borders(table, tlt)
    _move_after(ref, table._tbl)
    return idx


def add_equation(doc, anchor_text, text, profile=None):
    """
    在锚点段落后插入公式：居中公式 + 右编号"(章-序)"。
    """
    profile = profile or build_thesis_profile()
    from docx_template import find_para_index
    idx = find_para_index(doc, anchor_text)
    if idx is None:
        raise ValueError(f'锚点文本未找到: {anchor_text}')
    ref = doc.paragraphs[idx]._element

    cfg = profile.get('equation', {})
    p = doc.add_paragraph()
    _apply_profile_para_fmt(p, cfg)
    # 公式文本（居中）
    r_eq = p.add_run(text)
    _apply_profile_run(r_eq, cfg)
    # 制表符推到右侧
    r_tab = p.add_run('\t')
    _apply_profile_run(r_tab, cfg)
    # 右对齐制表位
    sec = doc.sections[0]
    right_pos = int((sec.page_width - sec.left_margin - sec.right_margin) / 914400 * 1440)
    pPr = p._element.get_or_add_pPr()
    tabs = parse_xml(
        f'<w:tabs {nsdecls("w")}><w:tab w:val="right" w:pos="{right_pos}"/></w:tabs>'
    )
    pPr.append(tabs)
    # 编号 (章-序)
    lp = cfg.get('left_paren', '(')
    rp = cfg.get('right_paren', ')')
    sep = cfg.get('separator', '-')
    r_lp = p.add_run(lp)
    _apply_profile_run(r_lp, cfg)
    _append_field(p, ' STYLEREF 1 \\n ', cached='1', run_fmt=cfg)
    r_sep = p.add_run(sep)
    _apply_profile_run(r_sep, cfg)
    _append_field(p, ' SEQ 公式 \\* ARABIC \\s 1 ', cached='1', run_fmt=cfg)
    r_rp = p.add_run(rp)
    _apply_profile_run(r_rp, cfg)

    _move_after(ref, p._element)
    return idx


# ============================================================
# E. 分节页码
# ============================================================

def set_section_page_number(section, fmt='decimal', start=None, link_previous=True):
    """
    设置某节页码格式。fmt: 'decimal'/'lowerRoman'/'upperRoman'。
    start: 指定则重启页码从该值开始。
    """
    sectPr = section._sectPr
    # 删除已有 pgNumType
    old = sectPr.find(qn('w:pgNumType'))
    if old is not None:
        sectPr.remove(old)
    attrs = f'w:fmt="{fmt}"'
    if start is not None:
        attrs += f' w:start="{start}"'
    pgNum = parse_xml(f'<w:pgNumType {nsdecls("w")} {attrs}/>')
    sectPr.append(pgNum)

    if not link_previous:
        # 取消页眉页脚与前节链接，使其独立
        for tag in ('headerReference', 'footerReference'):
            for ref in sectPr.findall(qn(f'w:{tag}')):
                sectPr.remove(ref)
    return section


def add_page_number_field(paragraph, fmt='decimal'):
    """在段落中插入 PAGE 域"""
    r1 = paragraph.add_run()
    r1._element.append(parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>'))
    r2 = paragraph.add_run()
    r2._element.append(parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve"> PAGE </w:instrText>'))
    r3 = paragraph.add_run()
    r3._element.append(parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="separate"/>'))
    r4 = paragraph.add_run('1')
    r4.font.size = Pt(9); r4.font.name = '宋体'
    _set_east_asia(r4, '宋体')
    r5 = paragraph.add_run()
    r5._element.append(parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>'))
    return paragraph


def setup_thesis_sections(doc, profile=None):
    """
    配置学位论文分节页码。
    假设文档已有分节符（或调用前已 add_section）。
    策略：第1节(封面)无页码；第2节(前置,摘要/目录)罗马数字；
         第3节起(正文)阿拉伯数字从1重启。
    若文档仅1节，则提示需先分节。
    """
    profile = profile or build_thesis_profile()
    sec_cfg = profile.get('sections', {})
    sections = doc.sections
    n = len(sections)
    if n < 3:
        # 文档不足3节，无法完整配置；尽力而为
        return False

    # 第1节：封面无页码 —— 不同首页 + 空页脚
    cover = sections[0]
    cover.different_first_page_header_footer = True
    # 清空封面页脚
    _clear_footer(cover)

    # 第2节：前置罗马数字
    front = sections[1]
    set_section_page_number(front, fmt=sec_cfg.get('front_fmt', 'lowerRoman'))
    _set_footer_page_number(front)

    # 第3节起：正文阿拉伯从1重启
    body_fmt = sec_cfg.get('body_fmt', 'decimal')
    body_start = sec_cfg.get('body_start', 1)
    for sec in sections[2:]:
        set_section_page_number(sec, fmt=body_fmt, start=body_start)
        _set_footer_page_number(sec)
    return True


def _clear_footer(section):
    """清空某节页脚（无页码）"""
    footer = section.footer
    footer.is_linked_to_previous = False
    for p in footer.paragraphs:
        for r in list(p.runs):
            r._element.getparent().remove(r._element)


def _set_footer_page_number(section):
    """在某节页脚居中插入页码域"""
    footer = section.footer
    footer.is_linked_to_previous = False
    if not footer.paragraphs:
        footer.add_paragraph()
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    # 清空已有内容
    for r in list(fp.runs):
        r._element.getparent().remove(r._element)
    add_page_number_field(fp)


# ============================================================
# F. 中英文摘要 / 参考文献
# ============================================================

def add_abstract(doc, zh_title, zh_body, zh_keywords,
                 en_title, en_body, en_keywords, profile=None):
    """
    插入中文摘要 + 分页 + 英文 Abstract。
    zh_body/en_body 可为字符串或字符串列表（多段）。
    """
    profile = profile or build_thesis_profile()
    body_cfg = profile.get('body', {})

    # --- 中文摘要 ---
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('摘    要')
    r.font.name = '黑体'; r.font.size = Pt(16); r.font.bold = True
    _set_east_asia(r, '黑体')
    p.paragraph_format.space_after = Pt(18)

    for para_text in (zh_body if isinstance(zh_body, list) else [zh_body]):
        p = doc.add_paragraph(para_text)
        if p.runs:
            _apply_profile_run(p.runs[0], body_cfg)
        _apply_profile_para_fmt(p, body_cfg)

    # 关键词
    if zh_keywords:
        p = doc.add_paragraph()
        r1 = p.add_run('关键词：')
        r1.font.name = '黑体'; r1.font.size = Pt(12); r1.font.bold = True
        _set_east_asia(r1, '黑体')
        r2 = p.add_run(zh_keywords if isinstance(zh_keywords, str) else '；'.join(zh_keywords))
        r2.font.name = '宋体'; r2.font.size = Pt(12)
        _set_east_asia(r2, '宋体')
        p.paragraph_format.space_before = Pt(12)

    doc.add_page_break()

    # --- 英文 Abstract ---
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('Abstract')
    r.font.name = 'Times New Roman'; r.font.size = Pt(16); r.font.bold = True
    p.paragraph_format.space_after = Pt(18)

    if en_title:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(en_title)
        r.font.name = 'Times New Roman'; r.font.size = Pt(14); r.font.bold = True
        p.paragraph_format.space_after = Pt(12)

    for para_text in (en_body if isinstance(en_body, list) else [en_body]):
        p = doc.add_paragraph(para_text)
        p.paragraph_format.first_line_indent = Pt(24)
        p.paragraph_format.line_spacing = 1.5
        if p.runs:
            p.runs[0].font.name = 'Times New Roman'
            p.runs[0].font.size = Pt(12)

    if en_keywords:
        p = doc.add_paragraph()
        r1 = p.add_run('Keywords: ')
        r1.font.name = 'Times New Roman'; r1.font.size = Pt(12); r1.font.bold = True
        r2 = p.add_run(en_keywords if isinstance(en_keywords, str) else '; '.join(en_keywords))
        r2.font.name = 'Times New Roman'; r2.font.size = Pt(12)
        p.paragraph_format.space_before = Pt(12)

    doc.add_page_break()
    return doc


def _format_reference(item, idx):
    """
    GB/T 7714 简化格式化。
    item 字段：authors, title, source, year, volume/issue, pages, type
    type: journal/book/conference/thesis
    """
    t = item.get('type', 'journal')
    authors = item.get('authors', '')
    title = item.get('title', '')
    source = item.get('source', '')
    year = item.get('year', '')
    vol = item.get('volume', '')
    issue = item.get('issue', '')
    pages = item.get('pages', '')

    if t == 'journal':
        # 作者. 题名[J]. 刊名, 年, 卷(期): 起止页码.
        s = f'{authors}. {title}[J]. {source}, {year}'
        if vol:
            s += f', {vol}'
        if issue:
            s += f'({issue})'
        if pages:
            s += f': {pages}'
        s += '.'
    elif t == 'book':
        # 作者. 书名[M]. 出版地: 出版者, 年.
        pub = item.get('publisher', '')
        place = item.get('place', '')
        s = f'{authors}. {title}[M]. {place}: {pub}, {year}.' if pub else f'{authors}. {title}[M]. {year}.'
    elif t == 'conference':
        s = f'{authors}. {title}[C]//{source}. {year}'
        if pages:
            s += f': {pages}'
        s += '.'
    elif t == 'thesis':
        degree = item.get('degree', '博士')
        s = f'{authors}. {title}[{degree[0]}]. {source}, {year}.'
    else:
        s = f'{authors}. {title}. {source}, {year}.'
    return f'[{idx}] {s}'


def add_references(doc, items, profile=None):
    """
    插入参考文献章节。items: dict 列表（见 _format_reference）。
    自动 [1][2] 编号 + 悬挂缩进。
    """
    profile = profile or build_thesis_profile()
    ref_cfg = profile.get('references', {})

    # 章节标题
    p = doc.add_paragraph()
    p.style = doc.styles['Heading 1']
    r = p.add_run('参考文献')
    h1 = profile.get('heading', {}).get(1, {})
    _apply_profile_run(r, h1)
    _apply_profile_para_fmt(p, h1)

    for i, item in enumerate(items, 1):
        text = _format_reference(item, i) if isinstance(item, dict) else f'[{i}] {item}'
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.left_indent = Pt(ref_cfg.get('hanging_indent_pt', 24))
        pf.first_line_indent = Pt(-ref_cfg.get('hanging_indent_pt', 24))
        pf.space_after = Pt(ref_cfg.get('space_after_pt', 2))
        pf.line_spacing = 1.5
        run = p.add_run(text)
        _apply_profile_run(run, ref_cfg)
    return doc


# ============================================================
# G. 图表索引
# ============================================================

def add_list_of_figures(doc, title='图  录', profile=None):
    r"""插入图索引（TOC 域带 \c "图" 开关）"""
    _add_toc_field(doc, title, seq_name='图', profile=profile or build_thesis_profile())
    return doc


def add_list_of_tables(doc, title='表  录', profile=None):
    r"""插入表索引"""
    _add_toc_field(doc, title, seq_name='表', profile=profile or build_thesis_profile())
    return doc


def _add_toc_field(doc, title, seq_name, profile):
    r"""通用图表索引：TOC \c seq_name"""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(title)
    r.font.name = '黑体'; r.font.size = Pt(16); r.font.bold = True
    _set_east_asia(r, '黑体')
    p.paragraph_format.space_after = Pt(12)

    para = doc.add_paragraph()
    _append_field(para, f' TOC \\h \\z \\c "{seq_name}" ',
                  cached='（请在 Word 中按 Ctrl+A 然后 F9 更新图表索引）')
    doc.add_page_break()
    return doc


# ============================================================
# H. 一键论文骨架
# ============================================================

def build_thesis_skeleton(spec):
    """
    从 JSON 规范生成完整学位论文骨架。
    spec 字段：
        output, school, title, author, student_id, supervisor, major, date,
        zh_abstract{title,body,keywords}, en_abstract{title,body,keywords},
        chapters:[{title, sections:[{title, paragraphs:[str]}]}],
        references:[{...}],
        acknowledgement: str,
        profile(ref 路径或 dict，可选)
    """
    profile = resolve_thesis_profile(spec.get('profile'), spec.get('ref'))

    doc = Document()
    setup_page(doc, profile.get('page'))
    register_styles(doc, 'formal_report')

    # 1. 封面（独立一节，无页码）
    add_thesis_cover(doc, {
        'school': spec.get('school', ''),
        'title': spec.get('title', ''),
        'author': spec.get('author', ''),
        'student_id': spec.get('student_id', ''),
        'supervisor': spec.get('supervisor', ''),
        'major': spec.get('major', ''),
        'date': spec.get('date', ''),
    }, profile)
    _add_section_break(doc)  # 封面节结束 → 前置节

    # 2. 独创性声明
    add_declaration(doc, profile)

    # 3. 中英文摘要（前置节）
    zh = spec.get('zh_abstract', {})
    en = spec.get('en_abstract', {})
    add_abstract(doc,
                 zh.get('title', spec.get('title', '')),
                 zh.get('body', ''),
                 zh.get('keywords', ''),
                 en.get('title', ''),
                 en.get('body', ''),
                 en.get('keywords', ''),
                 profile)

    # 4. 目录
    add_toc(doc)
    # 5. 图表索引
    add_list_of_figures(doc, profile=profile)
    add_list_of_tables(doc, profile=profile)

    # 正文前插入分节符（让正文成为新节，便于页码重启）
    # 通过分页 + section 实现：此处先加一个分节符
    _add_section_break(doc)

    # 6. 正文章节（带多级编号）
    num_id = setup_multilevel_numbering(doc, profile)
    body_cfg = profile.get('body', {})
    for ch in spec.get('chapters', []):
        p = doc.add_paragraph(ch.get('title', ''), style='Heading 1')
        if p.runs:
            _apply_profile_run(p.runs[0], profile['heading'][1])
        _apply_profile_para_fmt(p, profile['heading'][1])
        for sec in ch.get('sections', []):
            p = doc.add_paragraph(sec.get('title', ''), style='Heading 2')
            if p.runs:
                _apply_profile_run(p.runs[0], profile['heading'][2])
            _apply_profile_para_fmt(p, profile['heading'][2])
            for para_text in sec.get('paragraphs', []):
                p = doc.add_paragraph(para_text)
                if p.runs:
                    _apply_profile_run(p.runs[0], body_cfg)
                _apply_profile_para_fmt(p, body_cfg)
    apply_heading_numbering(doc, num_id)

    # 7. 参考文献
    add_references(doc, spec.get('references', []), profile)

    # 8. 致谢
    if spec.get('acknowledgement'):
        doc.add_page_break()
        add_acknowledgement(doc, spec['acknowledgement'], profile)

    # 配置分节页码（需 ≥3 节）
    setup_thesis_sections(doc, profile)
    # 标记所有域待更新
    refresh_toc(doc)

    output = spec.get('output', '论文.docx')
    save_doc(doc, output)
    return output


def _add_section_break(doc):
    """插入一个分节符（下一页），用于分隔前置与正文"""
    from docx.enum.section import WD_SECTION_START
    new_sec = doc.add_section(WD_SECTION_START.NEW_PAGE)
    return new_sec

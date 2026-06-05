"""
docx_template.py — 基于 python-docx 的模板填充核心库

提供格式复制、占位符查找、段落插入、图片嵌入、封面/目录/页眉页脚等可复用函数。
支持两种模式：
1. 模板填充：保留模板原始格式，按占位符替换内容
2. 从零创建：按 JSON 规范生成标准格式文档
"""
import os
import copy
import json
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor, Emu, Twips
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml


# ============================================================
# 格式复制
# ============================================================

def copy_run_format(src_run, dst_run):
    """复制 run 级格式：字体、字号、粗体、颜色、斜体、下划线"""
    if src_run.font.size:
        dst_run.font.size = src_run.font.size
    if src_run.font.name:
        dst_run.font.name = src_run.font.name
    # 东亚字体（中文）
    try:
        rpr = src_run._element.rPr
        if rpr is not None:
            rFonts = rpr.find(qn('w:rFonts'))
            if rFonts is not None:
                ea = rFonts.get(qn('w:eastAsia'))
                if ea:
                    dst_run._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), ea)
    except Exception:
        pass
    if src_run.font.bold is not None:
        dst_run.font.bold = src_run.font.bold
    if src_run.font.color and src_run.font.color.rgb:
        dst_run.font.color.rgb = src_run.font.color.rgb
    dst_run.font.italic = src_run.font.italic
    dst_run.font.underline = src_run.font.underline


def copy_para_format(src_para, dst_para):
    """复制段落级格式：对齐、间距、行距、首行缩进"""
    if src_para.alignment is not None:
        dst_para.alignment = src_para.alignment
    pf = src_para.paragraph_format
    dpf = dst_para.paragraph_format
    if pf.space_before is not None:
        dpf.space_before = pf.space_before
    if pf.space_after is not None:
        dpf.space_after = pf.space_after
    if pf.line_spacing is not None:
        dpf.line_spacing = pf.line_spacing
    if pf.first_line_indent is not None:
        dpf.first_line_indent = pf.first_line_indent


# ============================================================
# 段落查找
# ============================================================

def find_para_index(doc, search_text, start=0):
    """找到包含指定文本的段落索引，从 start 开始搜索"""
    for i in range(start, len(doc.paragraphs)):
        if search_text in doc.paragraphs[i].text:
            return i
    return None


def find_para_indices(doc, search_text):
    """找到所有包含指定文本的段落索引列表"""
    return [i for i, p in enumerate(doc.paragraphs) if search_text in p.text]


def get_normal_ref(doc):
    """找到一个 Normal 样式且有内容的段落作为格式参考"""
    for p in doc.paragraphs:
        if p.style.name == 'Normal' and p.text.strip() and p.runs:
            return p
    return doc.paragraphs[1] if len(doc.paragraphs) > 1 else doc.paragraphs[0]


# ============================================================
# 段落操作
# ============================================================

def clear_runs(para):
    """清空段落中的所有 runs"""
    for r in para.runs:
        r._element.getparent().remove(r._element)


def add_styled_para(doc, text, ref_para, bold=False, size_pt=None, font_name=None, color=None, alignment=None):
    """
    添加一个新段落，格式参照 ref_para。
    可通过 kwargs 覆盖部分格式。
    返回新段落对象。
    """
    new_para = doc.add_paragraph()
    copy_para_format(ref_para, new_para)
    if alignment is not None:
        new_para.alignment = alignment
    run = new_para.add_run(text)
    if ref_para.runs:
        copy_run_format(ref_para.runs[0], run)
    if bold:
        run.font.bold = True
    if size_pt:
        run.font.size = Pt(size_pt)
    if font_name:
        run.font.name = font_name
        run._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), font_name)
    if color:
        run.font.color.rgb = RGBColor(*color)
    return new_para


def insert_paras_after(doc, after_idx, paragraphs_text, ref_para, **kwargs):
    """
    在 after_idx 段落之后依次插入多个新段落。
    每个段落的格式参照 ref_para。
    返回最后插入的段落索引。
    """
    ref_element = doc.paragraphs[after_idx]._element
    parent = ref_element.getparent()
    insert_after = ref_element
    last_idx = after_idx

    for text in paragraphs_text:
        if not text.strip():
            continue
        new_para = doc.add_paragraph()
        copy_para_format(ref_para, new_para)
        run = new_para.add_run(text)
        if ref_para.runs:
            copy_run_format(ref_para.runs[0], run)
        if kwargs.get('bold'):
            run.font.bold = True
        if kwargs.get('size_pt'):
            run.font.size = Pt(kwargs['size_pt'])
        if kwargs.get('font_name'):
            run.font.name = kwargs['font_name']
            run._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), kwargs['font_name'])
        if kwargs.get('color'):
            run.font.color.rgb = RGBColor(*kwargs['color'])

        new_element = new_para._element
        parent.insert(list(parent).index(insert_after) + 1, new_element)
        insert_after = new_element
        last_idx += 1

    return last_idx


def replace_para_text(doc, idx, new_text, bold=False, size_pt=None, font_name=None, color=None):
    """替换指定段落的文本内容，保留段落格式"""
    p = doc.paragraphs[idx]
    clear_runs(p)
    run = p.add_run(new_text)
    if bold:
        run.font.bold = True
    if size_pt:
        run.font.size = Pt(size_pt)
    if font_name:
        run.font.name = font_name
        run._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), font_name)
    if color:
        run.font.color.rgb = RGBColor(*color)
    return p


def remove_paras_between(doc, start_idx, end_idx):
    """删除 start_idx（不含）到 end_idx（不含）之间的所有段落"""
    parent = doc.paragraphs[start_idx]._element.getparent()
    for i in range(end_idx - 1, start_idx, -1):
        el = doc.paragraphs[i]._element
        parent.remove(el)


# ============================================================
# 图片操作
# ============================================================

def add_image_after(doc, para_idx, image_path, width_inches=5.5, centered=True):
    """
    在指定段落后插入图片。
    返回图片段落对象。
    """
    ref_element = doc.paragraphs[para_idx]._element
    parent = ref_element.getparent()

    img_para = doc.add_paragraph()
    if centered:
        img_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = img_para.add_run()
    if os.path.exists(image_path):
        run.add_picture(image_path, width=Inches(width_inches))

    new_element = img_para._element
    parent.insert(list(parent).index(ref_element) + 1, new_element)
    return img_para


# ============================================================
# 文档加载与保存
# ============================================================

def load_template(template_path):
    """加载 Word 模板"""
    return Document(template_path)


def save_doc(doc, output_path):
    """保存文档，自动创建输出目录"""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    doc.save(output_path)
    return output_path


# ============================================================
# 样式注册（从零创建模式）
# ============================================================

# 预设样式配置
STYLE_PRESETS = {
    'formal_report': {
        'page': {'size': 'A4', 'margins': {'top': 2.54, 'right': 3.17, 'bottom': 2.54, 'left': 3.17}},
        'styles': {
            'Title': {'font': '黑体', 'east_asia': '黑体', 'size_pt': 26, 'bold': True, 'centered': True,
                      'space_after_pt': 12},
            'Subtitle': {'font': '宋体', 'east_asia': '宋体', 'size_pt': 16, 'centered': True,
                         'space_before_pt': 12},
            'Heading 1': {'font': '黑体', 'east_asia': '黑体', 'size_pt': 16, 'bold': True,
                          'space_before_pt': 12, 'space_after_pt': 6},
            'Heading 2': {'font': '黑体', 'east_asia': '黑体', 'size_pt': 14, 'bold': True,
                          'space_before_pt': 8, 'space_after_pt': 4},
            'Heading 3': {'font': '黑体', 'east_asia': '黑体', 'size_pt': 12, 'bold': True,
                          'space_before_pt': 6, 'space_after_pt': 3},
            'Heading 4': {'font': '黑体', 'east_asia': '黑体', 'size_pt': 12, 'bold': False,
                          'space_before_pt': 4, 'space_after_pt': 2},
            'Body Text': {'font': '宋体', 'east_asia': '宋体', 'size_pt': 12,
                          'line_spacing_pt': 28, 'first_line_indent_chars': 2,
                          'space_after_pt': 0, 'space_before_pt': 0},
            'Code Block': {'font': 'Consolas', 'east_asia': '宋体', 'size_pt': 9,
                           'bg_color': 'F2F2F2', 'border': True, 'indent_cm': 1,
                           'line_spacing_pt': 16, 'space_before_pt': 3, 'space_after_pt': 3},
            'Table Header': {'font': '黑体', 'east_asia': '黑体', 'size_pt': 10.5, 'bold': True,
                             'bg_color': 'D5E8F0'},
            'Table Cell': {'font': '宋体', 'east_asia': '宋体', 'size_pt': 10.5,
                           'line_spacing_pt': 18},
            'Caption': {'font': '宋体', 'east_asia': '宋体', 'size_pt': 9, 'centered': True,
                        'bold': True, 'space_before_pt': 6, 'space_after_pt': 6},
        }
    },
    'tech_spec': {
        'page': {'size': 'A4', 'margins': {'top': 2.54, 'right': 3.17, 'bottom': 2.54, 'left': 3.17}},
        'styles': {
            'Title': {'font': '黑体', 'east_asia': '黑体', 'size_pt': 26, 'bold': True, 'centered': True,
                      'space_after_pt': 12},
            'Subtitle': {'font': '宋体', 'east_asia': '宋体', 'size_pt': 16, 'centered': True,
                         'space_before_pt': 12},
            'Heading 1': {'font': '黑体', 'east_asia': '黑体', 'size_pt': 16, 'bold': True,
                          'space_before_pt': 12, 'space_after_pt': 6},
            'Heading 2': {'font': '黑体', 'east_asia': '黑体', 'size_pt': 14, 'bold': True,
                          'space_before_pt': 8, 'space_after_pt': 4},
            'Heading 3': {'font': '黑体', 'east_asia': '黑体', 'size_pt': 12, 'bold': True,
                          'space_before_pt': 6, 'space_after_pt': 3},
            'Heading 4': {'font': '黑体', 'east_asia': '黑体', 'size_pt': 12, 'bold': False,
                          'space_before_pt': 4, 'space_after_pt': 2},
            'Body Text': {'font': '宋体', 'east_asia': '宋体', 'size_pt': 12,
                          'line_spacing_pt': 28, 'first_line_indent_chars': 2,
                          'space_after_pt': 0, 'space_before_pt': 0},
            'Code Block': {'font': 'Consolas', 'east_asia': '宋体', 'size_pt': 9,
                           'bg_color': 'F2F2F2', 'border': True, 'indent_cm': 1,
                           'line_spacing_pt': 16, 'space_before_pt': 3, 'space_after_pt': 3},
            'Table Header': {'font': '黑体', 'east_asia': '黑体', 'size_pt': 9, 'bold': True,
                             'bg_color': 'D5E8F0'},
            'Table Cell': {'font': '宋体', 'east_asia': '宋体', 'size_pt': 9,
                           'line_spacing_pt': 16},
            'Caption': {'font': '宋体', 'east_asia': '宋体', 'size_pt': 9, 'centered': True,
                        'bold': True, 'space_before_pt': 6, 'space_after_pt': 6},
        }
    },
    'manual': {
        'page': {'size': 'A4', 'margins': {'top': 2.54, 'right': 3.17, 'bottom': 2.54, 'left': 3.17}},
        'styles': {
            'Title': {'font': '黑体', 'east_asia': '黑体', 'size_pt': 26, 'bold': True, 'centered': True,
                      'space_after_pt': 12},
            'Subtitle': {'font': '宋体', 'east_asia': '宋体', 'size_pt': 16, 'centered': True,
                         'space_before_pt': 12},
            'Heading 1': {'font': '黑体', 'east_asia': '黑体', 'size_pt': 16, 'bold': True,
                          'space_before_pt': 12, 'space_after_pt': 6},
            'Heading 2': {'font': '黑体', 'east_asia': '黑体', 'size_pt': 14, 'bold': True,
                          'space_before_pt': 8, 'space_after_pt': 4},
            'Heading 3': {'font': '黑体', 'east_asia': '黑体', 'size_pt': 12, 'bold': True,
                          'space_before_pt': 6, 'space_after_pt': 3},
            'Body Text': {'font': '宋体', 'east_asia': '宋体', 'size_pt': 12,
                          'line_spacing_pt': 28, 'first_line_indent_chars': 0,
                          'space_after_pt': 0, 'space_before_pt': 0},
            'Code Block': {'font': 'Consolas', 'east_asia': '宋体', 'size_pt': 10,
                           'bg_color': 'F2F2F2', 'border': True, 'indent_cm': 1,
                           'line_spacing_pt': 16, 'space_before_pt': 3, 'space_after_pt': 3},
            'Note': {'font': '楷体', 'east_asia': '楷体', 'size_pt': 11, 'color': '666666',
                     'space_before_pt': 6, 'space_after_pt': 6},
            'Table Header': {'font': '黑体', 'east_asia': '黑体', 'size_pt': 10.5, 'bold': True,
                             'bg_color': 'D5E8F0'},
            'Table Cell': {'font': '宋体', 'east_asia': '宋体', 'size_pt': 10.5,
                           'line_spacing_pt': 18},
        }
    },
    'checklist': {
        'page': {'size': 'A4', 'margins': {'top': 2.54, 'right': 2.0, 'bottom': 2.54, 'left': 2.0}},
        'styles': {
            'Title': {'font': '黑体', 'east_asia': '黑体', 'size_pt': 18, 'bold': True, 'centered': True,
                      'space_after_pt': 12},
            'Heading 1': {'font': '黑体', 'east_asia': '黑体', 'size_pt': 14, 'bold': True,
                          'space_before_pt': 8, 'space_after_pt': 4},
            'Body Text': {'font': '宋体', 'east_asia': '宋体', 'size_pt': 10.5,
                          'line_spacing_pt': 22, 'first_line_indent_chars': 0,
                          'space_after_pt': 0, 'space_before_pt': 0},
            'Table Header': {'font': '黑体', 'east_asia': '黑体', 'size_pt': 10.5, 'bold': True,
                             'bg_color': 'D5E8F0'},
            'Table Cell': {'font': '宋体', 'east_asia': '宋体', 'size_pt': 10.5,
                           'line_spacing_pt': 18},
        }
    },
}

# 文档注册表：每种文档类型的默认配置
DOC_REGISTRY = {
    '项目计划书': {
        'preset': 'formal_report', 'doc_name': '项目计划书',
        'sections': ['项目背景', '项目目标', '项目范围', '项目组织', '进度计划', '资源需求', '风险分析']
    },
    '需求说明书': {
        'preset': 'formal_report', 'doc_name': '需求说明书',
        'sections': ['项目概述', '功能需求', '非功能需求', '约束条件', '验收标准']
    },
    '现状分析报告': {
        'preset': 'formal_report', 'doc_name': '现状分析报告',
        'sections': ['分析背景', '现状概述', '问题分析', '差距分析', '改进建议']
    },
    '关键业务方案': {
        'preset': 'formal_report', 'doc_name': '关键业务方案',
        'sections': ['业务场景', '方案设计', '方案对比', '结论与建议']
    },
    '流程文档': {
        'preset': 'formal_report', 'doc_name': '流程文档',
        'sections': ['流程概述', '角色职责', '流程步骤', '异常处理', '流程图']
    },
    '测试文档': {
        'preset': 'formal_report', 'doc_name': '测试文档',
        'sections': ['测试概述', '测试计划', '测试用例', '测试执行', '缺陷记录', '测试报告']
    },
    '技术设计说明书': {
        'preset': 'tech_spec', 'doc_name': '技术设计说明书',
        'sections': ['系统概述', '系统架构', '模块设计', '接口定义', '数据流设计', '部署架构']
    },
    '数据库设计说明书': {
        'preset': 'tech_spec', 'doc_name': '数据库设计说明书',
        'sections': ['概述', 'ER模型', '表结构设计', '索引设计', '数据字典', 'SQL脚本']
    },
    '系统集成及接口设计功能说明书': {
        'preset': 'tech_spec', 'doc_name': '系统集成及接口设计功能说明书',
        'sections': ['接口概述', '接口列表', '协议规范', '数据格式', '错误码定义', '安全策略']
    },
    '二次开发及接口部署文档': {
        'preset': 'tech_spec', 'doc_name': '二次开发及接口部署文档',
        'sections': ['开发环境', '架构说明', '接口说明', '开发示例', '部署步骤', '常见问题']
    },
    '安装部署文档': {
        'preset': 'manual', 'doc_name': '安装部署文档',
        'sections': ['环境要求', '安装步骤', '配置说明', '验证方法', '回退方案']
    },
    '日常运维手册': {
        'preset': 'manual', 'doc_name': '日常运维手册',
        'sections': ['运维概述', '日常巡检', '监控告警', '日志管理', '应急处理']
    },
    '服务器启停手册': {
        'preset': 'manual', 'doc_name': '服务器启停手册',
        'sections': ['启动前检查', '启动顺序', '停止顺序', '异常处理']
    },
    '数据备份操作手册': {
        'preset': 'manual', 'doc_name': '数据备份操作手册',
        'sections': ['备份策略', '备份操作', '数据恢复', '恢复验证', '注意事项']
    },
    '权限配置管理手册': {
        'preset': 'manual', 'doc_name': '权限配置管理手册',
        'sections': ['角色定义', '权限矩阵', '配置步骤', '审计日志']
    },
    '应用系统常见问题及处理手册': {
        'preset': 'manual', 'doc_name': '应用系统常见问题及处理手册',
        'sections': ['常见问题分类', '问题排查流程', '问题与解答', '联系支持']
    },
    '用户培训资料及操作手册': {
        'preset': 'manual', 'doc_name': '用户培训资料及操作手册',
        'sections': ['系统介绍', '功能模块', '操作流程', '常见问题', '练习题']
    },
    '编译和打包的说明': {
        'preset': 'manual', 'doc_name': '编译和打包的说明',
        'sections': ['环境要求', '依赖说明', '编译命令', '打包流程', '常见问题']
    },
    '数据收集资料': {
        'preset': 'checklist', 'doc_name': '数据收集资料',
        'sections': ['数据说明', '数据清单'],
        'table_columns': ['序号', '数据名称', '数据来源', '数据格式', '收集周期', '负责人']
    },
    '项目问题清单': {
        'preset': 'checklist', 'doc_name': '项目问题清单',
        'sections': ['问题清单'],
        'table_columns': ['编号', '问题描述', '优先级', '状态', '责任人', '处理方案', '备注']
    },
    '管理员账号密码清单': {
        'preset': 'checklist', 'doc_name': '管理员账号密码清单',
        'sections': ['账号清单'],
        'table_columns': ['系统名称', '服务器地址', '账号', '密码', '权限', '备注']
    },
    '源代码交付清单': {
        'preset': 'checklist', 'doc_name': '源代码交付清单',
        'sections': ['交付清单'],
        'table_columns': ['模块名称', '源码目录', '文件数量', '代码行数', '版本号', '备注']
    },
}


# ============================================================
# 页面与样式设置（从零创建模式）
# ============================================================

def _cm_to_emu(cm):
    """厘米转 EMU"""
    return int(cm * 360000)


def _mm_to_twips(mm):
    """毫米转 Twips (1 inch = 1440 Twips, 1 mm = 56.7 Twips)"""
    return int(mm * 56.7)


def setup_page(doc, page_config=None):
    """
    设置页面布局（A4、页边距）。
    page_config: 可选的页面配置字典，覆盖预设默认值。
    """
    section = doc.sections[0]
    section.page_width = Cm(21.0)   # A4 宽
    section.page_height = Cm(29.7)  # A4 高
    section.orientation = WD_ORIENT.PORTRAIT

    margins = (page_config or {}).get('margins', {'top': 2.54, 'right': 3.17, 'bottom': 2.54, 'left': 3.17})
    section.top_margin = Cm(margins.get('top', 2.54))
    section.right_margin = Cm(margins.get('right', 3.17))
    section.bottom_margin = Cm(margins.get('bottom', 2.54))
    section.left_margin = Cm(margins.get('left', 3.17))
    return section


def register_styles(doc, preset_name='formal_report'):
    """
    注册预设文档样式。
    preset_name: 'formal_report', 'tech_spec', 'manual', 'checklist'
    """
    preset = STYLE_PRESETS.get(preset_name, STYLE_PRESETS['formal_report'])
    for style_name, config in preset.get('styles', {}).items():
        _register_single_style(doc, style_name, config)
    return preset


def _register_single_style(doc, style_name, config):
    """注册单个段落样式"""
    try:
        style = doc.styles[style_name]
    except KeyError:
        try:
            style = doc.styles.add_style(style_name, 1)  # 1 = WD_STYLE_TYPE.PARAGRAPH
        except Exception:
            return

    font = style.font
    pf = style.paragraph_format

    font.name = config.get('font', '宋体')
    font.size = Pt(config.get('size_pt', 12))
    font.bold = config.get('bold', None)

    # 东亚字体
    east_asia = config.get('east_asia')
    if east_asia:
        rpr = style.element.get_or_add_rPr()
        rFonts = rpr.find(qn('w:rFonts'))
        if rFonts is None:
            rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:eastAsia="{east_asia}"/>')
            rpr.insert(0, rFonts)
        else:
            rFonts.set(qn('w:eastAsia'), east_asia)

    # 颜色
    color_hex = config.get('color')
    if color_hex:
        font.color.rgb = RGBColor.from_string(color_hex)

    # 段落格式
    if config.get('centered'):
        pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if config.get('space_before_pt') is not None:
        pf.space_before = Pt(config['space_before_pt'])
    if config.get('space_after_pt') is not None:
        pf.space_after = Pt(config['space_after_pt'])
    if config.get('line_spacing_pt') is not None:
        pf.line_spacing = Pt(config['line_spacing_pt'])
    if config.get('first_line_indent_chars') is not None:
        pf.first_line_indent = Pt(config['first_line_indent_chars'] * 24)  # 约 2 字符


# ============================================================
# 封面页
# ============================================================

def add_cover_page(doc, project_name='', doc_name='', version='', date='', author='', reviewer=''):
    """
    添加封面页。
    封面格式：居中排列，项目名称（小二号黑体）、文档名称（小初号黑体）、
    版本号、日期、编制人、审核人。
    """
    # 添加空段落作为顶部间距
    for _ in range(4):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(12)

    # 项目名称
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(project_name)
    run.font.name = '黑体'
    run.font.size = Pt(22)
    run.font.bold = True
    _set_east_asia(run, '黑体')

    # 空行
    doc.add_paragraph().paragraph_format.space_after = Pt(24)

    # 文档名称
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(doc_name)
    run.font.name = '黑体'
    run.font.size = Pt(36)
    run.font.bold = True
    _set_east_asia(run, '黑体')

    # 多个空行
    for _ in range(3):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(12)

    # 元信息
    meta_items = []
    if version:
        meta_items.append(('版 本 号', version))
    if date:
        meta_items.append(('编制日期', date))
    if author:
        meta_items.append(('编 制 人', author))
    if reviewer:
        meta_items.append(('审 核 人', reviewer))

    for label, value in meta_items:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_label = p.add_run(f'{label}：')
        run_label.font.name = '宋体'
        run_label.font.size = Pt(14)
        _set_east_asia(run_label, '宋体')
        run_val = p.add_run(value)
        run_val.font.name = '宋体'
        run_val.font.size = Pt(14)
        _set_east_asia(run_val, '宋体')

    # 分页
    doc.add_page_break()


# ============================================================
# 目录页
# ============================================================

def add_toc(doc, title='目  录'):
    """
    添加自动目录页。
    目录使用 TOC 域代码，在 Word 中打开后按 Ctrl+A → F9 可更新。
    """
    # 目录标题
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(title)
    run.font.name = '黑体'
    run.font.size = Pt(16)
    run.font.bold = True
    _set_east_asia(run, '黑体')

    # 空行
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # 插入 TOC 域
    paragraph = doc.add_paragraph()
    run = paragraph.add_run()
    fldChar1 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>')
    run._element.append(fldChar1)

    run2 = paragraph.add_run()
    instrText = parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve"> TOC \\o "1-3" \\h \\z \\u </w:instrText>')
    run2._element.append(instrText)

    run3 = paragraph.add_run()
    fldChar2 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="separate"/>')
    run3._element.append(fldChar2)

    run4 = paragraph.add_run('（请在 Word 中按 Ctrl+A 然后 F9 更新目录）')
    run4.font.color.rgb = RGBColor(128, 128, 128)
    run4.font.size = Pt(10)

    run5 = paragraph.add_run()
    fldChar3 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>')
    run5._element.append(fldChar3)

    # 分页
    doc.add_page_break()


# ============================================================
# 页眉页脚
# ============================================================

def set_header_footer(doc, header_left='', header_right='', footer_text=''):
    """
    设置页眉页脚。
    header_left: 页眉左侧文字（如项目名称）
    header_right: 页眉右侧文字（如文档名称）
    footer_text: 页脚文字，支持 {{page}} 占位符表示页码
    """
    section = doc.sections[0]
    section.different_first_page_header_footer = True

    # --- 页眉 ---
    header = section.header
    if not header.paragraphs:
        header.add_paragraph()

    hp = header.paragraphs[0]
    hp.clear()

    # 左侧文字
    if header_left:
        run_left = hp.add_run(header_left)
        run_left.font.name = '宋体'
        run_left.font.size = Pt(9)
        _set_east_asia(run_left, '宋体')

    # 添加制表位实现右对齐
    if header_right:
        # 添加 tab
        tab_run = hp.add_run('\t')
        tab_run.font.size = Pt(9)

        run_right = hp.add_run(header_right)
        run_right.font.name = '宋体'
        run_right.font.size = Pt(9)
        _set_east_asia(run_right, '宋体')

        # 设置右对齐制表位
        pPr = hp._element.get_or_add_pPr()
        tabs = parse_xml(
            f'<w:tabs {nsdecls("w")}>'
            f'  <w:tab w:val="right" w:pos="8640" w:leader="none"/>'
            f'</w:tabs>'
        )
        pPr.append(tabs)

    # 页眉底线
    pBdr = parse_xml(
        f'<w:pBdr {nsdecls("w")}>'
        f'  <w:bottom w:val="single" w:sz="4" w:space="1" w:color="000000"/>'
        f'</w:pBdr>'
    )
    hp._element.get_or_add_pPr().append(pBdr)

    # --- 页脚 ---
    footer = section.footer
    if not footer.paragraphs:
        footer.add_paragraph()

    fp = footer.paragraphs[0]
    fp.clear()
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER

    if footer_text:
        # 替换 {{page}} 占位符
        parts = footer_text.split('{{page}}')
        for i, part in enumerate(parts):
            if part:
                run = fp.add_run(part)
                run.font.name = '宋体'
                run.font.size = Pt(9)
                _set_east_asia(run, '宋体')
            if i < len(parts) - 1:
                # 插入页码域
                _add_page_number_field(fp)


def _add_page_number_field(paragraph):
    """在段落中插入页码域"""
    run = paragraph.add_run()
    fldChar1 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>')
    run._element.append(fldChar1)

    run2 = paragraph.add_run()
    instrText = parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve"> PAGE </w:instrText>')
    run2._element.append(instrText)

    run3 = paragraph.add_run()
    fldChar2 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="separate"/>')
    run3._element.append(fldChar2)

    run4 = paragraph.add_run('1')
    run4.font.name = '宋体'
    run4.font.size = Pt(9)

    run5 = paragraph.add_run()
    fldChar3 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>')
    run5._element.append(fldChar3)


# ============================================================
# 表格创建
# ============================================================

def add_styled_table(doc, headers, rows, preset_name='formal_report', table_width_cm=None):
    """
    创建带样式的表格。
    headers: 列标题列表
    rows: 行数据列表（每行是值列表）
    preset_name: 使用的样式预设
    table_width_cm: 表格总宽度（厘米），默认占满页面
    """
    preset = STYLE_PRESETS.get(preset_name, STYLE_PRESETS['formal_report'])
    header_style = preset['styles'].get('Table Header', {})
    cell_style = preset['styles'].get('Table Cell', {})

    # 表格宽度
    section = doc.sections[0]
    if table_width_cm:
        total_width_emu = Cm(table_width_cm)
    else:
        total_width_emu = section.page_width - section.left_margin - section.right_margin

    col_count = len(headers)
    table = doc.add_table(rows=1 + len(rows), cols=col_count)
    table.autofit = False

    # 设置表格宽度（EMU 转 Twips: 1 inch = 1440 twips = 914400 emu）
    total_width_twips = int(total_width_emu / 914400 * 1440)
    tbl = table._tbl
    tblPr = tbl.tblPr
    tblW = parse_xml(f'<w:tblW {nsdecls("w")} w:w="{total_width_twips}" w:type="dxa"/>')
    existing_w = tblPr.find(qn('w:tblW'))
    if existing_w is not None:
        tblPr.remove(existing_w)
    tblPr.append(tblW)

    # 设置列宽均分
    col_width = int(total_width_twips / col_count)
    for col in table.columns:
        for cell in col.cells:
            cell.width = Twips(col_width)

    # 表头行
    for i, header_text in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ''
        p = cell.paragraphs[0]
        run = p.add_run(header_text)
        _apply_run_style(run, header_style)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        # 表头背景色
        _set_cell_bg(cell, header_style.get('bg_color', 'D5E8F0'))

    # 数据行
    for row_idx, row_data in enumerate(rows):
        for col_idx, value in enumerate(row_data):
            cell = table.rows[row_idx + 1].cells[col_idx]
            cell.text = ''
            p = cell.paragraphs[0]
            run = p.add_run(str(value))
            _apply_run_style(run, cell_style)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    return table


def _apply_run_style(run, style_config):
    """将样式配置应用到 run"""
    font_name = style_config.get('font', '宋体')
    run.font.name = font_name
    run.font.size = Pt(style_config.get('size_pt', 10.5))
    if style_config.get('bold'):
        run.font.bold = True
    east_asia = style_config.get('east_asia', font_name)
    _set_east_asia(run, east_asia)


def _set_cell_bg(cell, color_hex):
    """设置单元格背景色"""
    shading_elm = parse_xml(
        f'<w:shd {nsdecls("w")} w:fill="{color_hex}" w:val="clear"/>'
    )
    cell._tc.get_or_add_tcPr().append(shading_elm)


def _set_east_asia(run, font_name):
    """设置东亚字体（中文字体）"""
    rpr = run._element.get_or_add_rPr()
    rFonts = rpr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:eastAsia="{font_name}"/>')
        rpr.insert(0, rFonts)
    else:
        rFonts.set(qn('w:eastAsia'), font_name)


# ============================================================
# 代码块段落
# ============================================================

def add_code_block(doc, text, preset_name='formal_report'):
    """
    添加代码块段落（灰色背景、等宽字体、缩进）。
    text: 代码文本
    """
    preset = STYLE_PRESETS.get(preset_name, STYLE_PRESETS['formal_report'])
    code_style = preset['styles'].get('Code Block', {})

    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.name = code_style.get('font', 'Consolas')
    run.font.size = Pt(code_style.get('size_pt', 9))
    _set_east_asia(run, code_style.get('east_asia', '宋体'))

    # 灰色背景
    bg_color = code_style.get('bg_color', 'F2F2F2')
    pPr = p._element.get_or_add_pPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{bg_color}" w:val="clear"/>')
    pPr.append(shd)

    # 缩进
    indent_cm = code_style.get('indent_cm', 1)
    p.paragraph_format.left_indent = Cm(indent_cm)

    # 行距
    if code_style.get('line_spacing_pt'):
        p.paragraph_format.line_spacing = Pt(code_style['line_spacing_pt'])

    # 间距
    if code_style.get('space_before_pt') is not None:
        p.paragraph_format.space_before = Pt(code_style['space_before_pt'])
    if code_style.get('space_after_pt') is not None:
        p.paragraph_format.space_after = Pt(code_style['space_after_pt'])

    return p


# ============================================================
# 从零创建完整文档
# ============================================================

def create_doc_from_spec(spec):
    """
    从 JSON 规范创建完整的 Word 文档。
    spec: 包含以下字段的字典
        - project_name: 项目名称
        - doc_name: 文档名称
        - preset: 格式预设名 ('formal_report'/'tech_spec'/'manual'/'checklist')
        - version: 版本号（可选）
        - date: 日期（可选）
        - author: 编制人（可选）
        - reviewer: 审核人（可选）
        - toc: 是否生成目录（可选，默认 True）
        - header_left / header_right: 页眉文字（可选）
        - footer_text: 页脚文字（可选，支持 {{page}}）
        - sections: 章节列表或章节对象列表（可选）
        - output: 输出路径
    """
    preset_name = spec.get('preset', 'formal_report')
    doc = Document()

    # 1. 页面设置
    preset = STYLE_PRESETS.get(preset_name, STYLE_PRESETS['formal_report'])
    setup_page(doc, preset.get('page'))

    # 2. 注册样式
    register_styles(doc, preset_name)

    # 3. 封面页
    add_cover_page(
        doc,
        project_name=spec.get('project_name', ''),
        doc_name=spec.get('doc_name', ''),
        version=spec.get('version', ''),
        date=spec.get('date', ''),
        author=spec.get('author', ''),
        reviewer=spec.get('reviewer', '')
    )

    # 4. 目录页
    if spec.get('toc', True):
        add_toc(doc)

    # 5. 页眉页脚
    set_header_footer(
        doc,
        header_left=spec.get('header_left', spec.get('project_name', '')),
        header_right=spec.get('header_right', spec.get('doc_name', '')),
        footer_text=spec.get('footer_text', '第 {{page}} 页')
    )

    # 6. 章节内容
    sections = spec.get('sections', [])
    for section in sections:
        if isinstance(section, str):
            # 简单章节名，添加标题 + 空段落
            p = doc.add_paragraph(section, style='Heading 1')
            doc.add_paragraph('', style='Body Text')
        elif isinstance(section, dict):
            # 详细章节对象
            title = section.get('title', '')
            level = section.get('level', 1)
            if level >= 1:
                style_name = f'Heading {min(level, 4)}'
                doc.add_paragraph(title, style=style_name)
            elif title:
                # level 0 且有标题：使用正文样式加粗
                p = doc.add_paragraph(title, style='Body Text')
                if p.runs:
                    p.runs[0].font.bold = True
                else:
                    run = p.add_run(title)
                    run.font.bold = True

            # 段落内容
            for para in section.get('paragraphs', []):
                if isinstance(para, str):
                    doc.add_paragraph(para, style='Body Text')
                elif isinstance(para, dict):
                    if para.get('type') == 'code':
                        add_code_block(doc, para.get('text', ''), preset_name)
                    elif para.get('type') == 'table':
                        add_styled_table(
                            doc,
                            para.get('headers', []),
                            para.get('rows', []),
                            preset_name
                        )
                    elif para.get('type') == 'caption':
                        doc.add_paragraph(para.get('text', ''), style='Caption')
                    else:
                        doc.add_paragraph(para.get('text', ''), style='Body Text')

    # 7. 保存
    output_path = spec.get('output', 'output.docx')
    save_doc(doc, output_path)
    return output_path

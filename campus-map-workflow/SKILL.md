---
name: campus-map-workflow
description: 百科动态地图学校标注全流程。从核验过的markdown文本信息更新HTML文件（建筑数据、生活指南、关于信息），并结合OCR+LLM自动匹配建筑坐标。用户提供地图文件后触发。
---

# 校园地图标注全流程

将一所学校从核验文本到最终HTML的完整流程。以南开大学为标杆模板。

## 前置条件

- 当前工作目录在学校文件夹内（如 `南开大学/`）
- `地图.png` 已存在（用户刚提供）
- `*文本信息_已核验.md` 存在
- 标注工具 `../标注工具.html` 在项目根目录
- 模板 HTML `../北京科技大学(2)/index.html` 在项目根目录

## 流程

### Step 0: 确认主校区和地图来源（新学校必须）

在新学校开始标注前，必须先确认地图图片对应的是哪个校区：

1. 调用 `/find-campus-map` skill 确定主校区归属
2. 如果用户提供了 `地图.png`，确认它覆盖的是主校区还是分校区
3. 记录：当前地图覆盖的校区名称（一个地图通常只覆盖一个校区）

### Step 1: 初始化HTML

如果 `学校名.html` 尚不存在，从模板创建：

```bash
cp ../北京科技大学\(2\)/index.html ./{学校名}.html
```

模板包含完整的 React/CSS 基础设施和 13 栋北京科技大学的示例建筑。后续步骤会全部替换为当前学校的数据。

### Step 2: 读取核验文本

解析 `*文本信息_已核验.md`，提取以下结构化数据：

1. **校训精神**：校训文字、创办时间、官网URL、补充说明
2. **校区分布**：校区名称、地址、说明
3. **底部标语**
4. **生活指南**：6条 (g1-g6)，每条含 category + title + content
5. **建筑数据**：所有建筑条目，含 id, name, type, description, coverImage, location, campus, coords(占位值)

### Step 3: 更新HTML文本内容

逐项更新 `学校名.html`，用核验文本的数据替换模板中的 北京科技大学 内容：

**A. 生活指南 (LIFE_GUIDES)**
- 根据学校官网已有栏目信息灵活摘取生活指南类目，**不严格限制为固定6类**
- 优先查看学校官网的"校园服务""生活指南""后勤保障"等栏目，从中提取与学生校园生活直接相关的类目
- 常见参考类目（非强制）：餐饮美食、校际交通、学术资源、医疗健康、体育锻炼、公共服务
- 注意 content 末尾去掉具体营业时间（如无确认来源）

**B. About 信息**
- 校训：替换 HTML 中校训文字
- 创办时间：替换年份
- **不添加学校官网链接**（关于面板中明确不加官网URL）
- 校区分布：替换校区名称和地址（模板是2校区grid，可能需要改为3校区grid）
- 底部标语：替换

**C. 标题**
- `<title>` 改为 `学校名 · 智慧校园导航`
- 页面 heading 改为 `学校名 · 智慧校园导航`
- 生活指南标题改为 `学校简称生活指南`（如"南开生活指南"）

**D. 筛选项**
- filterOptions 仅保留建筑列表中实际出现的 type
- activeFilters 默认值与 filterOptions 一致
- 图标映射：landmark→IconStar, teaching→IconGraduationCap, sports→IconTrophy, public→IconHome

**E. 清理旧校名（务必彻底）**
- 全文搜索替换：`北京科技大学` → `学校名`
- **特别检查缩写**：`北科`、`USTB`、`ustb` 等可能被漏掉
- 逐一确认：生活指南标题、底部标语、about文字、alt属性、img标签

### Step 4: 更新建筑数据

**A. 替换 ORIGINAL_BUILDINGS 数组**
- 用核验文本的建筑数据替换整个 ORIGINAL_BUILDINGS 数组
- 此时 coords 用核验文本中的占位值即可（后续步骤校准）

**B. 校园字段校准**
- 建筑必须属于其在地图上实际出现的校区（不是文本描述中的重建/移址校区）
- 例如：南开大学的木斋图书馆/秀山堂/思源堂，文本说在津南校区，但地图上标注在八里台——应设 campus 为 "八里台校区"
- 仅保留在当前地图上实际可见的校区建筑

**C. 建筑审计 — 移除不应出现在地图上的建筑**
- 属于其他校区且该校区不在当前地图上的建筑：**删除**
- 已拆除/不存在/无法定位坐标的建筑：**删除**
- 删除后移除 filterOptions 中不再使用的 type（如无 living 类型建筑则移除 living 筛选项）

**D. 建筑封面图片**（如缺失）
- 盘点 images/ 目录已有图片，对照建筑列表找出缺失项
- 调用 `/find-building-images` skill 从百度百科等来源查找下载缺失的封面图
- 下载完成后回填 ORIGINAL_BUILDINGS 的 coverImage 路径为 `images/建筑名.png`

### Step 5: OCR 提取地图文字层

运行 PaddleOCR 从地图图片提取文字层：

```bash
python extract_text_paddle.py
```

输出：`地图文字层_paddle.json`，包含所有检测到的文字及其百分比坐标。

**PaddleOCR 安装**（仅首次，详见附录A）

### Step 6: LLM 自动匹配建筑坐标

运行匹配脚本，调用 DeepSeek API 将建筑名称匹配到文字层中的对应文本：

```bash
export LLM_API_KEY="sk-xxx"
python match_buildings.py
# 提示时选 y 将匹配结果写回 HTML
```

**重要**：必须确保 Step 3 已完成（ORIGINAL_BUILDINGS 已替换为正确数据），否则匹配脚本会将坐标写入错误建筑的 ID 上。

脚本对每栋建筑尝试匹配：
- 精确名称匹配（如"主楼" → OCR中的"主楼"）
- 语义关联（如"南开大学医院" → "校医院"）
- 无法匹配的标记为 unmatched

### Step 7: 人工审核匹配结果 + 估算未匹配坐标

LLM 匹配不是 100% 准确的，必须人工审核：

**修正错误匹配**
- 检查每个 matched 建筑的匹配结果是否合理
- 常见错误：语义过度关联（如"体育场馆"错误匹配到"体育馆"而非"南开大学体育中心"）
- 修正方法：从 OCR 文字层搜索正确的文字条目，手动改坐标

**估算未匹配建筑的坐标**
- 对 unmatched 建筑，根据 location 描述和 OCR 地标参考估算
- 例：location 描述为"马蹄湖、新开湖之间" → 搜索 OCR 文字层找"马蹄湖"(81.1,48.9)和"新开湖"(72.4,55.4) → 取中间值
- 坐标范围应在 0-100 之间

### Step 8: 坐标微调与验证

**CSS letterboxing 校准**
- 如果 HTML 中的 map 容器使用 `object-fit: contain` 且容器比例与地图原图不一致，会产生 letterboxing 偏移
- 检查方法：打开浏览器，对比 HTML 中主楼等已知位置的标记是否与地图上的实际位置重合
- 如不重合，计算 letterboxing 校正公式并应用到所有 Y 坐标

**浏览器验证**
1. 用 `python -m http.server` 启动本地服务器，浏览器打开 HTML
2. 检查建筑标记位置是否正确（逐个点击查看）
3. 检查生活指南面板标题和内容
4. 检查关于面板校训、网址
5. 检查筛选项和图标
6. 确认 0 JS 控制台错误
7. 全文搜索确认无旧校名残留（包括缩写）

### Step 9: （可选）标注工具精细校准

如果自动匹配+人工估算仍不满意：

1. 从 ORIGINAL_BUILDINGS 生成标注工具用的 JSON 字符串
2. 打开 `../标注工具.html`，上传 `地图.png`
3. 将 JSON 粘贴到文本框，拖拽标记到正确位置
4. 导出 JSON，回填 ORIGINAL_BUILDINGS 的 coords

## 关键注意事项

- **坐标是百分比**：相对于地图图片的 x% 和 y%，不是像素值
- **campus 字段**：必须和地图上建筑实际位置一致，不是文本描述
- **Step 4 必须在 Step 6 之前**：match_buildings.py 按建筑 ID 写入坐标，必须先有正确的建筑数据
- **filterOptions 应与实际建筑类型一致**：移除建筑后同步更新筛选项
- **官网链接**：关于面板中不添加学校官网链接
- **校名简称**：清理旧校名时务必检查缩写形式
- **校名简称规则**：生活指南标题中的学校简称要自然（如南开→南开、华南师范→华师、上海→上大、河北工业→河工大、山东科技→山科大、广东技术师范→广师大）

## 附录A：PaddleOCR 安装（Windows）

```bash
# 安装兼容版本（务必使用这些版本号）
mkdir -p /d/tmp
TMPDIR=/d/tmp TEMP=/d/tmp TMP=/d/tmp /d/APP/miniconda3/python -m pip install paddlepaddle==2.6.2
TMPDIR=/d/tmp TEMP=/d/tmp TMP=/d/tmp /d/APP/miniconda3/python -m pip install paddleocr==2.9.1 Pillow
```

`extract_text_paddle.py` 已内置必要的环境变量 workaround：
```python
os.environ["FLAGS_use_mkldnn"] = "0"   # 防止 OneDNN 崩溃
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"  # 解决 MKL 冲突
```

OCR 配置关键参数：`det_limit_side_len=8000`（高分辨率地图图片所需）。

## 附录B：match_buildings.py 通用化

脚本从当前目录自动发现文件，无需修改即可用于新学校：
- `BUILDINGS_FILE`：通过 glob 匹配 `*文本信息_已核验.md` 找到
- `HTML_FILE`：从 markdown 文件名推断学校名，拼接 `.html`
- API 密钥通过环境变量 `LLM_API_KEY` 传入

脚本文件位于项目根目录 `../match_buildings.py`，各学校文件夹可复制使用。

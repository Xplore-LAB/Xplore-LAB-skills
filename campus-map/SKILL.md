---
name: campus-map
description: 百科动态地图校园标注全流程。包括查找校园地图、查找建筑封面图、以及从核验文本到最终HTML的完整标注流程。用户提供学校名称或地图文件后触发。
---

# 校园地图标注全流程

将一所学校从零到最终HTML的完整流程。以南开大学为标杆模板。

---

## Part 1: 查找主校区与校园地图

确定大学的主校区归属，并从多种渠道找到高分辨率校园平面图。

### 前置条件

- 已知学校全称（如"南开大学"）
- 可能已知学校官网域名
- Playwright MCP 可用（用于访问百度百科和学校官网）

### Step 1.1: 确定主校区

从百度百科确定主校区归属是最可靠的方法。

**A. 百度百科词条**
1. 导航到 `https://baike.baidu.com/item/{学校全称}`
2. 查看信息框中的「地址」字段
3. 解析规则：校区按重要性排列，**第一个列出的即为主校区**
   - 例：`八里台校区：天津市南开区卫津路94号` → 主校区 = 八里台校区
4. 如果没有明确的地址字段，查看正文「校区情况」章节，寻找"校本部""主校区"标签

**B. 备选：学校官网**
1. 访问 `https://www.{学校域名}.edu.cn/xxgk/` 或 `/xygk/`（学校概况）
2. 查找"校区分布""学校简介"文字
3. 寻找"校本部""主校区""总部"关键词
4. 记录：主校区名称 + 详细地址

**C. 最后手段：百度地图**
1. 搜索 `{学校全称}`，第一个 POI 结果通常是主校区
2. 注意：这种方法不太可靠（可能受用户位置影响），仅当前两种失败时使用

### Step 1.2: 查找校园平面地图图片

按优先级从高到低依次尝试以下来源：

#### Tier 1: 学校官网（最可靠，优先尝试）

学校官网的基建处/后勤处/校园管理办公室是最可靠的高清地图来源。

**按顺序试探以下 URL 模式：**

| 优先级 | URL 模式 | 说明 | 示例 |
|--------|---------|------|------|
| 1 | `https://map.{domain}` | 电子地图子域名 | `map.sjtu.edu.cn`, `map.ustb.edu.cn` |
| 2 | `https://hq.{domain}/xygh/` | 后勤保障部·校园规划 | `hq.nankai.edu.cn/xygh/` |
| 3 | `https://jjc.{domain}/` | 基建处 | `jjc.tongji.edu.cn`, `jjc.nwu.edu.cn` |
| 4 | `https://www.{domain}/xydt/` | 校园地图目录 | 常见于招生网、迎新网 |
| 5 | `https://www.{domain}/xxgk/` | 信息公开网 | `xxgk.nankai.edu.cn` |
| 6 | `https://zsb.{domain}/` | 招生网（常有地图供新生） | `zsb.nankai.edu.cn` |

**操作步骤：**
1. 用 Playwright 按顺序尝试上述 URL
2. 在页面中搜索地图图片：查看 `<img>` 标签，寻找 `平面图` `校园地图` `鸟瞰图` `现状图` `规划图` 关键词
3. 用 `browser_evaluate` 提取图片 URL：
   ```js
   () => {
     const imgs = document.querySelectorAll('img');
     return Array.from(imgs)
       .filter(img => img.naturalWidth > 1000 || img.src.includes('地图'))
       .map(img => ({ src: img.src, w: img.naturalWidth, h: img.naturalHeight }));
   }
   ```
4. 如果找到多张图，优先选择：标注建筑名称的 > 鸟瞰图 > 规划图
5. 如果直接 URL 探测失败，在官网站内搜索 `site:{domain} 校园平面图`

#### Tier 2: 百度图片搜索

百度图片是中文高校地图覆盖最广的来源。

**搜索策略：**
1. 打开 `https://image.baidu.com/`
2. 搜索关键词组合（按效果排序）：
   - `{校名} {主校区名} 校园平面图 高清`（最推荐）
   - `{校名} 总平面图 大图`
   - `{校名} 校园地图 手绘`
   - `{校名} campus map`
3. 使用筛选功能：
   - 点击「高清」标签
   - 尺寸筛选 → 选择「大图」或「超大图」
   - 可选：限制 `site:edu.cn` 只看官方来源

**下载正确分辨率：**
- **关键**：搜索结果页显示的是缩略图，必须双击图片进入详情页
- 在详情页等待完整加载后右键保存
- 确认保存的图片尺寸 ≥ 1200px 宽

#### Tier 3: 谷歌图片搜索

谷歌图片对国际格式和 PNG 支持更好。

**搜索策略：**
1. 搜索关键词：`{校名} 校园地图 高清 filetype:png`
2. 使用 Tools → Size → Large 筛选
3. 特别关注 **Wikimedia Commons** 的结果（`commons.wikimedia.org`），常有超高清 PNG
4. 中英文都搜：`{English Name} campus map PNG`

#### Tier 4: 第三方来源

如果以上都失败，尝试：
- **世界校园地图网**: `http://www.shijieditu.net/xiaoyuan/`（校园地图聚合站）
- **百度百科图集**: 词条页面的「图集」tab 可能有校园地图
- **招生宣传材料**: 搜索 `{校名} 招生简章 校园地图`
- **百度地图/高德地图截图**: 最后手段，截图后裁剪

### Step 1.3: 评估和下载地图

**图片质量评判标准：**
- 分辨率：宽度 ≥ 1200px（越大越好，南开的图是 13139×6378）
- 格式：PNG 优先，JPG 可接受
- 内容：建筑名称标签清晰可辨，道路网络可见
- 范围：覆盖整个主校区（不只是局部区域）

**下载命令：**
```bash
curl -L -o "地图.png" "{图片URL}"
# 如果需要 referer：
curl -L -e "{来源页面URL}" -o "地图.png" "{图片URL}"
```

保存到学校目录根，文件名固定为 `地图.png`。

### Step 1.4: 输出结果

完成后汇报：
- 主校区名称 + 地址
- 地图图片来源（官网/百度图片/谷歌图片）
- 图片尺寸和格式
- 下载的文件路径

### 关键注意事项

- **主校区不等于"规模最大的校区"**：优先看历史主校区（校本部），因为地标建筑多集中在老校区
- **基建处/后勤处是最佳官方来源**：这些部门负责校园规划，维护着最新的平面图
- **百度图片必须点到详情页再存**：直接在搜索结果右键保存只会得到缩略图
- **先用官方来源，再用搜索引擎**：官网地图通常更准确、分辨率更高、无版权问题
- **如果百度百科地址字段列出了多个校区**：第一个就是主校区，这个规律正确率 >90%
- **`map.{domain}` 是最常见的电子地图 URL**：探测新学校时优先试这个
- **不要用 WebFetch 下载图片**：它只返回文本，图片需要用 curl 或浏览器下载

---

## Part 2: 查找建筑封面图片

为校园地图中的建筑从百度百科等来源查找并下载封面图片。

### 前置条件

- 当前工作目录在学校文件夹内（如 `南开大学/`）
- `images/` 目录已存在
- 已知建筑名称、学校名称

### Step 2.1: 盘点已有和缺失

先检查 `images/` 目录下已有图片，和建筑列表对照，确认每栋建筑是否已有 coverImage。

### Step 2.2: 搜索百度百科词条

对每栋缺失图片的建筑，用 Playwright 浏览器搜索百度百科：

1. 导航到 `https://baike.baidu.com`
2. 搜索框输入 `学校名 建筑名`（如 "南开大学 思源堂"）
3. 进入词条页面
4. 提取封面大图 URL

### Step 2.3: 提取百科封面图 URL

在百度百科词条页面，用 `browser_evaluate` 提取主图 URL：

```js
// 百科顶部的封面大图
const img = document.querySelector('.summary-pic img');
return img ? img.src : null;
```

如果 `.summary-pic` 不存在，尝试其他常见选择器：
- `.lemma-image img`
- `.main-content img:first-child`
- 取页面中第一个尺寸 > 200×200 的图片

### Step 2.4: URL 处理规则

百科图片 URL 格式：
```
https://bkimg.cdn.bcebos.com/pic/{hash}
```

**关键**：URL 中如果包含 `?x-bce-process=` 等 query 参数（如 `?x-bce-process=image/format,f_auto/resize,m_lfit,limit_1,h_500`），必须去掉这些参数，直接用纯净的 `https://bkimg.cdn.bcebos.com/pic/{hash}` 下载，才能获取全分辨率原图。

### Step 2.5: 下载图片

```bash
curl -L -o "建筑名.png" "https://bkimg.cdn.bcebos.com/pic/{hash}"
# 如果需要 referer 绕过防盗链：
curl -L -e "https://baike.baidu.com" -o "建筑名.png" "https://bkimg.cdn.bcebos.com/pic/{hash}"
```

保存到学校目录的 `images/` 子目录下，文件名用建筑名（如 `思源堂.png`）。

### Step 2.6: 备选方案（百科无词条时）

按优先级依次尝试：

1. **学校官方网站**：搜索 `学校域名 + 建筑名`，从官网宣传页面找图
2. **学校档案馆/宣传部网站**：常有历史建筑图片档案
3. **视觉中国**：`site:vcg.com 建筑名 学校名`，但通常有水印，仅作最后手段
4. **放弃设图**：如果确实找不到，在建筑数据的 coverImage 设为空字符串或不加载

### Step 2.7: 更新建筑数据

下载完成后，更新 HTML 中 ORIGINAL_BUILDINGS 对应建筑的 coverImage 路径为 `images/建筑名.png`。

### 注意事项

- **去除 query 参数**：百科图片 URL 的 query 参数限制了分辨率和格式，必须去掉以获取原图
- **防盗链**：如果下载失败(403)，添加 `-e "https://baike.baidu.com"` 作为 referer
- **注意图片格式**：百科图片实际多为 jpg 格式，但文件名统一用 png（浏览器会自动识别）
- **文件名一致**：确保下载的文件名和 coverImage 路径中的文件名完全一致
- **避免重复下载**：Step 2.1 的盘点是必须的，不要重复下载已有图片
- **一次一栋**：百科搜索时逐栋搜索，不要批量，因为可能有多义建筑名

---

## Part 3: 主流程（从核验文本到最终HTML）

### 前置条件

- 当前工作目录在学校文件夹内（如 `南开大学/`）
- `地图.png` 已存在（用户刚提供或通过 Part 1 下载）
- `*文本信息_已核验.md` 存在
- 标注工具 `../标注工具.html` 在项目根目录
- 模板 HTML `../北京科技大学(2)/index.html` 在项目根目录

### Step 3.0: 确认主校区和地图来源（新学校必须）

在新学校开始标注前，必须先确认地图图片对应的是哪个校区：

1. 按 **Part 1** 的流程确定主校区归属
2. 如果用户提供了 `地图.png`，确认它覆盖的是主校区还是分校区
3. 记录：当前地图覆盖的校区名称（一个地图通常只覆盖一个校区）

### Step 3.1: 初始化HTML

如果 `学校名.html` 尚不存在，从模板创建：

```bash
cp ../北京科技大学\(2\)/index.html ./{学校名}.html
```

模板包含完整的 React/CSS 基础设施和 13 栋北京科技大学的示例建筑。后续步骤会全部替换为当前学校的数据。

### Step 3.2: 读取核验文本

解析 `*文本信息_已核验.md`，提取以下结构化数据：

1. **校训精神**：校训文字、创办时间、官网URL、补充说明
2. **校区分布**：校区名称、地址、说明
3. **底部标语**
4. **生活指南**：6条 (g1-g6)，每条含 category + title + content
5. **建筑数据**：所有建筑条目，含 id, name, type, description, coverImage, location, campus, coords(占位值)

### Step 3.3: 更新HTML文本内容

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

### Step 3.4: 更新建筑数据

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
- 按 **Part 2** 的流程从百度百科等来源查找下载缺失的封面图
- 下载完成后回填 ORIGINAL_BUILDINGS 的 coverImage 路径为 `images/建筑名.png`

### Step 3.5: OCR 提取地图文字层

运行 PaddleOCR 从地图图片提取文字层：

```bash
python extract_text_paddle.py
```

输出：`地图文字层_paddle.json`，包含所有检测到的文字及其百分比坐标。

**PaddleOCR 安装**（仅首次，详见附录A）

### Step 3.6: LLM 自动匹配建筑坐标

运行匹配脚本，调用 DeepSeek API 将建筑名称匹配到文字层中的对应文本：

```bash
export LLM_API_KEY="sk-xxx"
python match_buildings.py
# 提示时选 y 将匹配结果写回 HTML
```

**重要**：必须确保 Step 3.3 已完成（ORIGINAL_BUILDINGS 已替换为正确数据），否则匹配脚本会将坐标写入错误建筑的 ID 上。

脚本对每栋建筑尝试匹配：
- 精确名称匹配（如"主楼" → OCR中的"主楼"）
- 语义关联（如"南开大学医院" → "校医院"）
- 无法匹配的标记为 unmatched

### Step 3.7: 人工审核匹配结果 + 估算未匹配坐标

LLM 匹配不是 100% 准确的，必须人工审核：

**修正错误匹配**
- 检查每个 matched 建筑的匹配结果是否合理
- 常见错误：语义过度关联（如"体育场馆"错误匹配到"体育馆"而非"南开大学体育中心"）
- 修正方法：从 OCR 文字层搜索正确的文字条目，手动改坐标

**估算未匹配建筑的坐标**
- 对 unmatched 建筑，根据 location 描述和 OCR 地标参考估算
- 例：location 描述为"马蹄湖、新开湖之间" → 搜索 OCR 文字层找"马蹄湖"(81.1,48.9)和"新开湖"(72.4,55.4) → 取中间值
- 坐标范围应在 0-100 之间

### Step 3.8: 坐标微调与验证

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

### Step 3.9: （可选）标注工具精细校准

如果自动匹配+人工估算仍不满意：

1. 从 ORIGINAL_BUILDINGS 生成标注工具用的 JSON 字符串
2. 打开 `../标注工具.html`，上传 `地图.png`
3. 将 JSON 粘贴到文本框，拖拽标记到正确位置
4. 导出 JSON，回填 ORIGINAL_BUILDINGS 的 coords

---

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

---

## 全局关键注意事项

- **坐标是百分比**：相对于地图图片的 x% 和 y%，不是像素值
- **campus 字段**：必须和地图上建筑实际位置一致，不是文本描述
- **Step 3.3 必须在 Step 3.6 之前**：match_buildings.py 按建筑 ID 写入坐标，必须先有正确的建筑数据
- **filterOptions 应与实际建筑类型一致**：移除建筑后同步更新筛选项
- **官网链接**：关于面板中不添加学校官网链接
- **校名简称**：清理旧校名时务必检查缩写形式
- **校名简称规则**：生活指南标题中的学校简称要自然（如南开→南开、华南师范→华师、上海→上大、河北工业→河工大、山东科技→山科大、广东技术师范→广师大）

---
name: campus-map-check
description: 校园地图上线前全面检查修复。逐项检查布局、弹窗、类型、筛选、图片等，确保地图可用。触发词：检查地图、地图检查、修复地图、校园地图检查、地图上线。
---

# 校园地图检查修复技能

当用户要求检查或修复校园地图 HTML 时，**自动执行以下检查并直接修复**。不要只报告问题，要实际修改代码。

---

## 执行原则

- **参考模板**：`D:\ZJU的我\9-兼职\百科动态地图-第二期\第二期-20校\01_浙江财经大学\浙江财经大学校园平面图\index.html`
- **目标文件**：用户指定的学校目录下的 HTML 文件
- **不要只列清单**：每检查一项，发现问题就立即修复
- **批量操作**：尽量在一次 Edit 中修复多个问题
- **完成后**：总结修复了哪些问题

---

## 第一步：确认目标学校

1. 如果用户指定了学校名，在以下目录中查找：
   - `D:\ZJU的我\9-兼职\百科动态地图-第二期\第二期-20校\`
2. 找到学校目录后，定位 HTML 文件（通常是 `index.html`、`校园平面图/index.html` 或 `XX大学.html`）
3. 读取目标 HTML 文件全文

---

## 第二步：十项检查修复

### 检查 1：左上角标题组件

在目标 HTML 中搜索 `<header` 标签。如果存在类似以下结构，**整块删除**：
```html
<header className="relative z-10 p-4 pointer-events-none">
  <motion.div ...>
    <div ...>XX大学 · 智慧校园导航</div>
  </motion.div>
</header>
```

### 检查 2：面板布局

找到生活指南/关于面板的 `<motion.div>`：
- className 必须包含 `absolute left-6 right-6 top-6 bottom-6`（不是 `inset-x-6`）
- 必须有 `flex flex-col`
- 标题区 className 用 `mb-4`
- 内容区 className 用 `flex-1 overflow-auto no-scrollbar`
- 网格用 `grid grid-cols-2 gap-5`
- 不给网格和卡片加 `h-full`

### 检查 3：地图缩放

- [ ] `minScale = 1, maxScale = 3`
- [ ] 必须有 `zoomBy` useCallback 处理按钮缩放
- [ ] 必须有 +/− 缩放按钮和百分比显示（参考模板格式）
- [ ] **不要**添加 wheel 事件（保持按钮缩放方式）
- [ ] 添加 `const scaleRef = useRef(1); scaleRef.current = scale;` 并在 `onMouseDown` 开头检查 `if (scaleRef.current <= 1) return;`（100% 禁止拖拽）

### 检查 4：地图容器结构

- [ ] 最外层：`<div className="w-full h-full relative">`
- [ ] map-scroll-container 用 `style={{ cursor: 'grab', overflow: scale <= 1 ? 'hidden' : 'auto' }}`（100% 时隐藏滚动条并禁止拖拽，放大后恢复）
- [ ] 底部提示：`<div className="fixed bottom-3 right-3 ...">+ / − 缩放地图</div>`（用 `fixed` 定位在视口右下角，放在 App 组件内、ZoomableMap 之外）
- [ ] `body { overflow: hidden }` — 页面不滚动
- [ ] 外层容器 `overflow-hidden`

### 检查 5：建筑数量与类型

- 建筑总数 ≥ 10 个（不够就根据 OCR 文字层或地图补充）
- 必须覆盖 7 种类型：
  - `landmark` → 核心地标 (IconStar)
  - `teaching` → 教学科研 (IconGraduationCap)
  - `sports` → 体育场馆 (IconTrophy)
  - `dining` → 餐饮食堂 (IconUtensils)
  - `dorm` → 学生宿舍 (IconHome)
  - `service` → 生活服务 (IconLayers)
  - `health` → 医疗健康 (IconHeart)

### 检查 6：图标组件

确保代码中定义了 `IconHeart` 组件。如果不存在，添加：
```jsx
const IconHeart = () => <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>;
```

### 检查 7：图层筛选系统

- 必须有 `ALL_FILTER_OPTIONS` 常量（7 种类型，含 icon）
- 必须有 `getBuildingIcon` 函数
- App 中用 `existingTypes` 动态初始化 `activeFilters`
- `filterOptions` 从 `ALL_FILTER_OPTIONS` 按 `existingTypes` 过滤

### 检查 8：弹窗系统（关键！）

- ZoomableMap 必须有 `hoveredBuildingId` 状态
- 标记按钮用 `onHoverStart`/`onHoverEnd` + `z-10 hover:z-20`
- **删除**按钮内部的旧 tooltip div（`group-hover:opacity-100` 那段）
- 在 AnimatePresence **之后**添加独立的标签渲染（`z-50`，绝对定位）

### 检查 9：食堂和宿舍内部图

- 食堂（dining 类型）gallery ≥ 1 张内部实拍
- 宿舍（dorm 类型）gallery ≥ 1 张内部实拍
- 确认 `coverImage` 和 `gallery` 中路径对应的文件实际存在

### 检查 10：图片同步

如果存在 `校园平面图/images/` 子目录：
- 主 `images/` 和 `校园平面图/images/` 中，HTML 引用的图片保持一致
- 缺失的图片从另一个目录复制

---

## 补充数据来源处理原则

当从微信公众号等外部来源获取建筑介绍文字时：

- **不要直接复制粘贴**：原文往往带有口语化表达（"西西"、"西瓜籽们"、"小丘比"等昵称）和营销口吻
- **提取关键信息**：菜品种类、楼层分布、特色档口、位置关系、设施配置等事实性内容
- **改写为专业表述**：用第三人称客观描述，保持与现有建筑描述一致的正式风格
- **控制篇幅**：每条 60-100 字，突出最核心的特色信息
- **保留数据**：座位数、面积、等级认证等客观数字可直接使用

示例对比：
- ❌ 原文："今天小丘比带领大家看看南科大的食堂和美食~"
- ✅ 改写："中心餐厅位于南科大中心一楼，供应大众菜、面档及潮汕风味。"

---

## 第三步：确认修复结果

全部修复完成后，报告：
- 修复了哪些问题
- 建筑数量是否 ≥ 10
- 类型覆盖是否完整
- 如还有遗留问题，列出来

---

## 第四步：自动语法验证（必须执行）

修复完成后必须运行括号平衡检查，确保 JSX 无语法错误再收工：

```bash
python -c "
import re
with open('目标文件路径','r',encoding='utf-8') as f: html=f.read()
m=re.search(r'<script type=\"text/babel\">(.*?)</script>',html,re.DOTALL)
if m:
 js=m.group(1);stack=[];i=0;ins=False;it=False;sc=None
 while i<len(js):
  ch=js[i]
  if ins:
   if ch=='\\\\' and i+1<len(js):i+=2;continue
   if ch==sc:ins=False
   i+=1;continue
  if it:
   if ch=='\\\\' and i+1<len(js):i+=2;continue
   if ch=='`':it=False
   i+=1;continue
  if ch in \"'\\\"\":ins=True;sc=ch;i+=1;continue
  if ch=='`':it=True;i+=1;continue
  if ch in '{[(':stack.append(ch)
  elif ch in '})]':
   if not stack:print(f'ERROR:unexpected {ch}');break
   exp={'{':'}','(':')','[':']'}[stack[-1]]
   if ch==exp:stack.pop()
   else:print(f'ERROR:expected {exp},got {ch}');break
  i+=1
 print('OK' if not stack else f'ERROR:{len(stack)}unclosed')
"
```

输出必须为 `OK`。常见语法错误：
- 建筑数组项之间缺少逗号
- 模板字符串中多余转义引号
- sed 导致的字面量 `\n` 未转为换行

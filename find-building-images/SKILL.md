---
name: find-building-images
description: 从百度百科和学校官网为校园建筑查找下载封面图片。当需要为建筑（教学楼、图书馆、体育场馆等）找到高质量封面图时使用此 skill。优先百科词条，其次学校官网/视觉中国，最后用校园风景图占位或不设图片。
---

# 查找建筑封面图片

为校园地图中的建筑从百度百科等来源查找并下载封面图片。

## 前置条件

- 当前工作目录在学校文件夹内（如 `南开大学/`）
- `images/` 目录已存在
- 已知建筑名称、学校名称

## 流程

### Step 1: 盘点已有和缺失

先检查 `images/` 目录下已有图片，和建筑列表对照，确认每栋建筑是否已有 coverImage。

### Step 2: 搜索百度百科词条

对每栋缺失图片的建筑，用 Playwright 浏览器搜索百度百科：

1. 导航到 `https://baike.baidu.com`
2. 搜索框输入 `学校名 建筑名`（如 "南开大学 思源堂"）
3. 进入词条页面
4. 提取封面大图 URL

### Step 3: 提取百科封面图 URL

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

### Step 4: URL 处理规则

百科图片 URL 格式：
```
https://bkimg.cdn.bcebos.com/pic/{hash}
```

**关键**：URL 中如果包含 `?x-bce-process=` 等 query 参数（如 `?x-bce-process=image/format,f_auto/resize,m_lfit,limit_1,h_500`），必须去掉这些参数，直接用纯净的 `https://bkimg.cdn.bcebos.com/pic/{hash}` 下载，才能获取全分辨率原图。

### Step 5: 下载图片

```bash
curl -L -o "建筑名.png" "https://bkimg.cdn.bcebos.com/pic/{hash}"
# 如果需要 referer 绕过防盗链：
curl -L -e "https://baike.baidu.com" -o "建筑名.png" "https://bkimg.cdn.bcebos.com/pic/{hash}"
```

保存到学校目录的 `images/` 子目录下，文件名用建筑名（如 `思源堂.png`）。

### Step 6: 备选方案（百科无词条时）

按优先级依次尝试：

1. **学校官方网站**：搜索 `学校域名 + 建筑名`，从官网宣传页面找图
2. **学校档案馆/宣传部网站**：常有历史建筑图片档案
3. **视觉中国**：`site:vcg.com 建筑名 学校名`，但通常有水印，仅作最后手段
4. **放弃设图**：如果确实找不到，在建筑数据的 coverImage 设为空字符串或不加载

### Step 7: 更新建筑数据

下载完成后，更新 HTML 中 ORIGINAL_BUILDINGS 对应建筑的 coverImage 路径为 `images/建筑名.png`。

## 注意事项

- **去除 query 参数**：百科图片 URL 的 query 参数限制了分辨率和格式，必须去掉以获取原图
- **防盗链**：如果下载失败(403)，添加 `-e "https://baike.baidu.com"` 作为 referer
- **注意图片格式**：百科图片实际多为 jpg 格式，但文件名统一用 png（浏览器会自动识别）
- **文件名一致**：确保下载的文件名和 coverImage 路径中的文件名完全一致
- **避免重复下载**：Step 1 的盘点是必须的，不要重复下载已有图片
- **一次一栋**：百科搜索时逐栋搜索，不要批量，因为可能有多义建筑名

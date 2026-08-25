## 常见操作工作流

### 工作流 1：查找并下载文件

当需要在微云中找到某个文件并下载到本地时，按以下步骤操作：

**第一步：查询根目录**

```
调用 weiyun.list，参数：limit=50, get_type=0
```

- 响应中的 `file_list` 包含文件，`dir_list` 包含子目录
- **记住响应顶层的 `pdir_key`**（后续下载需要用到）
- 如果文件在根目录 → 进入第三步
- 如果文件不在根目录 → 需要遍历子目录（第二步）

**第二步：遍历子目录查找文件**

```
调用 weiyun.list，参数：
  dir_key = <子目录的 dir_key>（从 dir_list 中获取）
  pdir_key = <子目录所在父目录的 pdir_key>（即上一次 list 响应顶层的 pdir_key，或子目录所在目录的 dir_key）
  limit = 50
```

**⚠️ 关键**：查询子目录时 `dir_key` 和 `pdir_key` 的含义：
- `dir_key`：要查询的目标子目录的 key（从 `dir_list` 中的 `dir_key` 字段获取）
- `pdir_key`：该子目录所在的父目录 key（从上一级 `weiyun.list` 响应顶层的 `pdir_key` 获取）

如果还有嵌套子目录，递归重复此步骤。

**第三步：获取下载链接**

```
调用 weiyun.download，参数：
  items = [{"file_id": "<文件的 file_id>", "pdir_key": "<文件所在目录的 pdir_key>"}]
```

- `file_id`：从 `file_list` 中获取
- `pdir_key`：使用 `weiyun.list` 响应中**顶层的 `pdir_key`**（不是文件自身的 `pdir_key` 字段）

**第四步：下载文件到本地**

```bash
curl -s -L -o <本地文件名> -b "<cookie>" "<https_download_url>"
```

> **Windows (PowerShell)**：
> ```powershell
> $session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
> $session.Cookies.Add((New-Object System.Net.Cookie("FTN5K", "<cookie值>", "/", ".weiyun.com")))
> Invoke-WebRequest -Uri "<https_download_url>" -OutFile "<本地文件名>" -WebSession $session
> ```

- `-L`：跟随重定向（必须）
- `-b`：携带 cookie（从 download 响应中获取，格式如 `FTN5K=08bfd4be`）
- 下载完成后验证文件大小与 `file_size` 一致

### 工作流 2：上传文件到微云

**推荐方式**（一键脚本）：

```bash
# 1. 先查根目录获取 pdir_key
# 调用 weiyun.list limit=50 → 记住响应中的 pdir_key

# 2. 上传
python3 scripts/upload_to_weiyun.py /path/to/file --pdir_key <pdir_key>
```

> **Windows (PowerShell)**：`chcp 65001 >nul && python scripts\upload_to_weiyun.py C:\path\to\file --pdir_key <pdir_key>`

**手动方式**：参见上方「5. weiyun.upload — 文件上传」章节。

### 工作流 3：生成分享链接

```
# 1. 先查目录获取文件信息和 pdir_key
调用 weiyun.list → 找到目标文件的 file_id，记住响应**顶层** pdir_key

# 2. 生成分享链接（pdir_key 必须非空！）
调用 weiyun.gen_share_link，参数：
  file_list = [{"file_id": "<file_id>", "pdir_key": "<响应顶层的 pdir_key>"}]
  share_name = "<文件名>"
```

**⚠️ 关键**：`pdir_key` 必须使用 `weiyun.list` 响应中**顶层的 `pdir_key`**，绝对不能传空字符串！文件项中的 `pdir_key` 字段可能为空，不可使用。

### 工作流 4：删除文件

```
# 1. 先查目录获取文件信息
调用 weiyun.list → 找到目标文件的 file_id，记住响应顶层 pdir_key

# 2. 删除
调用 weiyun.delete，参数：
  file_list = [{"file_id": "<file_id>", "pdir_key": "<pdir_key>"}]
  delete_completely = false  （移到回收站，更安全）
```

### 工作流 5：重命名文件或目录

```
# 1. 先查目录获取文件/目录信息
调用 weiyun.list → 找到目标文件的 file_id 或目录的 dir_key，记住响应顶层 pdir_key

# 2a. 重命名文件
调用 weiyun.rename_file，参数：
  file_id = "<file_id>"
  pdir_key = "<响应顶层的 pdir_key>"
  new_filename = "<新文件名>"

# 2b. 重命名目录
调用 weiyun.rename_dir，参数：
  dir_key = "<dir_key>"
  pdir_key = "<响应顶层的 pdir_key>"
  new_dir_name = "<新目录名>"
  src_dir_name = "<原目录名>"
```

### 工作流 6：按分类查找文件

```
# 查找所有 PDF 文件
调用 weiyun.list_by_category，参数：
  category_id = 8    （8 = PDF）
  count = 50

# 续拉更多结果
调用 weiyun.list_by_category，参数：
  category_id = 8
  count = 50
  local_version = "<上次响应的 server_version>"

# 按后缀查找
调用 weiyun.list_by_category，参数：
  lib_id = 1         （1 = 文档库）
  suffix_list = ["docx", "xlsx"]
  count = 50
```

### 工作流 7：创建文件夹

```
# 1. 先查目录获取 pdir_key（如果要在子目录下创建）
调用 weiyun.list → 记住响应顶层 pdir_key 或目标子目录的 dir_key

# 2. 创建文件夹
调用 weiyun.create_dir，参数：
  pdir_key = "<目标父目录的 pdir_key>"（为空则在 token 绑定的根目录下创建）
  dir_name = "<新文件夹名称>"
```

**响应**：返回新创建目录的 `dir_key` 和 `dir_name`（可能因同名被自动改名）。

### 工作流 8：移动文件或目录

```
# 1. 先查源目录获取文件/目录信息
调用 weiyun.list，查询源目录 → 找到目标文件的 file_id 或目录的 dir_key，记住响应顶层 pdir_key 作为 src_pdir_key

# 2. 查目标目录获取 dst_pdir_key
调用 weiyun.list，查询目标目录 → 记住响应顶层的 pdir_key 作为 dst_pdir_key

# 3a. 移动文件
调用 weiyun.move_file，参数：
  file_id = "<file_id>"
  src_pdir_key = "<源目录的 pdir_key>"
  dst_pdir_key = "<目标目录的 pdir_key>"

# 3b. 移动目录
调用 weiyun.move_dir，参数：
  dir_key = "<要移动的目录 dir_key>"
  src_pdir_key = "<源父目录的 pdir_key>"
  dst_pdir_key = "<目标父目录的 pdir_key>"
```

**⚠️ 关键**：`src_pdir_key` 和 `dst_pdir_key` 不能为空，必须通过 `weiyun.list` 获取正确的目录 key。

---

## 常见问题

1. **上传文件应该怎么做**：直接用 `python3 scripts/upload_to_weiyun.py <文件路径> --pdir_key <目录key>`，无需手动计算参数或调用 MCP
2. **下载时 pdir_key 应该填什么**：使用 `weiyun.list` 响应中**顶层的 `pdir_key`**，而不是文件自身的 `pdir_key` 字段（该字段可能为空字符串）
3. **生成分享链接时 pdir_key 不能为空**：必须先调用 `weiyun.list`，使用响应**顶层的 `pdir_key`**（不是 `file_list[i].pdir_key`，该字段通常为空）。`pdir_key` 为空会导致分享链接打开异常
4. **查询子目录时 pdir_key 怎么填**：填入子目录所在父目录的 key。对于根目录下的子目录，就是根目录 `weiyun.list` 响应顶层的 `pdir_key`
5. **下载时需要携带 cookie**：`weiyun.download` 返回的下载链接需要用 `curl -b "<cookie>"` 携带 cookie 值，同时 `-L` 跟随重定向
6. **上传报 "Cannot upload to a directory that you do not own"**：必须指定 `--pdir_key` 参数。先调用 `weiyun.list` 获取响应中顶层的 `pdir_key`
7. **分片上传通道 len=0**：每轮上传完一片后，返回的通道列表可能全部 len=0，需要重新预上传获取下一批通道。`upload_to_weiyun.py` 已自动处理此问题
8. **SHA1 不匹配**：确保分块 SHA 值使用流式 SHA1 内部状态（小端序），而非独立分块 SHA1
9. **file_sha 被覆盖**：服务端用最后一个 block 的 SHA 覆盖 file_sha — 两者必须相等
10. **Base64 双重编码**：MCP 框架自动将 base64 字符串转为 bytes 传给 `file_data` 字段，服务端会再次进行 Base64 解码
11. **通道 ID 不匹配**：上传分片时 `channel_id` 必须与 `channel_list` 中某个条目匹配
12. **环境标识**：SIT 环境需在 Cookie 中携带 `env_id=sit-xxxxx`
13. **权限校验**：下载、删除、分享操作会校验目录所有权，非本人目录的文件会被跳过
14. **腾讯文档过滤**：列表查询会自动过滤腾讯文档类型的文件
15. **pip install requests**：上传脚本依赖 `requests` 库，如提示缺少请先安装：`pip install requests`
16. **所有需要 pdir_key 的操作**（下载、删除、分享、上传、重命名），都应使用 `weiyun.list` 响应**顶层**的 `pdir_key`，而不是文件/目录条目自身的 `pdir_key` 字段
17. **Windows 编码要求（防止中文乱码）**：Windows 下执行 Python 脚本或 mcporter 命令前**必须**先切换控制台代码页为 UTF-8，格式为 `chcp 65001 >nul && python ...`。Python 脚本已内置 `_encoding_fix.py` 模块自动修复 stdout/stderr 编码，但 `chcp 65001` 仍然是必要的（确保 cmd/PowerShell 控制台本身使用 UTF-8 解码输出）
18. **Windows 下使用 `python` 而非 `python3`**：Windows 系统通常使用 `python` 命令，macOS/Linux 使用 `python3`。请根据用户操作系统自动选择正确的命令
19. **重命名文件/目录**：先调用 `weiyun.list` 获取 `file_id`/`dir_key`、`dir_name` 和顶层 `pdir_key`，再调用 `weiyun.rename_file` 或 `weiyun.rename_dir`（重命名目录时需额外传 `src_dir_name` 即原目录名）
20. **按分类查找文件**：使用 `weiyun.list_by_category`，通过 `category_id` 或 `lib_id` 指定分类，支持 `server_version` 续拉。该接口需要同时携带真实微云 cookie 和 `mcp_token`
21. **生成带密码的分享链接**：在调用 `weiyun.gen_share_link` 时设置 `passwd` 参数即可创建加密分享
22. **创建文件夹**：调用 `weiyun.create_dir`，传入 `pdir_key`（父目录 key）和 `dir_name`（文件夹名称）。`pdir_key` 为空时在 token 绑定的根目录下创建。返回的 `dir_name` 可能因同名冲突被自动改名
23. **移动文件/目录**：使用 `weiyun.move_file` 或 `weiyun.move_dir`。需要先通过 `weiyun.list` 分别获取源目录和目标目录的 `pdir_key`，填入 `src_pdir_key` 和 `dst_pdir_key`。两个 key 都不能为空
24. **移动操作的目录 key 获取**：`src_pdir_key` 来自文件/目录当前所在位置的 `weiyun.list` 响应顶层 `pdir_key`；`dst_pdir_key` 来自目标位置的 `weiyun.list` 响应顶层 `pdir_key` 或目标目录的 `dir_key`



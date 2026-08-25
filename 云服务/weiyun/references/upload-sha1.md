## 分块 SHA1 计算算法

这是上传功能最核心的部分。微云**不使用**标准的独立分块 SHA1，而是使用**流式 SHA1 内部状态**。

### 算法步骤（分块大小 = 512KB = 524288 字节）

1. 创建**一个**共享的 SHA1 哈希对象
2. 对于除最后一块之外的每个块：
   - 读取 524288 字节并 `update()` 到 SHA1 对象
   - 提取 SHA1 内部寄存器（h0, h1, h2, h3, h4）以**小端序**输出
   - 输出为 40 字符 hex 字符串 → 该块的 `sha` 值
3. 对于最后一块（可能不足 524288 字节）：
   - 继续用相同 SHA1 对象 update 剩余数据
   - `sha` 值为**整个文件的标准 SHA1 hexdigest**（大端序，含 finalization）

### check_sha 和 check_data 计算

用于服务端防篡改验证：

```
lastBlockSize = file_size % 524288（若为 0 则取 524288）
checkBlockSize = lastBlockSize % 128（若为 0 则取 128）

check_sha：处理完所有非最后块后，继续 update 最后块中前 (lastBlockSize - checkBlockSize) 字节，
           然后取 SHA1 内部寄存器 h0-h4 小端序输出为 hex
check_data：文件末尾 checkBlockSize 字节的 Base64 编码
```

### 使用脚本

#### 一键上传脚本（推荐）

直接上传本地文件到微云，整合了参数计算 + 预上传 + 分片上传的完整流程：

```bash
# 基本用法
python3 scripts/upload_to_weiyun.py /path/to/file --token <mcp_token> --env_id <env_id>

# 指定上传目录
python3 scripts/upload_to_weiyun.py /path/to/file --token <mcp_token> --pdir_key <dir_key>

# 使用环境变量
export WEIYUN_MCP_TOKEN=<mcp_token>
export WEIYUN_ENV_ID=<env_id>
python3 scripts/upload_to_weiyun.py /path/to/file
```

> **Windows (PowerShell)** 用户：需先切换 UTF-8 编码，将 `python3` 替换为 `python`，`export` 替换为 `$env:VAR = "value"`：
> ```powershell
> # 基本用法
> chcp 65001 >nul && python scripts\upload_to_weiyun.py C:\path\to\file --token <mcp_token> --env_id <env_id>
>
> # 使用环境变量
> $env:WEIYUN_MCP_TOKEN = "<mcp_token>"
> $env:WEIYUN_ENV_ID = "<env_id>"
> chcp 65001 >nul && python scripts\upload_to_weiyun.py C:\path\to\file
> ```


脚本参数：

| 参数 | 必填 | 说明 |
|------|------|------|
| `file_path` | **是** | 本地文件路径（位置参数） |
| `--token` | **是** | MCP token（或设 `WEIYUN_MCP_TOKEN` 环境变量） |
| `--env_id` | 否 | 环境标识（如 `sit-0cd15bb3`，或设 `WEIYUN_ENV_ID`） |
| `--pdir_key` | 否 | 上传目标目录 key（不填使用 token 绑定目录） |
| `--mcp_url` | 否 | MCP 服务地址（默认 `https://www.weiyun.com/api/v3/mcpserver`） |
| `--max_rounds` | 否 | 最大上传轮数（默认 50） |

上传策略：循环「预上传获取通道 → 上传一片 → 重新预上传」直到完成。每次预上传会自动跳过已成功的分片（offset 随进度递增），支持秒传。

**AI Agent 使用时**：只需要 `execute_command` 运行此脚本即可，无需手动计算 block_sha_list 或调用 MCP。

#### 参数计算脚本

仅计算上传参数（不执行上传），用于调试或手动调用 MCP：

```bash
python3 scripts/gen_block_info_list.py /path/to/file
```

> **Windows (PowerShell)**：`chcp 65001 >nul && python scripts\gen_block_info_list.py C:\path\to\file`

输出包括：`block_sha_list`、`file_sha`、`file_md5`、`check_sha`、`check_data`、`block_size`、`block_count`。

两个脚本均包含纯 Python 的 SHA1 实现，支持提取未经 finalization 的内部状态 — 这是 Python 标准库 `hashlib.sha1` 无法做到的。


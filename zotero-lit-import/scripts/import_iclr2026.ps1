# ICLR 2026 论文 Zotero 导入脚本 (PowerShell)
# 直接调用 Zotero Web API，无需 Python

$API_KEY = "7VOWMztrbY56yVYJprUO9b1q"
$USER_ID = "10931866"
$BASE = "https://api.zotero.org/users/$USER_ID"
$RIS_FILE = "ICLR2026_papers.ris"
$LOG_FILE = "import_log.txt"

# 清空日志
"" | Out-File -FilePath $LOG_FILE -Encoding UTF8

function Log($msg) {
    $timestamp = Get-Date -Format "HH:mm:ss"
    $line = "[$timestamp] $msg"
    Add-Content -Path $LOG_FILE -Value $line -Encoding UTF8
    Write-Host $line
}

function ApiCall($method, $endpoint, $bodyObj = $null) {
    $url = $BASE + "/" + $endpoint.TrimStart("/")
    $headers = @{
        "Zotero-API-Key" = $API_KEY
        "Content-Type" = "application/json; charset=utf-8"
    }
    $body = $null
    if ($bodyObj) {
        $body = [System.Text.Encoding]::UTF8.GetBytes(($bodyObj | ConvertTo-Json -Depth 10 -Compress))
    }
    try {
        if ($method -eq "GET") {
            $resp = Invoke-RestMethod -Uri $url -Headers $headers -Method GET -TimeoutSec 30
        } elseif ($method -eq "POST") {
            $resp = Invoke-RestMethod -Uri $url -Headers $headers -Method POST -Body $body -TimeoutSec 30
        } elseif ($method -eq "PATCH") {
            $resp = Invoke-RestMethod -Uri $url -Headers $headers -Method PATCH -Body $body -TimeoutSec 30
        }
        return $resp
    } catch {
        $status = $_.Exception.Response.StatusCode.value__
        $errBody = $_.ErrorDetails.Message
        Log "  ✗ HTTP $status : $errBody"
        return $null
    }
}

function GetExistingCollections {
    $data = ApiCall "GET" "collections?limit=100"
    $nameToKey = @{}
    $keyToParent = @{}
    if ($data) {
        foreach ($c in $data) {
            $nameToKey[$c.data.name] = $c.data.key
            if ($c.data.parentCollection -and $c.data.parentCollection -ne $false) {
                $keyToParent[$c.data.key] = $c.data.parentCollection
            }
        }
    }
    return $nameToKey, $keyToParent
}

# 主流程
Log "=" * 60
Log "Zotero 批量导入（PowerShell 直调 API）"
Log "RIS 文件: $RIS_FILE"

# Step 0: 解析 RIS
Log "解析 RIS 文件..."
$papers = @()
$current = $null
$risContent = Get-Content -Path $RIS_FILE -Encoding UTF8
foreach ($line in $risContent) {
    $line = $line.Trim()
    if (-not $line) { continue }
    if ($line -match "^TY\s+-\s*(.+)$") {
        if ($current -and $current.title) { $papers += $current }
        $current = @{ creators = @(); tags = @(); collections = @() }
    } elseif ($line -match "^TI\s+-\s*(.+)$") {
        $current.title = $matches[1].Trim()
    } elseif ($line -match "^AU\s+-\s*(.+)$") {
        $name = $matches[1].Trim()
        # 解析 Last, First
        if ($name -match "^(.+?),\s*(.+)$") {
            $last = $matches[1].Trim()
            $first = $matches[2].Trim()
        } else {
            $parts = $name -split "\s+"
            if ($parts.Count -ge 2) {
                $last = $parts[-1]
                $first = ($parts[0..($parts.Count-2)] -join " ").Trim()
            } else {
                $last = $name; $first = ""
            }
        }
        $current.creators += @{ creatorType = "author"; firstName = $first; lastName = $last }
    } elseif ($line -match "^PY\s+-\s*(.+)$") {
        $current.date = $matches[1].Trim()
    } elseif ($line -match "^UR\s+-\s*(.+)$") {
        $current.url = $matches[1].Trim()
    } elseif ($line -match "^T2\s+-\s*(.+)$") {
        $current.archive = $matches[1].Trim()
    } elseif ($line -match "^N1\s+-\s*(.+)$") {
        if ($current.abstractNote) {
            $current.abstractNote += "`n" + $matches[1].Trim()
        } else {
            $current.abstractNote = $matches[1].Trim()
        }
    } elseif ($line -match "^ER\s+-") {
        if ($current -and $current.title) { $papers += $current }
        $current = $null
    }
}
if ($current -and $current.title) { $papers += $current }
Log "解析得到 $($papers.Count) 篇论文"

# Step 1: 获取已有目录
Log "`n[1/4] 获取已有目录..."
$existing, $parentMap = GetExistingCollections
Log "  已有 $($existing.Count) 个目录"

# Step 2: 分类论文（根据标题关键词）
$COLLECTION_HIERARCHY = @{
    "大模型（科研模块）" = $null
    "大模型研究方向" = "大模型（科研模块）"
    "0-模型架构" = "大模型研究方向"
    "1-训练技术" = "大模型研究方向"
    "2-微调方法" = "大模型研究方向"
    "3-推理与部署" = "大模型研究方向"
    "4-检索增强RAG" = "大模型研究方向"
    "5-Agent与工具" = "大模型研究方向"
    "6-知识图谱" = "大模型研究方向"
    "7-多模态" = "大模型研究方向"
    "8-评估与对齐" = "大模型研究方向"
    "9-模型压缩" = "大模型研究方向"
    "LoRA研究" = "2-微调方法"
    "LoRA基础理论" = "LoRA研究"
    "LoRA变体" = "LoRA研究"
    "知识蒸馏" = "9-模型压缩"
    "模型量化" = "9-模型压缩"
    "注意力优化FlashAttn" = "3-推理与部署"
}

$PAPER_COLLECTION_MAP = @{
    "lora: low-rank adaptation" = @("LoRA基础理论", "LoRA研究", "2-微调方法")
    "qlora" = @("LoRA量化适配", "LoRA研究", "2-微调方法")
    "from large to small" = @("Transformer系列", "9-模型压缩", "大模型研究方向")
    "slm-mux" = @("Transformer系列", "9-模型压缩")
    "nrgpt" = @("Transformer系列", "0-模型架构")
    "futuremind" = @("5-Agent与工具", "大模型研究方向")
    "mobilellm-r1" = @("Transformer系列", "9-模型压缩", "大模型研究方向")
    "abba-adapters" = @("LoRA变体", "LoRA研究", "2-微调方法")
    "loft" = @("LoRA基础理论", "LoRA研究", "2-微调方法")
    "ld-mole" = @("LoRA变体", "LoRA研究", "2-微调方法")
    "lora meets riemannian" = @("LoRA基础理论", "LoRA研究", "2-微调方法")
    "titok" = @("LoRA变体", "LoRA研究", "2-微调方法")
    "q-rag" = @("4-检索增强RAG", "大模型研究方向")
    "enough is as good" = @("RLHF与对齐训练", "1-训练技术")
    "why dpo" = @("RLHF与对齐训练", "1-训练技术")
    "attention as a compass" = @("RLHF与对齐训练", "8-评估与对齐")
    "count counts" = @("RLHF与对齐训练", "大模型研究方向")
    "meta-rl induces" = @("Agent基础", "5-Agent与工具")
    "contextif" = @("RLHF与对齐训练", "1-训练技术")
    "emfuse" = @("1-训练技术", "大模型研究方向")
    "amid" = @("知识蒸馏", "9-模型压缩")
    "boomerang distillation" = @("知识蒸馏", "9-模型压缩")
    "bell box" = @("模型量化", "9-模型压缩")
    "anybcq" = @("模型量化", "9-模型压缩")
    "taming momentum" = @("LoRA研究", "2-微调方法")
    "freqkv" = @("3-推理与部署", "注意力优化FlashAttn")
    "lookaheadkv" = @("3-推理与部署", "LoRA研究", "2-微调方法")
    "efficient reasoning" = @("8-评估与对齐", "大模型研究方向")
    "inftithink" = @("8-评估与对齐", "大模型研究方向")
    "swireasoning" = @("8-评估与对齐", "大模型研究方向")
}

Log "`n[2/4] 分类论文并创建所需目录..."
$neededColls = @{}
foreach ($p in $papers) {
    $title = $p.title.ToLower()
    $colls = @("11-综述与全景")  # 默认
    foreach ($kv in $PAPER_COLLECTION_MAP.GetEnumerator()) {
        if ($title -match [regex]::Escape($kv.Key.ToLower())) {
            $colls = $kv.Value
            break
        }
    }
    $p.collections = $colls
    foreach ($c in $colls) { $neededColls[$c] = $true }
}

# 创建缺失的目录
$collMap = @{}
foreach ($kv in $existing.GetEnumerator()) { $collMap[$kv.Key] = $kv.Value }

# 先创建顶层目录
$topLevel = $COLLECTION_HIERARCHY.Keys | Where-Object { $COLLECTION_HIERARCHY[$_] -eq $null }
foreach ($name in $topLevel) {
    if ($collMap[$name]) { Log "  = 已存在: $name"; continue }
    Log "  + 创建顶层目录: $name"
    $body = @{ name = $name; parentCollection = $false } | ConvertTo-Json -Compress
    try {
        $resp = Invoke-RestMethod -Uri "$BASE/collections" -Headers @{ "Zotero-API-Key" = $API_KEY; "Content-Type" = "application/json" } -Method POST -Body ([System.Text.Encoding]::UTF8.GetBytes($body)) -TimeoutSec 30
        $key = $resp[0].key
        $collMap[$name] = $key
        Log "    ✓ key=$key"
    } catch {
        Log "    ✗ 创建失败: $_"
    }
    Start-Sleep -Milliseconds 400
}

# 再创建子目录
$children = $COLLECTION_HIERARCHY.Keys | Where-Object { $COLLECTION_HIERARCHY[$_] -ne $null }
foreach ($name in $children) {
    if ($collMap[$name]) { Log "  = 已存在: $name"; continue }
    $parentName = $COLLECTION_HIERARCHY[$name]
    $parentKey = $collMap[$parentName]
    if (-not $parentKey) {
        Log "  ! 父目录 $parentName 不存在，跳过: $name"
        continue
    }
    Log "  + 创建子目录: $name (父: $parentName)"
    $body = @{ name = $name; parentCollection = $parentKey } | ConvertTo-Json -Compress
    try {
        $resp = Invoke-RestMethod -Uri "$BASE/collections" -Headers @{ "Zotero-API-Key" = $API_KEY; "Content-Type" = "application/json" } -Method POST -Body ([System.Text.Encoding]::UTF8.GetBytes($body)) -TimeoutSec 30
        $key = $resp[0].key
        $collMap[$name] = $key
        Log "    ✓ key=$key"
    } catch {
        Log "    ✗ 创建失败: $_"
    }
    Start-Sleep -Milliseconds 400
}

Log "`n目录就绪，共 $($collMap.Count) 个"

# Step 3: 导入论文
Log "`n[3/4] 导入 $($papers.Count) 篇论文..."
$success = 0
foreach ($i in 0..($papers.Count-1)) {
    $p = $papers[$i]
    $titleShort = if ($p.title.Length -gt 40) { $p.title.Substring(0,40) + "..." } else { $p.title }
    Log "  [$i/$($papers.Count)] $titleShort"
    
    $itemType = "conferencePaper"
    if ($p.archive -and $p.archive -match "journal|transaction") { $itemType = "journalArticle" }
    
    $collKeys = @()
    foreach ($cn in $p.collections) {
        if ($collMap[$cn]) { $collKeys += $collMap[$cn] }
    }
    
    $item = @{
        itemType = $itemType
        title = $p.title
        creators = $p.creators
        date = $p.date
        url = $p.url
        archive = $p.archive
        abstractNote = $p.abstractNote
        tags = @()
    }
    if ($collKeys.Count -gt 0) { $item.collections = $collKeys }
    
    $body = @($item) | ConvertTo-Json -Depth 10 -Compress
    try {
        $resp = Invoke-RestMethod -Uri "$BASE/items" -Headers @{ "Zotero-API-Key" = $API_KEY; "Content-Type" = "application/json; charset=utf-8" } -Method POST -Body ([System.Text.Encoding]::UTF8.GetBytes($body)) -TimeoutSec 30
        $key = $resp.success."0"
        Log "    ✓ 添加成功 (key=$key)"
        $success++
    } catch {
        $status = $_.Exception.Response.StatusCode.value__
        if ($status -eq 409) {
            Log "    = 已存在，跳过"
            $success++
        } else {
            Log "    ✗ 添加失败: $_"
        }
    }
    Start-Sleep -Milliseconds 400
}

Log "`n" + "=" * 60
Log "完成！成功导入 $success/$($papers.Count) 篇论文到对应目录"
Log "=" * 60

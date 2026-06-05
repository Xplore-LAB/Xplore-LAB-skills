#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""独立导入 OKC-SFT 参考文献到 Zotero 独立文件夹"""
import json, urllib.request, urllib.error, time, re, os

API_KEY = "7VOWMztrbY56yVYJprUO9b1q"
USER_ID = "10931866"
RIS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CAC2026_OKC-SFT_refs.ris")
BASE = f"https://api.zotero.org/users/{USER_ID}"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(SCRIPT_DIR, "import_log_OKC-SFT.txt")

def log(msg):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    try:
        import sys
        sys.stdout.buffer.write((msg + "\n").encode("utf-8"))
        sys.stdout.buffer.flush()
    except:
        print(msg)

def api_call(method, endpoint, data=None, retries=2):
    url = BASE + "/" + endpoint.lstrip("/")
    headers = {"Zotero-API-Key": API_KEY, "Content-Type": "application/json; charset=utf-8"}
    body_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8") if data else None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, data=body_bytes, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.status, (json.loads(resp.read().decode("utf-8")) if resp.status != 204 else None)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            if e.code == 404: return 404, {}
            if attempt < retries:
                time.sleep(1)
                continue
            return e.code, {"error": body[:300]}
        except Exception as e:
            if attempt < retries:
                time.sleep(1)
                continue
            return 0, {"error": str(e)}
    return 0, {"error": "max retries"}

def get_or_create_collection(name, parent_key=None):
    """Get existing or create new collection. Returns collection key."""
    # Check if exists
    status, data = api_call("GET", "collections?limit=100")
    if status == 200 and data:
        for c in data:
            d = c["data"]
            if d["name"] == name:
                return d["key"]
    # Create
    payload = {"name": name}
    if parent_key:
        payload["parentCollection"] = parent_key
    status, result = api_call("POST", "collections", data=[payload])
    if status == 200 and result and "success" in result:
        key = result["success"].get("0")
        if key:
            log(f"  Created collection '{name}' -> {key}")
            return key
    # Try to get the key from created
    if result and "successful" in result:
        for k, v in result.get("successful", {}).items():
            if isinstance(v, dict) and "key" in v:
                log(f"  Created collection '{name}' -> {v['key']}")
                return v["key"]
    log(f"  FAILED to create collection '{name}': {result}")
    return None

def parse_ris(filepath):
    """Parse RIS file into list of paper dicts"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    papers = []
    current = {}
    for line in content.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("TY "):
            current = {"type": line[6:].strip()}
        elif line.startswith("TI "):
            current["title"] = line[6:].strip()
        elif line.startswith("AU "):
            if "authors" not in current:
                current["authors"] = []
            current["authors"].append(line[6:].strip())
        elif line.startswith("PY "):
            current["year"] = line[6:].strip()
        elif line.startswith("UR "):
            current["url"] = line[6:].strip()
        elif line.startswith("T2 "):
            current["journal"] = line[6:].strip()
        elif line.startswith("N1 "):
            current["note"] = line[6:].strip()
        elif line.startswith("DO "):
            current["doi"] = line[6:].strip()
        elif line.startswith("ER "):
            if current and "title" in current:
                papers.append(current)
            current = {}
    if current and "title" in current:
        papers.append(current)
    return papers

def classify_paper(title_lower, note=""):
    """Classify paper into sub-collection based on content"""
    text = title_lower + " " + note.lower()
    if any(k in text for k in ["fault diagnosis", "faultgpt", "phm", "s2s-fdd"]):
        return "1-LLM工业故障诊断微调"
    if any(k in text for k in ["kg-sft", "industrygpt", "glam", "knowledge graph"]):
        return "2-知识引导领域LLM训练"
    if any(k in text for k in ["air separation", "asu", "koopman", "rl-mpc"]):
        return "3-空分装置AI优化"
    if any(k in text for k in ["syn-diag", "cyberattack", "chemellm", "chemical engineering"]):
        return "4-流程行业LLM异常检测"
    if any(k in text for k in ["fine-tuned thoughts", "cot", "chain-of-thought", "shell", "digital twin", "ics"]):
        return "5-结构化知识注入工业决策"
    if any(k in text for k in ["foundation model", "factorynet", "epistemic", "hallucination"]):
        return "6-工业基础模型"
    return "1-LLM工业故障诊断微调"  # default

# ============ MAIN ============
log("=" * 60)
log("OKC-SFT 参考文献导入 Zotero")
log(f"RIS: {RIS_FILE}")
log("=" * 60)

# Step 1: Create collection hierarchy
log("\n[Step 1] Creating collection hierarchy...")
parent_key = get_or_create_collection("CAC2026_OKC-SFT_参考文献", parent_key=None)
if not parent_key:
    log("FATAL: Cannot create parent collection")
    exit(1)

sub_collections = [
    "1-LLM工业故障诊断微调",
    "2-知识引导领域LLM训练",
    "3-空分装置AI优化",
    "4-流程行业LLM异常检测",
    "5-结构化知识注入工业决策",
    "6-工业基础模型",
]
sub_keys = {}
for sub in sub_collections:
    key = get_or_create_collection(sub, parent_key=parent_key)
    if key:
        sub_keys[sub] = key
    time.sleep(0.3)

log(f"Created {len(sub_keys)}/6 sub-collections")

# Step 2: Parse RIS
log("\n[Step 2] Parsing RIS file...")
papers = parse_ris(RIS_FILE)
log(f"Parsed {len(papers)} papers from RIS")

# Step 3: Import papers
log("\n[Step 3] Importing papers...")
imported = 0
skipped = 0
for i, paper in enumerate(papers):
    title = paper["title"]
    title_lower = title.lower()
    authors = paper.get("authors", [])
    year = paper.get("year", "")
    url = paper.get("url", "")
    journal = paper.get("journal", "")
    note = paper.get("note", "")

    # Build Zotero item
    creators = []
    for au in authors:
        parts = au.split(",", 1)
        if len(parts) == 2:
            creators.append({"creatorType": "author", "lastName": parts[0].strip(), "firstName": parts[1].strip()})
        else:
            creators.append({"creatorType": "author", "name": au.strip()})

    item_data = {
        "itemType": "journalArticle",
        "title": title,
        "creators": creators,
        "date": year,
        "url": url,
        "publicationTitle": journal,
        "abstractNote": note if note else "",
    }

    # Classify into sub-collection
    sub_name = classify_paper(title_lower, note)
    col_key = sub_keys.get(sub_name)

    status, result = api_call("POST", "items", data=[item_data])
    if status == 200 and result:
        succ = result.get("success", {})
        item_key = None
        if "0" in succ:
            item_key = succ["0"]
        elif isinstance(succ, dict):
            for v in succ.values():
                if isinstance(v, str):
                    item_key = v
                    break
        if item_key:
            imported += 1
            # Add to collection
            if col_key:
                coll_data = {"collections": [col_key]}
                api_call("PATCH", f"items/{item_key}", data=coll_data)
            log(f"  [{i+1}/{len(papers)}] OK -> {sub_name}: {title[:80]}")
        else:
            log(f"  [{i+1}/{len(papers)}] WARN: no key returned for: {title[:60]}")
            skipped += 1
    elif status == 200 and isinstance(result, dict) and result.get("successful"):
        imported += 1
        log(f"  [{i+1}/{len(papers)}] OK (batch) -> {sub_name}: {title[:80]}")
    else:
        log(f"  [{i+1}/{len(papers)}] FAIL (status={status}): {title[:60]} {result}")
        skipped += 1

    time.sleep(0.3)  # Rate limit

log(f"\n{'='*60}")
log(f"IMPORT COMPLETE")
log(f"  Imported: {imported}")
log(f"  Skipped/Failed: {skipped}")
log(f"  Total: {len(papers)}")
log(f"  Parent: CAC2026_OKC-SFT_参考文献")
log(f"  Sub-collections: {len(sub_keys)}/6")
log(f"{'='*60}")

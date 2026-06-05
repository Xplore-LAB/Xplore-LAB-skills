#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zotero 清理脚本 - 删除指定列表的论文
"""

import json, urllib.request, urllib.error, time, os, sys

API_KEY = "7VOWMztrbY56yVYJprUO9b1q"
USER_ID = "10931866"
BASE = f"https://api.zotero.org/users/{USER_ID}"

def api_call(method, endpoint, data=None, extra_headers=None):
    url = BASE + "/" + endpoint.lstrip("/")
    headers = {"Zotero-API-Key": API_KEY, "Content-Type": "application/json"}
    if extra_headers:
        headers.update(extra_headers)
    body = json.dumps(data, ensure_ascii=False).encode("utf-8") if data else None
    try:
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read()
            return r.status, json.loads(body.decode("utf-8")) if body else None, dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, None, dict(e.headers)

# 需要删除的论文标题列表
TITLES_TO_DELETE = [
    "LoRA: Low-Rank Adaptation of Large Language Models",
    "QLoRA: Efficient Finetuning of Quantized LLMs",
    "DoRA: Weight-Decomposed Low-Rank Adaptation",
    "AdaLoRA: Adaptive Budget Allocation for Parameter-Efficient Fine-Tuning",
    "LoRA-GA: Low-Rank Adaptation with Gradient Approximation",
    "GoRA: Gradient-driven Adaptive Low Rank Adaptation",
    "BayesLoRA: Task-Specific Uncertainty in Low-Rank Adapters",
    "KD-LoRA: A Hybrid Approach to Efficient Fine-Tuning with LoRA and Knowledge Distillation",
    "GaLore: Gradient Low-Rank Projection for Memory-Efficient LLM Training",
    "Editing Models with Task Arithmetic",
    "TIES-Merging: Resolving Interference When Merging Models",
    "ConsNoTrainLoRA: Data-driven Weight Initialization of Low-rank Adapters using Constraints",
    "AuroRA: Breaking Low-Rank Bottleneck of LoRA with Nonlinear Projections",
    "MoRE: A Mixture of Low-Rank Experts for Adaptive Multi-Task Learning",
    "R-LoRA: Randomized Multi-Head LoRA for Efficient Multi-Task Learning",
    "MeteoRA: Multiple-tasks Embedded LoRA for Large Language Models",
    "LoRA Dropout as a Sparsity Regularizer for Overfitting Reduction",
    "Adaptive Rank, Reduced Forgetting: Knowledge Retention in Continual Learning with Dynamic Rank LoRA",
    "SLoRA: Scalable Serving of Thousands of LoRA Adapters",
    "LoRAHub: Efficient Cross-Task Generalization via Dynamic LoRA Combination",
    "Comp-LoRA: Unified Framework for Continual Learning with LoRA",
    "Make LoRA Great Again: Boosting LoRA with Adaptive Singular Value Initialization",
    "PiSSA: Principal Singular Values and Singular Vectors Adaptation of Large Language Models",
    "LoRA-FA: LoRA with Feature Adaptation",
    "A Survey on Parameter-Efficient Fine-Tuning of Large Language Models",
    "Revisiting Fine-Tuning: A Survey of Parameter-Efficient Approaches",
    "LLaMA-Adapter: Efficient Fine-tuning of Language Models with Zero-init Attention",
    "The Power of Scale for Parameter-Efficient Prompt Tuning",
    "Prefix-Tuning: Optimizing Continuous Prompts for Generation",
]

def main():
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cleanup_log.txt")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("")
    def log(msg):
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
        try:
            sys.stdout.buffer.write((msg + "\n").encode("utf-8"))
            sys.stdout.buffer.flush()
        except: pass

    log("=" * 60)
    log("Zotero 清理 - 删除已导入的论文")
    log("=" * 60)

    # 1. 分页获取所有 items
    log("\n[1/2] 获取 Zotero 库中的所有 items...")
    all_items = []
    start = 0
    limit = 50
    while True:
        status, data, headers = api_call("GET", f"items?limit={limit}&start={start}")
        if status != 200 or not data:
            break
        all_items.extend(data)
        if len(data) < limit:
            break
        start += limit
        time.sleep(0.3)
    log(f"  共获取 {len(all_items)} 个 items")

    # 2. 匹配并删除
    log(f"\n[2/2] 匹配并删除论文...")
    deleted = 0
    for item in all_items:
        title = item.get("data", {}).get("title", "")
        if title in TITLES_TO_DELETE:
            item_key = item["data"]["key"]
            version = item["data"]["version"]
            # DELETE 需要 version header
            status, _, _ = api_call("DELETE", f"items/{item_key}", extra_headers={
                "If-Unmodified-Since-Version": str(version)
            })
            if status == 204:
                log(f"  ✓ 已删除: {title[:50]}")
                deleted += 1
            else:
                log(f"  ✗ 删除失败: {title[:40]}, HTTP {status}")
            time.sleep(0.3)

    log(f"\n完成！已删除 {deleted} 篇论文")
    log("=" * 60)

if __name__ == "__main__":
    main()

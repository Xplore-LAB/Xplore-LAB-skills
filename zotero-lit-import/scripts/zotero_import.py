#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zotero 批量导入 - 从 RIS 文件自动解析并导入
用法：python zotero_import_from_ris.py
"""

import json
import urllib.request
import urllib.error
import time
import re
import os

if hasattr(__builtins__, 'print'):
    pass

log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "import_log.txt")

def log(msg):
    import sys
    # 写日志文件（UTF-8）
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    # 写控制台（绕过编码问题）
    try:
        sys.stdout.buffer.write((msg + "\n").encode("utf-8"))
        sys.stdout.buffer.flush()
    except:
        pass

# ============ 配置 ============
API_KEY = "7VOWMztrbY56yVYJprUO9b1q"  # Zotero API Key
USER_ID = "10931866"                   # Zotero User ID
RIS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ICLR2026_papers.ris")  # ICLR 2026 论文（LoRA/小模型/RL）
BASE = f"https://api.zotero.org/users/{USER_ID}"
# ==========================================


def api_call(method, endpoint, data=None, retries=2):
    url = BASE + "/" + endpoint.lstrip("/")
    headers = {
        "Zotero-API-Key": API_KEY,
        "Content-Type": "application/json; charset=utf-8",
    }
    body_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8") if data else None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, data=body_bytes, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=30) as resp:
                status = resp.status
                body = resp.read().decode("utf-8")
                return status, (json.loads(body) if body else None)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            if attempt < retries:
                time.sleep(1)
                continue
            return e.code, {"error": body[:500]}
        except Exception as e:
            if attempt < retries:
                time.sleep(1)
                continue
            return 0, {"error": str(e)}
    return 0, {"error": "max retries"}


def get_existing_collections():
    status, data = api_call("GET", "collections?limit=100")
    if status == 200 and data:
        # 返回: {name: key} 和 {key: parent_key}
        name_to_key = {}
        key_to_parent = {}
        for c in data:
            d = c["data"]
            name_to_key[d["name"]] = d["key"]
            parent = d.get("parentCollection")
            if parent and parent != False:
                key_to_parent[d["key"]] = parent
        return name_to_key, key_to_parent
    return {}, {}


# 目录层级定义：子目录 → 父目录名
# None 表示顶层目录
COLLECTION_HIERARCHY = {
    # === 顶层 ===
    "大模型（科研模块）": None,

    # === 大模型研究方向 ===
    "大模型研究方向": "大模型（科研模块）",
    "0-模型架构": "大模型研究方向",
    "1-训练技术": "大模型研究方向",
    "2-微调方法": "大模型研究方向",
    "3-推理与部署": "大模型研究方向",
    "4-检索增强RAG": "大模型研究方向",
    "5-Agent与工具": "大模型研究方向",
    "6-知识图谱": "大模型研究方向",
    "7-多模态": "大模型研究方向",
    "8-评估与对齐": "大模型研究方向",
    "9-模型压缩": "大模型研究方向",
    "10-Tokenization": "大模型研究方向",
    "11-综述与全景": "大模型研究方向",

    # === 公司专区 ===
    "大模型公司技术论文": "大模型（科研模块）",
    "OpenAI": "大模型公司技术论文",
    "Google-DeepMind": "大模型公司技术论文",
    "Meta-FAIR": "大模型公司技术论文",
    "DeepSeek": "大模型公司技术论文",
    "Anthropic": "大模型公司技术论文",
    "Microsoft": "大模型公司技术论文",
    "Mistral-AI": "大模型公司技术论文",
    "Others-Qwen-Yi": "大模型公司技术论文",
    "大模型公司技术论文": None,

    # === 模型架构 子目录 ===
    "Transformer系列": "0-模型架构",
    "MoE混合专家": "0-模型架构",
    "位置编码": "0-模型架构",
    "状态空间模型": "0-模型架构",

    # === 训练技术 子目录 ===
    "预训练与Scaling": "1-训练技术",
    "分布式训练": "1-训练技术",
    "RLHF与对齐训练": "1-训练技术",

    # === 微调方法 子目录（含LoRA研究全套） ===
    "PEFT基础方法": "2-微调方法",
    "全量微调": "2-微调方法",
    "LoRA研究": "2-微调方法",
    # LoRA研究 子目录
    "LoRA基础理论": "LoRA研究",
    "LoRA变体": "LoRA研究",
    "LoRA初始化方法": "LoRA研究",
    "LoRA量化适配": "LoRA研究",
    "LoRA前沿2025": "LoRA研究",
    "LoRA知识蒸馏": "LoRA研究",
    "LoRA多任务与持续学习": "LoRA研究",
    "LoRA模型合并与服务": "LoRA研究",
    "LoRA正则化与非线性": "LoRA研究",

    # === 推理与部署 子目录 ===
    "注意力优化FlashAttn": "3-推理与部署",
    "推理服务量化": "3-推理与部署",

    # === RAG 子目录 ===
    "RAG基础方法": "4-检索增强RAG",
    "嵌入与检索": "4-检索增强RAG",

    # === Agent 子目录 ===
    "Agent基础": "5-Agent与工具",
    "Agentic系统与工作流": "5-Agent与工具",

    # === 知识图谱 子目录 ===
    "KG基础方法": "6-知识图谱",
    "LLM与KG交叉": "6-知识图谱",

    # === 多模态 子目录 ===
    "视觉语言模型VLM": "7-多模态",
    "文生图与视频": "7-多模态",

    # === 评估与对齐 子目录 ===
    "评估基准": "8-评估与对齐",
    "安全对齐": "8-评估与对齐",

    # === 模型压缩 子目录 ===
    "知识蒸馏": "9-模型压缩",
    "模型量化": "9-模型压缩",
}


# 论文→目录映射（标题关键词 → [目录名列表]）
# 用于 classify_paper 的精准分类
PAPER_COLLECTION_MAP = {
    # 模型架构
    "attention is all you need": ["Transformer系列", "0-模型架构"],
    "bert: pre-training": ["Transformer系列", "0-模型架构"],
    "language models are few-shot": ["Transformer系列", "0-模型架构"],
    "gpt-3": ["Transformer系列", "0-模型架构"],
    "llama: open and efficient": ["Transformer系列", "0-模型架构"],
    "llama 2: open foundation": ["Transformer系列", "0-模型架构"],
    "llama 3": ["Transformer系列", "0-模型架构"],
    "deepseek-v2": ["Transformer系列", "0-模型架构"],
    "glm-130b": ["Transformer系列", "0-模型架构"],
    "outrageously large neural networks": ["MoE混合专家", "0-模型架构"],
    "switch transformers": ["MoE混合专家", "0-模型架构"],
    "mixtral of experts": ["MoE混合专家", "0-模型架构"],
    "deepseek-moe": ["MoE混合专家", "0-模型架构"],
    "roformer": ["位置编码", "0-模型架构"],
    "train short, test long": ["位置编码", "0-模型架构"],
    "mamba: linear-time": ["状态空间模型", "0-模型架构"],
    
    # 训练技术
    "scaling laws for neural": ["预训练与Scaling", "1-训练技术"],
    "training compute-optimal": ["预训练与Scaling", "1-训练技术"],
    "chinchilla": ["预训练与Scaling", "1-训练技术"],
    "megatron-lm": ["分布式训练", "1-训练技术"],
    "zero: memory optimizations": ["分布式训练", "1-训练技术"],
    "efficient large-scale language model training on gpu": ["分布式训练", "1-训练技术"],
    "reducing activation recomputation": ["分布式训练", "1-训练技术"],
    "training language models to follow instructions": ["RLHF与对齐训练", "1-训练技术"],
    "instructgpt": ["RLHF与对齐训练", "1-训练技术"],
    "constitutional ai": ["RLHF与对齐训练", "1-训练技术"],
    "direct preference optimization": ["RLHF与对齐训练", "1-训练技术"],
    "secrets of rlhf": ["RLHF与对齐训练", "1-训练技术"],
    "scaling data-constrained": ["预训练与Scaling", "1-训练技术"],
    "doremi: optimizing data": ["预训练与Scaling", "1-训练技术"],
    
    # 微调方法
    "parameter-efficient transfer learning for nlp": ["PEFT基础方法", "2-微调方法"],
    "prefix-tuning": ["PEFT基础方法", "2-微调方法"],
    "power of scale for parameter-efficient": ["PEFT基础方法", "2-微调方法"],
    "llama-adapter": ["PEFT基础方法", "2-微调方法"],
    "survey on parameter-efficient fine-tuning of large": ["PEFT基础方法", "2-微调方法", "11-综述与全景"],
    
    # LoRA系列专用分类
    "lora: low-rank adaptation": ["LoRA基础理论", "LoRA研究", "2-微调方法"],
    "qlora": ["LoRA量化适配", "LoRA研究", "2-微调方法"],
    "dora: weight-decomposed": ["LoRA变体", "LoRA研究", "2-微调方法"],
    "adalora": ["LoRA变体", "LoRA研究", "2-微调方法"],
    "lora-ga": ["LoRA初始化方法", "LoRA研究", "2-微调方法"],
    "pissa": ["LoRA初始化方法", "LoRA研究", "2-微调方法"],
    "consnotrainlora": ["LoRA初始化方法", "LoRA研究", "2-微调方法"],
    "gora: gradient-driven": ["LoRA前沿2025", "LoRA研究", "2-微调方法"],
    "bayeslora": ["LoRA前沿2025", "LoRA研究", "2-微调方法"],
    "kd-lora": ["LoRA知识蒸馏", "LoRA研究", "2-微调方法"],
    "galore": ["全量微调", "2-微调方法"],
    "autora": ["LoRA变体", "LoRA研究", "2-微调方法"],
    "more: a mixture": ["LoRA多任务与持续学习", "LoRA研究", "2-微调方法"],
    "r-lora": ["LoRA多任务与持续学习", "LoRA研究", "2-微调方法"],
    "meteora": ["LoRA多任务与持续学习", "LoRA研究", "2-微调方法"],
    "adaptive rank, reduced forgetting": ["LoRA多任务与持续学习", "LoRA研究", "2-微调方法"],
    "ties-merging": ["LoRA模型合并与服务", "LoRA研究", "2-微调方法"],
    "editing models with task arithmetic": ["LoRA模型合并与服务", "LoRA研究", "2-微调方法"],
    "sulora: subspace": ["LoRA变体", "LoRA研究", "2-微调方法"],
    "rectlora": ["LoRA变体", "LoRA研究", "2-微调方法"],
    
    # 推理与部署
    "flashattention: fast and memory": ["注意力优化FlashAttn", "3-推理与部署"],
    "flashattention-2": ["注意力优化FlashAttn", "3-推理与部署"],
    "fast transformer decoding": ["注意力优化FlashAttn", "3-推理与部署"],
    "gqa: training generalized": ["注意力优化FlashAttn", "3-推理与部署"],
    "ring attention": ["注意力优化FlashAttn", "3-推理与部署"],
    "efficient memory management for large language model serving": ["推理服务量化", "3-推理与部署"],
    "vllm": ["推理服务量化", "3-推理与部署"],
    "llm.int8": ["推理服务量化", "3-推理与部署"],
    "awq: activation-aware": ["推理服务量化", "3-推理与部署"],
    "gptq: accurate post-training": ["推理服务量化", "3-推理与部署"],
    "specinfer": ["推理服务量化", "3-推理与部署"],
    
    # RAG
    "retrieval-augmented generation for knowledge": ["RAG基础方法", "4-检索增强RAG"],
    "realm: retrieval-augmented language": ["RAG基础方法", "4-检索增强RAG"],
    "dense passage retrieval": ["RAG基础方法", "4-检索增强RAG"],
    "lost in the middle": ["RAG基础方法", "4-检索增强RAG"],
    "self-rag": ["RAG基础方法", "4-检索增强RAG"],
    "raptor: recursive": ["RAG基础方法", "4-检索增强RAG"],
    "sentence-bert": ["嵌入与检索", "4-检索增强RAG"],
    "text embeddings by weakly-supervised": ["嵌入与检索", "4-检索增强RAG"],
    "colbert: efficient": ["嵌入与检索", "4-检索增强RAG"],
    
    # Agent
    "react: synergizing reasoning": ["Agent基础", "5-Agent与工具"],
    "tree of thoughts": ["Agent基础", "5-Agent与工具"],
    "reflexion: language agents": ["Agent基础", "5-Agent与工具"],
    "toolformer": ["Agent基础", "5-Agent与工具"],
    "gorilla: large language model connected": ["Agent基础", "5-Agent与工具"],
    "generative agents": ["Agent基础", "5-Agent与工具"],
    "voyager: an open-ended": ["Agent基础", "5-Agent与工具"],
    
    # Agentic 系统与工作流
    "agentic ai: a comprehensive survey": ["Agentic系统与工作流", "5-Agent与工具", "11-综述与全景"],
    "survey on llm-based agentic workflow": ["Agentic系统与工作流", "5-Agent与工具", "11-综述与全景"],
    "large language model agent: a survey on methodology": ["Agentic系统与工作流", "5-Agent与工具", "11-综述与全景"],
    "beyond self-talk": ["Agentic系统与工作流", "5-Agent与工具", "11-综述与全景"],
    "multimodal llm agent survey": ["Agentic系统与工作流", "5-Agent与工具", "11-综述与全景"],
    "autogen: enabling next-gen": ["Agentic系统与工作流", "5-Agent与工具"],
    "agentverse": ["Agentic系统与工作流", "5-Agent与工具"],
    "metagpt: meta programming": ["Agentic系统与工作流", "5-Agent与工具"],
    "building effective ai agents": ["Agentic系统与工作流", "5-Agent与工具", "Anthropic", "大模型公司技术论文"],
    "landscape of emerging ai agent": ["Agentic系统与工作流", "5-Agent与工具"],
    "agentbench: evaluating llms as agents": ["Agentic系统与工作流", "5-Agent与工具"],
    "tool learning with foundation": ["Agentic系统与工作流", "5-Agent与工具"],
    "easyagent": ["Agentic系统与工作流", "5-Agent与工具"],
    "swe-agent": ["Agentic系统与工作流", "5-Agent与工具"],
    "webarena": ["Agentic系统与工作流", "5-Agent与工具"],
    "agentgym: a benchmark": ["Agentic系统与工作流", "5-Agent与工具"],
    "communication under the swarms": ["Agentic系统与工作流", "5-Agent与工具", "11-综述与全景"],
    
    # 知识图谱
    "translating embeddings for modeling": ["KG基础方法", "6-知识图谱"],
    "knowledge graph embedding: a survey": ["KG基础方法", "6-知识图谱"],
    "think-on-graph": ["LLM与KG交叉", "6-知识图谱"],
    
    # 多模态
    "clip: learning transferable": ["视觉语言模型VLM", "7-多模态"],
    "blip-2": ["视觉语言模型VLM", "7-多模态"],
    "visual instruction tuning": ["视觉语言模型VLM", "7-多模态"],
    "llava": ["视觉语言模型VLM", "7-多模态"],
    "flamingo: a visual": ["视觉语言模型VLM", "7-多模态"],
    "qwen-vl": ["视觉语言模型VLM", "7-多模态"],
    "denoising diffusion probabilistic": ["文生图与视频", "7-多模态"],
    "high-resolution image synthesis with latent": ["文生图与视频", "7-多模态"],
    "imagen: photorealistic": ["文生图与视频", "7-多模态"],
    "dall-e: zero-shot": ["文生图与视频", "7-多模态", "OpenAI", "大模型公司技术论文"],
    "dall-e 2: hierarchical": ["文生图与视频", "7-多模态", "OpenAI", "大模型公司技术论文"],
    "video diffusion models": ["文生图与视频", "7-多模态"],
    
    # 知识图谱
    "complex: complex embeddings": ["KG基础方法", "6-知识图谱"],
    "rotate: knowledge graph embedding by": ["KG基础方法", "6-知识图谱"],
    "kepler: a unified model": ["KG基础方法", "6-知识图谱"],
    "large language models and knowledge graphs: opportunities": ["LLM与KG交叉", "6-知识图谱", "11-综述与全景"],
    
    # 训练补充
    "data-juicer": ["预训练与Scaling", "1-训练技术"],
    "dolly: instruction tuning": ["预训练与Scaling", "1-训练技术"],
    
    # 模型结构补充
    "rwkv: reinventing rnns": ["Transformer系列", "0-模型架构"],
    
    # 正则化
    "dropout: a simple way": ["正则化与非线性", "LoRA研究", "2-微调方法"],
    "label smoothing": ["正则化与非线性", "LoRA研究", "2-微调方法"],
    "weight decay": ["正则化与非线性", "LoRA研究", "2-微调方法"],
    
    # 评估与对齐
    "glue: a multi-task benchmark": ["评估基准", "8-评估与对齐"],
    "superglue": ["评估基准", "8-评估与对齐"],
    "judging llm-as-a-judge": ["评估基准", "8-评估与对齐"],
    "mmlu: measuring massive": ["评估基准", "8-评估与对齐"],
    "gsm8k": ["评估基准", "8-评估与对齐"],
    "humaneval": ["评估基准", "8-评估与对齐"],
    "hellaswag": ["评估基准", "8-评估与对齐"],
    "big-bench": ["评估基准", "8-评估与对齐"],
    "helm: holistic": ["评估基准", "8-评估与对齐"],
    "truthfulqa": ["评估基准", "8-评估与对齐"],
    "arc: a challenge": ["评估基准", "8-评估与对齐"],
    "red teaming language models": ["安全对齐", "8-评估与对齐"],
    
    # 模型压缩
    "distilbert": ["知识蒸馏", "9-模型压缩"],
    "knowledge distillation: a survey": ["知识蒸馏", "9-模型压缩"],
    "distilling the knowledge in a neural": ["知识蒸馏", "9-模型压缩"],
    "tinybert: distilling bert": ["知识蒸馏", "9-模型压缩"],
    "mobilebert: a compact": ["知识蒸馏", "9-模型压缩"],
    "deep compression": ["模型量化", "9-模型压缩"],
    "smoothquant: accurate": ["模型量化", "9-模型压缩"],
    "q-bert: hessian": ["模型量化", "9-模型压缩"],
    "zeroquant: efficient": ["模型量化", "9-模型压缩"],
    
    # Tokenization
    "neural machine translation of rare words with subword": ["10-Tokenization"],
    "sentencepiece": ["10-Tokenization"],
    "google's neural machine translation": ["10-Tokenization"],
    "subword regularization": ["10-Tokenization"],
    "tokenization matters": ["10-Tokenization"],
    
    # 综述
    "a survey of large language models": ["11-综述与全景"],
    "opportunities and risks of foundation": ["11-综述与全景"],
    "sparks of artificial general intelligence": ["11-综述与全景"],
    "revisiting fine-tuning": ["11-综述与全景"],
    
    # === 公司专区 ===
    # OpenAI
    "improving language understanding by generative": ["OpenAI", "大模型公司技术论文"],
    "language models are unsupervised": ["OpenAI", "大模型公司技术论文"],
    "gpt-4 technical report": ["OpenAI", "大模型公司技术论文"],
    "learning to reason with llms": ["OpenAI", "大模型公司技术论文"],
    "gpt-4o system card": ["OpenAI", "大模型公司技术论文"],
    # Google-DeepMind
    "t5: exploring the limits": ["Google-DeepMind", "大模型公司技术论文"],
    "palm: scaling language": ["Google-DeepMind", "大模型公司技术论文"],
    "palm 2 technical report": ["Google-DeepMind", "大模型公司技术论文"],
    "gemini: a family of highly": ["Google-DeepMind", "大模型公司技术论文"],
    "gemma: open models": ["Google-DeepMind", "大模型公司技术论文"],
    # Meta-FAIR
    "opt: open pre-trained": ["Meta-FAIR", "大模型公司技术论文"],
    "code llama": ["Meta-FAIR", "大模型公司技术论文"],
    "segment anything": ["Meta-FAIR", "大模型公司技术论文"],
    "galactica: a large language model for science": ["Meta-FAIR", "大模型公司技术论文"],
    "meta llama 3.1": ["Meta-FAIR", "大模型公司技术论文"],
    # DeepSeek
    "deepseek-r1": ["DeepSeek", "大模型公司技术论文"],
    "deepseek-coder": ["DeepSeek", "大模型公司技术论文"],
    "deepseek-v3": ["DeepSeek", "大模型公司技术论文"],
    "deepseek-prover": ["DeepSeek", "大模型公司技术论文"],
    # Anthropic
    "training a helpful and harmless": ["Anthropic", "大模型公司技术论文"],
    "claude model": ["Anthropic", "大模型公司技术论文"],
    # Microsoft
    "textbooks are all you need": ["Microsoft", "大模型公司技术论文"],
    "phi-2": ["Microsoft", "大模型公司技术论文"],
    "phi-3 technical report": ["Microsoft", "大模型公司技术论文"],
    "deepspeed: system optimizations": ["Microsoft", "大模型公司技术论文"],
    # Mistral
    "mistral 7b": ["Mistral-AI", "大模型公司技术论文"],
    "mistral large": ["Mistral-AI", "大模型公司技术论文"],
    # Others
    "qwen technical report": ["Others-Qwen-Yi", "大模型公司技术论文"],
    "qwen2 technical report": ["Others-Qwen-Yi", "大模型公司技术论文"],
    "yi: open foundation": ["Others-Qwen-Yi", "大模型公司技术论文"],
    "falcon llm": ["Others-Qwen-Yi", "大模型公司技术论文"],
    # === ICLR 2026 新增论文分类 ===
    # 小语言模型
    "from large to small": ["Transformer系列", "9-模型压缩", "大模型研究方向"],
    "slm-mux": ["Transformer系列", "9-模型压缩"],
    "nrgpt": ["Transformer系列", "0-模型架构"],
    "long-document qa": ["8-评估与对齐", "大模型研究方向"],
    "futuremind": ["5-Agent与工具", "大模型研究方向"],
    "mobilellm-r1": ["Transformer系列", "9-模型压缩", "大模型研究方向"],
    # LoRA / PEFT
    "abba-adapters": ["LoRA变体", "LoRA研究", "2-微调方法"],
    "loft": ["LoRA基础理论", "LoRA研究", "2-微调方法"],
    "ld-mole": ["LoRA变体", "LoRA研究", "2-微调方法"],
    "lora meets riemannian": ["LoRA基础理论", "LoRA研究", "2-微调方法"],
    "titok": ["LoRA变体", "LoRA研究", "2-微调方法"],
    # 模型压缩
    "parer": ["全量微调", "9-模型压缩"],
    "amid": ["知识蒸馏", "9-模型压缩"],
    "boomerang distillation": ["知识蒸馏", "9-模型压缩"],
    "bell box quantization": ["模型量化", "9-模型压缩"],
    "anybcq": ["模型量化", "9-模型压缩"],
    "compute-optimal quantization": ["模型量化", "9-模型压缩"],
    "taming momentum": ["LoRA研究", "2-微调方法"],
    "pamm": ["3-推理与部署", "大模型研究方向"],
    "freqkv": ["3-推理与部署", "注意力优化FlashAttn"],
    "lookaheadkv": ["3-推理与部署", "LoRA研究", "2-微调方法"],
    "es-dllm": ["3-推理与部署", "大模型研究方向"],
    "parallel token prediction": ["0-模型架构", "大模型研究方向"],
    "embedding compression": ["9-模型压缩", "大模型研究方向"],
    # 强化学习 + LLM
    "q-rag": ["4-检索增强RAG", "大模型研究方向"],
    "deepcompress": ["8-评估与对齐", "大模型研究方向"],
    "emfuse": ["1-训练技术", "大模型研究方向"],
    "enough is as good": ["RLHF与对齐训练", "1-训练技术"],
    "why dpo is a misspecified": ["RLHF与对齐训练", "1-训练技术"],
    "count counts": ["RLHF与对齐训练", "大模型研究方向"],
    "meta-rl induces exploration": ["Agent基础", "5-Agent与工具"],
    "contextif": ["RLHF与对齐训练", "1-训练技术"],
    "attention as a compass": ["RLHF与对齐训练", "8-评估与对齐"],
    "recurrent action transformer": ["Agent基础", "5-Agent与工具"],
    "elmur": ["Agent基础", "5-Agent与工具"],
    # 知识蒸馏
    "pedagogically-inspired": ["知识蒸馏", "9-模型压缩"],
    "distillation of large language models via concrete": ["知识蒸馏", "9-模型压缩"],
    "star": ["知识蒸馏", "9-模型压缩"],
    # 推理优化
    "efficient reasoning": ["8-评估与对齐", "大模型研究方向"],
    "inftithink": ["8-评估与对齐", "大模型研究方向"],
    "swireasoning": ["8-评估与对齐", "大模型研究方向"],
    "state-transition framework": ["0-模型架构", "大模型研究方向"],
    "unify": ["4-检索增强RAG", "大模型研究方向"],
}


def create_collection(name, parent_key=None):
    body = {"name": name, "parentCollection": parent_key if parent_key else False}
    status, resp = api_call("POST", "collections", [body])
    if status == 200 and resp and isinstance(resp, list) and len(resp) > 0:
        key = resp[0]["key"]
        log(f"  ✓ 创建目录: {name} (key={key})")
        return key
    # 也处理 {"successful": ...} 格式
    if status == 200 and resp and "successful" in resp:
        key = resp["successful"]["0"]["key"]
        log(f"  ✓ 创建目录: {name} (key={key})")
        return key
    log(f"  ✗ 创建失败: {name}, HTTP {status}")
    return None


def create_item(paper):
    status, resp = api_call("POST", "items", [paper])
    if status == 200 and resp and "success" in resp:
        key = resp["success"]["0"]
        return key
    log(f"  ✗ 添加失败: {paper.get('title','?')[:40]}, HTTP {status}")
    return None


def add_to_collection(item_key, coll_key):
    # PATCH 更新单个条目的 collections 字段
    status, _ = api_call("PATCH", f"items/{item_key}", {"collections": [coll_key]})
    return status == 200


# ============ RIS 解析 ============

def parse_ris(filepath):
    """解析 RIS 文件，返回论文列表"""
    papers = []
    current = None
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # 新条目开始
            if line.startswith("TY  -"):
                if current and current.get("title"):
                    papers.append(current)
                current = {"creators": [], "tags": [], "collections": []}
            elif line.startswith("TI  -"):
                current["title"] = line[6:].strip()
            elif line.startswith("AU  -"):
                name = line[6:].strip()
                # 格式：Last, First Middle
                if "," in name:
                    parts = name.split(",", 1)
                    last = parts[0].strip()
                    first = parts[1].strip()
                else:
                    # 没有逗号，假设是 Last First 格式
                    parts = name.split()
                    if len(parts) >= 2:
                        last = parts[-1]
                        first = " ".join(parts[:-1])
                    else:
                        last = name
                        first = ""
                current["creators"].append({
                    "creatorType": "author",
                    "firstName": first,
                    "lastName": last
                })
            elif line.startswith("PY  -"):
                current["date"] = line[6:].strip()
            elif line.startswith("UR  -"):
                current["url"] = line[6:].strip()
            elif line.startswith("T2  -"):
                current["archive"] = line[6:].strip()
            elif line.startswith("N1  -"):
                current["abstractNote"] = line[6:].strip()
            elif line.startswith("M3  -"):
                m3 = line[6:].strip()
                if "abstractNote" in current:
                    current["abstractNote"] += f"\n{m3}"
                else:
                    current["abstractNote"] = m3
            elif line.startswith("ER  -"):
                if current and current.get("title"):
                    papers.append(current)
                current = None
    if current and current.get("title"):
        papers.append(current)
    return papers


def classify_paper(paper):
    """根据 PAPER_COLLECTION_MAP 精准分类"""
    title = paper.get("title", "").lower()
    
    # 在映射表中查找匹配
    matched_colls = None
    for key, colls in PAPER_COLLECTION_MAP.items():
        if key in title:
            matched_colls = colls
            break
    
    if matched_colls:
        paper["collections"] = matched_colls
        paper["tags"] = []
    else:
        # 默认放入"11-综述与全景"
        paper["collections"] = ["11-综述与全景"]
        paper["tags"] = []
    
    # 确定 itemType
    archive = paper.get("archive", "").lower()
    if any(k in archive for k in ["conference", "neurips", "iclr", "icml", "acl", "emnlp", "cvpr", "iccv", "sigir", "uist", "sosp", "sc ", "mlsys"]):
        paper["itemType"] = "conferencePaper"
    else:
        paper["itemType"] = "journalArticle"
    
    return paper
    paper["tags"] = [{"tag": t} for t in tags]
    return paper


def main():
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("")
    
    log("=" * 60)
    log("Zotero 批量导入（从 RIS 文件）")
    
    # Step 0: 解析 RIS
    log(f"解析 RIS 文件: {RIS_FILE}")
    papers_raw = parse_ris(RIS_FILE)
    log(f"解析得到 {len(papers_raw)} 篇论文")
    
    # Step 0.5: 分类
    papers = [classify_paper(p) for p in papers_raw]
    
    # Step 1: 获取已有目录
    log("\n[1/4] 获取已有目录...")
    existing, _ = get_existing_collections()
    log(f"  已有 {len(existing)} 个目录")
    
    # Step 2: 收集并创建所需目录（按层级顺序）
    needed_colls = set()
    for p in papers:
        for c in p.get("collections", []):
            needed_colls.add(c)
    
    log(f"\n[2/4] 检查 {len(needed_colls)} 个目录（含层级关系）...")
    coll_map = dict(existing)
    
    # 按拓扑排序：先创建父目录，再创建子目录
    def sort_by_hierarchy(names):
        """将目录按父子依赖关系排序"""
        result = []
        # 先处理顶层目录（没有父目录的）
        tops = [n for n in names if COLLECTION_HIERARCHY.get(n) is None]
        children = [n for n in names if COLLECTION_HIERARCHY.get(n) is not None]
        result = list(tops) + list(children)
        # 不在 hierarchy 中的排在最后
        others = [n for n in names if n not in COLLECTION_HIERARCHY]
        result = [n for n in result if n in names] + others
        return result
    
    for name in sort_by_hierarchy(list(needed_colls)):
        if name in coll_map:
            log(f"  = 已存在: {name}")
        else:
            # 查找父目录 key
            parent_name = COLLECTION_HIERARCHY.get(name)
            parent_key = coll_map.get(parent_name) if parent_name else None
            log(f"  + 创建: {name}" + (f" (父目录: {parent_name})" if parent_name else ""))
            key = create_collection(name, parent_key)
            if key:
                coll_map[name] = key
            time.sleep(0.4)
    
    log(f"\n目录就绪，共 {len(coll_map)} 个")
    
    # Step 3: 导入论文
    log(f"\n[3/4] 导入 {len(papers)} 篇论文...")
    success = 0
    item_key_map = {}  # title -> key 映射
    
    for i, paper in enumerate(papers):
        title_short = paper["title"][:45]
        log(f"  [{i+1}/{len(papers)}] {title_short}...")
        # 构造 Zotero item
        item = {
            "itemType": paper.get("itemType", "conferencePaper"),
            "title": paper["title"],
            "creators": paper.get("creators", []),
            "date": paper.get("date", ""),
            "url": paper.get("url", ""),
            "archive": paper.get("archive", ""),
            "abstractNote": paper.get("abstractNote", ""),
            "tags": paper.get("tags", []),
        }
        # 添加目录信息（用 key 而非名称）
        item_colls = []
        for cn in paper.get("collections", []):
            if cn in coll_map:
                item_colls.append(coll_map[cn])
        if item_colls:
            item["collections"] = item_colls
        key = create_item(item)
        if key:
            log(f"    ✓ 添加成功 (key={key})")
            item_key_map[paper["title"]] = key
            success += 1
        else:
            log(f"    ✗ 添加失败")
        time.sleep(0.4)
    
    # Step 4: 确认完成（已在 POST 时分配目录，无需 PATCH）
    log(f"\n[4/4] 确认完成！已在创建时分配到 {len(coll_map)} 个目录")
    log("请在 Zotero 中刷新查看（View → Refresh）")
    
    log("\n" + "=" * 60)
    log(f"完成！成功导入 {success}/{len(papers)} 篇论文到对应目录")
    log("=" * 60)
    log("=" * 60)


if __name__ == "__main__":
    main()

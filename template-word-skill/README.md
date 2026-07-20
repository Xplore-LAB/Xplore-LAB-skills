# template-word-skill

面向 Codex、Claude Code 等智能编码助手的中文 Word/DOCX 生成与编辑技能。支持模板填充、项目交付文档生成、Markdown 转 Word、保持格式编辑和学位论文排版。

## 核心能力

- 从 `.docx` 模板填充文本、表格和图片。
- 生成项目计划书、技术设计说明书、运维手册等 23 类交付文档。
- 从参考文档抽取格式档案，统一标题、正文、表格和页面边距。
- 执行保格式替换、内容插入、标题重排和目录刷新。
- 支持论文多级编号、题注、三线表、分节页码、摘要和 GB/T 7714 参考文献。

## 安装

将整个目录复制到 `~/.codex/skills/template-word-skill/`，并安装依赖：

```bash
pip install "python-docx>=0.8.11"
```

## 快速使用

```bash
python tools/create_doc.py --doc-type "技术设计说明书" --project-name "智能问数" --output 技术设计说明书.docx
python tools/edit_doc.py extract --ref 标杆.docx --profile 格式档案.json
python tools/edit_doc.py apply --input 待统一.docx --output 统一格式版.docx --profile 格式档案.json
python tools/thesis_doc.py new --spec 论文.json --output 论文.docx
```

完整参数和 JSON Schema 见 [SKILL.md](SKILL.md) 与 `prompts/`。

## 注意事项

- 默认生成新文件，不覆盖原文档。
- 目录、题注、编号和图表索引使用 Word 域代码，生成后请按 `Ctrl+A`、`F9` 更新。
- 复杂文档建议在交付前逐页检查。

## License

[MIT](LICENSE)

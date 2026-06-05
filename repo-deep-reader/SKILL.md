---
name: repo-deep-reader
description: |
  Deeply analyze a GitHub or local repository. Use when user asks to understand a
  project functionality, architecture, modules, APIs, entry points, data flow,
  interface contracts, or how to extend the project. Triggers include: read this
  repo, analyze this project, understand this codebase, 项目阅读, 仓库分析, 功能
  清单, 接口清单, 调用链, 二次开发. Do NOT use for simple README summarization.
  This skill is for comprehensive code-level analysis.
---

# Repo Deep Reader

## Goal

Analyze the current repository as if preparing a technical handover document for a new engineer joining the team.

**Core principle: Inspect actual code, not just README.** Read routing files, package manifests, configuration files, schemas, startup scripts, and test files. Output must cite exact file paths. Mark inferred information clearly.

---

## Workflow

Follow these phases in order. Do not skip phases 1-2 even if the project seems simple.

### Phase 1: Repository Inventory

First identify:

- Project name and purpose (from README + code)
- Primary language and framework
- Package manager and runtime version
- Project type: frontend / backend / fullstack / CLI / library / monorepo / microservice
- Main directories and their responsibilities
- Startup commands (`npm start`, `python main.py`, etc.)
- Build / test / lint commands
- Environment variables and config files (`.env.example`, `config/`, etc.)
- Database or external service dependencies

Key files to inspect:
```
README.md
package.json / pyproject.toml / requirements.txt / go.mod / Cargo.toml / pom.xml / build.gradle
docker-compose.yml / Dockerfile
.env.example / .env.template
src/ app/ server/ api/ routes/ controllers/ services/ models/ pages/ components/
tests/ e2e/ __tests__/ spec/
docs/ ARCHITECTURE.md / DESIGN.md
```

### Phase 2: Functional Analysis

Output a **feature map** — a table where each row is a distinct feature:

| Feature Name | What User Sees | Frontend Location | Backend Location | Data / Model | Key Config | Evidence |
|---|---|---|---|---|---|---|

For each feature, trace from user action to data layer. Do not list every file — only significant ones.

### Phase 3: API and Interface Analysis

Find ALL external and internal interfaces:

**Types to look for:**
- REST API routes (`router.get()`, `@app.route`, `api/`, `routes/`)
- RPC / gRPC endpoints
- GraphQL schemas and resolvers
- WebSocket events
- CLI commands (`#!/usr/bin/env`, `argparse`, `click`, `commander`)
- SDK / library exports (`export`, `module.exports`, `__all__`)
- Database access interfaces (ORM models, raw SQL, migration files)
- Third-party service integrations (webhooks, event buses, message queues)

For each interface, output:

| Property | Value |
|---|---|
| Method / Type | e.g. `GET`, `POST`, `WS`, `gRPC` |
| Path / Name | e.g. `/api/users/:id`, `cli deploy` |
| Request Params | Query, body, headers, path params |
| Response Structure | Shape of returned data |
| Auth / Permission | JWT, API key, role, none |
| Handler File | e.g. `src/handlers/user.go` |
| Downstream | Service or DB called by handler |
| Errors | How errors are returned |
| Evidence | **Exact** file:line reference |

If something is inferred rather than explicitly declared in code, mark it as `[推断]` (inferred). If not found in the repository, mark as `[未在仓库中找到]`.

### Phase 4: Call-Chain Analysis

For each major feature or API, trace the full flow:

```
User action / external request
  → route / page / entry file
    → controller / handler
      → service / use-case
        → data access / model
          → external service / database
  → response / output
```

Prefer concise text diagrams. If multiple features share a common path, show the shared trunk once.

### Phase 5: Architecture Summary

Explain in plain language:
- Overall architecture pattern (layered, MVC, microservices, serverless, etc.)
- Frontend/backend separation and how they communicate
- State management approach
- Data persistence design (which DB, ORM or raw, migrations)
- Authentication and authorization flow
- Configuration loading (env vars, config files, precedence)
- Error handling pattern (exceptions, error codes, middleware)
- Logging and observability (log library, metrics, tracing)
- Test coverage status (unit vs integration vs e2e)

### Phase 6: Extension Guidance

For a new developer who wants to add a feature, specify:
- Where to add frontend pages/components
- Where to add backend routes/controllers/services
- Where to add schema/model/migration
- Where to add tests
- Common pitfalls to avoid
- Files that should not be changed casually

### Phase 7: Risk Points

List:
- Areas where code is complex, underdocumented, or fragile
- Missing tests (low coverage areas)
- Third-party dependencies with known issues
- Security concerns (hardcoded secrets, missing auth, etc.)
- Items marked `[未在仓库中找到]` that would need investigation before production use

---

## Output Format

Always produce the final report in this exact structure:

```markdown
# [项目名] 项目阅读报告

## 1. 项目一句话说明

## 2. 技术栈与运行方式

## 3. 目录结构与模块职责

## 4. 核心功能清单

| 功能 | 用户看到什么 | 前端位置 | 后端位置 | 数据/模型 | 证据文件 |
|---|---|---|---|---|---|

## 5. 接口清单

| 接口 | 方法 | 入参 | 出参 | 权限 | 处理函数 | 下游调用 | 证据文件 |
|---|---|---|---|---|---|---|---|

## 6. 核心调用链

（文本流程图）

## 7. 数据模型与配置

## 8. 权限、异常与日志

## 9. 如何二次开发

## 10. 风险点与不确定项

## 11. 建议下一步阅读顺序
```

---

## Important Rules

1. **Cite exact file paths** in every table and claim. Format: `src/api/users.go:42`
2. **Mark inferred info** with `[推断]` — do not present as confirmed fact
3. **Mark missing info** with `[未在仓库中找到]` — do not hallucinate
4. **Inspect code, not README** — README is a starting hint, not the source of truth
5. **Prioritize routing/entry files** — for large repos, start with `index.js`, `main.go`, `app.py`, `App.vue`, `pages/`, `routes/`
6. **For monorepos**, identify each package/module separately
7. **If the repo is too large** (> 200 files at top level), analyze in passes: inventory → APIs → call chains. Report progress at each pass.
8. **Always show evidence** — every claim must link to a specific file and line number
9. **Be honest about uncertainty** — if you are not sure, say so instead of guessing

---

## Usage

After this skill is loaded, simply ask:

> "请阅读当前仓库，输出完整的项目阅读报告"

Or target specific aspects:

> "请重点分析这个项目的 API 接口和调用链"

> "我想二次开发，请告诉我应该从哪些文件开始"

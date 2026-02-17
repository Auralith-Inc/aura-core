---
metadata.clawdbot:
  name: aura-openclaw
  description: Compile documents into knowledge bases and manage persistent AI agent memory with Aura Core
  version: 0.1.0
  author: Auralith Inc.
  homepage: https://github.com/Auralith-Inc/aura-openclaw
requires:
  env: []
files: ["scripts/*"]
---

# Aura Memory Compiler

Compile any folder of documents (PDFs, DOCX, code, spreadsheets, markdown — 60+ formats) into an instant, queryable knowledge base and manage persistent AI agent memory using [Aura Core](https://github.com/Auralith-Inc/aura-core).

## Setup

```bash
pip install auralith-aura
```

For full document support (PDFs, DOCX, etc.):
```bash
pip install 'aura-core[all]'
```

## Commands

### Compile a Knowledge Base

When the user asks you to "learn", "compile", "index", or "remember" files from a directory:

```bash
python {SKILL_DIR}/scripts/compile.py <input_directory> <output_file>
```

Example:
```bash
python {SKILL_DIR}/scripts/compile.py ./my_documents knowledge.aura
```

Options:
```bash
# Mask PII before compilation
python {SKILL_DIR}/scripts/compile.py ./data knowledge.aura --pii-mask

# Filter low-quality content
python {SKILL_DIR}/scripts/compile.py ./data knowledge.aura --min-quality 0.3
```

### Query the Knowledge Base

Search compiled knowledge:
```bash
python {SKILL_DIR}/scripts/query.py knowledge.aura "what does the contract say about termination"
```

### Agent Memory

Write to agent memory tiers:
```bash
# Working notes (transient)
python {SKILL_DIR}/scripts/memory.py write pad "User prefers dark mode"

# Verified facts (persistent)
python {SKILL_DIR}/scripts/memory.py write fact "API key rotates monthly"

# Session logs
python {SKILL_DIR}/scripts/memory.py write episodic "Discussed deployment strategy"
```

Search memory:
```bash
python {SKILL_DIR}/scripts/memory.py query "user preferences"
```

Manage memory:
```bash
python {SKILL_DIR}/scripts/memory.py list
python {SKILL_DIR}/scripts/memory.py usage
python {SKILL_DIR}/scripts/memory.py prune --before 2026-01-01
python {SKILL_DIR}/scripts/memory.py end-session
```

### Archive Info

```bash
aura info <aura_file>
```

## Memory Tiers

| Tier | Path | Purpose | Lifecycle |
|------|------|---------|---------  |
| `/pad` | Working notepad | Scratch space, thinking | Transient, auto-cleared |
| `/episodic` | Session logs | Conversation history | Auto-archived at session end |
| `/fact` | Verified facts | User preferences, knowledge | Persistent, immutable |

## Supported File Types

Documents: PDF, DOCX, DOC, RTF, ODT, EPUB, TXT, HTML, PPTX, EML
Data: CSV, TSV, XLSX, XLS, Parquet, JSON, JSONL, YAML, TOML
Code: Python, JavaScript, TypeScript, Rust, Go, Java, C/C++, and 20+ more
Markup: Markdown (.md), reStructuredText, LaTeX

## External Endpoints

| URL | Data Sent |
|-----|-----------|
| None | None |

This skill makes **zero network requests**. All processing is local.

## Security & Privacy

- **No data leaves your machine.** All compilation and memory operations run locally.
- The `.aura` format uses `safetensors` (no pickle) — no arbitrary code execution risk.
- Memory files are stored in your local OpenClaw data directory.
- No environment variables or API keys are required.
- No telemetry, analytics, or usage reporting.

## Model Invocation Note

This skill is autonomously invoked by the agent as part of its normal operation. The agent decides when to compile documents and manage memory based on user requests. You can disable autonomous invocation in your OpenClaw settings.

## Trust Statement

By using this skill, **no data is sent to any external service**. All processing happens on your local machine. Only install this skill if you trust [Auralith Inc.](https://auralith.org) and have reviewed the source code at [GitHub](https://github.com/Auralith-Inc/aura-openclaw).

## Notes

- Memory uses a Two-Speed WAL: instant writes, background compilation.
- For emphasis weighting and training features, see [OMNI Platform](https://omni.auralith.org).

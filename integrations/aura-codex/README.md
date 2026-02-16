# 🔥 Aura for OpenAI Codex

**Give your Codex agent a persistent knowledge base and memory compiled from any documents.**

<p align="center">
  <a href="https://pypi.org/project/auralith-aura/"><img src="https://badge.fury.io/py/auralith-aura.svg" alt="PyPI"></a>
  <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License: Apache 2.0"></a>
</p>

## What This Does

This skill gives your Codex agent the ability to:

1. **Compile** any folder of documents (PDFs, DOCX, code, spreadsheets, markdown — 60+ formats) into a `.aura` knowledge base
2. **Query** that knowledge base instantly with natural language
3. **Remember** facts and context across sessions with the Memory OS

All processing happens **locally on your machine**. No data leaves your device.

## Setup

### 1. Install Aura Core

```bash
pip install auralith-aura
```

### 2. Add the Skill

Copy this repo's contents into your Codex skills directory, or reference it directly in your Codex configuration.

## Usage

### Compile a Knowledge Base

```
You: Compile all documentation in ./docs into a knowledge base
Codex: Running: aura compile ./docs --output knowledge.aura
       ✅ 156 documents compiled into knowledge.aura (12.4 MB)
```

### Query Documents

```
You: Search the knowledge base for how the payment system works
Codex: Found 3 relevant documents:
       📄 payment_flow.md (relevance: 8)
       📄 stripe_integration.py (relevance: 5)
       📄 api_reference.md (relevance: 3)
```

### Use Context for Coding

```
You: Using the knowledge base, write the refund endpoint
Codex: Based on payment_flow.md and stripe_integration.py:
       [generates code with correct patterns from your codebase]
```

## How It Works

```python
# The skill uses Aura's Python API
from aura.rag import AuraRAGLoader

loader = AuraRAGLoader("knowledge.aura")

# Get text from any document
text = loader.get_text_by_id("payment_flow")

# Search across all documents
for doc_id, text, meta in loader.iterate_texts():
    if "payment" in text.lower():
        print(f"Found: {meta['source']}")

# Framework wrappers
langchain_docs = loader.to_langchain_documents()
llama_docs = loader.to_llama_index_documents()
```

## System Requirements

| Files | RAM | Time |
|-------|-----|------|
| 50–500 | ~2 GB | < 1 min |
| 500–5,000 | ~4 GB | 5–15 min |

**Platforms**: macOS, Windows, Linux

## Links

- [Aura Core](https://github.com/Auralith-Inc/aura-core) — The compiler
- [Website](https://aura.auralith.org) — Documentation
- [PyPI](https://pypi.org/project/auralith-aura/) — Install

---

Made by [Auralith Inc.](https://auralith.org)

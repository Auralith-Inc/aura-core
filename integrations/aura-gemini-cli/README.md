# 🔥 Aura for Gemini CLI

**Give your Gemini CLI agent a persistent knowledge base and memory compiled from any documents.**

<p align="center">
  <a href="https://pypi.org/project/aura-core/"><img src="https://badge.fury.io/py/aura-core.svg" alt="PyPI"></a>
  <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License: Apache 2.0"></a>
</p>

## What This Does

This extension gives your Gemini CLI agent the ability to:

1. **Compile** any folder of documents (PDFs, DOCX, code, spreadsheets, markdown — 60+ formats) into a `.aura` knowledge base
2. **Query** that knowledge base instantly with natural language
3. **Remember** context across sessions with the Memory OS

All processing happens **locally on your machine**. No data leaves your device.

## Setup

### 1. Install Aura Core

```bash
pip install aura-core
```

### 2. Configure Gemini CLI

Add the Aura MCP server to your Gemini CLI settings at `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "aura": {
      "command": "python",
      "args": ["-m", "aura.mcp_server"],
      "env": {}
    }
  }
}
```

Or use custom slash commands by copying the `commands/` directory:

```bash
cp -r commands/* ~/.gemini/commands/
```

### 3. Add Custom Slash Commands

Copy the `.toml` files from this repo's `commands/` directory into `~/.gemini/commands/`:

- `/aura-compile` — Compile documents into a knowledge base
- `/aura-query` — Search a knowledge base
- `/aura-info` — Inspect an archive

## Usage

### Compile a Knowledge Base

```
You: /aura-compile ./docs
Gemini: 🔥 Compiling ./docs → knowledge.aura
        ✅ 234 documents compiled (12.4 MB)
```

### Query Documents

```
You: /aura-query knowledge.aura "how does authentication work"
Gemini: Found 3 relevant documents:
        📄 auth_module.py (relevance: 8)
        📄 architecture.md (relevance: 5)
```

### Use Context for Coding

```
You: Using the knowledge base, explain the payment flow
Gemini: Based on payment_flow.md and stripe_integration.py:
        The system processes payments through...
```

## How It Works

```python
# Aura compiles documents into a single .aura archive
aura compile ./docs --output knowledge.aura

# The agent loads it with Python
from aura.rag import AuraRAGLoader
loader = AuraRAGLoader("knowledge.aura")

# Retrieve any document instantly
text = loader.get_text_by_id("auth_module")

# Or convert to LangChain/LlamaIndex
docs = loader.to_langchain_documents()
```

## System Requirements

| Files | RAM | Time |
|-------|-----|------|
| 50–500 | ~2 GB | < 1 min |
| 500–5,000 | ~4 GB | 5–15 min |

**Platforms**: macOS, Windows, Linux

## Links

- [Aura Core](https://github.com/AuralithInc/aura-core) — The compiler
- [Website](https://aura.auralith.org) — Documentation
- [PyPI](https://pypi.org/project/aura-core/) — Install

---

Made by [Auralith Inc.](https://auralith.org)

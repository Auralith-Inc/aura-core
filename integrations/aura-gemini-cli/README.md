# 🔥 Aura for Gemini CLI

**Give your Gemini CLI agent a persistent knowledge base and 3-tier memory compiled from any documents.**

<p align="center">
  <a href="https://pypi.org/project/auralith-aura/"><img src="https://badge.fury.io/py/auralith-aura.svg" alt="PyPI"></a>
  <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License: Apache 2.0"></a>
</p>

## What This Does

This extension gives your Gemini CLI agent the ability to:

1. **Compile** any folder of documents (PDFs, DOCX, code, spreadsheets, markdown — 60+ formats) into a `.aura` knowledge base
2. **Query** that knowledge base instantly with natural language
3. **Remember** context across sessions with the 3-tier Memory OS (pad, episodic, fact)

All processing happens **locally on your machine**. No data leaves your device. No GPU required.

## Setup

### 1. Install Aura Core

```bash
pip install auralith-aura
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
        ✅ Knowledge base compiled — documents indexed
```

### Query Documents

```
You: /aura-query knowledge.aura "how does authentication work"
Gemini: Found relevant documents:
        📄 auth_module.py
        📄 architecture.md
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

## Runs Locally

- **No GPU required** — runs on any modern laptop or desktop (CPU-only)
- **Fully offline** — zero internet required after install
- **Cross-platform** — macOS, Windows, Linux, Python 3.8+

Your documents never leave your hardware.

## Scale Up with OMNI

Need enterprise-scale training pipelines, model fine-tuning, or production agent infrastructure? Check out [**OMNI**](https://omni.auralith.org).

## Links

- [Aura Core](https://github.com/Auralith-Inc/aura-core) — The compiler
- [Website](https://aura.auralith.org) — Documentation
- [OMNI Platform](https://omni.auralith.org) — Enterprise scale
- [PyPI](https://pypi.org/project/auralith-aura/) — Install

---

Made by [Auralith Inc.](https://auralith.org)

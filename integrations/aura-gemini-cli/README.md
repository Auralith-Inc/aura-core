<p align="center">
  <img src="https://raw.githubusercontent.com/Auralith-Inc/aura-core/main/logo.png" alt="Aura" width="100">
</p>

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

All processing happens **locally on your machine**. No data leaves your device.

## Setup

### 1. Install Aura Core

```bash
pip install auralith-aura
```

### 2. Configure the MCP Server

Add Aura as an MCP server in your Gemini CLI settings (`~/.gemini/settings.json`):

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

This exposes the following tools to your Gemini CLI agent automatically:

| Tool | Description |
|------|-------------|
| `aura_compile` | Compile a directory into a `.aura` knowledge base |
| `aura_query` | Search a knowledge base for relevant documents |
| `aura_memory_write` | Write to persistent memory (pad / episodic / fact) |
| `aura_memory_query` | Search persistent memory |
| `aura_memory_list` | List all stored memory entries |
| `aura_info` | Inspect an `.aura` archive (doc count, file types, size) |

## Usage

Once configured, your Gemini CLI agent can use Aura tools naturally through conversation:

### Compile a Knowledge Base

```
You: Compile all the docs in ./docs into a knowledge base
Gemini: [uses aura_compile] ✅ Compiled ./docs → knowledge.aura (47 documents indexed)
```

### Query Documents

```
You: Search the knowledge base for how authentication works
Gemini: [uses aura_query] Found relevant documents:
        📄 auth_module.py (relevance: 4)
        📄 architecture.md (relevance: 3)
```

### Persistent Memory

```
You: Remember that our staging API is at api-staging.example.com
Gemini: [uses aura_memory_write] ✅ Written to fact tier

--- next session ---

You: What's our staging API URL?
Gemini: [uses aura_memory_query] Based on stored memory: api-staging.example.com
```

## How It Works

The Aura MCP server implements the [Model Context Protocol](https://modelcontextprotocol.io/) over stdio, exposing Aura Core's capabilities as standard MCP tools. Gemini CLI discovers and calls these tools automatically.

```python
# Under the hood, the MCP server uses Aura's Python API:
from aura.rag import AuraRAGLoader

loader = AuraRAGLoader("knowledge.aura")
text = loader.get_text_by_id("auth_module")
docs = loader.to_langchain_documents()
```

## Runs Locally

- **Runs on your local hardware** — any modern laptop or desktop, your setup, your choice
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

<p align="center">
  <img src="https://raw.githubusercontent.com/Auralith-Inc/aura-core/main/logo.png" alt="Aura" width="100">
</p>

# Aura Core — Claude Code Integration

This project uses [Aura Core](https://github.com/Auralith-Inc/aura-core) for document compilation, RAG retrieval, and agent memory.

## What is Aura?

Aura compiles any documents (PDFs, DOCX, code, spreadsheets, markdown — 60+ formats) into a single `.aura` knowledge archive that can be queried instantly. It also provides a 3-tier memory system (pad, episodic, fact) for persistent agent context across sessions.

## Available Commands

### `/aura-compile` — Compile documents into a knowledge base

Usage: `/aura-compile <directory> [output_file]`

This compiles all files in the given directory into an `.aura` archive for instant retrieval.

### `/aura-query` — Search a knowledge base

Usage: `/aura-query <aura_file> <question>`

This searches through a compiled `.aura` archive and returns the most relevant passages.

### `/aura-memory` — Manage agent memory

Usage: `/aura-memory <action> [args]`

Actions: `write`, `list`, `usage`, `query`

**Memory tiers:**
- **`/pad`** — Working notes, scratch space (transient)
- **`/episodic`** — Session transcripts, conversation history (auto-archived)
- **`/fact`** — Verified facts, user preferences (persistent)

## Quick Setup

1. Install Aura Core: `pip install auralith-aura`
2. Copy the `.claude/commands/` directory into your project
3. Use `/aura-compile ./docs` to build a knowledge base
4. Use `/aura-query knowledge.aura "your question"` to search

## How It Works

```
You: /aura-compile ./docs
Claude: 🔥 Compiling ./docs → knowledge.aura
        ✅ Knowledge base created — documents indexed

You: /aura-query knowledge.aura "how does authentication work?"
Claude: Based on auth_module.py and architecture.md:
        The authentication system uses JWT tokens...
```

## Security & Privacy

- All processing happens **locally**. No data leaves your machine.
- Uses `safetensors` (no pickle) — safe and secure.
- Runs on your local hardware. Fully offline after install.
- Compiler and RAG: Apache-2.0. Memory OS: proprietary, free to use.

## Scale Up with OMNI

Need enterprise-scale training pipelines or production agent infrastructure? Check out [**OMNI**](https://omni.auralith.org).

## Links

- [Aura Core](https://github.com/Auralith-Inc/aura-core)
- [Website](https://aura.auralith.org)
- [OMNI Platform](https://omni.auralith.org)
- [PyPI](https://pypi.org/project/auralith-aura/)

Made by [Auralith Inc.](https://auralith.org)

# 🔥 Aura for OpenClaw

**Compile any documents into an instant, queryable knowledge base with 3-tier agent memory for your OpenClaw agent.**

<p align="center">
  <a href="https://pypi.org/project/auralith-aura/"><img src="https://badge.fury.io/py/auralith-aura.svg" alt="PyPI"></a>
  <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License: Apache 2.0"></a>
</p>

## What This Does

This skill gives your OpenClaw agent the ability to:

1. **Compile** any folder of documents (PDFs, DOCX, code, spreadsheets, emails — 60+ formats) into a `.aura` knowledge base
2. **Query** that knowledge base instantly with natural language
3. **Remember** facts, preferences, and session context across conversations using a 3-tier memory system

All processing happens **locally on your machine**. No data leaves your device. No GPU required.

## Installation

### 1. Install Aura Core

```bash
pip install auralith-aura
```

### 2. Install the Skill

In OpenClaw, install this skill from ClawHub or add it manually:

```
/install aura-knowledge-compiler
```

Or clone this repo into your OpenClaw skills directory.

## Usage

### "Learn my documents"

```
You: Learn everything in my ~/legal/ folder
Agent: 🔥 Compiling ~/legal/ → legal.aura
       ✅ Knowledge base created — documents indexed
```

### "Ask about my documents"

```
You: What does clause 4.2 say about termination?
Agent: Based on contract_v3.pdf, clause 4.2 states...
```

### "Remember this"

```
You: Remember that I prefer dark mode and my timezone is EST
Agent: ✅ Written to /fact: "User prefers dark mode, timezone EST"
```

### Memory Management

```
You: What do you remember about me?
Agent: Searching memory... Found 3 results:
       [fact] User prefers dark mode, timezone EST
       [episodic] Discussed deployment strategy on 2026-02-15
       [pad] TODO: review auth module changes
```

## 3-Tier Memory OS

Aura's memory system gives your agent persistent context across sessions:

| Tier | Purpose | Lifecycle |
|------|---------|-----------|
| **`/pad`** | Working notes, scratch space, in-progress tasks | Transient — cleared between sessions |
| **`/episodic`** | Session transcripts, conversation history | Auto-archived — retained for reference |
| **`/fact`** | Verified facts, user preferences, decisions | Persistent — survives indefinitely |

**How it works:**

- **Instant writes** (~0.001s) — agents are never blocked. Memories are appended to a write-ahead log immediately.
- **Background compilation** — at session end, the WAL is compiled into durable `.aura` shards for fast retrieval.
- **Queryable** — search across all tiers with natural language. The agent decides which tier to write to based on context.

```python
from aura.memory import AuraMemoryOS

memory = AuraMemoryOS()

# Write to different tiers
memory.write("fact", "User prefers dark mode", source="agent")
memory.write("episodic", "Discussed deployment strategy")
memory.write("pad", "TODO: check auth module")

# Search across all memory
results = memory.query("user preferences")

# End session (compiles WAL to durable shards)
memory.end_session()
```

## Runs Locally

- **No GPU required** — runs on any modern laptop or desktop (CPU-only)
- **Fully offline** — zero internet required after install
- **Cross-platform** — macOS, Windows, Linux, Python 3.8+

Your documents and memory never leave your hardware.

## Scale Up with OMNI

Need enterprise-scale training pipelines, model fine-tuning, or production agent infrastructure? Check out [**OMNI**](https://omni.auralith.org).

## Links

- [Aura Core](https://github.com/Auralith-Inc/aura-core) — The compiler
- [Website](https://aura.auralith.org) — Documentation
- [OMNI Platform](https://omni.auralith.org) — Enterprise scale
- [PyPI](https://pypi.org/project/auralith-aura/) — Install

---

Made by [Auralith Inc.](https://auralith.org)

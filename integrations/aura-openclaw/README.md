# 🔥 Aura for OpenClaw

**Compile any documents into an instant, queryable knowledge base with agent memory for your OpenClaw agent.**

<p align="center">
  <a href="https://pypi.org/project/auralith-aura/"><img src="https://badge.fury.io/py/auralith-aura.svg" alt="PyPI"></a>
  <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License: Apache 2.0"></a>
</p>

## What This Does

This skill gives your OpenClaw agent the ability to:

1. **Compile** any folder of documents (PDFs, DOCX, code, spreadsheets, emails — 60+ formats) into a `.aura` knowledge base
2. **Query** that knowledge base instantly with natural language
3. **Remember** facts, preferences, and session context across conversations

All processing happens **locally on your machine**. No data leaves your device.

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
       ✅ Knowledge base created: 234 documents indexed
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

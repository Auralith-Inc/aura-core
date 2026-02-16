#!/usr/bin/env python3
"""
Aura Gemini CLI Helper Script
Provides compile, query, info, and memory commands for Gemini CLI agents.
"""
import sys
import subprocess


def cmd_compile(args):
    """Compile a directory into an .aura knowledge base."""
    if len(args) < 1:
        print("Usage: aura_gemini.py compile <input_directory> [output_file]")
        sys.exit(1)

    input_dir = args[0]
    output_file = args[1] if len(args) > 1 else "knowledge.aura"
    extra_args = args[2:]

    cmd = ["aura", "compile", input_dir, "--output", output_file] + extra_args
    print(f"🔥 Compiling {input_dir} → {output_file}")
    result = subprocess.run(cmd, capture_output=False)

    if result.returncode == 0:
        print(f"✅ Knowledge base created: {output_file}")
    else:
        print(f"❌ Compilation failed with exit code {result.returncode}")
        sys.exit(result.returncode)


def cmd_query(args):
    """Search through an .aura knowledge base."""
    if len(args) < 2:
        print("Usage: aura_gemini.py query <aura_file> <search_query>")
        sys.exit(1)

    aura_file = args[0]
    query = " ".join(args[1:])

    try:
        from aura.rag import AuraRAGLoader
    except ImportError:
        print("❌ aura-core not installed. Run: pip install auralith-aura")
        sys.exit(1)

    loader = AuraRAGLoader(aura_file)
    print(f"🔍 Searching '{aura_file}' for: {query}")
    print(f"📦 Archive contains {len(loader)} documents")
    print("-" * 60)

    query_lower = query.lower()
    results = []

    for doc_id, text, meta in loader.iterate_texts():
        if not text:
            continue
        score = sum(1 for word in query_lower.split() if word in text.lower())
        if score > 0:
            results.append((score, doc_id, text, meta))

    results.sort(key=lambda x: x[0], reverse=True)

    if not results:
        print("No matching documents found.")
    else:
        for i, (score, doc_id, text, meta) in enumerate(results[:5], 1):
            source = meta.get("source", doc_id)
            preview = text[:300].replace("\n", " ").strip()
            print(f"\n📄 [{i}] {source} (relevance: {score})")
            print(f"   {preview}...")
        print(f"\n✅ Found {len(results)} matching documents (showing top 5)")

    loader.close()


def cmd_info(args):
    """Show information about an .aura archive."""
    if len(args) < 1:
        print("Usage: aura_gemini.py info <aura_file>")
        sys.exit(1)

    cmd = ["aura", "info", args[0]]
    subprocess.run(cmd, capture_output=False)


def cmd_memory(args):
    """Manage agent memory."""
    cmd = ["python", "-m", "aura.memory"] + args
    subprocess.run(cmd, capture_output=False)


def main():
    if len(sys.argv) < 2:
        print("Aura Gemini CLI Helper")
        print("Commands: compile, query, info, memory")
        print("Usage: aura_gemini.py <command> [args...]")
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "compile": cmd_compile,
        "query": cmd_query,
        "info": cmd_info,
        "memory": cmd_memory,
    }

    if command not in commands:
        print(f"Unknown command: {command}")
        print(f"Available commands: {', '.join(commands.keys())}")
        sys.exit(1)

    commands[command](args)


if __name__ == "__main__":
    main()

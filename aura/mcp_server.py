"""
Aura MCP Server — Model Context Protocol interface for Aura Core.

Run with:
    python -m aura.mcp_server

Exposes Aura's context compilation, RAG retrieval, and memory system
as MCP tools that any MCP-compatible client (Gemini CLI, Claude Code,
etc.) can use directly.

Protocol: JSON-RPC 2.0 over stdio (MCP standard transport)
"""

import json
import sys
import os
import subprocess
from pathlib import Path

# MCP Protocol version
PROTOCOL_VERSION = "2024-11-05"

# Server info
SERVER_INFO = {
    "name": "aura",
    "version": "0.1.0"
}

# Tool definitions
TOOLS = [
    {
        "name": "aura_compile",
        "description": "Compile a directory of documents (PDFs, DOCX, code, spreadsheets, markdown — 60+ formats) into a single .aura knowledge base archive. All processing is local.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "input_directory": {
                    "type": "string",
                    "description": "Path to the directory containing documents to compile"
                },
                "output_file": {
                    "type": "string",
                    "description": "Path for the output .aura file (default: knowledge.aura)"
                },
                "pii_mask": {
                    "type": "boolean",
                    "description": "Whether to mask PII (emails, phone numbers, SSNs) during compilation (default: false)"
                }
            },
            "required": ["input_directory"]
        }
    },
    {
        "name": "aura_query",
        "description": "Search through a compiled .aura knowledge base and return the most relevant document passages for a given query.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "aura_file": {
                    "type": "string",
                    "description": "Path to the .aura knowledge base file"
                },
                "query": {
                    "type": "string",
                    "description": "The search query to find relevant documents"
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of results to return (default: 5)"
                }
            },
            "required": ["aura_file", "query"]
        }
    },
    {
        "name": "aura_memory_write",
        "description": "Write an entry to Aura's 3-tier persistent memory system. Tiers: 'pad' (working notes, scratch space), 'episodic' (session logs, conversation history), 'fact' (verified facts, user preferences).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tier": {
                    "type": "string",
                    "enum": ["pad", "episodic", "fact"],
                    "description": "Memory tier to write to"
                },
                "content": {
                    "type": "string",
                    "description": "The content to store in memory"
                }
            },
            "required": ["tier", "content"]
        }
    },
    {
        "name": "aura_memory_query",
        "description": "Search Aura's persistent memory for entries matching a query. Returns results from all three tiers (pad, episodic, fact).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to find relevant memory entries"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "aura_memory_list",
        "description": "List all entries in Aura's persistent memory, organized by tier.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tier": {
                    "type": "string",
                    "enum": ["pad", "episodic", "fact"],
                    "description": "Optional: filter to a specific tier. If omitted, lists all tiers."
                }
            }
        }
    },
    {
        "name": "aura_info",
        "description": "Show metadata and statistics about a compiled .aura archive (document count, file types, size, compilation date).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "aura_file": {
                    "type": "string",
                    "description": "Path to the .aura file to inspect"
                }
            },
            "required": ["aura_file"]
        }
    }
]


def handle_compile(args):
    """Compile a directory into an .aura archive."""
    input_dir = args["input_directory"]
    output_file = args.get("output_file", "knowledge.aura")
    pii_mask = args.get("pii_mask", False)

    if not os.path.isdir(input_dir):
        return {"isError": True, "content": [{"type": "text", "text": f"Error: Directory not found: {input_dir}"}]}

    cmd = ["aura", "compile", input_dir, "--output", output_file]
    if pii_mask:
        cmd.append("--pii-mask")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        output = result.stdout + result.stderr
        if result.returncode == 0:
            return {"content": [{"type": "text", "text": f"✅ Compiled {input_dir} → {output_file}\n{output.strip()}"}]}
        else:
            return {"isError": True, "content": [{"type": "text", "text": f"Compilation failed:\n{output.strip()}"}]}
    except FileNotFoundError:
        return {"isError": True, "content": [{"type": "text", "text": "Error: aura CLI not found. Install with: pip install auralith-aura"}]}
    except subprocess.TimeoutExpired:
        return {"isError": True, "content": [{"type": "text", "text": "Error: Compilation timed out (5 min limit)"}]}


def handle_query(args):
    """Query an .aura archive."""
    aura_file = args["aura_file"]
    query = args["query"]
    top_k = args.get("top_k", 5)

    if not os.path.isfile(aura_file):
        return {"isError": True, "content": [{"type": "text", "text": f"Error: File not found: {aura_file}"}]}

    try:
        from aura.rag import AuraRAGLoader

        loader = AuraRAGLoader(aura_file)
        query_lower = query.lower()
        results = []

        for doc_id, text, meta in loader.iterate_texts():
            if not text:
                continue
            score = sum(1 for word in query_lower.split() if word in text.lower())
            if score > 0:
                results.append((score, doc_id, text, meta))

        results.sort(key=lambda x: x[0], reverse=True)
        loader.close()

        if not results:
            return {"content": [{"type": "text", "text": f"No results found for: {query}"}]}

        output_lines = []
        for score, doc_id, text, meta in results[:top_k]:
            source = meta.get("source", doc_id)
            preview = text[:400].replace("\n", " ")
            output_lines.append(f"📄 {source} (relevance: {score})\n   {preview}...")

        return {"content": [{"type": "text", "text": "\n\n".join(output_lines)}]}

    except ImportError:
        return {"isError": True, "content": [{"type": "text", "text": "Error: aura-core not installed. Run: pip install auralith-aura"}]}
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": f"Error querying archive: {str(e)}"}]}


def handle_memory_write(args):
    """Write to agent memory."""
    tier = args["tier"]
    content = args["content"]

    try:
        from aura.memory import AuraMemoryOS

        memory = AuraMemoryOS()
        memory.write(tier, content)
        return {"content": [{"type": "text", "text": f"✅ Written to {tier} tier: {content[:100]}{'...' if len(content) > 100 else ''}"}]}
    except ImportError:
        return {"isError": True, "content": [{"type": "text", "text": "Error: aura-core not installed. Run: pip install auralith-aura"}]}
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": f"Error writing memory: {str(e)}"}]}


def handle_memory_query(args):
    """Query agent memory."""
    query = args["query"]

    try:
        from aura.memory import AuraMemoryOS

        memory = AuraMemoryOS()
        results = memory.query(query)

        if not results:
            return {"content": [{"type": "text", "text": f"No memory entries found for: {query}"}]}

        output_lines = []
        for entry in results:
            output_lines.append(f"[{entry['tier']}] {entry['content']}")

        return {"content": [{"type": "text", "text": "\n".join(output_lines)}]}
    except ImportError:
        return {"isError": True, "content": [{"type": "text", "text": "Error: aura-core not installed. Run: pip install auralith-aura"}]}
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": f"Error querying memory: {str(e)}"}]}


def handle_memory_list(args):
    """List memory entries."""
    tier_filter = args.get("tier")

    try:
        from aura.memory import AuraMemoryOS

        memory = AuraMemoryOS()
        entries = memory.list_entries()

        if tier_filter:
            entries = [e for e in entries if e.get("tier") == tier_filter]

        if not entries:
            return {"content": [{"type": "text", "text": "No memory entries found."}]}

        output_lines = []
        for entry in entries:
            output_lines.append(f"[{entry['tier']}] {entry['content'][:200]}")

        return {"content": [{"type": "text", "text": "\n".join(output_lines)}]}
    except ImportError:
        return {"isError": True, "content": [{"type": "text", "text": "Error: aura-core not installed. Run: pip install auralith-aura"}]}
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": f"Error listing memory: {str(e)}"}]}


def handle_info(args):
    """Show info about an .aura archive."""
    aura_file = args["aura_file"]

    if not os.path.isfile(aura_file):
        return {"isError": True, "content": [{"type": "text", "text": f"Error: File not found: {aura_file}"}]}

    try:
        from aura.rag import AuraRAGLoader

        loader = AuraRAGLoader(aura_file)
        doc_count = len(loader.reader)
        file_size = os.path.getsize(aura_file)

        sources = set()
        for doc_id, text, meta in loader.iterate_texts():
            source = meta.get("source", "")
            if source:
                ext = Path(source).suffix.lower()
                if ext:
                    sources.add(ext)

        loader.close()

        size_str = f"{file_size / 1024:.1f} KB" if file_size < 1024 * 1024 else f"{file_size / (1024 * 1024):.1f} MB"
        ext_list = ", ".join(sorted(sources)) if sources else "N/A"

        info = (
            f"📦 {aura_file}\n"
            f"   Documents: {doc_count}\n"
            f"   File size: {size_str}\n"
            f"   File types: {ext_list}"
        )

        return {"content": [{"type": "text", "text": info}]}
    except ImportError:
        return {"isError": True, "content": [{"type": "text", "text": "Error: aura-core not installed. Run: pip install auralith-aura"}]}
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": f"Error reading archive: {str(e)}"}]}


# Tool dispatch
TOOL_HANDLERS = {
    "aura_compile": handle_compile,
    "aura_query": handle_query,
    "aura_memory_write": handle_memory_write,
    "aura_memory_query": handle_memory_query,
    "aura_memory_list": handle_memory_list,
    "aura_info": handle_info,
}


def send_response(response_id, result):
    """Send a JSON-RPC response to stdout."""
    response = {
        "jsonrpc": "2.0",
        "id": response_id,
        "result": result
    }
    msg = json.dumps(response)
    sys.stdout.write(f"Content-Length: {len(msg)}\r\n\r\n{msg}")
    sys.stdout.flush()


def send_error(response_id, code, message):
    """Send a JSON-RPC error response."""
    response = {
        "jsonrpc": "2.0",
        "id": response_id,
        "error": {"code": code, "message": message}
    }
    msg = json.dumps(response)
    sys.stdout.write(f"Content-Length: {len(msg)}\r\n\r\n{msg}")
    sys.stdout.flush()


def handle_request(request):
    """Process an incoming MCP request."""
    method = request.get("method", "")
    request_id = request.get("id")
    params = request.get("params", {})

    if method == "initialize":
        send_response(request_id, {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {
                "tools": {}
            },
            "serverInfo": SERVER_INFO
        })

    elif method == "notifications/initialized":
        # Client acknowledgment — no response needed
        pass

    elif method == "tools/list":
        send_response(request_id, {"tools": TOOLS})

    elif method == "tools/call":
        tool_name = params.get("name", "")
        tool_args = params.get("arguments", {})

        handler = TOOL_HANDLERS.get(tool_name)
        if handler:
            try:
                result = handler(tool_args)
                send_response(request_id, result)
            except Exception as e:
                send_response(request_id, {
                    "isError": True,
                    "content": [{"type": "text", "text": f"Internal error: {str(e)}"}]
                })
        else:
            send_error(request_id, -32601, f"Unknown tool: {tool_name}")

    elif method == "ping":
        send_response(request_id, {})

    else:
        if request_id is not None:
            send_error(request_id, -32601, f"Method not found: {method}")


def read_message():
    """Read a JSON-RPC message from stdin using Content-Length headers."""
    headers = {}
    while True:
        line = sys.stdin.readline()
        if not line:
            return None
        line = line.strip()
        if not line:
            break
        if ":" in line:
            key, value = line.split(":", 1)
            headers[key.strip()] = value.strip()

    content_length = int(headers.get("Content-Length", 0))
    if content_length == 0:
        return None

    body = sys.stdin.read(content_length)
    return json.loads(body)


def main():
    """Run the Aura MCP server (stdio transport)."""
    while True:
        try:
            message = read_message()
            if message is None:
                break
            handle_request(message)
        except json.JSONDecodeError:
            continue
        except KeyboardInterrupt:
            break
        except Exception:
            continue


if __name__ == "__main__":
    main()

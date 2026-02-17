Manage persistent agent memory using Aura's 3-tier Memory OS.

Usage: /aura-memory $ARGUMENTS

The first argument is the action. Supported actions:
- `write` — Write a memory entry
- `query` — Search memory for relevant entries
- `list` — List all stored memories
- `usage` — Show memory tier usage statistics
- `prune` — Remove old pad/episodic entries

Steps:
1. Check if aura-core is installed: `pip show aura-core`. If not installed, run `pip install auralith-aura`.
2. Parse the action from the first argument.
3. Run the appropriate Python code:

For `write`:
```python
from aura.memory import AuraMemoryOS

memory = AuraMemoryOS()

# Determine the tier from context:
# - "fact" for verified information, user preferences, project constants
# - "pad" for working notes, scratch space, TODO items
# - "episodic" for session logs, conversation summaries

tier = "<fact|pad|episodic>"  # Choose based on content
content = "<the content to remember>"

memory.write(tier, content)
print(f"✅ Written to {tier} tier")
```

For `query`:
```python
from aura.memory import AuraMemoryOS

memory = AuraMemoryOS()
results = memory.query("<search_query>")
for entry in results:
    print(f"[{entry['tier']}] {entry['content']}")
```

For `list`:
```python
from aura.memory import AuraMemoryOS

memory = AuraMemoryOS()
entries = memory.list_entries()
for entry in entries:
    print(f"[{entry['tier']}] {entry['content'][:200]}")
```

For `usage`:
```python
from aura.memory import AuraMemoryOS

memory = AuraMemoryOS()
stats = memory.usage()
for tier, info in stats.items():
    print(f"{tier}: {info['count']} entries, {info['size_bytes']} bytes")
```

Example invocations:
- `/aura-memory write fact User prefers dark mode and TypeScript`
- `/aura-memory query "user preferences"`
- `/aura-memory list`
- `/aura-memory usage`

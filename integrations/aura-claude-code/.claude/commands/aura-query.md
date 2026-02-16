Search an Aura knowledge base for relevant documents.

Usage: /aura-query $ARGUMENTS

The first argument should be the path to the .aura file.
All remaining arguments form the search query.

Steps:
1. Check if aura-core is installed. If not, run `pip install auralith-aura`.
2. Parse arguments: first arg = aura file path, rest = search query.
3. Use the following Python code to search:

```python
from aura.rag import AuraRAGLoader

loader = AuraRAGLoader("<aura_file>")
query = "<search_query>".lower()

results = []
for doc_id, text, meta in loader.iterate_texts():
    if not text:
        continue
    score = sum(1 for word in query.split() if word in text.lower())
    if score > 0:
        results.append((score, doc_id, text, meta))

results.sort(key=lambda x: x[0], reverse=True)

for score, doc_id, text, meta in results[:5]:
    source = meta.get("source", doc_id)
    print(f"📄 {source} (relevance: {score})")
    print(f"   {text[:300]}...")

loader.close()
```

4. Present the top 5 results with source file, relevance score, and a text preview.
5. If the user asks follow-up questions, use the same loader to retrieve more context.

Example:
- `/aura-query knowledge.aura how does authentication work`

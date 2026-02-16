Compile documents into an Aura knowledge base.

Usage: /aura-compile $ARGUMENTS

If no arguments are provided, compile the current project's ./docs directory.
If one argument is provided, treat it as the input directory.
If two arguments are provided, treat the second as the output filename.

Steps:
1. Check if aura-core is installed: `pip show aura-core`. If not installed, run `pip install aura-core`.
2. Determine the input directory (default: ./docs) and output file (default: knowledge.aura).
3. Run: `aura compile <input_dir> --output <output_file>`
4. Report the results: number of documents compiled, output file location, and file size.

Example invocations:
- `/aura-compile` → compiles ./docs → knowledge.aura
- `/aura-compile ./legal` → compiles ./legal → knowledge.aura
- `/aura-compile ./legal legal_kb.aura` → compiles ./legal → legal_kb.aura

"""
Aura: The Universal Context Compiler for AI Agent Memory

Aura compiles messy raw files (PDFs, Documents, Code, Data) into a single,
optimized binary format (.aura) ready for AI agent memory and RAG.

Quick Start:
    # Compile a directory
    >>> from aura import compile_directory
    >>> compile_directory("./my_docs/", "knowledge.aura")
    
    # Load for RAG
    >>> from aura.rag import AuraRAGLoader
    >>> loader = AuraRAGLoader("knowledge.aura")
"""

__version__ = "0.1.0"
__author__ = "Auralith Inc."
__license__ = "Apache-2.0"

from .loader import AuraReader, AuraWriter

__all__ = [
    "AuraReader",
    "AuraWriter",
    "__version__",
]

# Lazy imports for optional dependencies
def __getattr__(name):
    if name == "AuraRAGLoader":
        from .rag import AuraRAGLoader
        return AuraRAGLoader
    if name == "compile_directory":
        from .compiler import compile_directory
        return compile_directory
    if name == "AuraMemoryOS":
        from .memory import AuraMemoryOS
        return AuraMemoryOS
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

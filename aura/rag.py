# SPDX-License-Identifier: Apache-2.0
# AURA RAG ADAPTER
# Random-access retrieval for RAG applications

"""
Aura RAG Adapter

Enables using .aura files as a knowledge base for Retrieval-Augmented Generation.
The indexed format allows O(1) random access without loading the entire dataset.

Fully compatible with LangChain, LlamaIndex, and other RAG frameworks.

Example:
    from aura.rag import AuraRAGLoader
    
    loader = AuraRAGLoader("knowledge_base.aura")
    
    # Get all document IDs
    doc_ids = loader.get_all_ids()
    
    # Fetch specific document text
    text = loader.get_text_by_id(doc_ids[0])
    
    # Convert to LangChain Documents
    langchain_docs = loader.to_langchain_documents()
    
    # Convert to LlamaIndex Documents
    llama_docs = loader.to_llama_index_documents()
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Iterator, Union, Callable

from .loader import AuraReader

logger = logging.getLogger(__name__)


class AuraRAGLoader:
    """
    RAG-optimized loader for .aura files.
    
    Provides random-access retrieval without loading the entire dataset
    into memory. Designed for use as a knowledge base in RAG pipelines.
    
    Features:
        - O(1) access by document ID
        - Raw text retrieval for RAG
        - Metadata-based filtering
        - Memory-efficient streaming
        - Native LangChain/LlamaIndex integration
    
    Args:
        aura_path: Path to the .aura file
    """
    
    def __init__(self, aura_path: Union[str, Path]):
        self.aura_path = Path(aura_path)
        
        if not self.aura_path.exists():
            raise FileNotFoundError(f"Aura file not found: {aura_path}")
        
        self.reader = AuraReader(self.aura_path)
        self._id_to_meta_cache: Dict[str, Dict] = {}
        
        logger.info(f"AuraRAGLoader initialized: {len(self.reader)} documents")
    
    def get_by_id(self, doc_id: str) -> Dict[str, Any]:
        """
        Fetch a document by its ID.
        
        Args:
            doc_id: The document identifier
            
        Returns:
            Dictionary with 'tensors' and 'meta' keys
        """
        return self.reader.read_datapoint(doc_id)
    
    def get_text_by_id(self, doc_id: str) -> str:
        """
        Get the raw text content for a document.
        
        This returns the original text stored during compilation.
        Requires the archive was compiled with --include-text (default).
        
        Args:
            doc_id: The document identifier
            
        Returns:
            Raw text content, or empty string if not stored
        """
        record = self.reader.read_datapoint(doc_id)
        return record['meta'].get('text_content', '')
    
    def get_all_ids(self) -> List[str]:
        """
        Get all document IDs in the archive.
        
        Returns:
            List of document identifiers
        """
        return self.reader.datapoint_ids.copy()
    
    def get_metadata(self, doc_id: str) -> Dict[str, Any]:
        """
        Get only the metadata for a document (faster than full fetch).
        
        Args:
            doc_id: The document identifier
            
        Returns:
            Metadata dictionary
        """
        if doc_id in self._id_to_meta_cache:
            return self._id_to_meta_cache[doc_id]
        
        record = self.reader.read_datapoint(doc_id)
        meta = record['meta']
        self._id_to_meta_cache[doc_id] = meta
        return meta
    
    def filter_by_extension(self, extension: str) -> List[str]:
        """
        Find all documents with a specific file extension.
        
        Args:
            extension: File extension (e.g., '.pdf', '.py')
            
        Returns:
            List of matching document IDs
        """
        if not extension.startswith('.'):
            extension = '.' + extension
        
        matching = []
        for doc_id in self.reader.datapoint_ids:
            meta = self.get_metadata(doc_id)
            if meta.get('file_extension', '').lower() == extension.lower():
                matching.append(doc_id)
        return matching
    
    def filter_by_weight(self, min_weight: float = 1.0) -> List[str]:
        """
        Find all documents with emphasis weight >= min_weight.
        
        Args:
            min_weight: Minimum emphasis weight
            
        Returns:
            List of matching document IDs
        """
        matching = []
        for doc_id in self.reader.datapoint_ids:
            meta = self.get_metadata(doc_id)
            weight = meta.get('emphasis_weight', 1.0)
            if weight >= min_weight:
                matching.append(doc_id)
        return matching
    
    def filter_by_source(self, pattern: str) -> List[str]:
        """
        Find all documents whose source path contains the pattern.
        
        Args:
            pattern: String to match in source path (case-insensitive)
            
        Returns:
            List of matching document IDs
        """
        pattern_lower = pattern.lower()
        matching = []
        for doc_id in self.reader.datapoint_ids:
            meta = self.get_metadata(doc_id)
            source = meta.get('source', '').lower()
            if pattern_lower in source:
                matching.append(doc_id)
        return matching
    
    def filter(self, predicate: Callable[[Dict[str, Any]], bool]) -> List[str]:
        """
        Filter documents using a custom predicate function.
        
        Args:
            predicate: Function that takes metadata and returns bool
            
        Returns:
            List of matching document IDs
        """
        matching = []
        for doc_id in self.reader.datapoint_ids:
            meta = self.get_metadata(doc_id)
            if predicate(meta):
                matching.append(doc_id)
        return matching
    
    def iterate_all(self) -> Iterator[Dict[str, Any]]:
        """
        Iterate over all documents.
        
        Yields:
            Dictionary with 'tensors' and 'meta' keys
        """
        for record in self.reader:
            yield record
    
    def iterate_texts(self) -> Iterator[tuple]:
        """
        Iterate over all document texts.
        
        Yields:
            Tuple of (doc_id, text_content, metadata)
        """
        for doc_id in self.reader.datapoint_ids:
            record = self.reader.read_datapoint(doc_id)
            text = record['meta'].get('text_content', '')
            yield doc_id, text, record['meta']
    
    # =========================================================================
    # FRAMEWORK INTEGRATIONS
    # =========================================================================
    
    def to_langchain_documents(self) -> List:
        """
        Convert to LangChain Document objects.
        
        Requires: pip install langchain-core
        
        Returns:
            List of LangChain Document objects
        """
        try:
            from langchain_core.documents import Document
        except ImportError:
            raise ImportError(
                "LangChain not installed. Install with: pip install langchain-core"
            )
        
        docs = []
        for doc_id in self.reader.datapoint_ids:
            record = self.reader.read_datapoint(doc_id)
            text = record['meta'].get('text_content', '')
            if text:
                # Create metadata dict without text_content (it's in page_content)
                meta = {k: v for k, v in record['meta'].items() if k != 'text_content'}
                meta['doc_id'] = doc_id
                docs.append(Document(page_content=text, metadata=meta))
        
        return docs
    
    def to_llama_index_documents(self) -> List:
        """
        Convert to LlamaIndex Document objects.
        
        Requires: pip install llama-index-core
        
        Returns:
            List of LlamaIndex Document objects
        """
        try:
            from llama_index.core import Document
        except ImportError:
            raise ImportError(
                "LlamaIndex not installed. Install with: pip install llama-index-core"
            )
        
        docs = []
        for doc_id in self.reader.datapoint_ids:
            record = self.reader.read_datapoint(doc_id)
            text = record['meta'].get('text_content', '')
            if text:
                # Create metadata dict without text_content
                meta = {k: v for k, v in record['meta'].items() if k != 'text_content'}
                meta['doc_id'] = doc_id
                docs.append(Document(text=text, metadata=meta))
        
        return docs
    
    def to_dict_list(self) -> List[Dict[str, Any]]:
        """
        Convert to a list of dictionaries (universal format).
        
        Returns:
            List of dicts with 'text', 'metadata', and 'doc_id' keys
        """
        docs = []
        for doc_id in self.reader.datapoint_ids:
            record = self.reader.read_datapoint(doc_id)
            text = record['meta'].get('text_content', '')
            if text:
                meta = {k: v for k, v in record['meta'].items() if k != 'text_content'}
                docs.append({
                    'doc_id': doc_id,
                    'text': text,
                    'metadata': meta
                })
        return docs
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge base.
        
        Returns:
            Dictionary with stats like count, extensions, etc.
        """
        extensions = {}
        total_weight = 0.0
        has_text_count = 0
        
        for doc_id in self.reader.datapoint_ids:
            meta = self.get_metadata(doc_id)
            
            # Count extensions
            ext = meta.get('file_extension', 'unknown')
            extensions[ext] = extensions.get(ext, 0) + 1
            
            # Sum weights
            total_weight += meta.get('emphasis_weight', 1.0)
            
            # Count documents with text
            if meta.get('text_content'):
                has_text_count += 1
        
        return {
            'total_documents': len(self.reader),
            'documents_with_text': has_text_count,
            'extensions': extensions,
            'average_weight': total_weight / len(self.reader) if len(self.reader) > 0 else 0.0
        }
    
    def __len__(self) -> int:
        return len(self.reader)
    
    def __contains__(self, doc_id: str) -> bool:
        return doc_id in self.reader.datapoint_ids
    
    def close(self):
        """Close the underlying reader."""
        if hasattr(self, 'reader') and self.reader:
            self.reader.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
    
    def __del__(self):
        self.close()


# Convenience function for loading documents
def load_aura_documents(
    aura_path: Union[str, Path],
    filter_extension: Optional[str] = None,
    filter_source: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Load documents from an .aura file.
    
    Convenience function for loading documents, optionally filtered.
    
    Args:
        aura_path: Path to the .aura file
        filter_extension: Optional extension to filter by (e.g., '.pdf')
        filter_source: Optional source path pattern to filter by
        
    Returns:
        List of document dictionaries with 'text', 'metadata', 'doc_id'
    """
    with AuraRAGLoader(aura_path) as loader:
        if filter_extension:
            doc_ids = loader.filter_by_extension(filter_extension)
        elif filter_source:
            doc_ids = loader.filter_by_source(filter_source)
        else:
            doc_ids = loader.get_all_ids()
        
        docs = []
        for doc_id in doc_ids:
            record = loader.get_by_id(doc_id)
            text = record['meta'].get('text_content', '')
            if text:
                meta = {k: v for k, v in record['meta'].items() if k != 'text_content'}
                docs.append({
                    'doc_id': doc_id,
                    'text': text,
                    'metadata': meta
                })
        
        return docs

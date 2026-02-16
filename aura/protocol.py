# SPDX-License-Identifier: Apache-2.0
# AURA PROTOCOL - DATA SCHEMA AND TYPES
# Defines the standard schema for .aura datapoints

"""
Aura Protocol v0.1.0

This module defines the data schema and types used in .aura files.
It provides a clean, ML-focused vocabulary (no physics terminology).
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib


class AuraVersion(Enum):
    """Aura Protocol Version"""
    V0_1 = "aura-v0.1"


class FieldType(Enum):
    """
    Standard field types for Aura datapoints.
    
    These define what kind of data is stored in each tensor.
    """
    # Token-based fields (text/code)
    TOKEN_IDS = "token_ids"
    ATTENTION_MASK = "attention_mask"
    TOKEN_TYPE_IDS = "token_type_ids"
    
    # Pixel-based fields (images)
    PIXEL_VALUES = "pixel_values"
    
    # Emphasis/weighting (the "secret sauce")
    EMPHASIS_WEIGHT = "emphasis_weight"
    
    # Labels
    LABELS = "labels"
    MULTI_LABELS = "multi_labels"
    
    # Provenance
    SOURCE_REF = "source_ref"
    CONTENT_HASH = "content_hash"


@dataclass
class AuraMetadata:
    """
    Metadata for an Aura datapoint.
    
    This is stored alongside tensors and supports custom fields.
    """
    # Required fields
    source: str                          # Original file path or identifier
    content_hash: str                    # SHA256 of original content
    
    # Optional standard fields
    protocol_version: str = AuraVersion.V0_1.value
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    
    # Emphasis/weighting
    emphasis_weight: float = 1.0         # Default weight for training
    
    # Labels (flexible - user-provided)
    labels: Dict[str, Any] = field(default_factory=dict)
    
    # RAG Support - store original text for retrieval
    text_content: Optional[str] = None
    
    # Original file info
    file_extension: Optional[str] = None
    file_size_bytes: Optional[int] = None
    
    # Tokenization info
    tokenizer_name: Optional[str] = None
    max_length: Optional[int] = None
    truncated: bool = False
    
    # Custom fields
    extra: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            'source': self.source,
            'content_hash': self.content_hash,
            'protocol_version': self.protocol_version,
            'created_at': self.created_at,
            'emphasis_weight': self.emphasis_weight,
            'labels': self.labels,
            'file_extension': self.file_extension,
            'file_size_bytes': self.file_size_bytes,
            'tokenizer_name': self.tokenizer_name,
            'max_length': self.max_length,
            'truncated': self.truncated,
            **self.extra
        }
        # Only include text_content if present (can be large)
        if self.text_content is not None:
            result['text_content'] = self.text_content
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuraMetadata':
        """Create from dictionary."""
        known_fields = {
            'source', 'content_hash', 'protocol_version', 'created_at',
            'emphasis_weight', 'labels', 'text_content', 'file_extension',
            'file_size_bytes', 'tokenizer_name', 'max_length', 'truncated'
        }
        
        # Separate known and extra fields
        known = {k: v for k, v in data.items() if k in known_fields}
        extra = {k: v for k, v in data.items() if k not in known_fields and not k.startswith('_')}
        
        return cls(**known, extra=extra)


@dataclass
class AuraDatapoint:
    """
    A single datapoint in an Aura archive.
    
    Contains tensorized data and metadata.
    """
    id: str
    tensors: Dict[str, Any]  # numpy arrays
    metadata: AuraMetadata
    
    @property
    def input_ids(self):
        """Get input_ids tensor if present."""
        return self.tensors.get('input_ids')
    
    @property
    def attention_mask(self):
        """Get attention_mask tensor if present."""
        return self.tensors.get('attention_mask')
    
    @property
    def emphasis_weight(self) -> float:
        """Get emphasis weight for this datapoint."""
        return self.metadata.emphasis_weight


def compute_content_hash(content: str) -> str:
    """Compute SHA256 hash of content."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def validate_datapoint(datapoint: Dict[str, Any]) -> bool:
    """
    Validate that a datapoint has required fields.
    
    Returns True if valid, raises ValueError if not.
    """
    tensors = datapoint.get('tensors', {})
    meta = datapoint.get('meta', {})
    
    # Must have at least one tensor
    if not tensors:
        raise ValueError("Datapoint must have at least one tensor")
    
    # Must have source
    if 'source' not in meta and '_id' not in meta:
        raise ValueError("Datapoint must have 'source' in metadata")
    
    # Validate tensor types
    for key, value in tensors.items():
        import numpy as np
        if not isinstance(value, np.ndarray):
            raise ValueError(f"Tensor '{key}' must be a numpy array, got {type(value)}")
    
    return True
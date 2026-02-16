# SPDX-License-Identifier: Apache-2.0
# AURA MEMORY OS - Three-Tier Memory with Two-Speed WAL
#
# Provides a cognitively-inspired memory architecture for AI agents:
#   /pad       - Working notepad (transient, fast writes)
#   /episodic  - Session logs (auto-archived)
#   /fact      - Immutable truths (persistent knowledge)

"""
Aura Memory OS v2.0

Three-Tier Memory Architecture:
    /pad       → Working notes, scratch space, thinking-out-loud
    /episodic  → Session transcripts, conversation history
    /fact      → Verified facts, user preferences, persistent knowledge

Two-Speed Write-Ahead Log:
    Speed 1: Instant JSONL append (~0.001s) for agent responsiveness
    Speed 2: Background compilation to .aura shards (session end / threshold)
"""

import os
import json
import time
import logging
import hashlib
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

# Default memory root
DEFAULT_MEMORY_ROOT = Path.home() / ".aura" / "memory"

# WAL flush threshold (number of entries before background compile)
WAL_FLUSH_THRESHOLD = 100

# Shard size target (bytes) before rotation
SHARD_SIZE_TARGET = 5 * 1024 * 1024  # 5MB


@dataclass
class MemoryEntry:
    """A single memory entry in the WAL."""
    namespace: str          # pad, episodic, fact
    content: str            # Raw text content
    timestamp: str          # ISO 8601
    source: str             # Where this came from (agent, user, system)
    session_id: str         # Session identifier
    entry_id: str           # Unique entry hash
    tags: List[str] = None  # Optional classification tags

    def __post_init__(self):
        self.tags = self.tags or []


@dataclass
class ShardInfo:
    """Metadata about a compiled .aura shard."""
    shard_id: str
    namespace: str
    path: str
    created_at: str
    entry_count: int
    size_bytes: int
    session_ids: List[str]


class TwoSpeedWAL:
    """
    Two-Speed Write-Ahead Log.
    
    Speed 1 (Instant): Appends to a JSONL scratchpad (~0.001s)
    Speed 2 (Background): Compiles JSONL into .aura binary shards
    
    This ensures agents are never blocked by I/O while maintaining
    durable, queryable memory.
    """
    
    def __init__(self, memory_root: Path, namespace: str):
        self.memory_root = memory_root
        self.namespace = namespace
        self.wal_dir = memory_root / namespace / "wal"
        self.shard_dir = memory_root / namespace / "shards"
        
        # Ensure directories exist
        self.wal_dir.mkdir(parents=True, exist_ok=True)
        self.shard_dir.mkdir(parents=True, exist_ok=True)
        
        # Active WAL file
        self.wal_path = self.wal_dir / "active.jsonl"
        self._entry_count = self._count_wal_entries()
    
    def _count_wal_entries(self) -> int:
        """Count entries in active WAL."""
        if not self.wal_path.exists():
            return 0
        try:
            with open(self.wal_path, 'r', encoding='utf-8') as f:
                return sum(1 for line in f if line.strip())
        except Exception:
            return 0
    
    def append(self, entry: MemoryEntry) -> float:
        """
        Speed 1: Instant append to JSONL WAL.
        
        Returns: Time taken in seconds (should be ~0.001s)
        """
        start = time.perf_counter()
        
        entry_dict = asdict(entry)
        line = json.dumps(entry_dict, ensure_ascii=False) + "\n"
        
        with open(self.wal_path, 'a', encoding='utf-8') as f:
            f.write(line)
        
        self._entry_count += 1
        elapsed = time.perf_counter() - start
        
        logger.debug(f"WAL append: {elapsed:.4f}s ({self.namespace})")
        return elapsed
    
    @property
    def needs_flush(self) -> bool:
        """Check if WAL has enough entries to warrant compilation."""
        return self._entry_count >= WAL_FLUSH_THRESHOLD
    
    def flush_to_shard(self) -> Optional[ShardInfo]:
        """
        Speed 2: Compile WAL entries into an .aura shard.
        
        Called at session end or when WAL threshold is reached.
        """
        if not self.wal_path.exists() or self._entry_count == 0:
            return None
        
        # Read all WAL entries
        entries = []
        session_ids = set()
        
        try:
            with open(self.wal_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            entry = json.loads(line)
                            entries.append(entry)
                            session_ids.add(entry.get('session_id', 'unknown'))
                        except json.JSONDecodeError:
                            logger.warning(f"Skipping malformed WAL entry")
        except Exception as e:
            logger.error(f"Failed to read WAL: {e}")
            return None
        
        if not entries:
            return None
        
        # Generate shard ID
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        content_hash = hashlib.sha256(
            json.dumps(entries, sort_keys=True).encode()
        ).hexdigest()[:8]
        shard_id = f"{self.namespace}_{timestamp}_{content_hash}"
        
        # Write compiled shard (JSONL format for now, .aura binary later)
        shard_path = self.shard_dir / f"{shard_id}.jsonl"
        
        try:
            with open(shard_path, 'w', encoding='utf-8') as f:
                for entry in entries:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            
            shard_size = shard_path.stat().st_size
            
            # Clear WAL
            self.wal_path.unlink(missing_ok=True)
            self._entry_count = 0
            
            shard_info = ShardInfo(
                shard_id=shard_id,
                namespace=self.namespace,
                path=str(shard_path),
                created_at=datetime.utcnow().isoformat() + 'Z',
                entry_count=len(entries),
                size_bytes=shard_size,
                session_ids=list(session_ids)
            )
            
            logger.info(f"Compiled shard: {shard_id} ({len(entries)} entries, "
                       f"{shard_size / 1024:.1f} KB)")
            
            return shard_info
            
        except Exception as e:
            logger.error(f"Failed to compile shard: {e}")
            return None
    
    def read_wal(self) -> List[Dict[str, Any]]:
        """Read all entries from active WAL."""
        entries = []
        if not self.wal_path.exists():
            return entries
        
        try:
            with open(self.wal_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            entries.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        except Exception:
            pass
        
        return entries


class AuraMemoryOS:
    """
    Three-Tier Memory Operating System.
    
    Manages three cognitive memory tiers:
        /pad       - Working notepad, transient scratch space
        /episodic  - Session transcripts, auto-archived
        /fact      - Immutable knowledge, user preferences
    
    Each tier has its own Two-Speed WAL for instant writes
    with background compilation.
    """
    
    NAMESPACES = ('pad', 'episodic', 'fact')
    
    def __init__(self, memory_root: Optional[str] = None, session_id: Optional[str] = None):
        self.memory_root = Path(memory_root) if memory_root else DEFAULT_MEMORY_ROOT
        self.session_id = session_id or datetime.utcnow().strftime("session_%Y%m%d_%H%M%S")
        
        # Initialize WALs for each tier
        self.wals = {
            ns: TwoSpeedWAL(self.memory_root, ns)
            for ns in self.NAMESPACES
        }
        
        logger.info(f"AuraMemoryOS initialized: {self.memory_root} (session: {self.session_id})")
    
    def write(self, namespace: str, content: str, source: str = "agent",
              tags: Optional[List[str]] = None) -> MemoryEntry:
        """
        Write a memory entry to the specified namespace.
        
        Args:
            namespace: One of 'pad', 'episodic', 'fact'
            content: Text content to remember
            source: Origin (agent, user, system)
            tags: Optional classification tags
        
        Returns:
            The created MemoryEntry
        """
        if namespace not in self.NAMESPACES:
            raise ValueError(f"Invalid namespace '{namespace}'. Must be one of: {self.NAMESPACES}")
        
        # Generate entry ID
        entry_id = hashlib.sha256(
            f"{content}{time.time()}".encode()
        ).hexdigest()[:16]
        
        entry = MemoryEntry(
            namespace=namespace,
            content=content,
            timestamp=datetime.utcnow().isoformat() + 'Z',
            source=source,
            session_id=self.session_id,
            entry_id=entry_id,
            tags=tags
        )
        
        # Speed 1: Instant WAL append
        write_time = self.wals[namespace].append(entry)
        
        # Check if background compilation needed
        if self.wals[namespace].needs_flush:
            logger.info(f"WAL threshold reached for /{namespace}, auto-flushing...")
            self.wals[namespace].flush_to_shard()
        
        return entry
    
    def end_session(self):
        """
        End the current session, flushing all WALs to shards.
        
        This should be called when an agent session ends to ensure
        all buffered memory is durably persisted.
        """
        flushed = []
        for namespace in self.NAMESPACES:
            shard = self.wals[namespace].flush_to_shard()
            if shard:
                flushed.append(shard)
        
        if flushed:
            print(f"📦 Session ended. Compiled {len(flushed)} memory shard(s):")
            for shard in flushed:
                print(f"   /{shard.namespace}: {shard.entry_count} entries "
                      f"({shard.size_bytes / 1024:.1f} KB)")
        else:
            print(f"📦 Session ended. No new memories to compile.")
    
    def list_shards(self):
        """List all compiled memory shards across all tiers."""
        print(f"📋 Aura Memory Shards ({self.memory_root})")
        print()
        
        total_size = 0
        total_shards = 0
        
        for namespace in self.NAMESPACES:
            shard_dir = self.memory_root / namespace / "shards"
            if not shard_dir.exists():
                continue
            
            shards = sorted(shard_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
            
            if shards:
                print(f"  /{namespace}:")
                for shard_path in shards:
                    stat = shard_path.stat()
                    size_kb = stat.st_size / 1024
                    modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                    
                    # Count entries
                    try:
                        with open(shard_path, 'r', encoding='utf-8') as f:
                            entry_count = sum(1 for line in f if line.strip())
                    except Exception:
                        entry_count = '?'
                    
                    print(f"    {shard_path.stem}  |  {entry_count} entries  |  "
                          f"{size_kb:.1f} KB  |  {modified}")
                    
                    total_size += stat.st_size
                    total_shards += 1
                print()
            
            # Also show active WAL entries
            wal = self.wals[namespace]
            if wal._entry_count > 0:
                print(f"    📝 Active WAL: {wal._entry_count} buffered entries")
                print()
        
        if total_shards == 0:
            print("  No compiled shards found. Memory is still in WAL buffers.")
        else:
            print(f"  Total: {total_shards} shard(s), {total_size / 1024:.1f} KB")
    
    def prune_shards(self, before_date: Optional[str] = None, 
                     shard_ids: Optional[List[str]] = None,
                     namespace: Optional[str] = None):
        """
        Prune memory shards by date or ID.
        
        Args:
            before_date: Delete shards older than this date (YYYY-MM-DD)
            shard_ids: Delete specific shards by ID
            namespace: Only prune within this namespace (default: all)
        """
        namespaces = [namespace] if namespace else list(self.NAMESPACES)
        deleted = 0
        freed_bytes = 0
        
        for ns in namespaces:
            shard_dir = self.memory_root / ns / "shards"
            if not shard_dir.exists():
                continue
            
            for shard_path in shard_dir.glob("*.jsonl"):
                should_delete = False
                
                if shard_ids and shard_path.stem in shard_ids:
                    should_delete = True
                
                if before_date:
                    try:
                        cutoff = datetime.strptime(before_date, "%Y-%m-%d")
                        shard_mtime = datetime.fromtimestamp(shard_path.stat().st_mtime)
                        if shard_mtime < cutoff:
                            should_delete = True
                    except ValueError:
                        print(f"❌ Invalid date format: {before_date}. Use YYYY-MM-DD")
                        return
                
                if should_delete:
                    size = shard_path.stat().st_size
                    shard_path.unlink()
                    deleted += 1
                    freed_bytes += size
                    logger.info(f"Pruned shard: {shard_path.stem}")
        
        if deleted > 0:
            print(f"🗑️  Pruned {deleted} shard(s), freed {freed_bytes / 1024:.1f} KB")
        else:
            print(f"No shards matched the pruning criteria.")
    
    def show_usage(self):
        """Show total memory storage usage."""
        print(f"💾 Aura Memory Usage ({self.memory_root})")
        print()
        
        grand_total = 0
        
        for namespace in self.NAMESPACES:
            ns_dir = self.memory_root / namespace
            if not ns_dir.exists():
                print(f"  /{namespace}: 0 KB")
                continue
            
            total_bytes = sum(
                f.stat().st_size for f in ns_dir.rglob("*") if f.is_file()
            )
            grand_total += total_bytes
            
            # Count shards and WAL entries
            shard_dir = ns_dir / "shards"
            shard_count = len(list(shard_dir.glob("*.jsonl"))) if shard_dir.exists() else 0
            wal_entries = self.wals[namespace]._entry_count
            
            print(f"  /{namespace}: {total_bytes / 1024:.1f} KB  "
                  f"({shard_count} shard(s), {wal_entries} buffered)")
        
        print()
        print(f"  Total: {grand_total / 1024:.1f} KB ({grand_total / (1024*1024):.2f} MB)")
    
    def query(self, query_text: str, namespace: Optional[str] = None, 
              top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Simple keyword search across memory.
        
        For semantic search, use the OMNI Platform.
        
        Args:
            query_text: Search query
            namespace: Limit search to specific namespace (default: all)
            top_k: Number of results to return
        
        Returns:
            List of matching entries with relevance scores
        """
        namespaces = [namespace] if namespace else list(self.NAMESPACES)
        results = []
        query_lower = query_text.lower()
        query_words = set(query_lower.split())
        
        for ns in namespaces:
            # Search active WAL
            wal_entries = self.wals[ns].read_wal()
            for entry in wal_entries:
                content = entry.get('content', '').lower()
                # Simple word overlap scoring
                content_words = set(content.split())
                overlap = len(query_words & content_words)
                if overlap > 0:
                    score = overlap / len(query_words)
                    results.append({
                        'content': entry.get('content', ''),
                        'namespace': ns,
                        'timestamp': entry.get('timestamp', ''),
                        'source': entry.get('source', ''),
                        'score': score,
                        'location': 'wal'
                    })
            
            # Search compiled shards
            shard_dir = self.memory_root / ns / "shards"
            if shard_dir.exists():
                for shard_path in shard_dir.glob("*.jsonl"):
                    try:
                        with open(shard_path, 'r', encoding='utf-8') as f:
                            for line in f:
                                if line.strip():
                                    try:
                                        entry = json.loads(line)
                                        content = entry.get('content', '').lower()
                                        content_words = set(content.split())
                                        overlap = len(query_words & content_words)
                                        if overlap > 0:
                                            score = overlap / len(query_words)
                                            results.append({
                                                'content': entry.get('content', ''),
                                                'namespace': ns,
                                                'timestamp': entry.get('timestamp', ''),
                                                'source': entry.get('source', ''),
                                                'score': score,
                                                'location': shard_path.stem
                                            })
                                    except json.JSONDecodeError:
                                        continue
                    except Exception:
                        continue
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]

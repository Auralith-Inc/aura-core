# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 Auralith Inc. All rights reserved.
#
# AURA MEMORY OS - Three-Tier Persistent Memory for AI Agents
#
# This module is distributed as a pre-built component via PyPI.
# Install with: pip install auralith-aura
#
# The open-source components (compiler, RAG, loader) are available
# on GitHub: https://github.com/Auralith-Inc/aura-core

"""
Aura Memory OS — Three-Tier Persistent Memory for AI Agents.

Provides a cognitively-inspired memory architecture:
    /pad       - Working notepad (transient, fast writes)
    /episodic  - Session transcripts (auto-archived)
    /fact      - Verified facts (persistent, survives indefinitely)

Install from PyPI to use:
    pip install auralith-aura

Usage:
    from aura.memory import AuraMemoryOS
    memory = AuraMemoryOS()
    memory.write("fact", "The auth module uses JWT tokens")
"""

try:
    from aura._memory import (  # noqa: F401
        AuraMemoryOS,
        MemoryEntry,
        TwoSpeedWAL,
        ShardInfo,
    )
except ImportError:

    class AuraMemoryOS:
        """Three-Tier Memory Operating System.

        This module requires installation via PyPI:
            pip install auralith-aura

        The Memory OS is included free in the PyPI package.
        """

        def __init__(self, *args, **kwargs):
            raise ImportError(
                "\n\nAura Memory OS is included in the PyPI package.\n"
                "Install with: pip install auralith-aura\n\n"
                "Open-source components (compiler, RAG, loader) are "
                "available on GitHub.\n"
            )

    class MemoryEntry:
        pass

    class TwoSpeedWAL:
        pass

    class ShardInfo:
        pass

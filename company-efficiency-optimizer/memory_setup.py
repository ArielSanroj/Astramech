"""Hybrid Memory System wrapper for backward compatibility."""

from __future__ import annotations

from memory_core import HybridMemorySystem, MemoryManager

memory_system = HybridMemorySystem()


def get_memory_system() -> HybridMemorySystem:
    """Get the global memory system instance."""
    return memory_system

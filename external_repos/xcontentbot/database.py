#!/usr/bin/env python3
"""
Database layer for xcontentbot.
Provides persistent storage for posts, bot runs, and metrics.

This module re-exports from the database package for backwards compatibility.
"""

# Re-export everything from the database package
from database import (
    # Models
    Base,
    ProcessedPost,
    BotRun,
    Metrics,
    # Manager
    DatabaseManager,
    db_manager,
    # Convenience functions
    record_post,
    start_run,
    complete_run,
    get_recent_posts,
    get_recent_runs,
    get_summary,
)

__all__ = [
    "Base",
    "ProcessedPost",
    "BotRun",
    "Metrics",
    "DatabaseManager",
    "db_manager",
    "record_post",
    "start_run",
    "complete_run",
    "get_recent_posts",
    "get_recent_runs",
    "get_summary",
]

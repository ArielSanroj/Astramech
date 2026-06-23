#!/usr/bin/env python3
"""
Database layer for xcontentbot.
Provides persistent storage for posts, bot runs, and metrics.
"""

from typing import List, Dict, Any

from .models import Base, ProcessedPost, BotRun, Metrics
from .manager import DatabaseManager

# Global database manager instance
db_manager = DatabaseManager()


# Convenience functions
def record_post(post_id: str, url: str, query: str, status: str, **kwargs):
    """Record a processed post."""
    db_manager.record_processed_post(post_id, url, query, status, **kwargs)


def start_run(queries: List[str] = None) -> int:
    """Start a new bot run."""
    return db_manager.start_bot_run(queries)


def complete_run(
    run_id: int,
    posts_processed: int,
    posts_posted: int,
    errors: int
):
    """Complete a bot run."""
    db_manager.complete_bot_run(run_id, posts_processed, posts_posted, errors)


def get_recent_posts(limit: int = 100) -> List[Dict[str, Any]]:
    """Get recent processed posts."""
    return db_manager.get_processed_posts(limit)


def get_recent_runs(limit: int = 50) -> List[Dict[str, Any]]:
    """Get recent bot runs."""
    return db_manager.get_bot_runs(limit)


def get_summary() -> Dict[str, Any]:
    """Get database summary."""
    return db_manager.get_metrics_summary()


__all__ = [
    # Models
    "Base",
    "ProcessedPost",
    "BotRun",
    "Metrics",
    # Manager
    "DatabaseManager",
    "db_manager",
    # Convenience functions
    "record_post",
    "start_run",
    "complete_run",
    "get_recent_posts",
    "get_recent_runs",
    "get_summary",
]

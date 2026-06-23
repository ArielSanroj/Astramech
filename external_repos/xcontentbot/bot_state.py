"""Bot state management with persistence."""
import os
import json
import logging
from datetime import datetime
from typing import Optional, Set

from client_config import STATE_FILE

logger = logging.getLogger("x-mcp-client")


class BotState:
    """Manages bot state with JSON persistence."""

    def __init__(self):
        self.processed_posts: Set[str] = set()
        self.last_run_time: Optional[datetime] = None
        self.next_run_time: Optional[datetime] = None
        self.total_posts_processed: int = 0
        self.total_posts_posted: int = 0
        self.load_state()

    def load_state(self):
        """Load bot state from persistent storage."""
        try:
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, 'r') as f:
                    data = json.load(f)
                    self.processed_posts = set(data.get('processed_posts', []))
                    self.total_posts_processed = data.get('total_posts_processed', 0)
                    self.total_posts_posted = data.get('total_posts_posted', 0)
                    if data.get('last_run_time'):
                        self.last_run_time = datetime.fromisoformat(data['last_run_time'])
                    if data.get('next_run_time'):
                        self.next_run_time = datetime.fromisoformat(data['next_run_time'])
                logger.info(f"Loaded state: {len(self.processed_posts)} processed posts, "
                            f"{self.total_posts_processed} total processed, {self.total_posts_posted} posted")
        except Exception as e:
            logger.warning(f"Failed to load state: {e}")

    def save_state(self):
        """Save bot state to persistent storage."""
        try:
            data = {
                'processed_posts': list(self.processed_posts),
                'total_posts_processed': self.total_posts_processed,
                'total_posts_posted': self.total_posts_posted,
                'last_run_time': self.last_run_time.isoformat() if self.last_run_time else None,
                'next_run_time': self.next_run_time.isoformat() if self.next_run_time else None
            }
            with open(STATE_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug("State saved successfully")
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def mark_post_processed(self, post_id: str, posted: bool = False):
        """Mark a post as processed and optionally posted."""
        self.processed_posts.add(post_id)
        self.total_posts_processed += 1
        if posted:
            self.total_posts_posted += 1
        self.save_state()

    def is_post_processed(self, post_id: str) -> bool:
        """Check if a post has already been processed."""
        return post_id in self.processed_posts


# Global state instance
bot_state = BotState()

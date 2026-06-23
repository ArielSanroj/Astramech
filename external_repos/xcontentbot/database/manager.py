#!/usr/bin/env python3
"""
Database manager for xcontentbot.
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from .models import Base, ProcessedPost, BotRun, Metrics

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database operations."""

    def __init__(self, db_url: str = None):
        """Initialize database manager."""
        if db_url is None:
            db_url = os.getenv("DATABASE_URL", "sqlite:///xcontentbot.db")

        self.db_url = db_url
        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
        logger.info(f"Database initialized: {db_url}")

    def get_session(self) -> Session:
        """Get database session."""
        return self.SessionLocal()

    def record_processed_post(
        self,
        post_id: str,
        url: str,
        query: str,
        status: str,
        comment: str = None,
        posted: bool = False,
        error_message: str = None,
        author: str = None,
        text_preview: str = None
    ):
        """Record a processed post."""
        session = self.get_session()
        try:
            post = ProcessedPost(
                id=post_id,
                url=url,
                query=query,
                status=status,
                comment=comment,
                posted=posted,
                error_message=error_message,
                author=author,
                text_preview=text_preview
            )
            session.add(post)
            session.commit()
            logger.debug(f"Recorded processed post: {post_id}")
        except SQLAlchemyError as e:
            logger.error(f"Failed to record processed post {post_id}: {e}")
            session.rollback()
        finally:
            session.close()

    def start_bot_run(self, queries: List[str] = None) -> Optional[int]:
        """Start a new bot run."""
        session = self.get_session()
        try:
            bot_run = BotRun(
                queries=json.dumps(queries) if queries else None
            )
            session.add(bot_run)
            session.commit()
            run_id = bot_run.id
            logger.info(f"Started bot run: {run_id}")
            return run_id
        except SQLAlchemyError as e:
            logger.error(f"Failed to start bot run: {e}")
            session.rollback()
            return None
        finally:
            session.close()

    def complete_bot_run(
        self,
        run_id: int,
        posts_processed: int,
        posts_posted: int,
        errors: int
    ):
        """Complete a bot run."""
        session = self.get_session()
        try:
            bot_run = session.query(BotRun).filter(BotRun.id == run_id).first()
            if bot_run:
                self._update_bot_run(
                    bot_run, posts_processed, posts_posted, errors
                )
                session.commit()
                logger.info(
                    f"Completed bot run {run_id}: "
                    f"{posts_processed} processed, "
                    f"{posts_posted} posted, {errors} errors"
                )
        except SQLAlchemyError as e:
            logger.error(f"Failed to complete bot run {run_id}: {e}")
            session.rollback()
        finally:
            session.close()

    def _update_bot_run(
        self,
        bot_run: BotRun,
        posts_processed: int,
        posts_posted: int,
        errors: int
    ):
        """Update bot run with completion data."""
        bot_run.completed_at = datetime.utcnow()
        bot_run.posts_processed = posts_processed
        bot_run.posts_posted = posts_posted
        bot_run.errors = errors
        bot_run.duration = (
            bot_run.completed_at - bot_run.started_at
        ).total_seconds()

    def get_processed_posts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recently processed posts."""
        session = self.get_session()
        try:
            posts = session.query(ProcessedPost).order_by(
                ProcessedPost.processed_at.desc()
            ).limit(limit).all()
            return [self._post_to_dict(post) for post in posts]
        except SQLAlchemyError as e:
            logger.error(f"Failed to get processed posts: {e}")
            return []
        finally:
            session.close()

    def _post_to_dict(self, post: ProcessedPost) -> Dict[str, Any]:
        """Convert ProcessedPost to dictionary."""
        return {
            "id": post.id,
            "url": post.url,
            "query": post.query,
            "status": post.status,
            "comment": post.comment,
            "posted": post.posted,
            "processed_at": post.processed_at.isoformat(),
            "author": post.author,
            "text_preview": post.text_preview
        }

    def get_bot_runs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent bot runs."""
        session = self.get_session()
        try:
            runs = session.query(BotRun).order_by(
                BotRun.started_at.desc()
            ).limit(limit).all()
            return [self._run_to_dict(run) for run in runs]
        except SQLAlchemyError as e:
            logger.error(f"Failed to get bot runs: {e}")
            return []
        finally:
            session.close()

    def _run_to_dict(self, run: BotRun) -> Dict[str, Any]:
        """Convert BotRun to dictionary."""
        return {
            "id": run.id,
            "started_at": run.started_at.isoformat(),
            "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            "posts_processed": run.posts_processed,
            "posts_posted": run.posts_posted,
            "errors": run.errors,
            "duration": run.duration,
            "queries": run.queries
        }

    def record_metric(
        self,
        name: str,
        value: float,
        tags: Dict[str, str] = None
    ):
        """Record a metric."""
        session = self.get_session()
        try:
            metric = Metrics(
                metric_name=name,
                metric_value=value,
                tags=json.dumps(tags) if tags else None
            )
            session.add(metric)
            session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Failed to record metric {name}: {e}")
            session.rollback()
        finally:
            session.close()

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        session = self.get_session()
        try:
            return self._build_metrics_summary(session)
        except SQLAlchemyError as e:
            logger.error(f"Failed to get metrics summary: {e}")
            return {}
        finally:
            session.close()

    def _build_metrics_summary(self, session: Session) -> Dict[str, Any]:
        """Build metrics summary from database."""
        total_posts = session.query(ProcessedPost).count()
        posted_posts = session.query(ProcessedPost).filter(
            ProcessedPost.posted == True
        ).count()

        recent_runs = session.query(BotRun).filter(
            BotRun.completed_at.isnot(None)
        ).order_by(BotRun.completed_at.desc()).limit(10).all()

        return {
            "total_posts_processed": total_posts,
            "total_posts_posted": posted_posts,
            "success_rate": posted_posts / max(total_posts, 1),
            "recent_runs": len(recent_runs),
            "last_run": recent_runs[0].completed_at.isoformat() if recent_runs else None
        }

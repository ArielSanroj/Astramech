#!/usr/bin/env python3
"""
Database models for xcontentbot.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Boolean,
    Text,
    Float
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ProcessedPost(Base):
    """Model for processed posts."""
    __tablename__ = 'processed_posts'

    id = Column(String, primary_key=True)
    url = Column(String, nullable=False)
    query = Column(String, nullable=False)
    status = Column(String, nullable=False)  # posted, preview, error, skipped
    comment = Column(Text)
    processed_at = Column(DateTime, default=datetime.utcnow)
    posted = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    author = Column(String, nullable=True)
    text_preview = Column(Text, nullable=True)


class BotRun(Base):
    """Model for bot execution runs."""
    __tablename__ = 'bot_runs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    posts_processed = Column(Integer, default=0)
    posts_posted = Column(Integer, default=0)
    errors = Column(Integer, default=0)
    duration = Column(Float, nullable=True)
    queries = Column(Text, nullable=True)  # JSON string of queries used


class Metrics(Base):
    """Model for storing metrics data."""
    __tablename__ = 'metrics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metric_name = Column(String, nullable=False)
    metric_value = Column(Float, nullable=False)
    tags = Column(Text, nullable=True)  # JSON string of tags

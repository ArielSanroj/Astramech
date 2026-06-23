#!/usr/bin/env python3
"""
Tests for database functionality.
"""

import pytest
import os
import tempfile
from database import DatabaseManager, ProcessedPost, BotRun, Metrics, record_post, start_run, complete_run


class TestDatabaseManager:
    """Test database manager functionality."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        db_manager = DatabaseManager(f"sqlite:///{db_path}")
        yield db_manager
        
        # Cleanup
        os.unlink(db_path)
    
    def test_record_processed_post(self, temp_db):
        """Test recording processed post."""
        temp_db.record_processed_post(
            post_id="123",
            url="https://x.com/user/status/123",
            query="test query",
            status="posted",
            comment="Test comment",
            posted=True,
            author="testuser",
            text_preview="Test post text"
        )
        
        posts = temp_db.get_processed_posts(limit=1)
        assert len(posts) == 1
        assert posts[0]["id"] == "123"
        assert posts[0]["url"] == "https://x.com/user/status/123"
        assert posts[0]["status"] == "posted"
        assert posts[0]["posted"] is True
    
    def test_bot_run_lifecycle(self, temp_db):
        """Test bot run lifecycle."""
        # Start run
        run_id = temp_db.start_bot_run(["query1", "query2"])
        assert run_id is not None
        
        # Complete run
        temp_db.complete_bot_run(run_id, posts_processed=5, posts_posted=3, errors=1)
        
        # Check run was recorded
        runs = temp_db.get_bot_runs(limit=1)
        assert len(runs) == 1
        assert runs[0]["id"] == run_id
        assert runs[0]["posts_processed"] == 5
        assert runs[0]["posts_posted"] == 3
        assert runs[0]["errors"] == 1
        assert runs[0]["completed_at"] is not None
    
    def test_metrics_recording(self, temp_db):
        """Test metrics recording."""
        temp_db.record_metric("test_metric", 42.5, {"tag1": "value1"})
        
        # Check metric was recorded
        summary = temp_db.get_metrics_summary()
        assert "total_posts_processed" in summary
    
    def test_get_processed_posts(self, temp_db):
        """Test getting processed posts."""
        # Add multiple posts
        for i in range(5):
            temp_db.record_processed_post(
                post_id=f"post_{i}",
                url=f"https://x.com/user/status/{i}",
                query="test",
                status="posted" if i % 2 == 0 else "error"
            )
        
        posts = temp_db.get_processed_posts(limit=3)
        assert len(posts) == 3
        assert all("id" in post for post in posts)
        assert all("url" in post for post in posts)
    
    def test_get_bot_runs(self, temp_db):
        """Test getting bot runs."""
        # Add multiple runs
        for i in range(3):
            run_id = temp_db.start_bot_run([f"query_{i}"])
            temp_db.complete_bot_run(run_id, i+1, i, 0)
        
        runs = temp_db.get_bot_runs(limit=2)
        assert len(runs) == 2
        assert all("id" in run for run in runs)
        assert all("started_at" in run for run in runs)
    
    def test_metrics_summary(self, temp_db):
        """Test metrics summary."""
        # Add some data
        temp_db.record_processed_post("1", "url1", "query1", "posted", posted=True)
        temp_db.record_processed_post("2", "url2", "query2", "error", posted=False)
        
        run_id = temp_db.start_bot_run(["query1"])
        temp_db.complete_bot_run(run_id, 2, 1, 1)
        
        summary = temp_db.get_metrics_summary()
        assert summary["total_posts_processed"] == 2
        assert summary["total_posts_posted"] == 1
        assert summary["success_rate"] == 0.5
        assert summary["recent_runs"] == 1


class TestGlobalDatabaseFunctions:
    """Test global database functions."""
    
    @pytest.fixture
    def temp_db_global(self):
        """Create temporary database for global function testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        # Set environment variable for global functions
        os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
        
        # Import after setting env var to use temp DB
        from database import db_manager
        yield db_manager
        
        # Cleanup
        os.unlink(db_path)
        if "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]
    
    def test_record_post_function(self, temp_db_global):
        """Test record_post function."""
        record_post(
            post_id="123",
            url="https://x.com/user/status/123",
            query="test",
            status="posted",
            comment="Test comment",
            posted=True
        )
        
        posts = temp_db_global.get_processed_posts(limit=1)
        assert len(posts) == 1
        assert posts[0]["id"] == "123"
    
    def test_start_run_function(self, temp_db_global):
        """Test start_run function."""
        run_id = start_run(["query1", "query2"])
        assert run_id is not None
        
        runs = temp_db_global.get_bot_runs(limit=1)
        assert len(runs) == 1
        assert runs[0]["id"] == run_id
    
    def test_complete_run_function(self, temp_db_global):
        """Test complete_run function."""
        run_id = start_run(["query1"])
        complete_run(run_id, posts_processed=5, posts_posted=3, errors=1)
        
        runs = temp_db_global.get_bot_runs(limit=1)
        assert runs[0]["posts_processed"] == 5
        assert runs[0]["posts_posted"] == 3
        assert runs[0]["errors"] == 1
    
    def test_get_recent_posts_function(self, temp_db_global):
        """Test get_recent_posts function."""
        from database import get_recent_posts
        
        # Add some posts
        for i in range(3):
            record_post(f"post_{i}", f"url_{i}", "test", "posted")
        
        posts = get_recent_posts(limit=2)
        assert len(posts) == 2
        assert all("id" in post for post in posts)
    
    def test_get_recent_runs_function(self, temp_db_global):
        """Test get_recent_runs function."""
        from database import get_recent_runs
        
        # Add some runs
        for i in range(3):
            run_id = start_run([f"query_{i}"])
            complete_run(run_id, i+1, i, 0)
        
        runs = get_recent_runs(limit=2)
        assert len(runs) == 2
        assert all("id" in run for run in runs)
    
    def test_get_summary_function(self, temp_db_global):
        """Test get_summary function."""
        from database import get_summary
        
        # Add some data
        record_post("1", "url1", "query1", "posted", posted=True)
        record_post("2", "url2", "query2", "error", posted=False)
        
        summary = get_summary()
        assert "total_posts_processed" in summary
        assert "total_posts_posted" in summary
        assert "success_rate" in summary


class TestDatabaseModels:
    """Test database models."""
    
    def test_processed_post_model(self):
        """Test ProcessedPost model."""
        post = ProcessedPost(
            id="123",
            url="https://x.com/user/status/123",
            query="test",
            status="posted",
            comment="Test comment",
            posted=True,
            author="testuser"
        )
        
        assert post.id == "123"
        assert post.url == "https://x.com/user/status/123"
        assert post.status == "posted"
        assert post.posted is True
        assert post.author == "testuser"
    
    def test_bot_run_model(self):
        """Test BotRun model."""
        from datetime import datetime
        
        run = BotRun(
            posts_processed=5,
            posts_posted=3,
            errors=1,
            duration=120.5
        )
        
        assert run.posts_processed == 5
        assert run.posts_posted == 3
        assert run.errors == 1
        assert run.duration == 120.5
        assert run.started_at is not None
    
    def test_metrics_model(self):
        """Test Metrics model."""
        metric = Metrics(
            metric_name="test_metric",
            metric_value=42.5,
            tags='{"tag1": "value1"}'
        )
        
        assert metric.metric_name == "test_metric"
        assert metric.metric_value == 42.5
        assert metric.tags == '{"tag1": "value1"}'
        assert metric.timestamp is not None

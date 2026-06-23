#!/usr/bin/env python3
"""
Tests for configuration management system.
"""

import pytest
import os
import tempfile
from pathlib import Path
from config_manager import ConfigurationManager, LLMProviderConfig


class TestConfigurationManager:
    """Test configuration manager functionality."""
    
    def test_load_defaults(self):
        """Test loading default configuration."""
        config = ConfigurationManager("non_existent_file.yaml")
        assert config.get("app.queries") is not None
        assert isinstance(config.get("app.queries"), list)
        assert len(config.get("app.queries")) > 0
    
    def test_env_override(self, monkeypatch):
        """Test environment variable override."""
        monkeypatch.setenv("QUERIES", "test1,test2")
        config = ConfigurationManager()
        queries = config.get("app.queries")
        assert "test1" in queries
        assert "test2" in queries
    
    def test_llm_provider_config(self):
        """Test LLM provider configuration."""
        config = ConfigurationManager()
        provider = config.get_llm_provider("openai")
        assert isinstance(provider, LLMProviderConfig)
        assert provider.name == "openai"
        assert provider.model is not None
    
    def test_config_file_loading(self, temp_dir):
        """Test loading configuration from file."""
        config_file = temp_dir / "test_config.yaml"
        
        test_config = {
            "app": {
                "queries": ["test query"],
                "limit": 5
            },
            "llm": {
                "default_provider": "openai"
            }
        }
        
        import yaml
        with open(config_file, 'w') as f:
            yaml.dump(test_config, f)
        
        config = ConfigurationManager(str(config_file))
        assert config.get("app.queries") == ["test query"]
        assert config.get("app.limit") == 5
    
    def test_config_set_and_get(self):
        """Test setting and getting configuration values."""
        config = ConfigurationManager()
        
        # Test setting a value
        config.set("app.test_setting", "test_value")
        assert config.get("app.test_setting") == "test_value"
        
        # Test nested setting
        config.set("llm.providers.test.model", "test-model")
        assert config.get("llm.providers.test.model") == "test-model"
    
    def test_config_summary(self):
        """Test configuration summary."""
        config = ConfigurationManager()
        summary = config.get_config_summary()
        
        assert "config" in summary
        assert "sources" in summary
        assert "timestamp" in summary
        assert isinstance(summary["config"], dict)
        assert isinstance(summary["sources"], dict)
    
    def test_llm_provider_validation(self):
        """Test LLM provider configuration validation."""
        config = ConfigurationManager()
        
        # Test getting available providers
        providers = config.get_available_llm_providers()
        assert isinstance(providers, list)
        assert len(providers) > 0
        
        # Test getting specific provider
        provider = config.get_llm_provider("openai")
        assert provider.name == "openai"
        assert provider.api_key_env is not None
    
    def test_config_watchers(self):
        """Test configuration change watchers."""
        config = ConfigurationManager()
        changes = []
        
        def watcher(path, value, source):
            changes.append((path, value, source))
        
        config.add_watcher(watcher)
        
        # Set a value to trigger watcher
        config.set("app.test", "value")
        
        # Check if watcher was called
        assert len(changes) > 0
        assert changes[0][0] == "app.test"
        assert changes[0][1] == "value"
        
        # Remove watcher
        config.remove_watcher(watcher)
        
        # Set another value
        config.set("app.test2", "value2")
        
        # Should not have triggered watcher again
        assert len(changes) == 1
    
    def test_nested_config_access(self):
        """Test nested configuration access."""
        config = ConfigurationManager()
        
        # Test getting nested values
        queries = config.get("app.queries")
        assert isinstance(queries, list)
        
        # Test getting non-existent nested value
        non_existent = config.get("app.non_existent", "default")
        assert non_existent == "default"
    
    def test_config_reload(self):
        """Test configuration reload."""
        config = ConfigurationManager()
        
        # Get initial value
        initial_queries = config.get("app.queries")
        
        # Reload configuration
        config.reload()
        
        # Should still have the same structure
        reloaded_queries = config.get("app.queries")
        assert isinstance(reloaded_queries, list)
        assert len(reloaded_queries) > 0

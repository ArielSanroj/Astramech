#!/usr/bin/env python3
"""
Tests for security features and URL validation.
"""

import pytest
from x_mcp import validate_x_url


class TestSecurity:
    """Test security features."""
    
    def test_reject_linkedin_urls(self):
        """Test that LinkedIn URLs are rejected."""
        assert not validate_x_url("https://linkedin.com/in/someone")
        assert not validate_x_url("urn:li:activity:123")
        assert not validate_x_url("https://www.linkedin.com/feed/")
        assert not validate_x_url("https://linkedin.com/posts/123")
    
    def test_accept_valid_x_urls(self):
        """Test that valid X/Twitter URLs are accepted."""
        assert validate_x_url("https://x.com/user/status/123")
        assert validate_x_url("https://twitter.com/user/status/456")
        assert validate_x_url("https://x.com/i/status/789")
        assert validate_x_url("https://www.x.com/user/status/101112")
    
    def test_reject_malformed_urls(self):
        """Test that malformed URLs are rejected."""
        assert not validate_x_url("")
        assert not validate_x_url("not-a-url")
        assert not validate_x_url("https://example.com/status/123")
        assert not validate_x_url("https://facebook.com/user/status/123")
        assert not validate_x_url("ftp://x.com/status/123")
    
    def test_reject_urls_without_status(self):
        """Test that URLs without /status/ are rejected."""
        assert not validate_x_url("https://x.com/user")
        assert not validate_x_url("https://x.com/user/followers")
        assert not validate_x_url("https://x.com/settings")
        assert not validate_x_url("https://x.com/explore")
    
    def test_case_insensitive_validation(self):
        """Test that validation is case insensitive."""
        assert validate_x_url("https://X.COM/user/status/123")
        assert validate_x_url("https://TWITTER.COM/user/status/456")
        assert not validate_x_url("https://LINKEDIN.COM/in/someone")
    
    def test_url_with_parameters(self):
        """Test URLs with query parameters."""
        assert validate_x_url("https://x.com/user/status/123?s=20")
        assert validate_x_url("https://x.com/user/status/456?ref_src=twsrc")
        assert not validate_x_url("https://linkedin.com/in/someone?trk=profile")
    
    def test_url_with_fragments(self):
        """Test URLs with fragments."""
        assert validate_x_url("https://x.com/user/status/123#section")
        assert validate_x_url("https://x.com/user/status/456#top")
    
    def test_edge_cases(self):
        """Test edge cases for URL validation."""
        # Empty or None
        assert not validate_x_url(None)
        assert not validate_x_url("")
        assert not validate_x_url("   ")
        
        # Just domain
        assert not validate_x_url("https://x.com")
        assert not validate_x_url("https://twitter.com")
        
        # Invalid protocols
        assert not validate_x_url("http://x.com/user/status/123")  # Should be https
        assert not validate_x_url("ftp://x.com/user/status/123")
        
        # Subdomain variations
        assert validate_x_url("https://mobile.x.com/user/status/123")
        assert validate_x_url("https://api.x.com/user/status/123")
    
    def test_linkedin_injection_attempts(self):
        """Test various LinkedIn injection attempts."""
        # Direct LinkedIn URLs
        assert not validate_x_url("https://linkedin.com/in/someone")
        assert not validate_x_url("https://www.linkedin.com/feed/")
        
        # LinkedIn URNs
        assert not validate_x_url("urn:li:activity:123456")
        assert not validate_x_url("urn:li:share:789012")
        
        # Mixed content (should reject)
        assert not validate_x_url("https://x.com/user/status/123?linkedin=true")
        assert not validate_x_url("https://x.com/user/status/123#linkedin")
        
        # Case variations
        assert not validate_x_url("https://LINKEDIN.COM/in/someone")
        assert not validate_x_url("https://LinkedIn.com/in/someone")
    
    def test_valid_x_variations(self):
        """Test various valid X/Twitter URL formats."""
        # Standard formats
        assert validate_x_url("https://x.com/username/status/123456789")
        assert validate_x_url("https://twitter.com/username/status/123456789")
        
        # i/status format
        assert validate_x_url("https://x.com/i/status/123456789")
        assert validate_x_url("https://twitter.com/i/status/123456789")
        
        # With www
        assert validate_x_url("https://www.x.com/username/status/123456789")
        assert validate_x_url("https://www.twitter.com/username/status/123456789")
        
        # Mobile subdomain
        assert validate_x_url("https://mobile.x.com/username/status/123456789")
        assert validate_x_url("https://mobile.twitter.com/username/status/123456789")
    
    def test_numeric_status_ids(self):
        """Test that status IDs are properly extracted."""
        from x_mcp import extract_status_id
        
        assert extract_status_id("https://x.com/user/status/123456789") == "123456789"
        assert extract_status_id("https://twitter.com/user/status/987654321") == "987654321"
        assert extract_status_id("https://x.com/i/status/555666777") == "555666777"
        assert extract_status_id("invalid-url") == ""
        assert extract_status_id("") == ""
    
    def test_url_sanitization(self):
        """Test URL sanitization in submit_comment."""
        # This would be tested in integration tests with actual MCP calls
        # For now, we test the validation function
        test_urls = [
            "https://x.com/user/status/123",
            "https://twitter.com/user/status/456",
            "https://linkedin.com/in/someone",  # Should be rejected
            "https://facebook.com/user/status/789",  # Should be rejected
        ]
        
        valid_urls = [url for url in test_urls if validate_x_url(url)]
        assert len(valid_urls) == 2  # Only X/Twitter URLs should be valid
        assert all("x.com" in url or "twitter.com" in url for url in valid_urls)

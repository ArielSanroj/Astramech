"""Structured logging utilities."""
import re
import json
import logging
from datetime import datetime


class SensitiveDataFilter(logging.Filter):
    """Filter sensitive data from logs."""

    SENSITIVE_PATTERNS = [
        (r'(password["\']?\s*[:=]\s*["\'])([^"\']+)', r'\1***REDACTED***'),
        (r'(api[_-]?key["\']?\s*[:=]\s*["\'])([^"\']+)', r'\1***REDACTED***'),
        (r'(sk-[a-zA-Z0-9]{20,})', r'sk-***REDACTED***'),
        (r'(sk-ant-[a-zA-Z0-9]{20,})', r'sk-ant-***REDACTED***'),
    ]

    def filter(self, record):
        message = record.getMessage()
        for pattern, replacement in self.SENSITIVE_PATTERNS:
            message = re.sub(pattern, replacement, message, flags=re.IGNORECASE)
        record.msg = message
        return True


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, default=str)

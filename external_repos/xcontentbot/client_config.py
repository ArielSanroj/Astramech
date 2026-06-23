"""Configuration loading and defaults for X Content Bot Client."""
import os
import json
import asyncio
import logging
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Tuple
from dotenv import load_dotenv

load_dotenv()

CONFIG_PATH = os.getenv("CONFIG_FILE", "bot_config.yaml")

DEFAULT_CONFIG: Dict[str, Any] = {
    "app": {
        "mcp_server_url": "http://127.0.0.1:8000/mcp",
        "log_level": "INFO",
        "queries": ["burnout", "employee well-being", "productivity"],
        "limit": 10,
        "max_posts_to_process": 3,
        "auto": False,
        "concurrency": {"max_concurrent_posts": 2},
        "scheduler": {
            "enable": False,
            "run_on_startup": False,
            "timezone": "Europe/Madrid",
            "cron": "0 8 * * *"
        }
    },
    "retry": {
        "max_retries": 3,
        "base_delay": 1.0,
        "max_delay": 60.0,
        "exponential_base": 2.0,
        "jitter": 0.1
    },
    "llm": {
        "refine": False,
        "provider": "openai",
        "model": "gpt-4o-mini",
        "system_prompt": "Refine to warm, professional, under 280 chars. Avoid hard-sell.",
        "max_tokens": 120,
        "temperature": 0.4,
        "openai": {"api_key_env": "OPENAI_API_KEY"},
        "anthropic": {"api_key_env": "ANTHROPIC_API_KEY", "model": "claude-3-haiku-20240307"}
    },
    "state": {"state_file": "bot_state.json"}
}


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries recursively."""
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            base[key] = _deep_merge(base[key], value)
        else:
            base[key] = value
    return base


def _load_config_file(path: Path) -> Tuple[Dict[str, Any], List[str]]:
    """Load configuration from YAML or JSON file."""
    warnings: List[str] = []
    if not path.exists():
        return deepcopy(DEFAULT_CONFIG), warnings

    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        warnings.append(f"Failed to read config file '{path}': {e}")
        return deepcopy(DEFAULT_CONFIG), warnings

    if not content.strip():
        warnings.append(f"Config file '{path}' is empty; using defaults")
        return deepcopy(DEFAULT_CONFIG), warnings

    data: Dict[str, Any] = {}
    try:
        import yaml
        data_obj = yaml.safe_load(content)
        if isinstance(data_obj, dict):
            data = data_obj
        else:
            warnings.append(f"Config file '{path}' did not parse to a dictionary; using defaults")
    except ImportError:
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            warnings.append(f"Failed to parse config file '{path}' as JSON: {e}")
    except Exception as e:
        warnings.append(f"Failed to parse config file '{path}' as YAML: {e}")

    config = deepcopy(DEFAULT_CONFIG)
    if data:
        config = _deep_merge(config, data)
    return config, warnings


# Load config
CONFIG, CONFIG_WARNINGS = _load_config_file(Path(CONFIG_PATH))

# Extract settings from config and environment
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", CONFIG["app"].get("mcp_server_url", "http://127.0.0.1:8000/mcp"))
LOG_LEVEL = os.getenv("LOG_LEVEL", CONFIG["app"].get("log_level", "INFO")).upper()

env_queries = os.getenv("QUERIES")
if env_queries:
    QUERIES = [q.strip() for q in env_queries.split(",") if q.strip()]
else:
    QUERIES = [str(q).strip() for q in CONFIG["app"].get("queries", []) if str(q).strip()]

LIMIT = int(os.getenv("LIMIT", str(CONFIG["app"].get("limit", 10))))
MAX_POSTS_TO_PROCESS = int(os.getenv("MAX_POSTS_TO_PROCESS", str(CONFIG["app"].get("max_posts_to_process", 3))))
AUTO = os.getenv("AUTO", str(CONFIG["app"].get("auto", False))).lower() == "true"

# Scheduler settings
scheduler_config = CONFIG["app"].get("scheduler", {})
ENABLE_SCHEDULER = os.getenv("ENABLE_SCHEDULER", str(scheduler_config.get("enable", False))).lower() == "true"
RUN_ON_STARTUP = os.getenv("RUN_ON_STARTUP", str(scheduler_config.get("run_on_startup", False))).lower() == "true"
SCHEDULE_TZ = os.getenv("SCHEDULE_TZ", scheduler_config.get("timezone", "Europe/Madrid"))
SCHEDULE_CRON = os.getenv("SCHEDULE_CRON", scheduler_config.get("cron", "0 8 * * *"))

# Concurrency settings
max_concurrency = CONFIG["app"].get("concurrency", {}).get("max_concurrent_posts", 2)
MAX_CONCURRENT_POSTS = int(os.getenv("MAX_CONCURRENT_POSTS", str(max_concurrency)))
POST_PROCESSING_SEMAPHORE = asyncio.Semaphore(MAX_CONCURRENT_POSTS)

# Retry configuration
retry_defaults = CONFIG.get("retry", {})
RETRY_CONFIG = {
    "max_retries": int(os.getenv("MAX_RETRIES", str(retry_defaults.get("max_retries", 3)))),
    "base_delay": float(os.getenv("BASE_DELAY", str(retry_defaults.get("base_delay", 1.0)))),
    "max_delay": float(os.getenv("MAX_DELAY", str(retry_defaults.get("max_delay", 60.0)))),
    "exponential_base": float(os.getenv("EXPONENTIAL_BASE", str(retry_defaults.get("exponential_base", 2.0)))),
    "jitter": float(os.getenv("RETRY_JITTER", str(retry_defaults.get("jitter", 0.1))))
}

# State file
state_defaults = CONFIG.get("state", {})
STATE_FILE = os.getenv("STATE_FILE", state_defaults.get("state_file", "bot_state.json"))

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("x-mcp-client")

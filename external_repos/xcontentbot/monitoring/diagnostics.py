"""System diagnostics functions."""
import os
import sys
import time
import socket
import psutil
from typing import Dict, Any


def get_system_diagnostics() -> Dict[str, Any]:
    """Get system diagnostics."""
    try:
        process = psutil.Process()
        return {
            "process_id": process.pid,
            "memory_info": process.memory_info()._asdict(),
            "cpu_percent": process.cpu_percent(),
            "num_threads": process.num_threads(),
            "create_time": process.create_time(),
            "open_files": len(process.open_files()) if hasattr(process, 'open_files') else 0,
            "connections": len(process.connections()) if hasattr(process, 'connections') else 0
        }
    except Exception as e:
        return {"error": str(e)}


def get_application_diagnostics(start_time: float) -> Dict[str, Any]:
    """Get application diagnostics."""
    return {
        "uptime": time.time() - start_time,
        "python_version": sys.version,
        "working_directory": os.getcwd(),
        "environment_variables": {
            k: v for k, v in os.environ.items()
            if k.startswith(('X_', 'LLM_', 'LOG_', 'MCP_'))
        }
    }


async def get_network_diagnostics(port: int) -> Dict[str, Any]:
    """Get network diagnostics."""
    try:
        return {
            "hostname": socket.gethostname(),
            "local_ip": socket.gethostbyname(socket.gethostname()),
            "port": port
        }
    except Exception as e:
        return {"error": str(e)}


def get_dependency_diagnostics() -> Dict[str, Any]:
    """Get dependency diagnostics."""
    dependencies = {}

    try:
        import playwright
        dependencies["playwright"] = playwright.__version__
    except ImportError:
        dependencies["playwright"] = "not installed"

    try:
        import openai
        dependencies["openai"] = openai.__version__
    except ImportError:
        dependencies["openai"] = "not installed"

    try:
        import anthropic
        dependencies["anthropic"] = anthropic.__version__
    except ImportError:
        dependencies["anthropic"] = "not installed"

    return dependencies

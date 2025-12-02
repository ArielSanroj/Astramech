from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AgentCapability:
    name: str
    description: str
    inputs: List[str]
    outputs: List[str]


@dataclass
class AgentRunRequest:
    payload: Dict[str, Any]
    credentials: Dict[str, Any] = field(default_factory=dict)
    options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentRunResult:
    success: bool
    output: Dict[str, Any]
    message: str = ""
    logs: List[str] = field(default_factory=list)


class ExternalAgentAdapter(ABC):
    """Base contract all external agent adapters must follow."""

    name: str
    domain: str
    source_repo: str
    local_repo_path: str

    @abstractmethod
    def capabilities(self) -> List[AgentCapability]:
        ...

    @abstractmethod
    def required_credentials(self) -> List[str]:
        ...

    @abstractmethod
    def run(self, request: AgentRunRequest) -> AgentRunResult:
        ...

    def healthcheck(self) -> AgentRunResult:
        return AgentRunResult(success=False, output={}, message="Healthcheck not implemented")


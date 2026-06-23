"""Core hybrid memory system implementation."""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

try:
    from pinecone import Pinecone, ServerlessSpec
except Exception:  # noqa: F401
    Pinecone = None
    ServerlessSpec = None

try:
    from langchain_ollama import OllamaEmbeddings
except Exception:  # noqa: F401
    OllamaEmbeddings = None

load_dotenv()


class HybridMemorySystem:
    """Hybrid memory system combining short-term and Pinecone long-term memory."""

    def __init__(self):
        try:
            if Pinecone is None:
                raise RuntimeError("Pinecone SDK not available")
            self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
            self.index_name = "company-efficiency-memory-4096"
            if OllamaEmbeddings is not None:
                self.embeddings = OllamaEmbeddings(
                    model="llama3.1:8b",
                    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                )
            else:
                self.embeddings = None

            self._setup_index()
        except Exception as exc:
            print(f"⚠️ Memory system initialization failed: {exc}")
            print("   Continuing without long-term memory...")
            self.pc = None
            self.index = None

    def _setup_index(self) -> None:
        if not self.pc:
            self.index = None
            return

        try:
            existing_indexes = self.pc.list_indexes()
            if self.index_name not in existing_indexes.names():
                print(f"Creating Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=4096,
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                )

            self.index = self.pc.Index(self.index_name)
            print(f"✅ Connected to Pinecone index: {self.index_name}")
        except Exception as exc:
            print(f"❌ Error setting up Pinecone index: {exc}")
            self.index = None

    def store_memory(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        if not self.index:
            print("⚠️ Pinecone index not available, skipping memory storage")
            return None

        try:
            memory_id = str(uuid.uuid4())

            if self.embeddings is not None:
                embedding = self.embeddings.embed_query(text)
            else:
                embedding = [0.0] * 4096

            if metadata is None:
                metadata = {}

            metadata.update(
                {
                    "timestamp": datetime.now().isoformat(),
                    "text_length": len(text),
                    "type": metadata.get("type", "general"),
                }
            )

            self.index.upsert(
                vectors=[
                    {
                        "id": memory_id,
                        "values": embedding,
                        "metadata": {**metadata, "text": text},
                    }
                ]
            )

            print(f"✅ Stored memory with ID: {memory_id}")
            return memory_id
        except Exception as exc:
            print(f"❌ Error storing memory: {exc}")
            return None

    def retrieve_memory(
        self, query: str, top_k: int = 5, filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        if not self.index:
            print("⚠️ Pinecone index not available, returning empty results")
            return []

        try:
            query_embedding = self.embeddings.embed_query(query)
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_metadata,
            )

            memories: List[Dict[str, Any]] = []
            for match in results["matches"]:
                memories.append(
                    {
                        "id": match["id"],
                        "score": match["score"],
                        "text": match["metadata"].get("text", ""),
                        "metadata": {
                            k: v for k, v in match["metadata"].items() if k != "text"
                        },
                    }
                )

            print(f"✅ Retrieved {len(memories)} relevant memories")
            return memories
        except Exception as exc:
            print(f"❌ Error retrieving memories: {exc}")
            return []

    def store_kpi_data(
        self, kpi_name: str, value: float, period: str, benchmark: Optional[float] = None, status: str = "normal"
    ) -> Optional[str]:
        text = f"KPI: {kpi_name} = {value}% for {period}"
        if benchmark:
            text += f" (Benchmark: {benchmark}%)"

        metadata = {
            "type": "kpi",
            "kpi_name": kpi_name,
            "value": value,
            "period": period,
            "benchmark": benchmark,
            "status": status,
        }

        return self.store_memory(text, metadata)

    def store_inefficiency(
        self, issue_type: str, description: str, severity: str, recommended_agent: str
    ) -> Optional[str]:
        text = f"Inefficiency: {issue_type} - {description}"
        metadata = {
            "type": "inefficiency",
            "issue_type": issue_type,
            "severity": severity,
            "recommended_agent": recommended_agent,
        }
        return self.store_memory(text, metadata)

    def store_analysis_results(self, company_name: str, analysis: Dict[str, Any]) -> Optional[str]:
        if not analysis:
            return None

        company = company_name or "Unknown"
        try:
            summary = json.dumps(analysis, default=str)
        except TypeError:
            summary = str(analysis)

        metadata = {
            "type": "analysis_results",
            "company": company,
            "has_kpi_results": "kpi_results" in analysis,
            "has_diagnostic_results": "diagnostic_results" in analysis,
        }

        return self.store_memory(f"Analysis results for {company}", {**metadata, "raw_results": summary})

    def get_kpi_trends(self, kpi_name: str, periods: int = 4) -> List[Dict[str, Any]]:
        memories = self.retrieve_memory(
            query=f"KPI trends for {kpi_name}",
            filter_metadata={"type": "kpi", "kpi_name": kpi_name},
        )
        sorted_memories = sorted(
            memories, key=lambda x: x["metadata"].get("timestamp", ""), reverse=True
        )
        return sorted_memories[:periods]

    def get_inefficiencies_by_severity(self, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        filter_metadata = {"type": "inefficiency"}
        if severity:
            filter_metadata["severity"] = severity
        return self.retrieve_memory(query="company inefficiencies and issues", filter_metadata=filter_metadata)

    def summarize_patterns(self, query: str = "company performance patterns") -> str:
        memories = self.retrieve_memory(query, top_k=10)
        if not memories:
            return "No patterns found in memory."

        kpi_memories = [m for m in memories if m["metadata"].get("type") == "kpi"]
        inefficiency_memories = [m for m in memories if m["metadata"].get("type") == "inefficiency"]

        summary = "📊 Memory Pattern Summary:\n\n"

        if kpi_memories:
            summary += "📈 KPI Trends:\n"
            for memory in kpi_memories[:3]:
                summary += f"   - {memory['text']}\n"

        if inefficiency_memories:
            summary += "\n⚠️ Identified Issues:\n"
            for memory in inefficiency_memories[:3]:
                summary += f"   - {memory['text']}\n"

        return summary


MemoryManager = HybridMemorySystem

"""
Hybrid Memory System for Company Efficiency Optimizer

This module implements a hybrid memory system using:
- Short-term memory: CrewAI's built-in memory
- Long-term memory: Pinecone vector database with NVIDIA embeddings
"""

import os
import uuid
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_ollama import OllamaEmbeddings
import json
from datetime import datetime

load_dotenv()

class HybridMemorySystem:
    """Hybrid memory system combining CrewAI short-term and Pinecone long-term memory"""
    
    def __init__(self):
        """Initialize the memory system"""
        try:
            self.pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
            self.index_name = 'company-efficiency-memory-4096'
            self.embeddings = OllamaEmbeddings(
                model="llama3.1:8b",
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            )
            
            # Create or get the Pinecone index
            self._setup_index()
        except Exception as e:
            print(f"⚠️ Memory system initialization failed: {str(e)}")
            print("   Continuing without long-term memory...")
            self.pc = None
            self.index = None
    
    def _setup_index(self):
        """Set up the Pinecone index"""
        if not self.pc:
            self.index = None
            return
            
        try:
            # Check if index exists
            existing_indexes = self.pc.list_indexes()
            if self.index_name not in existing_indexes.names():
                print(f"Creating Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=4096,  # Ollama llama3.1:8b embedding dimension
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )
            
            self.index = self.pc.Index(self.index_name)
            print(f"✅ Connected to Pinecone index: {self.index_name}")
            
        except Exception as e:
            print(f"❌ Error setting up Pinecone index: {str(e)}")
            self.index = None
    
    def store_memory(self, text: str, metadata: Dict[str, Any] = None) -> str:
        """
        Store a memory in the long-term vector database
        
        Args:
            text: The text content to store
            metadata: Additional metadata to associate with the memory
            
        Returns:
            str: Unique ID of the stored memory
        """
        if not self.index:
            print("⚠️ Pinecone index not available, skipping memory storage")
            return None
        
        try:
            # Generate unique ID
            memory_id = str(uuid.uuid4())
            
            # Create embedding
            embedding = self.embeddings.embed_query(text)
            
            # Prepare metadata
            if metadata is None:
                metadata = {}
            
            metadata.update({
                'timestamp': datetime.now().isoformat(),
                'text_length': len(text),
                'type': 'general'
            })
            
            # Store in Pinecone
            self.index.upsert(vectors=[{
                "id": memory_id,
                "values": embedding,
                "metadata": {
                    **metadata,
                    'text': text  # Store text in metadata for retrieval
                }
            }])
            
            print(f"✅ Stored memory with ID: {memory_id}")
            return memory_id
            
        except Exception as e:
            print(f"❌ Error storing memory: {str(e)}")
            return None
    
    def retrieve_memory(self, query: str, top_k: int = 5, 
                        filter_metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memories based on query
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of relevant memories with metadata
        """
        if not self.index:
            print("⚠️ Pinecone index not available, returning empty results")
            return []
        
        try:
            # Create query embedding
            query_embedding = self.embeddings.embed_query(query)
            
            # Search Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_metadata
            )
            
            # Format results
            memories = []
            for match in results['matches']:
                memories.append({
                    'id': match['id'],
                    'score': match['score'],
                    'text': match['metadata'].get('text', ''),
                    'metadata': {k: v for k, v in match['metadata'].items() if k != 'text'}
                })
            
            print(f"✅ Retrieved {len(memories)} relevant memories")
            return memories
            
        except Exception as e:
            print(f"❌ Error retrieving memories: {str(e)}")
            return []
    
    def store_kpi_data(self, kpi_name: str, value: float, period: str, 
                       benchmark: float = None, status: str = "normal") -> str:
        """
        Store KPI data with specialized metadata
        
        Args:
            kpi_name: Name of the KPI (e.g., "gross_margin")
            value: Current value
            period: Time period (e.g., "Q3_2024")
            benchmark: Industry benchmark value
            status: Status indicator (normal, warning, critical)
            
        Returns:
            str: Memory ID
        """
        text = f"KPI: {kpi_name} = {value}% for {period}"
        if benchmark:
            text += f" (Benchmark: {benchmark}%)"
        
        metadata = {
            'type': 'kpi',
            'kpi_name': kpi_name,
            'value': value,
            'period': period,
            'benchmark': benchmark,
            'status': status
        }
        
        return self.store_memory(text, metadata)
    
    def store_inefficiency(self, issue_type: str, description: str, 
                          severity: str, recommended_agent: str) -> str:
        """
        Store identified inefficiency with metadata
        
        Args:
            issue_type: Type of inefficiency (e.g., "high_turnover")
            description: Detailed description
            severity: Severity level (low, medium, high, critical)
            recommended_agent: Recommended agent for resolution
            
        Returns:
            str: Memory ID
        """
        text = f"Inefficiency: {issue_type} - {description}"
        
        metadata = {
            'type': 'inefficiency',
            'issue_type': issue_type,
            'severity': severity,
            'recommended_agent': recommended_agent
        }
        
        return self.store_memory(text, metadata)
    
    def get_kpi_trends(self, kpi_name: str, periods: int = 4) -> List[Dict[str, Any]]:
        """
        Retrieve KPI trends over time
        
        Args:
            kpi_name: Name of the KPI to analyze
            periods: Number of periods to retrieve
            
        Returns:
            List of KPI data points
        """
        memories = self.retrieve_memory(
            query=f"KPI trends for {kpi_name}",
            filter_metadata={'type': 'kpi', 'kpi_name': kpi_name}
        )
        
        # Sort by timestamp and return recent periods
        sorted_memories = sorted(memories, 
                               key=lambda x: x['metadata'].get('timestamp', ''), 
                               reverse=True)
        
        return sorted_memories[:periods]
    
    def get_inefficiencies_by_severity(self, severity: str = None) -> List[Dict[str, Any]]:
        """
        Retrieve inefficiencies filtered by severity
        
        Args:
            severity: Severity level to filter by (optional)
            
        Returns:
            List of inefficiency records
        """
        filter_metadata = {'type': 'inefficiency'}
        if severity:
            filter_metadata['severity'] = severity
        
        return self.retrieve_memory(
            query="company inefficiencies and issues",
            filter_metadata=filter_metadata
        )
    
    def summarize_patterns(self, query: str = "company performance patterns") -> str:
        """
        Generate a summary of patterns from stored memories
        
        Args:
            query: Query to search for relevant patterns
            
        Returns:
            str: Summary of patterns
        """
        memories = self.retrieve_memory(query, top_k=10)
        
        if not memories:
            return "No patterns found in memory."
        
        # Group memories by type
        kpi_memories = [m for m in memories if m['metadata'].get('type') == 'kpi']
        inefficiency_memories = [m for m in memories if m['metadata'].get('type') == 'inefficiency']
        
        summary = "📊 Memory Pattern Summary:\n\n"
        
        if kpi_memories:
            summary += "📈 KPI Trends:\n"
            for memory in kpi_memories[:3]:  # Top 3 KPI memories
                summary += f"   - {memory['text']}\n"
        
        if inefficiency_memories:
            summary += "\n⚠️ Identified Issues:\n"
            for memory in inefficiency_memories[:3]:  # Top 3 inefficiency memories
                summary += f"   - {memory['text']}\n"
        
        return summary
    
    def store_analysis_results(self, company_name: str, analysis_data: Dict[str, Any]) -> str:
        """
        Store analysis results in memory system
        
        Args:
            company_name: Name of the company
            analysis_data: Dictionary containing analysis results
            
        Returns:
            str: Memory ID
        """
        try:
            # Create a summary text for storage
            summary_text = f"Analysis results for {company_name}: "
            
            if 'kpi_results' in analysis_data:
                summary_text += "KPI analysis completed. "
            
            if 'diagnostic_results' in analysis_data:
                summary_text += "Diagnostic analysis completed. "
            
            if 'questionnaire' in analysis_data:
                summary_text += f"Questionnaire data for {analysis_data['questionnaire'].get('industry', 'unknown')} industry. "
            
            # Store in memory
            memory_id = self.store_memory(summary_text, {
                'company_name': company_name,
                'analysis_type': 'efficiency_analysis',
                'timestamp': datetime.now().isoformat(),
                'data_keys': list(analysis_data.keys())
            })
            
            print(f"✅ Stored analysis results for {company_name}")
            return memory_id
            
        except Exception as e:
            print(f"❌ Error storing analysis results: {str(e)}")
            return None

# Global memory instance
memory_system = HybridMemorySystem()

# Alias for backward compatibility
MemoryManager = HybridMemorySystem

def get_memory_system() -> HybridMemorySystem:
    """Get the global memory system instance"""
    return memory_system
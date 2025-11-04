"""
Dynamic benchmarks by industry and company size
"""

from typing import Dict, Any, Optional
import yaml
import os


class BenchmarkManager:
    """Manager for industry and company size benchmarks"""
    
    def __init__(self, benchmarks_file: Optional[str] = None):
        """
        Initialize benchmark manager
        
        Args:
            benchmarks_file: Path to YAML file with benchmarks (optional)
        """
        self.benchmarks_file = benchmarks_file or 'config/benchmarks.yaml'
        self.benchmarks = self._load_benchmarks()
    
    def _load_benchmarks(self) -> Dict[str, Any]:
        """Load benchmarks from YAML file or use defaults"""
        if os.path.exists(self.benchmarks_file):
            try:
                with open(self.benchmarks_file, 'r') as f:
                    return yaml.safe_load(f) or {}
            except Exception:
                pass
        
        # Default benchmarks
        return {
            'technology': {
                'gross_margin': 0.40,
                'operating_margin': 0.15,
                'net_margin': 0.10,
                'turnover_rate': 0.15,
                'productivity_index': 0.85
            },
            'manufacturing': {
                'gross_margin': 0.25,
                'operating_margin': 0.12,
                'net_margin': 0.08,
                'turnover_rate': 0.12,
                'productivity_index': 0.75
            },
            'retail': {
                'gross_margin': 0.30,
                'operating_margin': 0.08,
                'net_margin': 0.05,
                'turnover_rate': 0.15,
                'productivity_index': 0.70
            },
            'services': {
                'gross_margin': 0.40,
                'operating_margin': 0.15,
                'net_margin': 0.10,
                'turnover_rate': 0.18,
                'productivity_index': 0.80
            },
            'default': {
                'gross_margin': 0.30,
                'operating_margin': 0.12,
                'net_margin': 0.08,
                'turnover_rate': 0.15,
                'productivity_index': 0.75
            }
        }
    
    def get_benchmark(self, industry: str, metric: str) -> float:
        """
        Get benchmark value for a specific industry and metric
        
        Args:
            industry: Industry type
            metric: Metric name (e.g., 'gross_margin')
            
        Returns:
            Benchmark value
        """
        industry_key = industry.lower() if industry else 'default'
        
        if industry_key in self.benchmarks:
            return self.benchmarks[industry_key].get(metric, self.benchmarks['default'].get(metric, 0.0))
        
        return self.benchmarks['default'].get(metric, 0.0)
    
    def get_all_benchmarks(self, industry: str) -> Dict[str, float]:
        """
        Get all benchmarks for an industry
        
        Args:
            industry: Industry type
            
        Returns:
            Dictionary of benchmark values
        """
        industry_key = industry.lower() if industry else 'default'
        
        if industry_key in self.benchmarks:
            return self.benchmarks[industry_key].copy()
        
        return self.benchmarks['default'].copy()
    
    def compare_to_benchmark(self, value: float, benchmark: float, higher_is_better: bool = True) -> str:
        """
        Compare a value to its benchmark
        
        Args:
            value: Actual value
            benchmark: Benchmark value
            higher_is_better: Whether higher values are better
            
        Returns:
            Status: 'excellent', 'good', 'warning', 'critical'
        """
        if benchmark == 0:
            return 'good'
        
        ratio = value / benchmark if higher_is_better else benchmark / value
        
        if ratio >= 1.0:
            return 'excellent'
        elif ratio >= 0.8:
            return 'good'
        elif ratio >= 0.6:
            return 'warning'
        else:
            return 'critical'


"""
Tests for KPI Calculator functionality
"""

import pytest
import pandas as pd
from tools.kpi_calculator import KPICalculator


class TestKPICalculator:
    """Test cases for KPICalculator"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.calculator = KPICalculator()
    
    def test_calculate_all_kpis_basic(self):
        """Test basic KPI calculation"""
        sample_data = {
            'financial_data': {
                'revenue': 1000000,
                'cost_of_goods_sold': 600000,
                'operating_expenses': 200000,
                'net_income': 200000
            },
            'hr_data': {
                'total_employees': 50
            },
            'operational_data': {
                'process_efficiency': 0.8
            }
        }
        
        results = self.calculator.calculate_all_kpis(sample_data)
        
        assert 'financial' in results
        assert 'hr' in results
        assert 'operational' in results
        
        # Check financial KPIs
        assert 'gross_margin' in results['financial']
        assert 'operating_margin' in results['financial']
        assert 'net_margin' in results['financial']
        assert 'revenue_per_employee' in results['financial']
        
        # Check HR KPIs
        assert 'turnover_rate' in results['hr']
        assert 'total_employees' in results['hr']
        
        # Check operational KPIs
        assert 'cost_efficiency_ratio' in results['operational']
        assert 'productivity_index' in results['operational']
    
    def test_calculate_all_kpis_empty_data(self):
        """Test KPI calculation with empty data"""
        sample_data = {}
        
        results = self.calculator.calculate_all_kpis(sample_data)
        
        # Should return default values
        assert results['financial']['gross_margin'] == 0.3
        assert results['hr']['total_employees'] == 50
    
    def test_calculate_financial_kpis(self):
        """Test financial KPI calculation"""
        financial_data = {
            'revenue': 1000000,
            'cost_of_goods_sold': 600000,
            'operating_income': 200000,
            'net_income': 150000
        }
        
        kpis = self.calculator.calculate_financial_kpis(financial_data)
        
        assert len(kpis) > 0
        assert all(hasattr(kpi, 'name') for kpi in kpis)
        assert all(hasattr(kpi, 'value') for kpi in kpis)
    
    def test_calculate_hr_kpis(self):
        """Test HR KPI calculation"""
        hr_data = pd.DataFrame({
            'employeeNumber': [1, 2, 3],
            'terminationDate': [None, '2024-01-01', None],
            'department': ['Sales', 'Marketing', 'Engineering']
        })
        
        kpis = self.calculator.calculate_hr_kpis(hr_data)
        
        assert len(kpis) > 0
        assert any(kpi.name == 'Turnover Rate' for kpi in kpis)
    
    def test_identify_inefficiencies(self):
        """Test inefficiency identification"""
        kpis = [
            type('KPIMetrics', (), {
                'name': 'Gross Margin',
                'value': 20.0,
                'benchmark': 30.0,
                'status': 'warning',
                'description': 'Low gross margin'
            })(),
            type('KPIMetrics', (), {
                'name': 'Turnover Rate',
                'value': 25.0,
                'benchmark': 15.0,
                'status': 'critical',
                'description': 'High turnover'
            })()
        ]
        
        inefficiencies = self.calculator.identify_inefficiencies(kpis)
        
        assert len(inefficiencies) == 2
        assert inefficiencies[0]['kpi_name'] == 'Gross Margin'
        assert inefficiencies[1]['kpi_name'] == 'Turnover Rate'
        assert inefficiencies[1]['recommended_agent'] == 'hr_optimizer'


if __name__ == '__main__':
    pytest.main([__file__])

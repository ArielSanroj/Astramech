# Company Efficiency Optimizer

A diagnostic and multi-agent architecture for company efficiency optimization, built with CrewAI and designed to identify inefficiencies in financial statements, HR metrics, and operational KPIs.

## 🚀 Features

- **Diagnostic Agent**: Analyzes P&L statements and identifies company inefficiencies
- **Specialized Agents**: HR Optimizer, Operations Optimizer, and Financial Optimizer
- **KPI Analysis**: Calculates financial ratios, turnover rates, and operational metrics
- **Hybrid Memory**: Short-term (CrewAI) and long-term (Pinecone) memory systems
- **Data Ingestion**: Supports multiple data sources (CSV, PDF, APIs)
- **Industry Benchmarks**: Compares performance against industry standards

## 📋 Prerequisites

- Python 3.9+ (tested with 3.9.6)
- API keys for:
  - OpenAI (for LLM) or NVIDIA AI Endpoints
  - Pinecone (for vector database)
  - Optional: QuickBooks, BambooHR for data integration

## 🛠️ Installation

1. **Clone or download the project**
   ```bash
   cd company-efficiency-optimizer
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install crewai==0.1.32 langchain python-dotenv pandas numpy requests pinecone pytesseract pdf2image Pillow rich typer
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_key_here

# Optional (for data integration)
QUICKBOOKS_API_KEY=your_quickbooks_key_here
BAMBOOHR_API_KEY=your_bamboohr_key_here

# Project Configuration
PROJECT_NAME=company-efficiency-optimizer
LOG_LEVEL=INFO
```

### Agent Configuration (config/agents.yaml)

The system includes four specialized agents:

- **Diagnostic Agent**: Main analyzer for KPIs and inefficiencies
- **HR Optimizer**: Focuses on talent management and turnover reduction
- **Operations Optimizer**: Optimizes processes and efficiency
- **Financial Optimizer**: Enhances financial performance

### Task Configuration (config/tasks.yaml)

Defines the workflow tasks:
1. Request P&L data from user
2. Compute KPIs and identify inefficiencies
3. Create comprehensive diagnostic summary
4. Specialized optimization analysis

## 🚀 Usage

### Quick Demo (No API Keys Required)

```bash
python demo.py
```

This demonstrates the system capabilities using sample data.

### Full System (Requires API Keys)

```bash
python main.py
```

### Test Setup

```bash
python test_setup.py
```

## 📊 System Architecture

### Phase 1: System Setup and Data Preparation
- Environment setup and dependency installation
- Data ingestion from various sources
- Memory system initialization

### Phase 2: Diagnostic Analysis
- P&L data processing and validation
- KPI calculation and benchmarking
- Inefficiency identification and routing

### Phase 3: Multi-Agent Optimization
- Specialized agent deployment
- Targeted optimization strategies
- Implementation roadmap generation

## 🔍 Key Performance Indicators (KPIs)

### Financial KPIs
- **Gross Margin**: (Gross Profit / Revenue) × 100
- **Operating Margin**: (Operating Income / Revenue) × 100
- **Net Margin**: (Net Income / Revenue) × 100
- **Revenue per Employee**: Revenue / Employee Count

### HR KPIs
- **Turnover Rate**: (Exits / Average Headcount) × 100
- **Department-specific turnover rates**

### Operational KPIs
- **Cost Efficiency Ratio**: Operating Expenses / Revenue
- **Productivity Index**: Revenue per Employee vs. Industry Benchmark

## 🧠 Memory System

### Short-term Memory
- CrewAI's built-in memory for conversation context
- Maintains context within agent interactions

### Long-term Memory
- Pinecone vector database for persistent storage
- Stores KPI trends, inefficiencies, and optimization strategies
- Enables pattern recognition and historical analysis

## 📁 Project Structure

```
company-efficiency-optimizer/
├── config/
│   ├── agents.yaml          # Agent configurations
│   └── tasks.yaml           # Task definitions
├── data/                    # Data storage directory
├── tools/
│   └── kpi_calculator.py   # KPI calculation utilities
├── .env                     # Environment variables
├── crew.py                  # Original crew implementation
├── simple_crew.py           # Simplified crew (compatible with CrewAI 0.1.32)
├── main.py                  # Main execution script
├── demo.py                  # Demo script
├── test_setup.py           # Setup validation
├── data_ingest.py          # Data ingestion module
├── memory_setup.py         # Memory system implementation
└── README.md               # This file
```

## 🔄 Workflow

1. **Data Ingestion**
   - User provides P&L data (PDF, CSV, or manual input)
   - System extracts and validates financial figures
   - HR data integration (optional)

2. **KPI Analysis**
   - Calculate financial ratios and operational metrics
   - Compare against industry benchmarks
   - Identify inefficiencies and their severity

3. **Agent Routing**
   - Route issues to specialized agents:
     - HR Optimizer (turnover issues)
     - Operations Optimizer (efficiency issues)
     - Financial Optimizer (margin issues)

4. **Optimization Strategy**
   - Generate targeted recommendations
   - Create implementation roadmap
   - Estimate ROI and impact

## 🎯 Industry Benchmarks

The system includes industry-specific benchmarks:

| Industry | Gross Margin | Operating Margin | Net Margin | Turnover Rate |
|----------|--------------|------------------|------------|---------------|
| Retail   | 30%          | 8%               | 5%         | 15%           |
| Manufacturing | 25%      | 12%              | 8%         | 12%           |
| Services | 40%          | 15%              | 10%        | 18%           |

## 🚨 Inefficiency Detection

The system automatically identifies inefficiencies based on:

- **Critical**: Performance significantly below benchmark
- **Warning**: Performance moderately below benchmark
- **Good**: Performance meets benchmark
- **Excellent**: Performance exceeds benchmark

## 🔧 Customization

### Adding New KPIs

1. Update `tools/kpi_calculator.py`
2. Add calculation logic in `calculate_financial_kpis()`
3. Update benchmarks in `__init__()`

### Adding New Agents

1. Update `config/agents.yaml`
2. Add agent creation method in `simple_crew.py`
3. Define tasks in `config/tasks.yaml`

### Custom Data Sources

1. Extend `data_ingest.py`
2. Add new ingestion methods
3. Update data validation logic

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure virtual environment is activated
2. **API Key Errors**: Verify keys in `.env` file
3. **Memory Issues**: Check Pinecone API key and index creation
4. **Version Conflicts**: Use exact versions specified in requirements

### Debug Mode

Enable verbose logging by setting `LOG_LEVEL=DEBUG` in `.env`

## 📈 Future Enhancements

- [ ] NVIDIA AI Endpoints integration
- [ ] Real-time data streaming
- [ ] Advanced visualization dashboard
- [ ] Machine learning-based predictions
- [ ] Multi-language support
- [ ] API endpoint for external integrations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- CrewAI team for the multi-agent framework
- LangChain for LLM integration
- Pinecone for vector database capabilities
- OpenAI for language model access

## 📞 Support

For questions or issues:
1. Check the troubleshooting section
2. Run `python test_setup.py` to validate setup
3. Review the demo output for expected behavior
4. Create an issue with detailed error information

---

**Built with ❤️ for business efficiency optimization**
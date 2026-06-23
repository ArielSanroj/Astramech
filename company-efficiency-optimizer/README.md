# Company Efficiency Optimizer

`company-efficiency-optimizer` es el núcleo activo de Astramech. Es una app Flask que captura contexto de una empresa, recibe archivos operativos o financieros y devuelve diagnóstico, KPIs y planes accionables por área.

## Qué hace hoy
- landing y quickstart comercial
- flujo guiado cuando el usuario no tiene datos listos
- carga de archivos `csv`, `xls`, `xlsx` y `pdf`
- cálculo de KPIs y resumen diagnóstico
- planes base para ventas, operaciones, finanzas, marketing y RRHH
- exportación de resultados a `csv` y `json`

## Stack real
- Flask como app web principal
- lógica de análisis en `app/services/` y módulos raíz de ingestión/KPIs
- sesiones locales con Flask-Session en desarrollo
- deploy serverless con `api/index.py`
- dependencias opcionales:
  - Ollama para generación o enriquecimiento
  - Pinecone para memoria de largo plazo

La app puede arrancar sin esas integraciones opcionales; cuando faltan, debe degradar de forma controlada.

## Arranque local
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp env.example .env
python3 run.py
```

Puerto por defecto: `5002`.

## Flujo principal
1. El usuario completa `quickstart` o entra al flujo `guided`.
2. La app guarda contexto mínimo del lead.
3. El usuario sube archivos.
4. La capa de ingestión normaliza datos y calcula KPIs.
5. Se renderizan resultados y planes por área.

## Puntos de entrada
- local: `run.py`
- app factory: `app/__init__.py`
- serverless: `api/index.py`

## Pruebas útiles
```bash
pytest tests -q
pytest tests/test_finance_efficiency_engine.py -q
pytest tests/test_pipeline.py -q
```

## Alcance actual
- este directorio es el producto principal del repo
- scripts de ngrok, documentación de deploy avanzada, MCP servers y artefactos experimentales no forman parte del flujo base de desarrollo
- las integraciones multi-servicio del monorepo viven fuera de este núcleo y no son necesarias para trabajar en la app principal

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

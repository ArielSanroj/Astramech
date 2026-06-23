# Astramech

Astramech se está limpiando alrededor de un núcleo más pequeño y mantenible. El producto principal actual es la app Flask en `company-efficiency-optimizer/`.

## Núcleo actual
- `company-efficiency-optimizer/`: app web para diagnóstico empresarial, carga de archivos, cálculo de KPIs y planes accionables por área.
- `api/`: entrypoint serverless que apunta a la app Flask principal.

## Secundario o legado
- `api_gateway/`: gateway FastAPI para integraciones externas.
- `astramech-orchestrator/`: consumidor de eventos y coordinación experimental.
- `external_repos/`: repos externos integrados o espejados; no forman parte del flujo principal de trabajo diario.
- documentación de migraciones, estados e integraciones en la raíz: mantener como referencia histórica hasta consolidar una limpieza mayor.

## Arranque recomendado
```bash
cd company-efficiency-optimizer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp env.example .env
python3 run.py
```

La app queda disponible por defecto en `http://localhost:5002`.

## Deploy
- serverless: `vercel.json` + `api/index.py`
- local/standalone: `company-efficiency-optimizer/run.py`

## Notas
- `external_repos/` y el stack multi-servicio completo quedan fuera de esta primera etapa de saneamiento.
- Si necesitas contexto histórico del monorepo, revisa `ARCHITECTURE.md` y `COMPLETE_SETUP.md`, pero no los tomes como la guía operativa principal del estado actual.

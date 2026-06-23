# Dynamic Crew (Optional)

The dynamic crew system orchestrates specialized AI agents (pricing, finance, operations, etc.) when a working LLM stack is available. It lives under `company-efficiency-optimizer/dynamic_crew.py` and uses the local `config/` folder for agent/task templates.

## When it runs
- `ENABLE_DYNAMIC_CREW` must be set to `1` or `true`.
- Either `OLLAMA_BASE_URL` or `OPENAI_API_KEY` (depending on the chosen provider) must be configured along with `OLLAMA_MODEL`.
- The config files (`config/agents.yaml`, `config/tasks.yaml`, optional `config/dynamic_agents.yaml`) must exist relative to `company-efficiency-optimizer/`.

If any of those requirements is missing, the system logs a warning, disables itself, and leaves the core Flask app unimpacted.

## Re-enabling
1. Populate `config/agents.yaml` and `config/tasks.yaml` with the agent/task definitions you want CrewAI to manage.
2. Set environment variables (either in `.env` or the process environment):
   - `ENABLE_DYNAMIC_CREW=1`
   - `OLLAMA_BASE_URL` pointing to your Ollama server or `OPENAI_API_KEY`.
   - Optional: `PINECONE_API_KEY`/`PINECONE_INDEX` if you want memory persistence.
3. Restart the app; the crew will log its status and attempt to create the diagnostic agent before running analysis tasks.

## Fallback
When disabled, the crew still exposes `dynamic_crew.py`, but `DynamicCrewSystem.create_diagnostic_agent()` returns `None` until the prerequisites are met. This keeps the rest of Astramech running without requiring OpenAI/Ollama keys.

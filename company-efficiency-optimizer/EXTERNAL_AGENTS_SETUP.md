# External Agents Setup

This folder adds a unified contract for external agents (Finanzas, Ventas, Marketing, RRHH/Legal when available). Each agent is wired as a git submodule under `external_repos/` plus a lightweight adapter in `external_agents/`.

## 1) Add submodules (run at repo root)

```bash
git submodule add https://github.com/ArielSanroj/supervincent external_repos/supervincent
git submodule add https://github.com/ArielSanroj/marketingagentcompanies external_repos/marketingagentcompanies
git submodule add https://github.com/ArielSanroj/marketingagent external_repos/marketingagent
git submodule add https://github.com/ArielSanroj/callagent external_repos/callagent
git submodule add https://github.com/ArielSanroj/linkedinposting external_repos/linkedinposting
git submodule add https://github.com/ArielSanroj/mailicpagent external_repos/mailicpagent
git submodule add https://github.com/ArielSanroj/clioalphamodel external_repos/clioalphamodel
```

Pull/update later with:

```bash
git submodule update --init --recursive
```

## 2) Contract

- Base interface in `external_agents/base.py` with `run(AgentRunRequest) -> AgentRunResult`.
- Catalog in `config/external_agents.yaml` lists repo URL, local path, and adapter import path.
- Registry in `external_agents/registry.py` exposes `get_adapter(name)` / `list_adapters()`.

## 3) Wire each adapter

For each adapter under `external_agents/adapters/`:
- Point `local_repo_path` to the submodule.
- Implement `run()` by calling the corresponding entrypoint in the submodule (CLI, API, or Python).
- Map credentials to environment variables expected by that project.
- Normalize outputs to a structured `AgentRunResult` (use consistent keys like `report`, `recommendations`, `actions`, `metrics`).

## 4) Where to call from Astramech

- Centralize creation/loading via `external_agents.registry`.
- Drive which agent to execute from configs (`config/external_agents.yaml`) or a DB row per client.
- Use queues/scheduler for long-running marketing/CRM tasks; keep financial analysis synchronous or batched.

## 5) Next steps

1) Add the submodules (above).
2) For two priority agents (e.g., Finanzas + Marketing TikTok), implement `run()` and a minimal integration test that mocks credentials.
3) Expand to the rest and add healthchecks per adapter.

# Legacy Notes

This repository has been trimmed to keep only the `company-efficiency-optimizer` core plus the necessary orchestration wiring.
The following content was intentionally archived to reduce noise:

- multiple `/company-efficiency-optimizer/*.md` operational reports (deploy, ngrok, status, integration narratives)
- shell helpers and scripts (`check_status.sh`, `start_ngrok*.sh`, `deploy_to_vercel.sh`, etc.)
- agent-specific docs and tools (supervincent/clio helpers, `interactive_main.py`, `nanobot*`, `summary.py`)
- duplicated tooling (`app_factory.py`, alternative tests/reports, external agent adapters inside `company-efficiency-optimizer/`)

If you need one of those files for reference, search `git log -- company-efficiency-optimizer/<file>` or revisit the historical branch that contained the full multi-agent stack.

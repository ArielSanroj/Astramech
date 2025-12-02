# Astramech Unified Architecture

## 1. Visión General de Astramech

a. **Objetivo**: Astramech es un orquestador IA que crea, coordina y supervisa sub-agentes especializados en marketing, ventas, CRM, finanzas y recursos humanos para automatizar toda la cadena de valor empresarial.

b. **Stack global**:
| Capa | Tecnologías principales |
| --- | --- |
| Orquestación | CrewAI supervisor + LangGraph workflows dentro de `astramech/` |
| API Gateway | FastAPI 0.115+ expone `/api/v1` y delega a cada agente |
| Messaging | RabbitMQ 3.12+ para eventos (lead.created, buyer_signal, call.completed) + Redis 7 para cache/session |
| Persistencia | PostgreSQL 16 con Alembic, shared schemas en `shared/db/` |
| Storage | MinIO (S3 compatible) para grabaciones, videos y documentos |
| Auth | JWT centralizado, OAuth proxies a TikTok/LinkedIn/Google/Twilio |
| Infraestructura | Docker Compose (local), Kubernetes+Helm (prod), GitHub Actions CI/CD |
| Observabilidad | Prometheus + Grafana + Sentry |

c. **Diagrama High-Level**:
```mermaid
flowchart TB
    subgraph External Platforms
        L(LinkedIn)
        T(TikTok)
        G(Google Ads)
        Tw(Twilio)
        O(OpenAI/Claude/Ollama)
    end
    subgraph Astramech Core
        AG[API Gateway]
        SU[CrewAI Supervisor]
        MQ[RabbitMQ]
        DB[(PostgreSQL)]
        REDIS[Redis Cache]
        STORAGE[MinIO]
    end
    subgraph Agents
        MG[Marketing Google Ads]
        MT[Marketing TikTok]
        LI[LinkedIn Commenting]
        CRM[CRM + Email Sequencer]
        CALL[Cold Call Agent]
        FN[SuperVincent Finance]
        HR[Clio HR Agent]
    end
    L --> LI
    T --> MT
    G --> MG
    Tw --> CALL
    O --> MT
    O --> LI
    AG --> MG
    AG --> MT
    AG --> LI
    AG --> CRM
    AG --> CALL
    AG --> FN
    AG --> HR
    MG & MT & LI & CRM & CALL & FN & HR -->|events| MQ
    MQ --> AG
    MQ --> CALL
    MG & MT & LI & CRM & CALL & FN & HR --> DB & REDIS & STORAGE
    AG --> SU
    SU -->|crea workflow| Agents
```

## 2. Análisis de Proyectos Individuales

Cada sub-agente conserva su stack y se conecta mediante `shared/schemas` y eventos.

### 2.1 Marketing Google Ads (https://github.com/ArielSanroj/marketingagent)
| Aspecto | Resumen |
| --- | --- |
| Árbol principal | `frontend/` (React + Vite + Redux), `backend/` (FastAPI + Celery + Socket.io), `docker-compose.yml`, `scripts/` y `docs/`. |
| Archivos clave | `backend/app/main.py` (FastAPI + routers) y `backend/app/workers/analytics_worker.py` (Celery). `frontend/src/store/` (Redux slices). |
| Endpoints | `/api/v1/campaigns`, `/analytics/*`, `/content/generate`, `/auth/*`, `/track/event`. JWT + Celery tasks. |
| Procesamiento | Usuarios crean campañas → evento `campaign.activated` entra a RabbitMQ → Celery workers actualizan PostgreSQL, Redis, envían WebSocket `campaign:{id}:updated`. |
| Streams | RabbitMQ (analytics.events, campaign.activated). Socket.io envía métricas en tiempo real. |
| Integración | Publica métricas compartidas (spend, ctr) a `astramech/` vía RabbitMQ y actualiza tabla `campaigns`.

### 2.2 Marketing TikTok (https://github.com/ArielSanroj/marketingagentcompanies)
| Aspecto | Resumen |
| --- | --- |
| Stack | Python CLI + FastAPI opcional. Ollama para generación, Apify para scraping, output en JSON local `/tmp/marketing_hub/metrics/`. |
| Archivos clave | `marketing_hub/agent.py`, `core/llm/generator.py`, `core/video/generator.py`, `core/tiktok/publisher.py`. |
| Endpoints | `GET /health`, `POST /run` (ejecuta marcas), `GET /metrics`. |
| Procesamiento | Scraper Apify → análisis de tendencias (Ollama) → script/caption → mock video generator → `publish_to_tiktok` stub. Resultados logueados en JSON. |
| Streams | Ninguno; reemplazado por cron + scheduling. |
| Integración | Expone métricas en API que el Gateway puede usar para alimentar `marketing_metrics` tables.

### 2.3 LinkedIn Commenting (https://github.com/ArielSanroj/linkedinposting)
| Aspecto | Resumen |
| --- | --- |
| Stack | FastAPI + Playwright + OpenAI. Archivos JSON para sesión, drafts y metrics. |
| Archivos clave | `linkedin_mcp/services/linkedin_service.py`, `core/session_manager.py`, `api/rest_api.py`. |
| Endpoints | `/api/v1/search`, `/draft`, `/submit`, `/metrics`, `/health`. |
| Procesamiento | Scheduler → Playwright Search → OpenAI prompt → Post comment (Playwright) → Verifica y registra en `comment_log.json`. |
| Streams | No; usa cron + JSON logs. |
| Integración | Gateway consulta `GET /api/v1/ready` para obtener posts listos y luego reinyecta datos a CRM (`lead.created`).

### 2.4 CRM + Email (https://github.com/ArielSanroj/mailicpagent)
| Aspecto | Resumen |
| --- | --- |
| Stack | Flask + SQLite, Gmail API, APScheduler, Twilio sync, Ollama. |
| Archivos clave | `src/automation_engine.py`, `crm_data_manager.py`, `email_service.py`, `automation/event_listener.py`. |
| Endpoints | `/api/v1/contacts`, `/deals`, `/tasks`, `/webhooks`, `/interactions/email`. Autenticación API keys. |
| Procesamiento | Emails enviados → tracking pixel hits → `automation_engine` actualiza lead score → genera buyer signal via RabbitMQ. |
| Streams | APScheduler (cron). Puede publicar `lead.created`, `buyer_signal.detected` en RabbitMQ para otros agentes. |
| Integración | Es el hub de buyer signals; la tabla `leads` se comparte con la base PostgreSQL central.

### 2.5 Cold Calling (https://github.com/ArielSanroj/callagent)
| Aspecto | Resumen |
| --- | --- |
| Stack | FastAPI + SQLAlchemy async + Twilio Media Streams + Deepgram + ElevenLabs + MinIO. |
| Archivos clave | `/app/services/*` (twilio_svc, policy_engine, ws_stream). Alembic migrations. |
| Endpoints | `/api/calls`, `/voice/answer`, `/voice/status`, `/streams/twilio`, `/api/audio/tts`, `/api/campaign/*`. |
| Procesamiento | POST `/api/calls` → Twilio callback `/voice/answer` → TwiML + Media Stream → WebSocket `/streams/twilio` streaming audio a Deepgram + policy engine → ElevenLabs TTS → Twilio `call.update`. Registra transcripciones, score, events. |
| Streams | WebSocket + events for transcripts; RabbitMQ `call.completed`, `policy.events`. |
| Integración | Publica `call.completed` y `transcript` a CRM, actualiza lead status/reports via RabbitMQ.

### 2.6 Finanzas (SuperVincent: https://github.com/ArielSanroj/supervincent)
| Aspecto | Resumen |
| --- | --- |
| Stack | FastAPI + PDF/OCR (pdfplumber/pytesseract) + Celery + Redis + JSON repository + Alegra API. |
| Archivos clave | `src/services/invoice_service.py`, `src/services/alegra_service.py`, `tasks.py`. |
| Endpoints | `/process`, `/process/upload`, `/reports/*`, `/tax/*`, `/processed/recent`, `/health`, `/cache`. |
| Procesamiento | Receives file upload → parser → tax calculation → Alegra bill/invoice creation → caching in Redis + JSON index. Celery tasks for async processing + watchdog. |
| Streams | Celery + Redis message queue. |
| Integración | Events `invoice.processed` via RabbitMQ updates CRM (deal status) and marketing budgets. Data posted to `financial_reports` table.

### 2.7 HR Agent (Clio Alpha)
| Aspecto | Resumen |
| --- | --- |
| Stack | Frontend Angular + NestJS backend + FastAPI ML (XGBoost + SHAP). SQLite DB + JSON shared data. |
| Archivos clave | `backend/src/modules`, `ml-service/main.py` + `models/predictor.py`. |
| Endpoints | `/api/questionnaire/*`, `/api/teams/*`, `/api/risks/*`, `/api/ml/predict`, `/api/ml/health`. |
| Procesamiento | Questionnaire answers → subscale calculation → assessment saved → ML proxy to FastAPI XGBoost service → Burnout/Turnover probabilities + SHAP. |
| Streams | Polling/HTTP only. Future: WebSockets for updates. |
| Integración | HR risk alerts produce `burnout.risk.detected` events; narratives fed into marketing personalization.

**Puntos de integración:**
- Shared Pydantic models under `shared/schemas/` (User, Lead, Campaign, Assessment, Invoice).
- `shared/events/` define RabbitMQ topics (lead.created, buyer_signal.detected, call.completed, invoice.processed, burnout.risk.detected).
- Auth via JWT + OAuth for external APIs; each agent inherits `shared/auth/jwt.py`.

## 3. Arquitectura Unificada

### 3.1 Estructura monorepo sugerida
```
astramech-monorepo/
├── astramech/                # Orquestador + CrewAI
├── agents/                   # Cada microservice + README
│   ├── marketing_googleads/
│   ├── marketing_tiktok/
│   ├── linkedinposting/
│   ├── crm_email/
│   ├── outbound_calling/
│   ├── finance_supervincent/
│   └── hr_clio/
├── shared/                   # Auth, DB models, events, storage, schemas
├── api_gateway/               # FastAPI + GraphQL entrypoint
├── infra/                    # Docker, terraform, helm charts
├── docs/
└── scripts/
```

### 3.2 Endpoints globales (API Gateway)
| Método | Ruta | Agente | Request/Response destacado |
| --- | --- | --- | --- |
| **Marketing Google Ads** |
| POST | `/api/v1/marketing/google-ads/analyze` | Marketing Google Ads | Body: `{email, hotel_url, instagram_url?}` → returns `request_id` |
| GET | `/api/v1/marketing/google-ads/status/{request_id}` | Marketing Google Ads | Returns campaign analysis status and results |
| GET | `/api/v1/marketing/google-ads/performance` | Marketing Google Ads | Returns performance statistics |
| GET | `/api/v1/marketing/google-ads/health` | Marketing Google Ads | Health check |
| **Marketing TikTok** |
| POST | `/api/v1/marketing/tiktok/run` | Marketing TikTok | Body: `{brands?}` → returns analysis results |
| GET | `/api/v1/marketing/tiktok/health` | Marketing TikTok | Health check |
| **LinkedIn** |
| POST | `/api/v1/linkedin/posts/comment` | LinkedIn Agent | Body: `{post_id, brand_voice?, comment_text?}` → returns comment draft + confidence |
| POST | `/api/v1/linkedin/posts/search` | LinkedIn Agent | Body: `{query, limit?}` → returns matching posts |
| GET | `/api/v1/linkedin/health` | LinkedIn Agent | Health check |
| **CRM** |
| POST | `/api/v1/crm/leads` | CRM | Body: `{contact_name, email, company?, phone?, source?}` → returns `lead_id`, score |
| POST | `/api/v1/crm/buyer-signal` | CRM | Body: `{lead_id, signal_type, strength, metadata?}` → returns queue_ack |
| GET | `/api/v1/crm/leads/{lead_id}` | CRM | Returns lead information |
| GET | `/api/v1/crm/health` | CRM | Health check |
| **Cold Calling** |
| POST | `/api/v1/calls/outbound` | Cold Call | Body: `{to_number, campaign_id?, lead_id?, metadata?}` → Twilio call queued + `call_id` |
| GET | `/api/v1/calls/status/{call_id}` | Cold Call | Returns call status and transcript |
| GET | `/api/v1/calls/health` | Cold Call | Health check |
| **Finance** |
| POST | `/api/v1/finance/invoices/process` | Finance | Body: `{file_path, user_id?}` → returns `invoice_id`, taxes |
| POST | `/api/v1/finance/invoices/batch` | Finance | Body: `{file_paths[], user_id?}` → returns batch processing results |
| GET | `/api/v1/finance/health` | Finance | Health check |
| **HR** |
| POST | `/api/v1/hr/questionnaire/submit` | HR | Body: `{userId, answers}` → returns assessment results |
| POST | `/api/v1/hr/teams/create` | HR | Body: `{name, memberIds[]}` → returns team_id |
| POST | `/api/v1/hr/risks/evaluate` | HR | Body: `{teamId}` → returns risk matrix evaluation |
| GET | `/api/v1/hr/health` | HR | Health check |
| **Analytics** |
| GET | `/api/v1/analytics/dashboard` | Gateway aggregating all metrics | Response: combined KPI (campaigns, calls, invoices, burnout) |

### 3.3 Data Streams (Mermaid)
```mermaid
flowchart LR
    CRM[CRM Signals]
    Buyer[Buyer Signal]
    Rabbit[RabbitMQ]
    Call[Cold Call Agent]
    Marketing[Marketing Agents]
    Finance[Finance Agent]
    HR[HR Agent]
    DB[(PostgreSQL)]

    CRM -->|lead.created| Rabbit
    CRM -->|buyer_signal.detected| Rabbit
    Rabbit --> Call
    Call -->|call.completed| Rabbit
    Rabbit --> Marketing
    Marketing -->|engagement.high| CRM
    Rabbit -->|invoice.processed| Finance
    Finance -->|financial metrics| CRM
    HR -->|burnout.risk.detected| Rabbit
    Rabbit --> Marketing
    Marketing --> DB
    Call --> DB
    Finance --> DB
    HR --> DB
```

### 3.4 Procesamiento cruzado
1. **Lead flow**: LinkedIn/CRM produce `lead.created` → CRM scores it → RabbitMQ dispatches to Cold Call → call transcripts published back to CRM → marketing uses sentiment/engagement to refine ads → finance matches invoice/revenue.
2. **Buyer signal loop**: CRM identifies intent `buyer_signal.detected`, triggers Cold Call and Marketing (targeted TikTok/Google Ads), update leads table and sequences.
3. **HR insight**: Clio ML raises `burnout.risk.detected`, Gateway pushes personalization flags to marketing + notifies CRM to check engagement; also triggers finance to budget for support.

## 4. Base de Datos y Modelos

### 4.1 Esquema central (PostgreSQL)
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  full_name TEXT,
  role TEXT CHECK (role IN ('admin','user','viewer')),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE companies (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  industry TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE leads (
  id UUID PRIMARY KEY,
  company_id UUID REFERENCES companies(id),
  contact_name TEXT,
  email TEXT,
  score DECIMAL,
  source TEXT,
  status TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE campaigns (
  id UUID PRIMARY KEY,
  name TEXT,
  channel TEXT,
  budget DECIMAL,
  start_date DATE,
  end_date DATE,
  status TEXT DEFAULT 'draft'
);

CREATE TABLE call_sessions (...);
CREATE TABLE email_interactions (...);
CREATE TABLE invoices (...);
CREATE TABLE assessments (...);
CREATE TABLE events_log (...);
```

### 4.2 Shared models & migrations
- `shared/db/models.py` defines SQLAlchemy models for every table.
- Alembic env configured once in `shared/db/alembic.ini`.
- Each agent imports from `shared/db/models` to keep entities consistent (User, Lead, Campaign, Assessment, Invoice).

### 4.3 Observabilidad de datos
- Auditado con `events_log` (type, payload, source).
- Metrics stored in Redis for WebSockets.

## 5. Infraestructura y Despliegue

### 5.1 Docker Compose (dev)
(ya mostrado arriba) con servicios: api-gateway, orchestrator, agents (cuando se prueban local), postgres, redis, rabbitmq, minio.

### 5.2 Variables de entorno clave
```
ENVIRONMENT=production
JWT_SECRET=...
DATABASE_URL=postgresql+asyncpg://...
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
REDIS_URL=redis://redis:6379/0
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
OPENAI_API_KEY=...
TWILIO_ACCOUNT_SID=...
TIKTOK_ACCESS_TOKEN=...
LINKEDIN_API_TOKEN=...
GMAIL_CREDENTIALS_PATH=/shared/secrets/gmail_credentials.json
```

### 5.3 CI/CD
1. **Test** job runs `pytest` across all agents (with DB mocks). 2. **Build** job builds Docker images for agents/gateway. 3. **Deploy** job pushes to registry and updates Kubernetes manifests via Helm.

## 6. Ejecución Local y Testing

1. `git clone ...` + `cp .env.example .env`.
2. `docker compose up -d` (levanta Postgres, Redis, RabbitMQ, MinIO, API Gateway, CrewAI supervisor).
3. `docker compose exec api-gateway alembic upgrade head`.
4. `source ./agents/marketing_googleads/.venv/bin/activate` y `pip install -r requirements.txt` (por agente) o usar `poetry install` unificado.
5. `docker compose up --build astramech-orchestrator` para lanzar workflow.
6. Tests: `pytest tests/` y `npm run test` para frontends (React, Angular). Use `playwright test` for LinkedIn flows. `callagent` tiene `pytest` + `twilio` mocks.

## 7. Roadmap y Riesgos

### 7.1 Próximos pasos
1. Multi-región Kubernetes + Helm charts.
2. Observabilidad avanzada (Prometheus metrics para RabbitMQ, Grafana dashboard, Sentry for FastAPI errors).
3. Event-driven workflows (Kafka como opción adicional, Drone/Temporal para stateful flows).
4. Expandir HR + Finance insights (predictive analytics, SLAs).  

### 7.2 Riesgos
- Rate limits en LinkedIn/TikTok/Twilio/OpenAI. Mitigar con retries + circuit breakers (
`shared/core/circuit_breaker`).
- Seguridad de grabaciones/llamadas: cifrar assets en MinIO + rotación de llaves.
- Coordinación de estados multi-agente: usar eventos idempotentes y deduplicación (`events_log`).

---
Astramech ahora combina la fuerza de cada agente en un plano unificado, con eventos, base de datos central y orchestración inspeccionada, listo para producción empresarial.

# Migración del Agente Financiero SuperVincent

## Estado Actual

✅ **Completado**:
- Carpeta `shared/` con helpers reutilizables:
  - `shared/db/` - SQLAlchemy session helpers
  - `shared/celery.py` - Configuración Celery unificada
  - `shared/events/` - Definiciones de tópicos RabbitMQ
- `docker-compose.yml` unificado con servicios:
  - PostgreSQL 16
  - Redis 7
  - RabbitMQ 3-management
  - MinIO (S3 compatible)
  - API Gateway (FastAPI)
  - Astramech Orchestrator (placeholder)
  - Finance SuperVincent service
- API Gateway con router de finanzas (`/api/v1/finance/*`)
- Servicio `finance-supervincent` apuntando a `external_repos/supervincent`

## Arquitectura de Integración

```
┌─────────────────┐
│   Cliente       │
│   (HTTP)        │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│   API Gateway (FastAPI)         │
│   Port: 8000                    │
│   /api/v1/finance/*             │
└────────┬────────────────────────┘
         │
         │ HTTP Proxy
         ▼
┌─────────────────────────────────┐
│   Finance SuperVincent          │
│   Port: 8000 (interno)          │
│   /process, /process/batch,     │
│   /health                       │
└────────┬────────────────────────┘
         │
         ├──► PostgreSQL (datos)
         ├──► Redis (cache)
         ├──► RabbitMQ (eventos)
         └──► Alegra API (externo)
```

## Endpoints Disponibles

### A través del API Gateway

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/finance/invoices/process` | Procesar una factura individual |
| POST | `/api/v1/finance/invoices/batch` | Procesar múltiples facturas |
| GET | `/api/v1/finance/health` | Health check del servicio financiero |

### Payloads

**POST `/api/v1/finance/invoices/process`**:
```json
{
  "file_path": "/app/uploads/invoice.pdf",
  "user_id": "optional_user_id"
}
```

**POST `/api/v1/finance/invoices/batch`**:
```json
{
  "file_paths": [
    "/app/uploads/invoice1.pdf",
    "/app/uploads/invoice2.pdf"
  ],
  "user_id": "optional_user_id"
}
```

## Próximos Pasos

### 1. Levantar el Stack Completo

```bash
# Copiar variables de entorno
cp .env.example .env

# Editar .env con tus valores (especialmente ALEGRA_EMAIL y ALEGRA_TOKEN)

# Levantar todos los servicios
docker compose up -d

# Verificar que todos los servicios están corriendo
docker compose ps
```

### 2. Verificar Servicios Base

```bash
# Verificar PostgreSQL
docker compose exec postgres psql -U astramech -d astramech -c "SELECT version();"

# Verificar Redis
docker compose exec redis redis-cli ping

# Verificar RabbitMQ (acceder a http://localhost:15672 con guest/guest)
# O verificar desde CLI:
docker compose exec rabbitmq rabbitmqctl status
```

### 3. Ejecutar Migraciones (si aplica)

```bash
# Si SuperVincent tiene migraciones Alembic:
docker compose exec finance-supervincent alembic upgrade head

# O si están en el contenedor:
docker compose exec finance-supervincent python -m alembic upgrade head
```

### 4. Verificar Integración

```bash
# Instalar dependencias del script de verificación
pip install httpx

# Ejecutar script de verificación
python scripts/verify_finance_integration.py

# O manualmente con curl/httpx:
# Health check del Gateway
curl http://localhost:8000/

# Health check de Finance via Gateway
curl http://localhost:8000/api/v1/finance/health

# Health check directo de Finance (si expone puerto)
curl http://localhost:8001/health
```

### 5. Testing con pytest/httpx

```bash
# Crear test de integración
pytest tests/test_finance_integration.py -v

# O ejecutar tests existentes de SuperVincent
docker compose exec finance-supervincent pytest
```

### 6. Publicar Eventos RabbitMQ

Una vez que el servicio esté funcionando, debería publicar eventos a RabbitMQ:

```python
# Ejemplo de publicación de evento desde SuperVincent
from shared.events import Topics
import pika

connection = pika.BlockingConnection(
    pika.URLParameters(os.getenv('RABBITMQ_URL'))
)
channel = connection.channel()

channel.basic_publish(
    exchange='',
    routing_key=Topics.finance_invoice_processed,
    body=json.dumps({
        'invoice_id': 'inv_123',
        'total_amount': 1000000,
        'vendor': 'Acme Corp',
        'status': 'processed'
    })
)
```

### 7. Integrar con CrewAI Orchestrator

El orquestador puede consumir eventos de finanzas:

```python
# En astramech-orchestrator/app.py
from shared.events import Topics
import pika

def on_finance_invoice_processed(ch, method, properties, body):
    """Handle invoice processed event."""
    data = json.loads(body)
    # Trigger workflow based on invoice data
    # e.g., update CRM deal status, trigger marketing campaign
    pass

# Setup consumer
channel.basic_consume(
    queue='finance_invoice_processed',
    on_message_callback=on_finance_invoice_processed,
    auto_ack=True
)
```

## Variables de Entorno Requeridas

Asegúrate de tener estas variables en tu `.env`:

```bash
# Base de datos
DATABASE_URL=postgresql+asyncpg://astramech:secret@postgres:5432/astramech

# Message Queue
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/

# Cache
REDIS_URL=redis://redis:6379/0

# Finance Service
FINANCE_SERVICE_URL=http://finance-supervincent:8000
ALEGRA_EMAIL=tu_email@alegra.com
ALEGRA_TOKEN=tu_token_de_alegra
```

## Troubleshooting

### El servicio finance-supervincent no inicia

```bash
# Ver logs
docker compose logs finance-supervincent

# Verificar que el Dockerfile existe en external_repos/supervincent
ls -la external_repos/supervincent/Dockerfile

# Rebuild el servicio
docker compose build finance-supervincent
docker compose up -d finance-supervincent
```

### Error de conexión a PostgreSQL

```bash
# Verificar que PostgreSQL está corriendo
docker compose ps postgres

# Verificar variables de entorno
docker compose exec finance-supervincent env | grep DATABASE_URL

# Verificar conectividad desde el contenedor
docker compose exec finance-supervincent python -c "import psycopg2; print('OK')"
```

### Error de conexión a Redis

```bash
# Verificar Redis
docker compose exec redis redis-cli ping

# Verificar desde el servicio
docker compose exec finance-supervincent python -c "import redis; r=redis.Redis.from_url('redis://redis:6379/0'); print(r.ping())"
```

### API Gateway no puede conectar a Finance Service

```bash
# Verificar que finance-supervincent está corriendo
docker compose ps finance-supervincent

# Verificar logs del Gateway
docker compose logs api-gateway

# Verificar conectividad entre contenedores
docker compose exec api-gateway ping finance-supervincent
```

## Próximas Mejoras

- [ ] Implementar autenticación JWT en el Gateway
- [ ] Agregar rate limiting por usuario
- [ ] Implementar circuit breaker para servicios externos
- [ ] Agregar métricas Prometheus
- [ ] Configurar logging centralizado
- [ ] Agregar tests de integración completos
- [ ] Implementar retry logic en el Gateway
- [ ] Agregar documentación OpenAPI/Swagger completa

## Referencias

- [SuperVincent README](../external_repos/supervincent/README.md)
- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [API Gateway Code](./api_gateway/)
- [Shared Helpers](./shared/)


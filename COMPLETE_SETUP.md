# Astramech - Setup Completo del Sistema Unificado

## 🎯 Visión General

Astramech es un sistema unificado que integra 7 agentes especializados:

1. **Marketing Google Ads** - Automatización de campañas Google Ads
2. **Marketing TikTok** - Análisis y generación de contenido TikTok
3. **LinkedIn Posting** - Comentarios automatizados en LinkedIn
4. **CRM + Email** - Gestión de leads y secuencias de email
5. **Cold Calling** - Llamadas salientes automatizadas con IA
6. **Finance SuperVincent** - Procesamiento de facturas e impuestos
7. **HR Clio** - Análisis de equipos y riesgo de burnout

## 📋 Prerrequisitos

- Docker y Docker Compose instalados
- Git
- Variables de entorno configuradas (ver `.env.example`)

## 🚀 Setup Paso a Paso

### 1. Clonar y Configurar

```bash
# Ya estás en el directorio Astramech
cd /Users/arielsanroj/Astramech

# Copiar variables de entorno
cp .env.example .env

# Editar .env con tus credenciales
nano .env  # o tu editor preferido
```

### 2. Variables de Entorno Críticas

Edita `.env` y configura estas variables mínimas:

```bash
# Base de datos
DATABASE_URL=postgresql+asyncpg://astramech:secret@postgres:5432/astramech
POSTGRES_PASSWORD=secret

# Message Queue
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/

# Cache
REDIS_URL=redis://redis:6379/0

# Finance Service
ALEGRA_EMAIL=tu_email@alegra.com
ALEGRA_TOKEN=tu_token_de_alegra

# External APIs (opcionales pero recomendados)
OPENAI_API_KEY=tu_openai_key
TWILIO_ACCOUNT_SID=tu_twilio_sid
TWILIO_AUTH_TOKEN=tu_twilio_token
DEEPGRAM_API_KEY=tu_deepgram_key
ELEVENLABS_API_KEY=tu_elevenlabs_key
```

### 3. Crear Directorios Necesarios

```bash
# Crear directorios para volúmenes
mkdir -p external_repos/supervincent/uploads
mkdir -p external_repos/callagent/uploads
mkdir -p external_repos/linkedinposting/browser/storage
mkdir -p external_repos/mailicpagent/data
mkdir -p external_repos/mailicpagent/config
mkdir -p external_repos/clioalphamodel/ml-service/models
mkdir -p external_repos/clioalphamodel/ml-service/data
```

### 4. Levantar Servicios Base

```bash
# Levantar servicios de infraestructura primero
docker-compose up -d postgres redis rabbitmq minio

# Verificar que están corriendo
docker-compose ps

# Esperar a que PostgreSQL esté saludable
docker-compose logs -f postgres
# Presiona Ctrl+C cuando veas "database system is ready to accept connections"
```

### 5. Construir y Levantar Servicios de Aplicación

```bash
# Construir todos los servicios (esto puede tardar varios minutos)
docker-compose build

# Levantar todos los servicios
docker-compose up -d

# Ver estado de todos los servicios
docker-compose ps
```

### 6. Verificar Servicios

```bash
# Health check del API Gateway
curl http://localhost:8000/

# Health check de cada servicio a través del Gateway
curl http://localhost:8000/api/v1/finance/health
curl http://localhost:8000/api/v1/hr/health
curl http://localhost:8000/api/v1/marketing/google-ads/health
curl http://localhost:8000/api/v1/linkedin/health
curl http://localhost:8000/api/v1/crm/health
curl http://localhost:8000/api/v1/calls/health
```

## 📊 Puertos de Servicios

| Servicio | Puerto Interno | Puerto Externo | URL Local |
|----------|---------------|----------------|-----------|
| API Gateway | 8000 | 8000 | http://localhost:8000 |
| PostgreSQL | 5432 | - | - |
| Redis | 6379 | 6379 | redis://localhost:6379 |
| RabbitMQ | 5672 | 5672 | amqp://localhost:5672 |
| RabbitMQ Management | 15672 | 15672 | http://localhost:15672 |
| MinIO | 9000-9001 | 9000-9001 | http://localhost:9000 |
| Finance SuperVincent | 8000 | - | http://finance-supervincent:8000 |
| HR Backend (Clio) | 3000 | 3000 | http://localhost:3000 |
| HR ML Service | 8001 | 8001 | http://localhost:8001 |
| Marketing Google Ads | 8080 | 8080 | http://localhost:8080 |
| Marketing TikTok | 8002 | 8002 | http://localhost:8002 |
| LinkedIn Posting | 8001 | 8003 | http://localhost:8003 |
| CRM Email | 5000 | 5000 | http://localhost:5000 |
| Cold Calling | 8000 | 8004 | http://localhost:8004 |

## 🔍 Verificación Completa

### Script de Verificación Automatizado

```bash
# Ejecutar script de verificación (si existe)
python scripts/verify_all_services.py

# O verificar manualmente cada servicio
```

### Verificación Manual

```bash
# 1. Verificar que todos los servicios están corriendo
docker-compose ps | grep -E "(Up|healthy)"

# 2. Verificar logs de errores
docker-compose logs --tail=50 | grep -i error

# 3. Verificar conectividad entre servicios
docker-compose exec api-gateway ping finance-supervincent
docker-compose exec api-gateway ping clio-hr-backend

# 4. Verificar base de datos
docker-compose exec postgres psql -U astramech -d astramech -c "SELECT version();"

# 5. Verificar Redis
docker-compose exec redis redis-cli ping

# 6. Verificar RabbitMQ
curl -u guest:guest http://localhost:15672/api/overview
```

## 🧪 Testing

### Tests de Integración

```bash
# Instalar dependencias de testing
pip install pytest httpx pytest-asyncio

# Ejecutar tests
pytest tests/ -v

# Tests específicos por servicio
pytest tests/test_finance_integration.py -v
pytest tests/test_marketing_integration.py -v
pytest tests/test_crm_integration.py -v
```

### Probar Endpoints Manualmente

```bash
# 1. Crear un lead en CRM
curl -X POST http://localhost:8000/api/v1/crm/leads \
  -H "Content-Type: application/json" \
  -d '{
    "contact_name": "John Doe",
    "email": "john@example.com",
    "company": "Acme Corp"
  }'

# 2. Procesar una factura
curl -X POST http://localhost:8000/api/v1/finance/invoices/process \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/app/uploads/invoice.pdf"
  }'

# 3. Analizar hotel para Google Ads
curl -X POST http://localhost:8000/api/v1/marketing/google-ads/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "email": "hotel@example.com",
    "hotel_url": "https://example-hotel.com"
  }'
```

## 🐛 Troubleshooting

### Servicio no inicia

```bash
# Ver logs del servicio
docker-compose logs -f <service-name>

# Reconstruir el servicio
docker-compose build --no-cache <service-name>
docker-compose up -d <service-name>
```

### Error de conexión a base de datos

```bash
# Verificar que PostgreSQL está corriendo
docker-compose ps postgres

# Verificar variables de entorno
docker-compose exec <service> env | grep DATABASE_URL

# Verificar conectividad
docker-compose exec <service> python -c "import psycopg2; print('OK')"
```

### Error de build

```bash
# Ver logs detallados del build
docker-compose build <service-name> --progress=plain 2>&1 | tee build.log

# Verificar Dockerfile
cat external_repos/<service>/Dockerfile

# Verificar requirements
cat external_repos/<service>/requirements.txt
```

### Servicios no se comunican

```bash
# Verificar que están en la misma red
docker network inspect astramech_default

# Verificar DNS resolution
docker-compose exec api-gateway nslookup finance-supervincent
```

## 📚 Documentación Adicional

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Arquitectura completa del sistema
- [MIGRATION_FINANCE_SUPERVINCENT.md](./MIGRATION_FINANCE_SUPERVINCENT.md) - Guía de migración de Finance
- [QUICK_START_FINANCE.md](./QUICK_START_FINANCE.md) - Inicio rápido Finance
- [STATUS_MIGRATION.md](./STATUS_MIGRATION.md) - Estado actual de migración

## 🎯 Próximos Pasos

Una vez que todos los servicios estén corriendo:

1. **Configurar autenticación JWT** en el API Gateway
2. **Implementar circuit breakers** para resiliencia
3. **Configurar métricas Prometheus** para observabilidad
4. **Integrar eventos RabbitMQ** entre servicios
5. **Configurar workflows CrewAI** en el orquestador

## ✅ Checklist Final

- [ ] Todos los servicios en `docker-compose ps` muestran "Up"
- [ ] API Gateway responde en `http://localhost:8000/`
- [ ] Todos los health checks pasan
- [ ] PostgreSQL acepta conexiones
- [ ] Redis responde
- [ ] RabbitMQ Management UI accesible
- [ ] MinIO accesible
- [ ] Tests de integración pasan
- [ ] Variables de entorno configuradas
- [ ] Directorios de volúmenes creados

---

**¡Sistema Astramech listo para usar!** 🚀


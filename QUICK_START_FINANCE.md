# Quick Start - Finance Service Integration

## 🚀 Inicio Rápido

### 1. Configurar Variables de Entorno

```bash
# Copiar template
cp .env.example .env

# Editar con tus valores
nano .env  # o tu editor preferido
```

**Variables mínimas requeridas**:
- `ALEGRA_EMAIL` - Tu email de Alegra
- `ALEGRA_TOKEN` - Tu token de API de Alegra

### 2. Levantar el Stack

```bash
# Opción 1: Script automatizado
./scripts/setup_local.sh

# Opción 2: Manual
docker compose up -d
```

### 3. Verificar Servicios

```bash
# Ver estado de todos los servicios
docker compose ps

# Ver logs del API Gateway
docker compose logs -f api-gateway

# Ver logs del servicio Finance
docker compose logs -f finance-supervincent
```

### 4. Ejecutar Verificación

```bash
# Instalar dependencias del script
pip install httpx

# Ejecutar verificación completa
python scripts/verify_finance_integration.py

# O verificar manualmente
curl http://localhost:8000/api/v1/finance/health
```

## 📋 Checklist de Verificación

- [ ] `.env` configurado con `ALEGRA_EMAIL` y `ALEGRA_TOKEN`
- [ ] Todos los servicios levantados (`docker compose ps`)
- [ ] PostgreSQL saludable (`docker compose exec postgres pg_isready`)
- [ ] Redis respondiendo (`docker compose exec redis redis-cli ping`)
- [ ] RabbitMQ accesible (http://localhost:15672 con guest/guest)
- [ ] API Gateway respondiendo (`curl http://localhost:8000/`)
- [ ] Finance Service saludable (`curl http://localhost:8000/api/v1/finance/health`)

## 🔧 Troubleshooting Rápido

### Servicio no inicia
```bash
docker compose logs finance-supervincent
docker compose restart finance-supervincent
```

### Error de conexión a base de datos
```bash
# Verificar que PostgreSQL está corriendo
docker compose ps postgres

# Verificar variables de entorno
docker compose exec finance-supervincent env | grep DATABASE_URL
```

### API Gateway no puede conectar a Finance
```bash
# Verificar que ambos servicios están corriendo
docker compose ps api-gateway finance-supervincent

# Verificar conectividad entre contenedores
docker compose exec api-gateway ping finance-supervincent
```

## 📚 Documentación Completa

Para más detalles, ver:
- [MIGRATION_FINANCE_SUPERVINCENT.md](./MIGRATION_FINANCE_SUPERVINCENT.md) - Guía completa de migración
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Arquitectura del sistema

## 🧪 Testing

```bash
# Ejecutar tests de integración
pytest tests/test_finance_integration.py -v

# Con coverage
pytest tests/test_finance_integration.py --cov=api_gateway --cov-report=html
```

## 🎯 Próximos Pasos

Una vez que el servicio esté funcionando:

1. **Probar procesamiento de facturas**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/finance/invoices/process \
     -H "Content-Type: application/json" \
     -d '{"file_path": "/app/uploads/invoice.pdf"}'
   ```

2. **Configurar eventos RabbitMQ** para integración con otros servicios

3. **Integrar con CrewAI Orchestrator** para workflows automatizados

4. **Agregar autenticación JWT** al API Gateway









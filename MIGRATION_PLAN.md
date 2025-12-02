# Plan de Migración - Estructura Monorepo

## 🎯 Objetivo

Reorganizar la estructura actual para seguir la arquitectura definida en `ARCHITECTURE.md`:

**Estructura Actual**:
```
Astramech/
├── external_repos/          # Repositorios como submodules
│   ├── supervincent/
│   ├── marketingagent/
│   ├── callagent/
│   └── ...
├── api_gateway/
├── shared/
└── ...
```

**Estructura Objetivo** (según ARCHITECTURE.md):
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

## 📋 Opciones de Migración

### Opción 1: Mover Repositorios (Recomendada)
Mover los repositorios de `external_repos/` a `agents/` con nombres normalizados.

**Ventajas**:
- Estructura limpia según arquitectura
- Nombres consistentes
- Más fácil de mantener

**Desventajas**:
- Requiere actualizar docker-compose.yml
- Requiere actualizar rutas en código

### Opción 2: Crear Symlinks
Crear symlinks desde `agents/` hacia `external_repos/`.

**Ventajas**:
- No requiere mover archivos
- Mantiene git submodules intactos

**Desventajas**:
- Puede causar problemas con Docker
- Estructura menos clara

### Opción 3: Mantener external_repos y crear agents/
Crear `agents/` con symlinks o wrappers que apunten a `external_repos/`.

**Ventajas**:
- Compatibilidad con estructura actual
- Fácil de implementar

**Desventajas**:
- Duplicación de estructura
- Menos limpio

## 🚀 Plan Recomendado: Opción 1 (Mover Repositorios)

### Paso 1: Crear estructura de agents/

```bash
# Crear directorio agents/
mkdir -p agents

# Crear subdirectorios con nombres normalizados
mkdir -p agents/marketing_googleads
mkdir -p agents/marketing_tiktok
mkdir -p agents/linkedinposting
mkdir -p agents/crm_email
mkdir -p agents/outbound_calling
mkdir -p agents/finance_supervincent
mkdir -p agents/hr_clio
```

### Paso 2: Mover contenido (o crear symlinks temporales)

**Opción A: Mover físicamente** (si no son git submodules):
```bash
mv external_repos/marketingagent/* agents/marketing_googleads/
mv external_repos/marketingagentcompanies/* agents/marketing_tiktok/
mv external_repos/linkedinposting/* agents/linkedinposting/
mv external_repos/mailicpagent/* agents/crm_email/
mv external_repos/callagent/* agents/outbound_calling/
mv external_repos/supervincent/* agents/finance_supervincent/
mv external_repos/clioalphamodel/* agents/hr_clio/
```

**Opción B: Si son git submodules, mantener y crear wrappers**:
```bash
# Crear README en cada agent/ que explique la ubicación
# Actualizar docker-compose.yml para apuntar a external_repos/ pero con nombres normalizados
```

### Paso 3: Actualizar docker-compose.yml

Cambiar los `context` de:
```yaml
context: external_repos/supervincent
```

A:
```yaml
context: agents/finance_supervincent
```

### Paso 4: Actualizar rutas en código

Buscar y reemplazar referencias a `external_repos/` por `agents/` en:
- docker-compose.yml
- Scripts de build
- Documentación
- CI/CD

## 🔄 Plan Alternativo: Mantener external_repos/ y Normalizar

Si prefieres mantener `external_repos/` (por ejemplo, si son git submodules), podemos:

1. **Mantener estructura actual** pero normalizar nombres en docker-compose.yml
2. **Crear wrappers en agents/** que apunten a external_repos/
3. **Actualizar documentación** para reflejar la estructura real

## 📝 Mapeo de Nombres

| Repositorio Original | Nombre Normalizado | Ruta en agents/ |
|----------------------|-------------------|-----------------|
| `marketingagent` | `marketing_googleads` | `agents/marketing_googleads/` |
| `marketingagentcompanies` | `marketing_tiktok` | `agents/marketing_tiktok/` |
| `linkedinposting` | `linkedinposting` | `agents/linkedinposting/` |
| `mailicpagent` | `crm_email` | `agents/crm_email/` |
| `callagent` | `outbound_calling` | `agents/outbound_calling/` |
| `supervincent` | `finance_supervincent` | `agents/finance_supervincent/` |
| `clioalphamodel` | `hr_clio` | `agents/hr_clio/` |

## ✅ Checklist de Migración

- [ ] Crear estructura `agents/`
- [ ] Decidir: mover archivos o mantener symlinks
- [ ] Actualizar `docker-compose.yml` con nuevos context paths
- [ ] Actualizar rutas en scripts
- [ ] Actualizar documentación
- [ ] Verificar que builds funcionan
- [ ] Actualizar `.gitignore` si es necesario
- [ ] Crear README.md en cada `agents/*/` explicando el servicio

## 🎯 Recomendación Final

**Para git submodules**: Mantener `external_repos/` pero crear estructura `agents/` con READMEs que expliquen la ubicación real. Actualizar docker-compose.yml para usar nombres consistentes.

**Para repositorios locales**: Mover a `agents/` con nombres normalizados.

¿Cómo procedemos?


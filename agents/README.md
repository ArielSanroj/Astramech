# Agents Directory

Este directorio contiene todos los agentes/microservicios de Astramech organizados según la arquitectura unificada.

## 📁 Estructura

Cada agente está organizado según ARCHITECTURE.md:

- `marketing_googleads/` → `external_repos/marketingagent` (Marketing Google Ads)
- `marketing_tiktok/` → `external_repos/marketingagentcompanies` (Marketing TikTok)
- `linkedinposting/` → `external_repos/linkedinposting` (LinkedIn Automation)
- `crm_email/` → `external_repos/mailicpagent` (CRM + Email Sequencer)
- `outbound_calling/` → `external_repos/callagent` (Cold Calling Agent)
- `finance_supervincent/` → `external_repos/supervincent` (Finance & Accounting)
- `hr_clio/` → `external_repos/clioalphamodel` (HR Analysis)

## 🔗 Symlinks

Los directorios en `agents/` son **symlinks** que apuntan a los repositorios reales en `external_repos/`. Esto permite:

1. ✅ Mantener los repositorios como git submodules
2. ✅ Tener una estructura consistente según ARCHITECTURE.md
3. ✅ Usar nombres normalizados en docker-compose.yml
4. ✅ Docker puede seguir symlinks sin problemas

## 📝 Uso en Docker Compose

En `docker-compose.yml`, los servicios usan:

```yaml
services:
  marketing-googleads:
    build:
      context: agents/marketing_googleads  # Symlink funciona perfectamente
```

## 🔄 Actualización de Repositorios

Para actualizar los git submodules:

```bash
git submodule update --init --recursive
```

Los symlinks seguirán funcionando automáticamente.

## 📚 Documentación

Cada agente tiene su propia documentación en su repositorio original en `external_repos/`.

# Fairness, explicabilidad y regulación (versión práctica)

Si este curso se conecta con crédito/seguros/fraude, este bloque es obligatorio en 2025–2026.

## 1) Fairness: qué se mide (y por qué no hay una sola definición)

Métricas comunes (depende del caso y del marco legal):
- **Disparate impact** (ratio de tasas de aprobación)
- **Equal opportunity** (igualar TPR entre grupos)
- **Equalized odds** (igualar TPR y FPR)
- **Calibration within groups** (probabilidades calibradas por grupo)

**Trade-off real:** es común que no puedas satisfacer todas a la vez.

## 2) Explicabilidad: para qué sirve de verdad

- **Global** (qué variables importan): para auditoría y control.
- **Local** (por qué esta decisión): para atención al cliente, disputas, compliance.

Herramientas típicas:
- SHAP (cuidado con correlaciones y leakage)
- Monotonic constraints en boosting (muy útil en riesgo)
- Model cards / datasheets

## 3) Regulación / gobernanza (alto nivel)

- GDPR / privacidad: propósito, minimización, retención, derecho de acceso/borrado (según jurisdicción).
- Banca (EE. UU.): **SR 11-7** (Model Risk Management) → documentación, validación independiente, monitoreo.
- Seguros: reglas locales (dependiendo país) sobre variables prohibidas/permitidas.

## 4) Errores caros que he visto
- “El modelo es preciso” pero no puedes explicar ni auditar → no se despliega.
- Variables “proxy” (ZIP code, device) → problemas de fairness.
- Cambios de datos → drift y sesgo sin darte cuenta.

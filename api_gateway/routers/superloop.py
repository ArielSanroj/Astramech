"""
Superloop router para el API Gateway (SUPERLOOP.md §6).

Expone el loop de negocio como HTTP. El Flask de company-efficiency-optimizer sigue
siendo la UI de upload que llama a estos endpoints. La aprobación (§6.4) es un endpoint
explícito con `aprobador` humano obligatorio (R1). ORCHESTRATE/VERIFY/LEARN se cierran
vía /resume sobre decisiones ya aprobadas.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/superloop", tags=["superloop"])


def _facade():
    # Import perezoso: el paquete superloop es top-level del repo.
    from superloop.facade import SuperloopFacade
    return SuperloopFacade()


class ObservePayload(BaseModel):
    seed: bool = True            # crear los productos-dominio si faltan


class ApprovePayload(BaseModel):
    decision_id: str
    aprobador: str               # humano obligatorio (R1)


@router.post("/observe")
def observe_decide(payload: ObservePayload):
    """Corre OBSERVE→DIAGNOSE→DECIDE y se detiene en APPROVE (R1)."""
    sl = _facade()
    if payload.seed:
        sl.seed_productos_dominios()
    return {"cards": sl.run_todos()}


@router.post("/approve")
def approve(payload: ApprovePayload):
    """Gate humano (§6.4, R1). Registra la aprobación en el Decision Ledger."""
    if not payload.aprobador:
        raise HTTPException(status_code=400, detail="aprobador humano requerido (R1)")
    sl = _facade()
    sl.aprobar(payload.decision_id, payload.aprobador)
    return {"decision_id": payload.decision_id, "estado_aprobacion": "aprobado",
            "aprobador": payload.aprobador}


@router.post("/resume")
def resume():
    """ORCHESTRATE→VERIFY→LEARN sobre decisiones aprobadas (cierra el loop, R8)."""
    return {"ciclos": _facade().resume_aprobados()}

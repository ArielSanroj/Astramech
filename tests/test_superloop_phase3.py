"""Fase 3 Astramech — cierre del loop: DECIDE → APPROVE(humano) → ORCHESTRATE→VERIFY→LEARN."""
from sqlalchemy import text

from superloop.facade import SuperloopFacade


def _url(tmp_path):
    return f"sqlite:///{tmp_path}/p3.db"


def _facade(tmp_path):
    sl = SuperloopFacade(db_url=_url(tmp_path),
                         datos_por_dominio={"finance": {"current_ratio": 0.8, "net_margin_pct": 2}})
    sl.seed_productos_dominios()
    sl.run_todos()
    return sl


def _una_decision(sl, dominio="prod_finance"):
    with sl.engine.connect() as conn:
        row = conn.execute(text(
            "SELECT decision_id, nivel_autonomia FROM superloop_decision_ledger "
            "WHERE producto_id = :p LIMIT 1"), {"p": dominio}).fetchone()
    return row


def test_resume_sin_aprobacion_no_cierra(tmp_path):
    sl = _facade(tmp_path)
    assert sl.resume_aprobados() == []


def test_loop_cierra_tras_aprobacion_y_R8(tmp_path):
    sl = _facade(tmp_path)
    dec = _una_decision(sl)
    assert dec is not None
    sl.aprobar(dec[0], aprobador="ariel@cliocircle.com")

    salidas = sl.resume_aprobados()
    assert len(salidas) >= 1
    s = next(x for x in salidas if x["decision_id"] == dec[0])
    assert s["ok"] is True and s["fase"] == "learn"
    assert s["siguiente_movimiento"] in {"scale", "iterate", "hold", "kill"}

    # LEARN escribió el aprendizaje (cierre del loop).
    with sl.engine.connect() as conn:
        row = conn.execute(text(
            "SELECT aprendizaje, siguiente_movimiento, accion_ejecutada "
            "FROM superloop_decision_ledger WHERE decision_id = :d"), {"d": dec[0]}).fetchone()
    assert row[0] and row[1] in {"scale", "iterate", "hold", "kill"} and row[2]

    # R8 — el aprendizaje queda disponible para el próximo DECIDE.
    aprendizajes = sl.ledger.ultimos_aprendizajes(dec[1] and "prod_finance" or "prod_finance")
    assert len(aprendizajes) >= 1


def test_ejecutor_gated_bloquea_nivel3_sin_mapeo(tmp_path):
    """Una decisión Nivel>=3 aprobada sin accion_externa/dispatch queda bloqueada (R1/§6.5)."""
    from superloop.domain.entities import DecisionRecomendada
    from superloop.domain.enums import NivelAutonomia, EstadoAprobacion
    sl = SuperloopFacade(db_url=_url(tmp_path))
    dec = DecisionRecomendada(
        decision_id="dn3", producto_id="prod_finance", fecha="2026-06-23T00:00:00Z",
        fase_origen="decide", decision_recomendada="contactar clientes",
        hipotesis="h", metrica_objetivo="m", criterio_exito="c", ventana_medicion="14d",
        nivel_autonomia=NivelAutonomia.EXTERNAL_ACTION)
    sl.ledger.registrar(dec)
    sl.aprobar("dn3", aprobador="ariel@cliocircle.com")
    res = sl.ejecutor.ejecutar({"decision_id": "dn3"})
    assert res["estado"] == "bloqueada"
    assert "no se improvisa" in res["bloqueada_razon"].lower() or "sin dispatch" in res["bloqueada_razon"].lower()

"""
E2E MVP Astramech — domain + persistencia SQLAlchemy (SQLite) + facade.

Corre el loop OBSERVE→DIAGNOSE→DECIDE deteniéndose en APPROVE (R1) e impone los
CHECK constraints R6/R1 a nivel de DB. (conftest.py añade el root al sys.path.)
"""
import pytest

from superloop.domain import phase_done
from superloop.facade import SuperloopFacade


def _sqlite_url(tmp_path):
    return f"sqlite:///{tmp_path}/superloop_test.db"


def test_phase_done_R6_R1_R3():
    ok, faltan = phase_done.decide_done({"hipotesis": "h", "nivel_autonomia": 1})
    assert ok is False and any("metrica_objetivo" in f for f in faltan)

    ok2, _ = phase_done.decide_done({
        "hipotesis": "h", "metrica_objetivo": "m", "criterio_exito": "c",
        "ventana_medicion": "14d", "nivel_autonomia": 1})
    assert ok2 is True

    ok3, faltan3 = phase_done.approve_done(
        {"estado_aprobacion": "aprobado", "nivel_autonomia": 3, "aprobador": None})
    assert ok3 is False and any("R1" in f for f in faltan3)


def test_schema_y_loop_se_detiene_en_approve(tmp_path):
    datos = {"finance": {"current_ratio": 0.9, "gross_margin_pct": 12, "net_margin_pct": 2}}
    sl = SuperloopFacade(db_url=_sqlite_url(tmp_path), datos_por_dominio=datos)
    creados = sl.seed_productos_dominios()
    assert creados == 5

    cards = sl.run_todos()
    assert len(cards) == 5
    finance = next(c for c in cards if "Finance" in c["producto"])
    assert finance["error"] is None
    assert finance["evidence_pack"]["detenido_en"] == "approve"
    for af in finance["evidence_pack"]["afirmaciones"]:
        assert af["etiqueta"] in {"HECHO", "INFERENCIA", "SUPUESTO", "PREGUNTA"}


def test_decision_ledger_persiste(tmp_path):
    from sqlalchemy import text
    sl = SuperloopFacade(db_url=_sqlite_url(tmp_path),
                         datos_por_dominio={"finance": {"current_ratio": 0.5}})
    sl.seed_productos_dominios()
    sl.run_todos()
    with sl.engine.connect() as conn:
        n = conn.execute(text("SELECT COUNT(*) FROM superloop_decision_ledger")).scalar()
        nreg = conn.execute(text("SELECT COUNT(*) FROM superloop_producto")).scalar()
    assert n == 5
    assert nreg == 5


def test_check_constraint_r6_bloquea_decide_sin_respaldo(tmp_path):
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError
    sl = SuperloopFacade(db_url=_sqlite_url(tmp_path))
    # SQLite necesita CHECK habilitado por defecto (lo está); inserción sin respaldo viola R6.
    with pytest.raises(IntegrityError):
        with sl.engine.begin() as conn:
            conn.execute(text(
                "INSERT INTO superloop_decision_ledger "
                "(decision_id, producto_id, fase_origen, nivel_autonomia) "
                "VALUES ('d1', 'prod_finance', 'decide', 1)"))

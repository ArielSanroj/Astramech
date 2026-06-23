"""§19.2 DIAGNOSE-as-debate en Astramech — dominio + integración en el loop."""
from sqlalchemy import text

from superloop.domain import debate
from superloop.facade import SuperloopFacade


def test_debate_rankea_y_etiqueta():
    hs = debate.debatir({"churn_risk": 0.8, "clientes_activos": 0}, [])
    assert hs and hs[0].nombre == "churn"
    for a in debate.afirmaciones_del_debate(hs):
        assert a.etiqueta.value in {"HECHO", "INFERENCIA", "SUPUESTO", "PREGUNTA"}


def test_debate_aparece_en_opciones_consideradas_del_ledger(tmp_path):
    sl = SuperloopFacade(db_url=f"sqlite:///{tmp_path}/d.db",
                         datos_por_dominio={"finance": {"current_ratio": 0.5, "net_margin_pct": 1}})
    sl.seed_productos_dominios()
    sl.run_todos()
    with sl.engine.connect() as c:
        opt = c.execute(text(
            "SELECT opciones_consideradas FROM superloop_decision_ledger "
            "WHERE producto_id='prod_finance' LIMIT 1")).scalar()
    import json
    ops = json.loads(opt)
    assert isinstance(ops, list) and ops
    # exactamente una opción marcada como elegida (la #1 del ranking)
    assert sum(1 for o in ops if o.get("elegida")) == 1
    assert "hipotesis" in ops[0]

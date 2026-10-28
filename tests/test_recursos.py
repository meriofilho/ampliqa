"""Textos, ajuda, NanoDrop, arquivo do experimento e um teste de fumaça de todas as telas (AppTest)."""
from pathlib import Path

import pandas as pd
import pytest

from ampliqa import analysis, experiment, help as faq, qpcr, quant, texts
from ampliqa.nanodrop import read_nanodrop
from ampliqa.quantstudio import read_results

ROOT = Path(__file__).parent.parent
DATA = Path(__file__).parent / "data" / "beatriz_results.txt"


def exp_beatriz():
    raw = read_results(DATA.read_bytes(), DATA.name)
    exp = experiment.new_experiment("Beatriz", "Teste")
    exp["quant"] = quant.example_table()
    exp["qpcr_raw"] = raw
    exp["qpcr_groups"] = qpcr.default_groups(raw["Amostra"])
    exp["qpcr_cfg"].update({"ref": "GAPDH", "controle": "A", "ordem_grupos": "A;B;C;D;E"})
    return exp


def test_textos_en_pt():
    an = analysis.run(exp_beatriz())
    assert an["ok"]
    for lang in ("en", "pt"):
        m = texts.methods(texts.METHODS_DEFAULTS, an["ref"], an["n_txt"], lang)
        assert "QuantStudio 3" in m and "NZY" in m and "RNeasy" in m
        r = texts.results(an["analyses"], an["summary"], an["control"], {}, lang)
        assert "BDNF" in r
        leg = texts.legend(an["genes"], an["ref"], an["n_txt"], "SEM", an["analyses"], lang)
        assert ("p < 0.05" in leg) if lang == "en" else ("p < 0,05" in leg)
        assert "0.5 *" not in leg and "0,5 *" not in leg
    assert texts.to_docx({"A": "x"}, "t")[:2] == b"PK"


def test_diagnostico_aponta_referencia_instavel_e_brancos():
    exp = exp_beatriz()
    ids = [i for i, _ in faq.diagnose(exp, experiment.results_tables(exp))]
    assert "ref_instavel" in ids  # GAPDH do grupo D ~2 ciclos acima
    assert "branco" in ids and "replicas" in ids and "conc_baixa" in ids


def test_busca_ajuda():
    assert faq.search("meu branco amplificou")[0]["id"] == "branco"
    assert faq.search("réplicas discrepantes")[0]["id"] == "replicas"


def test_nanodrop_provisorio():
    tsv = ("Sample ID\tUser ID\tDate\tTime\tNucleic Acid Conc.\tUnit\tA260\tA280\t260/280\t260/230\n"
           "A1\tlab\t10/10/2026\t10:00\t265,7\tng/µl\t6,6\t3,3\t1,98\t2,31\n"
           "A1\tlab\t10/10/2026\t10:01\t262,1\tng/µl\t6,5\t3,3\t1,99\t2,28\n"
           "B1\tlab\t10/10/2026\t10:02\t121,5\tng/µl\t3,0\t1,5\t1,95\t2,04\n")
    tab = read_nanodrop(tsv.encode("utf-8"), "nanodrop.tsv")
    assert list(tab["Código"]) == ["A1", "B1"]
    assert tab.iloc[0]["Conc. 2 (ng/µL)"] == pytest.approx(262.1)
    assert tab.iloc[0]["Grupo"] == "A" and pd.isna(tab.iloc[1]["Conc. 2 (ng/µL)"])


def test_arquivo_guarda_configuracoes():
    exp = exp_beatriz()
    exp["stats_cfg"] = {"metrica": "ΔCt", "bar_pontos": False, "bar_largura": 0.5, "rotulos": "A=Controle"}
    exp["qpcr_groups"]["Fator 2"] = "15 dpf"
    back = experiment.from_xlsx(experiment.to_xlsx(exp))
    assert back["stats_cfg"]["bar_pontos"] is False and back["stats_cfg"]["bar_largura"] == 0.5
    assert (back["qpcr_groups"]["Fator 2"] == "15 dpf").all()


@pytest.mark.parametrize("page", ["views/inicio.py", "views/quant_cdna.py", "views/qpcr.py", "views/estatistica.py",
                                  "views/textos.py", "views/ajuda.py"])
def test_todas_as_telas_abrem_sem_erro(page):
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60)
    at.session_state["exp"] = exp_beatriz()
    at.session_state["editor_ver"] = 0
    at.run()
    at.switch_page(page)
    at.run()
    assert not at.exception, [e.value for e in at.exception]

"""Interface bilíngue: toda frase marcada com t("...") tem tradução, os marcadores {x} batem e as telas abrem em
inglês com o experimento de exemplo."""
import ast
import re
from pathlib import Path

import pytest

from ampliqa import analysis, examples, experiment, help as faq, stats, texts
from ampliqa.locale_en import EN, FAQ_EN, PATTERNS
from ampliqa.params import QPCR_MIX

ROOT = Path(__file__).parent.parent
FILES = [ROOT / "app.py", *ROOT.glob("views/*.py"), *ROOT.glob("ampliqa/*.py")]


def _t_keys():
    keys = {}
    for f in FILES:
        for node in ast.walk(ast.parse(f.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "t" and node.args \
                    and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                keys.setdefault(node.args[0].value, f.name)
    return keys


def test_toda_frase_marcada_tem_traducao():
    missing = {k: f for k, f in _t_keys().items() if k not in EN}
    assert not missing, missing


def test_frases_usadas_por_variavel_tem_traducao():
    used = [stats.OUTLIER_GUIDE, stats.TWO_WAY_NOTE, *stats.METRICS, *QPCR_MIX, *examples.DOWNLOADS,
            *faq.REF_GROUPS, *analysis.TESTS, "SEM", "DP", "Asteriscos", "Letras", "Nenhuma", "Cheio", "Vazio",
            analysis.run(experiment.new_experiment())["motivo"]]
    assert [u for u in used if u not in EN] == []


def test_marcadores_iguais_nas_duas_linguas():
    for pt, en in EN.items():
        assert set(re.findall(r"{(\w+)}", pt)) == set(re.findall(r"{(\w+)}", en)), pt


def test_colunas_e_situacoes_dos_resultados_tem_traducao():
    e = examples.experiment_example()
    e["qpcr_cfg"]["ref"] = "actb1;cdnf"
    tabs = experiment.results_tables(e)
    cols = set()
    for k in ("quant", "pipetagem", "qpcr_resumo", "qpcr_brancos", "qpcr_alertas", "qpcr_estabilidade"):
        cols |= set(tabs[k].columns)
    an = analysis.run(e)
    cols |= set(analysis.overview(an).columns)
    a = next(iter(an["analyses"].values()))
    cols |= set(a["pares"].columns) | set(a["outliers"].columns)
    neutral = {"A260/230", "A260/230 1", "A260/230 2", "A260/280", "A260/280 1", "A260/280 2", "CV (%)",
               "Fold change", "G", "Gene", "M (geNorm)", "Outlier?", "Post hoc", "n", "p", "ΔCt", "ΔΔCt",
               "log2 fold change", "Eficiência (%)"}
    assert cols - set(EN) - neutral == set()
    for v in set(tabs["quant"]["Situação"]) | set(tabs["pipetagem"]["Situação"]) | set(tabs["qpcr_brancos"]["Situação"]):
        assert not v or v in EN or any(p.fullmatch(v) for p, _ in PATTERNS), v


def test_faq_em_ingles_completa():
    assert set(FAQ_EN) == {e["id"] for e in faq.FAQ}
    for e in FAQ_EN.values():
        assert {"titulo", "palavras", "causa", "solucao"} <= set(e)


def test_busca_da_ajuda_entende_ingles_e_portugues():
    assert faq.search("blank amplified")[0]["id"] == "branco"
    assert faq.search("branco amplificou")[0]["id"] == "branco"


def test_sample_types_en():
    assert all(len(v) == 2 for v in texts.SAMPLE_TYPES.values())


@pytest.mark.parametrize("page", ["views/inicio.py", "views/cronograma.py", "views/quant_cdna.py", "views/qpcr.py", "views/estatistica.py",
                                  "views/textos.py", "views/ajuda.py"])
def test_telas_em_ingles(page):
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60)
    at.session_state["exp"] = examples.experiment_example()
    at.session_state["editor_ver"] = 0
    at.session_state["lang"] = "en"
    at.run()
    at.switch_page(page)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    text = " ".join(str(m.value) for m in [*at.markdown, *at.caption, *at.info, *at.warning])
    for word in (" amostras ", " réplicas ", " Carregue ", " Confira "):
        assert word not in text, (page, word)

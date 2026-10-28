"""Estatística: confere os testes contra implementações de referência (pingouin, scikit-posthocs) e as regras de
recomendação. As bibliotecas de referência são só para teste (não fazem parte do app)."""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ampliqa import qpcr, stats
from ampliqa.quantstudio import read_results

DATA = Path(__file__).parent / "data" / "beatriz_results.txt"


def make(groups: dict):
    rows = [{"Amostra": f"{g}{i + 1}", "Grupo": g, "valor": v} for g, vals in groups.items() for i, v in enumerate(vals)]
    return pd.DataFrame(rows)


DF = make({"A": [5.1, 5.4, 5.0, 5.3], "B": [6.2, 6.0, 6.5, 6.4], "C": [5.2, 7.9, 6.8, 4.1]})


def test_anova_igual_scipy_e_pingouin():
    pg = pytest.importorskip("pingouin")
    r = stats.analyze(DF, ["A", "B", "C"], "A", test="ANOVA de uma via", post="Tukey", comparison="todos")
    ref = pg.anova(data=DF, dv="valor", between="Grupo")
    assert r["omnibus"]["valor"] == pytest.approx(ref["F"].iloc[0])
    assert r["omnibus"]["p"] == pytest.approx(ref["p_unc"].iloc[0] if "p_unc" in ref else ref["p-unc"].iloc[0])


def test_welch_e_games_howell_iguais_ao_pingouin():
    pg = pytest.importorskip("pingouin")
    r = stats.analyze(DF, ["A", "B", "C"], "A", test="ANOVA de Welch", post="Games-Howell", comparison="todos")
    ref = pg.welch_anova(data=DF, dv="valor", between="Grupo")
    assert r["omnibus"]["valor"] == pytest.approx(ref["F"].iloc[0], rel=1e-6)
    gh = pg.pairwise_gameshowell(data=DF, dv="valor", between="Grupo")
    pcol = "pval" if "pval" in gh else "p-tukey" if "p-tukey" in gh else gh.columns[-1]
    mine = {frozenset((a, b)): p for a, b, p in r["pares"][["Grupo 1", "Grupo 2", "p ajustado"]].to_numpy()}
    for _, row in gh.iterrows():
        assert mine[frozenset((row["A"], row["B"]))] == pytest.approx(row[pcol], abs=2e-3)


def test_dunn_holm_igual_scikit_posthocs():
    sp = pytest.importorskip("scikit_posthocs")
    r = stats.analyze(DF, ["A", "B", "C"], "A", test="Kruskal-Wallis", post="Dunn (Holm)", comparison="todos")
    ref = sp.posthoc_dunn(DF, val_col="valor", group_col="Grupo", p_adjust="holm")
    for a, b, p in r["pares"][["Grupo 1", "Grupo 2", "p ajustado"]].to_numpy():
        assert p == pytest.approx(ref.loc[a, b], rel=1e-6)


def test_dunnett_so_compara_com_controle():
    r = stats.analyze(DF, ["A", "B", "C"], "A", test="ANOVA de uma via", post="Dunnett", comparison="controle")
    assert set(r["pares"]["Grupo 1"]) == {"A"} and set(r["pares"]["Grupo 2"]) == {"B", "C"}


def test_recomendacao():
    normal = {"n": {"A": 3, "B": 3, "C": 3}, "shapiro_p": 0.6, "levene_p": 0.5}
    assert stats.recommend(normal, "controle")["posthoc"] == "Dunnett"
    assert stats.recommend(normal, "todos")["posthoc"] == "Tukey"
    het = {**normal, "levene_p": 0.01}
    assert stats.recommend(het)["teste"] == "ANOVA de Welch"
    nn = {**normal, "shapiro_p": 0.001}
    rec = stats.recommend(nn)
    assert rec["teste"] == "Kruskal-Wallis" and rec["posthoc"].startswith("Dunn")
    assert stats.recommend({"n": {"A": 3, "B": 3}, "shapiro_p": 0.5, "levene_p": 0.5})["teste"] == "Teste t de Student"


def test_letras():
    pares = pd.DataFrame([("A", "B", 0.001), ("A", "C", 0.3), ("B", "C", 0.2)],
                         columns=["Grupo 1", "Grupo 2", "p ajustado"])
    L = stats.letters(["A", "B", "C"], {"A": 1, "B": 3, "C": 2}, pares)
    assert L["A"] != L["B"] and set(L["C"]) & set(L["A"]) and set(L["C"]) & set(L["B"])


def test_grubbs_detecta_outlier_claro():
    df = make({"A": [1.0, 1.1, 0.9, 1.05, 0.95, 5.0]})
    g = stats.grubbs(df, ["A"])
    assert g.iloc[0]["Outlier?"] == "Sim" and g.iloc[0]["Amostra suspeita"] == "A6"


def test_metricas_dct_e_log2fc_dao_mesmo_p():
    raw = read_results(DATA.read_bytes(), DATA.name)
    res = qpcr.ddct(qpcr.summarize(raw), qpcr.default_groups(raw["Amostra"]), "GAPDH", "A")
    d1 = stats.gene_data(res, "BDNF", "ΔCt")
    d2 = stats.gene_data(res, "BDNF", "log2 fold change")
    order = ["A", "B", "C", "D", "E"]
    r1 = stats.analyze(d1, order, "A", test="ANOVA de uma via", post="Dunnett")
    r2 = stats.analyze(d2, order, "A", test="ANOVA de uma via", post="Dunnett")
    assert r1["omnibus"]["p"] == pytest.approx(r2["omnibus"]["p"])


def test_fator2_normaliza_por_controle_do_nivel():
    raw = read_results(DATA.read_bytes(), DATA.name)
    g = qpcr.default_groups(raw["Amostra"])
    g["Fator 2"] = ["15 dpf" if a in ("A1", "A2", "B1", "C1", "D1") else "45 dpf" for a in g["Amostra"]]
    g.loc[g["Amostra"] == "A3", "Fator 2"] = "45 dpf"
    res = qpcr.ddct(qpcr.summarize(raw), g, "GAPDH", "A")
    # a média do fold change do controle é ~1 dentro de cada nível
    for lvl in ("15 dpf", "45 dpf"):
        sub = res[(res["Grupo"] == "A") & (res["Fator 2"] == lvl) & (res["Gene"] == "BDNF")]
        assert np.log2(sub["Fold change"]).mean() == pytest.approx(0, abs=1e-9)


def test_two_way():
    rng = np.random.default_rng(1)
    rows = []
    for f2 in ("15", "45"):
        for g, eff in (("A", 0), ("B", 1)):
            for i in range(3):
                rows.append({"Grupo": g, "Fator 2": f2, "valor": 5 + eff + (0.5 if f2 == "45" else 0) + rng.normal(0, .1)})
    tab = stats.two_way(pd.DataFrame(rows))
    assert set(tab["Fonte"]) >= {"Grupo", "Fator 2", "Interação Grupo × Fator 2"}
    assert tab.set_index("Fonte").loc["Grupo", "p"] < 0.001

"""Quantificação no modelo do qBase (Hellemans et al. 2007), estabilidade das referências (geNorm) e critério de
réplicas técnicas do Auto-qPCR (Maussion et al. 2021)."""
import io

import numpy as np
import pandas as pd
import pytest

from ampliqa import analysis, examples, experiment, qpcr


def _toy():
    """2 grupos × 3 amostras, 3 genes; Cq escolhidos à mão."""
    cq = {
        "A1": {"r1": 18.0, "r2": 20.0, "g": 25.0}, "A2": {"r1": 18.2, "r2": 20.1, "g": 25.4},
        "A3": {"r1": 17.9, "r2": 19.8, "g": 24.8},
        "B1": {"r1": 18.1, "r2": 20.3, "g": 23.9}, "B2": {"r1": 18.4, "r2": 20.2, "g": 24.0},
        "B3": {"r1": 17.8, "r2": 19.9, "g": 23.5},
    }
    summ = pd.DataFrame([{"Amostra": s, "Gene": g, "Poços": 2, "Réplicas com Ct": 2, "Ct médio": v,
                          "Diferença entre réplicas": 0.1} for s, d in cq.items() for g, v in d.items()])
    groups = qpcr.default_groups(list(cq))
    return cq, summ, groups


def test_uma_referencia_e100_igual_ao_ddct_classico():
    cq, summ, groups = _toy()
    res = qpcr.ddct(summ, groups, "r1", "A").set_index(["Amostra", "Gene"])
    dct = {s: d["g"] - d["r1"] for s, d in cq.items()}
    ctrl = np.mean([dct[s] for s in ("A1", "A2", "A3")])
    for s in cq:
        assert res.loc[(s, "g"), "ΔCt"] == pytest.approx(dct[s])
        assert res.loc[(s, "g"), "ΔΔCt"] == pytest.approx(dct[s] - ctrl)
        assert res.loc[(s, "g"), "Fold change"] == pytest.approx(2 ** -(dct[s] - ctrl))


def test_duas_referencias_media_geometrica_e_eficiencia():
    cq, summ, groups = _toy()
    E = {"r1": 1.95, "r2": 2.0, "g": 1.92}
    res = qpcr.ddct(summ, groups, "r1;r2", "A", {"r1": 95, "g": 92}).set_index(["Amostra", "Gene"])
    ctrl = ["A1", "A2", "A3"]
    cal = {g: np.mean([cq[s][g] for s in ctrl]) for g in E}
    for s in cq:
        rq = {g: E[g] ** (cal[g] - cq[s][g]) for g in E}
        nf = np.sqrt(rq["r1"] * rq["r2"])           # média geométrica (Hellemans 2007, eq. 6–7)
        assert res.loc[(s, "g"), "Fold change"] == pytest.approx(rq["g"] / nf)
        assert res.loc[(s, "g"), "Eficiência (%)"] == pytest.approx(92)
    # ΔΔCt continua sendo ΔCt − média do ΔCt do controle (logo, testar ΔCt = testar log2 fold change)
    g = res.xs("g", level="Gene")
    assert np.allclose(g["ΔΔCt"], g["ΔCt"] - g.loc[ctrl, "ΔCt"].mean())
    assert np.allclose(g["log2 fold change"], -g["ΔΔCt"])


def test_referencia_faltando_em_uma_amostra_nao_inventa_valor():
    _, summ, groups = _toy()
    summ = summ[~((summ["Amostra"] == "B1") & (summ["Gene"] == "r2"))]
    res = qpcr.ddct(summ, groups, "r1;r2", "A").set_index(["Amostra", "Gene"])
    assert np.isnan(res.loc[("B1", "g"), "Fold change"])
    assert np.isfinite(res.loc[("B2", "g"), "Fold change"])


def test_estabilidade_genorm_manual():
    cq, summ, groups = _toy()
    est = qpcr.ref_stability(summ, groups, ["r1", "r2", "g"]).set_index("Gene")
    A = pd.DataFrame(cq).T                       # log2 RQ com E = 2 é −Cq (o calibrador se cancela no geNorm)
    def V(p, q):
        return np.std(-(A[p] - A[q]), ddof=1)
    assert est.loc["r1", "M (geNorm)"] == pytest.approx((V("r1", "r2") + V("r1", "g")) / 2)
    assert est.loc["g", "M (geNorm)"] > est.loc["r1", "M (geNorm)"]   # g é o gene que muda entre os grupos
    nrq = 2.0 ** -(A["r2"] - A.mean(axis=1))   # NRQ = RQ normalizado pela média geométrica das referências
    assert est.loc["r2", "CV (%)"] == pytest.approx(nrq.std(ddof=1) / nrq.mean() * 100)
    assert est.loc["r1", "Avaliação"] == "Estável"
    assert qpcr.ref_stability(summ, groups, "r1").empty


def _reps(values, sample="X1", gene="g"):
    return pd.DataFrame({"Poço": [f"w{i}" for i in range(len(values))], "Amostra": sample, "Gene": gene,
                         "Ct": values, "Omitir": False})


def test_auto_qpcr_remove_replica_distante():
    d = qpcr.auto_outliers(_reps([20.0, 20.1, 22.0]))
    assert list(d["Outlier"]) == [False, False, True]


def test_auto_qpcr_nao_mexe_em_duplicata_nem_em_replicas_boas():
    assert not qpcr.auto_outliers(_reps([20.0, 21.5]))["Outlier"].any()
    assert not qpcr.auto_outliers(_reps([20.0, 20.1, 20.2]))["Outlier"].any()


def test_auto_qpcr_preserva_variacao_sem_outlier_claro():
    vals = [20.0, 20.5, 21.0]                    # DP 0,5 mas média = mediana: nenhuma réplica é "a errada"
    assert not qpcr.auto_outliers(vals and _reps(vals))["Outlier"].any()
    assert qpcr.auto_outliers(_reps(vals), preserve=False)["Outlier"].sum() == 1


def test_auto_qpcr_respeita_proporcao_maxima():
    d = qpcr.auto_outliers(_reps([20.0, 21.0, 22.5, 24.5]), preserve=False)
    assert d["Outlier"].sum() <= 2 and (~d["Outlier"]).sum() >= 2


def test_experimento_com_eficiencia_outlier_e_prism():
    e = examples.experiment_example()
    e["qpcr_cfg"].update({"eficiencias": "bdnf=95;sox2=102", "outlier_auto": True})
    e2 = experiment.from_xlsx(experiment.to_xlsx(e))
    assert e2["qpcr_cfg"]["outlier_auto"] is True
    assert qpcr.eff_map(e2["qpcr_cfg"]["eficiencias"]) == pytest.approx({"bdnf": 1.95, "sox2": 2.02})
    an = analysis.run(e2)
    assert an["ok"] and an["eff"] and an["ref"] == [examples.REF]
    book = pd.read_excel(io.BytesIO(analysis.prism_xlsx(an)), sheet_name=None)
    assert {"bdnf", "sox2", "cdnf", "Dados_limpos"} <= set(book)
    assert list(book["bdnf"].columns) == an["order"] and len(book["bdnf"]) == 3


def test_eff_map_ignora_valores_invalidos():
    assert qpcr.eff_map("a=98,5;b=;c=abc;d=300") == pytest.approx({"a": 1.985})

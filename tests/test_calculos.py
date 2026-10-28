"""Testes dos cálculos com valores conferidos nas planilhas-anexo dos POPs e na corrida real da Beatriz."""
import io
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ampliqa import experiment, qpcr, quant
from ampliqa.quantstudio import read_results

DATA = Path(__file__).parent / "data" / "beatriz_results.txt"


# ------------------------------------------------------------------ quantificação → cDNA
def test_quant_volumes_e_situacao():
    res = quant.compute(quant.example_table())
    a1 = res.iloc[0]
    assert a1["Conc. média (ng/µL)"] == pytest.approx(263.9)
    assert a1["3º RNA (µL)"] == pytest.approx(500 / 263.9)
    assert a1["2º H2O DEPC (µL)"] == pytest.approx(8 - 500 / 263.9)
    assert a1["1º Mix comum (µL)"] == 12
    assert list(res["Situação"]) == [quant.PRONTO, quant.PRONTO, quant.PRONTO, quant.PRONTO, quant.INSUF, quant.DILUIR]
    assert res.iloc[2]["Qualidade"] == quant.RESSALVA


def test_mix_comum():
    res = quant.compute(quant.example_table())
    m = quant.mix_summary(res)
    assert m["amostras_prontas"] == 4 and m["reacoes"] == 5
    assert m["mm_total"] == pytest.approx(55.0) and m["em_total"] == pytest.approx(11.0)


def test_linhas_vazias_sao_ignoradas():
    res = quant.compute(quant.empty_table(3))
    assert (res["Situação"] == "").all()


# ------------------------------------------------------------------ leitura QuantStudio
def test_leitura_resultados():
    raw = read_results(DATA.read_bytes(), DATA.name)
    assert len(raw) == 96
    assert set(raw["Gene"]) == {"GAPDH", "BDNF", "TH1", "NMDA"}
    assert raw.loc[0, "Ct"] == pytest.approx(21.180)
    assert raw["Ct"].isna().sum() == 3  # Undetermined


def test_leitura_xlsx_com_cabecalho():
    raw = read_results(DATA.read_bytes(), DATA.name)
    buf = io.BytesIO()
    meta = pd.DataFrame([["Experiment Name", "teste"], [None, None]])
    with pd.ExcelWriter(buf, engine="openpyxl") as xw:
        meta.to_excel(xw, sheet_name="Results", index=False, header=False)
        tab = raw.rename(columns={"Poço": "Well Position", "Amostra": "Sample Name", "Gene": "Target Name",
                                  "Ct": "CT", "Omitir": "Omit"})
        tab.to_excel(xw, sheet_name="Results", index=False, startrow=3)
    raw2 = read_results(buf.getvalue(), "corrida.xlsx")
    assert len(raw2) == 96 and raw2["Ct"].sum() == pytest.approx(raw["Ct"].sum())


# ------------------------------------------------------------------ ΔΔCt (dados reais)
@pytest.fixture
def beatriz():
    raw = read_results(DATA.read_bytes(), DATA.name)
    groups = qpcr.default_groups(raw["Amostra"], 1)
    summ = qpcr.summarize(raw)
    res = qpcr.ddct(summ, groups, "GAPDH", "A")
    return raw, summ, res


def test_fold_change_d1(beatriz):
    _, _, res = beatriz
    d1 = res[res["Amostra"] == "D1"].set_index("Gene")["Fold change"]
    assert d1["GAPDH"] == pytest.approx(1.0)
    assert d1["BDNF"] == pytest.approx(1.216, abs=1e-3)
    assert d1["TH1"] == pytest.approx(7.396, abs=1e-3)
    assert d1["NMDA"] == pytest.approx(13.071, abs=1e-3)


def test_resumo_grupo(beatriz):
    _, _, res = beatriz
    s = qpcr.group_summary(res).set_index(["Gene", "Grupo"])
    assert s.loc[("BDNF", "B"), "Fold change médio"] == pytest.approx(0.233, abs=1e-3)
    assert s.loc[("NMDA", "D"), "Fold change médio"] == pytest.approx(5.085, abs=1e-3)
    assert s.loc[("BDNF", "A"), "Desvio padrão"] == pytest.approx(0.104, abs=1e-3)
    assert s.loc[("BDNF", "A"), "n"] == 3


def test_brancos(beatriz):
    raw, _, _ = beatriz
    b = qpcr.blanks_check(raw).set_index("Gene")["Situação"]
    assert b["GAPDH"].startswith("OK") and b["BDNF"].startswith("OK")
    assert b["TH1"].startswith("ATENÇÃO") and b["NMDA"].startswith("ATENÇÃO")


def test_alertas_replicas(beatriz):
    _, summ, _ = beatriz
    f = qpcr.flags(summ, 0.5)
    assert len(f[f["Alerta"].str.startswith("Diferença")]) == 16


# ------------------------------------------------------------------ placa
def test_placa_padrao_pop03():
    samples = [f"S{i}" for i in range(1, 12)]
    plan, n = qpcr.plan_plate(samples, ["G1", "G2", "G3", "G4"])
    assert n == 1 and len(plan) == 96
    g1 = plan[plan["Gene"] == "G1"]
    assert list(g1["Poço"])[:2] == ["A1", "A2"] and list(g1["Amostra"])[-2:] == ["NTC", "BcDNA"]
    assert list(g1["Poço"])[-1] == "B12"
    mix = qpcr.mix_per_gene(plan, "Econômico (10 µL)").set_index("Gene")
    assert mix.loc["G1", "SYBR (µL)"] == pytest.approx(132.0)


# ------------------------------------------------------------------ arquivo do experimento
def test_salvar_e_carregar(beatriz):
    raw, _, _ = beatriz
    exp = experiment.new_experiment("Teste", "Fulano")
    exp["quant"] = quant.example_table()
    exp["qpcr_raw"] = raw
    exp["qpcr_groups"] = qpcr.default_groups(raw["Amostra"], 1)
    exp["qpcr_cfg"].update({"ref": "GAPDH", "controle": "A", "ordem_grupos": "A;B;C;D;E"})
    data = experiment.to_xlsx(exp)
    back = experiment.from_xlsx(data)
    assert back["meta"]["Experimento"] == "Teste"
    assert len(back["qpcr_raw"]) == 96
    r1 = experiment.results_tables(exp)["qpcr"]["Fold change"].sum()
    r2 = experiment.results_tables(back)["qpcr"]["Fold change"].sum()
    assert r1 == pytest.approx(r2)
    q1 = quant.compute(back["quant"])
    assert list(q1["Situação"])[:6] == list(quant.compute(quant.example_table())["Situação"])

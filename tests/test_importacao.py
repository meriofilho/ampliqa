"""Importação de resultados: QuantStudio, Rotor-Gene Q e tabelas genéricas (arquivos reais do laboratório)."""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ampliqa import importers, qpcr

DATA = Path(__file__).parent / "data"
EXAMPLES = Path(__file__).parent.parent / "example-data"


def read(path: Path):
    return importers.read_file(path.read_bytes(), path.name)


# ------------------------------------------------------------------ todos os arquivos de exemplo
@pytest.mark.skipif(not EXAMPLES.exists(), reason="pasta example-data ausente")
@pytest.mark.parametrize("path", sorted(EXAMPLES.glob("*")) if EXAMPLES.exists() else [], ids=lambda p: p.name)
def test_todos_os_exemplos_sao_lidos(path):
    r = read(path)
    assert r["formato"] in ("QuantStudio", "Rotor-Gene Q", "Tabela genérica")
    if r["raw"] is not None:
        assert len(r["raw"]) > 0 and r["raw"]["Ct"].notna().sum() > 0
    else:
        assert len(r["poços"]) > 0 and len(r["blocos"]) > 0


# ------------------------------------------------------------------ Rotor-Gene
def test_rotorgene_casp3_bcl2_genes_pelo_nome_do_arquivo():
    r = read(DATA / "rotorgene_casp3_bcl2.csv")
    assert r["formato"] == "Rotor-Gene Q"
    blk = r["blocos"]
    assert list(blk["Gene"]) == ["casp3", "bcl2"]
    assert list(blk["Poços"]) == ["1–44", "45–64"]
    assert blk["Amostras com código"].all()
    raw = importers.build_rotorgene_raw(r["poços"], blk)
    assert len(raw) == 64
    casp3 = raw[raw["Gene"] == "casp3"]
    assert list(dict.fromkeys(casp3["Amostra"]))[:3] == ["A1", "A2", "A3"]
    bcl2 = raw[raw["Gene"] == "bcl2"]
    assert list(dict.fromkeys(bcl2["Amostra"]))[0] == "E1"
    assert casp3.iloc[0]["Ct"] == pytest.approx(17.57)
    # poço "NEG (Multi Ct)" e brancos sem Ct
    assert raw[raw["Amostra"] == "BRANCO"]["Ct"].notna().sum() == 1  # só o 27,81


def test_rotorgene_gene_parecido_com_codigo_nao_vira_amostra():
    r = read(DATA / "rotorgene_bdnf_sox2_sox3.csv")
    blk = r["blocos"]
    assert list(blk["Gene"]) == ["bdnf", "sox2", "sox3"]
    assert not blk["Amostras com código"].any()


def test_rotorgene_virgula_decimal_e_lista_de_amostras():
    r = read(DATA / "rotorgene_actb_shha_cdnf.csv")
    blk = r["blocos"]
    assert list(blk["Gene"]) == ["bact", "shha", "cdnf"]
    w = r["poços"]
    assert w.iloc[0]["Ct"] == pytest.approx(11.80)
    amostras = ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"]
    raw = importers.build_rotorgene_raw(w, blk, amostras, reps=2)
    bact = raw[raw["Gene"] == "bact"]
    assert list(bact["Amostra"][:4]) == ["A1", "A1", "A2", "A2"]
    assert list(bact["Amostra"][-2:]) == ["BRANCO", "BRANCO"]
    # análise completa a partir do Rotor-Gene
    groups = qpcr.default_groups(raw["Amostra"])
    res = qpcr.ddct(qpcr.summarize(raw), groups, "bact", "A")
    assert res["Fold change"].notna().sum() == 27  # 9 amostras × 3 genes
    a = res[(res["Grupo"] == "A") & (res["Gene"] == "shha")]["Fold change"]
    assert np.exp(np.log(a).mean()) == pytest.approx(1.0, abs=0.3)
    bl = qpcr.blanks_check(raw).set_index("Gene")["Situação"]
    assert bl["bact"].startswith("ATENÇÃO")  # branco com Ct 28,35


# ------------------------------------------------------------------ brancos com nomes variados
def test_brancos_com_numero_e_marcacao_manual():
    samples = ["A1", "A2", "BRANCO1", "BRANCO2", "NTC", "B"]
    g = qpcr.default_groups(samples)
    flags = dict(zip(g["Amostra"], g["Branco"]))
    assert flags["BRANCO1"] and flags["BRANCO2"] and flags["NTC"]
    assert not flags["B"]  # "B" sozinho é ambíguo: o usuário marca na tabela de grupos
    g.loc[g["Amostra"] == "B", "Branco"] = True
    assert "B" in qpcr.blank_names(g)
    assert list(qpcr.sample_groups(g)["Amostra"]) == ["A1", "A2"]


# ------------------------------------------------------------------ tabela genérica
def test_tabela_generica_longa_csv():
    csv = "Amostra;Gene;Ct\nA1;actb;18,2\nA1;actb;18,4\nA1;bdnf;24,1\nBRANCO;actb;Undetermined\n"
    r = importers.read_file(csv.encode(), "minha_tabela.csv")
    assert r["formato"] == "Tabela genérica"
    assert len(r["raw"]) == 4 and r["raw"]["Ct"].isna().sum() == 1
    assert r["raw"].iloc[0]["Ct"] == pytest.approx(18.2)


def test_tabela_generica_larga_com_grupos():
    csv = "Amostra;Grupo;actb;bdnf\n1;CONTROLE;18,1;24,0\n2;CONTROLE;18,3;24,2\n3;TRATADO;18,2;23,1\n"
    r = importers.read_file(csv.encode(), "larga.csv")
    assert set(r["raw"]["Gene"]) == {"actb", "bdnf"}
    g = qpcr.default_groups(r["raw"]["Amostra"], known=r["grupos"])
    assert dict(zip(g["Amostra"], g["Grupo"])) == {"1": "CONTROLE", "2": "CONTROLE", "3": "TRATADO"}

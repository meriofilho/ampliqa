"""Dados de exemplo fictícios e referências da central de ajuda."""
import re

import pytest

from ampliqa import analysis, examples, experiment, help as faq, importers
from ampliqa.nanodrop import read_nanodrop


@pytest.mark.parametrize("label", list(examples.DOWNLOADS))
def test_arquivos_de_exemplo_sao_lidos(label):
    fname, fn, _ = examples.DOWNLOADS[label]
    r = importers.read_file(fn(), fname)
    raw = r["raw"] if r["raw"] is not None else importers.build_rotorgene_raw(r["poços"], r["blocos"])
    assert list(dict.fromkeys(raw["Gene"])) == examples.GENES
    assert len(raw) == 80


def test_exemplo_completo_e_didatico():
    e = examples.experiment_example()
    an = analysis.run(e)
    ov = analysis.overview(an).set_index("Gene")
    assert set(ov["Teste"]) == {"ANOVA de uma via"} and set(ov["Post hoc"]) == {"Dunnett"}
    assert ov.loc["bdnf", "p"] < 0.05 and ov.loc["sox2", "p"] < 0.05 and ov.loc["cdnf", "p"] > 0.05
    assert faq.diagnose(e, experiment.results_tables(e)) == []
    fc = an["summary"].set_index(["Gene", "Grupo"])["Fold change médio"]
    assert fc[("bdnf", "C")] < 1 < fc[("sox2", "C")]


def test_nanodrop_de_exemplo():
    tab = read_nanodrop(examples.file_nanodrop(), "exemplo_nanodrop.tsv")
    assert list(tab["Código"]) == examples.SAMPLES


def test_referencias_validas():
    for key, (text, doi) in faq.REFS.items():
        assert re.match(r"^10\.\d{4,9}/\S+$", doi), key
        assert "(" in text and ")" in text
    for eid, keys in faq.FAQ_REFS.items():
        faq.entry(eid)
        assert all(k in faq.REFS for k in keys)
    for keys in faq.REF_GROUPS.values():
        assert all(k in faq.REFS for k in keys)
    assert "doi.org/10.1093/clinchem/hvaf043" in faq.entry_markdown(faq.entry("replicas"))
    assert "drive.google.com" in faq.entry_markdown(faq.entry("branco"))

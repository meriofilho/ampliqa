"""Desenho do experimento (tela Início): espécies, tecidos, códigos das amostras e texto de métodos."""
from ampliqa import design, examples, experiment, texts
from ampliqa.locale_en import EN


def test_cada_especie_tem_tecidos_traduzidos():
    for sp, info in design.SPECIES.items():
        assert info["tecidos"] and design.OUTRO == design.tissues_for(sp)[-1]
        assert all(ti in design.TISSUES for ti in info["tecidos"]), sp
        assert info["en"]
    assert design.tissues_for("Planária") == [design.OUTRO]


def test_codigos_das_amostras():
    assert design.sample_codes(3, 2) == ["A1", "A2", "B1", "B2", "C1", "C2"]
    assert len(design.sample_codes(30, 1)) == 26


def test_metodos_com_e_sem_pool():
    meta = {"Espécie": "Camundongo (Mus musculus)", "Tecido": "Hipocampo", "Indivíduos por pool": "1"}
    cfg = design.methods_from(meta)
    en = texts.methods(cfg, "actb", 4, "en")
    pt = texts.methods(cfg, "actb", 4, "pt")
    assert "4 biological replicates per group (hippocampi of mice (Mus musculus))" in en
    assert "4 réplicas biológicas por grupo (hipocampos de camundongos (Mus musculus))" in pt
    cfg = design.methods_from({"Espécie": "Zebrafish (Danio rerio)", "Tecido": "Cérebro", "Indivíduos por pool": 5})
    assert "3 pools per group, each containing 5 brains of zebrafish (Danio rerio)" in texts.methods(cfg, "a", 3, "en")


def test_cultura_de_celulas_sem_especie_no_texto():
    cfg = design.methods_from({"Espécie": "Cultura de células", "Tecido": "Linhagem celular", "Indivíduos por pool": 1})
    en = texts.methods(cfg, "gapdh", 3, "en")
    assert "3 biological replicates per group (cell line cultures)." in en


def test_especie_digitada_vai_para_o_texto():
    cfg = design.methods_from({"Espécie": "Planária (Schmidtea mediterranea)", "Tecido": "Animal inteiro",
                               "Indivíduos por pool": 3})
    assert "3 animal inteiro of Planária (Schmidtea mediterranea)" in texts.methods(cfg, "a", 2, "en")


def test_desenho_salvo_e_lido_do_arquivo():
    e = examples.experiment_example()
    e2 = experiment.from_xlsx(experiment.to_xlsx(e))
    d = design.plan(e2["meta"])
    assert d == {"especie": "Zebrafish (Danio rerio)", "tecido": "Larva inteira", "grupos": 3, "por_grupo": 3,
                 "por_pool": 10}


def test_arquivo_antigo_sem_desenho():
    assert design.plan({"Espécie / tecido": "zebrafish"})["por_pool"] == 1
    old = texts.methods({"tipo_amostra": "Larvas inteiras"}, "a", 3, "en")
    assert "10 whole larvae" in old


def test_rotulos_em_ingles():
    assert design.LABELS_EN["Camundongo (Mus musculus)"] == "Mouse (Mus musculus)"
    assert "Nº de grupos" in EN

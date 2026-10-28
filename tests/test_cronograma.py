"""Planejamento (cronograma, WhatsApp, Google Agenda) e figuras dentro do relatório .docx."""
import io
from datetime import date
from urllib.parse import parse_qs, urlparse

import pandas as pd
import pytest

from ampliqa import analysis, examples, experiment, schedule, texts


def _cron():
    return schedule.normalize(pd.DataFrame([
        {"Data": "19/06/2026", "Etapa": "qPCRs em si das amostras do estudo", "Detalhes": "", "Observação": "",
         "Responsável": "", "Convidados": "ana@ufrn.br, bia@ufrn.br"},
        {"Data": "24/06/2026", "Etapa": "qPCRs em si das amostras do estudo", "Detalhes": "amostras que precisarem "
         "repetir e finalização", "Observação": "dependendo dos resultados de sexta, esse dia pode ser dispensado",
         "Responsável": "", "Convidados": ""},
        {"Data": "26/06/2026", "Etapa": "Análise dos resultados e gráficos do estudo", "Detalhes": "",
         "Observação": "", "Responsável": "", "Convidados": ""},
    ]))


def test_mensagem_no_formato_do_laboratorio():
    msg = schedule.whatsapp(_cron())
    assert msg == ("📅 19/06 - Sexta-feira\nqPCRs em si das amostras do estudo\n\n"
                   "📅 24/06 - Quarta-feira\nqPCRs em si das amostras do estudo (amostras que precisarem repetir e "
                   "finalização)\n*dependendo dos resultados de sexta, esse dia pode ser dispensado\n\n"
                   "📅 26/06 - Sexta-feira\nAnálise dos resultados e gráficos do estudo")
    assert schedule.whatsapp(_cron(), "Teste", "en").startswith("🧬 *Teste* – schedule\n\n📅 19/06 - Friday")
    assert schedule.whatsapp_link("a b").endswith("a%20b")


def test_sugestao_pula_fim_de_semana():
    cron = schedule.suggest(date(2026, 6, 19), qpcr_days=2)     # sexta-feira
    dias = list(cron["Data"].dt.date)
    assert all(d.weekday() < 5 for d in dias)
    assert dias == sorted(dias) and len(cron) == 6
    assert "dispensado" in cron.iloc[-2]["Observação"]
    assert schedule.suggest(date(2026, 6, 20)).iloc[0]["Data"].date() == date(2026, 6, 22)   # sábado → segunda
    assert "PO.OPE.04" in schedule.suggest(date(2026, 6, 1), efficiency=True).iloc[2]["Etapa"]


def test_links_do_google_agenda():
    links = schedule.google_links(_cron(), "Exp X")
    assert len(links) == 3
    q = parse_qs(urlparse(links[0][2]).query)
    assert q["action"] == ["TEMPLATE"] and q["dates"] == ["20260619/20260620"]
    assert q["add"] == ["ana@ufrn.br,bia@ufrn.br"]
    assert "Exp X" in q["text"][0]
    assert "add" not in parse_qs(urlparse(links[1][2]).query)


def test_arquivo_ics():
    txt = schedule.ics(_cron(), "Exp, X").decode("utf-8")
    assert txt.startswith("BEGIN:VCALENDAR\r\n") and txt.count("BEGIN:VEVENT") == 3
    assert "DTSTART;VALUE=DATE:20260624" in txt and "mailto:bia@ufrn.br" in txt
    assert "Exp\\, X" in txt


def test_cronograma_salvo_no_arquivo_do_experimento():
    e = examples.experiment_example()
    e["cronograma"] = _cron()
    e2 = experiment.from_xlsx(experiment.to_xlsx(e))
    assert list(e2["cronograma"]["Data"].dt.date) == [date(2026, 6, 19), date(2026, 6, 24), date(2026, 6, 26)]
    assert e2["cronograma"].iloc[0]["Convidados"] == "ana@ufrn.br, bia@ufrn.br"
    assert schedule.normalize(None).empty


def test_relatorio_com_figuras_escolhidas():
    docx = pytest.importorskip("docx")
    e = examples.experiment_example()
    e["stats_cfg"] = {"fig_genes_barras": "sox2", "fig_genes_heatmap": "bdnf;sox2", "bar_paleta": "Fishlab"}
    an = analysis.run(e)
    figs = analysis.report_figures(an, an["cfg"])
    assert [n for n, _ in figs] == ["barras", "heatmap"]
    import matplotlib.pyplot as plt
    from ampliqa import figures
    pngs = [figures.to_bytes(f, "png", 100) for _, f in figs]
    for _, f in figs:
        plt.close(f)
    data = texts.to_docx({"Methods": "x"}, "T", [("Figure X – a", pngs[0]), ("Figure Y – b", pngs[1])], "en")
    doc = docx.Document(io.BytesIO(data))
    assert len(doc.inline_shapes) == 2
    assert any(p.text == "Figure Y – b" for p in doc.paragraphs)
    assert analysis.saved_list("sox2;zzz", ["bdnf", "sox2"], ["bdnf"]) == ["sox2"]
    assert analysis.saved_list("", ["bdnf", "sox2"], ["bdnf"]) == ["bdnf"]

import io
import zipfile

import matplotlib.pyplot as plt
import streamlit as st

from ampliqa import analysis, design, figures, texts, ui
from ampliqa.i18n import is_en, t

ui.header(t("Métodos e resultados"),
          t("Rascunho em inglês e português, preenchido com a sua análise – revise antes de usar"))
exp = st.session_state.exp
mc = {**texts.METHODS_DEFAULTS, **design.methods_from(exp["meta"]), **(exp.get("methods_cfg") or {})}

an = analysis.run(exp)
if not an["ok"]:
    st.info(t(an["motivo"]) + " " + t("Depois, confira a estatística na tela Estatística e figuras."))
    ui.footer()
    st.stop()

with st.container(border=True):
    st.markdown(t("**1. Confirme o POP, os kits e os equipamentos usados** (o padrão segue os POPs atuais "
                  "PO.OPE.01 a 04BIOMOL)"))
    c1, c2, c3 = st.columns(3)
    if is_en():
        mc["especie"] = c1.text_input(t("Espécie (texto em inglês)"), mc["especie"])
    else:
        mc["especie_pt"] = c1.text_input(t("Espécie (texto em português)"), mc.get("especie_pt") or mc["especie"])
    sp = design.plan(exp["meta"])["especie"]
    tipos = [x for x in design.tissues_for(sp) if x != design.OUTRO] if sp in design.SPECIES else list(texts.SAMPLE_TYPES)
    if mc["tipo_amostra"] not in tipos:
        tipos.append(mc["tipo_amostra"])
    mc["tipo_amostra"] = c2.selectbox(t("Tipo de amostra"), tipos, index=tipos.index(mc["tipo_amostra"]),
                                      format_func=lambda k: design.LABELS_EN.get(k, k) if is_en() else k)
    mc["animais_por_pool"] = int(c3.number_input(t("Indivíduos por pool"), 1, 200, int(mc["animais_por_pool"]),
                                                 help=t("Use 1 se cada amostra é um único indivíduo (sem pool).")))
    mc["exposicao"] = st.text_input(t("Exposição / tratamento (aparece entre parênteses)"), mc["exposicao"],
                                    placeholder="ex.: exposed to 2,4-DCP at 0, 50 and 500 µg/L for 96 h")
    with st.expander(t("Kits e equipamentos (padrão dos POPs)")):
        c1, c2 = st.columns(2)
        mc["extracao"] = c1.text_input(t("Extração de RNA (PO.OPE.01)"), mc["extracao"])
        mc["quantificacao"] = c2.text_input(t("Quantificação"), mc["quantificacao"])
        mc["kit_cdna"] = c1.text_input(t("Kit de cDNA (PO.OPE.02)"), mc["kit_cdna"])
        mc["massa_rna"] = int(c2.number_input(t("RNA por reação de cDNA (ng)"), 50, 2000, int(mc["massa_rna"]), 50))
        mc["termociclador"] = c1.text_input(t("Termociclador do cDNA"), mc["termociclador"])
        mc["master_mix"] = c2.text_input(t("Master mix da qPCR (PO.OPE.03)"), mc["master_mix"])
        mc["equipamento_qpcr"] = c1.text_input(t("Equipamento de qPCR"), mc["equipamento_qpcr"])
        mc["volume_qpcr"] = int(c2.number_input(t("Volume da reação de qPCR (µL)"), 5, 50, int(mc["volume_qpcr"])))
        mc["ng_cdna"] = int(c1.number_input(t("cDNA por poço (ng de RNA-eq)"), 1, 100, int(mc["ng_cdna"])))
        mc["primer_um"] = float(c2.number_input(t("Concentração final de cada primer (µM)"), 0.05, 2.0,
                                                float(mc["primer_um"]), 0.05))
        st.caption(t("Se o experimento usou outro protocolo (ex.: PureLink, High-Capacity, StepOne), troque aqui: o "
                     "texto é atualizado na hora."))
exp["methods_cfg"] = mc

s = an["cfg"]
genes = an["genes"]
if any("omnibus" not in a for a in an["analyses"].values()):
    st.warning(t("Alguns genes não puderam ser analisados (veja a tela Estatística e figuras); eles ficam fora do "
                 "texto."))

# ------------------------------------------------------------------ figuras do relatório
with st.container(border=True):
    st.markdown(t("**2. Figuras do relatório** – as mesmas da tela Estatística e figuras, com as cores, genes e "
                  "opções que você escolheu lá"))
    figs = analysis.report_figures(an, s)
    nomes = {"barras": t("Gráfico de barras"), "heatmap": "Heatmap"}
    incluir = st.multiselect(t("Incluir no relatório"), [n for n, _ in figs], default=[n for n, _ in figs],
                             format_func=nomes.get)
    imgs = {n: {"png": figures.to_bytes(f, "png", 300), "svg": figures.to_bytes(f, "svg")}
            for n, f in figs if n in incluir}
    for _, f in figs:
        plt.close(f)
    if imgs:
        cols = st.columns(len(imgs))
        for col, (n, im) in zip(cols, imgs.items()):
            col.image(im["png"], caption=nomes[n], use_container_width=True)
    else:
        st.caption(t("Nenhuma figura selecionada: o relatório terá só o texto."))
genes_bar = analysis.saved_list(s.get("fig_genes_barras"), genes, genes[:6])
genes_heat = analysis.saved_list(s.get("fig_genes_heatmap"), genes, genes)
lim_fc = 2 ** float(s.get("heat_limite_log2", figures.HEAT_DEFAULTS["limite_log2"]))


def captions(lang):
    out = []
    if "barras" in imgs:
        out.append((texts.legend(genes_bar, an["ref"], an["n_txt"], s["erro"], an["analyses"], lang),
                    imgs["barras"]["png"]))
    if "heatmap" in imgs:
        out.append((texts.heatmap_legend(genes_heat, an["ref"], an["n_txt"], lim_fc, lang), imgs["heatmap"]["png"]))
    return out


docs = {}
tab_en, tab_pt = st.tabs(["🇬🇧 English", "🇧🇷 Português"])
for tab, lang in ((tab_en, "en"), (tab_pt, "pt")):
    with tab:
        sec = {
            ("Methods – qPCR" if lang == "en" else "Métodos – qPCR"):
                texts.methods(mc, an["ref"], an["n_txt"], lang, an["eff"]),
            ("Statistical analysis" if lang == "en" else "Análise estatística"):
                texts.statistics(an["analyses"], s["metrica"], s["comparacao"], lang),
            ("Results – gene expression" if lang == "en" else "Resultados – expressão gênica"):
                texts.results(an["analyses"], an["summary"], an["control"], an["labels"], lang),
            ("Figure legend" if lang == "en" else "Legenda da figura"):
                texts.legend(genes, an["ref"], an["n_txt"], s["erro"], an["analyses"], lang),
        }
        for head, body in sec.items():
            st.markdown(f"**{head}**")
            st.text_area(head, body, height=min(420, 90 + len(body) // 3), key=f"txt_{lang}_{head}_{hash(body)}",
                         label_visibility="collapsed")
        docs[lang] = texts.to_docx(sec, "AmpliQA – qPCR", captions(lang), lang)
        st.download_button("⬇️ Baixar em Word (.docx), com as figuras" if lang == "pt"
                           else "⬇️ Download Word (.docx), with figures",
                           docs[lang], f"metodos_resultados_{lang}.docx",
                           "application/vnd.openxmlformats-officedocument.wordprocessingml.document", key=f"dl_{lang}")
st.caption(t("Os nomes dos grupos vêm da tela Estatística e figuras (ex.: A → Control). Os valores de F, p e fold "
             "change são os da análise atual; os limites de significância são * p < 0,05; ** p < 0,01; *** p < 0,001; "
             "**** p < 0,0001. Confira sempre antes de usar no manuscrito."))
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
    for lang, data in docs.items():
        z.writestr(f"metodos_resultados_{lang}.docx", data)
    for n, im in imgs.items():
        z.writestr(f"figura_{n}.png", im["png"])
        z.writestr(f"figura_{n}.svg", im["svg"])
st.download_button(t("📦 Baixar tudo (.zip): Word em inglês e português + figuras em PNG 300 dpi e SVG"),
                   buf.getvalue(), "ampliqa_relatorio.zip", "application/zip", type="primary")
ui.footer()

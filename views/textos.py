import streamlit as st

from ampliqa import analysis, design, texts, ui
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
        st.download_button("⬇️ Baixar em Word (.docx)" if lang == "pt" else "⬇️ Download Word (.docx)",
                           texts.to_docx(sec, "AmpliQA – qPCR"), f"metodos_resultados_{lang}.docx",
                           "application/vnd.openxmlformats-officedocument.wordprocessingml.document", key=f"dl_{lang}")
st.caption(t("Os nomes dos grupos vêm da tela Estatística e figuras (ex.: A → Control). Os valores de F, p e fold "
             "change são os da análise atual; os limites de significância são * p < 0,05; ** p < 0,01; *** p < 0,001; "
             "**** p < 0,0001. Confira sempre antes de usar no manuscrito."))
ui.footer()

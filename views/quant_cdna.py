import streamlit as st

from ampliqa import quant, ui
from ampliqa.i18n import t, tval

ui.header(t("Quantificação de RNA → síntese de cDNA"),
          t("PO.OPE.01BIOMOL e PO.OPE.02BIOMOL · NZY First-Strand, 20 µL, 500 ng de RNA"))
exp = st.session_state.exp
p = exp["quant_params"]
ver = st.session_state.get("editor_ver", 0)

with st.expander(t("⚙️ Parâmetros (padrão do POP – altere só se o protocolo mudar)")):
    c1, c2, c3, c4 = st.columns(4)
    p["massa_rna_ng"] = c1.number_input(t("Massa de RNA por reação (ng)"), 50.0, 2000.0, float(p["massa_rna_ng"]), 50.0)
    p["vol_rna_agua_ul"] = c2.number_input(t("Volume RNA + H2O (µL)"), 1.0, 20.0, float(p["vol_rna_agua_ul"]), 0.5)
    p["mm_ul"] = c3.number_input(t("Master Mix por reação (µL)"), 1.0, 20.0, float(p["mm_ul"]), 0.5)
    p["em_ul"] = c4.number_input(t("Enzyme Mix por reação (µL)"), 0.5, 10.0, float(p["em_ul"]), 0.5)
    c1, c2, c3, c4 = st.columns(4)
    p["a280_min"] = c1.number_input(t("A260/280 mínimo"), 1.0, 2.5, float(p["a280_min"]), 0.05)
    p["a280_max"] = c2.number_input(t("A260/280 máximo"), 1.5, 3.0, float(p["a280_max"]), 0.05)
    p["a230_min"] = c3.number_input(t("A260/230 mínimo (aceite)"), 0.5, 3.0, float(p["a230_min"]), 0.05)
    p["a230_ressalva"] = c4.number_input(t("A260/230 mínimo (ressalva)"), 0.5, 3.0, float(p["a230_ressalva"]), 0.05)
    c1, c2, c3, c4 = st.columns(4)
    p["vol_min_ul"] = c1.number_input(t("Volume mínimo pipetável (µL)"), 0.1, 5.0, float(p["vol_min_ul"]), 0.1)
    p["margem"] = c2.number_input(t("Margem do mix (fração)"), 0.0, 0.5, float(p["margem"]), 0.05)
    p["n_bcdna"] = int(c3.number_input(t("Brancos do cDNA (BcDNA)"), 0, 5, int(p["n_bcdna"]), 1))
    p["n_nrt"] = int(c4.number_input(t("Controles sem RT (NRT)"), 0, 10, int(p["n_nrt"]), 1))
    st.caption(t("Concentração mínima de RNA = {c} ng/µL ({m} ng em {v} µL).", c=ui.br(quant.conc_min(p)),
                 m=ui.br(p["massa_rna_ng"], 0), v=ui.br(p["vol_rna_agua_ul"])))

with st.expander(t("📥 Importar as leituras direto do arquivo do NanoDrop (versão provisória)")):
    st.caption(t("Exporte as leituras no software do NanoDrop 2000 e carregue o arquivo. Leituras repetidas da mesma "
                 "amostra viram Leitura 1 e Leitura 2. (Formato ainda será confirmado com arquivos reais.)"))
    from ampliqa import examples
    st.download_button(t("⬇️ Arquivo de exemplo do NanoDrop (fictício)"), examples.file_nanodrop(),
                       "exemplo_nanodrop.tsv", "text/tab-separated-values")
    nd = st.file_uploader(t("Arquivo do NanoDrop"), type=["tsv", "txt", "csv", "xls", "xlsx"], key="nd_up")
    if nd is not None and st.session_state.get("nd_ultimo") != (nd.name, nd.size):
        try:
            from ampliqa.nanodrop import read_nanodrop
            tab = read_nanodrop(nd.getvalue(), nd.name)
            exp["quant"] = tab
            st.session_state.nd_ultimo = (nd.name, nd.size)
            ui.bump_editors()
            st.success(t("{n} amostras importadas do NanoDrop.", n=len(tab)))
            st.rerun()
        except Exception as e:  # noqa: BLE001
            st.error(t("Não consegui ler o arquivo do NanoDrop: {e}", e=tval(str(e))))

ui.step(t("<b>1. Digite as leituras do NanoDrop</b> – uma amostra por linha. Se fez só uma leitura, deixe a "
          "Leitura 2 em branco. Use o <b>+</b> no fim da tabela para acrescentar linhas."))
base_key, ed_key = f"quant_base_{ver}", f"quant_ed_{ver}"
if ed_key not in st.session_state:  # 1ª vez ou voltando de outra tela: parte do que está no experimento
    st.session_state[base_key] = quant.normalize(exp["quant"])


def num(col, fmt="%.2f"):
    return st.column_config.NumberColumn(t(col), format=fmt, min_value=0.0)


edited = st.data_editor(
    st.session_state[base_key], key=ed_key, num_rows="dynamic", use_container_width=True,
    hide_index=True,
    column_config={
        "Código": st.column_config.TextColumn(t("Código"), help=t("ex.: A1, A2, B1…")),
        "Grupo": st.column_config.TextColumn(t("Grupo")),
        "Réplica": st.column_config.TextColumn(t("Réplica")),
        "Conc. 1 (ng/µL)": num("Conc. 1 (ng/µL)", "%.1f"),
        "A260/280 1": num("A260/280 1"), "A260/230 1": num("A260/230 1"),
        "Conc. 2 (ng/µL)": num("Conc. 2 (ng/µL)", "%.1f"),
        "A260/280 2": num("A260/280 2"), "A260/230 2": num("A260/230 2"),
        "Observações": st.column_config.TextColumn(t("Observações"), width="medium"),
    },
)
exp["quant"] = edited.reset_index(drop=True)
res = quant.compute(exp["quant"], p)
ativos = res[res["Situação"] != ""]

if ativos.empty:
    st.info(t("Digite ao menos uma amostra com código e concentração para ver os cálculos."))
    ui.footer()
    st.stop()

ui.step(t("<b>2. Confira a qualidade e a situação de cada amostra</b>"))
show = ativos[["Código", "Grupo", "Conc. média (ng/µL)", "A260/280", "A260/230", "Qualidade",
               "1º Mix comum (µL)", "2º H2O DEPC (µL)", "3º RNA (µL)", "Situação"]]
st.dataframe(ui.fmt(show, {"Conc. média (ng/µL)": 1, "A260/280": 2, "A260/230": 2, "1º Mix comum (µL)": 1,
                           "2º H2O DEPC (µL)": 2, "3º RNA (µL)": 2}, status=["Qualidade", "Situação"]),
             use_container_width=True, hide_index=True)

problemas = ativos[ativos["Situação"] != quant.PRONTO]
for _, r in problemas.iterrows():
    msg = f"**{r['Código']}** ({ui.br(r['Conc. média (ng/µL)'])} ng/µL): {tval(r['Situação'])}"
    (st.error if r["Situação"].startswith(("Não usar", "Revisar")) else st.warning)(msg)

ui.step(t("<b>3. Prepare o mix comum</b> (amostras prontas + brancos, com margem de pipetagem)"))
m = quant.mix_summary(res, p)
c1, c2, c3, c4 = st.columns(4)
c1.metric(t("Reações"), f"{m['reacoes']}", t("{a} amostras + {b} branco(s)", a=m["amostras_prontas"], b=m["brancos"]),
          delta_color="off")
c2.metric("NZYRT 2× Master Mix", f"{ui.br(m['mm_total'])} µL")
c3.metric("NZYRT Enzyme Mix", f"{ui.br(m['em_total'])} µL")
c4.metric(t("Mix comum por tubo"), f"{ui.br(m['mix_por_tubo'], 0)} µL")
st.caption(t("Total de mix comum: {v} µL ({r} reações com margem). O NRT, se feito, não leva Enzyme Mix: prepare à "
             "parte.", v=ui.br(m["mix_total"]), r=ui.br(m["reacoes_margem"])))

ui.step(t("<b>4. Monte os tubos nesta ordem:</b> 1º mix comum (mesma ponteira, tubos vazios) → 2º água DEPC → "
          "3º RNA (ponteira nova para cada amostra)"))
lista = quant.pipetting_list(res, p)
st.dataframe(ui.fmt(lista, {"1º Mix comum (µL)": 1, "2º H2O DEPC (µL)": 2, "3º RNA (µL)": 2}, status=["Situação"]),
             use_container_width=True, hide_index=True)
st.caption(t("Programa do termociclador (Veriti – FISHLAB cDNA): 25 °C 10 min → 55 °C 20 min → 85 °C 5 min → 4 °C. "
             "Depois, diluir o cDNA 1:2,5 (10 µL + 15 µL de água) para 10 ng/µL de RNA-eq."))
ui.footer()

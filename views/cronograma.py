from datetime import date

import streamlit as st

from ampliqa import schedule, ui
from ampliqa.i18n import lang, t

ui.header(t("Planejamento – cronograma"),
          t("Defina as datas de cada etapa, da bancada à análise, e compartilhe com os colaboradores"))
exp = st.session_state.exp
ver = st.session_state.get("editor_ver", 0)
nome = exp["meta"].get("Experimento") or ""

# ------------------------------------------------------------------ sugestão
with st.expander(t("✨ Sugerir um cronograma a partir de uma data (você ajusta depois)"),
                 expanded=not len(schedule.normalize(exp.get("cronograma")))):
    c1, c2, c3, c4 = st.columns(4)
    inicio = c1.date_input(t("Início (extração de RNA)"), value=date.today(), format="DD/MM/YYYY")
    dias_qpcr = c2.number_input(t("Dias de qPCR"), 1, 10, 1, help=t("Um dia por placa, em geral."))
    gap = c3.number_input(t("Dias úteis entre etapas"), 1, 10, 1)
    resp = c4.text_input(t("Responsável"), value=exp["meta"].get("Responsável", ""))
    efic = st.checkbox(t("Incluir curva de eficiência dos primers (PO.OPE.04)"))
    st.caption(t("Fins de semana são pulados. A repetição de qPCR fica 2 dias úteis depois do último qPCR e a "
                 "análise, 2 dias úteis depois. Isto substitui a tabela abaixo."))
    if st.button(t("Sugerir cronograma"), type="primary"):
        exp["cronograma"] = schedule.suggest(inicio, lang(), int(dias_qpcr), int(gap), efic, resp)
        ui.bump_editors()
        st.rerun()

# ------------------------------------------------------------------ tabela
ui.step(t("<b>Etapas do experimento</b> – edite à vontade. Use o <b>+</b> no fim da tabela para acrescentar "
          "etapas. Em <b>Convidados</b>, coloque os e-mails dos colaboradores separados por vírgula."))
bkey, ekey = f"cron_base_{ver}", f"cron_ed_{ver}"
if ekey not in st.session_state:
    st.session_state[bkey] = schedule.normalize(exp.get("cronograma"))
ed = st.data_editor(
    st.session_state[bkey], key=ekey, num_rows="dynamic", hide_index=True, use_container_width=True,
    column_config={
        "Data": st.column_config.DateColumn(t("Data"), format="DD/MM/YYYY", required=True),
        "Etapa": st.column_config.TextColumn(t("Etapa"), width="large", required=True),
        "Detalhes": st.column_config.TextColumn(t("Detalhes")),
        "Observação": st.column_config.TextColumn(t("Observação"), help=t("Aparece em uma linha com * na mensagem.")),
        "Responsável": st.column_config.TextColumn(t("Responsável")),
        "Convidados": st.column_config.TextColumn(t("Convidados"), help=t("E-mails separados por vírgula.")),
    })
exp["cronograma"] = schedule.normalize(ed)
cron = exp["cronograma"]

if not len(cron.dropna(subset=["Data"])):
    st.info(t("Preencha ao menos uma etapa com data para gerar a mensagem e os eventos."))
    ui.footer()
    st.stop()

tab_w, tab_g = st.tabs([t("💬 Mensagem para WhatsApp"), t("📆 Google Agenda")])

with tab_w:
    msg_lang = st.radio(t("Idioma da mensagem"), ["pt", "en"], horizontal=True, index=0 if lang() == "pt" else 1,
                        format_func={"pt": "Português", "en": "English"}.get)
    msg = schedule.whatsapp(cron, nome, msg_lang)
    st.code(msg, language=None)
    st.caption(t("Use o ícone de copiar no canto da caixa e cole no WhatsApp, ou abra direto pelo botão."))
    st.link_button(t("Abrir no WhatsApp"), schedule.whatsapp_link(msg))

with tab_g:
    st.markdown(t("**Opção 1 – um evento por vez:** cada link abre o Google Agenda com a etapa já preenchida (dia "
                  "inteiro, com os convidados). Confira e clique em Salvar; o Google envia o convite aos "
                  "convidados."))
    for d0, etapa, link in schedule.google_links(cron, nome):
        st.markdown(f"- {d0:%d/%m} – [{etapa}]({link})")
    st.markdown(t("**Opção 2 – todas as etapas de uma vez:** baixe o arquivo .ics e importe no Google Agenda "
                  "(Configurações → Importar e exportar). Também funciona no Outlook e no Apple Calendar."))
    st.download_button(t("📆 Baixar cronograma (.ics)"), schedule.ics(cron, nome), "ampliqa_cronograma.ics",
                       "text/calendar")
    st.caption(t("O cronograma é salvo no arquivo do experimento (aba Cronograma). O app não envia nada sozinho."))
ui.footer()

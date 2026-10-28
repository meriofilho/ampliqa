import streamlit as st

from ampliqa import experiment, help as faq, ui
from ampliqa.i18n import t

ui.header(t("Central de ajuda"), t("Problemas comuns na bancada e na análise – como resolver e onde ler mais"))
exp = st.session_state.exp

st.subheader(t("🔎 Diagnóstico do seu experimento"))
try:
    diag = faq.diagnose(exp, experiment.results_tables(exp))
except Exception as e:  # noqa: BLE001
    diag = []
    st.caption(t("Não foi possível analisar o experimento: {e}", e=e))
if not diag:
    st.success(t("Nenhum ponto de atenção encontrado nos dados abertos (ou ainda não há dados)."))
else:
    st.caption(t("Pontos encontrados nos dados que estão abertos agora, com a explicação e o que fazer."))
    for eid, detalhe in diag:
        e = faq.entry(eid)
        with st.expander(f"⚠️ {faq.loc(e)['titulo']} – {detalhe}"):
            st.markdown(faq.entry_markdown(e))

st.subheader(t("💬 Pergunte"))
q = st.text_input(t("Descreva o problema com suas palavras"), placeholder=t("ex.: minhas réplicas deram diferentes"))
if q:
    hits = faq.search(q)
    if not hits:
        st.info(t("Não encontrei uma resposta para isso. Tente outras palavras ou procure na lista abaixo."))
    for e in hits:
        with st.expander(faq.loc(e)["titulo"], expanded=e is hits[0]):
            st.markdown(faq.entry_markdown(e))

st.subheader(t("📚 Todas as perguntas frequentes"))
for e in faq.FAQ:
    with st.expander(faq.loc(e)["titulo"]):
        st.markdown(faq.entry_markdown(e))

st.subheader(t("📄 POPs do laboratório"))
st.markdown("\n".join(f"- [{code}]({url})" for code, url in faq.POP_LINKS.items())
            + f"\n- [{t('Pasta com todos os POPs e planilhas-anexo')}]({faq.POP_FOLDER})")
st.caption(t("Os links abrem os PDFs na pasta do Fishlab no Google Drive (é preciso ter acesso à pasta)."))

st.subheader(t("🔗 Referências oficiais"))
st.caption(t("Artigos de referência para qPCR e para os testes estatísticos usados no app. Clique no DOI para abrir o "
             "artigo. DOIs conferidos na Crossref."))
for grupo, keys in faq.REF_GROUPS.items():
    st.markdown(f"**{t(grupo)}**")
    st.markdown("\n".join(f"- {faq.ref_line(k)}" for k in keys))
st.caption(t("Esta central não usa inteligência artificial: as respostas foram escritas a partir dos POPs de Biologia "
             "Molecular e da literatura acima."))
ui.footer()

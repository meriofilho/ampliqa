"""AmpliQA – planejamento e análise de experimentos de expressão gênica (RT-qPCR).

Rodar localmente:  streamlit run app.py
"""
import streamlit as st

from ampliqa import ui
from ampliqa.i18n import t

st.set_page_config(page_title="AmpliQA", page_icon="🧬", layout="wide")
ui.setup_page()
ui.language_selector()

pages = st.navigation({
    "": [st.Page("views/inicio.py", title=t("Início"), icon=":material/home:", default=True)],
    t("Bancada"): [
        st.Page("views/quant_cdna.py", title=t("Quantificação → cDNA"), icon=":material/science:"),
        st.Page("views/qpcr.py", title="qPCR", icon=":material/grid_on:"),
    ],
    t("Análise"): [
        st.Page("views/estatistica.py", title=t("Estatística e figuras"), icon=":material/bar_chart:"),
        st.Page("views/textos.py", title=t("Métodos e resultados"), icon=":material/description:"),
    ],
    t("Ajuda"): [st.Page("views/ajuda.py", title=t("Central de ajuda"), icon=":material/help:")],
})
pages.run()
ui.sidebar()  # depois da tela, para o arquivo salvo já conter a última edição

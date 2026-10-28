"""AmpliQA – planejamento e análise de experimentos de expressão gênica (RT-qPCR).

Rodar localmente:  streamlit run app.py
"""
import sys
from pathlib import Path

import streamlit as st


def _fresh_ampliqa():
    """O Streamlit reexecuta este arquivo a cada interação, mas mantém o pacote ampliqa na memória. Depois de uma
    atualização (git pull no Streamlit Cloud ou edição local), as telas novas rodariam com módulos antigos.
    Se algum arquivo do pacote mudou desde a importação, o pacote é descartado e importado de novo."""
    sig = tuple(sorted((p.name, p.stat().st_mtime_ns) for p in (Path(__file__).parent / "ampliqa").glob("*.py")))
    old = sys.modules.get("ampliqa")
    if old is not None and getattr(old, "_SIG", None) != sig:
        for name in [m for m in sys.modules if m == "ampliqa" or m.startswith("ampliqa.")]:
            del sys.modules[name]
    import ampliqa
    ampliqa._SIG = sig


_fresh_ampliqa()

from ampliqa import ui  # noqa: E402
from ampliqa.i18n import t  # noqa: E402

st.set_page_config(page_title="AmpliQA", page_icon="🧬", layout="wide")
ui.setup_page()
ui.language_selector()

pages = st.navigation({
    "": [st.Page("views/inicio.py", title=t("Início"), icon=":material/home:", default=True)],
    t("Planejamento"): [
        st.Page("views/cronograma.py", title=t("Cronograma"), icon=":material/calendar_month:"),
    ],
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

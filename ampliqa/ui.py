"""Elementos visuais e estado compartilhado entre as telas."""
import re
from datetime import date

import pandas as pd
import streamlit as st

from . import experiment
from .i18n import LANGS, is_en, t, tval
from .params import FISHLAB

LAB_DG = '<a href="https://dalmolingroup.imd.ufrn.br/" target="_blank">Dalmolin Systems Biology Group</a>'
LAB_FL = '<a href="https://www.fishlabufrn.com/" target="_blank">Fish Lab</a>'

OK_BG, WARN_BG, BAD_BG = "#DCEFEA", "#FBE9D9", "#F6D5D1"

CSS = f"""
<style>
  .block-container {{ padding-top: 2.2rem; max-width: 1200px; }}
  .fl-header {{ background: {FISHLAB['primaria']}; color: white; padding: 0.9rem 1.2rem; border-radius: 10px;
               margin-bottom: 1rem; }}
  .fl-header h1 {{ color: white; font-size: 1.45rem; margin: 0; padding: 0; }}
  .fl-header p {{ color: #E3F1F1; margin: 0.2rem 0 0 0; font-size: 0.92rem; }}
  .fl-step {{ border-left: 5px solid {FISHLAB['destaque']}; background: white; padding: 0.6rem 0.9rem;
             border-radius: 6px; margin: 0.4rem 0 0.8rem 0; }}
  .fl-foot {{ color: #5b6b6b; font-size: 0.8rem; margin-top: 2rem; }}
  div[data-testid="stMetricValue"] {{ color: {FISHLAB['primaria']}; }}
  h2, h3 {{ color: {FISHLAB['primaria']}; }}
</style>
"""


def setup_page():
    st.markdown(CSS, unsafe_allow_html=True)
    if "exp" not in st.session_state:
        st.session_state.exp = experiment.new_experiment()
        st.session_state.editor_ver = 0
    if not st.session_state.get("lang"):
        st.session_state.lang = "pt"


def language_selector():
    with st.sidebar:
        st.segmented_control("Idioma / Language", list(LANGS), format_func=LANGS.get, key="lang",
                             label_visibility="collapsed")


def header(title: str, subtitle: str = ""):
    st.markdown(f'<div class="fl-header"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


def step(text: str):
    st.markdown(f'<div class="fl-step">{text}</div>', unsafe_allow_html=True)


def footer():
    st.markdown('<div class="fl-foot">' + t(
        "Ampliqa · código aberto (licença MIT) · desenvolvido por Romério de Oliveira Lima Filho, doutorando em "
        "Bioinformática no {dg}, em parceria com o {fl} (UFRN). Segue os POPs de Biologia Molecular (PO.OPE.01 a "
        "04BIOMOL).", dg=LAB_DG, fl=LAB_FL) + "</div>", unsafe_allow_html=True)


def file_name(exp: dict) -> str:
    nome = exp["meta"].get("Experimento") or "experimento"
    nome = re.sub(r"[^\w\-]+", "_", str(nome), flags=re.UNICODE).strip("_") or "experimento"
    return f"{date.today().isoformat()}_{nome}.xlsx"


def sidebar():
    exp = st.session_state.exp
    with st.sidebar:
        st.markdown("### 🧬 Ampliqa")
        nome = exp["meta"].get("Experimento") or t("— sem nome —")
        resp = exp["meta"].get("Responsável") or "—"
        st.markdown(f"**{t('Experimento')}:** {nome}  \n**{t('Responsável')}:** {resp}")
        st.download_button(t("💾 Salvar arquivo do experimento"), data=experiment.to_xlsx(exp),
                           file_name=file_name(exp), type="primary", use_container_width=True,
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        st.caption(t("Salve sempre que terminar uma etapa e guarde o arquivo no seu Google Drive."))
        _help_box(exp)


def _help_box(exp):
    from . import help as faq
    st.markdown("---")
    st.markdown(f"**❓ {t('Ajuda rápida')}**")
    try:
        diag = faq.diagnose(exp, experiment.results_tables(exp))
    except Exception:  # noqa: BLE001
        diag = []
    if diag:
        st.caption(t("⚠️ {n} ponto(s) de atenção no seu experimento – veja a Central de ajuda.", n=len(diag)))
    q = st.text_input(t("O que deu errado?"), key="help_q", placeholder=t("ex.: branco amplificou"),
                      label_visibility="collapsed")
    if q:
        hits = faq.search(q, k=3)
        if not hits:
            st.caption(t("Nada encontrado. Tente outras palavras ou abra a Central de ajuda."))
        for e in hits:
            with st.expander(faq.loc(e)["titulo"]):
                st.markdown(faq.entry_markdown(e))


def bump_editors():
    """Força os editores de tabela a recarregar (após abrir um arquivo ou carregar exemplo)."""
    st.session_state.editor_ver = st.session_state.get("editor_ver", 0) + 1


def color_status(v):
    s = str(v)
    if s.startswith(("OK", "Pronto", "Estável")):
        return f"background-color: {OK_BG}"
    if s.startswith(("Ressalva", "Diluir", "Só ", "Aceitável")):
        return f"background-color: {WARN_BG}"
    if s.startswith(("Fora", "Não usar", "Revisar", "ATENÇÃO", "Diferença", "Nenhuma", "Instável")):
        return f"background-color: {BAD_BG}"
    return ""


def br(x, d=1) -> str:
    """Número formatado no idioma da sessão (vírgula decimal em português)."""
    if x is None or pd.isna(x):
        return ""
    s = f"{x:.{d}f}"
    return s if is_en() else s.replace(".", ",")


def fmt(df: pd.DataFrame, decimals: dict | None = None, status=()) -> "pd.io.formats.style.Styler":
    """Tabela pronta para exibir: números formatados, colunas e valores traduzidos e cores nas colunas de
    situação (status)."""
    decimals = decimals or {}
    d = df.copy()
    colors = {c: d[c].map(color_status) for c in status if c in d}
    for c in d.columns:
        if d[c].dtype == object or pd.api.types.is_string_dtype(d[c]):
            d[c] = d[c].map(tval)
    names = {c: t(c) for c in d.columns}
    d = d.rename(columns=names)
    sty = d.style.format({names[k]: (lambda x, dd=dd: "" if pd.isna(x) else br(x, dd))
                          for k, dd in decimals.items() if k in names})
    for c, col in colors.items():
        sty = sty.apply(lambda _s, col=col: col.to_numpy(), subset=[names[c]])
    return sty

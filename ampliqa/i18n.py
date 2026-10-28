"""Interface em português (padrão) e inglês.

O texto em português é a própria chave: t("Salvar") devolve "Save" quando o idioma da sessão é inglês.
As traduções ficam em locale_en.py. Valores de tabela (situações, alertas, nomes de teste) são traduzidos na
exibição por tval(), por correspondência exata ou por padrões (PATTERNS). Fora do Streamlit (testes, scripts),
o idioma é sempre português.
"""
from .locale_en import EN, FAQ_EN, PATTERNS

LANGS = {"pt": "Português", "en": "English"}


def lang() -> str:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        if get_script_run_ctx(suppress_warning=True) is None:
            return "pt"
        import streamlit as st
        return st.session_state.get("lang", "pt")
    except Exception:  # noqa: BLE001
        return "pt"


def is_en() -> bool:
    return lang() == "en"


def t(text: str, **kw) -> str:
    out = EN.get(text, text) if is_en() else text
    return out.format(**kw) if kw else out


def tval(v):
    """Traduz um valor de célula (ex.: situação de uma amostra), se houver tradução."""
    if not is_en() or not isinstance(v, str) or not v:
        return v
    if v in EN:
        return EN[v]
    for pat, rep in PATTERNS:
        if pat.fullmatch(v):
            return pat.sub(rep, v)
    return v


def num(x, d=1) -> str:
    """Número com vírgula decimal (pt) ou ponto (en)."""
    s = f"{x:.{d}f}"
    return s if is_en() else s.replace(".", ",")


def faq(e: dict) -> dict:
    """Entrada da central de ajuda no idioma da sessão."""
    return {**e, **FAQ_EN.get(e["id"], {})} if is_en() else e

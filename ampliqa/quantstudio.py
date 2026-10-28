"""Leitura do arquivo de resultados exportado do QuantStudio (Design & Analysis)."""
import io

import numpy as np
import pandas as pd

ALIASES = {
    "Poço": ["well"],
    "Posição": ["well position"],
    "Omitir": ["omit"],
    "Amostra": ["sample name", "sample"],
    "Gene": ["target name", "target"],
    "Ct": ["ct", "cт", "cq", "crt"],
}


def _to_ct(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return np.nan
    if isinstance(v, (int, float, np.number)):
        return float(v)
    s = str(v).strip().replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return np.nan  # "Undetermined", vazio etc.


def _to_bool(v):
    return str(v).strip().upper() in ("TRUE", "VERDADEIRO", "1", "SIM", "YES")


def _find_table(df: pd.DataFrame) -> pd.DataFrame | None:
    """Acha a linha de cabeçalho (contém 'Sample Name' e 'CT') e devolve a tabela abaixo dela."""
    for i in range(min(len(df), 200)):
        cells = [str(x).strip().lower() for x in df.iloc[i].tolist()]
        if any(c in ("sample name", "sample") for c in cells) and any(c in ALIASES["Ct"] for c in cells):
            t = df.iloc[i + 1:].copy()
            t.columns = [str(x).strip() for x in df.iloc[i].tolist()]
            return t
    return None


def _normalize(t: pd.DataFrame) -> pd.DataFrame:
    low = {c.lower(): c for c in t.columns}
    out = pd.DataFrame()
    for name, al in ALIASES.items():
        col = next((low[a] for a in al if a in low), None)
        out[name] = t[col].values if col is not None else None
    out = out[out["Amostra"].notna() & (out["Amostra"].astype(str).str.strip() != "")]
    out = out[out["Gene"].notna()]
    out["Amostra"] = out["Amostra"].astype(str).str.strip()
    out["Gene"] = out["Gene"].astype(str).str.strip()
    out["Ct"] = out["Ct"].apply(_to_ct)
    out["Omitir"] = out["Omitir"].apply(_to_bool) if out["Omitir"].notna().any() else False
    out["Poço"] = out["Posição"].where(out["Posição"].notna(), out["Poço"]).astype(str)
    return out[["Poço", "Amostra", "Gene", "Ct", "Omitir"]].reset_index(drop=True)


def read_results(data: bytes, filename: str) -> pd.DataFrame:
    """Aceita .xls / .xlsx (aba Results) ou .csv / .txt exportados do QuantStudio."""
    name = filename.lower()
    if name.endswith((".xls", ".xlsx")):
        engine = "xlrd" if name.endswith(".xls") else "openpyxl"
        sheets = pd.read_excel(io.BytesIO(data), sheet_name=None, header=None, engine=engine)
        order = sorted(sheets, key=lambda s: 0 if s.strip().lower() == "results" else 1)
        for s in order:
            t = _find_table(sheets[s])
            if t is not None:
                return _normalize(t)
        raise ValueError("Não encontrei a tabela de resultados (colunas 'Sample Name' e 'CT') no arquivo.")
    text = data.decode("utf-8", errors="replace")
    sep = "\t" if "\t" in text else (";" if text.count(";") > text.count(",") else ",")
    lines = [ln.rstrip("\r") for ln in text.split("\n")]
    rows = [ln.split(sep) for ln in lines]
    width = max((len(r) for r in rows), default=0)
    df = pd.DataFrame([r + [None] * (width - len(r)) for r in rows])
    t = _find_table(df)
    if t is None:
        raise ValueError("Não encontrei a tabela de resultados (colunas 'Sample Name' e 'CT') no arquivo.")
    return _normalize(t)

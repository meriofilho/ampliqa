"""Importação de leituras do NanoDrop (PROVISÓRIO – será ajustado com arquivos reais do NanoDrop 2000).

Aceita a exportação de texto do software do NanoDrop (.tsv/.txt/.csv) ou planilha (.xlsx/.xls) com colunas como
"Sample ID", "Nucleic Acid Conc." (ou "Conc."), "260/280" e "260/230". Leituras repetidas da mesma amostra viram
Leitura 1 e Leitura 2.
"""
import re

import numpy as np
import pandas as pd

from . import quant
from .importers import _tables, to_ct


def _num(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return np.nan
    if isinstance(v, (int, float, np.number)):
        return float(v)
    s = str(v).strip().replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return np.nan


def read_nanodrop(data: bytes, filename: str) -> pd.DataFrame:
    for df in _tables(data, filename):
        for i in range(min(len(df), 60)):
            hdr = [str(x).strip().lower() if x is not None and not pd.isna(x) else "" for x in df.iloc[i].tolist()]
            s_col = next((j for j, h in enumerate(hdr) if h in ("sample id", "sample name", "sample", "amostra",
                                                                 "id da amostra", "nome da amostra")), None)
            c_col = next((j for j, h in enumerate(hdr) if "conc" in h), None)
            r280 = next((j for j, h in enumerate(hdr) if "260/280" in h), None)
            r230 = next((j for j, h in enumerate(hdr) if "260/230" in h), None)
            if s_col is None or c_col is None or r280 is None:
                continue
            body = df.iloc[i + 1:]
            reads = {}
            for _, r in body.iterrows():
                code = str(r.iloc[s_col]).strip() if not pd.isna(r.iloc[s_col]) else ""
                if not code or code.lower() in ("nan", "blank", "branco"):
                    continue
                c = _num(r.iloc[c_col])
                if pd.isna(c):
                    continue
                reads.setdefault(code, []).append((c, _num(r.iloc[r280]),
                                                   _num(r.iloc[r230]) if r230 is not None else np.nan))
            rows = []
            for code, lst in reads.items():
                m = re.match(r"^([A-Za-z]+)\s*0*(\d+)$", code)
                l1 = lst[0]
                l2 = lst[1] if len(lst) > 1 else (np.nan, np.nan, np.nan)
                rows.append({"Código": code, "Grupo": m.group(1).upper() if m else None,
                             "Réplica": m.group(2) if m else None,
                             "Conc. 1 (ng/µL)": l1[0], "A260/280 1": l1[1], "A260/230 1": l1[2],
                             "Conc. 2 (ng/µL)": l2[0], "A260/280 2": l2[1], "A260/230 2": l2[2],
                             "Observações": f"{len(lst)} leituras no arquivo" if len(lst) > 2 else None})
            if rows:
                return quant.normalize(pd.DataFrame(rows))
    raise ValueError("Não encontrei as colunas de amostra, concentração e 260/280 no arquivo do NanoDrop.")

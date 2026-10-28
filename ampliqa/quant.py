"""Quantificação de RNA total e cálculo da síntese de cDNA (PO.OPE.01 e 02BIOMOL)."""
import numpy as np
import pandas as pd

from .params import QUANT_DEFAULTS

INPUT_COLS = ["Código", "Grupo", "Réplica", "Conc. 1 (ng/µL)", "A260/280 1", "A260/230 1",
              "Conc. 2 (ng/µL)", "A260/280 2", "A260/230 2", "Observações"]
NUM_COLS = ["Conc. 1 (ng/µL)", "A260/280 1", "A260/230 1", "Conc. 2 (ng/µL)", "A260/280 2", "A260/230 2"]

OK, RESSALVA, FORA = "OK", "Ressalva (A260/230)", "Fora do critério"
PRONTO = "Pronto para cDNA"
DILUIR = "Diluir o RNA antes (volume < mínimo)"
INSUF = "Não usar: concentração insuficiente – concentrar ou reextrair"
REVISAR = "Revisar qualidade antes de usar"


TEXT_COLS = [c for c in INPUT_COLS if c not in NUM_COLS]


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    """Garante tipos estáveis para o editor: texto como objeto (str ou None) e leituras como float."""
    out = df.reindex(columns=INPUT_COLS).copy()
    for c in NUM_COLS:
        out[c] = pd.to_numeric(out[c], errors="coerce").astype("float64")
    for c in TEXT_COLS:
        out[c] = pd.Series([None if (v is None or (isinstance(v, float) and np.isnan(v)) or str(v) == "nan")
                            else (str(int(v)) if isinstance(v, float) and v.is_integer() else str(v))
                            for v in out[c]], dtype=object, index=out.index)
    return out.reset_index(drop=True)


def empty_table(n=6) -> pd.DataFrame:
    return normalize(pd.DataFrame({c: [None] * n for c in INPUT_COLS}))


def example_table() -> pd.DataFrame:
    rows = [
        ("A1", "A", 1, 265.7, 1.98, 2.31, 262.1, 1.99, 2.28, ""),
        ("A2", "A", 2, 195.1, 1.97, 2.36, 191.4, 1.97, 2.35, ""),
        ("A3", "A", 3, 141.6, 2.01, 1.66, 138.2, 2.00, 1.62, ""),
        ("B1", "B", 1, 121.5, 1.95, 2.04, 124.7, 1.95, 2.07, ""),
        ("B2", "B", 2, 44.8, 1.98, 1.55, 43.0, 1.98, 1.48, ""),
        ("B3", "B", 3, 612.0, 2.02, 2.21, 598.4, 2.01, 2.19, ""),
    ]
    return normalize(pd.DataFrame(rows, columns=INPUT_COLS))


def conc_min(p: dict) -> float:
    return p["massa_rna_ng"] / p["vol_rna_agua_ul"]


def _mean2(a, b):
    vals = [v for v in (a, b) if v is not None and not pd.isna(v)]
    return float(np.mean(vals)) if vals else np.nan


def compute(df: pd.DataFrame, p: dict | None = None) -> pd.DataFrame:
    """Recebe a tabela de entrada e devolve a tabela com médias, qualidade, volumes e situação."""
    p = {**QUANT_DEFAULTS, **(p or {})}
    out = df.copy()
    for c in NUM_COLS:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    has_code = out["Código"].fillna("").astype(str).str.strip() != ""
    out["Conc. média (ng/µL)"] = [_mean2(a, b) for a, b in zip(out["Conc. 1 (ng/µL)"], out["Conc. 2 (ng/µL)"])]
    out["A260/280"] = [_mean2(a, b) for a, b in zip(out["A260/280 1"], out["A260/280 2"])]
    out["A260/230"] = [_mean2(a, b) for a, b in zip(out["A260/230 1"], out["A260/230 2"])]

    qual, rna, agua, mix, sit = [], [], [], [], []
    cmin = conc_min(p)
    for code_ok, c, r280, r230 in zip(has_code, out["Conc. média (ng/µL)"], out["A260/280"], out["A260/230"]):
        if not code_ok or pd.isna(c):
            qual.append(""); rna.append(np.nan); agua.append(np.nan); mix.append(np.nan); sit.append("")
            continue
        if pd.isna(r280) or pd.isna(r230):
            q = ""
        elif r280 < p["a280_min"] or r280 > p["a280_max"] or r230 < p["a230_ressalva"]:
            q = FORA
        elif r230 < p["a230_min"]:
            q = RESSALVA
        else:
            q = OK
        v_rna = p["massa_rna_ng"] / c if c > 0 else np.nan
        qual.append(q)
        rna.append(v_rna)
        agua.append(p["vol_rna_agua_ul"] - v_rna)
        mix.append(p["mm_ul"] + p["em_ul"])
        if c < cmin:
            sit.append(INSUF)
        elif v_rna < p["vol_min_ul"]:
            sit.append(DILUIR)
        elif q == FORA:
            sit.append(REVISAR)
        else:
            sit.append(PRONTO)
    out["Qualidade"] = qual
    out["1º Mix comum (µL)"] = mix
    out["2º H2O DEPC (µL)"] = agua
    out["3º RNA (µL)"] = rna
    out["Situação"] = sit
    return out


def mix_summary(res: pd.DataFrame, p: dict | None = None) -> dict:
    p = {**QUANT_DEFAULTS, **(p or {})}
    n_ok = int((res["Situação"] == PRONTO).sum())
    n_tot = n_ok + int(p["n_bcdna"])
    n_marg = n_tot * (1 + p["margem"])
    return {
        "amostras_prontas": n_ok,
        "brancos": int(p["n_bcdna"]),
        "reacoes": n_tot,
        "reacoes_margem": n_marg,
        "mm_total": n_marg * p["mm_ul"],
        "em_total": n_marg * p["em_ul"],
        "mix_total": n_marg * (p["mm_ul"] + p["em_ul"]),
        "mix_por_tubo": p["mm_ul"] + p["em_ul"],
        "nrt": int(p["n_nrt"]),
    }


def pipetting_list(res: pd.DataFrame, p: dict | None = None) -> pd.DataFrame:
    """Lista de bancada na ordem do POP: 1º mix comum → 2º água → 3º RNA. Inclui os brancos."""
    p = {**QUANT_DEFAULTS, **(p or {})}
    rows = []
    for _, r in res.iterrows():
        if r["Situação"] == "":
            continue
        rows.append({"Tubo": r["Código"], "Grupo": r["Grupo"], "1º Mix comum (µL)": r["1º Mix comum (µL)"],
                     "2º H2O DEPC (µL)": r["2º H2O DEPC (µL)"], "3º RNA (µL)": r["3º RNA (µL)"],
                     "Situação": r["Situação"]})
    for i in range(int(p["n_bcdna"])):
        rows.append({"Tubo": f"BcDNA{'' if p['n_bcdna'] == 1 else i + 1}", "Grupo": "branco",
                     "1º Mix comum (µL)": p["mm_ul"] + p["em_ul"], "2º H2O DEPC (µL)": p["vol_rna_agua_ul"],
                     "3º RNA (µL)": 0.0, "Situação": "Branco do cDNA (água no lugar do RNA)"})
    for i in range(int(p["n_nrt"])):
        rows.append({"Tubo": f"NRT{'' if p['n_nrt'] == 1 else i + 1}", "Grupo": "controle sem RT",
                     "1º Mix comum (µL)": np.nan, "2º H2O DEPC (µL)": np.nan, "3º RNA (µL)": np.nan,
                     "Situação": f"{p['mm_ul']:g} µL MM + {p['em_ul']:g} µL H2O no lugar do EM + pool de RNA"})
    return pd.DataFrame(rows)

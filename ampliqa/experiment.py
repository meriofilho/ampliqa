"""Arquivo do experimento (.xlsx): guarda as entradas do usuário e uma cópia legível dos resultados.

Abas de ENTRADA (lidas de volta pelo app): Experimento, Parametros_cDNA, Quantificacao, qPCR_Ct, qPCR_Grupos,
qPCR_Config. Abas de RESULTADO (só leitura, recalculadas a cada salvamento): Quant_Resultados, Pipetagem_cDNA,
qPCR_Resultados, qPCR_Resumo.
"""
import io
import re
from datetime import datetime

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill

from . import qpcr, quant
from .params import FISHLAB, QPCR_DEFAULTS, QUANT_DEFAULTS

FORMATO = "ampliqa-v1"


def new_experiment(nome="", responsavel="") -> dict:
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    return {
        "meta": {"Experimento": nome, "Responsável": responsavel, "Espécie / tecido": "", "Observações": "",
                 "Criado em": now, "Atualizado em": now, "Formato": FORMATO},
        "quant_params": dict(QUANT_DEFAULTS),
        "quant": quant.empty_table(),
        "qpcr_raw": pd.DataFrame(columns=qpcr.RAW_COLS),
        "qpcr_groups": pd.DataFrame(columns=qpcr.GROUP_COLS),
        "qpcr_cfg": {"ref": "", "controle": "", "ordem_grupos": "", "dup_max": QPCR_DEFAULTS["dup_max"],
                     "blank_lim": QPCR_DEFAULTS["blank_lim"], "letras_grupo": QPCR_DEFAULTS["letras_grupo"],
                     "brancos": ";".join(QPCR_DEFAULTS["brancos"]),
                     "eficiencias": "", "outlier_auto": False},
        "stats_cfg": {},
        "methods_cfg": {},
    }


def _kv(d: dict) -> pd.DataFrame:
    return pd.DataFrame({"Campo": list(d.keys()), "Valor": [str(v) for v in d.values()]})


def _from_kv(df: pd.DataFrame) -> dict:
    return {str(k): ("" if pd.isna(v) else v) for k, v in zip(df["Campo"], df["Valor"])}


def results_tables(exp: dict) -> dict:
    """Calcula as tabelas de resultado a partir das entradas (usado no app e no salvamento)."""
    out = {}
    qres = quant.compute(exp["quant"], exp["quant_params"])
    out["quant"] = qres
    out["pipetagem"] = quant.pipetting_list(qres, exp["quant_params"])
    cfg = exp["qpcr_cfg"]
    raw = exp["qpcr_raw"]
    if len(raw) and cfg.get("ref") and cfg.get("controle") and len(exp["qpcr_groups"]):
        brancos = qpcr.blank_names(exp["qpcr_groups"], [b for b in str(cfg["brancos"]).split(";") if b.strip()])
        auto = cfg.get("outlier_auto") in (True, "True")
        summ = qpcr.summarize(raw, brancos, auto_outlier=auto)
        res = qpcr.ddct(summ, exp["qpcr_groups"], cfg["ref"], cfg["controle"], cfg.get("eficiencias"))
        order = [g for g in str(cfg.get("ordem_grupos", "")).split(";") if g] or None
        out["qpcr"] = res
        out["qpcr_resumo"] = qpcr.group_summary(res, order)
        out["qpcr_brancos"] = qpcr.blanks_check(raw, brancos, float(cfg["blank_lim"]))
        out["qpcr_alertas"] = qpcr.flags(summ, float(cfg["dup_max"]))
        out["qpcr_estabilidade"] = qpcr.ref_stability(summ, exp["qpcr_groups"], cfg["ref"], cfg.get("eficiencias"))
        if auto:
            marked = qpcr.auto_outliers(raw[~raw["Omitir"].fillna(False).astype(bool)])
            out["qpcr_outliers"] = marked[marked["Outlier"]].drop(columns=["Outlier"])
    return out


def to_xlsx(exp: dict) -> bytes:
    exp["meta"]["Atualizado em"] = datetime.now().strftime("%d/%m/%Y %H:%M")
    res = results_tables(exp)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as xw:
        pd.DataFrame({"Arquivo do experimento – Ampliqa": [
            "Este arquivo foi gerado pelo app Ampliqa. Guarde-o no seu Google Drive.",
            "Para continuar o experimento, abra o app e carregue este arquivo na tela Início.",
            "As abas Experimento, Parametros_cDNA, Quantificacao, qPCR_Ct, qPCR_Grupos e qPCR_Config são lidas pelo app.",
            "As abas de resultado (Quant_Resultados, Pipetagem_cDNA, qPCR_Resultados, qPCR_Resumo) são só para consulta.",
            "Ampliqa: desenvolvido por Romério de Oliveira Lima Filho (Dalmolin Systems Biology Group) em parceria com o "
            "Fish Lab – UFRN, seguindo os POPs de Biologia Molecular (PO.OPE.01 a 04BIOMOL). github.com/meriofilho/ampliqa",
        ]}).to_excel(xw, sheet_name="Leia-me", index=False)
        _kv(exp["meta"]).to_excel(xw, sheet_name="Experimento", index=False)
        _kv(exp["quant_params"]).to_excel(xw, sheet_name="Parametros_cDNA", index=False)
        exp["quant"].to_excel(xw, sheet_name="Quantificacao", index=False)
        exp["qpcr_raw"].to_excel(xw, sheet_name="qPCR_Ct", index=False)
        exp["qpcr_groups"].to_excel(xw, sheet_name="qPCR_Grupos", index=False)
        _kv(exp["qpcr_cfg"]).to_excel(xw, sheet_name="qPCR_Config", index=False)
        _kv(exp.get("stats_cfg") or {}).to_excel(xw, sheet_name="Config_Estatistica", index=False)
        _kv(exp.get("methods_cfg") or {}).to_excel(xw, sheet_name="Config_Metodos", index=False)
        res["quant"].to_excel(xw, sheet_name="Quant_Resultados", index=False)
        res["pipetagem"].to_excel(xw, sheet_name="Pipetagem_cDNA", index=False)
        if "qpcr" in res:
            res["qpcr"].to_excel(xw, sheet_name="qPCR_Resultados", index=False)
            res["qpcr_resumo"].to_excel(xw, sheet_name="qPCR_Resumo", index=False)
            if len(res.get("qpcr_estabilidade", [])):
                res["qpcr_estabilidade"].to_excel(xw, sheet_name="qPCR_Estabilidade_Ref", index=False)
    return _style(buf.getvalue())


def _style(data: bytes) -> bytes:
    wb = load_workbook(io.BytesIO(data))
    head_fill = PatternFill("solid", fgColor=FISHLAB["primaria"].lstrip("#"))
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                c.font = Font(name="Aptos", size=10, bold=c.row == 1, color="FFFFFF" if c.row == 1 else "000000")
                if c.row == 1:
                    c.fill = head_fill
                    c.alignment = Alignment(wrap_text=True, vertical="center")
        for col in ws.columns:
            width = max(len(str(c.value)) if c.value is not None else 0 for c in col[:200])
            ws.column_dimensions[col[0].column_letter].width = min(max(10, width + 2), 60)
    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()


def from_xlsx(data: bytes) -> dict:
    sh = pd.read_excel(io.BytesIO(data), sheet_name=None, engine="openpyxl")
    if "Experimento" not in sh:
        raise ValueError("Este arquivo não é um arquivo de experimento do app (falta a aba Experimento).")
    exp = new_experiment()
    exp["meta"].update(_from_kv(sh["Experimento"]))
    if "Parametros_cDNA" in sh:
        for k, v in _from_kv(sh["Parametros_cDNA"]).items():
            if k in QUANT_DEFAULTS:
                exp["quant_params"][k] = type(QUANT_DEFAULTS[k])(float(v))
    if "Quantificacao" in sh:
        exp["quant"] = quant.normalize(sh["Quantificacao"])
    if "qPCR_Ct" in sh:
        r = sh["qPCR_Ct"].reindex(columns=qpcr.RAW_COLS)
        r["Ct"] = pd.to_numeric(r["Ct"], errors="coerce")
        r["Omitir"] = r["Omitir"].fillna(False).astype(bool)
        r["Amostra"] = r["Amostra"].astype(str)
        r["Gene"] = r["Gene"].astype(str)
        exp["qpcr_raw"] = r
    if "qPCR_Grupos" in sh:
        g = sh["qPCR_Grupos"].reindex(columns=qpcr.GROUP_COLS).dropna(subset=["Amostra"])
        g["Amostra"] = g["Amostra"].astype(str)
        g["Grupo"] = g["Grupo"].fillna("").astype(str)
        g["Fator 2"] = [("" if pd.isna(v) else str(int(v)) if isinstance(v, float) and v.is_integer() else str(v))
                        for v in g["Fator 2"]]
        g["Branco"] = g["Branco"].fillna(False).astype(bool)
        exp["qpcr_groups"] = g.reset_index(drop=True)
    if "qPCR_Config" in sh:
        cfg = _from_kv(sh["qPCR_Config"])
        for k in ("dup_max", "blank_lim"):
            if k in cfg and cfg[k] != "":
                cfg[k] = float(cfg[k])
        if "letras_grupo" in cfg and cfg["letras_grupo"] != "":
            cfg["letras_grupo"] = int(float(cfg["letras_grupo"]))
        if "outlier_auto" in cfg:
            cfg["outlier_auto"] = str(cfg["outlier_auto"]) == "True"
        exp["qpcr_cfg"].update({k: ("" if v == "nan" else v) for k, v in cfg.items()})
    for sheet, key in (("Config_Estatistica", "stats_cfg"), ("Config_Metodos", "methods_cfg")):
        if sheet in sh and len(sh[sheet]):
            d = _from_kv(sh[sheet])
            for k, v in list(d.items()):
                if v in ("True", "False"):
                    d[k] = v == "True"
                    continue
                if isinstance(v, str) and re.fullmatch(r"-?\d+(\.\d+)?", v.strip()):
                    d[k] = float(v) if "." in v else int(v)
            exp[key] = d
    return exp

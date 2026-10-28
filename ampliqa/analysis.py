"""Análise estatística completa de um experimento (usada pelas telas Estatística, Figuras e Textos)."""
import io
import re

import pandas as pd

from . import experiment, qpcr, stats

STATS_DEFAULTS = {"metrica": "ΔCt", "comparacao": "controle", "modo_fator2": "por nível", "teste": "Automático",
                  "posthoc": "Automático", "erro": "SEM", "rotulos": ""}

TESTS = ["Automático", "ANOVA de uma via", "ANOVA de Welch", "Kruskal-Wallis", "Teste t de Student",
         "Teste t de Welch", "Mann-Whitney"]
POSTHOCS = ["Automático", "Dunnett", "Tukey", "Games-Howell", "Dunn (Holm)"]


def labels_from(cfg_str: str) -> dict:
    out = {}
    for part in str(cfg_str or "").split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            if k.strip() and v.strip():
                out[k.strip()] = v.strip()
    return out


def labels_to(d: dict) -> str:
    return ";".join(f"{k}={v}" for k, v in d.items() if str(v).strip())


def run(exp: dict, scfg: dict | None = None) -> dict:
    s = {**STATS_DEFAULTS, **(scfg or exp.get("stats_cfg") or {})}
    tabs = experiment.results_tables(exp)
    if "qpcr" not in tabs:
        return {"ok": False, "motivo": "Carregue a corrida e defina grupos, referência e controle na tela qPCR."}
    res, summary = tabs["qpcr"], tabs["qpcr_resumo"]
    cfg = exp["qpcr_cfg"]
    control = cfg["controle"]
    order = [g for g in str(cfg.get("ordem_grupos", "")).split(";") if g] or list(dict.fromkeys(res["Grupo"]))
    order = [g for g in order if g in set(res["Grupo"])]
    if control in order:
        order = [control] + [g for g in order if g != control]
    levels = [""]
    if "Fator 2" in res and (res["Fator 2"] != "").any():
        levels = list(dict.fromkeys(res["Fator 2"]))
    refs = qpcr.ref_list(cfg["ref"])
    genes = [g for g in dict.fromkeys(res["Gene"]) if g not in refs]
    test = None if s["teste"] == "Automático" else s["teste"]
    post = None if s["posthoc"] == "Automático" else s["posthoc"]
    analyses, pvals, two_way = {}, {}, {}
    for gene in genes:
        for lvl in levels:
            sub = res[res["Fator 2"] == lvl] if lvl else res
            d = stats.gene_data(sub, gene, s["metrica"])
            if d.empty:
                continue
            a = stats.analyze(d, order, control, s["comparacao"], test, post)
            analyses[(gene, lvl)] = a
            if "pares" in a:
                for _, r in a["pares"].iterrows():
                    if r["Grupo 1"] == control:
                        pvals[(gene, lvl, r["Grupo 2"])] = r["p ajustado"]
                    elif r["Grupo 2"] == control:
                        pvals[(gene, lvl, r["Grupo 1"])] = r["p ajustado"]
        if len(levels) > 1 and s["modo_fator2"] == "duas vias":
            d = stats.gene_data(res, gene, "ΔCt" if s["metrica"] == "Fold change" else s["metrica"])
            try:
                two_way[gene] = stats.two_way(d)
            except Exception as e:  # noqa: BLE001
                two_way[gene] = str(e)
    n_by_group = res[res["Gene"].isin(genes)].groupby(["Grupo"] + (["Fator 2"] if levels != [""] else []))[
        "Amostra"].nunique()
    n_txt = (str(n_by_group.min()) if n_by_group.min() == n_by_group.max()
             else f"{n_by_group.min()}–{n_by_group.max()}") if len(n_by_group) else "?"
    return {"ok": True, "res": res, "summary": summary, "order": order, "levels": levels, "genes": genes,
            "control": control, "ref": refs, "eff": bool(qpcr.eff_map(cfg.get("eficiencias"))), "analyses": analyses, "pvals": pvals, "two_way": two_way,
            "n_txt": n_txt, "labels": labels_from(s.get("rotulos", "")), "cfg": s, "tabs": tabs}


def overview(an: dict) -> pd.DataFrame:
    rows = []
    for (gene, lvl), a in an["analyses"].items():
        if "omnibus" not in a:
            rows.append({"Gene": gene, "Nível": lvl, "Teste": a.get("erro", "—")})
            continue
        om = a["omnibus"]
        sig = a["pares"][a["pares"]["p ajustado"] < 0.05]
        rows.append({"Gene": gene, "Nível": lvl, "Teste": a["teste"], "Post hoc": a["posthoc"],
                     "Estatística": f"{om['estatística']} = {om['valor']:.2f}", "p": om["p"],
                     "Sig.": stats.stars(om["p"]),
                     "Diferenças (post hoc)": ", ".join(f"{r['Grupo 1']}×{r['Grupo 2']} {r['Significância']}"
                                                        for _, r in sig.iterrows()) or "—"})
    df = pd.DataFrame(rows)
    if "Nível" in df and (df["Nível"] == "").all():
        df = df.drop(columns="Nível")
    return df


def prism_xlsx(an: dict, metric: str = "Fold change") -> bytes:
    """Tabelas prontas para o GraphPad Prism (tabela Column): uma aba por gene (e por nível do 2º fator), um grupo
    por coluna, uma réplica biológica por linha. Inclui os dados limpos e o resumo."""
    res = an["res"]
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as xw:
        pd.DataFrame({"Prism": [
            f"Valores / values: {metric} (média das réplicas técnicas / mean of technical replicates).",
            "Cada aba = um gene; cada coluna = um grupo. / One sheet per gene; one column per group.",
            "Prism: New table → Column → Enter replicate values in stacked columns → colar / paste.",
            f"Referência / reference: {', '.join(an['ref'])}. Controle / control: {an['control']}.",
        ]}).to_excel(xw, sheet_name="Leia-me", index=False)
        used = set()
        for gene in an["genes"]:
            for lvl in an["levels"]:
                sub = res[res["Gene"] == gene]
                if lvl:
                    sub = sub[sub["Fator 2"] == lvl]
                cols = {g: sub[sub["Grupo"] == g][metric].dropna().reset_index(drop=True) for g in an["order"]}
                name = re.sub(r"[\\/*?:\[\]]", "_", f"{gene} {lvl}".strip())[:31]
                while name in used:
                    name = name[:29] + "_" + str(len(used))
                used.add(name)
                pd.DataFrame(cols).to_excel(xw, sheet_name=name, index=False)
        res.to_excel(xw, sheet_name="Dados_limpos", index=False)
        an["summary"].to_excel(xw, sheet_name="Resumo", index=False)
    return buf.getvalue()

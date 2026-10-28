"""Análise de qPCR pelo método 2^-ΔΔCt e planejamento de placa (PO.OPE.03BIOMOL)."""
import math
import string

import numpy as np
import pandas as pd

from .params import QPCR_DEFAULTS, QPCR_MIX

RAW_COLS = ["Poço", "Amostra", "Gene", "Ct", "Omitir"]


# ---------------------------------------------------------------- grupos
def is_blank(sample: str, blanks) -> bool:
    """Branco = nome com BRANCO/NTC/BcDNA/NRT/BLANK (com ou sem número) ou um dos nomes da lista."""
    from .importers import is_blank_name
    return is_blank_name(sample, blanks or [])


GROUP_COLS = ["Amostra", "Grupo", "Fator 2", "Branco"]


def default_groups(samples, n_letters=1, blanks=None, known: pd.DataFrame | None = None) -> pd.DataFrame:
    """Uma linha por amostra. Grupo = primeiras letras do código (A1, A2 → A), a não ser que o arquivo já traga
    os grupos (known). Brancos ficam marcados e sem grupo."""
    blanks = blanks if blanks is not None else QPCR_DEFAULTS["brancos"]
    known_map, known_f2 = {}, {}
    if known is not None and len(known):
        known_map = dict(zip(known["Amostra"].astype(str), known["Grupo"].astype(str)))
        if "Fator 2" in known:
            known_f2 = dict(zip(known["Amostra"].astype(str), known["Fator 2"].fillna("").astype(str)))
    rows = []
    for s in dict.fromkeys(samples):
        if s is None or str(s).strip() == "":
            continue
        s = str(s)
        bl = is_blank(s, blanks)
        rows.append({"Amostra": s, "Grupo": "" if bl else known_map.get(s, s[:int(n_letters)]),
                     "Fator 2": known_f2.get(s, ""), "Branco": bl})
    return pd.DataFrame(rows, columns=GROUP_COLS)


def blank_names(groups: pd.DataFrame, extra=()) -> list:
    """Nomes tratados como branco: os da configuração + os marcados na tabela de grupos."""
    marked = []
    if groups is not None and len(groups) and "Branco" in groups:
        marked = groups.loc[groups["Branco"].fillna(False).astype(bool), "Amostra"].astype(str).tolist()
    return list(dict.fromkeys([*extra, *marked]))


def sample_groups(groups: pd.DataFrame) -> pd.DataFrame:
    g = groups.copy()
    if "Branco" in g:
        g = g[~g["Branco"].fillna(False).astype(bool)]
    g = g[g["Grupo"].astype(str).str.strip() != ""]
    if "Fator 2" not in g:
        g["Fator 2"] = ""
    g["Fator 2"] = g["Fator 2"].fillna("").astype(str).str.strip()
    return g[["Amostra", "Grupo", "Fator 2"]]


def has_factor2(groups: pd.DataFrame) -> bool:
    return groups is not None and "Fator 2" in groups and (groups["Fator 2"].fillna("").astype(str).str.strip() != "").any()


# ---------------------------------------------------------------- médias
def auto_outliers(raw: pd.DataFrame, sd_cut=0.3, max_prop=0.5, preserve=True) -> pd.DataFrame:
    """Marca réplicas técnicas discrepantes (critério do Auto-qPCR, Maussion et al. 2021, Sci Rep 11:21293):
    se o DP das réplicas de uma amostra × gene passa de sd_cut, remove a réplica mais distante da média, de forma
    recursiva, até o DP ficar abaixo do corte ou até atingir a proporção máxima removida (max_prop), sempre
    mantendo pelo menos 2 réplicas. Com preserve=True, mantém tudo quando |média − mediana| < 0,1 (sem outlier claro).
    Devolve uma cópia com a coluna "Outlier" (True = réplica removida pelo critério)."""
    d = raw.copy()
    d["Outlier"] = False
    for _, idx in d.groupby(["Amostra", "Gene"], sort=False).groups.items():
        sub = d.loc[idx]
        keep = list(sub.index[sub["Ct"].notna() & ~sub["Omitir"].fillna(False).astype(bool)])
        n0 = len(keep)
        if n0 < 3:
            continue
        while len(keep) > 2 and (n0 - len(keep) + 1) / n0 <= max_prop:
            v = d.loc[keep, "Ct"]
            if v.std(ddof=1) <= sd_cut:
                break
            if preserve and abs(v.mean() - v.median()) < 0.1:
                break
            far = (v - v.mean()).abs().idxmax()
            d.loc[far, "Outlier"] = True
            keep.remove(far)
    return d


def summarize(raw: pd.DataFrame, blanks=None, auto_outlier=False) -> pd.DataFrame:
    """Uma linha por amostra × gene: Cq médio, nº de réplicas com Ct, diferença entre réplicas."""
    blanks = blanks if blanks is not None else QPCR_DEFAULTS["brancos"]
    d = raw.copy()
    if "Omitir" in d:
        d = d[~d["Omitir"].fillna(False).astype(bool)]
    if auto_outlier:
        d = auto_outliers(d)
        d = d[~d["Outlier"]]
    d = d[~d["Amostra"].apply(lambda s: is_blank(s, blanks))]
    g = d.groupby(["Amostra", "Gene"], sort=False)["Ct"]
    out = pd.DataFrame({
        "Poços": g.size(),
        "Réplicas com Ct": g.count(),
        "Ct médio": g.mean(),
        "Diferença entre réplicas": g.max() - g.min(),
    }).reset_index()
    out.loc[out["Réplicas com Ct"] < 2, "Diferença entre réplicas"] = np.nan
    return out


def blanks_check(raw: pd.DataFrame, blanks=None, limit=None) -> pd.DataFrame:
    blanks = blanks if blanks is not None else QPCR_DEFAULTS["brancos"]
    limit = QPCR_DEFAULTS["blank_lim"] if limit is None else limit
    d = raw[raw["Amostra"].apply(lambda s: is_blank(s, blanks))]
    rows = []
    for gene in dict.fromkeys(raw["Gene"]):
        sub = d[d["Gene"] == gene]
        n_ct = int(sub["Ct"].notna().sum())
        min_ct = float(sub["Ct"].min()) if n_ct else np.nan
        if len(sub) == 0:
            st = "Sem branco para este gene"
        elif n_ct == 0:
            st = "OK – sem amplificação"
        elif min_ct > limit:
            st = "OK – Ct acima do limite"
        else:
            st = "ATENÇÃO – possível contaminação"
        rows.append({"Gene": gene, "Poços de branco": len(sub), "Poços com Ct": n_ct, "Menor Ct": min_ct,
                     "Situação": st})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- quantificação relativa (qBase / ΔΔCt)
def ref_list(ref) -> list:
    if isinstance(ref, (list, tuple)):
        return [r for r in ref if str(r).strip()]
    return [r.strip() for r in str(ref or "").split(";") if r.strip()]


def eff_map(effs) -> dict:
    """Eficiência por gene em %, como dict {gene: base E}. Aceita dict ou texto 'gene=98.5;gene2=101'."""
    out = {}
    if isinstance(effs, dict):
        items = effs.items()
    else:
        items = [p.split("=", 1) for p in str(effs or "").split(";") if "=" in p]
    for k, v in items:
        try:
            pct = float(str(v).replace(",", "."))
        except ValueError:
            continue
        if 50 <= pct <= 150:
            out[str(k).strip()] = 1 + pct / 100
    return out


def ddct(summary: pd.DataFrame, groups: pd.DataFrame, ref_gene, control: str, efficiencies=None) -> pd.DataFrame:
    """Quantidade relativa normalizada (NRQ) no modelo generalizado do qBase (Hellemans et al. 2007, Genome Biol
    8:R19): eficiência específica de cada gene e normalização pela média geométrica de 1 a 5 genes de referência.
    O calibrador é a média do Cq do grupo controle (em cada nível do 2º fator, se houver), então o fold change é
    relativo ao controle. Com eficiência de 100% (E = 2) e um gene de referência, o resultado é idêntico ao 2^−ΔΔCt
    de Livak & Schmittgen (2001).

    Colunas: ΔCt (Cq·log2E do gene − média de Cq·log2E das referências; com E = 2 é o ΔCt clássico), ΔΔCt (= −log2 NRQ), Fold change (NRQ),
    log2 fold change."""
    refs = ref_list(ref_gene)
    E = eff_map(efficiencies)
    s = summary.merge(sample_groups(groups), on="Amostra", how="inner")
    keys = ["Gene", "Fator 2"] if (s["Fator 2"] != "").any() else ["Gene"]
    calib = s[s["Grupo"] == control].groupby(keys)["Ct médio"].mean().rename("Cq calibrador")
    s = s.merge(calib, on=keys, how="left")
    base = s["Gene"].map(lambda g: E.get(g, 2.0))
    s["log2 RQ"] = (s["Cq calibrador"] - s["Ct médio"]) * np.log2(base)
    rq = s[s["Gene"].isin(refs)].pivot_table(index="Amostra", columns="Gene", values="log2 RQ")
    ok = rq.reindex(columns=refs).notna().all(axis=1) if refs else pd.Series(dtype=bool)
    nf = rq.reindex(columns=refs).mean(axis=1).where(ok)   # log2 da média geométrica dos RQ das referências
    r = s[s["Gene"].isin(refs)]
    ctref = r.pivot_table(index="Amostra", columns="Gene", values="Ct médio").reindex(columns=refs).mean(axis=1)
    wref = r.assign(w=r["Ct médio"] * np.log2(base[r.index])) \
        .pivot_table(index="Amostra", columns="Gene", values="w").reindex(columns=refs).mean(axis=1)
    s["Ct referência"] = s["Amostra"].map(ctref.where(ok))
    # ΔCt ponderado pela eficiência (Cq·log2 E); com E = 2 é o ΔCt clássico. ΔΔCt = ΔCt − média do controle.
    s["ΔCt"] = s["Ct médio"] * np.log2(base) - s["Amostra"].map(wref.where(ok))
    s["log2 fold change"] = s["log2 RQ"] - s["Amostra"].map(nf) + 0.0
    s["ΔΔCt"] = -s["log2 fold change"] + 0.0
    s["Fold change"] = np.power(2.0, s["log2 fold change"])
    s["Eficiência (%)"] = (base - 1) * 100
    return s.drop(columns=["log2 RQ", "Cq calibrador"])


def ref_stability(summary: pd.DataFrame, groups: pd.DataFrame, refs, efficiencies=None) -> pd.DataFrame:
    """Estabilidade dos genes de referência (Hellemans et al. 2007): CV dos NRQ e M do geNorm
    (Vandesompele et al. 2002). Exige 2 ou mais referências. Valores típicos de referências estáveis: CV < 25% e
    M < 0,5 (amostras homogêneas); até 50% e 1 em amostras heterogêneas."""
    refs = ref_list(refs)
    if len(refs) < 2:
        return pd.DataFrame()
    E = eff_map(efficiencies)
    s = summary.merge(sample_groups(groups), on="Amostra", how="inner")
    s = s[s["Gene"].isin(refs)]
    mean_cq = s.groupby("Gene")["Ct médio"].mean()          # calibrador = média de todas as amostras (qBase)
    s = s.assign(l2rq=(s["Gene"].map(mean_cq) - s["Ct médio"]) * np.log2(s["Gene"].map(lambda g: E.get(g, 2.0))))
    A = s.pivot_table(index="Amostra", columns="Gene", values="l2rq").reindex(columns=refs).dropna()
    if len(A) < 3:
        return pd.DataFrame()
    nrq = np.power(2.0, A.sub(A.mean(axis=1), axis=0))
    rows = []
    for p in refs:
        V = [np.std(A[p] - A[q], ddof=1) for q in refs if q != p]
        cv = nrq[p].std(ddof=1) / nrq[p].mean()
        rows.append({"Gene": p, "M (geNorm)": float(np.mean(V)), "CV (%)": float(cv * 100), "Amostras": len(A)})
    out = pd.DataFrame(rows)
    def judge(r):
        if r["M (geNorm)"] < 0.5 and r["CV (%)"] < 25:
            return "Estável"
        if r["M (geNorm)"] < 1 and r["CV (%)"] < 50:
            return "Aceitável para amostras heterogêneas"
        return "Instável – revisar"
    out["Avaliação"] = out.apply(judge, axis=1)
    return out


def group_summary(res: pd.DataFrame, group_order=None) -> pd.DataFrame:
    keys = ["Gene", "Fator 2", "Grupo"] if "Fator 2" in res and (res["Fator 2"] != "").any() else ["Gene", "Grupo"]
    g = res.dropna(subset=["Fold change"]).groupby(keys, sort=False)
    out = pd.DataFrame({
        "n": g["Fold change"].count(),
        "Fold change médio": g["Fold change"].mean(),
        "Desvio padrão": g["Fold change"].std(ddof=1),
        "Erro padrão": g["Fold change"].std(ddof=1) / np.sqrt(g["Fold change"].count()),
        "log2FC médio": g["log2 fold change"].mean() + 0.0,
    }).reset_index()
    if group_order:
        out["Grupo"] = pd.Categorical(out["Grupo"], categories=list(group_order), ordered=True)
        out = out.sort_values(keys).reset_index(drop=True)
        out["Grupo"] = out["Grupo"].astype(str)
    return out


def flags(summary: pd.DataFrame, dup_max: float) -> pd.DataFrame:
    """Alertas por amostra × gene."""
    rows = []
    for _, r in summary.iterrows():
        if r["Réplicas com Ct"] == 0:
            rows.append((r["Amostra"], r["Gene"], "Nenhuma réplica amplificou"))
        elif r["Réplicas com Ct"] < r["Poços"]:
            rows.append((r["Amostra"], r["Gene"], f"Só {int(r['Réplicas com Ct'])} de {int(r['Poços'])} réplicas com Ct"))
        if pd.notna(r["Diferença entre réplicas"]) and r["Diferença entre réplicas"] > dup_max:
            rows.append((r["Amostra"], r["Gene"], f"Diferença entre réplicas = {r['Diferença entre réplicas']:.2f} Ct"))
    return pd.DataFrame(rows, columns=["Amostra", "Gene", "Alerta"])


# ---------------------------------------------------------------- exemplo
def example_run(seed=11) -> pd.DataFrame:
    """Corrida fictícia no formato do QuantStudio: 11 amostras em duplicata + 2 brancos por gene."""
    rnd = np.random.default_rng(seed)
    samples = ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3", "D1", "D2"]
    base = {"actb1": 18.6, "gene_alvo_A": 24.3, "gene_alvo_B": 27.1}
    eff = {"B": {"gene_alvo_A": -0.6, "gene_alvo_B": 0.3}, "C": {"gene_alvo_A": -1.2, "gene_alvo_B": 0.7},
           "D": {"gene_alvo_A": -1.6, "gene_alvo_B": 1.1}}
    bio = {s: rnd.uniform(-0.25, 0.25) for s in samples}
    rows, w = [], 0
    for gene, b in base.items():
        for s in samples:
            mu = b + bio[s] + eff.get(s[0], {}).get(gene, 0) + rnd.uniform(-0.2, 0.2)
            for _ in range(2):
                rows.append((gene, s, round(mu + rnd.uniform(-0.12, 0.12), 3)))
        rows += [(gene, "BRANCO", np.nan), (gene, "BRANCO", 36.12 if gene == "gene_alvo_A" else np.nan)]
    out = []
    for i, (gene, s, ct) in enumerate(rows):
        r, c = divmod(i % 96, 12)
        out.append({"Poço": f"{ROWS_ALL[r]}{c + 1}", "Amostra": s, "Gene": gene, "Ct": ct, "Omitir": False})
    df = pd.DataFrame(out)
    df.loc[(df["Amostra"] == "B2") & (df["Gene"] == "gene_alvo_B"), "Ct"] = [27.6, np.nan]
    return df


ROWS_ALL = list(string.ascii_uppercase[:8])


# ---------------------------------------------------------------- placa
ROWS = list(string.ascii_uppercase[:8])


def plan_plate(samples, genes, blanks=("NTC", "BcDNA"), reps=2):
    """Distribui, gene a gene, as amostras em duplicata seguidas dos brancos (1 poço cada),
    preenchendo a placa por linhas (A1→A12, B1→B12...), como no mapa do PO.OPE.03BIOMOL.
    Retorna (lista de poços, nº de placas)."""
    wells = []
    for gene in genes:
        for s in samples:
            for _ in range(reps):
                wells.append({"Gene": gene, "Amostra": s})
        for b in blanks:
            wells.append({"Gene": gene, "Amostra": b})
    out = []
    for i, w in enumerate(wells):
        plate, pos = divmod(i, 96)
        row, col = divmod(pos, 12)
        out.append({"Placa": plate + 1, "Poço": f"{ROWS[row]}{col + 1}", "Linha": ROWS[row], "Coluna": col + 1,
                    "Nº do poço": pos + 1, **w})
    n_plates = max(1, math.ceil(len(wells) / 96))
    return pd.DataFrame(out), n_plates


def plate_grid(plan: pd.DataFrame, plate=1) -> pd.DataFrame:
    grid = pd.DataFrame("", index=ROWS, columns=[str(c) for c in range(1, 13)])
    for _, w in plan[plan["Placa"] == plate].iterrows():
        grid.loc[w["Linha"], str(w["Coluna"])] = f"{w['Gene']}\n{w['Amostra']}"
    return grid


def mix_per_gene(plan: pd.DataFrame, protocol: str, margin=0.10) -> pd.DataFrame:
    vols = QPCR_MIX[protocol]
    rows = []
    for gene, n in plan.groupby("Gene", sort=False).size().items():
        nm = n * (1 + margin)
        rows.append({"Gene": gene, "Poços": n, "Reações (+margem)": round(nm, 1),
                     **{f"{k} (µL)": round(v * nm, 1) for k, v in vols.items() if k != "cDNA"},
                     "Mix por poço (µL)": sum(v for k, v in vols.items() if k != "cDNA"),
                     "cDNA por poço (µL)": vols["cDNA"]})
    return pd.DataFrame(rows)

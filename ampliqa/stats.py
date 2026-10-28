"""Estatística para expressão gênica relativa (qPCR).

Escala da análise
-----------------
Por padrão os testes são feitos sobre o ΔCt de cada amostra (réplica biológica). Testar o ΔCt dá exatamente os
mesmos p-valores que testar o log2 fold change (log2FC = −ΔCt + constante) e segue a literatura:
- Yuan et al. (2006) BMC Bioinformatics 7:85 – o Ct/ΔCt é a variável diretamente afetada pelo tratamento;
- Rieu & Powers (2009) The Plant Cell 21:1031 – quantidades relativas (fold change) devem ser log-transformadas
  antes dos testes;
- Bustin et al. (2009, MIQE; 2025, MIQE 2.0) – descrever e justificar a análise estatística.
O fold change (2^−ΔΔCt) é usado para apresentar os resultados. Testar o próprio fold change continua disponível
para manter comparabilidade com análises antigas, com aviso.
"""
from itertools import combinations

import numpy as np
import pandas as pd
from scipy import stats as ss

from .i18n import lang as _lang, t

ALPHA = 0.05
METRICS = {
    "ΔCt (recomendado – mesmos p-valores do log2FC)": "ΔCt",
    "log2 fold change": "log2 fold change",
    "Fold change (2^−ΔΔCt) – como em análises antigas": "Fold change",
}


# ------------------------------------------------------------------ utilidades
def stars(p):
    if p is None or pd.isna(p):
        return ""
    return "****" if p < 1e-4 else "***" if p < 1e-3 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"


def fmt_p(p, lang="pt"):
    """p formatado; lang=None usa o idioma da sessão."""
    lang = lang or _lang()
    if p is None or pd.isna(p):
        return "–"
    if p < 1e-4:
        s = "p < 0.0001"
    elif p < 0.001:
        s = f"p = {p:.4f}"
    elif p < 0.01:
        s = f"p = {p:.3f}"
    else:
        s = f"p = {p:.2f}" if p >= 0.1 else f"p = {p:.3f}"
    return s.replace(".", ",") if lang == "pt" else s


def _groups(df, order):
    order = [g for g in order if g in set(df["Grupo"])]
    return order, [df.loc[df["Grupo"] == g, "valor"].dropna().to_numpy(float) for g in order]


# ------------------------------------------------------------------ premissas
def assumptions(df, order):
    """Shapiro-Wilk nos resíduos (valor − média do grupo) e Brown-Forsythe (Levene com mediana)."""
    order, samples = _groups(df, order)
    resid = np.concatenate([s - s.mean() for s in samples if len(s)]) if samples else np.array([])
    out = {"n": {g: len(s) for g, s in zip(order, samples)}, "shapiro_p": np.nan, "levene_p": np.nan}
    if len(resid) >= 3 and np.ptp(resid) > 0:
        out["shapiro_p"] = float(ss.shapiro(resid).pvalue)
    valid = [s for s in samples if len(s) >= 2]
    if len(valid) >= 2 and all(np.ptp(s) > 0 for s in valid):
        out["levene_p"] = float(ss.levene(*valid, center="median").pvalue)
    return out


def recommend(assump, comparison="controle", alpha=ALPHA):
    """Escolhe teste e post hoc a partir do desenho (nº de grupos, n) e das premissas, explicando o motivo."""
    n = assump["n"]
    k = len([g for g, v in n.items() if v > 0])
    nmin = min(n.values()) if n else 0
    sw, lev = assump["shapiro_p"], assump["levene_p"]
    normal = pd.isna(sw) or sw >= alpha
    homog = pd.isna(lev) or lev >= alpha
    why = []
    if nmin < 3:
        why.append(t("Atenção: há grupo com n = {n}. Com menos de 3 réplicas biológicas por grupo, qualquer teste "
                     "tem baixa confiabilidade – interprete com cautela e descreva o n na legenda.", n=nmin))
    if nmin <= 5:
        why.append(t("Com n pequeno (≤ 5 por grupo), os testes de normalidade e de homogeneidade têm pouco poder: um "
                     "p > 0,05 não prova que as premissas são atendidas. Em qPCR, a escala ΔCt (log) costuma deixar os "
                     "dados aproximadamente normais, o que favorece testes paramétricos."))
    why.append(t("Normalidade dos resíduos (Shapiro-Wilk): {p} → {r}.", p=fmt_p(sw, None),
                 r=t("sem evidência contra a normalidade") if normal else t("desvio da normalidade")))
    why.append(t("Homogeneidade das variâncias (Brown-Forsythe/Levene): {p} → {r}.", p=fmt_p(lev, None),
                 r=t("variâncias semelhantes") if homog else t("variâncias diferentes")))
    if k == 2:
        if normal and homog:
            test, post = "Teste t de Student", "—"
            why.append(t("Dois grupos, dados normais e variâncias semelhantes: teste t de Student."))
        elif normal:
            test, post = "Teste t de Welch", "—"
            why.append(t("Dois grupos com variâncias diferentes: teste t de Welch (não assume variâncias iguais)."))
        else:
            test, post = "Mann-Whitney", "—"
            why.append(t("Dois grupos sem normalidade: Mann-Whitney (não paramétrico). Com n = 3 por grupo, o menor "
                         "p possível é 0,1 – ele não consegue dar significância; prefira o teste t na escala ΔCt."))
        return {"teste": test, "posthoc": post, "motivos": why}
    if normal and homog:
        test = "ANOVA de uma via"
        post = "Dunnett" if comparison == "controle" else "Tukey"
        why.append(t("Premissas atendidas: ANOVA de uma via. Post hoc de Dunnett, que compara cada grupo apenas com o "
                     "controle (mais poder que o Tukey quando essa é a pergunta).") if post == "Dunnett" else
                   t("Premissas atendidas: ANOVA de uma via. Post hoc de Tukey, que compara todos os pares de grupos "
                     "controlando o erro do conjunto."))
    elif normal:
        test, post = "ANOVA de Welch", "Games-Howell"
        why.append(t("Dados normais, mas com variâncias diferentes: ANOVA de Welch (não assume variâncias iguais) com "
                     "post hoc de Games-Howell (o app mostra as comparações com o controle).")
                   if comparison == "controle" else
                   t("Dados normais, mas com variâncias diferentes: ANOVA de Welch (não assume variâncias iguais) com "
                     "post hoc de Games-Howell."))
    else:
        test, post = "Kruskal-Wallis", "Dunn (Holm)"
        why.append(t("Dados sem normalidade: Kruskal-Wallis (não paramétrico, compara postos) com post hoc de Dunn e "
                     "correção de Holm. Com n = 3 por grupo, testes não paramétricos têm pouquíssimo poder."))
    return {"teste": test, "posthoc": post, "motivos": why}


# ------------------------------------------------------------------ testes omnibus
def welch_anova(samples):
    k = len(samples)
    n = np.array([len(s) for s in samples], float)
    m = np.array([s.mean() for s in samples])
    v = np.array([s.var(ddof=1) for s in samples])
    w = n / v
    mw = (w * m).sum() / w.sum()
    a = (w * (m - mw) ** 2).sum() / (k - 1)
    tmp = (((1 - w / w.sum()) ** 2) / (n - 1)).sum()
    b = 1 + 2 * (k - 2) / (k ** 2 - 1) * tmp
    F = a / b
    df2 = (k ** 2 - 1) / (3 * tmp)
    return F, k - 1, df2, float(ss.f.sf(F, k - 1, df2))


def omnibus(test, samples):
    k = len(samples)
    N = sum(len(s) for s in samples)
    if test == "ANOVA de uma via":
        r = ss.f_oneway(*samples)
        return {"estatística": "F", "valor": float(r.statistic), "df1": k - 1, "df2": N - k, "p": float(r.pvalue)}
    if test == "ANOVA de Welch":
        F, d1, d2, p = welch_anova(samples)
        return {"estatística": "F de Welch", "valor": F, "df1": d1, "df2": d2, "p": p}
    if test == "Kruskal-Wallis":
        r = ss.kruskal(*samples)
        return {"estatística": "H", "valor": float(r.statistic), "df1": k - 1, "df2": None, "p": float(r.pvalue)}
    if test in ("Teste t de Student", "Teste t de Welch"):
        r = ss.ttest_ind(samples[1], samples[0], equal_var=test == "Teste t de Student")
        return {"estatística": "t", "valor": float(r.statistic), "df1": float(r.df), "df2": None, "p": float(r.pvalue)}
    if test == "Mann-Whitney":
        r = ss.mannwhitneyu(samples[1], samples[0], alternative="two-sided")
        return {"estatística": "U", "valor": float(r.statistic), "df1": None, "df2": None, "p": float(r.pvalue)}
    raise ValueError(test)


# ------------------------------------------------------------------ post hoc
def _holm(p):
    p = np.asarray(p, float)
    order = np.argsort(p)
    adj = np.empty_like(p)
    running = 0.0
    m = len(p)
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * p[i]))
        adj[i] = running
    return adj


def posthoc(name, order, samples, control=None, comparison="controle"):
    """Devolve DataFrame com Grupo 1, Grupo 2, p ajustado (Grupo 1 = controle nas comparações com controle)."""
    pairs = []
    ci = order.index(control) if control in order else 0
    if name == "Tukey":
        r = ss.tukey_hsd(*samples)
        for i, j in combinations(range(len(order)), 2):
            pairs.append((order[i], order[j], float(r.pvalue[i, j])))
    elif name == "Dunnett":
        others = [s for k, s in enumerate(samples) if k != ci]
        r = ss.dunnett(*others, control=samples[ci])
        for g, p in zip([g for k, g in enumerate(order) if k != ci], r.pvalue):
            pairs.append((order[ci], g, float(p)))
    elif name == "Games-Howell":
        k = len(order)
        for i, j in combinations(range(k), 2):
            a, b = samples[i], samples[j]
            va, vb = a.var(ddof=1) / len(a), b.var(ddof=1) / len(b)
            se = np.sqrt(va + vb)
            t = abs(a.mean() - b.mean()) / se
            df = (va + vb) ** 2 / (va ** 2 / (len(a) - 1) + vb ** 2 / (len(b) - 1))
            p = float(ss.studentized_range.sf(t * np.sqrt(2), k, df))
            pairs.append((order[i], order[j], min(1.0, p)))
    elif name.startswith("Dunn"):
        allv = np.concatenate(samples)
        ranks = ss.rankdata(allv)
        N = len(allv)
        _, counts = np.unique(allv, return_counts=True)
        tie = (counts ** 3 - counts).sum() / (12 * (N - 1))
        bounds = np.cumsum([0] + [len(s) for s in samples])
        mr = [ranks[bounds[i]:bounds[i + 1]].mean() for i in range(len(samples))]
        raw = []
        idx = [(ci, j) for j in range(len(order)) if j != ci] if comparison == "controle" \
            else list(combinations(range(len(order)), 2))
        for i, j in idx:
            se = np.sqrt((N * (N + 1) / 12 - tie) * (1 / len(samples[i]) + 1 / len(samples[j])))
            z = abs(mr[i] - mr[j]) / se
            raw.append(2 * ss.norm.sf(z))
        adj = _holm(raw)
        for (i, j), p in zip(idx, adj):
            pairs.append((order[i], order[j], float(p)))
    out = pd.DataFrame(pairs, columns=["Grupo 1", "Grupo 2", "p ajustado"])
    if comparison == "controle" and len(out):
        out = out[(out["Grupo 1"] == control) | (out["Grupo 2"] == control)].copy()
        swap = out["Grupo 2"] == control
        out.loc[swap, ["Grupo 1", "Grupo 2"]] = out.loc[swap, ["Grupo 2", "Grupo 1"]].to_numpy()
    out["Significância"] = out["p ajustado"].map(stars)
    return out.reset_index(drop=True)


# ------------------------------------------------------------------ outliers
def grubbs(df, order, alpha=ALPHA):
    """Grubbs bilateral em cada grupo (n ≥ 3). Devolve uma linha por grupo testado."""
    rows = []
    for g in order:
        sub = df[df["Grupo"] == g].dropna(subset=["valor"])
        x = sub["valor"].to_numpy(float)
        n = len(x)
        if n < 3 or x.std(ddof=1) == 0:
            continue
        dev = np.abs(x - x.mean())
        i = int(dev.argmax())
        G = dev[i] / x.std(ddof=1)
        t = ss.t.ppf(1 - alpha / (2 * n), n - 2)
        Gc = (n - 1) / np.sqrt(n) * np.sqrt(t ** 2 / (n - 2 + t ** 2))
        rows.append({"Grupo": g, "n": n, "Amostra suspeita": sub.iloc[i]["Amostra"], "G": G, "G crítico": Gc,
                     "Outlier?": "Sim" if G > Gc else "Não"})
    return pd.DataFrame(rows)


OUTLIER_GUIDE = (
    "O teste de Grubbs só aponta valores estatisticamente afastados; ele não diz que o valor está errado. "
    "Com n = 3, o G máximo possível (1,155) é praticamente igual ao crítico (1,153), então o teste quase nunca "
    "detecta nada – com poucas réplicas, olhe os dados. Antes de excluir uma amostra: (1) confira as réplicas "
    "técnicas (diferença > 0,5 Ct), a curva de melting e os brancos; (2) confira a qualidade do RNA (A260/280, "
    "A260/230) e o Ct do gene de referência dessa amostra; (3) procure anotações de problema na coleta, extração ou "
    "pipetagem. Só exclua com justificativa técnica, nunca apenas porque o valor 'atrapalha' o resultado, e informe "
    "a exclusão e o motivo nos métodos.")


# ------------------------------------------------------------------ letras (compact letter display)
def letters(order, means, pairs, alpha=ALPHA):
    """Letras de significância: grupos que compartilham uma letra não diferem."""
    sig = set()
    for _, r in pairs.iterrows():
        if r["p ajustado"] < alpha:
            sig.add(frozenset((r["Grupo 1"], r["Grupo 2"])))
    groups = sorted(order, key=lambda g: -means.get(g, 0))
    cols = [set(groups)]
    changed = True
    while changed:
        changed = False
        for pair in list(sig):
            a, b = tuple(pair)
            for c in list(cols):
                if a in c and b in c:
                    cols.remove(c)
                    cols += [c - {a}, c - {b}]
                    changed = True
        # remove colunas contidas em outras
        cols = [c for c in cols if c and not any(c < d for d in cols)]
        cols = [set(t) for t in {frozenset(c) for c in cols}]
    cols.sort(key=lambda c: min(groups.index(g) for g in c))
    out = {g: "" for g in order}
    for i, c in enumerate(cols):
        for g in c:
            out[g] += "abcdefghijklmnopqrstuvwxyz"[i]
    return out


# ------------------------------------------------------------------ análise por gene
def gene_data(res, gene, metric):
    sub = res[(res["Gene"] == gene)].copy()
    sub["valor"] = sub[metric]
    return sub.dropna(subset=["valor"])


def analyze(df, order, control, comparison="controle", test=None, post=None, alpha=ALPHA):
    """df: colunas Amostra, Grupo, valor. Faz premissas, recomendação, omnibus, post hoc e outliers."""
    avisos = []
    small = [g for g in order if 0 < (df["Grupo"] == g).sum() < 2]
    if small:
        avisos.append("Grupo(s) com só 1 réplica biológica ficaram fora da estatística (aparecem no gráfico): "
                      + ", ".join(small) + ".")
        df = df[~df["Grupo"].isin(small)]
    order = [g for g in order if (df["Grupo"] == g).sum() > 0]
    if control not in order:
        return {"ordem": order, "erro": "O grupo controle não tem réplicas suficientes (mínimo 2).", "avisos": avisos}
    asp = assumptions(df, order)
    rec = recommend(asp, comparison, alpha)
    test = test or rec["teste"]
    post = post or rec["posthoc"]
    order_, samples = _groups(df, order)
    out = {"ordem": order_, "premissas": asp, "recomendação": rec, "teste": test, "posthoc": post, "avisos": avisos}
    if len(order_) < 2 or any(len(s) < 2 for s in samples):
        out["erro"] = "É preciso ter pelo menos 2 grupos com 2 ou mais réplicas biológicas."
        return out
    if test.startswith("Teste t") or test == "Mann-Whitney":
        if control in order_ and order_.index(control) != 0:
            i = order_.index(control)
            order_ = [order_[i]] + [g for g in order_ if g != control]
            samples = [samples[i]] + [s for k, s in enumerate(samples) if k != i]
    out["omnibus"] = omnibus(test, samples)
    if post != "—" and len(order_) > 2:
        out["pares"] = posthoc(post, order_, samples, control, comparison)
    else:
        out["pares"] = pd.DataFrame([(order_[0], order_[1], out["omnibus"]["p"])],
                                    columns=["Grupo 1", "Grupo 2", "p ajustado"])
        out["pares"]["Significância"] = out["pares"]["p ajustado"].map(stars)
    out["outliers"] = grubbs(df, order_, alpha)
    return out


def two_way(df, f1="Grupo", f2="Fator 2"):
    """ANOVA de duas vias com interação (tipo II). df: colunas valor, Grupo, Fator 2."""
    import statsmodels.formula.api as smf
    from statsmodels.stats.anova import anova_lm
    d = df.rename(columns={f1: "A", f2: "B"}).dropna(subset=["valor"])
    model = smf.ols("valor ~ C(A) * C(B)", data=d).fit()
    tab = anova_lm(model, typ=2).reset_index().rename(columns={"index": "Fonte", "sum_sq": "SQ", "df": "gl",
                                                               "F": "F", "PR(>F)": "p"})
    tab["Fonte"] = tab["Fonte"].replace({"C(A)": f"{f1}", "C(B)": f"{f2}", "C(A):C(B)": f"Interação {f1} × {f2}",
                                         "Residual": "Resíduo"})
    return tab


TWO_WAY_NOTE = (
    "A ANOVA de duas vias testa, ao mesmo tempo, o efeito do tratamento, o efeito do segundo fator (ex.: idade) e a "
    "interação entre eles. Use quando a pergunta envolve os dois fatores juntos (ex.: \"o efeito do etanol muda com a "
    "idade?\"). Cuidados: (1) interprete primeiro a interação – se ela for significativa, os efeitos principais "
    "sozinhos podem enganar, e o correto é comparar os grupos dentro de cada nível do segundo fator (opção \"por "
    "nível\"); (2) no 2^−ΔΔCt cada nível costuma ser normalizado pelo seu próprio controle, então o efeito principal "
    "do segundo fator no fold change perde o sentido – analise na escala ΔCt; (3) com n = 3 por célula o poder para "
    "detectar interação é baixo.")

"""Figuras para publicação (matplotlib): barras de expressão gênica e heatmap. Exporta PNG 300 dpi e SVG."""
import io
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm  # noqa: E402

from .stats import stars  # noqa: E402

FONT_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"
for f in FONT_DIR.glob("*.ttf"):
    font_manager.fontManager.addfont(str(f))
plt.rcParams.update({"font.family": ["Roboto", "DejaVu Sans"], "mathtext.fallback": "stixsans", "svg.fonttype": "path", "axes.spines.top": False,
                     "mathtext.fontset": "custom", "mathtext.rm": "Roboto", "mathtext.it": "Roboto",
                     "mathtext.bf": "Roboto:bold",
                     "axes.spines.right": False, "axes.linewidth": 1.0})

CONTROL_GRAY = "#BDBDBD"
PALETTES = {
    "Fishlab": ["#077b7b", "#c7692a", "#7DAEB4", "#3E5C76", "#B8A04A", "#8C5E8F", "#5E8C61"],
    "Tons de cinza (estilo Prism)": ["#7F7F7F", "#4D4D4D", "#262626", "#A6A6A6", "#000000", "#D9D9D9"],
    "Okabe-Ito (amigável a daltônicos)": ["#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7", "#56B4E9",
                                          "#F0E442"],
    "Azuis": ["#9ECAE1", "#6BAED6", "#3182BD", "#08519C", "#08306B", "#C6DBEF"],
    "Viridis": [matplotlib.colors.to_hex(c) for c in plt.get_cmap("viridis")(np.linspace(0.15, 0.9, 6))],
}
HEAT_CMAP = LinearSegmentedColormap.from_list("fishlab_div", ["#2166AC", "#92C5DE", "#D9D9D9", "#F4A582", "#B2182B"])

BAR_DEFAULTS = {
    "erro": "SEM", "pontos": True, "largura": 0.65, "contorno_cor": "#000000", "contorno_esp": 1.0,
    "preenchimento": "Cheio", "paleta": "Fishlab", "controle_cinza": True, "sig": "Asteriscos",
    "ncols": 3, "fonte": 11, "ylabel": "Relative expression ($2^{-ΔΔCt}$)", "linha_1": True,
    "letras_paineis": True, "tamanho_ponto": 28, "titulo_italico": True,
}


def _colors(order, control, opts):
    pal = PALETTES.get(opts["paleta"], PALETTES["Fishlab"])
    out, k = {}, 0
    for g in order:
        if g == control and opts["controle_cinza"]:
            out[g] = CONTROL_GRAY
        else:
            out[g] = pal[k % len(pal)]
            k += 1
    return out


def _pvals_vs_control(result, control):
    p = {}
    if result and "pares" in result:
        for _, r in result["pares"].iterrows():
            if r["Grupo 1"] == control:
                p[r["Grupo 2"]] = r["p ajustado"]
            elif r["Grupo 2"] == control:
                p[r["Grupo 1"]] = r["p ajustado"]
    return p


def bar_figure(res, panels, order, control, results, labels=None, opts=None):
    """panels: lista de (gene, nível do fator 2 ou ""). results: {(gene, nível): resultado de stats.analyze}.
    labels: {grupo: rótulo a mostrar no eixo}."""
    o = {**BAR_DEFAULTS, **(opts or {})}
    labels = labels or {}
    n = len(panels)
    ncols = max(1, min(int(o["ncols"]), n))
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(3.1 * ncols, 3.0 * nrows), squeeze=False)
    plt.rcParams["font.size"] = o["fonte"]
    colors = _colors(order, control, o)
    for idx, (gene, lvl) in enumerate(panels):
        ax = axes[idx // ncols][idx % ncols]
        sub = res[(res["Gene"] == gene) & ((res.get("Fator 2", "") == lvl) if lvl else True)]
        sub = sub.dropna(subset=["Fold change"])
        grp = [g for g in order if (sub["Grupo"] == g).any()]
        x = np.arange(len(grp))
        means, errs = [], []
        for g in grp:
            v = sub.loc[sub["Grupo"] == g, "Fold change"].to_numpy(float)
            means.append(v.mean())
            sd = v.std(ddof=1) if len(v) > 1 else 0.0
            errs.append(sd / np.sqrt(len(v)) if o["erro"] == "SEM" else sd)
        filled = o["preenchimento"] == "Cheio"
        ax.bar(x, means, width=o["largura"], color=[colors[g] if filled else "white" for g in grp],
               edgecolor=[o["contorno_cor"] if filled else colors[g] for g in grp],
               linewidth=o["contorno_esp"] if filled else max(1.5, o["contorno_esp"]), zorder=2)
        ax.errorbar(x, means, yerr=errs, fmt="none", ecolor="black", elinewidth=1.1, capsize=4, capthick=1.1,
                    zorder=3)
        if o["pontos"]:
            rng = np.random.default_rng(0)
            for i, g in enumerate(grp):
                v = sub.loc[sub["Grupo"] == g, "Fold change"].to_numpy(float)
                jit = rng.uniform(-o["largura"] * 0.18, o["largura"] * 0.18, len(v))
                ax.scatter(x[i] + jit, v, s=o["tamanho_ponto"], facecolor="white", edgecolor="black",
                           linewidth=0.9, zorder=4)
        top = max([m + e for m, e in zip(means, errs)] + [sub["Fold change"].max() if len(sub) else 1])
        step = top * 0.08
        r = results.get((gene, lvl)) if results else None
        if r and "pares" in r and o["sig"] != "Nenhuma":
            if o["sig"] == "Letras":
                from .stats import letters
                L = letters([g for g in grp if g in r["ordem"]], dict(zip(grp, means)), r["pares"])
                for i, g in enumerate(grp):
                    if g in L:
                        ax.text(x[i], means[i] + errs[i] + step * 0.5, L[g], ha="center", va="bottom",
                                fontsize=o["fonte"], fontweight="bold")
            else:
                pv = r["pares"]
                vs_ctrl = (pv["Grupo 1"] == control).all()
                if vs_ctrl:
                    pc = _pvals_vs_control(r, control)
                    for i, g in enumerate(grp):
                        s = stars(pc.get(g)) if g in pc else ""
                        if s and s != "ns":
                            ax.text(x[i], means[i] + errs[i] + step * 0.4, s, ha="center", va="bottom",
                                    fontsize=o["fonte"] + 1, fontweight="bold")
                else:
                    level = top + step
                    for _, row in pv[pv["p ajustado"] < 0.05].iterrows():
                        if row["Grupo 1"] not in grp or row["Grupo 2"] not in grp:
                            continue
                        a, b = sorted((grp.index(row["Grupo 1"]), grp.index(row["Grupo 2"])))
                        ax.plot([a, a, b, b], [level, level + step * 0.3, level + step * 0.3, level], color="black",
                                linewidth=1)
                        ax.text((a + b) / 2, level + step * 0.32, stars(row["p ajustado"]), ha="center",
                                va="bottom", fontsize=o["fonte"])
                        level += step * 1.6
                    top = max(top, level)
        if o["linha_1"]:
            ax.axhline(1, color="#555555", linestyle=(0, (3, 3)), linewidth=0.8, zorder=1)
        ax.set_xticks(x)
        ax.set_xticklabels([labels.get(g, g) for g in grp], rotation=0 if len(grp) <= 4 else 35,
                           ha="center" if len(grp) <= 4 else "right")
        ax.set_ylim(0, top * 1.25 + step)
        title = gene if not lvl else f"{gene} – {lvl}"
        ax.set_title(title, fontstyle="italic" if o["titulo_italico"] else "normal", fontsize=o["fonte"] + 1,
                     fontweight="bold")
        if idx % ncols == 0:
            ax.set_ylabel(o["ylabel"])
        if o["letras_paineis"] and n > 1:
            ax.text(-0.22, 1.08, "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[idx], transform=ax.transAxes, fontsize=o["fonte"] + 3,
                    fontweight="bold", va="bottom")
    for j in range(n, nrows * ncols):
        axes[j // ncols][j % ncols].axis("off")
    fig.tight_layout()
    return fig


HEAT_DEFAULTS = {"limite_log2": float(np.log2(3)), "asteriscos": True, "valores": False, "incluir_controle": True,
                 "rotulo_barra": "Relative mRNA expression\n$2^{-ΔΔCt}$ (fold change)", "fonte": 10}


def heatmap_figure(summary, genes, order, levels, control, pvals, labels=None, opts=None):
    """summary: colunas Gene, Grupo, (Fator 2), Fold change médio. pvals: {(gene, nível, grupo): p vs controle}.
    Linhas = grupos (agrupados por nível do 2º fator), colunas = genes."""
    o = {**HEAT_DEFAULTS, **(opts or {})}
    labels = labels or {}
    levels = levels or [""]
    rows = []
    for lvl in levels:
        for g in order:
            if g == control and not o["incluir_controle"]:
                continue
            rows.append((lvl, g))
    M = np.full((len(rows), len(genes)), np.nan)
    has_f2 = "Fator 2" in summary
    for i, (lvl, g) in enumerate(rows):
        for j, gene in enumerate(genes):
            q = summary[(summary["Gene"] == gene) & (summary["Grupo"] == g)]
            if has_f2 and lvl:
                q = q[q["Fator 2"] == lvl]
            if len(q):
                M[i, j] = np.log2(q["Fold change médio"].iloc[0])
    lim = float(o["limite_log2"])
    fig_h = 0.42 * len(rows) + 1.6
    fig_w = 0.55 * len(genes) + 3.4
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    plt.rcParams["font.size"] = o["fonte"]
    norm = TwoSlopeNorm(vmin=-lim, vcenter=0, vmax=lim)
    im = ax.imshow(np.clip(M, -lim, lim), cmap=HEAT_CMAP, norm=norm, aspect="auto")
    ax.set_xticks(np.arange(len(genes)))
    ax.set_xticklabels(genes, rotation=45, ha="left", fontstyle="italic", fontweight="bold")
    ax.xaxis.tick_top()
    ax.set_yticks(np.arange(len(rows)))
    ax.set_yticklabels([labels.get(g, g) for _, g in rows], fontweight="bold")
    ax.set_xticks(np.arange(-0.5, len(genes)), minor=True)
    ax.set_yticks(np.arange(-0.5, len(rows)), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.5)
    ax.tick_params(which="minor", length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    # separadores e rótulos dos níveis do 2º fator
    if len(levels) > 1 or levels[0]:
        start = 0
        for lvl in levels:
            n_l = sum(1 for r in rows if r[0] == lvl)
            ax.add_patch(plt.Rectangle((-0.5, start - 0.5), len(genes), n_l, fill=False, edgecolor="black",
                                       linewidth=1.8, clip_on=False, zorder=6))
            ax.text(-0.5 - 0.06 * len(genes) - 1.4, start + n_l / 2 - 0.5, lvl, ha="right", va="center",
                    fontweight="bold", fontsize=o["fonte"] + 1)
            start += n_l
    for i, (lvl, g) in enumerate(rows):
        for j, gene in enumerate(genes):
            if np.isnan(M[i, j]):
                ax.text(j, i, "–", ha="center", va="center", color="#777777")
                continue
            txt = ""
            if o["valores"]:
                txt = f"{2 ** M[i, j]:.2f}"
            if o["asteriscos"] and g != control:
                s = stars(pvals.get((gene, lvl, g)))
                if s and s != "ns":
                    txt = f"{txt}\n{s}" if txt else s
            if txt:
                ax.text(j, i, txt, ha="center", va="center", fontsize=o["fonte"] - 1, fontweight="bold",
                        color="white" if abs(M[i, j]) > lim * 0.6 else "black")
    ticks = [t for t in (-3, -2, -1, 0, 1, 2, 3) if abs(t) <= lim + 1e-9]
    if lim not in ticks:
        ticks = sorted(set(ticks + [-lim, lim]))
    cb = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.03, ticks=ticks)
    cb.ax.set_yticklabels([f"{2 ** t:.2f}".rstrip("0").rstrip(".") for t in ticks])
    cb.set_label(o["rotulo_barra"], fontweight="bold")
    fig.tight_layout()
    return fig


def to_bytes(fig, fmt="png", dpi=300) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format=fmt, dpi=dpi, bbox_inches="tight", facecolor="white")
    return buf.getvalue()

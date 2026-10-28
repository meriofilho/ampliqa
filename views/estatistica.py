import math

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from ampliqa import analysis, figures, stats, ui
from ampliqa.i18n import t, tval

ui.header(t("Estatística e figuras"),
          t("Comparação entre grupos, recomendação do teste, outliers, gráfico de barras e heatmap"))
exp = st.session_state.exp
scfg = exp.setdefault("stats_cfg", {})
s = {**analysis.STATS_DEFAULTS, **scfg}

# ------------------------------------------------------------------ configuração
with st.container(border=True):
    st.markdown(t("**Como analisar**"))
    c1, c2, c3 = st.columns(3)
    met_labels = list(stats.METRICS)
    met_idx = [stats.METRICS[k] for k in met_labels].index(s["metrica"]) if s["metrica"] in stats.METRICS.values() else 0
    s["metrica"] = stats.METRICS[c1.selectbox(t("Escala dos testes"), met_labels, index=met_idx, format_func=t,
                                              help=t("O padrão (ΔCt) segue Yuan et al. 2006 e Rieu & Powers 2009: o "
                                                     "fold change deve estar em escala log para os testes. ΔCt e "
                                                     "log2FC dão exatamente os mesmos p-valores."))]
    comp = c2.radio(t("Pergunta"), ["controle", "todos"], index=0 if s["comparacao"] == "controle" else 1,
                    format_func=lambda v: t("Cada grupo contra o controle") if v == "controle"
                    else t("Todos os grupos entre si"))
    s["comparacao"] = comp
    s["erro"] = c3.radio(t("Barras de erro (gráfico e legenda)"), ["SEM", "DP"], index=0 if s["erro"] == "SEM" else 1,
                         horizontal=True, format_func=t)
    if s["metrica"] == "Fold change":
        st.warning(t("Testar o fold change (2^−ΔΔCt) diretamente é comum em trabalhos antigos, mas o fold change é "
                     "assimétrico (reduções ficam entre 0 e 1, aumentos de 1 ao infinito). A literatura recomenda a "
                     "escala log (ΔCt ou log2FC). Use esta opção só para comparar com análises anteriores."))
    with st.expander(t("Escolher o teste manualmente (o padrão é automático, conforme as premissas)")):
        c1, c2 = st.columns(2)
        s["teste"] = c1.selectbox(t("Teste"), analysis.TESTS, index=analysis.TESTS.index(s["teste"]), format_func=tval)
        s["posthoc"] = c2.selectbox("Post hoc", analysis.POSTHOCS, index=analysis.POSTHOCS.index(s["posthoc"]),
                                    format_func=tval)
        st.caption(t("Dunnett: cada grupo × controle. Tukey: todos os pares (variâncias iguais). Games-Howell: todos "
                     "os pares com variâncias diferentes. Dunn (Holm): não paramétrico."))
scfg.update(s)

an = analysis.run(exp, s)
if not an["ok"]:
    st.info(t(an["motivo"]))
    ui.footer()
    st.stop()

two_levels = len(an["levels"]) > 1
if two_levels:
    with st.container(border=True):
        st.markdown(t("**Segundo fator detectado** ({lv})", lv=", ".join(an["levels"])))
        modo = st.radio(t("Como analisar o 2º fator"), ["por nível", "duas vias"],
                        index=0 if s["modo_fator2"] == "por nível" else 1,
                        format_func=lambda v: t("Por nível: compara os grupos dentro de cada nível (ex.: em cada "
                                                "idade)") if v == "por nível"
                        else t("Também ANOVA de duas vias (tratamento × 2º fator, com interação)"))
        s["modo_fator2"] = modo
        scfg.update(s)
        if s["modo_fator2"] == "duas vias":
            st.info(t(stats.TWO_WAY_NOTE))
            an = analysis.run(exp, s)

# rótulos dos grupos
with st.expander(t("Nomes dos grupos nos gráficos e textos (ex.: A → Controle)")):
    cols = st.columns(min(4, len(an["order"])))
    labs = dict(an["labels"])
    for i, g in enumerate(an["order"]):
        labs[g] = cols[i % len(cols)].text_input(t("Grupo {g}", g=g), value=labs.get(g, g), key=f"lab_{g}")
    s["rotulos"] = analysis.labels_to({k: v for k, v in labs.items() if v and v != k})
    scfg.update(s)
    an["labels"] = analysis.labels_from(s["rotulos"])

t1, t2, t3 = st.tabs([t("📊 Resultados estatísticos"), t("📈 Gráfico de barras"), "🟥 Heatmap"])

# ------------------------------------------------------------------ resultados
with t1:
    st.markdown(t("Gene(s) de referência: **{ref}** · controle: **{c}** · n por grupo: **{n}** · escala: **{m}**",
                  ref=" + ".join(an["ref"]), c=an["control"], n=an["n_txt"], m=s["metrica"]))
    ov = analysis.overview(an)
    if "p" in ov:
        ov = ov.assign(p=ov["p"].map(lambda p: stats.fmt_p(p, None)))
    st.dataframe(ui.fmt(ov), use_container_width=True, hide_index=True)
    if an["two_way"]:
        st.markdown(t("**ANOVA de duas vias** (escala ΔCt/log2FC)"))
        for gene, tab in an["two_way"].items():
            with st.expander(f"{gene}"):
                if isinstance(tab, str):
                    st.error(tab)
                else:
                    tab = tab.assign(p=tab["p"].map(lambda p: stats.fmt_p(p, None) if pd.notna(p) else ""))
                    st.dataframe(ui.fmt(tab, {"SQ": 3, "F": 2}), hide_index=True, use_container_width=True)
    st.markdown(t("**Detalhes por gene** – premissas, por que o teste foi escolhido, comparações e outliers"))
    for (gene, lvl), a in an["analyses"].items():
        titulo = f"{gene}" + (f" – {lvl}" if lvl else "")
        om = a.get("omnibus")
        badge = f" · {stats.fmt_p(om['p'], None)} {stats.stars(om['p'])}" if om else ""
        with st.expander(titulo + badge):
            for av in a.get("avisos", []):
                st.warning(tval(av))
            if "erro" in a:
                st.error(tval(a["erro"]))
                continue
            st.markdown(f"**{t('Teste usado')}:** {tval(a['teste'])}"
                        + (f" + {tval(a['posthoc'])}" if a["posthoc"] != "—" else ""))
            for m in a["recomendação"]["motivos"]:
                st.markdown(f"- {m}")
            if a["teste"] != a["recomendação"]["teste"] or (a["posthoc"] != a["recomendação"]["posthoc"]):
                st.info(t("Recomendação automática era: {a} + {b}.", a=tval(a["recomendação"]["teste"]),
                          b=tval(a["recomendação"]["posthoc"])))
            d1 = om["df1"]
            d2 = om["df2"]
            gl = f"({d1:.0f}{', ' + (f'{d2:.0f}' if float(d2).is_integer() else f'{d2:.1f}') if d2 is not None else ''})" \
                if d1 is not None else ""
            st.markdown(f"**{om['estatística']}{gl} = {ui.br(om['valor'], 2)}**, {stats.fmt_p(om['p'], None)}")
            pares = a["pares"].assign(**{"p ajustado": a["pares"]["p ajustado"].map(lambda p: stats.fmt_p(p, None))})
            st.dataframe(ui.fmt(pares, {"Diferença": 3}), hide_index=True, use_container_width=True)
            if len(a["outliers"]):
                st.markdown(t("**Outliers (Grubbs, α = 0,05)**"))
                st.dataframe(ui.fmt(a["outliers"], {"G": 3, "G crítico": 3, "valor": 3}), hide_index=True,
                             use_container_width=True)
                if (a["outliers"]["Outlier?"] == "Sim").any():
                    st.warning(t("Possível outlier detectado.") + " " + t(stats.OUTLIER_GUIDE))
                else:
                    st.caption(t(stats.OUTLIER_GUIDE))

# ------------------------------------------------------------------ barras
with t2:
    o = dict(figures.BAR_DEFAULTS)
    o.update({k[4:]: v for k, v in scfg.items() if k.startswith("bar_")})
    c1, c2, c3, c4 = st.columns(4)
    saved = analysis.saved_list(scfg.get("fig_genes_barras"), an["genes"], an["genes"][:6])
    genes_sel = c1.multiselect("Genes", an["genes"], default=saved)
    lvls_sel = (c2.multiselect(t("Níveis do 2º fator"), an["levels"],
                               default=analysis.saved_list(scfg.get("fig_niveis"), an["levels"], an["levels"]))
                if two_levels else [""])
    scfg["fig_genes_barras"], scfg["fig_niveis"] = ";".join(genes_sel), ";".join(lvls_sel)
    o["sig"] = c3.radio(t("Significância"), ["Asteriscos", "Letras", "Nenhuma"],
                        index=["Asteriscos", "Letras", "Nenhuma"].index(o["sig"]), format_func=t)
    o["erro"] = s["erro"]
    o["ncols"] = c4.number_input(t("Painéis por linha"), 1, 6, int(o["ncols"]))
    with st.expander(t("🎨 Personalizar aparência")):
        c1, c2, c3, c4 = st.columns(4)
        o["paleta"] = c1.selectbox(t("Paleta de cores"), list(figures.PALETTES),
                                   index=list(figures.PALETTES).index(o["paleta"]))
        o["controle_cinza"] = c1.checkbox(t("Controle em cinza"), o["controle_cinza"])
        o["preenchimento"] = c2.radio(t("Barras"), ["Cheio", "Vazio"], index=["Cheio", "Vazio"].index(o["preenchimento"]),
                                      horizontal=True, format_func=t)
        o["largura"] = c2.slider(t("Largura das barras"), 0.3, 0.95, float(o["largura"]), 0.05)
        o["contorno_esp"] = c3.slider(t("Espessura do contorno"), 0.0, 3.0, float(o["contorno_esp"]), 0.25)
        o["contorno_cor"] = c3.color_picker(t("Cor do contorno"), o["contorno_cor"])
        o["pontos"] = c4.checkbox(t("Mostrar pontos (cada amostra)"), o["pontos"])
        o["linha_1"] = c4.checkbox(t("Linha de referência em 1"), o["linha_1"])
        o["letras_paineis"] = c4.checkbox(t("Letras nos painéis (A, B, C…)"), o["letras_paineis"])
        c1, c2 = st.columns([1, 3])
        o["fonte"] = c1.number_input(t("Tamanho da fonte"), 7, 18, int(o["fonte"]))
        o["ylabel"] = c2.text_input(t("Título do eixo Y"), o["ylabel"])
    scfg.update({f"bar_{k}": v for k, v in o.items()})
    panels = [(g, lv) for g in genes_sel for lv in lvls_sel]
    if panels:
        fig = figures.bar_figure(an["res"], panels, an["order"], an["control"], an["analyses"], an["labels"], o)
        st.image(figures.to_bytes(fig, "png", 160), use_container_width=True)
        c1, c2 = st.columns(2)
        c1.download_button("⬇️ PNG 300 dpi", figures.to_bytes(fig, "png", 300), "expressao_barras.png", "image/png")
        c2.download_button(t("⬇️ SVG (editável)"), figures.to_bytes(fig, "svg"), "expressao_barras.svg",
                           "image/svg+xml")
        plt.close(fig)
        sig_txt = {"Asteriscos": t("Asteriscos: comparação com o controle (ou colchetes entre pares, na opção 'todos "
                                   "os grupos'). "),
                   "Letras": t("Letras: grupos com a mesma letra não diferem. "), "Nenhuma": ""}[o["sig"]]
        st.caption(t("Barras: média ± {e}. ", e=t("erro padrão (SEM)") if o["erro"] == "SEM" else t("desvio padrão"))
                   + sig_txt + t("* p < 0,05; ** p < 0,01; *** p < 0,001; **** p < 0,0001."))
    else:
        st.info(t("Escolha ao menos um gene."))

# ------------------------------------------------------------------ heatmap
with t3:
    h = dict(figures.HEAT_DEFAULTS)
    h.update({k[5:]: v for k, v in scfg.items() if k.startswith("heat_")})
    c1, c2, c3 = st.columns(3)
    genes_h = c1.multiselect(t("Genes (colunas)"), an["genes"], key="heat_genes",
                             default=analysis.saved_list(scfg.get("fig_genes_heatmap"), an["genes"], an["genes"]))
    scfg["fig_genes_heatmap"] = ";".join(genes_h)
    lim_fc = c2.select_slider(t("Limite da escala (fold change)"), options=[1.5, 2.0, 3.0, 4.0, 8.0],
                              value=min([1.5, 2.0, 3.0, 4.0, 8.0], key=lambda v: abs(v - 2 ** h["limite_log2"])))
    h["limite_log2"] = math.log2(lim_fc)
    h["asteriscos"] = c3.checkbox(t("Asteriscos (vs controle)"), h["asteriscos"])
    h["valores"] = c3.checkbox(t("Mostrar valores de fold change"), h["valores"])
    h["incluir_controle"] = c3.checkbox(t("Incluir linha do controle"), h["incluir_controle"])
    scfg.update({f"heat_{k}": v for k, v in h.items()})
    if genes_h:
        fig = figures.heatmap_figure(an["summary"], genes_h, an["order"], an["levels"] if two_levels else [""],
                                     an["control"], an["pvals"], an["labels"], h)
        st.image(figures.to_bytes(fig, "png", 160), width=min(1100, 140 + 90 * len(genes_h)))
        c1, c2 = st.columns(2)
        c1.download_button("⬇️ PNG 300 dpi", figures.to_bytes(fig, "png", 300), "expressao_heatmap.png", "image/png")
        c2.download_button(t("⬇️ SVG (editável)"), figures.to_bytes(fig, "svg"), "expressao_heatmap.svg",
                           "image/svg+xml")
        plt.close(fig)
        st.caption(t("Cinza = expressão igual à do controle (fold change 1). Azul = menor expressão (down). Vermelho = "
                     "maior expressão (up). Cores em escala log2, limitadas a {lim}× para cima e para baixo; "
                     "asteriscos = comparação com o controle pelo teste escolhido.", lim=f"{lim_fc:g}"))
ui.footer()

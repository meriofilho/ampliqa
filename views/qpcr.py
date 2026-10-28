import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ampliqa import analysis, design, experiment, importers, qpcr, quant, ui
from ampliqa.i18n import t, tval
from ampliqa.params import FISHLAB, QPCR_MIX

ui.header(t("qPCR – expressão gênica relativa"),
          t("PO.OPE.03BIOMOL · qPCR Green Master LowROX with UNG · QuantStudio 3"))
exp = st.session_state.exp
cfg = exp["qpcr_cfg"]
ver = st.session_state.get("editor_ver", 0)
GENE_COLORS = [FISHLAB["primaria"], FISHLAB["destaque"], FISHLAB["apoio"], "#3E5C76", "#B8A04A", "#8C5E8F",
               "#5E8C61", "#C94F4F", "#4F7CC9", "#9C7A5B"]

t1, t2, t3, t4 = st.tabs([t("1 · Planejar placa"), t("2 · Importar corrida"), t("3 · Grupos"), t("4 · Resultados")])

# ------------------------------------------------------------------ 1. placa
with t1:
    ui.step(t("Monte o mapa da placa e o mix de cada gene. Padrão do POP: amostras em duplicata e, no fim do bloco "
              "de cada gene, os brancos (1 poço cada)."))
    _q = quant.compute(exp["quant"], exp["quant_params"])
    codes_quant = [str(c) for c in _q.loc[_q["Situação"] != "", "Código"]]
    _d = design.plan(exp["meta"])
    if not codes_quant and _d["grupos"] and _d["por_grupo"]:
        codes_quant = design.sample_codes(_d["grupos"], _d["por_grupo"])
    c1, c2 = st.columns(2)
    genes_txt = c1.text_area(t("Genes (um por linha; o de referência primeiro)"),
                             value=cfg.get("genes_placa") or "actb1\ngene_alvo_1\ngene_alvo_2\ngene_alvo_3",
                             height=150)
    samples_txt = c2.text_area(t("Amostras (uma por linha)"),
                               value=cfg.get("amostras_placa") or "\n".join(codes_quant), height=150,
                               help=t("Já vem preenchido com as amostras da tela de Quantificação (ou do desenho do experimento, "
                                      "na tela Início)."))
    cfg["genes_placa"], cfg["amostras_placa"] = genes_txt, samples_txt
    genes = [g.strip() for g in genes_txt.splitlines() if g.strip()]
    samples = [s.strip() for s in samples_txt.splitlines() if s.strip()]
    c1, c2, c3 = st.columns(3)
    brancos = c1.multiselect(t("Brancos por gene"), ["NTC", "BcDNA", "NRT", "BRANCO"], default=["NTC", "BcDNA"])
    reps = c2.number_input(t("Réplicas técnicas"), 1, 3, 2)
    protocolo = c3.radio(t("Protocolo"), list(QPCR_MIX), format_func=t, horizontal=False)
    if genes and samples:
        plan, n_plates = qpcr.plan_plate(samples, genes, brancos, int(reps))
        per_gene = len(samples) * int(reps) + len(brancos)
        st.caption(t("{a} poços por gene × {b} genes = {c} poços → {d} placa(s) de 96.", a=per_gene, b=len(genes),
                     c=len(plan), d=n_plates))
        if n_plates > 1:
            st.warning(t("Os genes não cabem numa placa só. O POP recomenda manter todas as amostras de um gene na "
                         "mesma placa – confira a divisão abaixo."))
        cmap = {g: GENE_COLORS[i % len(GENE_COLORS)] for i, g in enumerate(genes)}
        for pl in range(1, n_plates + 1):
            sub = plan[plan["Placa"] == pl]
            grid = pd.DataFrame("", index=qpcr.ROWS, columns=[str(c) for c in range(1, 13)])
            colors = pd.DataFrame("", index=qpcr.ROWS, columns=grid.columns)
            for _, w in sub.iterrows():
                grid.loc[w["Linha"], str(w["Coluna"])] = w["Amostra"]
                colors.loc[w["Linha"], str(w["Coluna"])] = (f"background-color: {cmap[w['Gene']]}; color: white; "
                                                            "font-weight: 600; text-align: center")
            st.markdown(f"**{t('Placa')} {pl}** – " + " · ".join(
                f'<span style="color:{cmap[g]};font-weight:700">■ {g}</span>' for g in sub["Gene"].unique()),
                unsafe_allow_html=True)
            st.dataframe(grid.style.apply(lambda _: colors, axis=None), use_container_width=True)
        st.markdown(t("**Mix por gene** (+10% de margem)"))
        st.dataframe(ui.fmt(qpcr.mix_per_gene(plan, protocolo)), use_container_width=True, hide_index=True)
        st.caption(t("Ordem no mix: H2O → Pf → Pr → SYBR. Distribua o mix, depois o cDNA 1:2,5 (ponteira nova por "
                     "amostra), água no NTC e o BcDNA no último poço. Programa padrão do QuantStudio 3 com melting."))
    else:
        st.info(t("Informe os genes e as amostras para gerar o mapa da placa."))

# ------------------------------------------------------------------ 2. importar
with t2:
    ui.step(t("Carregue o(s) arquivo(s) de resultados. O app reconhece sozinho a exportação do <b>QuantStudio</b> "
              "(.xls, aba Results), do <b>Rotor-Gene Q</b> (.csv \"Excel Analysed Data Export\") e tabelas simples "
              "com as colunas Amostra, Gene e Ct. Pode enviar vários arquivos de uma vez (ex.: um por gene)."))

    def load_run(raw, known_groups=None):
        exp["qpcr_raw"] = raw.reset_index(drop=True)
        brancos_cfg = [b for b in str(cfg["brancos"]).split(";") if b.strip()]
        exp["qpcr_groups"] = qpcr.default_groups(raw["Amostra"], int(cfg["letras_grupo"]), brancos_cfg,
                                                 known_groups)
        genes_run = list(dict.fromkeys(raw["Gene"]))
        refs_ok = [r for r in qpcr.ref_list(cfg.get("ref")) if r in genes_run]
        cfg["ref"] = ";".join(refs_ok) if refs_ok else genes_run[0]
        grupos = list(dict.fromkeys(qpcr.sample_groups(exp["qpcr_groups"])["Grupo"]))
        cfg["controle"] = grupos[0] if grupos else ""
        cfg["ordem_grupos"] = ";".join(grupos)
        ui.bump_editors()

    ups = st.file_uploader(t("Arquivos de resultados"), type=["xls", "xlsx", "csv", "txt"],
                           accept_multiple_files=True)
    cache = st.session_state.setdefault("imports", {})
    current = []
    for up in ups or []:
        key = f"{up.name}|{up.size}"
        current.append(key)
        if key not in cache:
            try:
                r = importers.read_file(up.getvalue(), up.name)
                r["nome"] = up.name
                cache[key] = r
            except Exception as e:  # noqa: BLE001
                cache[key] = {"erro": str(e), "nome": up.name}
    for key in list(cache):
        if key not in current:
            del cache[key]

    prontos, pendentes = [], []
    for key in current:
        r = cache[key]
        if "erro" in r:
            st.error(t("**{nome}** – não consegui ler: {erro}", nome=r["nome"], erro=tval(r["erro"])))
            continue
        with st.container(border=True):
            st.markdown(t("**{nome}** · formato: **{fmt}**", nome=r["nome"], fmt=tval(r["formato"])))
            for a in r["avisos"]:
                st.caption("⚠️ " + tval(a))
            if r["formato"] != "Rotor-Gene Q":
                raw_f = r["raw"]
                st.caption(t("{n} poços · genes: {g} · {a} amostras", n=len(raw_f),
                             g=", ".join(dict.fromkeys(raw_f["Gene"])), a=raw_f["Amostra"].nunique()))
                prontos.append((r, raw_f))
                continue
            st.caption(t("O Rotor-Gene não exporta o nome do gene. Confira o gene de cada bloco de poços "
                         "(cada bloco termina nos brancos) e desmarque blocos que não devem entrar."))
            blk = st.data_editor(r["blocos"], key=f"blk_{key}", hide_index=True, use_container_width=True,
                                 disabled=["Bloco", "Poços", "Nomes no arquivo", "Amostras com código", "Observação"],
                                 column_config={c: st.column_config.Column(t(c)) for c in r["blocos"].columns
                                                if c not in ("Usar", "Gene")} |
                                               {"Usar": st.column_config.CheckboxColumn(t("Usar")),
                                                "Gene": st.column_config.TextColumn("Gene")})
            sample_list, reps = None, 2
            usados = blk[blk["Usar"]]
            if len(usados) and not usados["Amostras com código"].all():
                b0 = usados.loc[~usados["Amostras com código"], "Bloco"].iloc[0]
                pw = r["poços"]
                n_nb = int((~pw.loc[pw["Bloco"] == b0, "Branco"]).sum())
                c1, c2 = st.columns([3, 1])
                sample_txt = c1.text_area(
                    t("Amostras na ordem dos poços (uma por linha) – vale para todos os blocos sem código"),
                    key=f"smp_{key}", height=140, placeholder=t("ex.: A1\nA2\nA3\nB1\n…"),
                    help=t("Os nomes dos poços deste arquivo não trazem o código da amostra. Informe as amostras na "
                           "ordem em que foram pipetadas."))
                reps = c2.number_input(t("Réplicas por amostra"), 1, 4, 2, key=f"rep_{key}")
                sample_list = [x for x in sample_txt.splitlines() if x.strip()]
                c2.caption(t("{n} poços de amostra por bloco → {a} amostras", n=n_nb, a=n_nb // max(1, int(reps))))
                if not sample_list:
                    st.warning(t("Sem a lista, as amostras ficam como S1, S2, S3… e os grupos não serão "
                                 "reconhecidos. Preencha a lista acima."))
            if (blk["Usar"] & (blk["Gene"].fillna("").astype(str).str.strip() == "")).any():
                st.warning(t("Há bloco marcado sem gene – informe o gene ou desmarque."))
                pendentes.append(r["nome"])
            raw_f = importers.build_rotorgene_raw(r["poços"], blk, sample_list, int(reps),
                                                  arquivo=r["nome"] if len(current) > 1 else "")
            prontos.append((r, raw_f))

    c1, c2 = st.columns(2)
    if prontos and c1.button(t("✅ Usar estes dados na análise"), type="primary", disabled=bool(pendentes)):
        multi = len(prontos) > 1
        raws, known = [], []
        for r, raw_f in prontos:
            raw_f = raw_f.copy()
            if multi and r["formato"] != "Rotor-Gene Q":
                raw_f["Poço"] = r["nome"] + "#" + raw_f["Poço"].astype(str)
            raws.append(raw_f)
            if r.get("grupos") is not None:
                known.append(r["grupos"])
        load_run(pd.concat(raws, ignore_index=True), pd.concat(known) if known else None)
        st.rerun()
    if c2.button(t("Usar uma corrida de exemplo (dados fictícios)")):
        from ampliqa import examples
        load_run(examples.qpcr_long())
        cfg["ref"] = examples.REF
        exp.setdefault("stats_cfg", {})["rotulos"] = ";".join(f"{k}={v}" for k, v in examples.GROUPS.items())
        st.rerun()
    with st.expander(t("📄 Arquivos de exemplo – veja como deve ser o arquivo que você vai carregar")):
        from ampliqa import examples
        st.caption(t("Dados fictícios (3 grupos × 3 pools, genes actb1, bdnf, sox2 e cdnf). Baixe, abra para ver o "
                     "formato e carregue de volta aqui para testar."))
        for label, (fname, fn, mime) in examples.DOWNLOADS.items():
            st.download_button(f"⬇️ {t(label)}", fn(), fname, mime, key=f"ex_{fname}")
        st.caption(t("Dica para o Rotor-Gene: nomeie cada poço com o código da amostra (a1, a2…), termine o bloco de "
                     "cada gene com os brancos e coloque os genes no nome do arquivo, na ordem dos blocos – como no "
                     "exemplo \"actb1 bdnf sox2 cdnf - exemplo.csv\"."))

    raw = exp["qpcr_raw"]
    if len(raw):
        st.markdown("---")
        st.markdown(t("**Dados em uso na análise**"))
        c1, c2, c3 = st.columns(3)
        c1.metric(t("Poços"), len(raw))
        c2.metric("Genes", raw["Gene"].nunique())
        c3.metric(t("Amostras (com brancos)"), raw["Amostra"].nunique())
        st.markdown(t("Marque **Omitir** para tirar um poço da análise (ex.: réplica com problema) – registre o "
                      "motivo no seu caderno."))
        bkey, ekey = f"raw_base_{ver}", f"raw_ed_{ver}"
        if ekey not in st.session_state:
            st.session_state[bkey] = raw.copy()
        ed = st.data_editor(st.session_state[bkey], key=ekey, hide_index=True, use_container_width=True,
                            disabled=["Poço", "Amostra", "Gene", "Ct"], height=380,
                            column_config={"Poço": st.column_config.TextColumn(t("Poço")),
                                           "Amostra": st.column_config.TextColumn(t("Amostra")),
                                           "Ct": st.column_config.NumberColumn("Ct", format="%.3f"),
                                           "Omitir": st.column_config.CheckboxColumn(t("Omitir"))})
        exp["qpcr_raw"] = ed.reset_index(drop=True)
    else:
        st.info(t("Nenhuma corrida em uso ainda."))

# ------------------------------------------------------------------ 3. grupos
with t3:
    raw = exp["qpcr_raw"]
    if not len(raw):
        st.info(t("Carregue primeiro a corrida na aba 2."))
    else:
        ui.step(t("Confira os grupos. Por padrão, o grupo é a 1ª letra do código (A1, A2, A3 = grupo A). "
                  "Edite a coluna Grupo à vontade e marque <b>Branco</b> nos poços de branco que o app não "
                  "reconheceu pelo nome (ex.: \"B\"). Se o experimento tem um <b>segundo fator</b> (ex.: idade 15, 45 "
                  "e 90 dpf), preencha a coluna <b>Fator 2</b>: cada nível será normalizado pelo seu próprio "
                  "controle."))
        genes_run = list(dict.fromkeys(raw["Gene"]))
        refs_now = [r for r in qpcr.ref_list(cfg.get("ref")) if r in genes_run] or genes_run[:1]
        refs_sel = st.multiselect(t("Gene(s) de referência (1 a 5)"), genes_run, default=refs_now, max_selections=5,
                                  help=t("Com 2 ou mais, o app normaliza pela média geométrica das referências (qBase, "
                                         "Hellemans et al. 2007) e mostra a estabilidade de cada uma (geNorm M e "
                                         "CV)."))
        cfg["ref"] = ";".join(refs_sel or refs_now)
        with st.expander(t("⚙️ Eficiência dos primers e réplicas técnicas (opcional)")):
            st.caption(t("Deixe em branco para usar 100% (método 2^−ΔΔCt). Informe a eficiência da curva padrão "
                         "(PO.OPE.04BIOMOL, planilha-anexo) para corrigir o cálculo de cada gene (modelo do qBase). "
                         "Aceite: 90–110%."))
            effs = qpcr.eff_map(cfg.get("eficiencias"))
            eff_df = pd.DataFrame({"Gene": genes_run,
                                   "Eficiência (%)": [round((effs[g] - 1) * 100, 1) if g in effs else None
                                                      for g in genes_run]})
            eff_ed = st.data_editor(eff_df, key=f"eff_{ver}", hide_index=True, disabled=["Gene"],
                                    column_config={"Eficiência (%)": st.column_config.NumberColumn(
                                        t("Eficiência (%)"), min_value=50.0, max_value=150.0, step=0.1,
                                        format="%.1f")})
            cfg["eficiencias"] = ";".join(f"{g}={v}" for g, v in zip(eff_ed["Gene"], eff_ed["Eficiência (%)"])
                                          if pd.notna(v))
            fora = [g for g, v in zip(eff_ed["Gene"], eff_ed["Eficiência (%)"]) if pd.notna(v) and not 90 <= v <= 110]
            if fora:
                st.warning(t("Eficiência fora de 90–110%: {g}. Refaça a curva ou otimize o primer.",
                             g=", ".join(fora)))
            cfg["outlier_auto"] = st.checkbox(
                t("Remover réplicas técnicas discrepantes automaticamente (critério do Auto-qPCR)"),
                value=cfg.get("outlier_auto") in (True, "True"),
                help=t("Se o desvio padrão das réplicas de uma amostra passa de 0,3 ciclo, a réplica mais distante da "
                       "média é removida, até o DP ficar abaixo do limite, sem remover mais da metade e sempre "
                       "mantendo 2 réplicas (Maussion et al. 2021). Com duplicatas não há como saber qual réplica "
                       "está errada: nesse caso nada é removido e o alerta continua aparecendo."))
        c1, c2, c3 = st.columns(3)
        cfg["dup_max"] = c1.number_input(t("Dif. máx. entre réplicas (Ct)"), 0.1, 3.0, float(cfg["dup_max"]), 0.1)
        cfg["blank_lim"] = c2.number_input(t("Ct limite dos brancos"), 20.0, 45.0, float(cfg["blank_lim"]), 1.0)
        cfg["brancos"] = c3.text_input(t("Outros nomes de branco (separados por ;)"), value=cfg["brancos"],
                                       help=t("BRANCO, BRANCO1, NTC, BcDNA e NRT já são reconhecidos sozinhos."))
        c1, c2 = st.columns([1, 3])
        letras = c1.number_input(t("Letras do código = grupo"), 1, 5, int(cfg["letras_grupo"]))
        if c1.button(t("Refazer grupos pelas letras")):
            cfg["letras_grupo"] = int(letras)
            brancos_cfg = [b for b in str(cfg["brancos"]).split(";") if b.strip()]
            exp["qpcr_groups"] = qpcr.default_groups(raw["Amostra"], int(letras), brancos_cfg)
            grupos = list(dict.fromkeys(qpcr.sample_groups(exp["qpcr_groups"])["Grupo"]))
            cfg["controle"], cfg["ordem_grupos"] = (grupos[0] if grupos else ""), ";".join(grupos)
            ui.bump_editors()
            st.rerun()
        gkey_b, gkey_e = f"grp_base_{ver}", f"grp_ed_{ver}"
        if "Fator 2" not in exp["qpcr_groups"]:
            exp["qpcr_groups"].insert(2, "Fator 2", "")
        if gkey_e not in st.session_state:
            st.session_state[gkey_b] = exp["qpcr_groups"].copy()
        with c2:
            ged = st.data_editor(st.session_state[gkey_b], key=gkey_e, hide_index=True, use_container_width=True,
                                 disabled=["Amostra"], height=300,
                                 column_config={"Amostra": st.column_config.TextColumn(t("Amostra")),
                                                "Grupo": st.column_config.TextColumn(t("Grupo")),
                                                "Branco": st.column_config.CheckboxColumn(t("Branco")),
                                                "Fator 2": st.column_config.TextColumn(t("Fator 2 (opcional)"),
                                                                                       help=t("ex.: 15 dpf"))})
        exp["qpcr_groups"] = ged.reset_index(drop=True)
        grupos = list(dict.fromkeys(qpcr.sample_groups(exp["qpcr_groups"])["Grupo"].astype(str)))
        if not grupos:
            st.warning(t("Nenhum grupo definido."))
        else:
            c1, c2 = st.columns(2)
            cfg["controle"] = c1.selectbox(t("Grupo controle (calibrador)"), grupos,
                                           index=grupos.index(cfg["controle"]) if cfg.get("controle") in grupos else 0)
            ordem_atual = [g for g in str(cfg.get("ordem_grupos", "")).split(";") if g in grupos]
            ordem = c2.multiselect(t("Ordem dos grupos nos gráficos"), grupos,
                                   default=ordem_atual + [g for g in grupos if g not in ordem_atual])
            cfg["ordem_grupos"] = ";".join(ordem + [g for g in grupos if g not in ordem])

# ------------------------------------------------------------------ 4. resultados
with t4:
    raw = exp["qpcr_raw"]
    if not len(raw) or not len(qpcr.sample_groups(exp["qpcr_groups"])):
        st.info(t("Carregue a corrida (aba 2) e confira os grupos (aba 3)."))
    else:
        tabs = experiment.results_tables(exp)
        res, resumo, bl, fl = tabs["qpcr"], tabs["qpcr_resumo"], tabs["qpcr_brancos"], tabs["qpcr_alertas"]
        ordem = [g for g in str(cfg["ordem_grupos"]).split(";") if g]
        refs = qpcr.ref_list(cfg["ref"])

        n_bad_bl = int(bl["Situação"].str.startswith("ATENÇÃO").sum())
        c1, c2, c3 = st.columns(3)
        c1.metric(t("Brancos com alerta"), n_bad_bl)
        c2.metric(t("Alertas de réplicas"), len(fl))
        c3.metric(t("Referência / controle"), f"{' + '.join(refs)} / {cfg['controle']}")

        with st.expander(t("🧪 Brancos ({n} com alerta)", n=n_bad_bl), expanded=n_bad_bl > 0):
            st.dataframe(ui.fmt(bl, {"Menor Ct": 2}, status=["Situação"]), use_container_width=True, hide_index=True)
        with st.expander(t("⚠️ Réplicas e amplificação ({n} alertas)", n=len(fl)), expanded=False):
            if len(fl):
                st.dataframe(ui.fmt(fl, status=["Alerta"]), use_container_width=True, hide_index=True)
                st.caption(t("Para excluir um poço discrepante, marque Omitir na aba 2 e registre a justificativa."))
            else:
                st.success(t("Nenhum alerta: todas as réplicas dentro do limite."))
        out = tabs.get("qpcr_outliers")
        if out is not None:
            with st.expander(t("🧹 Réplicas removidas automaticamente ({n})", n=len(out))):
                if len(out):
                    st.dataframe(ui.fmt(out, {"Ct": 3}), use_container_width=True, hide_index=True)
                    st.caption(t("Critério do Auto-qPCR (DP > 0,3 ciclo). Registre a remoção no caderno."))
                else:
                    st.success(t("Nenhuma réplica precisou ser removida."))
        est = tabs.get("qpcr_estabilidade")
        if est is not None and len(est):
            ruins = int((est["Avaliação"] != "Estável").sum())
            with st.expander(t("⚖️ Estabilidade dos genes de referência ({n} com ressalva)", n=ruins),
                             expanded=ruins > 0):
                st.dataframe(ui.fmt(est, {"M (geNorm)": 2, "CV (%)": 1}, status=["Avaliação"]),
                             use_container_width=True, hide_index=True)
                st.caption(t("geNorm M e CV dos NRQ (Hellemans et al. 2007). Referências estáveis: M < 0,5 e CV < 25% "
                             "(amostras homogêneas); até M < 1 e CV < 50% em amostras heterogêneas."))
        elif len(refs) == 1:
            st.caption(t("💡 Com 2 ou mais genes de referência (aba Grupos), o app avalia a estabilidade de cada um "
                         "(geNorm M e CV) e normaliza pela média geométrica (recomendação MIQE)."))

        ui.step(t("<b>Fold change médio ± desvio padrão por grupo</b> (pontos = cada amostra)"))
        genes_plot = [g for g in dict.fromkeys(res["Gene"]) if g not in refs]
        cols = st.columns(2)
        for i, gene in enumerate(genes_plot):
            sub = resumo[resumo["Gene"] == gene]
            pts = res[(res["Gene"] == gene) & res["Fold change"].notna()]
            fig = go.Figure()
            fig.add_bar(x=sub["Grupo"], y=sub["Fold change médio"], marker_color=FISHLAB["primaria"],
                        error_y=dict(type="data", array=sub["Desvio padrão"].fillna(0), color="#333", thickness=1.4),
                        name=t("Média"), hovertemplate="%{x}: %{y:.2f}<extra></extra>")
            fig.add_scatter(x=pts["Grupo"], y=pts["Fold change"], mode="markers", name=t("Amostras"),
                            marker=dict(color=FISHLAB["destaque"], size=7, line=dict(color="white", width=1)),
                            text=pts["Amostra"], hovertemplate="%{text}: %{y:.2f}<extra></extra>")
            fig.add_hline(y=1, line_dash="dot", line_color="#888")
            fig.update_layout(title=gene, height=330, margin=dict(l=10, r=10, t=40, b=10), showlegend=False,
                              plot_bgcolor="white", paper_bgcolor="white", font=dict(family="Aptos, sans-serif"),
                              yaxis_title="Fold change (NRQ)",
                              xaxis=dict(categoryorder="array", categoryarray=ordem))
            cols[i % 2].plotly_chart(fig, use_container_width=True)

        st.markdown(t("**Resumo por grupo**"))
        st.dataframe(ui.fmt(resumo, {"Fold change médio": 3, "Desvio padrão": 3, "Erro padrão": 3, "log2FC médio": 3}),
                     use_container_width=True, hide_index=True)
        with st.expander(t("Resultados por amostra (ΔCt, ΔΔCt, fold change)")):
            cols_show = ["Amostra", "Grupo", "Gene", "Réplicas com Ct", "Ct médio", "Diferença entre réplicas",
                         "Ct referência", "ΔCt", "ΔΔCt", "Fold change", "log2 fold change"]
            st.dataframe(ui.fmt(res[cols_show], {"Ct médio": 2, "Diferença entre réplicas": 2, "Ct referência": 2,
                                                 "ΔCt": 3, "ΔΔCt": 3, "Fold change": 3, "log2 fold change": 3}),
                         use_container_width=True, hide_index=True)
        an = analysis.run(exp)
        if an.get("ok"):
            c1, c2 = st.columns(2)
            c1.download_button(t("📊 Tabelas para o GraphPad Prism (fold change)"),
                               analysis.prism_xlsx(an, "Fold change"), "prism_fold_change.xlsx",
                               use_container_width=True)
            c2.download_button(t("📊 Tabelas para o GraphPad Prism (log2 fold change)"),
                               analysis.prism_xlsx(an, "log2 fold change"), "prism_log2_fold_change.xlsx",
                               use_container_width=True)
        st.caption(t("Para estatística, use ΔCt ou log2 fold change por amostra. Sem eficiência informada, o cálculo "
                     "assume 100% (2^−ΔΔCt), válido para primers com eficiência de 90–110% (PO.OPE.04BIOMOL). Todos "
                     "estes resultados vão junto no arquivo do experimento."))
ui.footer()

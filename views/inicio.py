import streamlit as st

from ampliqa import design, experiment, ui
from ampliqa.i18n import is_en, t

ui.header("AmpliQA", t("Planejamento e análise de experimentos de expressão gênica – quantificação de RNA, "
                      "cDNA e qPCR"))
st.caption(t("Um projeto do [Dalmolin Systems Biology Group]({dg}) e do [Fish Lab – Laboratório de Peixes]({fl}), "
           "Universidade Federal do Rio Grande do Norte (UFRN).", dg=ui.URL_DG, fl=ui.URL_FL))

exp = st.session_state.exp

st.markdown(t("**Como funciona:** cada experimento fica num **arquivo do experimento** (.xlsx) que é só seu. Você "
              "trabalha aqui, clica em **💾 Salvar arquivo do experimento** (barra lateral) e guarda o arquivo no seu "
              "Google Drive. Para continuar outro dia, é só carregar o arquivo de novo nesta tela. Nada fica guardado "
              "no servidor."))

c1, c2 = st.columns([3, 2], gap="large")
with c1:
    st.subheader(t("Novo experimento"))
    meta = exp["meta"]
    d = design.plan(meta)
    v = st.session_state.get("editor_ver", 0)
    label = (lambda x: design.LABELS_EN.get(x, x)) if is_en() else (lambda x: x)
    with st.container(border=True):
        nome = st.text_input(t("Nome do experimento"), value=meta.get("Experimento", ""), key=f"nm_{v}",
                             placeholder=t("ex.: Fipronil larvas 96 hpf"))
        resp = st.text_input(t("Seu nome"), value=meta.get("Responsável", ""), key=f"rs_{v}")
        ca = cb = st.container()
        sp_opts = list(design.SPECIES) + [design.OUTRA]
        sp_idx = sp_opts.index(d["especie"]) if d["especie"] in sp_opts else (len(sp_opts) - 1 if d["especie"] else 0)
        sp = ca.selectbox(t("Espécie / modelo"), sp_opts, index=sp_idx, format_func=label, key=f"sp_{v}")
        if sp == design.OUTRA:
            sp = ca.text_input(t("Qual espécie ou modelo?"), key=f"spx_{v}",
                               value="" if d["especie"] in design.SPECIES else d["especie"]).strip()
        ti_opts = design.tissues_for(sp)
        ti_idx = ti_opts.index(d["tecido"]) if d["tecido"] in ti_opts else (len(ti_opts) - 1 if d["tecido"] else 0)
        ti = cb.selectbox(t("Tecido / tipo de amostra"), ti_opts, index=ti_idx, format_func=label,
                          key=f"ti_{v}_{sp if sp in design.SPECIES else 'outra'}",
                          help=t("A lista muda conforme a espécie escolhida."))
        if ti == design.OUTRO:
            ti = cb.text_input(t("Qual tecido ou tipo de amostra?"), key=f"tix_{v}",
                               value="" if d["tecido"] in design.TISSUES else d["tecido"]).strip()
        c_g = c_n = c_p = st.container()
        n_grupos = c_g.number_input(t("Nº de grupos"), 1, 26, d["grupos"] or 3, key=f"ng_{v}",
                                    help=t("Inclua o grupo controle."))
        n_amostras = c_n.number_input(t("Amostras por grupo"), 1, 50, d["por_grupo"] or 3, key=f"na_{v}",
                                      help=t("Réplicas biológicas de cada grupo: pools ou indivíduos."))
        n_pool = c_p.number_input(t("Indivíduos por pool"), 1, 200, d["por_pool"] or 1, key=f"np_{v}",
                                  help=t("Quantos indivíduos foram juntados em cada amostra. Use 1 se não houver pool."))
        codes = design.sample_codes(n_grupos, n_amostras)
        st.caption(t("{n} amostras no total ({g} grupos × {k}), com códigos de {a} a {b}. A 1ª letra é o grupo.",
                     n=len(codes), g=int(n_grupos), k=int(n_amostras), a=codes[0], b=codes[-1]))
        obs = st.text_area(t("Observações"), value=meta.get("Observações", ""), height=80, key=f"ob_{v}")
        novo = st.button(t("Começar / atualizar dados"), type="primary")
    if novo:
        if not nome or not resp:
            st.warning(t("Preencha o nome do experimento e o seu nome."))
        else:
            meta.pop("Espécie / tecido", None)
            meta.update({"Experimento": nome, "Responsável": resp, "Espécie": sp, "Tecido": ti,
                         "Grupos": int(n_grupos), "Amostras por grupo": int(n_amostras),
                         "Indivíduos por pool": int(n_pool), "Observações": obs})
            exp.setdefault("methods_cfg", {}).update(design.methods_from(meta))
            st.success(t("Pronto! Siga para **Quantificação → cDNA** no menu ao lado."))

with c2:
    st.subheader(t("Continuar um experimento"))
    up = st.file_uploader(t("Carregue o arquivo do experimento (.xlsx) salvo no seu Drive"), type=["xlsx"])
    if up is not None and st.session_state.get("ultimo_arquivo") != (up.name, up.size):
        try:
            st.session_state.exp = experiment.from_xlsx(up.getvalue())
            st.session_state.ultimo_arquivo = (up.name, up.size)
            ui.bump_editors()
            st.success(t("Experimento **{nome}** carregado.", nome=st.session_state.exp["meta"].get("Experimento")))
            st.rerun()
        except Exception as e:  # noqa: BLE001
            st.error(t("Não consegui abrir o arquivo: {e}", e=e))
    with st.container(border=True):
        st.markdown(t("""**Etapas disponíveis**
0. **Planejamento**: cronograma das etapas, mensagem para WhatsApp e eventos para o Google Agenda.
1. **Quantificação → cDNA**: leituras do NanoDrop (digitadas ou do arquivo), qualidade, volumes para 500 ng e lista de pipetagem (mix → água → RNA) – PO.OPE.01 e 02BIOMOL.
2. **qPCR**: mapa de placa e mix por gene, importação do QuantStudio ou Rotor-Gene, 1 a 5 genes de referência, eficiência por gene, estabilidade das referências e alertas – PO.OPE.03 e 04BIOMOL.
3. **Estatística e figuras**: teste recomendado e explicado, outliers, gráfico de barras, heatmap e tabelas para o GraphPad Prism.
4. **Métodos e resultados**: rascunho em inglês e português com os seus números.
5. **Central de ajuda**: diagnóstico do experimento e soluções para problemas comuns."""))
    st.markdown(t("**Primeira vez? Experimente com dados de exemplo**"))
    st.caption(t("Experimento fictício: larvas de zebrafish em 3 grupos (Controle, Dose baixa, Dose alta), 3 pools por "
                 "grupo, gene de referência actb1 e 3 genes-alvo – bdnf diminui, sox2 aumenta e cdnf não muda. Todas "
                 "as telas ficam preenchidas para você explorar."))
    from ampliqa import examples
    c1, c2 = st.columns(2)
    if c1.button(t("▶️ Carregar o experimento de exemplo"), type="primary"):
        st.session_state.exp = examples.experiment_example()
        ui.bump_editors()
        st.rerun()
    c2.download_button(t("📄 Baixar o arquivo de exemplo"), examples.file_experiment(),
                       "exemplo_experimento_ampliqa.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       help=t("Veja como é um arquivo do experimento salvo pelo app (pode abrir no Excel)."))

ui.footer()

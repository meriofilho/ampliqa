from pathlib import Path

import streamlit as st

from ampliqa import experiment, ui
from ampliqa.i18n import t

c_logo, c_head = st.columns([1, 6], vertical_alignment="center")
c_logo.image(str(Path(__file__).resolve().parent.parent / "assets" / "fishlab_logo.png"), width=110)
with c_head:
    ui.header("Ampliqa", t("Planejamento e análise de experimentos de expressão gênica – quantificação de RNA, "
                                  "cDNA e qPCR"))
    st.caption(t("Um projeto do [Dalmolin Systems Biology Group]({dg}) e do [Fish Lab – Laboratório de Peixes]({fl}), "
                 "Universidade Federal do Rio Grande do Norte (UFRN).", dg="https://dalmolingroup.imd.ufrn.br/", fl="https://www.fishlabufrn.com/"))

exp = st.session_state.exp

st.markdown(t("**Como funciona:** cada experimento fica num **arquivo do experimento** (.xlsx) que é só seu. Você "
              "trabalha aqui, clica em **💾 Salvar arquivo do experimento** (barra lateral) e guarda o arquivo no seu "
              "Google Drive. Para continuar outro dia, é só carregar o arquivo de novo nesta tela. Nada fica guardado "
              "no servidor."))

c1, c2 = st.columns(2, gap="large")
with c1:
    st.subheader(t("Novo experimento"))
    with st.form("novo"):
        nome = st.text_input(t("Nome do experimento"), value=exp["meta"].get("Experimento", ""),
                             placeholder=t("ex.: Fipronil larvas 96 hpf"))
        resp = st.text_input(t("Seu nome"), value=exp["meta"].get("Responsável", ""))
        esp = st.text_input(t("Espécie / tecido"), value=exp["meta"].get("Espécie / tecido", ""),
                            placeholder=t("ex.: zebrafish – larvas (pool de 10)"))
        obs = st.text_area(t("Observações"), value=exp["meta"].get("Observações", ""), height=80)
        novo = st.form_submit_button(t("Começar / atualizar dados"), type="primary")
    if novo:
        if not nome or not resp:
            st.warning(t("Preencha o nome do experimento e o seu nome."))
        else:
            exp["meta"].update({"Experimento": nome, "Responsável": resp, "Espécie / tecido": esp,
                                "Observações": obs})
            st.success(t("Pronto! Siga para **Quantificação → cDNA** no menu ao lado."))
            st.rerun()

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

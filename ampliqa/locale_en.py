"""English translations of the interface. Key = Portuguese text exactly as written in the code.

To translate a new string: wrap it with t("...") in the code and add the same text here as a key.
tests/test_i18n.py lists any t("...") call without a translation.
"""
import re

EN = {
    # ---------------------------------------------------------------- navigation and shared
    "Início": "Home", "Bancada": "Bench", "Análise": "Analysis", "Ajuda": "Help",
    "Quantificação → cDNA": "Quantification → cDNA", "Estatística e figuras": "Statistics and figures",
    "Métodos e resultados": "Methods and results", "Central de ajuda": "Help center",
    "Experimento": "Experiment", "Responsável": "Researcher", "— sem nome —": "— unnamed —",
    "💾 Salvar arquivo do experimento": "💾 Save experiment file",
    "Salve sempre que terminar uma etapa e guarde o arquivo no seu Google Drive.":
        "Save whenever you finish a step and keep the file in your Google Drive.",
    "Ajuda rápida": "Quick help", "O que deu errado?": "What went wrong?",
    "ex.: branco amplificou": "e.g. blank amplified",
    "⚠️ {n} ponto(s) de atenção no seu experimento – veja a Central de ajuda.":
        "⚠️ {n} issue(s) found in your experiment – see the Help center.",
    "Nada encontrado. Tente outras palavras ou abra a Central de ajuda.":
        "Nothing found. Try other words or open the Help center.",
    "AmpliQA · código aberto (licença MIT) · desenvolvido por Romério de Oliveira Lima Filho, doutorando em "
    "Bioinformática no {dg}, em parceria com o {fl} (UFRN). Segue os POPs de Biologia Molecular (PO.OPE.01 a "
    "04BIOMOL).":
        "AmpliQA · open source (MIT license) · developed by Romério de Oliveira Lima Filho, PhD student in "
        "Bioinformatics at the {dg}, in partnership with the {fl} (UFRN). Follows the Molecular Biology SOPs "
        "(PO.OPE.01 to 04BIOMOL).",
    "Um projeto de": "A project of",
    "Um projeto do [Dalmolin Systems Biology Group]({dg}) e do [Fish Lab – Laboratório de Peixes]({fl}), "
    "Universidade Federal do Rio Grande do Norte (UFRN).":
        "A project of the [Dalmolin Systems Biology Group]({dg}) and the [Fish Lab – Laboratório de Peixes]({fl}), "
        "Federal University of Rio Grande do Norte (UFRN), Brazil.",

    # ---------------------------------------------------------------- home
    "Planejamento e análise de experimentos de expressão gênica – quantificação de RNA, cDNA e qPCR":
        "Planning and analysis of gene-expression experiments – RNA quantification, cDNA and qPCR",
    "**Como funciona:** cada experimento fica num **arquivo do experimento** (.xlsx) que é só seu. Você trabalha "
    "aqui, clica em **💾 Salvar arquivo do experimento** (barra lateral) e guarda o arquivo no seu Google Drive. Para "
    "continuar outro dia, é só carregar o arquivo de novo nesta tela. Nada fica guardado no servidor.":
        "**How it works:** each experiment lives in an **experiment file** (.xlsx) that belongs only to you. Work "
        "here, click **💾 Save experiment file** (sidebar) and keep the file in your Google Drive. To continue "
        "another day, load the file again on this screen. Nothing is stored on the server.",
    "Novo experimento": "New experiment", "Continuar um experimento": "Continue an experiment",
    "Espécie / modelo": "Species / model", "Qual espécie ou modelo?": "Which species or model?",
    "Tecido / tipo de amostra": "Tissue / sample type", "A lista muda conforme a espécie escolhida.":
        "The list changes with the chosen species.",
    "Qual tecido ou tipo de amostra?": "Which tissue or sample type?", "Nº de grupos": "Number of groups",
    "Inclua o grupo controle.": "Include the control group.", "Amostras por grupo": "Samples per group",
    "Réplicas biológicas de cada grupo: pools ou indivíduos.": "Biological replicates in each group: pools or individuals.",
    "Indivíduos por pool": "Individuals per pool",
    "Quantos indivíduos foram juntados em cada amostra. Use 1 se não houver pool.":
        "How many individuals were pooled in each sample. Use 1 if there is no pooling.",
    "{n} amostras no total ({g} grupos × {k}), com códigos de {a} a {b}. A 1ª letra é o grupo.":
        "{n} samples in total ({g} groups × {k}), coded {a} to {b}. The 1st letter is the group.",
    "Use 1 se cada amostra é um único indivíduo (sem pool).": "Use 1 if each sample is a single individual (no pooling).",
    "Espécie (texto em inglês)": "Species (English text)", "Espécie (texto em português)": "Species (Portuguese text)",
    "Já vem preenchido com as amostras da tela de Quantificação (ou do desenho do experimento, na tela Início).":
        "Pre-filled with the samples from the Quantification screen (or from the experiment design on the Home "
        "screen).",
    "Nome do experimento": "Experiment name", "Seu nome": "Your name", "Espécie / tecido": "Species / tissue",
    "Observações": "Notes", "Começar / atualizar dados": "Start / update details",
    "ex.: Fipronil larvas 96 hpf": "e.g. Fipronil larvae 96 hpf",
    "ex.: zebrafish – larvas (pool de 10)": "e.g. zebrafish – larvae (pool of 10)",
    "Preencha o nome do experimento e o seu nome.": "Fill in the experiment name and your name.",
    "Pronto! Siga para **Quantificação → cDNA** no menu ao lado.":
        "Done! Go to **Quantification → cDNA** in the side menu.",
    "Carregue o arquivo do experimento (.xlsx) salvo no seu Drive":
        "Load the experiment file (.xlsx) saved in your Drive",
    "Experimento **{nome}** carregado.": "Experiment **{nome}** loaded.",
    "Não consegui abrir o arquivo: {e}": "Could not open the file: {e}",
    "**Etapas disponíveis**\n0. **Planejamento**: cronograma das etapas, mensagem para WhatsApp e eventos para o "
    "Google Agenda.\n1. **Quantificação → cDNA**: leituras do NanoDrop (digitadas ou do arquivo), qualidade, "
    "volumes para 500 ng e lista de pipetagem (mix → água → RNA) – PO.OPE.01 e 02BIOMOL.\n2. **qPCR**: mapa de placa e "
    "mix por gene, importação do QuantStudio ou Rotor-Gene, 1 a 5 genes de referência, eficiência por gene, "
    "estabilidade das referências e alertas – PO.OPE.03 e 04BIOMOL.\n3. **Estatística e figuras**: teste recomendado "
    "e explicado, outliers, gráfico de barras, heatmap e tabelas para o GraphPad Prism.\n4. **Métodos e resultados**: "
    "rascunho em inglês e português com os seus números.\n5. **Central de ajuda**: diagnóstico do experimento e "
    "soluções para problemas comuns.":
        "**Available steps**\n0. **Planning**: step schedule, WhatsApp message and Google Calendar events.\n"
        "1. **Quantification → cDNA**: NanoDrop readings (typed or from file), quality, volumes "
        "for 500 ng and pipetting list (mix → water → RNA) – PO.OPE.01 and 02BIOMOL.\n2. **qPCR**: plate map and "
        "per-gene mix, QuantStudio or Rotor-Gene import, 1–5 reference genes, per-gene efficiency, reference "
        "stability and alerts – PO.OPE.03 and 04BIOMOL.\n3. **Statistics and figures**: recommended and explained "
        "test, outliers, bar chart, heatmap and GraphPad Prism tables.\n4. **Methods and results**: draft in English "
        "and Portuguese with your numbers.\n5. **Help center**: experiment diagnosis and fixes for common problems.",
    "**Primeira vez? Experimente com dados de exemplo**": "**First time? Try it with example data**",
    "Experimento fictício: larvas de zebrafish em 3 grupos (Controle, Dose baixa, Dose alta), 3 pools por grupo, gene "
    "de referência actb1 e 3 genes-alvo – bdnf diminui, sox2 aumenta e cdnf não muda. Todas as telas ficam "
    "preenchidas para você explorar.":
        "Fictitious experiment: zebrafish larvae in 3 groups (Control, Low dose, High dose), 3 pools per group, "
        "reference gene actb1 and 3 target genes – bdnf goes down, sox2 goes up and cdnf does not change. Every "
        "screen is filled in for you to explore.",
    "▶️ Carregar o experimento de exemplo": "▶️ Load the example experiment",
    "📄 Baixar o arquivo de exemplo": "📄 Download the example file",
    "Veja como é um arquivo do experimento salvo pelo app (pode abrir no Excel).":
        "See what an experiment file saved by the app looks like (it opens in Excel).",

    # ---------------------------------------------------------------- quantification → cDNA
    "Quantificação de RNA → síntese de cDNA": "RNA quantification → cDNA synthesis",
    "PO.OPE.01BIOMOL e PO.OPE.02BIOMOL · NZY First-Strand, 20 µL, 500 ng de RNA":
        "PO.OPE.01BIOMOL and PO.OPE.02BIOMOL · NZY First-Strand, 20 µL, 500 ng RNA",
    "⚙️ Parâmetros (padrão do POP – altere só se o protocolo mudar)":
        "⚙️ Parameters (SOP defaults – change only if the protocol changes)",
    "Massa de RNA por reação (ng)": "RNA mass per reaction (ng)", "Volume RNA + H2O (µL)": "RNA + H2O volume (µL)",
    "Master Mix por reação (µL)": "Master Mix per reaction (µL)", "Enzyme Mix por reação (µL)": "Enzyme Mix per reaction (µL)",
    "A260/280 mínimo": "A260/280 minimum", "A260/280 máximo": "A260/280 maximum",
    "A260/230 mínimo (aceite)": "A260/230 minimum (accept)", "A260/230 mínimo (ressalva)": "A260/230 minimum (with caveat)",
    "Volume mínimo pipetável (µL)": "Minimum pipetting volume (µL)", "Margem do mix (fração)": "Mix margin (fraction)",
    "Brancos do cDNA (BcDNA)": "cDNA blanks (BcDNA)", "Controles sem RT (NRT)": "No-RT controls (NRT)",
    "Concentração mínima de RNA = {c} ng/µL ({m} ng em {v} µL).": "Minimum RNA concentration = {c} ng/µL ({m} ng in {v} µL).",
    "📥 Importar as leituras direto do arquivo do NanoDrop (versão provisória)":
        "📥 Import readings directly from the NanoDrop file (provisional)",
    "Exporte as leituras no software do NanoDrop 2000 e carregue o arquivo. Leituras repetidas da mesma amostra viram "
    "Leitura 1 e Leitura 2. (Formato ainda será confirmado com arquivos reais.)":
        "Export the readings from the NanoDrop 2000 software and load the file. Repeated readings of the same sample "
        "become Reading 1 and Reading 2. (Format still to be confirmed with real files.)",
    "⬇️ Arquivo de exemplo do NanoDrop (fictício)": "⬇️ Example NanoDrop file (fictitious)",
    "Arquivo do NanoDrop": "NanoDrop file", "{n} amostras importadas do NanoDrop.": "{n} samples imported from NanoDrop.",
    "Não consegui ler o arquivo do NanoDrop: {e}": "Could not read the NanoDrop file: {e}",
    "<b>1. Digite as leituras do NanoDrop</b> – uma amostra por linha. Se fez só uma leitura, deixe a Leitura 2 em "
    "branco. Use o <b>+</b> no fim da tabela para acrescentar linhas.":
        "<b>1. Enter the NanoDrop readings</b> – one sample per row. If you made a single reading, leave Reading 2 "
        "empty. Use the <b>+</b> at the end of the table to add rows.",
    "ex.: A1, A2, B1…": "e.g. A1, A2, B1…",
    "Digite ao menos uma amostra com código e concentração para ver os cálculos.":
        "Enter at least one sample with code and concentration to see the calculations.",
    "<b>2. Confira a qualidade e a situação de cada amostra</b>": "<b>2. Check the quality and status of each sample</b>",
    "<b>3. Prepare o mix comum</b> (amostras prontas + brancos, com margem de pipetagem)":
        "<b>3. Prepare the common mix</b> (ready samples + blanks, with pipetting margin)",
    "Reações": "Reactions", "{a} amostras + {b} branco(s)": "{a} samples + {b} blank(s)",
    "Mix comum por tubo": "Common mix per tube",
    "Total de mix comum: {v} µL ({r} reações com margem). O NRT, se feito, não leva Enzyme Mix: prepare à parte.":
        "Total common mix: {v} µL ({r} reactions with margin). The NRT, if done, has no Enzyme Mix: prepare it "
        "separately.",
    "<b>4. Monte os tubos nesta ordem:</b> 1º mix comum (mesma ponteira, tubos vazios) → 2º água DEPC → 3º RNA "
    "(ponteira nova para cada amostra)":
        "<b>4. Fill the tubes in this order:</b> 1st common mix (same tip, empty tubes) → 2nd DEPC water → 3rd RNA "
        "(new tip for each sample)",
    "Programa do termociclador (Veriti – FISHLAB cDNA): 25 °C 10 min → 55 °C 20 min → 85 °C 5 min → 4 °C. Depois, "
    "diluir o cDNA 1:2,5 (10 µL + 15 µL de água) para 10 ng/µL de RNA-eq.":
        "Thermal cycler program (Veriti – FISHLAB cDNA): 25 °C 10 min → 55 °C 20 min → 85 °C 5 min → 4 °C. Then "
        "dilute the cDNA 1:2.5 (10 µL + 15 µL water) to 10 ng/µL RNA-eq.",

    # ---------------------------------------------------------------- qPCR
    "qPCR – expressão gênica relativa": "qPCR – relative gene expression",
    "PO.OPE.03BIOMOL · qPCR Green Master LowROX with UNG · QuantStudio 3":
        "PO.OPE.03BIOMOL · qPCR Green Master LowROX with UNG · QuantStudio 3",
    "1 · Planejar placa": "1 · Plan plate", "2 · Importar corrida": "2 · Import run", "3 · Grupos": "3 · Groups",
    "4 · Resultados": "4 · Results",
    "Monte o mapa da placa e o mix de cada gene. Padrão do POP: amostras em duplicata e, no fim do bloco de cada gene, "
    "os brancos (1 poço cada).":
        "Build the plate map and the mix for each gene. SOP default: samples in duplicate and, at the end of each "
        "gene block, the blanks (1 well each).",
    "Genes (um por linha; o de referência primeiro)": "Genes (one per line; reference first)",
    "Amostras (uma por linha)": "Samples (one per line)",
    "Já vem preenchido com as amostras da tela de Quantificação.": "Pre-filled with the samples from the Quantification screen.",
    "Brancos por gene": "Blanks per gene", "Réplicas técnicas": "Technical replicates", "Protocolo": "Protocol",
    "{a} poços por gene × {b} genes = {c} poços → {d} placa(s) de 96.":
        "{a} wells per gene × {b} genes = {c} wells → {d} 96-well plate(s).",
    "Os genes não cabem numa placa só. O POP recomenda manter todas as amostras de um gene na mesma placa – confira a "
    "divisão abaixo.":
        "The genes do not fit in a single plate. The SOP recommends keeping all samples of a gene on the same plate – "
        "check the split below.",
    "Placa": "Plate", "**Mix por gene** (+10% de margem)": "**Mix per gene** (+10% margin)",
    "Ordem no mix: H2O → Pf → Pr → SYBR. Distribua o mix, depois o cDNA 1:2,5 (ponteira nova por amostra), água no NTC "
    "e o BcDNA no último poço. Programa padrão do QuantStudio 3 com melting.":
        "Mix order: H2O → Fw → Rv → SYBR. Dispense the mix, then the 1:2.5 cDNA (new tip per sample), water in the "
        "NTC and the BcDNA in the last well. Standard QuantStudio 3 program with melt curve.",
    "Informe os genes e as amostras para gerar o mapa da placa.": "Enter the genes and samples to build the plate map.",
    "Carregue o(s) arquivo(s) de resultados. O app reconhece sozinho a exportação do <b>QuantStudio</b> (.xls, aba "
    "Results), do <b>Rotor-Gene Q</b> (.csv \"Excel Analysed Data Export\") e tabelas simples com as colunas Amostra, "
    "Gene e Ct. Pode enviar vários arquivos de uma vez (ex.: um por gene).":
        "Load the result file(s). The app recognizes the <b>QuantStudio</b> export (.xls, Results sheet), the "
        "<b>Rotor-Gene Q</b> export (.csv \"Excel Analysed Data Export\") and simple tables with Sample, Gene and Ct "
        "columns. You can send several files at once (e.g. one per gene).",
    "Arquivos de resultados": "Result files",
    "**{nome}** – não consegui ler: {erro}": "**{nome}** – could not read: {erro}",
    "**{nome}** · formato: **{fmt}**": "**{nome}** · format: **{fmt}**",
    "{n} poços · genes: {g} · {a} amostras": "{n} wells · genes: {g} · {a} samples",
    "O Rotor-Gene não exporta o nome do gene. Confira o gene de cada bloco de poços (cada bloco termina nos brancos) e "
    "desmarque blocos que não devem entrar.":
        "The Rotor-Gene does not export the gene name. Check the gene of each block of wells (each block ends at the "
        "blanks) and untick blocks that should be left out.",
    "Amostras na ordem dos poços (uma por linha) – vale para todos os blocos sem código":
        "Samples in well order (one per line) – applies to all blocks without codes",
    "ex.: A1\nA2\nA3\nB1\n…": "e.g. A1\nA2\nA3\nB1\n…",
    "Os nomes dos poços deste arquivo não trazem o código da amostra. Informe as amostras na ordem em que foram "
    "pipetadas.":
        "The well names in this file do not include the sample code. Enter the samples in the order they were "
        "pipetted.",
    "Réplicas por amostra": "Replicates per sample",
    "{n} poços de amostra por bloco → {a} amostras": "{n} sample wells per block → {a} samples",
    "Sem a lista, as amostras ficam como S1, S2, S3… e os grupos não serão reconhecidos. Preencha a lista acima.":
        "Without the list, samples are named S1, S2, S3… and groups will not be recognized. Fill in the list above.",
    "Há bloco marcado sem gene – informe o gene ou desmarque.": "A ticked block has no gene – enter the gene or untick it.",
    "✅ Usar estes dados na análise": "✅ Use this data in the analysis",
    "Usar uma corrida de exemplo (dados fictícios)": "Use an example run (fictitious data)",
    "📄 Arquivos de exemplo – veja como deve ser o arquivo que você vai carregar":
        "📄 Example files – see what the file you upload should look like",
    "Dados fictícios (3 grupos × 3 pools, genes actb1, bdnf, sox2 e cdnf). Baixe, abra para ver o formato e carregue "
    "de volta aqui para testar.":
        "Fictitious data (3 groups × 3 pools, genes actb1, bdnf, sox2 and cdnf). Download, open it to see the format "
        "and load it back here to test.",
    "Dica para o Rotor-Gene: nomeie cada poço com o código da amostra (a1, a2…), termine o bloco de cada gene com os "
    "brancos e coloque os genes no nome do arquivo, na ordem dos blocos – como no exemplo \"actb1 bdnf sox2 cdnf - "
    "exemplo.csv\".":
        "Rotor-Gene tip: name each well with the sample code (a1, a2…), end each gene block with the blanks and put "
        "the genes in the file name, in block order – as in the example \"actb1 bdnf sox2 cdnf - exemplo.csv\".",
    "**Dados em uso na análise**": "**Data used in the analysis**",
    "Amostras (com brancos)": "Samples (with blanks)",
    "Marque **Omitir** para tirar um poço da análise (ex.: réplica com problema) – registre o motivo no seu caderno.":
        "Tick **Omit** to leave a well out of the analysis (e.g. a faulty replicate) – record the reason in your "
        "lab notebook.",
    "Nenhuma corrida em uso ainda.": "No run loaded yet.",
    "Carregue primeiro a corrida na aba 2.": "Load the run in tab 2 first.",
    "Confira os grupos. Por padrão, o grupo é a 1ª letra do código (A1, A2, A3 = grupo A). Edite a coluna Grupo à "
    "vontade e marque <b>Branco</b> nos poços de branco que o app não reconheceu pelo nome (ex.: \"B\"). Se o "
    "experimento tem um <b>segundo fator</b> (ex.: idade 15, 45 e 90 dpf), preencha a coluna <b>Fator 2</b>: cada "
    "nível será normalizado pelo seu próprio controle.":
        "Check the groups. By default, the group is the 1st letter of the code (A1, A2, A3 = group A). Edit the "
        "Group column freely and tick <b>Blank</b> for blank wells the app did not recognize by name (e.g. \"B\"). "
        "If the experiment has a <b>second factor</b> (e.g. age 15, 45 and 90 dpf), fill in the <b>Factor 2</b> "
        "column: each level will be normalized to its own control.",
    "Gene(s) de referência (1 a 5)": "Reference gene(s) (1 to 5)",
    "Com 2 ou mais, o app normaliza pela média geométrica das referências (qBase, Hellemans et al. 2007) e mostra a "
    "estabilidade de cada uma (geNorm M e CV).":
        "With 2 or more, the app normalizes to the geometric mean of the references (qBase, Hellemans et al. 2007) "
        "and shows the stability of each one (geNorm M and CV).",
    "⚙️ Eficiência dos primers e réplicas técnicas (opcional)": "⚙️ Primer efficiency and technical replicates (optional)",
    "Deixe em branco para usar 100% (método 2^−ΔΔCt). Informe a eficiência da curva padrão (PO.OPE.04BIOMOL, "
    "planilha-anexo) para corrigir o cálculo de cada gene (modelo do qBase). Aceite: 90–110%.":
        "Leave empty to use 100% (2^−ΔΔCt method). Enter the standard-curve efficiency (PO.OPE.04BIOMOL annex "
        "spreadsheet) to correct the calculation of each gene (qBase model). Acceptance: 90–110%.",
    "Eficiência fora de 90–110%: {g}. Refaça a curva ou otimize o primer.":
        "Efficiency outside 90–110%: {g}. Repeat the curve or optimize the primer.",
    "Remover réplicas técnicas discrepantes automaticamente (critério do Auto-qPCR)":
        "Remove outlying technical replicates automatically (Auto-qPCR rule)",
    "Se o desvio padrão das réplicas de uma amostra passa de 0,3 ciclo, a réplica mais distante da média é removida, "
    "até o DP ficar abaixo do limite, sem remover mais da metade e sempre mantendo 2 réplicas (Maussion et al. 2021). "
    "Com duplicatas não há como saber qual réplica está errada: nesse caso nada é removido e o alerta continua "
    "aparecendo.":
        "If the SD of a sample's replicates exceeds 0.3 cycles, the replicate furthest from the mean is removed until "
        "the SD is below the limit, never removing more than half and always keeping 2 replicates (Maussion et al. "
        "2021). With duplicates there is no way to tell which replicate is wrong: nothing is removed and the alert "
        "remains.",
    "Dif. máx. entre réplicas (Ct)": "Max. difference between replicates (Ct)",
    "Ct limite dos brancos": "Blank Ct limit", "Outros nomes de branco (separados por ;)": "Other blank names (separated by ;)",
    "BRANCO, BRANCO1, NTC, BcDNA e NRT já são reconhecidos sozinhos.":
        "BRANCO, BRANCO1, NTC, BcDNA and NRT are recognized automatically.",
    "Letras do código = grupo": "Code letters = group", "Refazer grupos pelas letras": "Rebuild groups from letters",
    "Fator 2 (opcional)": "Factor 2 (optional)", "ex.: 15 dpf": "e.g. 15 dpf",
    "Nenhum grupo definido.": "No groups defined.",
    "Grupo controle (calibrador)": "Control group (calibrator)", "Ordem dos grupos nos gráficos": "Group order in charts",
    "Carregue a corrida (aba 2) e confira os grupos (aba 3).": "Load the run (tab 2) and check the groups (tab 3).",
    "Brancos com alerta": "Blanks with alerts", "Alertas de réplicas": "Replicate alerts",
    "Referência / controle": "Reference / control",
    "🧪 Brancos ({n} com alerta)": "🧪 Blanks ({n} with alerts)",
    "⚠️ Réplicas e amplificação ({n} alertas)": "⚠️ Replicates and amplification ({n} alerts)",
    "Para excluir um poço discrepante, marque Omitir na aba 2 e registre a justificativa.":
        "To exclude an outlying well, tick Omit in tab 2 and record the reason.",
    "Nenhum alerta: todas as réplicas dentro do limite.": "No alerts: all replicates within the limit.",
    "🧹 Réplicas removidas automaticamente ({n})": "🧹 Replicates removed automatically ({n})",
    "Critério do Auto-qPCR (DP > 0,3 ciclo). Registre a remoção no caderno.":
        "Auto-qPCR rule (SD > 0.3 cycles). Record the removal in your lab notebook.",
    "Nenhuma réplica precisou ser removida.": "No replicate needed to be removed.",
    "⚖️ Estabilidade dos genes de referência ({n} com ressalva)": "⚖️ Reference gene stability ({n} with caveats)",
    "geNorm M e CV dos NRQ (Hellemans et al. 2007). Referências estáveis: M < 0,5 e CV < 25% (amostras homogêneas); "
    "até M < 1 e CV < 50% em amostras heterogêneas.":
        "geNorm M and CV of the NRQs (Hellemans et al. 2007). Stable references: M < 0.5 and CV < 25% (homogeneous "
        "samples); up to M < 1 and CV < 50% in heterogeneous samples.",
    "💡 Com 2 ou mais genes de referência (aba Grupos), o app avalia a estabilidade de cada um (geNorm M e CV) e "
    "normaliza pela média geométrica (recomendação MIQE).":
        "💡 With 2 or more reference genes (Groups tab), the app evaluates the stability of each one (geNorm M and "
        "CV) and normalizes to their geometric mean (MIQE recommendation).",
    "<b>Fold change médio ± desvio padrão por grupo</b> (pontos = cada amostra)":
        "<b>Mean fold change ± SD per group</b> (dots = each sample)",
    "Média": "Mean", "Amostras": "Samples", "**Resumo por grupo**": "**Summary per group**",
    "Resultados por amostra (ΔCt, ΔΔCt, fold change)": "Results per sample (ΔCt, ΔΔCt, fold change)",
    "📊 Tabelas para o GraphPad Prism (fold change)": "📊 GraphPad Prism tables (fold change)",
    "📊 Tabelas para o GraphPad Prism (log2 fold change)": "📊 GraphPad Prism tables (log2 fold change)",
    "Para estatística, use ΔCt ou log2 fold change por amostra. Sem eficiência informada, o cálculo assume 100% "
    "(2^−ΔΔCt), válido para primers com eficiência de 90–110% (PO.OPE.04BIOMOL). Todos estes resultados vão junto no "
    "arquivo do experimento.":
        "For statistics, use ΔCt or log2 fold change per sample. Without efficiencies, the calculation assumes 100% "
        "(2^−ΔΔCt), valid for primers with 90–110% efficiency (PO.OPE.04BIOMOL). All these results are saved in the "
        "experiment file.",

    # ---------------------------------------------------------------- statistics screen
    "Comparação entre grupos, recomendação do teste, outliers, gráfico de barras e heatmap":
        "Group comparison, test recommendation, outliers, bar chart and heatmap",
    "**Como analisar**": "**How to analyse**", "Escala dos testes": "Test scale",
    "O padrão (ΔCt) segue Yuan et al. 2006 e Rieu & Powers 2009: o fold change deve estar em escala log para os testes. "
    "ΔCt e log2FC dão exatamente os mesmos p-valores.":
        "The default (ΔCt) follows Yuan et al. 2006 and Rieu & Powers 2009: fold change must be on a log scale for "
        "testing. ΔCt and log2FC give exactly the same p-values.",
    "Pergunta": "Question", "Cada grupo contra o controle": "Each group versus control",
    "Todos os grupos entre si": "All groups against each other",
    "Barras de erro (gráfico e legenda)": "Error bars (chart and legend)",
    "Testar o fold change (2^−ΔΔCt) diretamente é comum em trabalhos antigos, mas o fold change é assimétrico (reduções "
    "ficam entre 0 e 1, aumentos de 1 ao infinito). A literatura recomenda a escala log (ΔCt ou log2FC). Use esta "
    "opção só para comparar com análises anteriores.":
        "Testing fold change (2^−ΔΔCt) directly is common in older work, but fold change is asymmetric (decreases lie "
        "between 0 and 1, increases from 1 to infinity). The literature recommends the log scale (ΔCt or log2FC). "
        "Use this option only to compare with previous analyses.",
    "Escolher o teste manualmente (o padrão é automático, conforme as premissas)":
        "Choose the test manually (default is automatic, based on the assumptions)",
    "Teste": "Test",
    "Dunnett: cada grupo × controle. Tukey: todos os pares (variâncias iguais). Games-Howell: todos os pares com "
    "variâncias diferentes. Dunn (Holm): não paramétrico.":
        "Dunnett: each group × control. Tukey: all pairs (equal variances). Games-Howell: all pairs with unequal "
        "variances. Dunn (Holm): non-parametric.",
    "**Segundo fator detectado** ({lv})": "**Second factor detected** ({lv})",
    "Como analisar o 2º fator": "How to analyse the 2nd factor",
    "Por nível: compara os grupos dentro de cada nível (ex.: em cada idade)":
        "Per level: compares groups within each level (e.g. at each age)",
    "Também ANOVA de duas vias (tratamento × 2º fator, com interação)":
        "Also two-way ANOVA (treatment × 2nd factor, with interaction)",
    "Nomes dos grupos nos gráficos e textos (ex.: A → Controle)": "Group names in charts and texts (e.g. A → Control)",
    "Grupo {g}": "Group {g}",
    "📊 Resultados estatísticos": "📊 Statistical results", "📈 Gráfico de barras": "📈 Bar chart",
    "Gene(s) de referência: **{ref}** · controle: **{c}** · n por grupo: **{n}** · escala: **{m}**":
        "Reference gene(s): **{ref}** · control: **{c}** · n per group: **{n}** · scale: **{m}**",
    "**ANOVA de duas vias** (escala ΔCt/log2FC)": "**Two-way ANOVA** (ΔCt/log2FC scale)",
    "**Detalhes por gene** – premissas, por que o teste foi escolhido, comparações e outliers":
        "**Details per gene** – assumptions, why the test was chosen, comparisons and outliers",
    "Teste usado": "Test used", "Recomendação automática era: {a} + {b}.": "Automatic recommendation was: {a} + {b}.",
    "**Outliers (Grubbs, α = 0,05)**": "**Outliers (Grubbs, α = 0.05)**",
    "Possível outlier detectado.": "Possible outlier detected.",
    "Níveis do 2º fator": "2nd-factor levels", "Significância": "Significance", "Painéis por linha": "Panels per row",
    "🎨 Personalizar aparência": "🎨 Customize appearance", "Paleta de cores": "Color palette",
    "Controle em cinza": "Control in gray", "Barras": "Bars", "Largura das barras": "Bar width",
    "Espessura do contorno": "Outline width", "Cor do contorno": "Outline color",
    "Mostrar pontos (cada amostra)": "Show dots (each sample)", "Linha de referência em 1": "Reference line at 1",
    "Letras nos painéis (A, B, C…)": "Panel letters (A, B, C…)", "Tamanho da fonte": "Font size",
    "Título do eixo Y": "Y-axis title", "⬇️ SVG (editável)": "⬇️ SVG (editable)",
    "Barras: média ± {e}. ": "Bars: mean ± {e}. ", "erro padrão (SEM)": "standard error (SEM)",
    "desvio padrão": "standard deviation",
    "Asteriscos: comparação com o controle (ou colchetes entre pares, na opção 'todos os grupos'). ":
        "Asterisks: comparison with control (or brackets between pairs, with the 'all groups' option). ",
    "Letras: grupos com a mesma letra não diferem. ": "Letters: groups sharing a letter do not differ. ",
    "* p < 0,05; ** p < 0,01; *** p < 0,001; **** p < 0,0001.": "* p < 0.05; ** p < 0.01; *** p < 0.001; **** p < 0.0001.",
    "Escolha ao menos um gene.": "Choose at least one gene.",
    "Genes (colunas)": "Genes (columns)", "Limite da escala (fold change)": "Scale limit (fold change)",
    "Asteriscos (vs controle)": "Asterisks (vs control)", "Mostrar valores de fold change": "Show fold-change values",
    "Incluir linha do controle": "Include control row",
    "Cinza = expressão igual à do controle (fold change 1). Azul = menor expressão (down). Vermelho = maior expressão "
    "(up). Cores em escala log2, limitadas a {lim}× para cima e para baixo; asteriscos = comparação com o controle pelo "
    "teste escolhido.":
        "Gray = same expression as control (fold change 1). Blue = lower expression (down). Red = higher expression "
        "(up). Colors on a log2 scale, capped at {lim}× up and down; asterisks = comparison with control by the "
        "chosen test.",
    # options shown through format_func
    "ΔCt (recomendado – mesmos p-valores do log2FC)": "ΔCt (recommended – same p-values as log2FC)",
    "log2 fold change": "log2 fold change",
    "Fold change (2^−ΔΔCt) – como em análises antigas": "Fold change (2^−ΔΔCt) – as in older analyses",
    "SEM": "SEM", "DP": "SD", "Asteriscos": "Asterisks", "Letras": "Letters", "Nenhuma": "None",
    "Cheio": "Filled", "Vazio": "Empty",
    "Econômico (10 µL)": "Economy (10 µL)", "Padrão (20 µL)": "Standard (20 µL)",
    "QuantStudio (aba Results)": "QuantStudio (Results sheet)", "Rotor-Gene Q (.csv)": "Rotor-Gene Q (.csv)",
    "Tabela simples (Amostra, Gene, Ct)": "Simple table (Sample, Gene, Ct)",
    "Carregue a corrida e defina grupos, referência e controle na tela qPCR.":
        "Load the run and define groups, reference and control on the qPCR screen.",

    # ---------------------------------------------------------------- methods screen
    "Rascunho em inglês e português, preenchido com a sua análise – revise antes de usar":
        "Draft in English and Portuguese, filled in with your analysis – review before use",
    "Depois, confira a estatística na tela Estatística e figuras.": "Then check the statistics on the Statistics and figures screen.",
    "**1. Confirme o POP, os kits e os equipamentos usados** (o padrão segue os POPs atuais PO.OPE.01 a 04BIOMOL)":
        "**1. Confirm the SOP, kits and equipment used** (defaults follow the current SOPs PO.OPE.01 to 04BIOMOL)",
    "Espécie": "Species", "Tipo de amostra": "Sample type", "Animais por pool": "Animals per pool",
    "Exposição / tratamento (aparece entre parênteses)": "Exposure / treatment (shown in parentheses)",
    "Kits e equipamentos (padrão dos POPs)": "Kits and equipment (SOP defaults)",
    "Extração de RNA (PO.OPE.01)": "RNA extraction (PO.OPE.01)", "Quantificação": "Quantification",
    "Kit de cDNA (PO.OPE.02)": "cDNA kit (PO.OPE.02)", "RNA por reação de cDNA (ng)": "RNA per cDNA reaction (ng)",
    "Termociclador do cDNA": "cDNA thermal cycler", "Master mix da qPCR (PO.OPE.03)": "qPCR master mix (PO.OPE.03)",
    "Equipamento de qPCR": "qPCR instrument", "Volume da reação de qPCR (µL)": "qPCR reaction volume (µL)",
    "cDNA por poço (ng de RNA-eq)": "cDNA per well (ng RNA-eq)",
    "Concentração final de cada primer (µM)": "Final concentration of each primer (µM)",
    "Se o experimento usou outro protocolo (ex.: PureLink, High-Capacity, StepOne), troque aqui: o texto é atualizado "
    "na hora.":
        "If the experiment used another protocol (e.g. PureLink, High-Capacity, StepOne), change it here: the text "
        "updates immediately.",
    "Alguns genes não puderam ser analisados (veja a tela Estatística e figuras); eles ficam fora do texto.":
        "Some genes could not be analysed (see the Statistics and figures screen); they are left out of the text.",
    "Os nomes dos grupos vêm da tela Estatística e figuras (ex.: A → Control). Os valores de F, p e fold change são os "
    "da análise atual; os limites de significância são * p < 0,05; ** p < 0,01; *** p < 0,001; **** p < 0,0001. "
    "Confira sempre antes de usar no manuscrito.":
        "Group names come from the Statistics and figures screen (e.g. A → Control). F, p and fold-change values are "
        "those of the current analysis; significance thresholds are * p < 0.05; ** p < 0.01; *** p < 0.001; "
        "**** p < 0.0001. Always check before using them in a manuscript.",

    # ---------------------------------------------------------------- help center
    "Problemas comuns na bancada e na análise – como resolver e onde ler mais":
        "Common bench and analysis problems – how to fix them and where to read more",
    "🔎 Diagnóstico do seu experimento": "🔎 Diagnosis of your experiment",
    "Não foi possível analisar o experimento: {e}": "Could not analyse the experiment: {e}",
    "Nenhum ponto de atenção encontrado nos dados abertos (ou ainda não há dados).":
        "No issues found in the open data (or there is no data yet).",
    "Pontos encontrados nos dados que estão abertos agora, com a explicação e o que fazer.":
        "Issues found in the data currently open, with the explanation and what to do.",
    "💬 Pergunte": "💬 Ask", "Descreva o problema com suas palavras": "Describe the problem in your own words",
    "ex.: minhas réplicas deram diferentes": "e.g. my replicates differ",
    "Não encontrei uma resposta para isso. Tente outras palavras ou procure na lista abaixo.":
        "I could not find an answer for that. Try other words or browse the list below.",
    "📚 Todas as perguntas frequentes": "📚 All frequently asked questions",
    "📄 POPs do laboratório": "📄 Lab SOPs", "Pasta com todos os POPs e planilhas-anexo": "Folder with all SOPs and annex spreadsheets",
    "Os links abrem os PDFs na pasta do Fishlab no Google Drive (é preciso ter acesso à pasta).":
        "Links open the PDFs in the Fishlab Google Drive folder (folder access is required).",
    "🔗 Referências oficiais": "🔗 Key references",
    "Artigos de referência para qPCR e para os testes estatísticos usados no app. Clique no DOI para abrir o artigo. "
    "DOIs conferidos na Crossref.":
        "Reference papers for qPCR and for the statistical tests used in the app. Click the DOI to open the paper. "
        "DOIs checked on Crossref.",
    "Esta central não usa inteligência artificial: as respostas foram escritas a partir dos POPs de Biologia Molecular e "
    "da literatura acima.":
        "This help center does not use artificial intelligence: answers were written from the Molecular Biology SOPs "
        "and the literature above.",
    "Por quê": "Why", "O que fazer": "What to do", "Referências": "References",
    "Diretrizes de qPCR": "qPCR guidelines", "Cálculo da expressão relativa": "Relative expression calculation",
    "Genes de referência": "Reference genes", "Ferramentas de análise automatizada": "Automated analysis tools",
    "Estatística de dados de qPCR": "Statistics of qPCR data",
    "Qualidade do RNA e especificidade": "RNA quality and specificity",
    "Testes estatísticos usados no app": "Statistical tests used in the app",
    # diagnosis
    "Amostra {c}: concentração abaixo do mínimo.": "Sample {c}: concentration below the minimum.",
    "Amostra {c}: volume de RNA menor que 1 µL.": "Sample {c}: RNA volume below 1 µL.",
    "Amostra {c}: razões de pureza fora do critério.": "Sample {c}: purity ratios out of range.",
    "Amostra {c}: A260/230 entre 1,5 e 1,8.": "Sample {c}: A260/230 between 1.5 and 1.8.",
    "Gene {g}: branco com Ct {ct}.": "Gene {g}: blank with Ct {ct}.",
    "{n} amostra(s)×gene com réplicas discrepantes (ex.: {a} / {g}).":
        "{n} sample(s)×gene with discrepant replicates (e.g. {a} / {g}).",
    "{a} / {g}: nenhuma réplica amplificou.": "{a} / {g}: no replicate amplified.",
    "{g}: Ct médio varia {d} ciclos entre grupos (de {a} a {b}).": "{g}: mean Ct varies {d} cycles between groups ({a} to {b}).",
    "{g}: geNorm M = {m} e CV = {cv}% (acima do limite).": "{g}: geNorm M = {m} and CV = {cv}% (above the limit).",
    "{n} valor(es) com fold change > 8 ou < 0,125 (ex.: {a} / {g} = {v}).":
        "{n} value(s) with fold change > 8 or < 0.125 (e.g. {a} / {g} = {v}).",
    "Grupo(s) com menos de 3 réplicas: {g}.": "Group(s) with fewer than 3 replicates: {g}.",
    "Há amostras com nome automático (S1, S2…).": "Some samples have automatic names (S1, S2…).",

    # ---------------------------------------------------------------- statistics: recommendation text
    "Atenção: há grupo com n = {n}. Com menos de 3 réplicas biológicas por grupo, qualquer teste tem baixa "
    "confiabilidade – interprete com cautela e descreva o n na legenda.":
        "Warning: there is a group with n = {n}. With fewer than 3 biological replicates per group any test has low "
        "reliability – interpret with caution and report n in the legend.",
    "Com n pequeno (≤ 5 por grupo), os testes de normalidade e de homogeneidade têm pouco poder: um p > 0,05 não prova "
    "que as premissas são atendidas. Em qPCR, a escala ΔCt (log) costuma deixar os dados aproximadamente normais, o "
    "que favorece testes paramétricos.":
        "With small n (≤ 5 per group), normality and homogeneity tests have little power: p > 0.05 does not prove the "
        "assumptions hold. In qPCR, the ΔCt (log) scale usually makes data approximately normal, which favours "
        "parametric tests.",
    "Normalidade dos resíduos (Shapiro-Wilk): {p} → {r}.": "Normality of residuals (Shapiro-Wilk): {p} → {r}.",
    "Homogeneidade das variâncias (Brown-Forsythe/Levene): {p} → {r}.":
        "Homogeneity of variances (Brown-Forsythe/Levene): {p} → {r}.",
    "sem evidência contra a normalidade": "no evidence against normality", "desvio da normalidade": "departure from normality",
    "variâncias semelhantes": "similar variances", "variâncias diferentes": "unequal variances",
    "Dois grupos, dados normais e variâncias semelhantes: teste t de Student.":
        "Two groups, normal data and similar variances: Student's t-test.",
    "Dois grupos com variâncias diferentes: teste t de Welch (não assume variâncias iguais).":
        "Two groups with unequal variances: Welch's t-test (does not assume equal variances).",
    "Dois grupos sem normalidade: Mann-Whitney (não paramétrico). Com n = 3 por grupo, o menor p possível é 0,1 – ele "
    "não consegue dar significância; prefira o teste t na escala ΔCt.":
        "Two groups without normality: Mann-Whitney (non-parametric). With n = 3 per group the smallest possible p is "
        "0.1 – it cannot reach significance; prefer the t-test on the ΔCt scale.",
    "Premissas atendidas: ANOVA de uma via. Post hoc de Dunnett, que compara cada grupo apenas com o controle (mais "
    "poder que o Tukey quando essa é a pergunta).":
        "Assumptions met: one-way ANOVA. Dunnett's post hoc, which compares each group only with the control (more "
        "power than Tukey when that is the question).",
    "Premissas atendidas: ANOVA de uma via. Post hoc de Tukey, que compara todos os pares de grupos controlando o erro "
    "do conjunto.":
        "Assumptions met: one-way ANOVA. Tukey's post hoc, which compares all pairs of groups controlling the "
        "family-wise error.",
    "Dados normais, mas com variâncias diferentes: ANOVA de Welch (não assume variâncias iguais) com post hoc de "
    "Games-Howell (o app mostra as comparações com o controle).":
        "Normal data but unequal variances: Welch's ANOVA (does not assume equal variances) with Games-Howell post hoc "
        "(the app shows the comparisons with the control).",
    "Dados normais, mas com variâncias diferentes: ANOVA de Welch (não assume variâncias iguais) com post hoc de "
    "Games-Howell.":
        "Normal data but unequal variances: Welch's ANOVA (does not assume equal variances) with Games-Howell post hoc.",
    "Dados sem normalidade: Kruskal-Wallis (não paramétrico, compara postos) com post hoc de Dunn e correção de Holm. "
    "Com n = 3 por grupo, testes não paramétricos têm pouquíssimo poder.":
        "Data without normality: Kruskal-Wallis (non-parametric, compares ranks) with Dunn's post hoc and Holm "
        "correction. With n = 3 per group, non-parametric tests have very little power.",
    "O teste de Grubbs só aponta valores estatisticamente afastados; ele não diz que o valor está errado. Com n = 3, o "
    "G máximo possível (1,155) é praticamente igual ao crítico (1,153), então o teste quase nunca detecta nada – com "
    "poucas réplicas, olhe os dados. Antes de excluir uma amostra: (1) confira as réplicas técnicas (diferença > 0,5 "
    "Ct), a curva de melting e os brancos; (2) confira a qualidade do RNA (A260/280, A260/230) e o Ct do gene de "
    "referência dessa amostra; (3) procure anotações de problema na coleta, extração ou pipetagem. Só exclua com "
    "justificativa técnica, nunca apenas porque o valor 'atrapalha' o resultado, e informe a exclusão e o motivo nos "
    "métodos.":
        "Grubbs' test only flags statistically distant values; it does not say the value is wrong. With n = 3 the "
        "largest possible G (1.155) is practically equal to the critical value (1.153), so the test almost never "
        "detects anything – with few replicates, look at the data. Before excluding a sample: (1) check the technical "
        "replicates (difference > 0.5 Ct), the melt curve and the blanks; (2) check RNA quality (A260/280, A260/230) "
        "and the reference-gene Ct of that sample; (3) look for notes of problems during collection, extraction or "
        "pipetting. Exclude only with a technical justification, never just because the value 'spoils' the result, "
        "and report the exclusion and its reason in the methods.",
    "A ANOVA de duas vias testa, ao mesmo tempo, o efeito do tratamento, o efeito do segundo fator (ex.: idade) e a "
    "interação entre eles. Use quando a pergunta envolve os dois fatores juntos (ex.: \"o efeito do etanol muda com a "
    "idade?\"). Cuidados: (1) interprete primeiro a interação – se ela for significativa, os efeitos principais "
    "sozinhos podem enganar, e o correto é comparar os grupos dentro de cada nível do segundo fator (opção \"por "
    "nível\"); (2) no 2^−ΔΔCt cada nível costuma ser normalizado pelo seu próprio controle, então o efeito principal "
    "do segundo fator no fold change perde o sentido – analise na escala ΔCt; (3) com n = 3 por célula o poder para "
    "detectar interação é baixo.":
        "Two-way ANOVA tests, at the same time, the treatment effect, the second-factor effect (e.g. age) and their "
        "interaction. Use it when the question involves both factors together (e.g. \"does the ethanol effect change "
        "with age?\"). Caveats: (1) interpret the interaction first – if it is significant, main effects alone can "
        "mislead, and groups should be compared within each level of the second factor (\"per level\" option); "
        "(2) with 2^−ΔΔCt each level is usually normalized to its own control, so the main effect of the second factor "
        "on fold change is meaningless – analyse on the ΔCt scale; (3) with n = 3 per cell, power to detect an "
        "interaction is low.",

    # ---------------------------------------------------------------- planning and report
    'Planejamento': 'Planning',
    'Cronograma': 'Schedule',
    'Planejamento – cronograma': 'Planning – schedule',
    'Defina as datas de cada etapa, da bancada à análise, e compartilhe com os colaboradores': 'Set the date of each step, from the bench to the analysis, and share it with collaborators',
    '✨ Sugerir um cronograma a partir de uma data (você ajusta depois)': '✨ Suggest a schedule from a start date (adjust it afterwards)',
    'Início (extração de RNA)': 'Start (RNA extraction)',
    'Dias de qPCR': 'qPCR days',
    'Um dia por placa, em geral.': 'Usually one day per plate.',
    'Dias úteis entre etapas': 'Working days between steps',
    'Incluir curva de eficiência dos primers (PO.OPE.04)': 'Include primer efficiency curve (PO.OPE.04)',
    'Fins de semana são pulados. A repetição de qPCR fica 2 dias úteis depois do último qPCR e a análise, 2 dias úteis depois. Isto substitui a tabela abaixo.': 'Weekends are skipped. The qPCR repeat goes 2 working days after the last qPCR and the analysis 2 working days later. This replaces the table below.',
    'Sugerir cronograma': 'Suggest schedule',
    '<b>Etapas do experimento</b> – edite à vontade. Use o <b>+</b> no fim da tabela para acrescentar etapas. Em <b>Convidados</b>, coloque os e-mails dos colaboradores separados por vírgula.': "<b>Experiment steps</b> – edit freely. Use the <b>+</b> at the end of the table to add steps. In <b>Guests</b>, enter collaborators' e-mails separated by commas.",
    'Data': 'Date',
    'Etapa': 'Step',
    'Detalhes': 'Details',
    'Convidados': 'Guests',
    'Aparece em uma linha com * na mensagem.': 'Shown on a line starting with * in the message.',
    'E-mails separados por vírgula.': 'E-mails separated by commas.',
    'Preencha ao menos uma etapa com data para gerar a mensagem e os eventos.': 'Fill in at least one dated step to build the message and the events.',
    '💬 Mensagem para WhatsApp': '💬 WhatsApp message',
    '📆 Google Agenda': '📆 Google Calendar',
    'Idioma da mensagem': 'Message language',
    'Use o ícone de copiar no canto da caixa e cole no WhatsApp, ou abra direto pelo botão.': 'Use the copy icon in the corner of the box and paste it into WhatsApp, or open it directly with the button.',
    'Abrir no WhatsApp': 'Open in WhatsApp',
    '**Opção 1 – um evento por vez:** cada link abre o Google Agenda com a etapa já preenchida (dia inteiro, com os convidados). Confira e clique em Salvar; o Google envia o convite aos convidados.': '**Option 1 – one event at a time:** each link opens Google Calendar with the step filled in (all-day, with guests). Check it and click Save; Google sends the invitation to the guests.',
    '**Opção 2 – todas as etapas de uma vez:** baixe o arquivo .ics e importe no Google Agenda (Configurações → Importar e exportar). Também funciona no Outlook e no Apple Calendar.': '**Option 2 – all steps at once:** download the .ics file and import it into Google Calendar (Settings → Import & export). It also works in Outlook and Apple Calendar.',
    '📆 Baixar cronograma (.ics)': '📆 Download schedule (.ics)',
    'O cronograma é salvo no arquivo do experimento (aba Cronograma). O app não envia nada sozinho.': 'The schedule is saved in the experiment file (Schedule sheet). The app never sends anything on its own.',
    '**2. Figuras do relatório** – as mesmas da tela Estatística e figuras, com as cores, genes e opções que você escolheu lá': '**2. Report figures** – the same as on the Statistics and figures screen, with the colors, genes and options you chose there',
    'Gráfico de barras': 'Bar chart',
    'Incluir no relatório': 'Include in the report',
    'Nenhuma figura selecionada: o relatório terá só o texto.': 'No figure selected: the report will have text only.',
    '📦 Baixar tudo (.zip): Word em inglês e português + figuras em PNG 300 dpi e SVG': '📦 Download everything (.zip): Word in English and Portuguese + figures as 300 dpi PNG and SVG',
    # ---------------------------------------------------------------- table columns
    "Código": "Code", "Grupo": "Group", "Réplica": "Replicate", "Amostra": "Sample", "Poço": "Well",
    "Omitir": "Omit", "Branco": "Blank", "Usar": "Use", "Eficiência (%)": "Efficiency (%)", "Poços": "Wells",
    "Conc. 1 (ng/µL)": "Conc. 1 (ng/µL)", "Conc. 2 (ng/µL)": "Conc. 2 (ng/µL)",
    "Conc. média (ng/µL)": "Mean conc. (ng/µL)", "Qualidade": "Quality", "Situação": "Status",
    "1º Mix comum (µL)": "1st Common mix (µL)", "2º H2O DEPC (µL)": "2nd DEPC H2O (µL)", "3º RNA (µL)": "3rd RNA (µL)",
    "Tubo": "Tube", "Fator 2": "Factor 2", "Poços de branco": "Blank wells", "Poços com Ct": "Wells with Ct",
    "Menor Ct": "Lowest Ct", "Alerta": "Alert", "Avaliação": "Assessment",
    "Réplicas com Ct": "Replicates with Ct", "Ct médio": "Mean Ct", "Diferença entre réplicas": "Replicate difference",
    "Ct referência": "Reference Ct", "Fold change médio": "Mean fold change", "Desvio padrão": "SD",
    "Erro padrão": "SEM", "log2FC médio": "Mean log2FC", "Reações (+margem)": "Reactions (+margin)",
    "Mix por poço (µL)": "Mix per well (µL)", "cDNA por poço (µL)": "cDNA per well (µL)",
    "Nível": "Level", "Estatística": "Statistic", "Sig.": "Sig.", "Diferenças (post hoc)": "Differences (post hoc)",
    "Grupo 1": "Group 1", "Grupo 2": "Group 2", "p ajustado": "adjusted p", "Amostra suspeita": "Suspect sample",
    "G crítico": "Critical G", "Fonte": "Source", "SQ": "SS", "gl": "df", "Bloco": "Block",
    "Nomes no arquivo": "Names in file", "Amostras com código": "Samples with code", "Observação": "Note",
    "Diferença": "Difference",

    # ---------------------------------------------------------------- cell values (tval)
    "Pronto para cDNA": "Ready for cDNA", "Diluir o RNA antes (volume < mínimo)": "Dilute the RNA first (volume < minimum)",
    "Não usar: concentração insuficiente – concentrar ou reextrair":
        "Do not use: insufficient concentration – concentrate or re-extract",
    "Revisar qualidade antes de usar": "Review quality before use", "Ressalva (A260/230)": "Caveat (A260/230)",
    "Fora do critério": "Out of range", "branco": "blank", "controle sem RT": "no-RT control",
    "Branco do cDNA (água no lugar do RNA)": "cDNA blank (water instead of RNA)",
    "Sem branco para este gene": "No blank for this gene", "OK – sem amplificação": "OK – no amplification",
    "OK – Ct acima do limite": "OK – Ct above the limit", "ATENÇÃO – possível contaminação": "WARNING – possible contamination",
    "Nenhuma réplica amplificou": "No replicate amplified",
    "Estável": "Stable", "Aceitável para amostras heterogêneas": "Acceptable for heterogeneous samples",
    "Instável – revisar": "Unstable – review", "Sim": "Yes", "Não": "No", "Resíduo": "Residual",
    "Automático": "Automatic", "ANOVA de uma via": "One-way ANOVA", "ANOVA de Welch": "Welch's ANOVA",
    "Teste t de Student": "Student's t-test", "Teste t de Welch": "Welch's t-test",
    "Kruskal-Wallis": "Kruskal-Wallis", "Mann-Whitney": "Mann-Whitney",
    "Tabela genérica": "Generic table",
    "Grupo(s) com só 1 réplica biológica ficaram fora da estatística (aparecem no gráfico): ":
        "Group(s) with only 1 biological replicate were left out of the statistics (shown in the chart): ",
    "O grupo controle não tem réplicas suficientes (mínimo 2).": "The control group does not have enough replicates (minimum 2).",
    "É preciso ter pelo menos 2 grupos com 2 ou mais réplicas biológicas.":
        "At least 2 groups with 2 or more biological replicates are required.",
    "gene sugerido pelo nome do arquivo": "gene suggested from the file name",
    "não consegui identificar o gene – informe": "could not identify the gene – please enter it",
    "Alguns blocos não têm o código da amostra no nome do poço: informe a lista de amostras na ordem dos poços.":
        "Some blocks do not have the sample code in the well name: enter the sample list in well order.",
    "Não encontrei a tabela (No., Name, Ct) do Rotor-Gene no arquivo.": "Could not find the Rotor-Gene table (No., Name, Ct) in the file.",
    "A tabela do Rotor-Gene está vazia.": "The Rotor-Gene table is empty.",
    "Não encontrei a tabela de resultados (colunas 'Sample Name' e 'CT') no arquivo.":
        "Could not find the results table ('Sample Name' and 'CT' columns) in the file.",
    "Não encontrei as colunas de amostra, concentração e 260/280 no arquivo do NanoDrop.":
        "Could not find the sample, concentration and 260/280 columns in the NanoDrop file.",
}

# Valores com partes variáveis: (padrão em português, tradução com \1, \2…)
PATTERNS = [(re.compile(p), r) for p, r in [
    (r"Só (\d+) de (\d+) réplicas com Ct", r"Only \1 of \2 replicates with Ct"),
    (r"Diferença entre réplicas = (.+) Ct", r"Replicate difference = \1 Ct"),
    (r"(.+) µL MM \+ (.+) µL H2O no lugar do EM \+ pool de RNA", r"\1 µL MM + \2 µL H2O instead of EM + RNA pool"),
    (r"Interação (.+) × (.+)", r"Interaction \1 × \2"),
    (r"Grupo\(s\) com só 1 réplica biológica ficaram fora da estatística \(aparecem no gráfico\): (.+)",
     r"Group(s) with only 1 biological replicate were left out of the statistics (shown in the chart): \1"),
    (r"nomes misturados \((.+)\) – confira ou deixe desmarcado", r"mixed names (\1) – check or leave unticked"),
    (r"(\d+) poço\(s\) marcados como NEG pelo Rotor-Gene foram considerados sem Ct\.",
     r"\1 well(s) marked NEG by the Rotor-Gene were treated as no Ct."),
    (r"Não reconheci o formato\.(.*)", r"Unrecognized format. Use the QuantStudio or Rotor-Gene export, or a table "
                                       r"with Sample, Gene and Ct columns."),
]]

# Central de ajuda em inglês (mesmos ids de help.FAQ)
FAQ_EN = {
    "conc_baixa": {
        "titulo": "RNA concentration too low for cDNA",
        "palavras": "low concentration insufficient rna yield cdna nanodrop",
        "causa": "With 500 ng in 8 µL, RNA must be at least 62.5 ng/µL. Little tissue, incomplete lysis, elution in a "
                 "large volume or loss on the column reduce the concentration.",
        "solucao": "1) Concentrate the sample (speed-vac without heat) and re-quantify. 2) If that fails, re-extract "
                   "with more tissue (up to 30 mg) or re-apply the eluate in the 2nd elution. 3) Only as a last resort, "
                   "lower the RNA mass of ALL samples of the experiment to the same value."},
    "a230": {
        "titulo": "Low A260/230 (guanidine or ethanol carry-over)",
        "palavras": "260/230 guanidine ethanol purity salt contamination",
        "causa": "Guanidine salt (RLT/RW1 buffers) or ethanol carried over into the eluate.",
        "solucao": "Do the column drying spin (1 min, maximum speed) and do not let the column touch the "
                   "flow-through. Between 1.5 and 1.8 the sample can be used with a caveat; below 1.5, re-extract."},
    "a280": {
        "titulo": "A260/280 outside 1.8–2.1",
        "palavras": "260/280 protein phenol purity",
        "causa": "Residual protein or phenol, usually from incomplete lysis or homogenization.",
        "solucao": "Re-extract ensuring complete lysis (sonication on ice, 2–3 cycles) and do not exceed 30 mg of "
                   "tissue."},
    "diluir": {
        "titulo": "RNA volume below 1 µL",
        "palavras": "small volume dilute concentrated rna pipette",
        "causa": "Very concentrated RNA: 500 ng fit in less than 1 µL, an imprecise volume to pipette.",
        "solucao": "Dilute an RNA aliquot (e.g. 1:5) in DEPC water, re-quantify (or calculate from the dilution) and "
                   "pipette from the dilution."},
    "branco": {
        "titulo": "Blank (NTC or BcDNA) amplified",
        "palavras": "blank ntc bcdna contamination amplified primer dimer",
        "causa": "Contamination of reagents, water, tips or bench with DNA/PCR products; or primer dimer (melt peak at "
                 "a lower temperature than the product).",
        "solucao": "1) Compare the blank melt curve with the samples: a different peak and high Ct (> 35) indicate a "
                   "dimer, which is acceptable. 2) If the peak matches the product, discard the water, primer and mix "
                   "aliquots used and repeat the gene. 3) Never open amplified plates in the preparation lab."},
    "replicas": {
        "titulo": "Technical replicates differing by more than 0.5 Ct",
        "palavras": "replicates duplicate difference discrepant variation pipetting",
        "causa": "Pipetting error (mainly the 1 µL of cDNA), bubbles, poorly sealed well, insufficient mixing or high "
                 "Ct (> 32), where variation is naturally larger.",
        "solucao": "Check both wells' curves in Design & Analysis. If one well has an obvious technical problem, tick "
                   "Omit in the import tab and record the reason; otherwise repeat the sample for that gene. With "
                   "triplicates, the app can remove the outlying replicate automatically (Auto-qPCR rule). For genes "
                   "with very high Ct, consider using more cDNA."},
    "nd": {
        "titulo": "Sample without amplification (Undetermined / ND)",
        "palavras": "undetermined nd no amplification missing ct neg",
        "causa": "Very low-abundance transcript, failed cDNA synthesis, cDNA forgotten in the well or a poor primer.",
        "solucao": "Check whether the reference gene amplified in the same sample (if not, the problem is the cDNA). "
                   "If only this gene failed, check the primer efficiency (PO.OPE.04BIOMOL) and consider more cDNA."},
    "ref_instavel": {
        "titulo": "Reference gene varying between groups",
        "palavras": "reference endogenous housekeeping gapdh actin unstable normalization genorm stability",
        "causa": "The treatment affects the reference gene, or RNA amount/quality differs between groups. This "
                 "distorts every fold change of the affected group.",
        "solucao": "A reference-gene Ct difference above ~1 between groups is a warning sign. Check the RNA "
                   "quantification of that group, validate another reference gene (e.g. ef1a, rpl13a) and, ideally, "
                   "select 2 or more reference genes in the app: it normalizes to their geometric mean and reports "
                   "geNorm M and CV (MIQE)."},
    "fc_extremo": {
        "titulo": "Very high or very low fold change",
        "palavras": "fold change high extreme very large strange",
        "causa": "It can be biological, but often comes from an unstable reference gene, very high target Ct (near "
                 "35), few replicates or sample mix-ups.",
        "solucao": "Check the reference-gene Ct in those samples, the technical replicates and the plate map before "
                   "interpreting."},
    "n_baixo": {
        "titulo": "Group with fewer than 3 biological replicates",
        "palavras": "low n biological replicates pools few lost sample",
        "causa": "Sample lost, excluded or failed to amplify.",
        "solucao": "With n < 3 statistics are unreliable and groups with n = 1 are left out of the tests. Plan at least "
                   "3 pools per group and, if possible, a spare pool."},
    "grupos": {
        "titulo": "Groups not recognized (samples S1, S2…)",
        "palavras": "groups s1 s2 sample name code rotor-gene list",
        "causa": "The Rotor-Gene file did not have the sample code in the well name and the sample list was not "
                 "filled in.",
        "solucao": "In the Import run tab, fill in the sample list in well order. In future runs, name each well with "
                   "the sample code (a1, a2…)."},
    "normalidade": {
        "titulo": "Data not normal or with unequal variances",
        "palavras": "normality shapiro levene variance kruskal welch non-parametric assumption",
        "causa": "Skewed distribution, an outlier or unequal variances between groups.",
        "solucao": "The app chooses the appropriate test (Welch with Games-Howell for unequal variances; "
                   "Kruskal-Wallis with Dunn for non-normality) and explains why. Analyse on the ΔCt (log) scale, "
                   "which usually fixes the fold-change skew. With n = 3, assumption tests have little power."},
    "outlier": {
        "titulo": "Possible outlier: exclude or not?",
        "palavras": "outlier grubbs rout exclude sample discrepant",
        "causa": "A value far from the others in the group.",
        "solucao": "Do not exclude a value just because it gets in the way. Check technical replicates, melt curve, "
                   "blanks, RNA quality, the sample's reference-gene Ct and collection notes. Exclude only with a "
                   "technical justification and report the exclusion in the methods."},
    "eficiencia": {
        "titulo": "Primer efficiency outside 90–110%",
        "palavras": "efficiency primer slope standard curve r2 90 110",
        "causa": "Imprecise dilutions, inhibition at concentrated points, primer dimer or points outside the linear "
                 "range.",
        "solucao": "Repeat the serial dilution with a new tip for each point, drop points outside the linear range "
                   "(Ct > 35 or plateau) and, if it persists, adjust the primer concentration or design a new pair. "
                   "Enter the efficiency of each gene in the app (Groups tab) to correct the calculation."},
    "arquivo": {
        "titulo": "The app did not recognize my results file",
        "palavras": "file error upload format csv xls quantstudio rotor not recognized",
        "causa": "Different format than expected (e.g. export of another sheet or another software).",
        "solucao": "QuantStudio: export via Results → Export (.xls). Rotor-Gene: use 'Excel Analysed Data Export' "
                   "(.csv). Others: build a table with Sample, Gene and Ct columns (Amostra, Gene, Ct)."},
    "escala": {
        "titulo": "Why are statistics done on ΔCt and not on fold change?",
        "palavras": "log scale delta ct fold change statistics anova asymmetric log2",
        "causa": "Fold change (2^−ΔΔCt) is asymmetric: decreases lie between 0 and 1 and increases from 1 to "
                 "infinity, and the variance grows with the mean. Ct/ΔCt is what the treatment affects directly and "
                 "is closer to a normal distribution.",
        "solucao": "The app tests the ΔCt of each biological replicate (same p-values as log2 fold change) and shows "
                   "fold change in charts and text. Testing fold change directly is available only to compare with "
                   "older analyses."},
    "posthoc": {
        "titulo": "Dunnett, Tukey, Games-Howell or Dunn: which post hoc?",
        "palavras": "post hoc dunnett tukey games howell dunn multiple comparisons which test",
        "causa": "Each post hoc answers a different question and has different assumptions.",
        "solucao": "Dunnett: each group versus control (more power when that is the question). Tukey: all pairs, with "
                   "similar variances. Games-Howell: all pairs when variances differ (after Welch's ANOVA). Dunn with "
                   "Holm correction: after Kruskal-Wallis (non-parametric). The app suggests the appropriate one and "
                   "explains why on the Statistics and figures screen."},
}

# AmpliQA

[![tests](https://github.com/meriofilho/ampliqa/actions/workflows/tests.yml/badge.svg)](https://github.com/meriofilho/ampliqa/actions/workflows/tests.yml)

[English](README.md) · **Português**

### ▶️ [Abrir o AmpliQA no navegador](https://ampliqpcr.streamlit.app/) – sem instalar nada

O **AmpliQA** é um app web gratuito e de código aberto (Python + Streamlit) para **planejar e analisar experimentos de expressão
gênica por RT-qPCR**, da quantificação do RNA à figura e ao texto de métodos. Segue as diretrizes MIQE e os POPs de
Biologia Molecular (PO.OPE.01 a 04BIOMOL) do Fish Lab.

O AmpliQA é um projeto conjunto de dois laboratórios da Universidade Federal do Rio Grande do Norte (UFRN):

- [**Dalmolin Systems Biology Group**](https://dalmolingroup.imd.ufrn.br/), Programa de Pós-Graduação em Bioinformática
- [**Fish Lab – Laboratório de Peixes**](https://www.fishlabufrn.com/)

### Por que "AmpliQA"?

- **Ampli** – de *amplificação*, o processo central da PCR, a técnica mais usada em qualquer laboratório de biologia molecular.
- **QA** – *Quality Assurance* (garantia de qualidade): a ferramenta ajuda a organizar, padronizar e validar os experimentos, da qualidade do RNA à conferência de réplicas, brancos e genes de referência.

> Licença [MIT](LICENSE). Como citar: [CITATION.cff](CITATION.cff).

## O que o app faz

| Etapa | Recursos |
|---|---|
| **Quantificação → cDNA** | Leituras do NanoDrop, critérios de qualidade (A260/280, A260/230), volumes para 500 ng em 20 µL, mix comum e lista de pipetagem. |
| **qPCR** | Mapa de placa e mix por gene; importação automática (QuantStudio, Rotor-Gene Q, tabelas); conferência de brancos e réplicas; **1 a 5 genes de referência** (média geométrica); **eficiência por gene**; **estabilidade das referências** (geNorm M e CV); remoção opcional de réplicas técnicas discrepantes (critério do Auto-qPCR). |
| **Estatística e figuras** | Premissas (Shapiro-Wilk nos resíduos, Brown-Forsythe), teste recomendado e explicado (ANOVA + Dunnett/Tukey; Welch + Games-Howell; Kruskal-Wallis + Dunn-Holm; testes t / Mann-Whitney), Grubbs, 2º fator (por nível ou ANOVA de duas vias), gráfico de barras e heatmap (PNG 300 dpi e SVG, fonte Roboto), **exportação pronta para o GraphPad Prism**. |
| **Métodos e resultados** | Rascunho em inglês e português com F, p e fold change preenchidos; exporta .docx. |
| **Central de ajuda** | Diagnóstico do experimento aberto, perguntas frequentes com causa e solução, links para os POPs e referências com DOI conferido na Crossref. Sem IA. |

Interface em **português e inglês** (seletor na barra lateral).

## Como os cálculos são feitos

- **Quantidade relativa** pelo modelo generalizado do qBase (Hellemans et al., 2007):
  RQ = E^(Cq calibrador − Cq amostra), com o calibrador = média do Cq do grupo controle (em cada nível do 2º fator);
  NF = média geométrica dos RQ das referências; **NRQ = RQ / NF = fold change**.
  Com eficiência de 100% (E = 2) e uma referência, o resultado é **idêntico ao 2^−ΔΔCt** (Livak & Schmittgen, 2001).
- **ΔCt** ponderado pela eficiência (Cq·log2E do alvo − média de Cq·log2E das referências), de modo que
  ΔΔCt = ΔCt − média do controle = −log2 fold change.
- **Estatística** no ΔCt de cada réplica biológica (os mesmos p-valores do log2 fold change; Yuan et al., 2006;
  Rieu & Powers, 2009). O fold change é usado para apresentar os resultados.
- **Estabilidade das referências**: geNorm M (Vandesompele et al., 2002) e CV dos NRQ; estáveis quando M < 0,5 e
  CV < 25% (amostras homogêneas) ou M < 1 e CV < 50% (heterogêneas) (Hellemans et al., 2007).
- **Réplicas técnicas** (opcional): se o DP passa de 0,3 ciclo, remove a réplica mais distante da média, sem passar de
  metade das réplicas e mantendo ao menos 2; preserva conjuntos sem outlier claro (|média − mediana| < 0,1)
  (Maussion et al., 2021).

Validação: cálculos conferidos com as planilhas-anexo dos POPs, com corridas reais de qPCR (só no computador do laboratório, não distribuídas) e com fórmulas
independentes; estatística conferida com `pingouin` e `scikit-posthocs` (ver `tests/`).

## Formatos de resultados aceitos (detectados sozinhos; vários arquivos de uma vez)

| Equipamento / formato | Arquivo | Observações |
|---|---|---|
| QuantStudio (Design & Analysis) | .xls/.xlsx (aba Results) ou .csv/.txt | Usa Sample Name, Target Name e CT. |
| Rotor-Gene Q (QIAGEN) | .csv "Excel Analysed Data Export" | Não traz o gene: o app divide os poços em blocos (cada bloco termina nos brancos) e sugere o gene pelo nome do poço ou do arquivo, para conferir. Vírgula ou ponto decimal; "NEG" = sem Ct. |
| Tabela genérica longa | .csv/.xlsx | Colunas Amostra, Gene, Ct. |
| Tabela genérica larga | .csv/.xlsx | Coluna Amostra e/ou Grupo + uma coluna de Ct por gene. |

## Como os dados ficam guardados

Nada fica no servidor. Cada experimento é um **arquivo do experimento (.xlsx)** que o usuário baixa e guarda no próprio
Google Drive; para continuar, carrega o arquivo na tela Início. O arquivo também abre no Excel.

## Rodar no computador

```bash
git clone https://github.com/meriofilho/ampliqa.git
cd ampliqa
python -m venv .venv
.venv\Scripts\activate        # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
python -m streamlit run app.py
```

## Testes

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

## Estrutura

```
app.py                 navegação entre as telas
views/                 telas (Início, Quantificação → cDNA, qPCR, Estatística, Métodos, Ajuda)
ampliqa/qpcr.py         qBase/ΔΔCt, estabilidade das referências, réplicas, brancos, placa e mix
ampliqa/stats.py        premissas, testes, post hoc, outliers
ampliqa/analysis.py     análise completa e exportação para o Prism
ampliqa/figures.py      gráfico de barras e heatmap
ampliqa/texts.py        textos de métodos e resultados (EN/PT)
ampliqa/importers.py    leitura dos arquivos dos equipamentos
ampliqa/i18n.py         traduções da interface
ampliqa/help.py         central de ajuda e referências
```

## Publicar (Streamlit Community Cloud – grátis)

Versão pública: https://ampliqpcr.streamlit.app/

1. Código: https://github.com/meriofilho/ampliqa
2. Em share.streamlit.io: *Create app* → repositório, branch e `app.py`.
3. Em *Settings → Sharing*, deixar público ou restrito a e-mails.

## Licença e créditos

Código sob licença [MIT](LICENSE). Fonte Roboto (assets/fonts), do Google, sob SIL Open Font License / Apache 2.0. Desenvolvido por Romério de Oliveira Lima Filho, doutorando em Bioinformática no
[Dalmolin Systems Biology Group](https://dalmolingroup.imd.ufrn.br/), em parceria com o [Fish Lab](https://www.fishlabufrn.com/) (UFRN).
Os POPs citados no app são documentos internos do Fish Lab/Z-SAFE.

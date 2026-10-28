# AmpliQA

[![tests](https://github.com/meriofilho/ampliqa/actions/workflows/tests.yml/badge.svg)](https://github.com/meriofilho/ampliqa/actions/workflows/tests.yml)

**English** · [Português](README.pt-BR.md)

### ▶️ [Open AmpliQA in your browser](https://ampliqpcr.streamlit.app/) – nothing to install

**AmpliQA** is a free, open-source web app (Python + Streamlit) to **plan and analyse RT-qPCR gene-expression experiments**, from RNA
quantification to the figure and the methods text. It follows the MIQE guidelines and the molecular biology SOPs
(PO.OPE.01–04BIOMOL) of the Fish Lab.

AmpliQA is a joint project of two laboratories at the Federal University of Rio Grande do Norte (UFRN, Brazil):

- [**Dalmolin Systems Biology Group**](https://dalmolingroup.imd.ufrn.br/), Graduate Program in Bioinformatics
- [**Fish Lab, Laboratório de Peixes**](https://www.fishlabufrn.com/)

### Why "AmpliQA"?

- **Ampli** – from *amplification*, the core of PCR, the most used technique in any molecular biology lab.
- **QA** – *Quality Assurance*: the tool helps organize, standardize and validate experiments, from RNA quality to replicate, blank and reference-gene checks.

> Licensed under [MIT](LICENSE). How to cite: [CITATION.cff](CITATION.cff).

## Features

| Step | What it does |
|---|---|
| **Quantification → cDNA** | NanoDrop readings, quality criteria (A260/280, A260/230), volumes for 500 ng in 20 µL, master mix and pipetting list. |
| **qPCR** | Plate map and per-gene mix; automatic import (QuantStudio, Rotor-Gene Q, generic tables); blank and replicate checks; **1–5 reference genes** (geometric mean); **gene-specific efficiencies**; **reference-gene stability** (geNorm M and CV); optional removal of outlying technical replicates (Auto-qPCR rule). |
| **Statistics and figures** | Assumption checks (Shapiro-Wilk on residuals, Brown-Forsythe), recommended and explained test (ANOVA + Dunnett/Tukey; Welch + Games-Howell; Kruskal-Wallis + Dunn-Holm; t-tests / Mann-Whitney), Grubbs, second factor (per level or two-way ANOVA), bar chart and heatmap (PNG 300 dpi and SVG, Roboto font), **GraphPad Prism-ready export**. |
| **Methods and results** | Draft text in English and Portuguese with F, p and fold change filled in; .docx export. |
| **Help center** | Diagnosis of the open experiment, FAQ with cause and fix, links to the SOPs and references with Crossref-checked DOIs. No AI. |

Interface in **English and Portuguese** (selector in the sidebar).

## How the calculations work

- **Relative quantities** follow the generalized qBase model (Hellemans et al., 2007):
  RQ = E^(Cq calibrator − Cq sample), where the calibrator is the mean Cq of the control group (per level of the
  second factor); NF = geometric mean of the reference-gene RQs; **NRQ = RQ / NF = fold change**.
  With 100% efficiency (E = 2) and one reference gene this is **identical to 2^−ΔΔCt** (Livak & Schmittgen, 2001).
- **ΔCt** is efficiency-weighted (Cq·log2E of the target − mean Cq·log2E of the references), so that
  ΔΔCt = ΔCt − control mean = −log2 fold change.
- **Statistics** run on the ΔCt of each biological replicate (same p-values as log2 fold change; Yuan et al., 2006;
  Rieu & Powers, 2009). Fold change is used to present results.
- **Reference stability**: geNorm M (Vandesompele et al., 2002) and CV of the NRQs; stable when M < 0.5 and CV < 25%
  (homogeneous samples) or M < 1 and CV < 50% (heterogeneous samples) (Hellemans et al., 2007).
- **Technical replicates** (optional): when the SD exceeds 0.3 cycles, the replicate furthest from the mean is removed,
  never more than half of them and always keeping at least 2; sets without a clear outlier (|mean − median| < 0.1)
  are kept (Maussion et al., 2021).

Validation: calculations checked against the SOP spreadsheets, real qPCR runs (local only, not distributed) and independent formulas; statistics
checked against `pingouin` and `scikit-posthocs` (see `tests/`).

## Supported result files (auto-detected; several at once)

| Instrument / format | File | Notes |
|---|---|---|
| QuantStudio (Design & Analysis) | .xls/.xlsx (Results sheet) or .csv/.txt | Uses Sample Name, Target Name and CT. |
| Rotor-Gene Q (QIAGEN) | .csv "Excel Analysed Data Export" | Has no gene column: wells are split into blocks (each ending at the blanks) and the gene is suggested from the well or file name, for the user to confirm. Decimal comma or point; "NEG" = no Ct. |
| Generic long table | .csv/.xlsx | Columns Sample, Gene, Ct (Amostra, Gene, Ct). |
| Generic wide table | .csv/.xlsx | Sample and/or Group column + one Ct column per gene. |

## Where data is stored

Nothing is stored on the server. Each experiment is an **experiment file (.xlsx)** that users download and keep in
their own Google Drive; to continue, they load it on the Home screen. The file also opens in Excel.

## Run locally

```bash
git clone https://github.com/meriofilho/ampliqa.git
cd ampliqa
python -m venv .venv
.venv\Scripts\activate        # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
python -m streamlit run app.py
```

## Tests

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

## Project layout

```
app.py                 page navigation
views/                 screens (Home, Quantification → cDNA, qPCR, Statistics, Methods, Help)
ampliqa/qpcr.py         qBase/ΔΔCt, reference stability, replicates, blanks, plate and mix
ampliqa/stats.py        assumptions, tests, post hoc, outliers
ampliqa/analysis.py     full analysis and Prism export
ampliqa/figures.py      bar chart and heatmap
ampliqa/texts.py        methods and results text (EN/PT)
ampliqa/importers.py    instrument file readers
ampliqa/i18n.py         interface translations
ampliqa/help.py         help center and references
```

## Deploy (Streamlit Community Cloud – free)

Public instance: https://ampliqpcr.streamlit.app/

1. Code: https://github.com/meriofilho/ampliqa
2. At share.streamlit.io: *Create app* → repository, branch and `app.py`.
3. Under *Settings → Sharing*, make it public or restrict it to specific e-mails.

## License and credits

Code released under the [MIT License](LICENSE). Roboto font (assets/fonts) by Google, under the SIL Open Font License / Apache 2.0. Developed by Romério de Oliveira Lima Filho, PhD student in Bioinformatics at the
[Dalmolin Systems Biology Group](https://dalmolingroup.imd.ufrn.br/), in partnership with the [Fish Lab](https://www.fishlabufrn.com/) (UFRN).
The lab SOPs referenced in the app are internal Fish Lab/Z-SAFE documents.

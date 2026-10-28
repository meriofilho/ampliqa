"""Dados FICTÍCIOS, limpos e fáceis de entender, para o usuário ver como cada etapa funciona e como devem ser os
arquivos que ele vai carregar.

Desenho do exemplo: 3 grupos × 3 pools (larvas de zebrafish), 1 gene de referência e 3 genes-alvo.
- A = Controle · B = Dose baixa · C = Dose alta (códigos A1–A3, B1–B3, C1–C3)
- actb1: referência estável
- bdnf: expressão diminui com a dose (fold change ≈ 0,7 e 0,5)
- sox2: expressão aumenta com a dose (fold change ≈ 1,5 e 2,5)
- cdnf: sem efeito (fold change ≈ 1)
"""
import io

import numpy as np
import pandas as pd

from . import experiment, quant

GROUPS = {"A": "Controle", "B": "Dose baixa", "C": "Dose alta"}
SAMPLES = [f"{g}{i}" for g in GROUPS for i in (1, 2, 3)]
GENES = ["actb1", "bdnf", "sox2", "cdnf"]
REF = "actb1"

# ΔCt alvo por grupo (gene − actb1)
DCT = {"bdnf": {"A": 6.0, "B": 6.5, "C": 7.0},
       "sox2": {"A": 8.0, "B": 7.4, "C": 6.7},
       "cdnf": {"A": 7.0, "B": 7.0, "C": 7.05}}
# variação biológica pequena e diferente em cada pool (valores fixos, para o exemplo ser sempre igual)
BIO = {"A1": -0.11, "A2": 0.02, "A3": 0.12, "B1": 0.07, "B2": -0.13, "B3": 0.04,
       "C1": -0.04, "C2": 0.14, "C3": -0.09}
GENE_VAR = {"actb1": 0.0, "bdnf": 1.0, "sox2": -0.8, "cdnf": 0.6}
TEC = (-0.04, 0.04)                           # diferença entre as duas réplicas técnicas
REF_CT = {"A": 18.20, "B": 18.25, "C": 18.15}


def quant_table() -> pd.DataFrame:
    """Leituras do NanoDrop: todas as amostras dentro dos critérios."""
    conc = [212.4, 188.6, 240.1, 175.3, 203.8, 226.9, 195.2, 181.7, 230.5]
    rows = []
    for s, c in zip(SAMPLES, conc):
        rows.append({"Código": s, "Grupo": s[0], "Réplica": s[1], "Conc. 1 (ng/µL)": c, "A260/280 1": 2.02,
                     "A260/230 1": 2.15, "Conc. 2 (ng/µL)": round(c * 0.99, 1), "A260/280 2": 2.03,
                     "A260/230 2": 2.12, "Observações": None})
    return quant.normalize(pd.DataFrame(rows))


def ct_value(gene, sample, rep):
    g = sample[0]
    ref = REF_CT[g] + 0.3 * BIO[sample]
    ct = ref if gene == REF else ref + DCT[gene][g] + GENE_VAR[gene] * BIO[sample]
    return round(ct + TEC[rep], 2)


def qpcr_long() -> pd.DataFrame:
    """Uma linha por poço, no layout do PO.OPE.03BIOMOL: por gene, amostras em duplicata + NTC + BcDNA."""
    rows, w = [], 0
    for gene in GENES:
        for s in SAMPLES:
            for rep in (0, 1):
                rows.append((gene, s, ct_value(gene, s, rep)))
        rows += [(gene, "NTC", np.nan), (gene, "BcDNA", np.nan)]
    out = []
    for i, (gene, s, ct) in enumerate(rows):
        r, c = divmod(i, 12)
        out.append({"Poço": f"{'ABCDEFGH'[r]}{c + 1}", "Amostra": s, "Gene": gene, "Ct": ct, "Omitir": False})
    return pd.DataFrame(out)


def experiment_example() -> dict:
    e = experiment.new_experiment("Exemplo – larvas expostas a duas doses", "Fishlab (dados fictícios)")
    e["meta"].update({"Espécie": "Zebrafish (Danio rerio)", "Tecido": "Larva inteira", "Grupos": 3,
                      "Amostras por grupo": 3, "Indivíduos por pool": 10})
    e["meta"]["Observações"] = "Dados fictícios para aprender a usar o app."
    e["quant"] = quant_table()
    raw = qpcr_long()
    from . import qpcr
    e["qpcr_raw"] = raw
    e["qpcr_groups"] = qpcr.default_groups(raw["Amostra"])
    e["qpcr_cfg"].update({"ref": REF, "controle": "A", "ordem_grupos": "A;B;C",
                          "genes_placa": "\n".join(GENES), "amostras_placa": "\n".join(SAMPLES)})
    e["stats_cfg"] = {"rotulos": ";".join(f"{k}={v}" for k, v in GROUPS.items())}
    e["methods_cfg"] = {"exposicao": "exposed to compound X at a low and a high dose (fictitious example)"}
    return e


# ------------------------------------------------------------------ arquivos de exemplo para baixar
def file_quantstudio() -> bytes:
    """Planilha no formato da exportação do QuantStudio (aba Results)."""
    raw = qpcr_long()
    meta = [["Block Type", "96-Well 0.1-mL Block"], ["Chemistry", "SYBR_GREEN"],
            ["Experiment Name", "Exemplo Fishlab (dados fictícios)"], ["Instrument Type", "QuantStudio™ 3 System"],
            ["Passive Reference", "ROX"], [None, None]]
    tab = pd.DataFrame({
        "Well": range(1, len(raw) + 1), "Well Position": raw["Poço"], "Omit": False, "Sample Name": raw["Amostra"],
        "Target Name": raw["Gene"], "Task": ["NTC" if s in ("NTC", "BcDNA") else "UNKNOWN" for s in raw["Amostra"]],
        "Reporter": "SYBR", "Quencher": "None",
        "CT": [("Undetermined" if pd.isna(v) else v) for v in raw["Ct"]]})
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as xw:
        pd.DataFrame(meta).to_excel(xw, sheet_name="Results", index=False, header=False)
        tab.to_excel(xw, sheet_name="Results", index=False, startrow=len(meta))
    return buf.getvalue()


def file_rotorgene() -> bytes:
    """CSV no formato 'Excel Analysed Data Export' do Rotor-Gene Q (um bloco por gene, terminando nos brancos)."""
    raw = qpcr_long()
    lines = ["Excel Analysed Data Export", "Copyright (c) QIAGEN GmbH. (arquivo de exemplo fictício)",
             "File;actb1 bdnf sox2 cdnf - exemplo.rex", "", "Quantitative analysis of Cycling A.Green (Page 1)", "",
             "No.;Color;Name;Type;Ct;Ct Comment"]
    for i, r in enumerate(raw.itertuples(), 1):
        name = r.Amostra.lower() if r.Amostra not in ("NTC", "BcDNA") else "branco"
        ct = "" if pd.isna(r.Ct) else f"{r.Ct:.2f}".replace(".", ",")
        lines.append(f"{i};255;{name};Unknown;{ct};")
    return "\r\n".join(lines).encode("utf-8")


def file_generic() -> bytes:
    raw = qpcr_long()
    t = raw[["Amostra", "Gene", "Ct"]].copy()
    t["Ct"] = [("Undetermined" if pd.isna(v) else f"{v:.2f}".replace(".", ",")) for v in t["Ct"]]
    return t.to_csv(sep=";", index=False).encode("utf-8")


def file_nanodrop() -> bytes:
    rows = ["Sample ID\tUser ID\tDate\tTime\tNucleic Acid Conc.\tUnit\tA260\tA280\t260/280\t260/230\tSample Type"]
    for _, r in quant_table().iterrows():
        for k in (1, 2):
            c = r[f"Conc. {k} (ng/µL)"]
            rows.append(f"{r['Código']}\tfishlab\t27/10/2026\t10:0{k}\t{c:.1f}\tng/µl\t{c / 40:.3f}\t"
                        f"{c / 40 / r[f'A260/280 {k}']:.3f}\t{r[f'A260/280 {k}']:.2f}\t{r[f'A260/230 {k}']:.2f}\tRNA")
    return ("\n".join(rows) + "\n").encode("utf-8")


def file_experiment() -> bytes:
    return experiment.to_xlsx(experiment_example())


DOWNLOADS = {
    "QuantStudio (aba Results)": ("exemplo_quantstudio_results.xlsx", file_quantstudio,
                                  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
    "Rotor-Gene Q (.csv)": ("actb1 bdnf sox2 cdnf - exemplo.csv", file_rotorgene, "text/csv"),
    "Tabela simples (Amostra, Gene, Ct)": ("exemplo_tabela_simples.csv", file_generic, "text/csv"),
}

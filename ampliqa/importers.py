"""Importação de resultados de qPCR de diferentes equipamentos e formatos.

Formatos reconhecidos automaticamente:
- QuantStudio (Design & Analysis): .xls/.xlsx/.csv/.txt com a tabela da aba Results
  (Sample Name, Target Name, CT).
- Rotor-Gene Q (QIAGEN) – "Excel Analysed Data Export" em .csv (No., Name, Type, Ct). Não traz coluna de gene:
  os poços são divididos em blocos (cada bloco termina nos brancos) e o gene de cada bloco é sugerido a partir do
  nome dos poços ou do nome do arquivo, para o usuário conferir.
- Tabela genérica longa: colunas Amostra/Sample, Gene/Target e Ct/Cq.
- Tabela genérica larga: coluna Amostra (ou nº) e/ou Grupo + uma coluna de Ct por gene.

Observação: o Rotor-Gene calcula "Rep. Ct" agrupando poços com o mesmo nome – se a mesma amostra aparece em
dois genes, ele mistura os dois. Por isso o app ignora "Rep. Ct" e recalcula tudo a partir do Ct de cada poço.
"""
import io
import os
import re

import numpy as np
import pandas as pd

from . import quantstudio

BLANK_RE = re.compile(r"^(branco|blank|ntc|bcdna|nrt|nada)\d*$", re.I)
CODE_RE = re.compile(r"^[a-z]{1,3}\d{1,3}$", re.I)
NOISE_RE = re.compile(r"^(\d+|\d+dpf|\d+ugml|\d+(\.\d+)?ug(/)?ml|\d{1,2}\.\d{1,2}|dpf|ugml)$", re.I)
FILE_STOP = {"certo", "e", "and", "de", "do", "da", "pcr", "qpcr", "extras", "novo", "nova", "final", "teste",
             "copia", "cópia", "corrida", "resultado", "resultados", "rotorgene", "rotor", "gene", "qiagen",
             "quantstudio", "export", "dados", "data", "exemplo", "example"}
RAW_COLS = ["Poço", "Amostra", "Gene", "Ct", "Omitir"]


# ---------------------------------------------------------------- utilidades
def _text(data: bytes) -> str:
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def _split_lines(text: str):
    lines = [ln.rstrip("\r") for ln in text.split("\n")]
    sample = "\n".join(lines[:80])
    sep = ";" if sample.count(";") > max(sample.count(","), sample.count("\t")) else (
        "\t" if sample.count("\t") >= sample.count(",") else ",")
    rows = []
    for ln in lines:
        cells = [c.strip().strip('"').strip() for c in ln.split(sep)]
        rows.append(cells)
    return rows


def to_ct(v):
    if v is None:
        return np.nan
    if isinstance(v, (int, float, np.number)):
        return float(v) if not pd.isna(v) else np.nan
    s = str(v).strip()
    if not s:
        return np.nan
    if s.count(",") == 1 and s.count(".") == 0:
        s = s.replace(",", ".")
    try:
        x = float(s)
    except ValueError:
        return np.nan  # "Undetermined", "NEG", vazio
    return x if 0 < x < 60 else np.nan


def tokens(name: str):
    return [t for t in re.split(r"[\s\-_/]+", str(name).strip().lower()) if t]


def is_blank_name(name: str, extra=()) -> bool:
    toks = tokens(name)
    if any(BLANK_RE.match(t) for t in toks):
        return True
    return str(name).strip().upper() in {str(e).strip().upper() for e in extra if str(e).strip()}


def file_gene_tokens(filename: str):
    base = os.path.splitext(os.path.basename(filename))[0]
    out = []
    for t in re.split(r"[\s\-_]+", base.lower()):
        t = t.strip(".")
        if not t or t in FILE_STOP or NOISE_RE.match(t) or not re.search(r"[a-z]", t):
            continue
        if re.match(r"^\d{1,2}\.\d{1,2}$", t):
            continue
        out.append(t)
    return out


# ---------------------------------------------------------------- detecção
def detect(data: bytes, filename: str) -> str:
    name = filename.lower()
    if name.endswith((".xls", ".xlsx")):
        try:
            quantstudio.read_results(data, filename)
            return "quantstudio"
        except Exception:  # noqa: BLE001
            return "generico"
    head = _text(data)[:4000].lower()
    if "analysed data export" in head or ("no.;color;name" in head.replace('"', "").replace(" ", "")):
        return "rotorgene"
    if "sample name" in head and ("target name" in head or "target" in head):
        return "quantstudio"
    return "generico"


# ---------------------------------------------------------------- Rotor-Gene
def parse_rotorgene(data: bytes, filename: str):
    """Devolve (poços, blocos, avisos). Poços: Poço, Nome, Ct, Comentário, Bloco, Branco, Código."""
    rows = _split_lines(_text(data))
    hdr = next((i for i, r in enumerate(rows) if len(r) > 4 and r[0].lower().startswith("no.")
                and any(c.lower() == "name" for c in r) and any(c.lower() == "ct" for c in r)), None)
    if hdr is None:
        raise ValueError("Não encontrei a tabela (No., Name, Ct) do Rotor-Gene no arquivo.")
    cols = [c.lower() for c in rows[hdr]]
    i_no, i_name, i_ct = cols.index("no."), cols.index("name"), cols.index("ct")
    i_com = cols.index("ct comment") if "ct comment" in cols else None
    wells = []
    for r in rows[hdr + 1:]:
        if len(r) <= i_ct or not r[i_no].strip():
            if wells and not any(c.strip() for c in r):
                # linha em branco depois dos dados: fim da tabela (pode haver outra seção depois)
                if len(wells) > 0:
                    break
            continue
        if not re.match(r"^\d+$", r[i_no].strip()):
            break
        com = r[i_com] if i_com is not None and len(r) > i_com else ""
        wells.append({"Poço": int(r[i_no]), "Nome": r[i_name], "Ct": to_ct(r[i_ct]), "Comentário": com})
    w = pd.DataFrame(wells)
    if w.empty:
        raise ValueError("A tabela do Rotor-Gene está vazia.")
    w["Branco"] = w["Nome"].apply(is_blank_name)

    # blocos: um bloco termina no(s) branco(s); poços depois do último branco formam o último bloco
    bloco, prev_blank, ids = 1, False, []
    for b in w["Branco"]:
        if prev_blank and not b:
            bloco += 1
        ids.append(bloco)
        prev_blank = b
    w["Bloco"] = ids

    # código da amostra: token tipo "a1" que VARIA dentro do bloco. Se o mesmo token se repete em todos os
    # poços do bloco (ex.: sox2, adh5, tp53), ele é o gene, não a amostra.
    codes, block_codes = [""] * len(w), {}
    for b, sub in w.groupby("Bloco"):
        nb = sub[~sub["Branco"]]
        tl = [set(tokens(n)) for n in nb["Nome"]]
        const = set.intersection(*tl) if tl else set()
        found = set()
        for idx in nb.index:
            c = next((t for t in tokens(w.at[idx, "Nome"]) if CODE_RE.match(t) and t not in const), "")
            codes[w.index.get_loc(idx)] = c.upper()
            if c:
                found.add(c)
        block_codes[b] = found
    w["Código"] = codes

    # sugestão de gene por bloco: palavras do nome que não são código, branco ou ruído (dpf, µg/mL, datas),
    # tirando as que aparecem na maioria dos blocos (ex.: "fasd", "15dpf")
    tok_sets = {}
    for b, sub in w.groupby("Bloco"):
        tok_sets[b] = {t for n in sub["Nome"] for t in tokens(n)
                       if not (BLANK_RE.match(t) or NOISE_RE.match(t) or t in block_codes[b])}
    n_blk = len(tok_sets)
    cnt = {}
    for s in tok_sets.values():
        for t in s:
            cnt[t] = cnt.get(t, 0) + 1
    common = {t for t, c in cnt.items() if n_blk > 1 and c >= max(2, -(-n_blk // 2))}
    ftoks = file_gene_tokens(filename)
    blocks, fi, avisos = [], 0, []
    for b, sub in w.groupby("Bloco"):
        cand = sorted(tok_sets[b] - common, key=lambda t: -sum(t in tokens(n) for n in sub["Nome"]))
        nomes = list(dict.fromkeys(sub["Nome"]))
        gene, usar, obs = "", True, ""
        if len(cand) == 1:
            gene = cand[0]
            longer = [f for f in ftoks if f.startswith(gene) and f != gene]
            gene = longer[0] if longer else gene
        elif len(cand) == 0:
            if fi < len(ftoks):
                gene, obs = ftoks[fi], "gene sugerido pelo nome do arquivo"
                fi += 1
            else:
                usar, obs = False, "não consegui identificar o gene – informe"
        else:
            usar, obs = False, "nomes misturados (" + ", ".join(cand[:4]) + ") – confira ou deixe desmarcado"
        n_amostra = int((~sub["Branco"]).sum())
        tem_cod = n_amostra > 0 and (sub.loc[~sub["Branco"], "Código"] != "").all()
        blocks.append({"Bloco": b, "Poços": f"{sub['Poço'].min()}–{sub['Poço'].max()}",
                       "Nomes no arquivo": "; ".join(nomes[:3]) + ("…" if len(nomes) > 3 else ""),
                       "Gene": gene, "Usar": usar, "Amostras com código": bool(tem_cod), "Observação": obs})
    blk = pd.DataFrame(blocks)
    if not blk["Amostras com código"].all():
        avisos.append("Alguns blocos não têm o código da amostra no nome do poço: informe a lista de amostras "
                      "na ordem dos poços.")
    neg = w["Comentário"].fillna("").str.contains("NEG", case=False)
    if neg.any():
        avisos.append(f"{int(neg.sum())} poço(s) marcados como NEG pelo Rotor-Gene foram considerados sem Ct.")
    return w, blk, avisos


def build_rotorgene_raw(wells: pd.DataFrame, blocks: pd.DataFrame, sample_list=None, reps=2,
                        arquivo="") -> pd.DataFrame:
    """Monta a tabela padrão (Poço, Amostra, Gene, Ct, Omitir) a partir dos blocos conferidos pelo usuário."""
    sample_list = [s.strip() for s in (sample_list or []) if str(s).strip()]
    out = []
    for _, blk in blocks.iterrows():
        if not blk["Usar"] or not str(blk["Gene"]).strip():
            continue
        sub = wells[wells["Bloco"] == blk["Bloco"]]
        k = 0
        for _, r in sub.iterrows():
            if r["Branco"]:
                amostra = "BRANCO"
            elif blk["Amostras com código"]:
                amostra = r["Código"]
            else:
                idx = k // max(1, int(reps))
                amostra = sample_list[idx] if idx < len(sample_list) else f"S{idx + 1}"
                k += 1
            out.append({"Poço": f"{arquivo}#{r['Poço']}" if arquivo else str(r["Poço"]), "Amostra": amostra,
                        "Gene": str(blk["Gene"]).strip(), "Ct": r["Ct"], "Omitir": False})
    return pd.DataFrame(out, columns=RAW_COLS)


# ---------------------------------------------------------------- genérico
SAMPLE_KEYS = ("amostra", "sample", "sample name", "nome", "name", "id")
GENE_KEYS = ("gene", "target", "target name", "alvo")
CT_KEYS = ("ct", "cq", "cт", "crt")
GROUP_KEYS = ("grupo", "grupos", "group", "tratamento")


def _tables(data: bytes, filename: str):
    if filename.lower().endswith((".xls", ".xlsx")):
        engine = "xlrd" if filename.lower().endswith(".xls") else "openpyxl"
        for _, df in pd.read_excel(io.BytesIO(data), sheet_name=None, header=None, engine=engine).items():
            yield df
    else:
        rows = _split_lines(_text(data))
        width = max((len(r) for r in rows), default=0)
        yield pd.DataFrame([r + [None] * (width - len(r)) for r in rows])


def parse_generic(data: bytes, filename: str):
    """Tabela longa (Amostra, Gene, Ct) ou larga (Amostra/Grupo + uma coluna por gene).
    Devolve (raw, grupos ou None)."""
    for df in _tables(data, filename):
        for i in range(min(len(df), 60)):
            hdr = [str(x).strip() if x is not None and not pd.isna(x) else "" for x in df.iloc[i].tolist()]
            low = [h.lower() for h in hdr]
            s_col = next((j for j, h in enumerate(low) if h in SAMPLE_KEYS), None)
            g_col = next((j for j, h in enumerate(low) if h in GENE_KEYS), None)
            c_col = next((j for j, h in enumerate(low) if h in CT_KEYS), None)
            grp_col = next((j for j, h in enumerate(low) if h in GROUP_KEYS), None)
            body = df.iloc[i + 1:]
            if s_col is not None and g_col is not None and c_col is not None:  # longa
                raw = pd.DataFrame({"Poço": [str(k + 1) for k in range(len(body))],
                                    "Amostra": body.iloc[:, s_col].astype(str).str.strip().values,
                                    "Gene": body.iloc[:, g_col].astype(str).str.strip().values,
                                    "Ct": [to_ct(v) for v in body.iloc[:, c_col]], "Omitir": False})
                raw = raw[(raw["Amostra"] != "") & (raw["Amostra"].str.lower() != "nan")]
                return raw.reset_index(drop=True), None
            anchor = s_col if s_col is not None else grp_col
            if anchor is None:
                continue
            gene_cols = []
            for j in range(anchor + 1, len(hdr)):
                if hdr[j] == "":
                    break
                if j in (s_col, grp_col):
                    continue
                vals = [to_ct(v) for v in body.iloc[:, j]]
                if sum(not pd.isna(v) for v in vals) >= 2:
                    gene_cols.append(j)
            if not gene_cols:
                continue
            body = body[body.iloc[:, anchor].notna() & (body.iloc[:, anchor].astype(str).str.strip() != "")]
            if s_col is not None:
                samples = body.iloc[:, s_col].astype(str).str.strip().tolist()
            else:
                first = body.iloc[:, 0].tolist() if anchor != 0 else list(range(1, len(body) + 1))
                samples = [str(int(v)) if isinstance(v, (int, float)) and not pd.isna(v) else str(k + 1)
                           for k, v in enumerate(first)]
            rows, grupos = [], []
            for r_i, s in enumerate(samples):
                if grp_col is not None:
                    grupos.append({"Amostra": s, "Grupo": str(body.iloc[r_i, grp_col]).strip()})
                for j in gene_cols:
                    rows.append({"Poço": f"{r_i + 1}", "Amostra": s, "Gene": hdr[j],
                                 "Ct": to_ct(body.iloc[r_i, j]), "Omitir": False})
            g = pd.DataFrame(grupos).drop_duplicates("Amostra") if grupos else None
            return pd.DataFrame(rows, columns=RAW_COLS), g
    raise ValueError("Não reconheci o formato. Use a exportação do QuantStudio, do Rotor-Gene ou uma tabela com "
                     "as colunas Amostra, Gene e Ct.")


# ---------------------------------------------------------------- entrada única
def read_file(data: bytes, filename: str) -> dict:
    """Lê um arquivo e devolve {'formato', 'raw' (ou None se precisar de conferência), 'poços', 'blocos',
    'grupos', 'avisos'}."""
    fmt = detect(data, filename)
    if fmt == "quantstudio":
        return {"formato": "QuantStudio", "raw": quantstudio.read_results(data, filename), "poços": None,
                "blocos": None, "grupos": None, "avisos": []}
    if fmt == "rotorgene":
        w, b, avisos = parse_rotorgene(data, filename)
        return {"formato": "Rotor-Gene Q", "raw": None, "poços": w, "blocos": b, "grupos": None,
                "avisos": avisos}
    raw, grupos = parse_generic(data, filename)
    return {"formato": "Tabela genérica", "raw": raw, "poços": None, "blocos": None, "grupos": grupos,
            "avisos": []}

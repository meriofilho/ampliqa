"""Planejamento: cronograma do experimento, mensagem para WhatsApp e eventos para o Google Agenda.

Nada é enviado pelo app: a pessoa copia a mensagem, abre o link do Google Agenda (que já vem preenchido, com os
convidados) ou importa o arquivo .ics na própria agenda.
"""
from datetime import date, datetime, timedelta, timezone
from urllib.parse import quote, urlencode

import pandas as pd

COLS = ["Data", "Etapa", "Detalhes", "Observação", "Responsável", "Convidados"]

DIAS = {"pt": ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"],
        "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}

# etapas sugeridas (pt, en), seguindo os POPs de Biologia Molecular
STEPS = {
    "extracao": ("Extração de RNA (PO.OPE.01)", "RNA extraction (PO.OPE.01)"),
    "quant_cdna": ("Quantificação no NanoDrop e síntese de cDNA (PO.OPE.01 e 02)",
                   "NanoDrop quantification and cDNA synthesis (PO.OPE.01 and 02)"),
    "eficiencia": ("Curva de eficiência dos primers (PO.OPE.04)", "Primer efficiency curve (PO.OPE.04)"),
    "qpcr": ("qPCR das amostras do estudo (PO.OPE.03)", "qPCR of the study samples (PO.OPE.03)"),
    "repeticao": ("qPCR – amostras que precisarem repetir e finalização",
                  "qPCR – samples that need repeating and wrap-up"),
    "analise": ("Análise dos resultados e gráficos (AmpliQA)", "Analysis of results and charts (AmpliQA)"),
}
REPEAT_NOTE = ("*dependendo dos resultados anteriores, esse dia pode ser dispensado",
               "*depending on the previous results, this day may be skipped")


def empty() -> pd.DataFrame:
    df = pd.DataFrame({c: pd.Series(dtype="object") for c in COLS})
    df["Data"] = pd.Series(dtype="datetime64[ns]")
    return df


def normalize(df) -> pd.DataFrame:
    if df is None or not len(df):
        return empty()
    d = df.reindex(columns=COLS).copy()
    d["Data"] = pd.to_datetime(d["Data"], errors="coerce", dayfirst=True)
    for c in COLS[1:]:
        d[c] = d[c].fillna("").astype(str).replace("nan", "")
    return d.reset_index(drop=True)


def _workday(d: date, n: int) -> date:
    """n dias úteis depois de d (n = 0: o próprio dia, ou a próxima segunda se cair no fim de semana)."""
    while d.weekday() >= 5:
        d += timedelta(days=1)
    for _ in range(n):
        d += timedelta(days=1)
        while d.weekday() >= 5:
            d += timedelta(days=1)
    return d


def suggest(start: date, lang="pt", qpcr_days=1, gap=1, efficiency=False, responsible="") -> pd.DataFrame:
    """Etapas em dias úteis: cada etapa `gap` dias úteis depois da anterior; a repetição de qPCR fica 2 dias
    úteis depois do último dia de qPCR e a análise, 2 dias úteis depois da repetição."""
    i = 0 if lang == "pt" else 1
    rows, d = [], _workday(start, 0)

    def add(key, day, details="", note=""):
        rows.append({"Data": pd.Timestamp(day), "Etapa": STEPS[key][i], "Detalhes": details, "Observação": note,
                     "Responsável": responsible, "Convidados": ""})

    add("extracao", d)
    d = _workday(d, gap)
    add("quant_cdna", d)
    if efficiency:
        d = _workday(d, gap)
        add("eficiencia", d)
    for k in range(max(1, int(qpcr_days))):
        d = _workday(d, gap)
        add("qpcr", d, (f"placa {k + 1}" if lang == "pt" else f"plate {k + 1}") if qpcr_days > 1 else "")
    d = _workday(d, 2)
    add("repeticao", d, note=REPEAT_NOTE[i])
    d = _workday(d, 2)
    add("analise", d)
    return normalize(pd.DataFrame(rows))


def _rows(df):
    d = normalize(df).dropna(subset=["Data"])
    d = d[d["Etapa"].str.strip() != ""]
    return d.sort_values("Data", kind="stable")


def whatsapp(df, experiment="", lang="pt") -> str:
    """Mensagem no formato usado no laboratório (um bloco por dia)."""
    lines = []
    if experiment:
        lines += [f"🧬 *{experiment}* – " + ("cronograma" if lang == "pt" else "schedule"), ""]
    rows = _rows(df)
    for day, sub in rows.groupby(rows["Data"].dt.date, sort=True):
        lines.append(f"📅 {day:%d/%m} - {DIAS[lang][day.weekday()]}")
        for _, r in sub.iterrows():
            text = r["Etapa"] + (f" ({r['Detalhes']})" if r["Detalhes"] else "")
            if r["Responsável"]:
                text += f" – {r['Responsável']}"
            lines.append(text)
            if r["Observação"]:
                note = r["Observação"]
                lines.append(note if note.startswith("*") else f"*{note}")
        lines.append("")
    return "\n".join(lines).strip()


def whatsapp_link(text: str) -> str:
    return "https://wa.me/?text=" + quote(text)


def _emails(s) -> list:
    return [e.strip() for e in str(s or "").replace(";", ",").split(",") if "@" in e]


def _description(r, experiment):
    parts = [p for p in (r["Detalhes"], r["Observação"]) if p]
    if r["Responsável"]:
        parts.append(f"Responsável / researcher: {r['Responsável']}")
    if experiment:
        parts.append(f"Experimento / experiment: {experiment}")
    parts.append("AmpliQA – https://ampliqpcr.streamlit.app/")
    return "\n".join(parts)


def google_links(df, experiment="") -> list:
    """[(data, etapa, link)] – link do Google Agenda já preenchido (evento de dia inteiro, com convidados)."""
    out = []
    for _, r in _rows(df).iterrows():
        d0 = r["Data"].date()
        params = {"action": "TEMPLATE", "text": f"{r['Etapa']}" + (f" – {experiment}" if experiment else ""),
                  "dates": f"{d0:%Y%m%d}/{d0 + timedelta(days=1):%Y%m%d}", "details": _description(r, experiment)}
        guests = _emails(r["Convidados"])
        if guests:
            params["add"] = ",".join(guests)
        out.append((d0, r["Etapa"], "https://calendar.google.com/calendar/render?" + urlencode(params, quote_via=quote)))
    return out


def _ics_text(s: str) -> str:
    return str(s).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def ics(df, experiment="") -> bytes:
    """Arquivo .ics com todas as etapas (importável no Google Agenda, Outlook e Apple Calendar)."""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//AmpliQA//Cronograma//PT", "CALSCALE:GREGORIAN"]
    for i, (_, r) in enumerate(_rows(df).iterrows()):
        d0 = r["Data"].date()
        lines += ["BEGIN:VEVENT", f"UID:{d0:%Y%m%d}-{i}-{abs(hash((r['Etapa'], experiment)))}@ampliqa",
                  f"DTSTAMP:{stamp}", f"DTSTART;VALUE=DATE:{d0:%Y%m%d}",
                  f"DTEND;VALUE=DATE:{d0 + timedelta(days=1):%Y%m%d}",
                  "SUMMARY:" + _ics_text(r["Etapa"] + (f" – {experiment}" if experiment else "")),
                  "DESCRIPTION:" + _ics_text(_description(r, experiment))]
        lines += [f"ATTENDEE;ROLE=REQ-PARTICIPANT:mailto:{e}" for e in _emails(r["Convidados"])]
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    return ("\r\n".join(lines) + "\r\n").encode("utf-8")

"""Central de ajuda (sem IA): perguntas frequentes com causa e solução + diagnóstico do experimento aberto."""
import re
import unicodedata

import numpy as np
import pandas as pd

from .i18n import FAQ_EN, faq as loc, num, t

FAQ = [
    {"id": "conc_baixa", "titulo": "RNA com concentração insuficiente para o cDNA",
     "palavras": "concentração baixa insuficiente rna pouco 62,5 cdna nanodrop rendimento",
     "causa": "Com 500 ng em 8 µL, o RNA precisa ter pelo menos 62,5 ng/µL. Pouco tecido, lise incompleta, eluição "
              "em volume grande ou perda na coluna reduzem a concentração.",
     "solucao": "1) Concentre a amostra (speed-vac sem aquecimento) e requantifique. 2) Se não der, reextraia com "
                "mais tecido (até 30 mg) ou reaplique o eluato na 2ª eluição. 3) Só em último caso, reduza a massa de "
                "RNA de TODAS as amostras do experimento para o mesmo valor.",
     "pop": "PO.OPE.01BIOMOL (5.8) e PO.OPE.02BIOMOL (5.5)"},
    {"id": "a230", "titulo": "A260/230 baixo (resíduo de guanidina ou etanol)",
     "palavras": "260/230 230 guanidina etanol pureza sal contaminação",
     "causa": "Sal de guanidina (tampões RLT/RW1) ou etanol carregados para o eluato.",
     "solucao": "Faça a centrifugação de secagem da coluna (1 min, velocidade máxima) e não encoste a coluna no "
                "flow-through. Entre 1,5 e 1,8 a amostra pode ser usada com ressalva; abaixo de 1,5, reextraia.",
     "pop": "PO.OPE.01BIOMOL (5.7 e 5.9)"},
    {"id": "a280", "titulo": "A260/280 fora de 1,8–2,1",
     "palavras": "260/280 280 proteína fenol pureza",
     "causa": "Proteína ou fenol residual, geralmente por lise ou homogeneização incompleta.",
     "solucao": "Reextraia garantindo lise completa (sonicação no gelo, 2–3 ciclos) e não exceda 30 mg de tecido.",
     "pop": "PO.OPE.01BIOMOL (5.5)"},
    {"id": "diluir", "titulo": "Volume de RNA menor que 1 µL",
     "palavras": "volume pequeno diluir rna concentrado 1 µl pipetar",
     "causa": "RNA muito concentrado: 500 ng cabem em menos de 1 µL, volume impreciso de pipetar.",
     "solucao": "Dilua uma alíquota do RNA (ex.: 1:5) em água DEPC, requantifique (ou calcule pela diluição) e "
                "pipete a partir da diluição.",
     "pop": "PO.OPE.02BIOMOL (5.4)"},
    {"id": "branco", "titulo": "Branco (NTC ou BcDNA) amplificou",
     "palavras": "branco ntc bcdna contaminação amplificou ct branco dímero",
     "causa": "Contaminação de reagentes, água, ponteiras ou bancada com DNA/produtos de PCR; ou dímero de primers "
              "(pico de melting em temperatura menor que a do produto).",
     "solucao": "1) Compare a curva de melting do branco com a das amostras: pico diferente e Ct alto (> 35) indicam "
                "dímero, aceitável. 2) Se o pico é igual ao do produto, descarte as alíquotas de água, primers e mix "
                "usadas e repita o gene. 3) Nunca abra placas já amplificadas no laboratório de preparo.",
     "pop": "PO.OPE.03BIOMOL (5.2 e 5.8)"},
    {"id": "replicas", "titulo": "Réplicas técnicas com diferença maior que 0,5 Ct",
     "palavras": "réplicas duplicata diferença discrepante 0,5 ct variação pipetagem",
     "causa": "Erro de pipetagem (principalmente do cDNA, 1 µL), bolhas, poço mal vedado, mistura insuficiente ou "
              "Ct alto (> 32), onde a variação é naturalmente maior.",
     "solucao": "Confira as curvas dos dois poços no Design & Analysis. Se um poço tem problema técnico evidente, "
                "marque Omitir na aba de importação e registre o motivo; se não, repita a amostra no gene. Com "
                "triplicatas, o app pode remover a réplica discrepante automaticamente (critério do Auto-qPCR). Para "
                "genes de Ct muito alto, considere usar mais cDNA.",
     "pop": "PO.OPE.03BIOMOL (5.6 e 5.8)"},
    {"id": "nd", "titulo": "Amostra sem amplificação (Undetermined / ND)",
     "palavras": "undetermined nd sem amplificação não amplificou ct ausente neg",
     "causa": "Transcrito muito pouco expresso, falha na síntese de cDNA, cDNA esquecido no poço ou primer ruim.",
     "solucao": "Confira se o gene de referência amplificou na mesma amostra (se não, o problema é o cDNA). Se só "
                "esse gene falhou, verifique a eficiência do primer (PO.OPE.04BIOMOL) e considere mais cDNA.",
     "pop": "PO.OPE.03BIOMOL e PO.OPE.04BIOMOL"},
    {"id": "ref_instavel", "titulo": "Gene de referência variando entre os grupos",
     "palavras": "referência endógeno gapdh actina instável varia normalização housekeeping genorm estabilidade",
     "causa": "O tratamento afeta a expressão do gene de referência, ou a quantidade/qualidade de RNA difere entre "
              "os grupos. Isso distorce todos os fold changes do grupo afetado.",
     "solucao": "Diferença de Ct do gene de referência acima de ~1 entre grupos é sinal de alerta. Confira a "
                "quantificação do RNA desse grupo, valide outro gene de referência (ex.: ef1a, rpl13a) e, de "
                "preferência, selecione 2 ou mais genes de referência no app: ele normaliza pela média geométrica e "
                "mostra o geNorm M e o CV (MIQE).",
     "pop": "PO.OPE.03BIOMOL (5.4)"},
    {"id": "fc_extremo", "titulo": "Fold change muito alto ou muito baixo",
     "palavras": "fold change alto extremo 10 13 muito grande estranho",
     "causa": "Pode ser biológico, mas é frequente vir de gene de referência instável, Ct muito alto do alvo "
              "(perto de 35), poucas réplicas ou erro de identificação de amostras.",
     "solucao": "Confira o Ct do gene de referência nessas amostras, as réplicas técnicas e o mapa da placa antes "
                "de interpretar.",
     "pop": "PO.OPE.03BIOMOL"},
    {"id": "n_baixo", "titulo": "Grupo com menos de 3 réplicas biológicas",
     "palavras": "n baixo réplicas biológicas pools poucas amostra perdida",
     "causa": "Amostra perdida, excluída ou com falha de amplificação.",
     "solucao": "Com n < 3 a estatística é pouco confiável e grupos com n = 1 ficam fora dos testes. Planeje pelo "
                "menos 3 pools por grupo e, se possível, um pool extra de reserva.",
     "pop": "PO.OPE.01BIOMOL (5.3)"},
    {"id": "grupos", "titulo": "Grupos não reconhecidos (amostras S1, S2…)",
     "palavras": "grupos s1 s2 amostra nome código rotor-gene lista",
     "causa": "O arquivo do Rotor-Gene não trazia o código da amostra no nome do poço e a lista de amostras não foi "
              "preenchida.",
     "solucao": "Na aba Importar corrida, preencha a lista de amostras na ordem dos poços. Nas próximas corridas, "
                "nomeie cada poço com o código da amostra (a1, a2…).",
     "pop": "—"},
    {"id": "normalidade", "titulo": "Dados sem normalidade ou com variâncias diferentes",
     "palavras": "normalidade shapiro levene variância kruskal welch não paramétrico premissa",
     "causa": "Distribuição assimétrica, outlier ou variâncias desiguais entre grupos.",
     "solucao": "O app escolhe o teste adequado (Welch com Games-Howell para variâncias diferentes; Kruskal-Wallis com "
                "Dunn para falta de normalidade) e explica o motivo. Faça a análise na escala ΔCt (log), que costuma "
                "resolver a assimetria do fold change. Com n = 3, os testes de premissas têm pouco poder.",
     "pop": "—"},
    {"id": "outlier", "titulo": "Possível outlier: excluir ou não?",
     "palavras": "outlier grubbs rout excluir amostra discrepante fora da curva",
     "causa": "Um valor muito afastado dos demais do grupo.",
     "solucao": "Não exclua só porque o valor atrapalha. Confira réplicas técnicas, melting, brancos, qualidade do "
                "RNA e o Ct do gene de referência dessa amostra, e anotações da coleta. Exclua apenas com justificativa "
                "técnica e informe a exclusão nos métodos.",
     "pop": "—"},
    {"id": "eficiencia", "titulo": "Eficiência do primer fora de 90–110%",
     "palavras": "eficiência primer slope curva padrão r2 r² 90 110",
     "causa": "Diluições imprecisas, inibição em pontos concentrados, primer com dímero ou fora da faixa linear.",
     "solucao": "Refaça a diluição seriada com ponteira nova a cada ponto, exclua pontos fora da faixa linear (Ct > 35 "
                "ou platô) e, se persistir, ajuste a concentração do primer ou desenhe novo par. Informe a eficiência "
                "de cada gene no app (aba Grupos) para corrigir o cálculo.",
     "pop": "PO.OPE.04BIOMOL"},
    {"id": "arquivo", "titulo": "O app não reconheceu meu arquivo de resultados",
     "palavras": "arquivo erro upload não reconheci formato csv xls quantstudio rotor",
     "causa": "Formato diferente do esperado (ex.: exportação de outra aba ou de outro software).",
     "solucao": "QuantStudio: exporte em Results → Export (.xls). Rotor-Gene: use 'Excel Analysed Data Export' (.csv). "
                "Outros: monte uma tabela com as colunas Amostra, Gene e Ct.",
     "pop": "—"},
]


# Referências oficiais (DOIs conferidos na Crossref em 27/10/2026)
REFS = {
    "miqe2009": ("Bustin SA et al. (2009) The MIQE guidelines: minimum information for publication of quantitative "
                 "real-time PCR experiments. Clinical Chemistry 55:611–622.", "10.1373/clinchem.2008.112797"),
    "miqe2025": ("Bustin SA et al. (2025) MIQE 2.0: revision of the minimum information for publication of quantitative "
                 "real-time PCR experiments guidelines. Clinical Chemistry 71:634–651.", "10.1093/clinchem/hvaf043"),
    "taylor2019": ("Taylor SC et al. (2019) The ultimate qPCR experiment: producing publication quality, reproducible "
                   "data the first time. Trends in Biotechnology 37:761–774.", "10.1016/j.tibtech.2018.12.002"),
    "livak2001": ("Livak KJ, Schmittgen TD (2001) Analysis of relative gene expression data using real-time "
                  "quantitative PCR and the 2^−ΔΔCT method. Methods 25:402–408.", "10.1006/meth.2001.1262"),
    "schmittgen2008": ("Schmittgen TD, Livak KJ (2008) Analyzing real-time PCR data by the comparative CT method. "
                       "Nature Protocols 3:1101–1108.", "10.1038/nprot.2008.73"),
    "pfaffl2001": ("Pfaffl MW (2001) A new mathematical model for relative quantification in real-time RT-PCR. "
                   "Nucleic Acids Research 29:e45.", "10.1093/nar/29.9.e45"),
    "vandesompele2002": ("Vandesompele J et al. (2002) Accurate normalization of real-time quantitative RT-PCR data by "
                         "geometric averaging of multiple internal control genes. Genome Biology 3:research0034.",
                         "10.1186/gb-2002-3-7-research0034"),
    "hellemans2007": ("Hellemans J et al. (2007) qBase relative quantification framework and software for management "
                      "and automated analysis of real-time quantitative PCR data. Genome Biology 8:R19.",
                      "10.1186/gb-2007-8-2-r19"),
    "maussion2021": ("Maussion G et al. (2021) Auto-qPCR; a python-based web app for automated and reproducible "
                     "analysis of qPCR data. Scientific Reports 11:21293.", "10.1038/s41598-021-99727-6"),
    "kozera2013": ("Kozera B, Rapacz M (2013) Reference genes in real-time PCR. Journal of Applied Genetics 54:391–406.",
                   "10.1007/s13353-013-0173-x"),
    "yuan2006": ("Yuan JS, Reed A, Chen F, Stewart CN (2006) Statistical analysis of real-time PCR data. BMC "
                 "Bioinformatics 7:85.", "10.1186/1471-2105-7-85"),
    "rieu2009": ("Rieu I, Powers SJ (2009) Real-time quantitative RT-PCR: design, calculations, and statistics. The "
                 "Plant Cell 21:1031–1033.", "10.1105/tpc.109.066001"),
    "nolan2006": ("Nolan T, Hands RE, Bustin SA (2006) Quantification of mRNA using real-time RT-PCR. Nature Protocols "
                  "1:1559–1582.", "10.1038/nprot.2006.236"),
    "fleige2006": ("Fleige S, Pfaffl MW (2006) RNA integrity and the effect on the real-time qRT-PCR performance. "
                   "Molecular Aspects of Medicine 27:126–139.", "10.1016/j.mam.2005.12.003"),
    "ruiz2017": ("Ruiz-Villalba A et al. (2017) Amplification of nonspecific products in quantitative polymerase chain "
                 "reactions (qPCR). Biomolecular Detection and Quantification 14:7–18.", "10.1016/j.bdq.2017.10.001"),
    "shapiro1965": ("Shapiro SS, Wilk MB (1965) An analysis of variance test for normality (complete samples). "
                    "Biometrika 52:591–611.", "10.1093/biomet/52.3-4.591"),
    "brown1974": ("Brown MB, Forsythe AB (1974) Robust tests for the equality of variances. Journal of the American "
                  "Statistical Association 69:364–367.", "10.1080/01621459.1974.10482955"),
    "welch1951": ("Welch BL (1951) On the comparison of several mean values: an alternative approach. Biometrika "
                  "38:330–336.", "10.1093/biomet/38.3-4.330"),
    "kruskal1952": ("Kruskal WH, Wallis WA (1952) Use of ranks in one-criterion variance analysis. Journal of the "
                    "American Statistical Association 47:583–621.", "10.1080/01621459.1952.10483441"),
    "dunnett1955": ("Dunnett CW (1955) A multiple comparison procedure for comparing several treatments with a "
                    "control. Journal of the American Statistical Association 50:1096–1121.",
                    "10.1080/01621459.1955.10501294"),
    "games1976": ("Games PA, Howell JF (1976) Pairwise multiple comparison procedures with unequal n's and/or "
                  "variances: a Monte Carlo study. Journal of Educational Statistics 1:113–125.",
                  "10.3102/10769986001002113"),
    "dunn1964": ("Dunn OJ (1964) Multiple comparisons using rank sums. Technometrics 6:241–252.",
                 "10.1080/00401706.1964.10490181"),
    "grubbs1969": ("Grubbs FE (1969) Procedures for detecting outlying observations in samples. Technometrics 11:1–21.",
                   "10.1080/00401706.1969.10490657"),
}

REF_GROUPS = {
    "Diretrizes de qPCR": ["miqe2009", "miqe2025", "taylor2019"],
    "Cálculo da expressão relativa": ["livak2001", "schmittgen2008", "pfaffl2001", "hellemans2007"],
    "Genes de referência": ["vandesompele2002", "kozera2013", "hellemans2007"],
    "Ferramentas de análise automatizada": ["hellemans2007", "maussion2021"],
    "Estatística de dados de qPCR": ["yuan2006", "rieu2009"],
    "Qualidade do RNA e especificidade": ["nolan2006", "fleige2006", "ruiz2017"],
    "Testes estatísticos usados no app": ["shapiro1965", "brown1974", "welch1951", "kruskal1952", "dunnett1955",
                                          "games1976", "dunn1964", "grubbs1969"],
}

# POPs do laboratório (pasta do Drive do Fishlab)
POP_LINKS = {
    "PO.OPE.01BIOMOL": "https://drive.google.com/file/d/11mgYLHMhyfG6WOQZ43DW5w02DI_zltsa/view",
    "PO.OPE.02BIOMOL": "https://drive.google.com/file/d/1YHO0TvQ9WIeKX4CFFlO05XrWBM-fwv7H/view",
    "PO.OPE.03BIOMOL": "https://drive.google.com/file/d/1ZmKQy3helHQh8BvVXeGHJ60oYBciZNOV/view",
    "PO.OPE.04BIOMOL": "https://drive.google.com/file/d/1zL1n0C9N5r1crJnKBjqxTNycfNUXjTnq/view",
}
POP_FOLDER = "https://drive.google.com/drive/folders/1VZZwY7NadZiZ21ey0N4yu9442MvZP_FE"

FAQ_REFS = {
    "conc_baixa": ["nolan2006", "fleige2006"], "a230": ["nolan2006"], "a280": ["nolan2006", "fleige2006"],
    "branco": ["miqe2009", "ruiz2017"], "replicas": ["taylor2019", "miqe2025", "maussion2021"], "nd": ["miqe2009", "ruiz2017"],
    "ref_instavel": ["vandesompele2002", "hellemans2007", "kozera2013", "miqe2025"], "fc_extremo": ["livak2001", "vandesompele2002"],
    "n_baixo": ["taylor2019", "miqe2025"],
    "normalidade": ["yuan2006", "rieu2009", "shapiro1965", "brown1974", "welch1951", "kruskal1952"],
    "outlier": ["grubbs1969", "taylor2019"], "eficiencia": ["pfaffl2001", "schmittgen2008", "miqe2009"],
    "escala": ["yuan2006", "rieu2009", "livak2001", "schmittgen2008"],
    "posthoc": ["dunnett1955", "games1976", "dunn1964"],
}

FAQ += [
    {"id": "escala", "titulo": "Por que a estatística é feita no ΔCt e não no fold change?",
     "palavras": "escala log delta ct fold change estatística anova assimétrico log2 2^-ddct",
     "causa": "O fold change (2^−ΔΔCt) é assimétrico: reduções ficam entre 0 e 1 e aumentos vão de 1 ao infinito, e "
              "a variância cresce com a média. O Ct/ΔCt é a medida que o tratamento afeta diretamente e tem "
              "distribuição mais próxima da normal.",
     "solucao": "O app testa o ΔCt de cada réplica biológica (mesmos p-valores do log2 fold change) e mostra o fold "
                "change nos gráficos e no texto. Testar o fold change diretamente fica disponível só para comparar "
                "com análises antigas.",
     "pop": "PO.OPE.03BIOMOL"},
    {"id": "posthoc", "titulo": "Dunnett, Tukey, Games-Howell ou Dunn: qual post hoc usar?",
     "palavras": "post hoc dunnett tukey games howell dunn comparações múltiplas qual teste",
     "causa": "Cada post hoc responde a uma pergunta e tem premissas diferentes.",
     "solucao": "Dunnett: cada grupo contra o controle (mais poder quando essa é a pergunta). Tukey: todos os pares, "
                "com variâncias semelhantes. Games-Howell: todos os pares quando as variâncias são diferentes (após "
                "ANOVA de Welch). Dunn com correção de Holm: depois do Kruskal-Wallis (não paramétrico). O app sugere "
                "o adequado e explica o motivo na tela Estatística e figuras.",
     "pop": "—"},
]


def doi_link(doi):
    return f"https://doi.org/{doi}"


def ref_line(key):
    text, doi = REFS[key]
    return f"{text} [doi:{doi}]({doi_link(doi)})"


def refs_markdown(eid):
    return "\n".join(f"- {ref_line(k)}" for k in FAQ_REFS.get(eid, []))


def pop_markdown(text):
    """Troca os códigos de POP pelo link do PDF no Drive do laboratório."""
    out = str(text)
    for code, url in POP_LINKS.items():
        out = out.replace(code, f"[{code}]({url})")
    return out


def entry_markdown(e):
    e = loc(e)
    md = (f"**{t('Por quê')}:** {e['causa']}\n\n**{t('O que fazer')}:** {e['solucao']}\n\n"
          f"*POP: {pop_markdown(e['pop'])}*")
    r = refs_markdown(e["id"])
    return md + (f"\n\n**{t('Referências')}:**\n{r}" if r else "")


def _norm(s):
    s = unicodedata.normalize("NFKD", str(s).lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def search(query, k=6):
    """Busca por palavras nas perguntas em português e em inglês."""
    q = [w for w in re.split(r"\W+", _norm(query)) if len(w) > 1]
    if not q:
        return []
    scored = []
    for e in FAQ:
        en = FAQ_EN.get(e["id"], {})
        key = _norm(" ".join([e["titulo"], e["palavras"], en.get("titulo", ""), en.get("palavras", "")]))
        text = key + " " + _norm(" ".join([e["causa"], e["solucao"], en.get("causa", ""), en.get("solucao", "")]))
        score = sum(3 if w in key else 1 for w in q if w in text)
        if score:
            scored.append((score, e))
    return [e for _, e in sorted(scored, key=lambda x: -x[0])[:k]]


def entry(eid):
    return next(e for e in FAQ if e["id"] == eid)


def diagnose(exp, results: dict) -> list:
    """Lista de (id da FAQ, detalhe concreto do experimento aberto)."""
    out = []
    q = results.get("quant")
    if q is not None and len(q):
        for code, sit in zip(q["Código"], q["Situação"]):
            if str(sit).startswith("Não usar"):
                out.append(("conc_baixa", t("Amostra {c}: concentração abaixo do mínimo.", c=code)))
            elif str(sit).startswith("Diluir"):
                out.append(("diluir", t("Amostra {c}: volume de RNA menor que 1 µL.", c=code)))
        for code, qual in zip(q["Código"], q["Qualidade"]):
            if qual == "Fora do critério":
                out.append(("a280", t("Amostra {c}: razões de pureza fora do critério.", c=code)))
            elif str(qual).startswith("Ressalva"):
                out.append(("a230", t("Amostra {c}: A260/230 entre 1,5 e 1,8.", c=code)))
    bl = results.get("qpcr_brancos")
    if bl is not None:
        for _, r in bl[bl["Situação"].str.startswith("ATENÇÃO")].iterrows():
            out.append(("branco", t("Gene {g}: branco com Ct {ct}.", g=r["Gene"], ct=num(r["Menor Ct"], 2))))
    fl = results.get("qpcr_alertas")
    if fl is not None and len(fl):
        rep = fl[fl["Alerta"].str.startswith("Diferença")]
        if len(rep):
            out.append(("replicas", t("{n} amostra(s)×gene com réplicas discrepantes (ex.: {a} / {g}).", n=len(rep),
                                      a=rep.iloc[0]["Amostra"], g=rep.iloc[0]["Gene"])))
        nd = fl[fl["Alerta"].str.startswith("Nenhuma")]
        for _, r in nd.head(5).iterrows():
            out.append(("nd", t("{a} / {g}: nenhuma réplica amplificou.", a=r["Amostra"], g=r["Gene"])))
    res = results.get("qpcr")
    cfg = exp.get("qpcr_cfg", {})
    if res is not None and len(res):
        from .qpcr import ref_list
        refs = ref_list(cfg.get("ref"))
        for rg in refs:
            ref = res[res["Gene"] == rg]
            if len(ref):
                m = ref.groupby("Grupo")["Ct médio"].mean()
                if m.max() - m.min() > 1:
                    out.append(("ref_instavel", t("{g}: Ct médio varia {d} ciclos entre grupos (de {a} a {b}).", g=rg,
                                                  d=num(m.max() - m.min(), 1), a=m.idxmin(), b=m.idxmax())))
        est = results.get("qpcr_estabilidade")
        if est is not None and len(est):
            for _, r in est[est["Avaliação"].str.startswith("Instável")].iterrows():
                out.append(("ref_instavel", t("{g}: geNorm M = {m} e CV = {cv}% (acima do limite).", g=r["Gene"],
                                              m=num(r["M (geNorm)"], 2), cv=num(r["CV (%)"], 0))))
        ext = res[(~res["Gene"].isin(refs)) & ((res["Fold change"] > 8) | (res["Fold change"] < 0.125))]
        if len(ext):
            r = ext.iloc[0]
            out.append(("fc_extremo", t("{n} valor(es) com fold change > 8 ou < 0,125 (ex.: {a} / {g} = {v}).",
                                        n=len(ext), a=r["Amostra"], g=r["Gene"], v=num(r["Fold change"], 1))))
        n = res[~res["Gene"].isin(refs)].groupby("Grupo")["Amostra"].nunique()
        small = n[n < 3]
        if len(small):
            out.append(("n_baixo", t("Grupo(s) com menos de 3 réplicas: {g}.",
                                     g=", ".join(f"{g} (n = {v})" for g, v in small.items()))))
        if res["Amostra"].astype(str).str.match(r"^S\d+$").any():
            out.append(("grupos", t("Há amostras com nome automático (S1, S2…).")))
    return out

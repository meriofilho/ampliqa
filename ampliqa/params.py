"""Valores-padrão dos POPs de Biologia Molecular (PO.OPE.01 a 04BIOMOL)."""

# Quantificação de RNA e síntese de cDNA (PO.OPE.01 e 02BIOMOL)
QUANT_DEFAULTS = {
    "massa_rna_ng": 500.0,        # ng de RNA por reação de cDNA
    "vol_rna_agua_ul": 8.0,       # µL disponíveis para RNA + H2O DEPC (20 − 10 MM − 2 EM)
    "a280_min": 1.8,
    "a280_max": 2.1,
    "a230_min": 1.8,              # aceite
    "a230_ressalva": 1.5,         # entre 1,5 e 1,8 = aceitar com ressalva
    "vol_min_ul": 1.0,            # abaixo disso, diluir o RNA antes
    "margem": 0.10,               # margem de pipetagem do mix comum
    "mm_ul": 10.0,                # NZYRT 2× Master Mix por reação
    "em_ul": 2.0,                 # NZYRT Enzyme Mix por reação
    "n_bcdna": 1,                 # brancos do cDNA
    "n_nrt": 0,                   # controles sem RT (recomendado)
}

# qPCR (PO.OPE.03BIOMOL)
QPCR_DEFAULTS = {
    "dup_max": 0.5,               # diferença máxima entre réplicas técnicas (Ct)
    "blank_lim": 35.0,            # Ct limite para brancos
    "letras_grupo": 1,            # nº de letras iniciais do código que indicam o grupo
    "brancos": ["BRANCO", "NTC", "BcDNA", "NRT"],
}

# Volumes por poço (µL) – PO.OPE.03BIOMOL
QPCR_MIX = {
    "Econômico (10 µL)": {"SYBR": 5.0, "Pf": 1.0, "Pr": 1.0, "H2O": 2.0, "cDNA": 1.0},
    "Padrão (20 µL)": {"SYBR": 10.0, "Pf": 2.0, "Pr": 2.0, "H2O": 4.0, "cDNA": 2.0},
}

FISHLAB = {
    "primaria": "#077b7b",
    "destaque": "#c7692a",
    "fundo": "#F1F1F1",
    "apoio": "#7DAEB4",
}

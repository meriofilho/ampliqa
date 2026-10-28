"""Desenho do experimento: espécie, tecido, grupos e réplicas biológicas.

Cada espécie tem sua lista de tecidos/tipos de amostra. Os rótulos em português são as chaves (o que vai para o
arquivo do experimento); as traduções em inglês e as frases usadas no texto de métodos ficam aqui.
"""
from string import ascii_uppercase

OUTRO = "Outro (digitar)"
OUTRA = "Outra (digitar)"

# espécie (rótulo pt): rótulo en, nome no texto de métodos (en, pt), tecidos
SPECIES = {
    "Zebrafish (Danio rerio)": {
        "en": "Zebrafish (Danio rerio)", "methods": ("zebrafish (Danio rerio)", "zebrafish (Danio rerio)"),
        "tecidos": ["Larva inteira", "Cérebro", "Cabeça", "Olho", "Fígado", "Coração", "Brânquias", "Intestino",
                    "Músculo", "Gônadas", "Nadadeira caudal"]},
    "Peixe-donzela (Pomacentridae)": {
        "en": "Damselfish (Pomacentridae)", "methods": ("damselfish (Pomacentridae)", "peixe-donzela (Pomacentridae)"),
        "tecidos": ["Cérebro", "Fígado", "Brânquias", "Músculo", "Intestino", "Gônadas"]},
    "Peixe-palhaço (Amphiprion spp.)": {
        "en": "Clownfish (Amphiprion spp.)", "methods": ("clownfish (Amphiprion spp.)", "peixe-palhaço (Amphiprion spp.)"),
        "tecidos": ["Larva inteira", "Cérebro", "Fígado", "Brânquias", "Músculo", "Gônadas"]},
    "Camundongo (Mus musculus)": {
        "en": "Mouse (Mus musculus)", "methods": ("mice (Mus musculus)", "camundongos (Mus musculus)"),
        "tecidos": ["Cérebro", "Hipocampo", "Córtex", "Hipotálamo", "Fígado", "Rim", "Coração", "Pulmão", "Baço",
                    "Músculo", "Tecido adiposo", "Sangue total"]},
    "Rato (Rattus norvegicus)": {
        "en": "Rat (Rattus norvegicus)", "methods": ("rats (Rattus norvegicus)", "ratos (Rattus norvegicus)"),
        "tecidos": ["Cérebro", "Hipocampo", "Córtex", "Hipotálamo", "Fígado", "Rim", "Coração", "Pulmão", "Baço",
                    "Músculo", "Tecido adiposo", "Sangue total"]},
    "Humano (Homo sapiens)": {
        "en": "Human (Homo sapiens)", "methods": ("human donors", "doadores humanos"),
        "tecidos": ["Sangue total", "PBMC", "Biópsia de tecido", "Tumor", "Saliva", "Swab nasofaríngeo"]},
    "Cultura de células": {
        "en": "Cell culture", "methods": ("", ""),
        "tecidos": ["Linhagem celular", "Cultura primária", "Células-tronco / iPSC", "Organoide"]},
    "Bactéria": {
        "en": "Bacteria", "methods": ("", ""),
        "tecidos": ["Cultura em meio líquido", "Colônias", "Biofilme"]},
    "Vírus": {
        "en": "Virus", "methods": ("", ""),
        "tecidos": ["Sobrenadante de cultura", "Células infectadas", "Swab", "Amostra clínica"]},
}

# tecido (rótulo pt): rótulo en, frase no texto de métodos (en, pt) – no plural, como em "pools of 10 brains"
TISSUES = {
    "Larva inteira": ("Whole larva", "whole larvae", "larvas inteiras"),
    "Cérebro": ("Brain", "brains", "cérebros"),
    "Cabeça": ("Head", "heads", "cabeças"),
    "Olho": ("Eye", "eyes", "olhos"),
    "Fígado": ("Liver", "livers", "fígados"),
    "Coração": ("Heart", "hearts", "corações"),
    "Brânquias": ("Gills", "gill samples", "amostras de brânquias"),
    "Intestino": ("Intestine", "intestines", "intestinos"),
    "Músculo": ("Muscle", "muscle samples", "amostras de músculo"),
    "Gônadas": ("Gonads", "gonads", "gônadas"),
    "Nadadeira caudal": ("Caudal fin", "caudal fins", "nadadeiras caudais"),
    "Hipocampo": ("Hippocampus", "hippocampi", "hipocampos"),
    "Córtex": ("Cortex", "cortex samples", "amostras de córtex"),
    "Hipotálamo": ("Hypothalamus", "hypothalami", "hipotálamos"),
    "Rim": ("Kidney", "kidneys", "rins"),
    "Pulmão": ("Lung", "lungs", "pulmões"),
    "Baço": ("Spleen", "spleens", "baços"),
    "Tecido adiposo": ("Adipose tissue", "adipose tissue samples", "amostras de tecido adiposo"),
    "Sangue total": ("Whole blood", "whole blood samples", "amostras de sangue total"),
    "PBMC": ("PBMC", "PBMC samples", "amostras de PBMC"),
    "Biópsia de tecido": ("Tissue biopsy", "tissue biopsies", "biópsias de tecido"),
    "Tumor": ("Tumor", "tumor samples", "amostras de tumor"),
    "Saliva": ("Saliva", "saliva samples", "amostras de saliva"),
    "Swab nasofaríngeo": ("Nasopharyngeal swab", "nasopharyngeal swabs", "swabs nasofaríngeos"),
    "Linhagem celular": ("Cell line", "cell line cultures", "culturas de linhagem celular"),
    "Cultura primária": ("Primary culture", "primary cultures", "culturas primárias"),
    "Células-tronco / iPSC": ("Stem cells / iPSC", "stem cell cultures", "culturas de células-tronco"),
    "Organoide": ("Organoid", "organoids", "organoides"),
    "Cultura em meio líquido": ("Liquid culture", "liquid cultures", "culturas em meio líquido"),
    "Colônias": ("Colonies", "colony samples", "amostras de colônias"),
    "Biofilme": ("Biofilm", "biofilm samples", "amostras de biofilme"),
    "Sobrenadante de cultura": ("Culture supernatant", "culture supernatants", "sobrenadantes de cultura"),
    "Células infectadas": ("Infected cells", "infected cell cultures", "culturas de células infectadas"),
    "Swab": ("Swab", "swabs", "swabs"),
    "Amostra clínica": ("Clinical sample", "clinical samples", "amostras clínicas"),
}

LABELS_EN = {OUTRO: "Other (type it)", OUTRA: "Other (type it)",
             **{k: v["en"] for k, v in SPECIES.items()}, **{k: v[0] for k, v in TISSUES.items()}}


def tissues_for(species: str) -> list:
    return SPECIES[species]["tecidos"] + [OUTRO] if species in SPECIES else [OUTRO]


def group_letters(n: int) -> list:
    return list(ascii_uppercase[:max(1, min(int(n), 26))])


def sample_codes(n_groups: int, per_group: int) -> list:
    """Códigos A1, A2… B1, B2… no padrão do laboratório (a 1ª letra é o grupo)."""
    return [f"{g}{i}" for g in group_letters(n_groups) for i in range(1, int(per_group) + 1)]


def _int(v, default=0):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return default


def plan(meta: dict) -> dict:
    """Desenho salvo no experimento (valores do arquivo podem vir como texto)."""
    return {"especie": str(meta.get("Espécie") or ""), "tecido": str(meta.get("Tecido") or ""),
            "grupos": _int(meta.get("Grupos")), "por_grupo": _int(meta.get("Amostras por grupo")),
            "por_pool": _int(meta.get("Indivíduos por pool"), 1) or 1}


def methods_from(meta: dict) -> dict:
    """Valores do texto de métodos que vêm do desenho do experimento."""
    d = plan(meta)
    out = {}
    if d["especie"]:
        en, pt = SPECIES.get(d["especie"], {}).get("methods", (d["especie"], d["especie"]))
        out.update({"especie": en, "especie_pt": pt})
    if d["tecido"]:
        out["tipo_amostra"] = d["tecido"]
    if d["por_pool"]:
        out["animais_por_pool"] = d["por_pool"]
    return out

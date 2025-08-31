import streamlit as st
from dataclasses import dataclass
import uuid

risques_dict = {
    "Incidents cyber": "cyber crimes, interruptions de service et réseau IT, logiciels malveillants/ransomware, violation de données, amendes et sanctions",
    "Interruptions d'activités": "y compris les perturbations de la chaîne logistique",
    "Catastrophes naturelles": "tempête, inondation, tremblement de terre, feu de forêt, évènement climatiques extrêmes",
    "Evolutions législatives et réglementaires": "nouvelles directives, protectionnisme, les exigences RSE et en matière de durabilité",
    "Changement climatique": "risques physiques, opérationnels et financiers résultant du réchauffement climatique",
    "Incendie, explosion": "... à venir ....",
    "Evolutions macro-économiques": "inflation/déflation, politiques monétaires, programme d'austérité",
    "Evolutions de marché": "concurrence accrue/nouveaux entrants, fusions/acquisitions, stagnation ou fluctuation de marchés",
    "Risques politiques": "instabilité politique, guerre, terrorisme, coup d'état, conflits sociaux, grèves, émeutes, pillages",
    "Nouvelles technologies": "impact de l'intelligence artificielle, des systèmes connectés/autonomes, risques éthiques",
    "Pénurie de talents": "... à venir ....",
    "Pannes ou défaillances d'infrastructures critiques": "panne d'électricité, barrages, ponts, voies ferrées vieillissants",
    "Crise énergétique": "pénurie/rupture d'approvisionnement, fluctuation des prix",
    "Vol, fraude, corruption": "... à venir ....",
    "Atteinte à la réputation ou à l'image de marque": "critiques publiques",
    "Insolvabilité": "... à venir ....",
    "Risques environnementaux": "pollution, enjeux liés à la biodiversité, aux ressources naturelles, pénurie",
    "Rappel de produits, défaillances de qualité, défauts de série": "... à venir ....",
    "Pandémie": "problématiques liées à la santé et à la main d'œuvre, restrictions de circulation, annulation d'évènements",
    "Erreur humaine": "perte d'appareils, de supports de stockage ou de documents",
    "Risques humains": "harcèlement, problème psychologique, décès/accident au travail, suicide, évolution des pratiques de santé et nouvelles maladies professionnelles",
}

@dataclass
class Menace:
    nom: str
    categorie_risque: str
    id: str
    occurence: int
    impact_financier: tuple[float, dict]
    impact_reputation: float
    mesure: dict[int, int]

def get_id() -> str:
    return str(uuid.uuid4())

def white_bar() -> None:
    st.markdown(
        """
            <div style="
            height: 3px; 
            background-color: white; 
            margin: 20px 0; 
            border-radius: 2px;
            "></div>
        """,
        unsafe_allow_html=True
    )

def ui_get_name(i:int, id:str, initial_value:str="") -> str:
    menace_name:str = st.text_input(f"Nom de la menace {i + 1}", value=initial_value,key=f"menace_name_{id}")
    return menace_name

def ui_get_categorie(id:str, initial_value:str="") -> str:

    selected_category = st.selectbox(
        "Catégorie de la menace :",
        list(risques_dict.keys()),
        index=list(risques_dict.keys()).index(initial_value) if initial_value in risques_dict else 0,
        key=f"menace_categorie_{id}",
        accept_new_options=True,
        placeholder="Choisissez ou ajoutez une catégorie"
    )

    if not isinstance(selected_category, str):
        st.error("Catégorie de menace invalide.")
        selected_category = initial_value

    return selected_category

def ui_get_occurence(id:str, initial_value:int=1) -> int:

    occurence:int = st.number_input("Veuillez saisir le nombre de crises liées à cette menace", min_value=1, value=initial_value, step=1, key=f"occurence_{id}")

    return occurence

def ui_get_impact_financier(id:str, initial_value:dict={}) -> dict:

    data_impact_financier = initial_value

    st.markdown("Choisissez une méthode pour calculer l'impact financier:", unsafe_allow_html=True)
    methode = st.selectbox("Méthode", options=[1, 2], index=data_impact_financier.get("methode", 1) - 1, format_func=lambda x: f"Méthode {x}", key=f"methode_{id}")
    data_impact_financier["methode"] = methode
    st.caption("Merci de remplir les informations pour la méthode selectionnée")

    st.markdown("Méthode 1: Perte financière annuelle / Bénéfice d'exploitation", unsafe_allow_html=True)
    perte_financiere = st.number_input("Perte financière annuelle (€)", min_value=0.0, value=float(initial_value.get("perte_financiere", 0.0)), step=1.0, key=f"perte_financiere_0_{id}")
    data_impact_financier["perte_financiere"] = perte_financiere
    
    st.markdown("Méthode 2: (Nb cessations x Perte si continuité) / Bénéfice d'exploitation", unsafe_allow_html=True)
    nb_cessations = st.number_input("Nombre de cessations d'activité", min_value=0, value=initial_value.get("nb_cessations", 0), step=1, key=f"nb_cessations_{id}")
    perte_continuite = st.number_input("Perte si continuité d'activité (€)", min_value=0.0, value=float(initial_value.get("perte_continuite", 0.0)), step=1.0, key=f"perte_continuite_1_{id}")
    data_impact_financier["nb_cessations"] = nb_cessations
    data_impact_financier["perte_continuite"] = perte_continuite

    return data_impact_financier

def ui_get_impact_reputation(id:str, initial_value:int=1) -> int:
    st.markdown("Veuillez évaluer l'impact sur la réputation sur une échelle de 1 à 4:", unsafe_allow_html=True)
    impact_reputation: int = st.number_input(
        "Impact réputation", 
        min_value=1, 
        max_value=4, 
        value=initial_value, 
        step=1, 
        key=f"impact_reputation_{id}",
        help="1 = Très faible : impact non significatif sur les parties prenantes, \n2 = Faible : impact sur un petit nombre de personnes ou groupe, \n3 = Elevé : impact sur la majorité des parties prenantes ou un nombre significatif, \n4 = Très élevé : impact sur (presque) toutes les parties prenantes"
    )
    return impact_reputation

def ui_get_mesures(id:str, initial_value:dict={}) -> dict:
    st.markdown("Veuillez indiquer le nombre de mesures par catégorie mises en places pour réduire l'impact de cette menace :", unsafe_allow_html=True)
    mesures = {"0":0,
               "50":0,
               "100":0}
    
    c1_1, c1_2 = st.columns(2)
    c2_1, c2_2 = st.columns(2)
    c3_1, c3_2 = st.columns(2)

    with c1_1:
        st.markdown("Nombre de mesures non testées :", unsafe_allow_html=True)
    with c1_2:
        mesures["0"] = st.number_input("", min_value=0, value=initial_value.get("0", 0), step=1, key=f"mesures_0_{id}")

    with c2_1:
        st.markdown("Nombre de mesures testées à 50% :", unsafe_allow_html=True)
    with c2_2:
        mesures["50"] = st.number_input("", min_value=0, value=initial_value.get("50", 0), step=1, key=f"mesures_50_{id}")

    with c3_1:
        st.markdown("Nombre de mesures testées à 100% :", unsafe_allow_html=True)
    with c3_2:
        mesures["100"] = st.number_input("", min_value=0, value=initial_value.get("100", 0), step=1, key=f"mesures_100_{id}")

    return mesures

def calc_impact_financier(data_impact_financier:dict, benef_exp: int) -> dict:

        if data_impact_financier["methode"] == 1:
            impact_financier =  float(data_impact_financier["perte_financiere"] / benef_exp)
        elif data_impact_financier["methode"] == 2:
            impact_financier = float((data_impact_financier["nb_cessations"] * data_impact_financier["perte_continuite"]) / benef_exp)
        
        if impact_financier <= 5/10/100:
            impact_financier = 1
        elif impact_financier <= 5/100:
            impact_financier = 2
        elif impact_financier <= 15/100:
            impact_financier = 3
        elif impact_financier > 15/100:
            impact_financier = 4

        data_impact_financier["impact_financier"] = impact_financier
        return data_impact_financier

def get_impact_reputation(id:str) -> int:
    st.markdown(create_styled_div("Veuillez évaluer l'impact sur la réputation sur une échelle de 1 à 4:", 16, center=False), unsafe_allow_html=True)
    impact_reputation: int = st.number_input(
        "Impact réputation", 
        min_value=1, 
        max_value=4, 
        value=1, 
        step=1, 
        key=f"impact_reputation_{id}"
    )
    return impact_reputation

def calc_impact_reputation(impact_reputation:int):
    return float(impact_reputation * 0.25)

def calc_occurence(n:int, N:int) -> float:
    return 4 * (n/N if N> 0 else 0.0)

def calc_inherent(reputation:float=0.0, financier:float=0.0) -> float:
    return (reputation + financier) / 2

def calc_reduction(mesures:dict) -> float:

    n_teste_0 = mesures.get("0", 0)
    n_test_50 = mesures.get("50", 0)
    n_test_100 = mesures.get("100", 0)

    if n_teste_0 + n_test_50 + n_test_100 == 0:
        return +1.0
    if (n_test_100) / (n_teste_0 + n_test_50 + n_test_100) >= 0.5:
        return -1.0
    if (n_test_50) / (n_teste_0 + n_test_50 + n_test_100) >= 0.5:
        return 0.0
    if n_test_50 > 0 and n_teste_0 + n_test_100 == 0:
        return 0.0
    if n_teste_0 == n_test_100:
        return 0.0
    if n_teste_0 > n_test_50 and n_test_100 == 0:
        return +1
    if n_teste_0 > n_test_50 and n_test_100 > 0:
        return 0.0
    if n_test_50 + n_test_100 > n_teste_0:
        return 0
    return +1.0

def calc_impact_reel(inherent:float=0.0, reduction:float=0.0) -> float:
    value = inherent + reduction
    if value < 1:
        return 1.0
    if value > 4:
        return 4.0
    return value

def from_4_to_100(n:float) -> float:
    if n < 1:
        return 25
    elif n > 4:
        return 100
    else:
        return round(n * 25, 4)

def calc_criticite(occurence:float=0.0, impact_reel:float=0.0) -> float:
    return round(from_4_to_100(occurence) + from_4_to_100(impact_reel), 4)

def create_styled_div(text: str, font_size: int, center: bool = False) -> str:
    style = f"font-size: {font_size}px;"
    if center:
        style += " text-align: center;"
    return f"<div style='{style}'>{text}</div>"
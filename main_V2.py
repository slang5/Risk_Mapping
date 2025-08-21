import streamlit as st
import utils as utils
import pandas as pd
import numpy as np
import base64
import io

def set_title_page() -> None:
    st.markdown("<h1 style='text-align: center;'>Mapping des menaces</h1>", unsafe_allow_html=True)

def upload_file(current_step: int):
    uploaded_file = st.file_uploader("Importer un fichier EXCEL", type=["xlsx", "xlsm"])
    num_threats_default = 0
    benefice_exploitation_default = 1
    threats_dict = {}

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.dataframe(df)

        # Try to get expected values from the file
        if "Nombre de crises" in df.columns:
            num_threats_default = max(int(df["Nombre de crises"].iloc[0]), 0)
        if "Bénéfice exploitation" in df.columns:
            benefice_exploitation_default = int(df["Bénéfice exploitation"].iloc[0])

        # Try to reconstruct threats_dict if threat columns are present
        threat_columns = {"id", "nom", "categorie_risque", "occurence", "financier_methode", "financier_perte_financiere", "financier_nb_cessations", "financier_perte_continuite", "data_impact_reputation", "mesure_0", "mesure_50", "mesure_100"}
        if threat_columns.intersection(df.columns):
            for _, row in df.iterrows():
                threat_id = row.get("id", utils.get_id())
                threats_dict[threat_id] = {
                    "id": threat_id,
                    "nom": row.get("nom", ""),
                    "categorie_risque": row.get("categorie_risque", ""),
                    "occurence": row.get("occurence", 1),
                    "data_impact_financier": {
                        "methode": row.get("financier_methode", 1),
                        "perte_financiere": row.get("financier_perte_financiere", 0.0),
                        "nb_cessions": row.get("financier_nb_cessations", 0),
                        "perte_continuite": row.get("financier_perte_continuite", 0.0)
                    },
                    "data_impact_reputation": row.get("data_impact_reputation", 1),
                    "mesures": {
                        "0": row.get("mesure_0", 0),
                        "50": row.get("mesure_50", 0),
                        "100": row.get("mesure_100", 0)
                    }
                }
    
    return num_threats_default, benefice_exploitation_default, threats_dict

def export_threats_dict_to_excel(threats_dict):
    filename=f"menaces_export_{utils.uuid.uuid1()}.xlsx"
    rows = []
    nb_crises = st.session_state.get("num_threats", 0)
    benef_exp = st.session_state.get("benefice_exploitation", 0)
    for threat_id, data in threats_dict.items():
        flat = data.copy()
        # Flatten data_impact_financier
        for k, v in data.get("data_impact_financier", {}).items():
            flat[f"financier_{k}"] = v
        # Flatten mesures
        for k, v in data.get("mesures", {}).items():
            flat[f"mesure_{k}"] = v
        # Remove nested dicts
        flat.pop("data_impact_financier", None)
        flat.pop("mesures", None)
        #add global columns
        flat["Nombre de crises"] = nb_crises
        flat["Bénéfice exploitation"] = benef_exp
        rows.append(flat)
    df = pd.DataFrame(rows)
    output = io.BytesIO()
    df.to_excel(output, index=False)
    excel_bytes = output.getvalue()

    st.download_button("Télécharger les données", data=excel_bytes, file_name=filename)

def get_nb_crises(num_threats_default) -> int:
    st.markdown(utils.create_styled_div("Entrez le nombre de crises sur une année :", 18), unsafe_allow_html=True)
    num_threats = st.number_input("Nombre de crises", min_value=0, step=1, value=num_threats_default, key="num_threats_input")

    return num_threats

def get_benef_exp(benef_exp_default) -> int:
    st.markdown(utils.create_styled_div("Entrez le bénéfice d'exploitation annuelle de l'entreprise (€) :", 18), unsafe_allow_html=True)
    benef_exp = st.number_input("Bénéfice d'exploitation (€)", min_value=0, value=benef_exp_default, step=1, key="benef_exp_int")

    return benef_exp

def get_data_for_one_threat(id:str) -> dict:
    threat_data = st.session_state["threats_dict"].get(id, {})

    keys_list = list(st.session_state["threats_dict"].keys())
    place_in_list = keys_list.index(id)

    threat_data["place"] = place_in_list
    st.session_state["threats_dict"][id]["place"] = place_in_list
    with st.form(f"threat_form_{id}"):
        threat_data["id"] = id
        threat_data["nom"] = utils.ui_get_name(place_in_list, id, threat_data.get("nom", ""))
        threat_data["categorie_risque"] = utils.ui_get_categorie(id, threat_data.get("categorie_risque", ""))
        threat_data["occurence"] = utils.ui_get_occurence(id, threat_data.get("occurence", 1))
        threat_data["data_impact_financier"] = utils.ui_get_impact_financier(id, threat_data.get("data_impact_financier", {}))
        threat_data["data_impact_reputation"] = utils.ui_get_impact_reputation(id, threat_data.get("data_impact_reputation", 1))
        threat_data["mesures"] = utils.ui_get_mesures(id, threat_data.get("mesures", {}))
        submit_button = st.form_submit_button("Validation des données")

    if submit_button:
        st.session_state["threats_dict"][id] = threat_data
        st.rerun()

    return threat_data


if __name__ == "__main__":
    set_title_page()

    num_threats:int = 0
    benef_exploitation:int = 1
    threats_dict:dict = {}

    if "step" not in st.session_state:
        st.session_state["step"] = 0

    if st.session_state["step"] <= 1:
        with st.form("upload_form"):
            st.markdown("Veuillez importer un fichier Excel contenant les menaces à évaluer :", unsafe_allow_html=True)
            num_threats, benef_exploitation, threats_dict = upload_file(st.session_state["step"])
            submit_button_importer = st.form_submit_button("Importer")

            if submit_button_importer:
                st.session_state["step"] = 1
                st.rerun()
                

    if st.session_state["step"] <= 1:
        
        with st.form("step1_form"):
            st.session_state["num_threats"] = get_nb_crises(num_threats)
            st.session_state["benefice_exploitation"] = get_benef_exp(benef_exploitation)
            st.session_state["threats_dict"] = threats_dict
            submit_button = st.form_submit_button("Valider")

        if submit_button:
            if st.session_state["num_threats"] > num_threats:
                for _ in range(st.session_state["num_threats"] - num_threats):
                    st.session_state["threats_dict"] [utils.get_id()] = {}
            st.session_state["step"] = 2
            st.rerun()

    if st.session_state["step"] == 2:
        for threat_id, data in st.session_state["threats_dict"].items():
            get_data_for_one_threat(threat_id)

        button_all_verifier = st.button("Validation des données pour toutes les menaces")

        if button_all_verifier:
            
            st.success("Toutes les menaces ont été validées !")
            st.session_state["step"] = 3
            st.rerun()

    if st.session_state["step"] == 3:
        N_occurrences = sum([data["occurence"] for sid, data in st.session_state["threats_dict"].items()])
        if "resultat" not in st.session_state:
            st.session_state["resultat"] = {}
        for threat_id, data in st.session_state["threats_dict"].items():
            impact_financier = utils.calc_impact_financier(data["data_impact_financier"], st.session_state["benefice_exploitation"])["impact_financier"]
            impact_reputation = utils.calc_impact_reputation(data["data_impact_reputation"])
            occurence = utils.calc_occurence(data["occurence"], N_occurrences)
            impact_inherent = utils.calc_inherent(impact_reputation, impact_financier)
            mesures = utils.calc_reduction(data["mesures"])
            reel = utils.calc_impact_reel(impact_inherent, mesures)
            criticite = utils.calc_criticite(occurence, reel)
            st.session_state["resultat"][threat_id] = {
                "impact_financier": impact_financier,
                "impact_reputation": impact_reputation,
                "occurence": occurence,
                "impact_inherent": impact_inherent,
                "mesures": mesures,
                "reel": reel,
                "criticite": criticite
            }
            st.markdown(st.session_state["resultat"][threat_id])
        st.success("Toutes les étapes ont été validées !")

        import plotly.express as px

        # Prepare data for the scatter plot
        plot_data = []
        for threat_id, result in st.session_state["resultat"].items():
            threat_name = st.session_state["threats_dict"][threat_id].get("nom", f"Threat {threat_id}")
            plot_data.append({
                "Nom de la menace": threat_name,
                "impact reel": result["reel"]*25,
                "occurence": result["occurence"]*25,
                "criticite": result["criticite"]
            })

        df_plot = pd.DataFrame(plot_data)

        # Create scatter plot
        fig = px.scatter(
            df_plot,
            x="impact reel",
            y="occurence",
            size="criticite",
            hover_name="Nom de la menace",
            title="Analyse des Risques: Impact Réel vs Occurrence",
            labels={
                "impact reel": "Impact Réel",
                "occurence": "Occurrence",
                "criticite": "Criticité"
            }
        )
        # Read your local image file and encode it as base64
        with open("grille.png", "rb") as f:
            img_bytes = f.read()
        img_base64 = "data:image/png;base64," + base64.b64encode(img_bytes).decode()

        sizex = 100
        sizey = 100

        fig.update_xaxes(gridcolor="white", dtick=25)
        fig.update_yaxes(gridcolor="white", dtick=25)
        fig.update_xaxes(range=[0, 100])
        fig.update_yaxes(range=[0, 100])
        fig.update_layout(
            xaxis_title="Impact Réel",
            yaxis_title="Occurrence",
            showlegend=True, 
            images=[dict(
                source=img_base64,
                xref="x", yref="y",
                x=0, y=100,
                sizex=sizex, sizey=sizey,
                sizing="stretch",  # or "fill", or "contain"
                opacity=0.8,
                layer="below"
            )],
            height=600,
            width=600
        )

        df_table = pd.DataFrame(plot_data)
        df_table = df_table.sort_values(by="criticite", ascending=False).reset_index(drop=True)
        df_table["Rang"] = df_table.index + 1
        top_n = min(st.session_state["num_threats"], 5)

        st.dataframe(df_table.head(top_n))

        st.plotly_chart(fig, use_container_width=True)
    if st.session_state["step"] >= 1:
        export_threats_dict_to_excel(st.session_state["threats_dict"])

    return_start = st.button("Recommencer")
    if return_start:
        st.session_state["step"] = 0
        st.session_state["threats_dict"] = {}
        st.session_state["resultat"] = {}
        st.session_state["num_threats"] = 0
        st.rerun()
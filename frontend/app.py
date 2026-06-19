import streamlit as st
import requests

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Système Multi-Agents Médical",
    page_icon="🩺",
    layout="centered"
)

if "screen" not in st.session_state:
    st.session_state.screen = 1
if "thread_id" not in st.session_state:
    st.session_state.thread_id = ""
if "question_count" not in st.session_state:
    st.session_state.question_count = 0
if "current_question" not in st.session_state:
    st.session_state.current_question = ""
if "diagnostic_summary" not in st.session_state:
    st.session_state.diagnostic_summary = ""
if "interim_care" not in st.session_state:
    st.session_state.interim_care = ""
if "final_report" not in st.session_state:
    st.session_state.final_report = ""

st.title("🩺 Orientation Clinique")
st.divider()

# --- FONCTION DE TRAITEMENT DE L'ÉTAT DU GRAPHE ---
def process_graph_state(state_values):
    count = state_values.get("question_count", 0)
    st.session_state.question_count = count

    if count < 5:
        # On prend directement la question envoyée par l'API
        st.session_state.current_question = state_values.get("current_question", "Une question est en cours de préparation...")
        st.session_state.screen = 2
    else:
        st.session_state.diagnostic_summary = state_values.get("diagnostic_summary", "Synthèse indisponible.")
        st.session_state.interim_care = state_values.get("interim_care", "Repos, hydratation.")
        st.session_state.screen = 3

# =====================================================================
# ÉCRAN 1 : SAISIE DU CAS INITIAL PATIENT
# =====================================================================
if st.session_state.screen == 1:
    st.header("Description des symptômes initiaux")
    patient_case = st.text_area(
        "Décrivez précisément ce que vous ressentez (fièvre, douleurs, durée...) :",
        placeholder="Exemple : J'ai une forte fièvre et des maux de tête depuis hier soir..."
    )
    
    if st.button("Démarrer la consultation", type="primary"):
        if patient_case.strip():
            with st.spinner("Initialisation du workflow multi-agents..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/consultation/start",
                        json={"patient_case": patient_case}
                    )
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.thread_id = data["thread_id"]
                        process_graph_state(data["state"])
                        st.rerun()
                    else:
                        st.error(f"Erreur du serveur backend : {response.text}")
                except Exception as e:
                    st.error("Impossible de joindre l'API FastAPI. Vérifiez qu'Uvicorn est bien lancé.")
        else:
            st.warning("Veuillez saisir vos symptômes avant de continuer.")

# =====================================================================
# ÉCRAN 2 : QUESTIONNAIRE PATIENT DYNAMIQUE (CORRIGÉ)
# =====================================================================
elif st.session_state.screen == 2:
    st.header("Questionnaire Médical ")
    
    # Affichage de la question posée par l'agent
    st.info(f"**Diagnostic :** {st.session_state.current_question}")
    
    # Utilisation d'un formulaire Streamlit pour bloquer la soumission automatique intempestive
    with st.form(key="answer_form", clear_on_submit=True):
        patient_answer = st.text_input("Votre réponse :", placeholder="Écrivez votre réponse ici...")
        submit_button = st.form_submit_button(label="Envoyer la réponse", type="primary")
        
    if submit_button:
        if patient_answer.strip():
            with st.spinner("L'agent analyse votre réponse..."):
                try:
                    # Envoi de la réponse réelle à l'API
                    response = requests.post(
                        f"{API_BASE_URL}/consultation/answer",
                        json={
                            "thread_id": st.session_state.thread_id,
                            "answer": patient_answer
                        }
                    )
                    if response.status_code == 200:
                        data = response.json()
                        process_graph_state(data["state"])
                        st.rerun()
                    else:
                        st.error(f"Erreur renvoyée par le serveur : {response.text}")
                except Exception as e:
                    st.error("Erreur réseau lors de la communication avec l'API.")
        else:
            st.warning("Veuillez écrire une réponse avant de valider.")

# =====================================================================
# ÉCRAN 3 : REVUE MÉDECIN (HUMAN-IN-THE-LOOP)
# =====================================================================
elif st.session_state.screen == 3:
    st.header("Validation Médicale Du Médecin")
    st.warning("Attente de la validation du médecin traitant.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Synthèse clinique préliminaire")
        st.text_area("Analyse de l'agent :", value=st.session_state.diagnostic_summary, height=200, disabled=True)
    with col2:
        st.subheader("Recommandation intermédiaire")
        st.info(st.session_state.interim_care)
        
    st.divider()
    
    physician_treatment = st.text_area(
        "Directives médicales, prescriptions ou conduite à tenir :",
        placeholder="Exemple : Repos strict, paracétamol 1g si douleurs, surveiller la température..."
    )
    
    if st.button("Valider et Lever l'interruption", type="primary"):
        if physician_treatment.strip():
            with st.spinner("Génération du rapport final par le Report Agent..."):
                try:
                    resume_resp = requests.post(
                        f"{API_BASE_URL}/consultation/resume",
                        json={
                            "thread_id": st.session_state.thread_id,
                            "physician_treatment": physician_treatment
                        }
                    )
                    if resume_resp.status_code == 200:
                        report_resp = requests.get(f"{API_BASE_URL}/consultation/{st.session_state.thread_id}/report")
                        if report_resp.status_code == 200:
                            st.session_state.final_report = report_resp.json()["final_report"]
                            st.session_state.screen = 4
                            st.rerun()
                except Exception as e:
                    st.error("Erreur lors de la levée de l'interruption.")
        else:
            st.warning("Le médecin doit obligatoirement saisir des consignes cliniques.")

# =====================================================================
# ÉCRAN 4 : AFFICHAGE DU RAPPORT FINAL
# =====================================================================
elif st.session_state.screen == 4:
    st.header("Rapport Clinique Final")
    
    st.success("Rapport généré avec succès .")
    st.markdown(st.session_state.final_report)
    
    st.divider()
    st.error("⚠️ **Ce système ne remplace pas une consultation médicale.**")
    
    if st.button("Nouvelle Consultation"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
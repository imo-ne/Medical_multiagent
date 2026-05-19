import streamlit as st

import requests


API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Medical Multi Agent",
    layout="wide"
)


st.title("🏥 Système Multi-Agents Médical")


# =========================
# SESSION STATE
# =========================

if "graph_response" not in st.session_state:
    st.session_state.graph_response = None

if "final_report" not in st.session_state:
    st.session_state.final_report = None

if "current_interrupt" not in st.session_state:
    st.session_state.current_interrupt = None


# =========================
# START CONSULTATION
# =========================

if st.button("Démarrer consultation"):

    response = requests.post(
        f"{API_URL}/consultation/start"
    )

    st.session_state.graph_response = response.json()

    if "__interrupt__" in st.session_state.graph_response:

        st.session_state.current_interrupt = (
            st.session_state.graph_response[
                "__interrupt__"
            ][0]["value"]
        )


# =========================
# HANDLE INTERRUPTS
# =========================

if st.session_state.current_interrupt:

    interrupt_data = st.session_state.current_interrupt

    interrupt_type = interrupt_data["type"]


    # =====================
    # PATIENT QUESTIONS
    # =====================

    if interrupt_type == "patient_question":

        st.header("Question patient")

        st.write(
            interrupt_data["question"]
        )

        answer = st.text_input(
            "Votre réponse"
        )

        if st.button("Envoyer réponse"):

            response = requests.post(
                f"{API_URL}/consultation/answer",
                params={
                    "answer": answer
                }
            )

            result = response.json()

            if "__interrupt__" in result:

                st.session_state.current_interrupt = (
                    result["__interrupt__"][0]["value"]
                )

            else:

                st.session_state.current_interrupt = None

                st.session_state.graph_response = result


    # =====================
    # PHYSICIAN REVIEW
    # =====================

    elif interrupt_type == "physician_review":

        st.header("Validation médecin")

        st.subheader(
            "Synthèse clinique"
        )

        st.write(
            interrupt_data["diagnostic_summary"]
        )

        st.subheader(
            "Recommandation intermédiaire"
        )

        st.write(
            interrupt_data.get(
                "interim_care",
                "Aucune recommandation"
            )
        )

        treatment = st.text_area(
            "Traitement / conduite à tenir"
        )

        if st.button("Valider traitement"):

            response = requests.post(
                f"{API_URL}/consultation/answer",
                params={
                    "answer": treatment
                }
            )

            result = response.json()

            st.session_state.final_report = (
                result["final_report"]
            )

            st.session_state.current_interrupt = None


# =========================
# FINAL REPORT
# =========================

if st.session_state.final_report:

    st.header("Rapport final")

    st.markdown(
        st.session_state.final_report
    )
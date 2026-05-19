from app.llm import llm


def report_agent_node(state):

    prompt = f"""
    Génère un rapport médical structuré.

    Synthèse clinique :
    {state.get("diagnostic_summary")}

    Recommandation intermédiaire :
    {state.get("interim_care")}

    Traitement médecin :
    {state.get("physician_treatment")}

    Ajouter obligatoirement :
    Ce système ne remplace pas une consultation médicale.
    """

    response = llm.invoke(prompt)

    return {
        **state,
        "final_report": response.content
    }
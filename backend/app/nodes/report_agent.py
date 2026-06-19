from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from app.state import MedicalState

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1)
async def report_agent_node(state: MedicalState):
    messages = state.get("messages", [])
    diagnostic_summary = state.get("diagnostic_summary", "")
    interim_care = state.get("interim_care", "")
    physician_treatment = state.get("physician_treatment", "")
    
    prompt = f"""
    Tu es le Report Agent. Tu dois rédiger un compte rendu clinique final clair et structuré au format Markdown.
    
    Voici les éléments à intégrer obligatoirement :
    1. **Anamnèse & Synthèse initiale** : {diagnostic_summary}
    2. **Recommandations conservatoires** : {interim_care}
    3. **Décision et Traitement Validé par le Médecin** : {physician_treatment}
    
    Mets en page ce rapport de façon professionnelle avec des sections claires (##). 
    Ne rajoute PAS la mention d'avertissement éthique à la fin, elle est déjà gérée par l'interface utilisateur.
    """
    
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    
    return {
        "final_report": response.content,
        "next": "__end__"
    }
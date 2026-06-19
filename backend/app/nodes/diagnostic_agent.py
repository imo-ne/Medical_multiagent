from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import interrupt 
from app.state import MedicalState

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2)

async def diagnostic_agent_node(state: MedicalState):
    messages = state.get("messages", [])
    question_count = state.get("question_count", 0)
    
    while question_count < 5:
        prompt = (
            "Tu es le Diagnostic Agent. Ton rôle est de poser exactement 1 question claire "
            "au patient pour comprendre ses symptômes. "
            f"Tu en es à la question {question_count + 1}/5.\n"
            "Formule uniquement ta question sous forme de texte direct."
        )
        
        response = await llm.ainvoke([*messages, HumanMessage(content=prompt)])
        question_text = response.content
        patient_response = interrupt(question_text)
        messages.append(AIMessage(content=question_text))
        messages.append(HumanMessage(content=patient_response))
        question_count += 1

    prompt_analysis = (
        "Tu as collecté toutes les réponses (5 questions complétées). "
        "Rédige maintenant une 'synthèse clinique préliminaire' détaillée du patient. "
        "Génère également une 'recommandation intermédiaire générale' prudente."
    )
    
    response = await llm.ainvoke([*messages, HumanMessage(content=prompt_analysis)])
    
    return {
        "messages": messages + [response],
        "question_count": question_count,
        "diagnostic_summary": response.content,
        "interim_care": "Repos, hydratation, et surveillance des symptômes. Consulter rapidement en cas d'aggravation.",
        "next": "supervisor"
    }
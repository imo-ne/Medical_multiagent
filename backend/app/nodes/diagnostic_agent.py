from langgraph.types import interrupt

from app.tools.patient_tools import ask_patient

from app.tools.care_tools import recommend_interim_care

from app.llm import llm


def diagnostic_agent_node(state):

    question_count = state.get("question_count", 0)

    patient_answers = state.get("patient_answers", [])


    # =========================
    # ASK QUESTIONS
    # =========================

    if question_count < 5:

        question = ask_patient(question_count)

        answer = interrupt(
            {
                "type": "patient_question",
                "question": question,
                "question_count": question_count
            }
        )

        patient_answers.append(
            f"Q: {question} | R: {answer}"
        )

        return {
            **state,
            "question_count": question_count + 1,
            "patient_answers": patient_answers
        }


    # =========================
    # LLM ANALYSIS
    # =========================

    patient_context = "\n".join(patient_answers)


    interim_care = recommend_interim_care.invoke(
        patient_context
    )


    prompt = f"""
    Tu es un assistant médical académique.

    Analyse les réponses suivantes :

    {patient_context}

    Produis :
    1. Une synthèse clinique préliminaire
    2. Une recommandation prudente

    IMPORTANT :
    - ne jamais donner de diagnostic définitif
    - rester prudent
    - ne jamais remplacer un médecin
    """


    response = llm.invoke(prompt)


    return {
        **state,
        "diagnostic_summary": response.content,
        "interim_care": interim_care
    }
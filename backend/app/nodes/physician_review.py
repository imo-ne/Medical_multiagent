from langgraph.types import interrupt


def physician_review_node(state):

    physician_input = interrupt(
        {
            "type": "physician_review",
            "message": "Veuillez valider et ajouter un traitement.",
            "diagnostic_summary": state["diagnostic_summary"],
            "interim_care": state["interim_care"]
        }
    )

    return {
        **state,
        "physician_treatment": physician_input
    }
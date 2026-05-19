from langchain_core.tools import tool


@tool

def recommend_interim_care(summary: str):
    """
    Fournit une recommandation intermédiaire prudente.
    """

    return (
        "Repos, hydratation, surveillance des symptômes "
        "et consultation médicale en cas d'aggravation."
    )
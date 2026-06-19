from langchain_core.tools import tool

@tool
def recommend_interim_care_tool(condition_summary: str) -> str:
    """Génère des recommandations de soins intermédiaires prudents (repos, hydratation, etc.)."""
    return "Recommandations : Repos complet, hydratation abondante, et surveillance des symptômes. Consultez rapidement en cas d'aggravation."
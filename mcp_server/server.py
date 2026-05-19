from mcp.server.fastmcp import FastMCP


mcp = FastMCP("medical-mcp")


@mcp.tool()

def get_emergency_level(symptoms: str) -> str:
    """
    Détermine un niveau d'urgence simplifié.
    """

    symptoms = symptoms.lower()

    if "difficultés respiratoires" in symptoms:
        return "HIGH"

    if "fièvre" in symptoms:
        return "MEDIUM"

    return "LOW"


if __name__ =="__main__":
    mcp.run()
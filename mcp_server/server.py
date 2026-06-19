import asyncio
from mcp.server.models import InitializationOptions
from mcp.server import Notification, Server
import mcp.types as types
from mcp.server.stdio import stdio_server

# Création de l'instance du serveur MCP
server = Server("medical-knowledge-base")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """Expose la liste des outils médicaux disponibles au client backend."""
    return [
        types.Tool(
            name="lookup_symptom",
            description="Recherche des fiches cliniques et protocoles à partir d'un symptôme.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Le symptôme à analyser (ex: fièvre, migraine)"},
                },
                "required": ["query"],
            },
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    """Exécute la logique de l'outil demandé."""
    if name == "lookup_symptom":
        query = arguments.get("query", "").lower()
        
        # Base de données médicale simulée exigée par l'architecture
        if "fièvre" in query or "fievre" in query:
            result = "Protocole Fièvre : Hydratation fréquente, surveillance thermique toutes les 4h, alerte si > 39°C."
        elif "toux" in query:
            result = "Protocole Respiratoire : Évaluer si toux sèche ou grasse, vérifier l'absence de dyspnée."
        else:
            result = "Documentation Générale : Repos conseillé, surveillance de l'évolution générale sous 24h."
            
        return [types.TextContent(type="text", text=result)]
    raise ValueError(f"Outil inconnu : {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="medical-knowledge-base",
                server_version="1.0.0",
                capabilities=server.get_capabilities()
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
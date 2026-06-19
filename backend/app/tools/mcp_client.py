import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_core.tools import tool

server_params = StdioServerParameters(
    command=sys.executable,  
    args=["../mcp_server/server.py"]  
)

@tool
async def fetch_medical_knowledge(query: str) -> str:
    """
    Interroge le serveur MCP pour récupérer des connaissances médicales, 
    des fiches de symptômes ou des protocoles cliniques de référence.
    """
    try:
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                response = await session.call_tool("lookup_symptom", arguments={"query": query})
                return response.content[0].text
    except Exception as e:
        return f"Erreur de connexion au serveur MCP : {str(e)}"
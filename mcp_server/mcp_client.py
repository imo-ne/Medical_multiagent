import httpx


async def call_mcp_tool(symptoms: str):

    async with httpx.AsyncClient() as client:

        response = await client.post(
            "http://localhost:8001/tools/get_emergency_level",
            json={
                "symptoms": symptoms
            }
        )

        return response.json()
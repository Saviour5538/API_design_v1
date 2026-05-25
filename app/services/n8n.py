import httpx
from app.config import settings

async def trigger_n8n_workflow(n8n_workflow_id: str, input_values: dict) -> str:
    headers = {"X-N8N-API-KEY": settings.N8N_API_KEY, "Content-Type": "application/json"}
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.N8N_BASE_URL}/api/v1/workflows/{n8n_workflow_id}/execute",
            json={"data": input_values},
            headers=headers,
            timeout=10.0
        )
        response.raise_for_status()
        return response.json().get("data", {}).get("executionId", "")

async def cancel_n8n_execution(n8n_execution_id: str) -> bool:
    headers = {"X-N8N-API-KEY": settings.N8N_API_KEY}
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.N8N_BASE_URL}/api/v1/executions/{n8n_execution_id}/stop",
            headers=headers,
            timeout=10.0
        )
        return response.status_code == 200

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from math import ceil
from app.database import get_db
from app.models.agent import Agent
from app.schemas.agent import AgentOut, AgentDetailOut, AgentCategoryOut, AgentListOut

router = APIRouter(prefix="/agents", tags=["Agents"])

def build_agent_out(agent: Agent) -> AgentOut:
    return AgentOut(
        id=agent.id,
        name=agent.name,
        description=agent.description,
        category=AgentCategoryOut(id=agent.category.id, name=agent.category.name),
        inputs=agent.inputs or [],
        is_active=agent.is_active,
        created_at=agent.created_at,
        updated_at=agent.updated_at
    )

@router.get("")
def list_agents(
    category_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Agent)
    if category_id:
        query = query.filter(Agent.category_id == category_id)
    if search:
        query = query.filter(Agent.name.ilike(f"%{search}%"))
    total = query.count()
    agents = query.offset((page - 1) * limit).limit(limit).all()
    return {
        "status": "success",
        "data": {
            "items": [build_agent_out(a) for a in agents],
            "total": total, "page": page, "limit": limit,
            "total_pages": ceil(total / limit)
        }
    }

@router.get("/{agent_id}")
def get_agent(agent_id: str, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail={"message": "Agent not found", "code": 404})
    if not agent.is_active:
        raise HTTPException(status_code=403, detail={"message": "This agent is currently inactive", "code": 403})
    return {
        "status": "success",
        "data": AgentDetailOut(
            id=agent.id, name=agent.name, description=agent.description,
            category=AgentCategoryOut(id=agent.category.id, name=agent.category.name),
            inputs=agent.inputs or [], is_active=agent.is_active,
            n8n_workflow_id=agent.n8n_workflow_id,
            created_at=agent.created_at, updated_at=agent.updated_at
        )
    }

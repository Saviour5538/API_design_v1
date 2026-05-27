from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from math import ceil
from app.database import get_db
from app.models.agent import Agent
from app.models.category import Category
from app.schemas.agent import AgentOut, AgentCategoryOut

router = APIRouter(prefix="/agents", tags=["Agents"])

def build_agent_out(agent: Agent, category: Optional[Category]) -> AgentOut:
    return AgentOut(
        id=agent.id,
        name=agent.name,
        description=agent.description,
        category=AgentCategoryOut(
            id=category.id, name=category.name, color=category.color
        ) if category else None,
        input=agent.input,
        output=agent.output,
        configs=agent.configs
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

    items = []
    for a in agents:
        cat = db.query(Category).filter(Category.id == a.category_id).first() if a.category_id else None
        items.append(build_agent_out(a, cat))

    return {
        "status": "success",
        "data": {"items": items, "total": total, "page": page, "limit": limit, "total_pages": ceil(total / limit)}
    }

@router.get("/{agent_id}")
def get_agent(agent_id: str, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail={"message": "Agent not found", "code": 404})
    cat = db.query(Category).filter(Category.id == agent.category_id).first() if agent.category_id else None
    return {"status": "success", "data": build_agent_out(agent, cat)}

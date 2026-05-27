from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from math import ceil
from app.database import get_db
from app.models.workflow import Workflow
from app.schemas.workflow import WorkflowCreate, WorkflowUpdate, WorkflowListItemOut, WorkflowDetailOut

router = APIRouter(prefix="/workflows", tags=["Workflows"])

VALID_STATUSES = {"DRAFT", "ACTIVE", "INACTIVE"}

def build_list_item(wf: Workflow) -> WorkflowListItemOut:
    return WorkflowListItemOut(
        id=wf.id, name=wf.name, description=wf.description, status=wf.status,
        version=wf.version,
        node_count=len(wf.nodes),
        created_at=wf.created_at, updated_at=wf.updated_at
    )

@router.get("")
def list_workflows(
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Workflow)
    if search:
        query = query.filter(Workflow.name.ilike(f"%{search}%"))
    if status:
        query = query.filter(Workflow.status == status.upper())
    total = query.count()
    workflows = query.offset((page - 1) * limit).limit(limit).all()
    return {
        "status": "success",
        "data": {
            "items": [build_list_item(wf) for wf in workflows],
            "total": total, "page": page, "limit": limit,
            "total_pages": ceil(total / limit)
        }
    }

@router.get("/{workflow_id}")
def get_workflow(workflow_id: str, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail={"message": "Workflow not found", "code": 404})
    from app.schemas.node import NodeOut, NodeAgentOut, NodeConfigOut
    from app.models.node import Node
    from app.models.agent import Agent
    from app.models.category import Category
    nodes_out = []
    for n in wf.nodes:
        agent = db.query(Agent).filter(Agent.id == n.node_id).first()
        cat = db.query(Category).filter(Category.id == agent.category_id).first() if (agent and agent.category_id) else None
        cfgs = [NodeConfigOut(id=c.id, var_name=c.var_name, value=c.value) for c in n.configs]
        nodes_out.append(NodeOut(
            id=n.id, node_id=n.node_id,
            agent=NodeAgentOut(id=agent.id, name=agent.name, category=cat.name if cat else None) if agent else NodeAgentOut(id=n.node_id, name="Unknown", category=None),
            configs=cfgs,
            workflow_id=n.workflow_id,
            created_at=n.created_at, updated_at=n.updated_at
        ))
    return {
        "status": "success",
        "data": WorkflowDetailOut(
            id=wf.id, name=wf.name, description=wf.description, status=wf.status,
            version=wf.version,
            nodes=nodes_out,
            created_at=wf.created_at, updated_at=wf.updated_at
        )
    }

@router.post("", status_code=201)
def create_workflow(body: WorkflowCreate, db: Session = Depends(get_db)):
    wf = Workflow(name=body.name, description=body.description)
    db.add(wf)
    db.commit()
    db.refresh(wf)
    return {
        "status": "success",
        "data": WorkflowDetailOut(
            id=wf.id, name=wf.name, description=wf.description, status=wf.status,
            version=wf.version, nodes=[],
            created_at=wf.created_at, updated_at=wf.updated_at
        )
    }

@router.patch("/{workflow_id}")
def update_workflow(workflow_id: str, body: WorkflowUpdate, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail={"message": "Workflow not found", "code": 404})
    if body.name: wf.name = body.name
    if body.description is not None: wf.description = body.description
    if body.status:
        s = body.status.upper()
        if s not in VALID_STATUSES:
            raise HTTPException(status_code=422, detail={
                "message": "Validation failed", "code": 422,
                "errors": [{"field": "status", "issue": f"must be one of {sorted(VALID_STATUSES)}"}]
            })
        wf.status = s
    db.commit()
    db.refresh(wf)
    return {"status": "success", "data": build_list_item(wf)}

@router.delete("/{workflow_id}")
def delete_workflow(workflow_id: str, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail={"message": "Workflow not found", "code": 404})
    running = any(e.status == "RUNNING" for e in wf.executions)
    if running:
        raise HTTPException(status_code=422, detail={"message": "Cannot delete a workflow that is currently running", "code": 422})
    db.delete(wf)
    db.commit()
    return {"status": "success", "message": "Workflow deleted successfully"}

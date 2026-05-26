from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from math import ceil
from datetime import datetime
from app.database import get_db
from app.models.workflow import Workflow
from app.models.category import Category
from app.schemas.workflow import WorkflowCreate, WorkflowUpdate, WorkflowListItemOut, WorkflowDetailOut, WorkflowCategoryOut

router = APIRouter(prefix="/workflows", tags=["Workflows"])

def build_list_item(wf: Workflow) -> WorkflowListItemOut:
    return WorkflowListItemOut(
        id=wf.id, name=wf.name, description=wf.description, status=wf.status,
        category=WorkflowCategoryOut(id=wf.category.id, name=wf.category.name) if wf.category else None,
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
    query = db.query(Workflow).filter(Workflow.deleted_at == None)
    if search:
        query = query.filter(Workflow.name.ilike(f"%{search}%"))
    if status:
        query = query.filter(Workflow.status == status)
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
    wf = db.query(Workflow).filter(Workflow.id == workflow_id, Workflow.deleted_at == None).first()
    if not wf:
        raise HTTPException(status_code=404, detail={"message": "Workflow not found", "code": 404})
    from app.schemas.node import NodeOut, NodeAgentOut
    nodes_out = [
        NodeOut(
            id=n.id, name=n.name, order=n.order,
            agent=NodeAgentOut(id=n.agent.id, name=n.agent.name, category=n.agent.category.name),
            input_values=n.input_values or {}, workflow_id=n.workflow_id,
            created_at=n.created_at, updated_at=n.updated_at
        ) for n in wf.nodes
    ]
    return {
        "status": "success",
        "data": WorkflowDetailOut(
            id=wf.id, name=wf.name, description=wf.description, status=wf.status,
            category=WorkflowCategoryOut(id=wf.category.id, name=wf.category.name) if wf.category else None,
            nodes=nodes_out,
            created_at=wf.created_at, updated_at=wf.updated_at
        )
    }

@router.post("", status_code=201)
def create_workflow(body: WorkflowCreate, db: Session = Depends(get_db)):
    if body.category_id:
        if not db.query(Category).filter(Category.id == body.category_id).first():
            raise HTTPException(status_code=422, detail={
                "message": "Validation failed", "code": 422,
                "errors": [{"field": "category_id", "issue": "invalid category"}]
            })
    wf = Workflow(name=body.name, description=body.description, category_id=body.category_id)
    db.add(wf)
    db.commit()
    db.refresh(wf)
    return {
        "status": "success",
        "data": WorkflowDetailOut(
            id=wf.id, name=wf.name, description=wf.description, status=wf.status,
            category=WorkflowCategoryOut(id=wf.category.id, name=wf.category.name) if wf.category else None,
            nodes=[],
            created_at=wf.created_at, updated_at=wf.updated_at
        )
    }

@router.patch("/{workflow_id}")
def update_workflow(workflow_id: str, body: WorkflowUpdate, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id, Workflow.deleted_at == None).first()
    if not wf:
        raise HTTPException(status_code=404, detail={"message": "Workflow not found", "code": 404})
    if body.name: wf.name = body.name
    if body.description is not None: wf.description = body.description
    if body.status: wf.status = body.status
    if body.category_id: wf.category_id = body.category_id
    db.commit()
    db.refresh(wf)
    return {"status": "success", "data": build_list_item(wf)}

@router.delete("/{workflow_id}")
def delete_workflow(workflow_id: str, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id, Workflow.deleted_at == None).first()
    if not wf:
        raise HTTPException(status_code=404, detail={"message": "Workflow not found", "code": 404})
    running = any(e.status == "running" for e in wf.executions)
    if running:
        raise HTTPException(status_code=422, detail={"message": "Cannot delete a workflow that is currently running", "code": 422})
    wf.deleted_at = datetime.utcnow()
    db.commit()
    return {"status": "success", "message": "Workflow deleted successfully"}

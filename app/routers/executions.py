from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from math import ceil
from datetime import datetime
from app.database import get_db
from app.models.execution import Execution
from app.models.workflow import Workflow
from app.schemas.execution import ExecutionCreate, ExecutionOut, ExecutionListOut, WebhookUpdate, ExecutionWorkflowOut
from app.services.n8n import trigger_n8n_workflow, cancel_n8n_execution

router = APIRouter(prefix="/executions", tags=["Executions"])

def build_execution_out(ex: Execution) -> ExecutionOut:
    return ExecutionOut(
        execution_id=ex.id,
        workflow=ExecutionWorkflowOut(id=ex.workflow.id, name=ex.workflow.name),
        status=ex.status,
        started_at=ex.started_at,
        completed_at=ex.completed_at,
        result=ex.result,
        error=ex.error
    )

@router.post("", status_code=201)
async def trigger_execution(body: ExecutionCreate, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == body.workflow_id, Workflow.deleted_at == None).first()
    if not wf:
        raise HTTPException(status_code=404, detail={"message": "Workflow not found", "code": 404})
    if wf.status != "active":
        raise HTTPException(status_code=422, detail={"message": "Only active workflows can be executed", "code": 422})
    if not wf.nodes:
        raise HTTPException(status_code=422, detail={"message": "Cannot execute a workflow with no nodes", "code": 422})

    execution = Execution(workflow_id=wf.id, input_values=body.input_values or {})
    db.add(execution)
    db.commit()
    db.refresh(execution)

    try:
        n8n_id = await trigger_n8n_workflow(wf.nodes[0].agent.n8n_workflow_id or "", body.input_values or {})
        execution.n8n_execution_id = n8n_id
        db.commit()
    except Exception:
        execution.status = "failed"
        execution.error = "Failed to connect to n8n"
        execution.completed_at = datetime.utcnow()
        db.commit()

    db.refresh(execution)
    return {"status": "success", "data": build_execution_out(execution)}

@router.get("")
def list_executions(
    workflow_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Execution)
    if workflow_id:
        query = query.filter(Execution.workflow_id == workflow_id)
    if status:
        query = query.filter(Execution.status == status)
    total = query.count()
    executions = query.order_by(Execution.started_at.desc()).offset((page - 1) * limit).limit(limit).all()
    return {
        "status": "success",
        "data": {
            "items": [build_execution_out(e) for e in executions],
            "total": total, "page": page, "limit": limit,
            "total_pages": ceil(total / limit)
        }
    }

@router.get("/{execution_id}")
def get_execution(execution_id: str, db: Session = Depends(get_db)):
    ex = db.query(Execution).filter(Execution.id == execution_id).first()
    if not ex:
        raise HTTPException(status_code=404, detail={"message": "Execution not found", "code": 404})
    return {"status": "success", "data": build_execution_out(ex)}

@router.post("/{execution_id}/cancel")
async def cancel_execution(execution_id: str, db: Session = Depends(get_db)):
    ex = db.query(Execution).filter(Execution.id == execution_id).first()
    if not ex:
        raise HTTPException(status_code=404, detail={"message": "Execution not found", "code": 404})
    if ex.status != "running":
        raise HTTPException(status_code=422, detail={"message": "Cannot cancel an execution that is already completed", "code": 422})

    if ex.n8n_execution_id:
        await cancel_n8n_execution(ex.n8n_execution_id)

    ex.status = "cancelled"
    ex.completed_at = datetime.utcnow()
    db.commit()
    return {"status": "success", "message": "Execution cancelled successfully"}

@router.post("/{execution_id}/webhook")
def execution_webhook(execution_id: str, body: WebhookUpdate, db: Session = Depends(get_db)):
    ex = db.query(Execution).filter(Execution.id == execution_id).first()
    if not ex:
        raise HTTPException(status_code=404, detail={"message": "Execution not found", "code": 404})
    ex.status = body.status
    ex.result = body.result
    ex.error = body.error
    ex.n8n_execution_id = body.n8n_execution_id
    ex.completed_at = datetime.utcnow()
    db.commit()
    return {"status": "success", "message": "Execution result recorded"}

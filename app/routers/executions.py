from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from math import ceil
from datetime import datetime
import uuid
from app.database import get_db

def is_valid_uuid(val: str) -> bool:
    try:
        uuid.UUID(val)
        return True
    except ValueError:
        return False
from app.models.execution import Execution
from app.models.workflow import Workflow
from app.schemas.execution import ExecutionCreate, ExecutionOut, ExecutionWorkflowOut
from app.schemas.node_execution import NodeExecutionOut

router = APIRouter(prefix="/executions", tags=["Executions"])

def build_execution_out(ex: Execution) -> ExecutionOut:
    node_execs = [
        NodeExecutionOut(
            id=ne.id, workflow_node_id=ne.workflow_node_id, status=ne.status,
            input_snapshot=ne.input_snapshot, output_snapshot=ne.output_snapshot,
            error_log=ne.error_log, started_at=ne.started_at,
            finished_at=ne.finished_at, created_at=ne.created_at
        ) for ne in ex.node_executions
    ]
    return ExecutionOut(
        id=ex.id,
        workflow=ExecutionWorkflowOut(id=ex.workflow.id, name=ex.workflow.name),
        status=ex.status,
        input_variables=ex.input_variables,
        output_variables=ex.output_variables,
        started_at=ex.started_at,
        finished_at=ex.finished_at,
        created_at=ex.created_at,
        node_executions=node_execs
    )

@router.post("", status_code=201)
def trigger_execution(body: ExecutionCreate, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == body.workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail={"message": "Workflow not found", "code": 404})
    if wf.status != "ACTIVE":
        raise HTTPException(status_code=422, detail={"message": "Only active workflows can be executed", "code": 422})
    if not wf.nodes:
        raise HTTPException(status_code=422, detail={"message": "Cannot execute a workflow with no nodes", "code": 422})

    execution = Execution(workflow_id=wf.id, input_variables=body.input_variables or {}, started_at=datetime.utcnow())
    db.add(execution)
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
    if not is_valid_uuid(execution_id):
        raise HTTPException(status_code=404, detail={"message": "Execution not found", "code": 404})
    ex = db.query(Execution).filter(Execution.id == execution_id).first()
    if not ex:
        raise HTTPException(status_code=404, detail={"message": "Execution not found", "code": 404})
    return {"status": "success", "data": build_execution_out(ex)}

@router.patch("/{execution_id}/complete")
def complete_execution(execution_id: str, db: Session = Depends(get_db)):
    if not is_valid_uuid(execution_id):
        raise HTTPException(status_code=404, detail={"message": "Execution not found", "code": 404})
    ex = db.query(Execution).filter(Execution.id == execution_id).first()
    if not ex:
        raise HTTPException(status_code=404, detail={"message": "Execution not found", "code": 404})
    if ex.status != "running":
        raise HTTPException(status_code=422, detail={"message": "Execution is not running", "code": 422})
    ex.status = "completed"
    ex.finished_at = datetime.utcnow()
    db.commit()
    return {"status": "success", "message": "Execution marked as completed"}

@router.patch("/{execution_id}/cancel")
def cancel_execution(execution_id: str, db: Session = Depends(get_db)):
    if not is_valid_uuid(execution_id):
        raise HTTPException(status_code=404, detail={"message": "Execution not found", "code": 404})
    ex = db.query(Execution).filter(Execution.id == execution_id).first()
    if not ex:
        raise HTTPException(status_code=404, detail={"message": "Execution not found", "code": 404})
    if ex.status not in ("PENDING", "RUNNING"):
        raise HTTPException(status_code=422, detail={"message": "Can only cancel a pending or running execution", "code": 422})
    ex.status = "FAILED"
    ex.finished_at = datetime.utcnow()
    db.commit()
    return {"status": "success", "message": "Execution cancelled successfully"}

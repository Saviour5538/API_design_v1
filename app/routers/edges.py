from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
from app.database import get_db
from app.models.workflow import Workflow
from app.models.node import Node
from app.models.workflow_edge import WorkflowEdge
from app.schemas.workflow_edge import EdgeCreate, EdgeOut

router = APIRouter(prefix="/workflows", tags=["Edges"])

def is_valid_uuid(val: str) -> bool:
    try:
        uuid.UUID(val)
        return True
    except ValueError:
        return False

def get_workflow_or_404(workflow_id: str, db: Session) -> Workflow:
    if not is_valid_uuid(workflow_id):
        raise HTTPException(status_code=404, detail={"message": "Workflow not found", "code": 404})
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail={"message": "Workflow not found", "code": 404})
    return wf

@router.get("/{workflow_id}/edges")
def list_edges(workflow_id: str, db: Session = Depends(get_db)):
    get_workflow_or_404(workflow_id, db)
    node_ids = [n.id for n in db.query(Node).filter(Node.workflow_id == workflow_id).all()]
    if not node_ids:
        return {"status": "success", "data": {"items": [], "total": 0}}
    edges = db.query(WorkflowEdge).filter(WorkflowEdge.src_id.in_(node_ids)).all()
    return {"status": "success", "data": {"items": [EdgeOut(id=e.id, src_id=e.src_id, dest_id=e.dest_id, created_at=e.created_at) for e in edges], "total": len(edges)}}

@router.post("/{workflow_id}/edges", status_code=201)
def create_edge(workflow_id: str, body: EdgeCreate, db: Session = Depends(get_db)):
    wf = get_workflow_or_404(workflow_id, db)
    if wf.status == "ACTIVE":
        raise HTTPException(status_code=422, detail={"message": "Cannot add edges to an active workflow, set it to draft first", "code": 422})

    if not is_valid_uuid(body.src_id) or not is_valid_uuid(body.dest_id):
        raise HTTPException(status_code=422, detail={"message": "Validation failed", "code": 422, "errors": [{"field": "src_id/dest_id", "issue": "must be valid UUIDs"}]})

    if body.src_id == body.dest_id:
        raise HTTPException(status_code=422, detail={"message": "Validation failed", "code": 422, "errors": [{"field": "dest_id", "issue": "src and dest cannot be the same node"}]})

    src = db.query(Node).filter(Node.id == body.src_id, Node.workflow_id == workflow_id).first()
    if not src:
        raise HTTPException(status_code=422, detail={"message": "Validation failed", "code": 422, "errors": [{"field": "src_id", "issue": "node not found in this workflow"}]})

    dest = db.query(Node).filter(Node.id == body.dest_id, Node.workflow_id == workflow_id).first()
    if not dest:
        raise HTTPException(status_code=422, detail={"message": "Validation failed", "code": 422, "errors": [{"field": "dest_id", "issue": "node not found in this workflow"}]})

    existing = db.query(WorkflowEdge).filter(WorkflowEdge.src_id == body.src_id, WorkflowEdge.dest_id == body.dest_id).first()
    if existing:
        raise HTTPException(status_code=422, detail={"message": "Edge already exists between these nodes", "code": 422})

    edge = WorkflowEdge(src_id=body.src_id, dest_id=body.dest_id)
    db.add(edge)
    db.commit()
    db.refresh(edge)
    return {"status": "success", "data": EdgeOut(id=edge.id, src_id=edge.src_id, dest_id=edge.dest_id, created_at=edge.created_at)}

@router.delete("/{workflow_id}/edges/{edge_id}")
def delete_edge(workflow_id: str, edge_id: str, db: Session = Depends(get_db)):
    wf = get_workflow_or_404(workflow_id, db)
    if wf.status == "ACTIVE":
        raise HTTPException(status_code=422, detail={"message": "Cannot remove edges from an active workflow, set it to draft first", "code": 422})

    if not is_valid_uuid(edge_id):
        raise HTTPException(status_code=404, detail={"message": "Edge not found", "code": 404})

    node_ids = [n.id for n in db.query(Node).filter(Node.workflow_id == workflow_id).all()]
    edge = db.query(WorkflowEdge).filter(WorkflowEdge.id == edge_id, WorkflowEdge.src_id.in_(node_ids)).first()
    if not edge:
        raise HTTPException(status_code=404, detail={"message": "Edge not found in this workflow", "code": 404})

    db.delete(edge)
    db.commit()
    return {"status": "success", "message": "Edge removed successfully"}

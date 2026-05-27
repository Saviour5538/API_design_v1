from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
import uuid
from app.database import get_db
from app.models.workflow import Workflow
from app.models.workflow_data import WorkflowData
from app.schemas.workflow_edge import EdgeCreate

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

def get_or_create_workflow_data(workflow_id: str, db: Session) -> WorkflowData:
    wd = db.query(WorkflowData).filter(WorkflowData.workflow_id == workflow_id).first()
    if not wd:
        wd = WorkflowData(workflow_id=workflow_id, nodes=[], edges=[])
        db.add(wd)
        db.commit()
        db.refresh(wd)
    return wd

@router.get("/{workflow_id}/edges")
def list_edges(workflow_id: str, db: Session = Depends(get_db)):
    get_workflow_or_404(workflow_id, db)
    wd = get_or_create_workflow_data(workflow_id, db)
    edges = wd.edges or []
    return {"status": "success", "data": {"items": edges, "total": len(edges)}}

@router.post("/{workflow_id}/edges", status_code=201)
def create_edge(workflow_id: str, body: EdgeCreate, db: Session = Depends(get_db)):
    wf = get_workflow_or_404(workflow_id, db)
    if wf.status != "DRAFT":
        raise HTTPException(status_code=422, detail={"message": "Cannot add edges to a non-draft workflow", "code": 422})

    if not is_valid_uuid(body.src_id) or not is_valid_uuid(body.dest_id):
        raise HTTPException(status_code=422, detail={"message": "Validation failed", "code": 422, "errors": [{"field": "src_id/dest_id", "issue": "must be valid UUIDs"}]})

    if body.src_id == body.dest_id:
        raise HTTPException(status_code=422, detail={"message": "Validation failed", "code": 422, "errors": [{"field": "dest_id", "issue": "src and dest cannot be the same node"}]})

    wd = get_or_create_workflow_data(workflow_id, db)
    nodes = wd.nodes or []
    node_ids = {n["id"] for n in nodes}

    if body.src_id not in node_ids:
        raise HTTPException(status_code=422, detail={"message": "Validation failed", "code": 422, "errors": [{"field": "src_id", "issue": "node not found in this workflow"}]})
    if body.dest_id not in node_ids:
        raise HTTPException(status_code=422, detail={"message": "Validation failed", "code": 422, "errors": [{"field": "dest_id", "issue": "node not found in this workflow"}]})

    edges = list(wd.edges or [])
    existing = next((e for e in edges if e["src_id"] == body.src_id and e["dest_id"] == body.dest_id), None)
    if existing:
        raise HTTPException(status_code=422, detail={"message": "Edge already exists between these nodes", "code": 422})

    new_edge = {"id": str(uuid.uuid4()), "src_id": body.src_id, "dest_id": body.dest_id}
    edges.append(new_edge)
    wd.edges = edges
    flag_modified(wd, "edges")
    db.commit()
    return {"status": "success", "data": new_edge}

@router.delete("/{workflow_id}/edges/{edge_id}")
def delete_edge(workflow_id: str, edge_id: str, db: Session = Depends(get_db)):
    wf = get_workflow_or_404(workflow_id, db)
    if wf.status != "DRAFT":
        raise HTTPException(status_code=422, detail={"message": "Cannot remove edges from a non-draft workflow", "code": 422})

    if not is_valid_uuid(edge_id):
        raise HTTPException(status_code=404, detail={"message": "Edge not found", "code": 404})

    wd = get_or_create_workflow_data(workflow_id, db)
    edges = list(wd.edges or [])
    edge = next((e for e in edges if e["id"] == edge_id), None)
    if not edge:
        raise HTTPException(status_code=404, detail={"message": "Edge not found in this workflow", "code": 404})

    wd.edges = [e for e in edges if e["id"] != edge_id]
    flag_modified(wd, "edges")
    db.commit()
    return {"status": "success", "message": "Edge removed successfully"}

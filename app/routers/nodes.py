from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
import uuid
from app.database import get_db
from app.models.workflow import Workflow
from app.models.workflow_data import WorkflowData
from app.models.agent import Agent
from app.models.category import Category
from app.schemas.node import NodeCreate, NodeUpdate

router = APIRouter(prefix="/workflows", tags=["Nodes"])

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

def enrich_node(node_data: dict, workflow_id: str, db: Session) -> dict:
    agent_id = node_data.get("node_id")
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    cat = db.query(Category).filter(Category.id == agent.category_id).first() if (agent and agent.category_id) else None
    return {
        "id": node_data["id"],
        "node_id": node_data["node_id"],
        "agent": {
            "id": agent.id if agent else node_data["node_id"],
            "name": agent.name if agent else "Unknown",
            "category": cat.name if cat else None
        },
        "config": node_data.get("config", []),
        "ui_meta": node_data.get("ui_meta"),
        "workflow_id": workflow_id
    }

@router.get("/{workflow_id}/nodes")
def list_nodes(workflow_id: str, db: Session = Depends(get_db)):
    get_workflow_or_404(workflow_id, db)
    wd = get_or_create_workflow_data(workflow_id, db)
    nodes = wd.nodes or []
    return {"status": "success", "data": {"items": [enrich_node(n, workflow_id, db) for n in nodes], "total": len(nodes)}}

@router.get("/{workflow_id}/nodes/{node_id}")
def get_node(workflow_id: str, node_id: str, db: Session = Depends(get_db)):
    get_workflow_or_404(workflow_id, db)
    if not is_valid_uuid(node_id):
        raise HTTPException(status_code=404, detail={"message": "Node not found in this workflow", "code": 404})
    wd = get_or_create_workflow_data(workflow_id, db)
    node_data = next((n for n in (wd.nodes or []) if n["id"] == node_id), None)
    if not node_data:
        raise HTTPException(status_code=404, detail={"message": "Node not found in this workflow", "code": 404})
    return {"status": "success", "data": enrich_node(node_data, workflow_id, db)}

@router.post("/{workflow_id}/nodes", status_code=201)
def create_node(workflow_id: str, body: NodeCreate, db: Session = Depends(get_db)):
    wf = get_workflow_or_404(workflow_id, db)
    if wf.status != "DRAFT":
        raise HTTPException(status_code=422, detail={"message": "Cannot add nodes to a non-draft workflow", "code": 422})

    if not is_valid_uuid(body.node_id):
        raise HTTPException(status_code=422, detail={"message": "Validation failed", "code": 422, "errors": [{"field": "node_id", "issue": "must be a valid UUID"}]})

    agent = db.query(Agent).filter(Agent.id == body.node_id).first()
    if not agent:
        raise HTTPException(status_code=422, detail={"message": "Validation failed", "code": 422, "errors": [{"field": "node_id", "issue": "agent not found"}]})

    wd = get_or_create_workflow_data(workflow_id, db)
    nodes = list(wd.nodes or [])

    new_node = {
        "id": str(uuid.uuid4()),
        "node_id": body.node_id,
        "config": [{"var_name": c.var_name, "value": c.value} for c in (body.config or [])],
        "ui_meta": {"x": body.ui_meta.x, "y": body.ui_meta.y, "label": body.ui_meta.label} if body.ui_meta else {"x": 0, "y": 0, "label": None}
    }
    nodes.append(new_node)
    wd.nodes = nodes
    flag_modified(wd, "nodes")
    db.commit()
    db.refresh(wd)
    return {"status": "success", "data": enrich_node(new_node, workflow_id, db)}

@router.patch("/{workflow_id}/nodes/{node_id}")
def update_node(workflow_id: str, node_id: str, body: NodeUpdate, db: Session = Depends(get_db)):
    wf = get_workflow_or_404(workflow_id, db)
    if wf.status != "DRAFT":
        raise HTTPException(status_code=422, detail={"message": "Cannot edit nodes in a non-draft workflow", "code": 422})

    if not is_valid_uuid(node_id):
        raise HTTPException(status_code=404, detail={"message": "Node not found in this workflow", "code": 404})

    wd = get_or_create_workflow_data(workflow_id, db)
    nodes = list(wd.nodes or [])
    idx = next((i for i, n in enumerate(nodes) if n["id"] == node_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail={"message": "Node not found in this workflow", "code": 404})

    if body.config is not None:
        nodes[idx]["config"] = [{"var_name": c.var_name, "value": c.value} for c in body.config]

    if body.ui_meta is not None:
        nodes[idx]["ui_meta"] = {"x": body.ui_meta.x, "y": body.ui_meta.y, "label": body.ui_meta.label}

    wd.nodes = nodes
    flag_modified(wd, "nodes")
    db.commit()
    db.refresh(wd)
    return {"status": "success", "data": enrich_node(nodes[idx], workflow_id, db)}

@router.delete("/{workflow_id}/nodes/{node_id}")
def delete_node(workflow_id: str, node_id: str, db: Session = Depends(get_db)):
    wf = get_workflow_or_404(workflow_id, db)
    if wf.status != "DRAFT":
        raise HTTPException(status_code=422, detail={"message": "Cannot remove nodes from a non-draft workflow", "code": 422})

    if not is_valid_uuid(node_id):
        raise HTTPException(status_code=404, detail={"message": "Node not found in this workflow", "code": 404})

    wd = get_or_create_workflow_data(workflow_id, db)
    nodes = list(wd.nodes or [])
    node_data = next((n for n in nodes if n["id"] == node_id), None)
    if not node_data:
        raise HTTPException(status_code=404, detail={"message": "Node not found in this workflow", "code": 404})

    from app.models.node_execution import NodeExecution
    has_history = db.query(NodeExecution).filter(NodeExecution.workflow_node_id == node_id).first()
    if has_history:
        raise HTTPException(status_code=422, detail={"message": "Cannot remove a node that has execution history", "code": 422})

    wd.nodes = [n for n in nodes if n["id"] != node_id]
    edges = [e for e in (wd.edges or []) if e["src_id"] != node_id and e["dest_id"] != node_id]
    wd.edges = edges
    flag_modified(wd, "nodes")
    flag_modified(wd, "edges")
    db.commit()
    return {"status": "success", "message": "Node removed from workflow successfully"}

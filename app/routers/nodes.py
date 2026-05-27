from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.workflow import Workflow
from app.models.node import Node
from app.models.agent import Agent
from app.models.category import Category
from app.models.workflow_node_config import WorkflowNodeConfig
from app.schemas.node import NodeCreate, NodeUpdate, NodeOut, NodeAgentOut, NodeConfigOut

router = APIRouter(prefix="/workflows", tags=["Nodes"])

def get_workflow_or_404(workflow_id: str, db: Session) -> Workflow:
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail={"message": "Workflow not found", "code": 404})
    return wf

def build_node_out(node: Node, db: Session) -> NodeOut:
    agent = db.query(Agent).filter(Agent.id == node.node_id).first()
    cat = db.query(Category).filter(Category.id == agent.category_id).first() if (agent and agent.category_id) else None
    cfgs = [NodeConfigOut(id=c.id, var_name=c.var_name, value=c.value) for c in node.configs]
    return NodeOut(
        id=node.id,
        node_id=node.node_id,
        agent=NodeAgentOut(
            id=agent.id, name=agent.name, category=cat.name if cat else None
        ) if agent else NodeAgentOut(id=node.node_id, name="Unknown", category=None),
        configs=cfgs,
        workflow_id=node.workflow_id,
        created_at=node.created_at, updated_at=node.updated_at
    )

@router.get("/{workflow_id}/nodes")
def list_nodes(workflow_id: str, db: Session = Depends(get_db)):
    get_workflow_or_404(workflow_id, db)
    nodes = db.query(Node).filter(Node.workflow_id == workflow_id).all()
    return {"status": "success", "data": {"items": [build_node_out(n, db) for n in nodes], "total": len(nodes)}}

@router.get("/{workflow_id}/nodes/{node_id}")
def get_node(workflow_id: str, node_id: str, db: Session = Depends(get_db)):
    get_workflow_or_404(workflow_id, db)
    node = db.query(Node).filter(Node.id == node_id, Node.workflow_id == workflow_id).first()
    if not node:
        raise HTTPException(status_code=404, detail={"message": "Node not found in this workflow", "code": 404})
    return {"status": "success", "data": build_node_out(node, db)}

@router.post("/{workflow_id}/nodes", status_code=201)
def create_node(workflow_id: str, body: NodeCreate, db: Session = Depends(get_db)):
    wf = get_workflow_or_404(workflow_id, db)
    if wf.status == "ACTIVE":
        raise HTTPException(status_code=422, detail={"message": "Cannot add nodes to an active workflow, set it to draft first", "code": 422})

    agent = db.query(Agent).filter(Agent.id == body.node_id).first()
    if not agent:
        raise HTTPException(status_code=422, detail={
            "message": "Validation failed", "code": 422,
            "errors": [{"field": "node_id", "issue": "agent not found"}]
        })

    node = Node(node_id=body.node_id, workflow_id=workflow_id)
    db.add(node)
    db.flush()

    for cfg in (body.configs or []):
        db.add(WorkflowNodeConfig(workflow_node_id=node.id, var_name=cfg.var_name, value=cfg.value))

    db.commit()
    db.refresh(node)
    return {"status": "success", "data": build_node_out(node, db)}

@router.patch("/{workflow_id}/nodes/{node_id}")
def update_node(workflow_id: str, node_id: str, body: NodeUpdate, db: Session = Depends(get_db)):
    wf = get_workflow_or_404(workflow_id, db)
    if wf.status == "ACTIVE":
        raise HTTPException(status_code=422, detail={"message": "Cannot edit nodes in an active workflow, set it to draft first", "code": 422})

    node = db.query(Node).filter(Node.id == node_id, Node.workflow_id == workflow_id).first()
    if not node:
        raise HTTPException(status_code=404, detail={"message": "Node not found in this workflow", "code": 404})

    if body.configs is not None:
        db.query(WorkflowNodeConfig).filter(WorkflowNodeConfig.workflow_node_id == node.id).delete()
        for cfg in body.configs:
            db.add(WorkflowNodeConfig(workflow_node_id=node.id, var_name=cfg.var_name, value=cfg.value))

    db.commit()
    db.refresh(node)
    return {"status": "success", "data": build_node_out(node, db)}

@router.delete("/{workflow_id}/nodes/{node_id}")
def delete_node(workflow_id: str, node_id: str, db: Session = Depends(get_db)):
    wf = get_workflow_or_404(workflow_id, db)
    if wf.status == "ACTIVE":
        raise HTTPException(status_code=422, detail={"message": "Cannot remove nodes from an active workflow, set it to draft first", "code": 422})

    node = db.query(Node).filter(Node.id == node_id, Node.workflow_id == workflow_id).first()
    if not node:
        raise HTTPException(status_code=404, detail={"message": "Node not found in this workflow", "code": 404})

    db.delete(node)
    db.commit()
    return {"status": "success", "message": "Node removed from workflow successfully"}

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.workflow import Workflow
from app.models.node import Node
from app.models.agent import Agent
from app.schemas.node import NodeCreate, NodeUpdate, NodeOut, NodeAgentOut, NodeListOut

router = APIRouter(prefix="/workflows", tags=["Nodes"])

def get_workflow_or_404(workflow_id: str, db: Session) -> Workflow:
    wf = db.query(Workflow).filter(Workflow.id == workflow_id, Workflow.deleted_at == None).first()
    if not wf:
        raise HTTPException(status_code=404, detail={"message": "Workflow not found", "code": 404})
    return wf

def build_node_out(node: Node) -> NodeOut:
    return NodeOut(
        id=node.id, name=node.name, order=node.order,
        agent=NodeAgentOut(id=node.agent.id, name=node.agent.name, category=node.agent.category.name),
        input_values=node.input_values or {},
        workflow_id=node.workflow_id,
        created_at=node.created_at, updated_at=node.updated_at
    )

@router.get("/{workflow_id}/nodes")
def list_nodes(workflow_id: str, db: Session = Depends(get_db)):
    get_workflow_or_404(workflow_id, db)
    nodes = db.query(Node).filter(Node.workflow_id == workflow_id).order_by(Node.order).all()
    return {"status": "success", "data": {"items": [build_node_out(n) for n in nodes], "total": len(nodes)}}

@router.get("/{workflow_id}/nodes/{node_id}")
def get_node(workflow_id: str, node_id: str, db: Session = Depends(get_db)):
    get_workflow_or_404(workflow_id, db)
    node = db.query(Node).filter(Node.id == node_id, Node.workflow_id == workflow_id).first()
    if not node:
        raise HTTPException(status_code=404, detail={"message": "Node not found in this workflow", "code": 404})
    return {"status": "success", "data": build_node_out(node)}

@router.post("/{workflow_id}/nodes", status_code=201)
def create_node(workflow_id: str, body: NodeCreate, db: Session = Depends(get_db)):
    wf = get_workflow_or_404(workflow_id, db)
    if wf.status == "active":
        raise HTTPException(status_code=422, detail={"message": "Cannot add nodes to an active workflow, set it to draft first", "code": 422})

    agent = db.query(Agent).filter(Agent.id == body.agent_id).first()
    if not agent or not agent.is_active:
        raise HTTPException(status_code=422, detail={
            "message": "Validation failed", "code": 422,
            "errors": [{"field": "agent_id", "issue": "agent not found or inactive"}]
        })

    node = Node(
        name=body.name, agent_id=body.agent_id,
        order=body.order, workflow_id=workflow_id,
        input_values=body.input_values or {}
    )
    db.add(node)
    db.commit()
    db.refresh(node)
    return {"status": "success", "data": build_node_out(node)}

@router.patch("/{workflow_id}/nodes/{node_id}")
def update_node(workflow_id: str, node_id: str, body: NodeUpdate, db: Session = Depends(get_db)):
    wf = get_workflow_or_404(workflow_id, db)
    if wf.status == "active":
        raise HTTPException(status_code=422, detail={"message": "Cannot edit nodes in an active workflow, set it to draft first", "code": 422})

    node = db.query(Node).filter(Node.id == node_id, Node.workflow_id == workflow_id).first()
    if not node:
        raise HTTPException(status_code=404, detail={"message": "Node not found in this workflow", "code": 404})

    if body.name: node.name = body.name
    if body.order is not None: node.order = body.order
    if body.input_values is not None: node.input_values = body.input_values
    db.commit()
    db.refresh(node)
    return {"status": "success", "data": build_node_out(node)}

@router.delete("/{workflow_id}/nodes/{node_id}")
def delete_node(workflow_id: str, node_id: str, db: Session = Depends(get_db)):
    wf = get_workflow_or_404(workflow_id, db)
    if wf.status == "active":
        raise HTTPException(status_code=422, detail={"message": "Cannot remove nodes from an active workflow, set it to draft first", "code": 422})

    node = db.query(Node).filter(Node.id == node_id, Node.workflow_id == workflow_id).first()
    if not node:
        raise HTTPException(status_code=404, detail={"message": "Node not found in this workflow", "code": 404})

    db.delete(node)
    db.commit()
    return {"status": "success", "message": "Node removed from workflow successfully"}

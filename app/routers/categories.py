from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from math import ceil
from app.database import get_db
from app.models.category import Category
from app.models.agent import Agent
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("")
def list_categories(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    total = db.query(Category).count()
    categories = db.query(Category).offset((page - 1) * limit).limit(limit).all()
    items = []
    for cat in categories:
        agent_count = db.query(Agent).filter(Agent.category_id == cat.id).count()
        items.append(CategoryOut(id=cat.id, name=cat.name, color=cat.color, agent_count=agent_count))
    return {"status": "success", "data": {"items": items, "total": total, "page": page, "limit": limit, "total_pages": ceil(total / limit)}}

@router.get("/{category_id}")
def get_category(category_id: str, db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail={"message": "Category not found", "code": 404})
    agent_count = db.query(Agent).filter(Agent.category_id == cat.id).count()
    return {"status": "success", "data": CategoryOut(id=cat.id, name=cat.name, color=cat.color, agent_count=agent_count)}

@router.post("", status_code=201)
def create_category(body: CategoryCreate, db: Session = Depends(get_db)):
    if db.query(Category).filter(Category.name == body.name).first():
        raise HTTPException(status_code=422, detail={
            "message": "Validation failed", "code": 422,
            "errors": [{"field": "name", "issue": "category name already exists"}]
        })
    cat = Category(name=body.name, color=body.color)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return {"status": "success", "data": CategoryOut(id=cat.id, name=cat.name, color=cat.color, agent_count=0)}

@router.patch("/{category_id}")
def update_category(category_id: str, body: CategoryUpdate, db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail={"message": "Category not found", "code": 404})
    if body.name:
        cat.name = body.name
    if body.color is not None:
        cat.color = body.color
    db.commit()
    db.refresh(cat)
    agent_count = db.query(Agent).filter(Agent.category_id == cat.id).count()
    return {"status": "success", "data": CategoryOut(id=cat.id, name=cat.name, color=cat.color, agent_count=agent_count)}

@router.delete("/{category_id}")
def delete_category(category_id: str, db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail={"message": "Category not found", "code": 404})
    agent_count = db.query(Agent).filter(Agent.category_id == category_id).count()
    if agent_count > 0:
        raise HTTPException(status_code=422, detail={"message": "Cannot delete category with existing agents", "code": 422})
    db.delete(cat)
    db.commit()
    return {"status": "success", "message": "Category deleted successfully"}

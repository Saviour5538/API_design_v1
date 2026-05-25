from app.database import SessionLocal
from app.models.agent import Agent
from app.models.category import Category

db = SessionLocal()

finance_cat = db.query(Category).filter(Category.name == "Finance").first()
if not finance_cat:
    print("Finance category not found. Run the app first and create the Finance category.")
    db.close()
    exit()

agents_data = [
    {
        "name": "Invoice Processor",
        "description": "Extracts and processes invoice data automatically",
        "category_id": finance_cat.id,
        "n8n_workflow_id": "n8n_wf_001",
        "inputs": [{"name": "file_url", "type": "string", "required": True}],
        "is_active": True
    },
    {
        "name": "Payment Reconciliation",
        "description": "Reconciles payments against bank statements",
        "category_id": finance_cat.id,
        "n8n_workflow_id": "n8n_wf_002",
        "inputs": [{"name": "statement_url", "type": "string", "required": True}],
        "is_active": True
    },
    {
        "name": "Expense Classifier",
        "description": "Classifies and categorizes business expenses",
        "category_id": finance_cat.id,
        "n8n_workflow_id": "n8n_wf_003",
        "inputs": [{"name": "expense_data", "type": "object", "required": True}],
        "is_active": True
    },
]

for data in agents_data:
    existing = db.query(Agent).filter(Agent.name == data["name"]).first()
    if not existing:
        db.add(Agent(**data))
        print(f"Added agent: {data['name']}")
    else:
        print(f"Skipped (already exists): {data['name']}")

db.commit()
db.close()
print("Done.")

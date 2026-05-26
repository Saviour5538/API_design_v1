# Workflow Builder API

A REST API for managing AI agent workflows built with FastAPI and SQLite. This API powers a platform that lets users browse pre-built AI agents and compose them into automated workflows that run on n8n.

Authentication is handled externally — all endpoints are open.

---

## What This Is

The platform has pre-built AI agents (Invoice Processor, Expense Classifier, etc.), each backed by an n8n workflow. Users can:

1. Browse agents by category
2. Create their own workflows by chaining agents as nodes
3. Execute workflows (which trigger n8n behind the scenes)
4. Track execution history and results

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.x | Language |
| FastAPI | Web framework, auto-generates Swagger UI |
| SQLAlchemy | ORM for database models |
| SQLite | Database (file-based, zero install) |
| Pydantic v2 + pydantic-settings | Request/response validation and env config |
| httpx | HTTP client for calling n8n |
| uvicorn | ASGI server to run the app |

---

## Project Structure

```
API_Design/
├── app/
│   ├── main.py           # App entry point, router registration, OpenAPI config
│   ├── database.py       # SQLAlchemy engine and session setup
│   ├── config.py         # Reads .env via pydantic-settings
│   ├── models/           # SQLAlchemy database models
│   │   ├── category.py
│   │   ├── agent.py
│   │   ├── workflow.py
│   │   ├── node.py
│   │   └── execution.py
│   ├── schemas/          # Pydantic request/response schemas
│   │   ├── category.py
│   │   ├── agent.py
│   │   ├── workflow.py
│   │   ├── node.py
│   │   └── execution.py
│   ├── routers/          # Endpoint definitions
│   │   ├── categories.py
│   │   ├── agents.py
│   │   ├── workflows.py
│   │   ├── nodes.py
│   │   └── executions.py
│   └── services/
│       └── n8n.py        # HTTP calls to trigger/cancel n8n workflows
├── seed_agents.py        # Script to seed test agents into the database
├── .env                  # Environment variables (not committed)
├── .env.example          # Template for .env
├── API_REFERENCE.md      # Full endpoint and payload reference
├── requirements.txt
└── workflow.db           # SQLite database file (auto-created on first run)
```

---

## Setup

### 1. Create and activate virtual environment

```powershell
python -m venv venv
venv\Scripts\Activate
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Create `.env` file

```env
DATABASE_URL=sqlite:///./workflow.db
N8N_BASE_URL=http://localhost:5678
N8N_API_KEY=your-n8n-api-key
```

### 4. Run the server

```powershell
venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The database tables are created automatically on first run.

### 5. Seed test agents (optional, for testing)

First create a "Finance" category via the API, then run:

```powershell
venv\Scripts\python seed_agents.py
```

### 6. Open Swagger UI

Navigate to `http://localhost:8000/docs`

---

## API Endpoints

Base URL: `http://localhost:8000/api/v1`

### Health
| Method | Path | Description |
|---|---|---|
| GET | `/health` | Check if server is online |

### Categories
| Method | Path | Description |
|---|---|---|
| POST | `/categories` | Create a category |
| GET | `/categories` | List all categories |
| GET | `/categories/{category_id}` | Get a single category |
| PATCH | `/categories/{category_id}` | Update a category |
| DELETE | `/categories/{category_id}` | Delete a category |

### Agents
Agents are pre-seeded by admins — end users can only read them.

| Method | Path | Description |
|---|---|---|
| GET | `/agents` | List all agents (filter by category, search by name) |
| GET | `/agents/{agent_id}` | Get a single agent with its input schema |

### Workflows
| Method | Path | Description |
|---|---|---|
| POST | `/workflows` | Create a new workflow |
| GET | `/workflows` | List workflows (filter by status, search by name) |
| GET | `/workflows/{workflow_id}` | Get workflow with all its nodes |
| PATCH | `/workflows/{workflow_id}` | Update name, description, or status |
| DELETE | `/workflows/{workflow_id}` | Soft delete a workflow |

### Nodes
Nodes are the agents inside a workflow, in order. A workflow must be in `draft` status to add/edit/remove nodes.

| Method | Path | Description |
|---|---|---|
| POST | `/workflows/{workflow_id}/nodes` | Add a node (agent) to a workflow |
| GET | `/workflows/{workflow_id}/nodes` | List all nodes in a workflow |
| GET | `/workflows/{workflow_id}/nodes/{node_id}` | Get a single node |
| PATCH | `/workflows/{workflow_id}/nodes/{node_id}` | Update node order or input values |
| DELETE | `/workflows/{workflow_id}/nodes/{node_id}` | Remove a node from a workflow |

### Executions
Only `active` workflows with at least one node can be executed.

| Method | Path | Description |
|---|---|---|
| POST | `/executions` | Trigger a workflow execution (calls n8n) |
| GET | `/executions` | List executions (filter by workflow_id or status) |
| GET | `/executions/{execution_id}` | Get execution details and result |
| POST | `/executions/{execution_id}/cancel` | Cancel a running execution |
| POST | `/executions/{execution_id}/webhook` | n8n webhook to update execution result |

For full request/response payloads see [API_REFERENCE.md](API_REFERENCE.md).

---

## Resource IDs

Every resource has a prefixed unique ID generated automatically:

| Resource | Prefix | Example |
|---|---|---|
| Category | `cat_` | `cat_6c28cdbb` |
| Agent | `agt_` | `agt_3f9a1b2c` |
| Workflow | `wfl_` | `wfl_7d4e2a1f` |
| Node | `nod_` | `nod_1c8b5e3a` |
| Execution | `exc_` | `exc_9a2f4d7c` |

---

## Response Format

All responses follow the same envelope:

```json
{ "status": "success", "data": { ... } }

{ "status": "success", "data": { "items": [...], "total": 10, "page": 1, "limit": 10, "total_pages": 1 } }

{ "status": "success", "message": "Resource deleted successfully" }

{ "status": "error", "message": "Not found", "code": 404 }
```

---

## Workflow Status Lifecycle

```
draft → active → (execute) → completed / failed / cancelled
```

- A new workflow starts as `draft`
- Nodes can only be added/edited/removed when status is `draft`
- Set status to `active` before executing
- Cannot delete a workflow that has a running execution

---

## Notes

- If port 8000 is already in use: `Get-Process python | Stop-Process -Force`, then restart
- The SQLite database file `workflow.db` is created in the project root automatically

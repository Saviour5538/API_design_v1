# Workflow Builder API

A REST API for managing AI agent workflows built with FastAPI and PostgreSQL (Supabase). This API powers a platform that lets users browse pre-built AI agents and compose them into automated workflows.

Authentication is handled externally — all endpoints are open.

---

## What This Is

The platform has pre-built AI agents (HTTP GET, JSON Parser, Database Query, etc.), each defined with input/output schemas. Users can:

1. Browse agents by category
2. Create workflows by adding agents as nodes
3. Connect nodes with edges to define execution flow
4. Set node positions on a visual canvas (ui_meta)
5. Execute workflows and track per-execution history

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.x | Language |
| FastAPI | Web framework, auto-generates Swagger UI |
| SQLAlchemy | ORM for database models |
| PostgreSQL (Supabase) | Shared cloud database |
| Pydantic v2 + pydantic-settings | Request/response validation and env config |
| psycopg2-binary | PostgreSQL driver |
| uvicorn | ASGI server to run the app |

---

## Project Structure

```
API_Design/
├── app/
│   ├── main.py                      # App entry point, router registration
│   ├── database.py                  # SQLAlchemy engine and session setup
│   ├── config.py                    # Reads .env via pydantic-settings
│   ├── models/                      # SQLAlchemy database models
│   │   ├── category.py              # node_categories table
│   │   ├── agent.py                 # nodes table
│   │   ├── workflow.py              # workflows table
│   │   ├── node.py                  # workflow_nodes table
│   │   ├── workflow_node_config.py  # workflow_node_configs table
│   │   ├── workflow_edge.py         # workflow_edges table
│   │   ├── workflow_ui_meta.py      # workflow_ui_meta table
│   │   ├── execution.py             # workflow_executions table
│   │   ├── node_execution.py        # node_executions table
│   │   └── execution_join_counter.py# execution_join_counters table
│   ├── schemas/                     # Pydantic request/response schemas
│   │   ├── category.py
│   │   ├── agent.py
│   │   ├── workflow.py
│   │   ├── node.py
│   │   ├── workflow_edge.py
│   │   ├── node_execution.py
│   │   └── execution.py
│   ├── routers/                     # Endpoint definitions
│   │   ├── categories.py
│   │   ├── agents.py
│   │   ├── workflows.py
│   │   ├── nodes.py
│   │   ├── edges.py
│   │   └── executions.py
│   └── services/
│       └── n8n.py
├── .env                             # Environment variables (not committed)
├── .env.example                     # Template for .env
├── requirements.txt
└── README.md
```

---

## Database Schema

This API connects to a shared Supabase PostgreSQL database. It uses 10 tables:

| Table | Purpose | Access |
|---|---|---|
| `node_categories` | Agent categories with color labels | Read-only |
| `nodes` | Pre-built agents with input/output/configs schema | Read-only |
| `workflows` | User-created workflows | Read/Write |
| `workflow_nodes` | Agents added to a workflow | Read/Write |
| `workflow_node_configs` | Config values per node (var_name + value) | Read/Write |
| `workflow_edges` | Directed connections between nodes | Read/Write |
| `workflow_ui_meta` | Canvas x/y position per node | Read/Write |
| `workflow_executions` | Execution runs of a workflow | Read/Write |
| `node_executions` | Per-node execution tracking | Read |
| `execution_join_counters` | Internal execution engine table | Internal |

---

## Setup

### 1. Clone and create virtual environment

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
DATABASE_URL=postgresql://user:password@host:5432/postgres?sslmode=require
N8N_BASE_URL=http://localhost:5678
N8N_API_KEY=your-n8n-api-key
```

> Note: If your password contains `@`, URL-encode it as `%40`

### 4. Run the server

```powershell
uvicorn app.main:app --reload
```

Tables are created automatically on first run if they don't exist.

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
| GET | `/categories` | List all categories with agent count |
| GET | `/categories/{id}` | Get a single category |

### Agents
Agents are managed by the DB team — read-only via API.

| Method | Path | Description |
|---|---|---|
| GET | `/agents` | List all agents (filter by `category_id`, search by `name`) |
| GET | `/agents/{id}` | Get a single agent with input/output/configs schema |

### Workflows
| Method | Path | Description |
|---|---|---|
| POST | `/workflows` | Create a new workflow |
| GET | `/workflows` | List workflows (filter by `status`, search by `name`) |
| GET | `/workflows/{id}` | Get workflow with nodes, edges, ui_meta |
| PATCH | `/workflows/{id}` | Update name, description, or status |
| DELETE | `/workflows/{id}` | Delete workflow (blocked if execution history exists) |

### Nodes
A workflow must be in `DRAFT` status to add/edit/remove nodes.

| Method | Path | Description |
|---|---|---|
| POST | `/workflows/{id}/nodes` | Add a node with optional configs and ui_meta |
| GET | `/workflows/{id}/nodes` | List all nodes in a workflow |
| GET | `/workflows/{id}/nodes/{node_id}` | Get a single node |
| PATCH | `/workflows/{id}/nodes/{node_id}` | Update node configs or ui_meta position |
| DELETE | `/workflows/{id}/nodes/{node_id}` | Remove a node (blocked if execution history exists) |

### Edges
Directed connections between nodes. Workflow must be in `DRAFT` to edit.

| Method | Path | Description |
|---|---|---|
| POST | `/workflows/{id}/edges` | Connect two nodes (src → dest) |
| GET | `/workflows/{id}/edges` | List all edges in a workflow |
| DELETE | `/workflows/{id}/edges/{edge_id}` | Remove an edge |

### Executions
Only `ACTIVE` workflows with at least one node can be executed.

| Method | Path | Description |
|---|---|---|
| POST | `/executions` | Trigger a workflow execution |
| GET | `/executions` | List executions (filter by `workflow_id` or `status`) |
| GET | `/executions/{id}` | Get execution details with node_executions |
| PATCH | `/executions/{id}/cancel` | Cancel a pending or running execution |
| PATCH | `/executions/{id}/complete` | Mark execution as completed |

---

## Request/Response Examples

### Create Workflow
```json
POST /api/v1/workflows
{
    "name": "My Workflow",
    "description": "Optional description"
}
```

### Add Node
```json
POST /api/v1/workflows/{id}/nodes
{
    "node_id": "uuid-of-agent",
    "configs": [
        {"var_name": "url", "value": "https://api.example.com"}
    ],
    "ui_meta": {"x": 100, "y": 200}
}
```

### Add Edge
```json
POST /api/v1/workflows/{id}/edges
{
    "src_id": "workflow-node-uuid",
    "dest_id": "workflow-node-uuid"
}
```

### Trigger Execution
```json
POST /api/v1/executions
{
    "workflow_id": "workflow-uuid",
    "input_variables": {"key": "value"}
}
```

---

## Response Format

All responses use the same envelope:

```json
{ "status": "success", "data": { ... } }

{ "status": "success", "data": { "items": [...], "total": 10, "page": 1, "limit": 10, "total_pages": 1 } }

{ "status": "success", "message": "Deleted successfully" }

{ "detail": { "message": "Not found", "code": 404 } }
```

---

## Workflow Status Lifecycle

```
DRAFT → ACTIVE → (execute) → PENDING → RUNNING → COMPLETED / FAILED
```

- New workflows start as `DRAFT`
- Nodes and edges can only be added/edited/removed in `DRAFT`
- Set status to `ACTIVE` to allow execution
- Set status to `INACTIVE` to disable without deleting
- Cannot delete a workflow that has execution history

## Execution Status Values

| Status | Meaning |
|---|---|
| `PENDING` | Triggered, not yet picked up |
| `RUNNING` | Currently executing |
| `COMPLETED` | Finished successfully |
| `FAILED` | Failed or cancelled |

---

## Notes

- All IDs are UUIDs
- Status enums are uppercase: `DRAFT`, `ACTIVE`, `INACTIVE`, `PENDING`, `RUNNING`, `COMPLETED`, `FAILED`
- If port 8000 is in use: `Get-Process python | Stop-Process -Force`
- Swagger UI available at `http://localhost:8000/docs`

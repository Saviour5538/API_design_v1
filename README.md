# Workflow Builder API

A REST API for managing AI agent workflows built with FastAPI and SQLite. This API powers a platform that lets users browse pre-built AI agents and compose them into automated workflows that run on n8n.

---

## What This Is

The platform has around 70 pre-built AI agents (Invoice Processor, Expense Classifier, etc.), each backed by an n8n workflow. Users can:

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
| Pydantic v2 | Request/response validation and schemas |
| python-jose | JWT token generation and verification |
| passlib + bcrypt 4.0.1 | Password hashing |
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
│   │   ├── user.py
│   │   ├── category.py
│   │   ├── agent.py
│   │   ├── workflow.py
│   │   ├── node.py
│   │   └── execution.py
│   ├── schemas/          # Pydantic request/response schemas
│   │   ├── auth.py
│   │   ├── category.py
│   │   ├── agent.py
│   │   ├── workflow.py
│   │   ├── node.py
│   │   └── execution.py
│   ├── routers/          # Endpoint definitions
│   │   ├── auth.py
│   │   ├── categories.py
│   │   ├── agents.py
│   │   ├── workflows.py
│   │   ├── nodes.py
│   │   └── executions.py
│   └── services/
│       ├── auth.py       # JWT logic, password hashing, get_current_user
│       └── n8n.py        # HTTP calls to trigger/cancel n8n workflows
├── seed_agents.py        # Script to seed test agents into the database
├── .env                  # Environment variables (not committed)
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
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
N8N_BASE_URL=http://localhost:5678
N8N_API_KEY=your-n8n-api-key
```

### 4. Run the server

```powershell
venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The database tables are created automatically on first run.

### 5. Seed test agents (optional, for testing)

```powershell
venv\Scripts\python seed_agents.py
```

### 6. Open Swagger UI

Navigate to `http://localhost:8000/docs`

---

## Authentication

The API uses JWT Bearer tokens.

1. Register at `POST /api/v1/auth/register`
2. Login at `POST /api/v1/auth/login` — returns `access_token` and `refresh_token`
3. Click **Authorize** in Swagger UI and paste the `access_token`
4. All protected endpoints will now send the token automatically

Tokens expire after 1 hour. Use `POST /api/v1/auth/refresh` with the `refresh_token` to get a new access token without logging in again.

---

## API Endpoints

Base URL: `https://workflow.aifirstenteprise.ai/api/v1`
Local: `http://localhost:8000/api/v1`

### Health
| Method | Path | Description |
|---|---|---|
| GET | `/health` | Check if server is online |

### Auth
| Method | Path | Description |
|---|---|---|
| POST | `/auth/register` | Create a new account |
| POST | `/auth/login` | Login and get tokens |
| POST | `/auth/logout` | Logout |
| POST | `/auth/refresh` | Refresh access token |
| GET | `/auth/me` | Get current user profile |
| PATCH | `/auth/me` | Update name or email |
| PATCH | `/auth/me/password` | Change password |

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

---

## Resource IDs

Every resource has a prefixed unique ID generated automatically:

| Resource | Prefix | Example |
|---|---|---|
| User | `usr_` | `usr_4b1e9c2d` |
| Category | `cat_` | `cat_6c28cdbb` |
| Agent | `agt_` | `agt_3f9a1b2c` |
| Workflow | `wfl_` | `wfl_7d4e2a1f` |
| Node | `nod_` | `nod_1c8b5e3a` |
| Execution | `exc_` | `exc_9a2f4d7c` |

---

## Response Format

All responses follow the same envelope:

```json
// Single resource
{ "status": "success", "data": { ... } }

// List with pagination
{ "status": "success", "data": { "items": [...], "total": 10, "page": 1, "limit": 10, "total_pages": 1 } }

// Delete / action
{ "status": "success", "message": "Resource deleted successfully" }

// Error
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

## Known Issues / Notes

- `bcrypt` must be pinned to `4.0.1` — version 5.x is incompatible with `passlib 1.7.4`
- If port 8000 is already in use: `Get-Process python | Stop-Process -Force`, then restart
- The SQLite database file `workflow.db` is created in the project root automatically

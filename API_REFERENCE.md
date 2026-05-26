# API Reference

Base URL: `http://localhost:8000/api/v1`

All responses follow this envelope:
```json
{ "status": "success", "data": { ... } }          // single resource
{ "status": "success", "data": { "items": [], "total": 0, "page": 1, "limit": 10, "total_pages": 1 } }  // list
{ "status": "success", "message": "..." }          // delete / action
{ "status": "error",   "message": "...", "code": 404 }  // error
```

No authentication required — auth is handled externally.

---

## Health

### GET `/health`
Check if the server is running.

**Response**
```json
{
  "status": "success",
  "data": { "server": "online", "version": "v1" }
}
```

---

## Categories

### POST `/categories`
Create a new category.

**Request body**
```json
{
  "name": "Finance",
  "description": "Finance related agents"
}
```
| Field | Type | Required |
|---|---|---|
| name | string | yes |
| description | string | no |

**Response** `201`
```json
{
  "status": "success",
  "data": {
    "id": "cat_6c28cdbb",
    "name": "Finance",
    "description": "Finance related agents",
    "agent_count": 0,
    "created_at": "2025-01-01T10:00:00Z",
    "updated_at": "2025-01-01T10:00:00Z"
  }
}
```

---

### GET `/categories`
List all categories.

**Query params**
| Param | Type | Default | Description |
|---|---|---|---|
| page | int | 1 | Page number |
| limit | int | 10 | Items per page (max 100) |

**Response** `200`
```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "id": "cat_6c28cdbb",
        "name": "Finance",
        "description": "Finance related agents",
        "agent_count": 3,
        "created_at": "2025-01-01T10:00:00Z",
        "updated_at": "2025-01-01T10:00:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "limit": 10,
    "total_pages": 1
  }
}
```

---

### GET `/categories/{category_id}`
Get a single category.

**Response** `200` — same shape as a single item in the list above.

**Error** `404`
```json
{ "status": "error", "message": "Category not found", "code": 404 }
```

---

### PATCH `/categories/{category_id}`
Update a category. All fields are optional.

**Request body**
```json
{
  "name": "Updated Name",
  "description": "Updated description"
}
```

**Response** `200` — returns the updated category.

---

### DELETE `/categories/{category_id}`
Delete a category. Fails if the category has agents assigned to it.

**Response** `200`
```json
{ "status": "success", "message": "Category deleted successfully" }
```

**Error** `422` — if agents exist under this category
```json
{ "status": "error", "message": "Cannot delete category with existing agents", "code": 422 }
```

---

## Agents

Agents are pre-seeded by admins. End users can only read them.

### GET `/agents`
List all agents with optional filters.

**Query params**
| Param | Type | Description |
|---|---|---|
| category_id | string | Filter by category |
| search | string | Search by agent name |
| page | int | Page number (default 1) |
| limit | int | Items per page (default 10, max 100) |

**Response** `200`
```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "id": "agt_3f9a1b2c",
        "name": "Invoice Processor",
        "description": "Extracts and processes invoice data automatically",
        "category": { "id": "cat_6c28cdbb", "name": "Finance" },
        "inputs": [
          { "name": "file_url", "type": "string", "required": true }
        ],
        "is_active": true,
        "created_at": "2025-01-01T10:00:00Z",
        "updated_at": "2025-01-01T10:00:00Z"
      }
    ],
    "total": 3,
    "page": 1,
    "limit": 10,
    "total_pages": 1
  }
}
```

---

### GET `/agents/{agent_id}`
Get a single agent. Includes `n8n_workflow_id` which is not shown in the list.

**Response** `200`
```json
{
  "status": "success",
  "data": {
    "id": "agt_3f9a1b2c",
    "name": "Invoice Processor",
    "description": "Extracts and processes invoice data automatically",
    "category": { "id": "cat_6c28cdbb", "name": "Finance" },
    "inputs": [
      { "name": "file_url", "type": "string", "required": true }
    ],
    "is_active": true,
    "n8n_workflow_id": "n8n_wf_001",
    "created_at": "2025-01-01T10:00:00Z",
    "updated_at": "2025-01-01T10:00:00Z"
  }
}
```

**Error** `403` — if agent is inactive
```json
{ "status": "error", "message": "This agent is currently inactive", "code": 403 }
```

---

## Workflows

### POST `/workflows`
Create a new workflow. Always starts in `draft` status.

**Request body**
```json
{
  "name": "Invoice Processing Flow",
  "description": "Processes invoices end to end",
  "category_id": "cat_6c28cdbb"
}
```
| Field | Type | Required |
|---|---|---|
| name | string | yes |
| description | string | no |
| category_id | string | no |

**Response** `201`
```json
{
  "status": "success",
  "data": {
    "id": "wfl_7d4e2a1f",
    "name": "Invoice Processing Flow",
    "description": "Processes invoices end to end",
    "status": "draft",
    "category": { "id": "cat_6c28cdbb", "name": "Finance" },
    "nodes": [],
    "created_at": "2025-01-01T10:00:00Z",
    "updated_at": "2025-01-01T10:00:00Z"
  }
}
```

---

### GET `/workflows`
List workflows.

**Query params**
| Param | Type | Description |
|---|---|---|
| search | string | Search by workflow name |
| status | string | Filter by status: `draft`, `active`, `completed`, `failed`, `cancelled` |
| page | int | Page number (default 1) |
| limit | int | Items per page (default 10, max 100) |

**Response** `200`
```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "id": "wfl_7d4e2a1f",
        "name": "Invoice Processing Flow",
        "description": "Processes invoices end to end",
        "status": "draft",
        "category": { "id": "cat_6c28cdbb", "name": "Finance" },
        "node_count": 2,
        "created_at": "2025-01-01T10:00:00Z",
        "updated_at": "2025-01-01T10:00:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "limit": 10,
    "total_pages": 1
  }
}
```

---

### GET `/workflows/{workflow_id}`
Get a workflow with all its nodes expanded.

**Response** `200` — same as POST response, with `nodes` populated.

---

### PATCH `/workflows/{workflow_id}`
Update a workflow. All fields are optional.

**Request body**
```json
{
  "name": "New Name",
  "description": "New description",
  "status": "active",
  "category_id": "cat_6c28cdbb"
}
```

Status lifecycle: `draft` → `active` → `completed` / `failed` / `cancelled`

**Response** `200` — returns the updated workflow (list item shape, no nodes expanded).

---

### DELETE `/workflows/{workflow_id}`
Soft delete a workflow. Fails if there is a running execution.

**Response** `200`
```json
{ "status": "success", "message": "Workflow deleted successfully" }
```

**Error** `422`
```json
{ "status": "error", "message": "Cannot delete a workflow that is currently running", "code": 422 }
```

---

## Nodes

Nodes are agents added to a workflow in a specific order. The workflow must be in `draft` status to add, edit, or remove nodes.

### POST `/workflows/{workflow_id}/nodes`
Add an agent as a node to a workflow.

**Request body**
```json
{
  "name": "Step 1 - Parse Invoice",
  "agent_id": "agt_3f9a1b2c",
  "order": 1,
  "input_values": {
    "file_url": "https://example.com/invoice.pdf"
  }
}
```
| Field | Type | Required |
|---|---|---|
| name | string | yes |
| agent_id | string | yes |
| order | int | yes |
| input_values | object | no |

**Response** `201`
```json
{
  "status": "success",
  "data": {
    "id": "nod_1c8b5e3a",
    "name": "Step 1 - Parse Invoice",
    "order": 1,
    "agent": { "id": "agt_3f9a1b2c", "name": "Invoice Processor", "category": "Finance" },
    "input_values": { "file_url": "https://example.com/invoice.pdf" },
    "workflow_id": "wfl_7d4e2a1f",
    "created_at": "2025-01-01T10:00:00Z",
    "updated_at": "2025-01-01T10:00:00Z"
  }
}
```

**Error** `422` — if workflow is active
```json
{ "status": "error", "message": "Cannot add nodes to an active workflow, set it to draft first", "code": 422 }
```

---

### GET `/workflows/{workflow_id}/nodes`
List all nodes in a workflow, ordered by `order`.

**Response** `200`
```json
{
  "status": "success",
  "data": {
    "items": [ { ...node } ],
    "total": 2
  }
}
```

---

### GET `/workflows/{workflow_id}/nodes/{node_id}`
Get a single node.

**Response** `200` — single node object wrapped in `data`.

---

### PATCH `/workflows/{workflow_id}/nodes/{node_id}`
Update a node. All fields are optional.

**Request body**
```json
{
  "name": "Updated Step Name",
  "order": 2,
  "input_values": { "file_url": "https://new.url/invoice.pdf" }
}
```

**Response** `200` — returns the updated node.

---

### DELETE `/workflows/{workflow_id}/nodes/{node_id}`
Remove a node from a workflow.

**Response** `200`
```json
{ "status": "success", "message": "Node removed from workflow successfully" }
```

---

## Executions

Only `active` workflows with at least one node can be executed.

### POST `/executions`
Trigger a workflow execution. Calls n8n behind the scenes.

**Request body**
```json
{
  "workflow_id": "wfl_7d4e2a1f",
  "input_values": {
    "file_url": "https://example.com/invoice.pdf"
  }
}
```
| Field | Type | Required |
|---|---|---|
| workflow_id | string | yes |
| input_values | object | no |

**Response** `201`
```json
{
  "status": "success",
  "data": {
    "execution_id": "exc_9a2f4d7c",
    "workflow": { "id": "wfl_7d4e2a1f", "name": "Invoice Processing Flow" },
    "status": "running",
    "started_at": "2025-01-01T10:00:00Z",
    "completed_at": null,
    "result": null,
    "error": null
  }
}
```

**Error** `422` — workflow not active or has no nodes
```json
{ "status": "error", "message": "Only active workflows can be executed", "code": 422 }
```

---

### GET `/executions`
List executions.

**Query params**
| Param | Type | Description |
|---|---|---|
| workflow_id | string | Filter by workflow |
| status | string | Filter by status: `running`, `completed`, `failed`, `cancelled` |
| page | int | Page number (default 1) |
| limit | int | Items per page (default 10, max 100) |

**Response** `200` — paginated list of execution objects.

---

### GET `/executions/{execution_id}`
Get a single execution with its result.

**Response** `200` — single execution object, `result` populated once completed.

---

### POST `/executions/{execution_id}/cancel`
Cancel a running execution.

**Response** `200`
```json
{ "status": "success", "message": "Execution cancelled successfully" }
```

**Error** `422` — if not running
```json
{ "status": "error", "message": "Cannot cancel an execution that is already completed", "code": 422 }
```

---

### POST `/executions/{execution_id}/webhook`
Called by n8n to report the result of a completed execution. Not called by end users.

**Request body**
```json
{
  "n8n_execution_id": "123",
  "status": "completed",
  "result": { "output": "Processed successfully" },
  "error": null
}
```

**Response** `200`
```json
{ "status": "success", "message": "Execution result recorded" }
```

---

## Resource ID Prefixes

| Resource | Prefix | Example |
|---|---|---|
| Category | `cat_` | `cat_6c28cdbb` |
| Agent | `agt_` | `agt_3f9a1b2c` |
| Workflow | `wfl_` | `wfl_7d4e2a1f` |
| Node | `nod_` | `nod_1c8b5e3a` |
| Execution | `exc_` | `exc_9a2f4d7c` |

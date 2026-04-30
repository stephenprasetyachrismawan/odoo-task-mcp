# Odoo Task MCP Server

Real MCP server for Odoo `project.task` over XML-RPC (external to Odoo).

## Implemented tools
- list_tasks
- list_my_tasks
- get_task
- get_task_as_coding_prompt
- list_task_attachments (metadata only)
- post_task_comment (blocked by default via `MCP_READ_ONLY=true`)
- set_task_stage (blocked by default via `MCP_READ_ONLY=true`)
- attach_pr_link (GitHub HTTPS URL validation)

## Security defaults
- Read-only mode enabled by default.
- Access policy enforcement via `ODOO_ALLOWED_PROJECT_IDS`.
- Task description treated as untrusted input.
- Description is transformed and redacted; raw description is not returned.
- No direct PostgreSQL access.

## Run
```bash
uv sync
uv run python -m odoo_task_mcp.server
```

## Config
Copy `.env.example` to `.env` and set:
`ODOO_URL`, `ODOO_DB`, `ODOO_USERNAME`, `ODOO_API_KEY`.
Optional: `ODOO_ALLOWED_PROJECT_IDS`, `MCP_READ_ONLY`, `MCP_SERVER_NAME`.

## Limitations
- Attachment binary download is not implemented (metadata only).
- MCP resources are future enhancement.

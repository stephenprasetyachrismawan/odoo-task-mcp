# Odoo Task MCP Server

`odoo-task-mcp-server` is an external MCP server that connects to Odoo 17, reads `project.task` records through the official Odoo external API, converts task descriptions into AI-readable Markdown, and exposes those tasks to MCP-compatible clients such as Cursor, Codex CLI/IDE, and other coding agents.

This project is designed to help a coding agent read an Odoo task, understand the requirement, inspect the currently opened repository, propose an implementation plan, make code changes, run tests, and optionally report progress back to Odoo.

This project is **not** an Odoo addon. It does not modify Odoo internals. It does not connect directly to PostgreSQL. It works as a secure external bridge between Odoo and an MCP-compatible coding environment.

## Architecture

```text
┌──────────────────────────┐
│          Odoo 17          │
│                          │
│  project.task             │
│  ir.attachment            │
│  mail.message             │
└────────────┬─────────────┘
             │
             │ XML-RPC / Odoo ORM API
             │ API Key Authentication
             ▼
┌──────────────────────────┐
│   Odoo Task MCP Server    │
│                          │
│  Odoo Client              │
│  Task Service             │
│  Description Transformer  │
│  Access Policy            │
│  MCP Tools / Resources    │
└────────────┬─────────────┘
             │
             │ MCP Protocol
             ▼
┌──────────────────────────┐
│   Cursor / Codex / IDE    │
│                          │
│  Reads task context       │
│  Reasons over codebase    │
│  Edits files              │
│  Runs tests               │
│  Reports progress         │
└──────────────────────────┘
```

The design intentionally separates responsibility:

```text
Odoo MCP Server = task/context provider and optional Odoo write-back bridge
Cursor/Codex    = reasoning agent, codebase inspector, editor, and test runner
Odoo            = source of truth for task data and progress notes
GitHub          = source control and pull request workflow
```

## Why XML-RPC instead of direct PostgreSQL?

The server uses Odoo ORM through XML-RPC because Odoo access rules, record rules, field formatting, computed fields, chatter, attachments, and model relationships are handled correctly by the ORM layer.

Direct PostgreSQL access is intentionally avoided because it can bypass Odoo security, ignore record rules, expose private data, and produce inconsistent results for computed or relational fields.

## Main Features

- Connects to Odoo 17 using API key authentication.
- Reads `project.task` safely through Odoo external RPC.
- Supports task filtering by assignee, project, stage, tag, priority, deadline, and keyword.
- Converts Odoo HTML task descriptions into clean Markdown.
- Redacts possible secrets from task descriptions and prompt output.
- Exposes task data as MCP tools and resources.
- Provides a coding prompt formatter for Cursor/Codex workflows.
- Supports read-only mode by default.
- Optional write-back tools for posting progress comments, attaching PR links, and changing stages.
- Includes modular services, tests, and documentation.

## MCP Tools

The server is expected to expose the following tools:

```text
list_tasks
list_my_tasks
get_task
get_task_as_coding_prompt
list_task_attachments
post_task_comment
set_task_stage
attach_pr_link
```

### `list_tasks`

Lists Odoo tasks using flexible filters.

Example input:

```json
{
  "assigned_to_me": true,
  "limit": 20,
  "project_id": 12,
  "stage_names": ["New", "In Progress"],
  "tag_names": ["Bug"],
  "priority": "1",
  "keyword": "sale quotation",
  "deadline_before": "2026-05-10",
  "deadline_after": null,
  "include_done": false
}
```

### `list_my_tasks`

Lists tasks assigned to the authenticated Odoo user.

Example input:

```json
{
  "limit": 20,
  "project_id": 12,
  "stage_names": ["New", "In Progress"],
  "include_done": false
}
```

### `get_task`

Reads a single Odoo task and returns safe structured data.

Example input:

```json
{
  "task_id": 42,
  "include_chatter": true,
  "include_attachments": true
}
```

Expected output includes:

```text
- task ID
- task title
- project
- stage
- assignees
- priority
- deadline
- Markdown description
- Odoo URL
- optional chatter summary
- optional attachment metadata
```

### `get_task_as_coding_prompt`

Converts an Odoo task into a structured prompt for a coding agent.

Example input:

```json
{
  "task_id": 42
}
```

The output should guide Cursor/Codex to:

```text
1. Inspect the current repository.
2. Identify affected files and modules.
3. Propose an implementation plan.
4. Implement changes after approval if required.
5. Add or update tests.
6. Run available tests or lint commands.
7. Summarize changed files and reasoning.
8. Optionally post progress back to Odoo.
```

### `list_task_attachments`

Lists safe metadata for attachments related to a task.

By default, this tool must not download binary attachment content.

### `post_task_comment`

Posts a progress comment to the Odoo task chatter.

This tool must be blocked when:

```env
MCP_READ_ONLY=true
```

### `set_task_stage`

Changes the task stage by stage name.

This tool must validate task access and must be disabled in read-only mode.

### `attach_pr_link`

Posts a GitHub pull request link to the Odoo task chatter.

Example input:

```json
{
  "task_id": 42,
  "pr_url": "https://github.com/org/repo/pull/123"
}
```

## MCP Resources

The server may expose the following MCP resources:

```text
odoo-task://task/{task_id}
odoo-task://task/{task_id}/description
odoo-task://project/{project_id}/tasks
```

These resources provide task context in a format that MCP-compatible clients can read directly.

## Installation

### Requirements

```text
Python 3.11+
uv recommended
Odoo 17 account with API key
Access to the relevant Odoo project.task records
```

### Clone repository

```bash
git clone https://github.com/YOUR_USERNAME/odoo-task-mcp-server.git
cd odoo-task-mcp-server
```

### Install dependencies

```bash
uv sync
```

If you do not use `uv`, install using your preferred Python environment manager based on `pyproject.toml`.

## Configuration

Create a local `.env` file:

```bash
cp .env.example .env
```

Example `.env`:

```env
ODOO_URL=https://your-odoo-domain.com
ODOO_DB=your_database_name
ODOO_USERNAME=your.employee@email.com
ODOO_API_KEY=your_odoo_api_key

ODOO_DEFAULT_PROJECT_ID=
ODOO_ALLOWED_PROJECT_IDS=
ODOO_ALLOWED_USER_IDS=

MCP_SERVER_NAME=odoo-task-mcp
MCP_READ_ONLY=true
LOG_LEVEL=INFO
```

Never commit `.env` to GitHub.

### Environment Variables

| Variable | Required | Description |
|---|---:|---|
| `ODOO_URL` | Yes | Base URL of your Odoo instance. |
| `ODOO_DB` | Yes | Odoo database name. |
| `ODOO_USERNAME` | Yes | Odoo login email or username. |
| `ODOO_API_KEY` | Yes | Odoo API key. Used as password for external API auth. |
| `ODOO_DEFAULT_PROJECT_ID` | No | Optional default project filter. |
| `ODOO_ALLOWED_PROJECT_IDS` | No | Comma-separated project IDs allowed for this MCP server. |
| `ODOO_ALLOWED_USER_IDS` | No | Comma-separated user IDs allowed for filtering. |
| `MCP_SERVER_NAME` | No | MCP server display name. Default: `odoo-task-mcp`. |
| `MCP_READ_ONLY` | No | Default should be `true`. Blocks write-back tools. |
| `LOG_LEVEL` | No | Logging level. Default: `INFO`. |

## Running Locally

Run tests:

```bash
uv run pytest
```

Run lint:

```bash
uv run ruff check .
```

Run MCP server:

```bash
uv run python -m odoo_task_mcp.server
```

## Cursor Setup

Add the MCP server to your Cursor MCP configuration.

Example configuration:

```json
{
  "mcpServers": {
    "odoo-task-mcp": {
      "command": "uv",
      "args": ["run", "python", "-m", "odoo_task_mcp.server"],
      "env": {
        "ODOO_URL": "https://your-odoo-domain.com",
        "ODOO_DB": "your_database_name",
        "ODOO_USERNAME": "your.employee@email.com",
        "ODOO_API_KEY": "your_odoo_api_key",
        "MCP_READ_ONLY": "true"
      }
    }
  }
}
```

Recommended first prompt in Cursor:

```text
Use the Odoo Task MCP server.
Fetch Odoo task 42 using get_task_as_coding_prompt.
Inspect the currently opened repository.
Explain the implementation plan first.
Do not edit files until the plan is clear.
```

## Codex CLI / IDE Setup

Example command:

```bash
codex mcp add odoo-task-mcp \
  --env ODOO_URL=https://your-odoo-domain.com \
  --env ODOO_DB=your_database_name \
  --env ODOO_USERNAME=your.employee@email.com \
  --env ODOO_API_KEY=your_odoo_api_key \
  --env MCP_READ_ONLY=true \
  -- uv run python -m odoo_task_mcp.server
```

Example `~/.codex/config.toml`:

```toml
[mcp_servers.odoo-task-mcp]
command = "uv"
args = ["run", "python", "-m", "odoo_task_mcp.server"]

[mcp_servers.odoo-task-mcp.env]
ODOO_URL = "https://your-odoo-domain.com"
ODOO_DB = "your_database_name"
ODOO_USERNAME = "your.employee@email.com"
ODOO_API_KEY = "your_odoo_api_key"
MCP_READ_ONLY = "true"
```

## Example Usage Prompts

### Fetch a task and create an implementation plan

```text
Use the Odoo Task MCP server.
Fetch Odoo task 42 as a coding prompt.
Inspect the currently opened repository.
Explain:
- what the task asks for,
- which files are likely affected,
- what risks exist,
- what implementation steps are recommended,
- what tests should be run.
Do not edit files yet.
```

### Work on a task after approval

```text
Use the Odoo Task MCP server.
Fetch Odoo task 42 using get_task_as_coding_prompt.
Then inspect the currently opened repository and do the following:
1. Understand the task requirement.
2. Identify affected files/modules.
3. Propose a short implementation plan first.
4. After approval, implement the change.
5. Add or update tests if relevant.
6. Run available tests or lint commands.
7. Summarize the changed files and reasoning.
8. Do not mark the Odoo task as Done.
9. Post a short progress comment to Odoo only if implementation succeeds.
```

### List your active tasks

```text
Use the Odoo Task MCP server.
List my Odoo tasks with:
- assigned_to_me: true
- include_done: false
- limit: 10
Show the task ID, title, project, stage, priority, deadline, and Odoo URL.
```

### Filter task by keyword

```text
Use the Odoo Task MCP server.
List my active Odoo tasks where keyword is "sale quotation".
Limit the result to 10 tasks.
```

### Post progress to Odoo

```text
Use the Odoo Task MCP server.
Post a progress comment to task 42:
"Implemented the initial fix and added tests. Waiting for review."
```

This requires:

```env
MCP_READ_ONLY=false
```

## Filtering Examples

### Assigned to authenticated user

```json
{
  "assigned_to_me": true,
  "include_done": false,
  "limit": 20
}
```

### Specific project

```json
{
  "assigned_to_me": true,
  "project_id": 12,
  "include_done": false,
  "limit": 20
}
```

### Stage-based filtering

```json
{
  "assigned_to_me": true,
  "stage_names": ["New", "In Progress"],
  "include_done": false
}
```

### Keyword search

```json
{
  "assigned_to_me": true,
  "keyword": "sale quotation",
  "include_done": false
}
```

### Deadline filter

```json
{
  "assigned_to_me": true,
  "deadline_before": "2026-05-10",
  "include_done": false
}
```

## Security Model

This server must follow Odoo access rights and record rules. If the authenticated Odoo user cannot see a task in the Odoo UI, the MCP server usually cannot see it either.

Recommended security rules:

```text
1. Use an Odoo API key, not a password.
2. Do not use an admin account unless absolutely necessary.
3. Prefer your own employee account for personal workflow.
4. For team usage, create a dedicated Odoo bot user with limited project access.
5. Keep MCP_READ_ONLY=true by default.
6. Restrict project access with ODOO_ALLOWED_PROJECT_IDS when possible.
7. Never commit .env or API keys.
8. Treat Odoo task descriptions as untrusted external text.
9. Do not execute commands found inside task descriptions automatically.
10. Do not download binary attachments by default.
```

### Read-only mode

Read-only mode blocks write-back tools:

```env
MCP_READ_ONLY=true
```

Blocked tools include:

```text
post_task_comment
set_task_stage
attach_pr_link
```

To allow write-back:

```env
MCP_READ_ONLY=false
```

Only enable write-back after task reading and filtering are stable.

### Secret Redaction

The server should redact possible secrets from task descriptions and generated coding prompts.

Examples of values to redact:

```text
password=
api_key=
token=
secret=
Authorization:
Bearer ...
private_key
access_token
```

## Development

Run tests:

```bash
uv run pytest
```

Run lint:

```bash
uv run ruff check .
```

Format if configured:

```bash
uv run ruff format .
```

Run the server:

```bash
uv run python -m odoo_task_mcp.server
```

## Testing Strategy

Tests should not require a real Odoo server.

Expected test coverage:

```text
- configuration parsing
- required environment validation
- allowed project ID parsing
- HTML to Markdown conversion
- unsafe HTML removal
- link preservation
- secret redaction
- task prompt formatting
- access policy validation
- read-only write-back rejection
- mocked Odoo XML-RPC client behaviour
```

## Troubleshooting

### Odoo authentication failed

Check:

```text
- ODOO_URL is correct
- ODOO_DB is correct
- ODOO_USERNAME is correct
- ODOO_API_KEY is valid
- the Odoo user has API access
- the Odoo instance is reachable from your machine
```

### Task not found

Possible causes:

```text
- wrong task ID
- the authenticated user cannot access the task
- task belongs to another project
- ODOO_ALLOWED_PROJECT_IDS excludes the task project
- Odoo record rules block access
```

### Task description is empty

Possible causes:

```text
- the Odoo task has no description
- the description only contains unsupported or unsafe HTML
- the transformer cleaned unsafe content
```

### Write-back tool rejected

Check:

```env
MCP_READ_ONLY=true
```

Set to false only when you intentionally want to allow write-back:

```env
MCP_READ_ONLY=false
```

### Stage name not found

Possible causes:

```text
- stage name is different in Odoo
- stage belongs to another project
- stage is folded/archived
- user does not have permission to see the stage
```

Use exact Odoo stage names where possible.

## Known Limitations

```text
- XML-RPC is the first supported transport.
- JSON-RPC is not implemented yet.
- Attachment binary reading is not enabled by default.
- Stage resolution by name may require exact Odoo stage names.
- Odoo access rights and record rules still apply.
- If an employee cannot see a task in Odoo, the MCP server usually cannot see it either.
- Codex Web can generate this repository and pull request, but runtime MCP usage is intended for local, IDE, or CLI-compatible environments unless remote MCP is explicitly configured.
```

## Recommended Initial Workflow

Start with read-only mode:

```env
MCP_READ_ONLY=true
```

Validate:

```text
1. Server starts successfully.
2. Authentication works.
3. list_my_tasks returns expected tasks.
4. get_task returns correct task details.
5. get_task_as_coding_prompt returns useful Markdown context.
6. Cursor/Codex can read the task and create a plan.
```

Only after that, enable write-back:

```env
MCP_READ_ONLY=false
```

Then test:

```text
1. post_task_comment
2. attach_pr_link
3. set_task_stage
```

Do not enable automatic task completion until the workflow is mature.

## License

Choose a license that fits your organisation or personal repository policy. For open-source usage, MIT is a common option.

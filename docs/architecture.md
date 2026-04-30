# Architecture

Flow: Odoo (XML-RPC ORM) -> Odoo Task MCP Server -> Cursor/Codex MCP client.

The MCP server provides tools/context only; the coding agent performs reasoning and code edits.

Access policy is enforced in app layer (allowed project IDs) in addition to Odoo record rules.

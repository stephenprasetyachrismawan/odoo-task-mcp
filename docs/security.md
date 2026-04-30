# Security

- Uses Odoo API key via XML-RPC only.
- No direct PostgreSQL access.
- `MCP_READ_ONLY=true` by default.
- Redacts common secrets (password/api key/token/bearer/private keys).
- Odoo task text is treated as untrusted external context.
- Attachment binaries are not downloaded by default.

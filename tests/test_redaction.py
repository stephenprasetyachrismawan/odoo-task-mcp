from odoo_task_mcp.security.redaction import redact_text


def test_redact_long_tokens():
    raw = "token abcdefghijklmnopqrstuvwxyz123456"
    out = redact_text(raw)
    assert "[REDACTED]" in out

from odoo_task_mcp.security.redaction import redact_text


def test_redaction_patterns():
    text = "password=abc api_key=def token=ghi Authorization: Bearer xyz"
    out = redact_text(text)
    assert "abc" not in out and "def" not in out and "ghi" not in out and "xyz" not in out


def test_redact_long_tokens():
    assert "[REDACTED]" in redact_text("abcdefghijklmnopqrstuvwxyz123456")

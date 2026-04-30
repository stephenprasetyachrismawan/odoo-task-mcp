import pytest

from odoo_task_mcp.config import Settings
from odoo_task_mcp.exceptions import OdooAccessPolicyError, ReadOnlyModeError
from odoo_task_mcp.security.access_policy import AccessPolicy


def make_settings(**kw):
    base = dict(ODOO_URL="https://x", ODOO_DB="d", ODOO_USERNAME="u", ODOO_API_KEY="k")
    base.update(kw)
    return Settings(**base)


def test_policy_reject_disallowed():
    p = AccessPolicy(make_settings(ODOO_ALLOWED_PROJECT_IDS="1,2"))
    with pytest.raises(OdooAccessPolicyError):
        p.ensure_project_allowed(9)


def test_readonly_reject_write():
    p = AccessPolicy(make_settings(MCP_READ_ONLY=True))
    with pytest.raises(ReadOnlyModeError):
        p.ensure_write_allowed()

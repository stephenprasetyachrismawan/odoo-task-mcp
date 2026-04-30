import pytest

from odoo_task_mcp.exceptions import OdooAuthenticationError
from odoo_task_mcp.odoo.client import OdooXmlRpcClient


def test_auth_failure(monkeypatch):
    c = OdooXmlRpcClient(base_url="https://x", db="d", username="u", api_key="k")

    class Common:
        def authenticate(self, *a, **k):
            return False

    c._common = Common()
    with pytest.raises(OdooAuthenticationError):
        c.authenticate()

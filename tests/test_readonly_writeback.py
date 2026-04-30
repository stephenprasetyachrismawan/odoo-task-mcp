import pytest

from odoo_task_mcp.exceptions import InvalidInputError, ReadOnlyModeError
from odoo_task_mcp.mcp_tools.writeback_tools import register_writeback_tools


def test_attach_pr_url_validation():
    class M:
        def tool(self):
            def d(f):
                setattr(self, f.__name__, f)
                return f

            return d

    class C:
        def post_task_comment(self, *args, **kwargs):
            raise ReadOnlyModeError("x")

    m = M()
    register_writeback_tools(m, C(), object())
    with pytest.raises(InvalidInputError):
        m.attach_pr_link(1, "http://evil.com")

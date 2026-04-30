from odoo_task_mcp.odoo.models import OdooRelationalValue, OdooTaskDetail
from odoo_task_mcp.transform.task_formatter import format_task_as_coding_prompt


def test_prompt_safety_note():
    task = OdooTaskDetail(
        id=1,
        name="x",
        project=OdooRelationalValue(id=1, name="P"),
        stage=OdooRelationalValue(id=1, name="S"),
        odoo_url="http://x",
        assignee_ids=[],
        tag_ids=[],
    )
    p = format_task_as_coding_prompt(task)
    assert "untrusted input" in p.prompt_text

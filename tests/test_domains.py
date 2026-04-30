from odoo_task_mcp.odoo.domains import build_task_domain


def test_domain_filters():
    d = build_task_domain(
        uid=7,
        assigned_to_me=True,
        project_id=3,
        allowed_project_ids=[3, 4],
        priority="1",
        keyword="abc",
        deadline_before="2026-01-01",
        deadline_after="2025-01-01",
    )
    assert ("user_ids", "in", [7]) in d
    assert ("project_id", "=", 3) in d
    assert ("project_id", "in", [3, 4]) in d
    assert "|" in d

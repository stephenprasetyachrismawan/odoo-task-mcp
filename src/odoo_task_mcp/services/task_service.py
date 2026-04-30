from __future__ import annotations

from typing import Any

from odoo_task_mcp.odoo.client import OdooXmlRpcClient
from odoo_task_mcp.security.redaction import redact_text
from odoo_task_mcp.transform.html_to_markdown import html_to_markdown


class TaskService:
    def __init__(self, client: OdooXmlRpcClient) -> None:
        self.client = client

    def list_tasks(self, *, limit: int = 20) -> list[dict[str, Any]]:
        return self.client.search_read(
            "project.task",
            domain=[],
            fields=["id", "name", "stage_id", "priority", "date_deadline"],
            limit=limit,
            order="write_date desc",
        )

    def get_task(self, task_id: int) -> dict[str, Any] | None:
        rows = self.client.read(
            "project.task",
            [task_id],
            [
                "id",
                "name",
                "description",
                "project_id",
                "stage_id",
                "priority",
                "date_deadline",
                "user_ids",
            ],
        )
        if not rows:
            return None
        row = rows[0]
        markdown = html_to_markdown(row.get("description"))
        row["description_markdown"] = redact_text(markdown)
        return row

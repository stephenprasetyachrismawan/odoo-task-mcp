from __future__ import annotations

from odoo_task_mcp.exceptions import OdooTaskNotFoundError
from odoo_task_mcp.odoo.domains import build_task_domain
from odoo_task_mcp.odoo.models import OdooRelationalValue, OdooTaskDetail, OdooTaskSummary
from odoo_task_mcp.security.redaction import redact_text
from odoo_task_mcp.transform.html_to_markdown import html_to_markdown
from odoo_task_mcp.transform.task_formatter import format_task_as_coding_prompt

DONE_NAMES = {"done", "cancelled", "canceled", "archived"}


class TaskService:
    def __init__(self, client, settings, access_policy) -> None:
        self.client = client
        self.settings = settings
        self.access_policy = access_policy

    def build_task_url(self, task_id: int) -> str:
        return f"{self.settings.odoo_url}/web#id={task_id}&model=project.task&view_type=form"

    def _rel(self, value):
        return (
            OdooRelationalValue(id=value[0], name=value[1])
            if isinstance(value, list) and len(value) >= 2
            else OdooRelationalValue()
        )

    def _summary(self, row) -> OdooTaskSummary:
        return OdooTaskSummary(
            id=row["id"],
            name=row.get("name", ""),
            project=self._rel(row.get("project_id")),
            stage=self._rel(row.get("stage_id")),
            priority=row.get("priority"),
            deadline=row.get("date_deadline"),
            assignee_ids=row.get("user_ids", []),
            tag_ids=row.get("tag_ids", []),
            odoo_url=self.build_task_url(row["id"]),
        )

    def _ensure_task_allowed(self, task_id: int):
        rows = self.client.read("project.task", [task_id], ["id", "project_id", "stage_id"])
        if not rows:
            raise OdooTaskNotFoundError(f"Task not found: {task_id}")
        self.access_policy.ensure_task_allowed(rows[0])
        return rows[0]

    def list_tasks(
        self,
        assigned_to_me=True,
        limit=20,
        project_id=None,
        stage_names=None,
        tag_names=None,
        priority=None,
        keyword=None,
        deadline_before=None,
        deadline_after=None,
        include_done=False,
    ):
        domain = build_task_domain(
            uid=self.client.get_uid(),
            assigned_to_me=assigned_to_me,
            project_id=project_id,
            allowed_project_ids=self.settings.allowed_project_ids,
            priority=priority,
            keyword=keyword,
            deadline_before=deadline_before,
            deadline_after=deadline_after,
        )
        if stage_names:
            domain.append(("stage_id.name", "in", stage_names))
        if tag_names:
            domain.append(("tag_ids.name", "in", tag_names))
        rows = self.client.search_read(
            "project.task",
            domain,
            [
                "id",
                "name",
                "project_id",
                "stage_id",
                "priority",
                "date_deadline",
                "user_ids",
                "tag_ids",
            ],
            limit=limit,
            order="write_date desc",
        )
        tasks = [self._summary(r) for r in rows]
        if include_done:
            return tasks
        return [t for t in tasks if (t.stage.name or "").lower() not in DONE_NAMES]

    def list_my_tasks(self, limit=20, project_id=None, stage_names=None, include_done=False):
        return self.list_tasks(
            assigned_to_me=True,
            limit=limit,
            project_id=project_id,
            stage_names=stage_names,
            include_done=include_done,
        )

    def get_task(
        self, task_id: int, include_chatter=False, include_attachments=False
    ) -> OdooTaskDetail:
        rows = self.client.read(
            "project.task",
            [task_id],
            [
                "id",
                "name",
                "description",
                "project_id",
                "stage_id",
                "user_ids",
                "tag_ids",
                "priority",
                "date_deadline",
                "create_date",
                "write_date",
            ],
        )
        if not rows:
            raise OdooTaskNotFoundError(f"Task not found: {task_id}")
        row = rows[0]
        self.access_policy.ensure_task_allowed(row)
        detail = OdooTaskDetail(
            **self._summary(row).model_dump(),
            description_markdown=redact_text(html_to_markdown(row.get("description"))),
        )
        return detail

    def get_task_as_coding_prompt(self, task_id: int):
        return format_task_as_coding_prompt(self.get_task(task_id))

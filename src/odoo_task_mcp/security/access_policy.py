from __future__ import annotations

from odoo_task_mcp.config import Settings
from odoo_task_mcp.exceptions import OdooAccessPolicyError, ReadOnlyModeError


class AccessPolicy:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def ensure_project_allowed(self, project_id: int | None) -> None:
        allowed = self.settings.allowed_project_ids
        if not allowed:
            return
        if project_id is None or project_id not in allowed:
            raise OdooAccessPolicyError("Task project is not allowed by configured access policy")

    def ensure_task_allowed(self, task: object) -> None:
        project = None
        if isinstance(task, dict):
            value = task.get("project_id")
            project = value[0] if isinstance(value, list) and value else value
        else:
            project_obj = getattr(task, "project", None)
            project = getattr(project_obj, "id", None)
        self.ensure_project_allowed(project)

    def build_allowed_project_domain(self) -> list:
        if not self.settings.allowed_project_ids:
            return []
        return [("project_id", "in", self.settings.allowed_project_ids)]

    def is_read_only(self) -> bool:
        return self.settings.mcp_read_only

    def ensure_write_allowed(self) -> None:
        if self.is_read_only():
            raise ReadOnlyModeError("Write operations are disabled because MCP_READ_ONLY=true")

from odoo_task_mcp.exceptions import StageResolutionError


class StageService:
    def __init__(self, client, access_policy, task_service) -> None:
        self.client = client
        self.access_policy = access_policy
        self.task_service = task_service

    def resolve_stage_by_name(self, stage_name: str, project_id: int | None = None) -> int:
        domain = [("name", "=", stage_name)]
        if project_id is not None:
            domain.append(("project_ids", "in", [project_id]))
        ids = self.client.search("project.task.type", domain, limit=1)
        if not ids:
            raise StageResolutionError(f"Stage not found: {stage_name}")
        return ids[0]

    def set_task_stage(self, task_id: int, stage_name: str) -> bool:
        self.access_policy.ensure_write_allowed()
        task = self.task_service._ensure_task_allowed(task_id)
        proj = task.get("project_id")
        project_id = proj[0] if isinstance(proj, list) and proj else None
        stage_id = self.resolve_stage_by_name(stage_name, project_id)
        return self.client.write("project.task", [task_id], {"stage_id": stage_id})

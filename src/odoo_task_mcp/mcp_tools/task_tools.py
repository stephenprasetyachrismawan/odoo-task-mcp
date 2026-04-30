from odoo_task_mcp.services.attachment_service import AttachmentService
from odoo_task_mcp.services.task_service import TaskService


def register_task_tools(mcp, task_service: TaskService, attachment_service: AttachmentService):
    @mcp.tool()
    def list_tasks(**kwargs):
        return [t.model_dump() for t in task_service.list_tasks(**kwargs)]

    @mcp.tool()
    def list_my_tasks(
        limit: int = 20,
        project_id: int | None = None,
        stage_names: list[str] | None = None,
        include_done: bool = False,
    ):
        return [
            t.model_dump()
            for t in task_service.list_my_tasks(
                limit=limit,
                project_id=project_id,
                stage_names=stage_names,
                include_done=include_done,
            )
        ]

    @mcp.tool()
    def get_task(task_id: int, include_chatter: bool = False, include_attachments: bool = False):
        return task_service.get_task(task_id, include_chatter, include_attachments).model_dump()

    @mcp.tool()
    def get_task_as_coding_prompt(task_id: int):
        return task_service.get_task_as_coding_prompt(task_id).model_dump()

    @mcp.tool()
    def list_task_attachments(task_id: int):
        return [a.model_dump() for a in attachment_service.list_task_attachments(task_id)]

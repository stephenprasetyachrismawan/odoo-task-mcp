from odoo_task_mcp.exceptions import InvalidInputError
from odoo_task_mcp.services.chatter_service import ChatterService
from odoo_task_mcp.services.stage_service import StageService


def register_writeback_tools(mcp, chatter_service: ChatterService, stage_service: StageService):
    @mcp.tool()
    def post_task_comment(task_id: int, message: str):
        return {"result": chatter_service.post_task_comment(task_id, message)}

    @mcp.tool()
    def set_task_stage(task_id: int, stage_name: str):
        return {"result": stage_service.set_task_stage(task_id, stage_name)}

    @mcp.tool()
    def attach_pr_link(task_id: int, pr_url: str):
        if not pr_url.startswith("https://github.com/"):
            raise InvalidInputError("PR URL must start with https://github.com/")
        msg = f"PR created: {pr_url}"
        return {"result": chatter_service.post_task_comment(task_id, msg)}

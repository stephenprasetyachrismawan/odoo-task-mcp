from odoo_task_mcp.config import Settings
from odoo_task_mcp.logging_config import configure_logging
from odoo_task_mcp.mcp_tools.task_tools import register_task_tools
from odoo_task_mcp.mcp_tools.writeback_tools import register_writeback_tools
from odoo_task_mcp.odoo.client import OdooXmlRpcClient
from odoo_task_mcp.security.access_policy import AccessPolicy
from odoo_task_mcp.services.attachment_service import AttachmentService
from odoo_task_mcp.services.chatter_service import ChatterService
from odoo_task_mcp.services.stage_service import StageService
from odoo_task_mcp.services.task_service import TaskService


def create_server():
    from mcp.server.fastmcp import FastMCP

    settings = Settings()
    configure_logging(settings.log_level)
    client = OdooXmlRpcClient(
        base_url=settings.odoo_url,
        db=settings.odoo_db,
        username=settings.odoo_username,
        api_key=settings.odoo_api_key.get_secret_value(),
    )
    access_policy = AccessPolicy(settings)
    task_service = TaskService(client, settings, access_policy)
    attachment_service = AttachmentService(client, task_service)
    chatter_service = ChatterService(client, access_policy, task_service)
    stage_service = StageService(client, access_policy, task_service)

    mcp = FastMCP(settings.mcp_server_name)
    register_task_tools(mcp, task_service, attachment_service)
    register_writeback_tools(mcp, chatter_service, stage_service)
    return mcp


def main() -> None:
    create_server().run()


if __name__ == "__main__":
    main()

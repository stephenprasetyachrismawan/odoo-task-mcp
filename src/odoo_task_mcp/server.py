from odoo_task_mcp.config import Settings
from odoo_task_mcp.odoo.client import OdooXmlRpcClient
from odoo_task_mcp.services.task_service import TaskService


def build_task_service() -> TaskService:
    settings = Settings()
    client = OdooXmlRpcClient(
        base_url=settings.odoo_url,
        db=settings.odoo_db,
        username=settings.odoo_username,
        api_key=settings.odoo_api_key,
    )
    return TaskService(client)


def main() -> None:
    _ = build_task_service()
    print("odoo-task-mcp-server initialized")


if __name__ == "__main__":
    main()

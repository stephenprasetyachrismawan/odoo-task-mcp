from odoo_task_mcp.odoo.models import OdooAttachmentSummary


class AttachmentService:
    def __init__(self, client, task_service) -> None:
        self.client = client
        self.task_service = task_service

    def list_task_attachments(self, task_id: int) -> list[OdooAttachmentSummary]:
        self.task_service._ensure_task_allowed(task_id)
        rows = self.client.search_read(
            "ir.attachment",
            [("res_model", "=", "project.task"), ("res_id", "=", task_id)],
            ["id", "name", "mimetype", "file_size", "create_date"],
        )
        return [OdooAttachmentSummary(**row) for row in rows]

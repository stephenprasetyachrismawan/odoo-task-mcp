from odoo_task_mcp.exceptions import InvalidInputError
from odoo_task_mcp.security.redaction import redact_text


class ChatterService:
    def __init__(self, client, access_policy, task_service) -> None:
        self.client = client
        self.access_policy = access_policy
        self.task_service = task_service

    def list_task_messages(self, task_id: int, limit: int = 10):
        self.task_service._ensure_task_allowed(task_id)
        return self.client.search_read(
            "mail.message",
            [("model", "=", "project.task"), ("res_id", "=", task_id)],
            ["id", "body", "date"],
            limit=limit,
            order="date desc",
        )

    def post_task_comment(self, task_id: int, message: str):
        self.access_policy.ensure_write_allowed()
        self.task_service._ensure_task_allowed(task_id)
        if not message.strip():
            raise InvalidInputError("Comment message must not be empty")
        return self.client.message_post("project.task", task_id, redact_text(message))

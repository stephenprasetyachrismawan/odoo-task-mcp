from odoo_task_mcp.config import Settings
from odoo_task_mcp.security.access_policy import AccessPolicy
from odoo_task_mcp.services.task_service import TaskService


class FakeClient:
    def get_uid(self):
        return 9

    def search_read(self, *args, **kwargs):
        self.last = (args, kwargs)
        return [
            {
                "id": 1,
                "name": "Task",
                "project_id": [1, "P"],
                "stage_id": [2, "In Progress"],
                "priority": "1",
                "date_deadline": None,
                "user_ids": [9],
                "tag_ids": [],
            }
        ]

    def read(self, model, ids, fields):
        return [
            {
                "id": 1,
                "name": "Task",
                "description": "token=abc",
                "project_id": [1, "P"],
                "stage_id": [2, "In Progress"],
                "priority": "1",
                "date_deadline": None,
                "user_ids": [9],
                "tag_ids": [],
            }
        ]


def make_service():
    settings = Settings(ODOO_URL="https://x", ODOO_DB="d", ODOO_USERNAME="u", ODOO_API_KEY="k")
    return TaskService(FakeClient(), settings, AccessPolicy(settings))


def test_get_task_redacted_and_no_raw_description():
    d = make_service().get_task(1).model_dump()
    assert "description" not in d
    assert "[REDACTED]" in d["description_markdown"]


def test_list_my_tasks_uses_user_filter():
    s = make_service()
    s.list_my_tasks()
    assert ("user_ids", "in", [9]) in s.client.last[0][1]

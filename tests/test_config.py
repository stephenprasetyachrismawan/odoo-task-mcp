from odoo_task_mcp.config import Settings


def test_settings_parse_csv_and_url(monkeypatch):
    monkeypatch.setenv("ODOO_URL", "https://example.com/")
    monkeypatch.setenv("ODOO_DB", "db")
    monkeypatch.setenv("ODOO_USERNAME", "user")
    monkeypatch.setenv("ODOO_API_KEY", "key")
    monkeypatch.setenv("ODOO_ALLOWED_PROJECT_IDS", "1, 2,3")

    s = Settings()
    assert s.odoo_url == "https://example.com"
    assert s.allowed_project_ids == [1, 2, 3]

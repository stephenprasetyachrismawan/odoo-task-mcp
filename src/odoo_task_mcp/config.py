from __future__ import annotations

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    odoo_url: str = Field(..., alias="ODOO_URL")
    odoo_db: str = Field(..., alias="ODOO_DB")
    odoo_username: str = Field(..., alias="ODOO_USERNAME")
    odoo_api_key: str = Field(..., alias="ODOO_API_KEY")

    odoo_default_project_id: int | None = Field(None, alias="ODOO_DEFAULT_PROJECT_ID")
    odoo_allowed_project_ids: str = Field("", alias="ODOO_ALLOWED_PROJECT_IDS")
    odoo_allowed_user_ids: str = Field("", alias="ODOO_ALLOWED_USER_IDS")

    mcp_server_name: str = Field("odoo-task-mcp", alias="MCP_SERVER_NAME")
    mcp_read_only: bool = Field(True, alias="MCP_READ_ONLY")
    log_level: str = Field("INFO", alias="LOG_LEVEL")

    @field_validator("odoo_url")
    @classmethod
    def strip_trailing_slash(cls, value: str) -> str:
        return value.rstrip("/")

    @staticmethod
    def _parse_csv_ids(value: str) -> list[int]:
        if not value:
            return []
        return [int(item.strip()) for item in value.split(",") if item.strip()]

    @property
    def allowed_project_ids(self) -> list[int]:
        return self._parse_csv_ids(self.odoo_allowed_project_ids)

    @property
    def allowed_user_ids(self) -> list[int]:
        return self._parse_csv_ids(self.odoo_allowed_user_ids)

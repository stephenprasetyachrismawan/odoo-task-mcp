from __future__ import annotations

from pydantic import BaseModel


class OdooRelationalValue(BaseModel):
    id: int | None = None
    name: str | None = None


class OdooAttachmentSummary(BaseModel):
    id: int
    name: str | None = None
    mimetype: str | None = None
    file_size: int | None = None
    create_date: str | None = None


class OdooChatterMessage(BaseModel):
    id: int
    body: str | None = None
    date: str | None = None
    author_name: str | None = None


class OdooTaskSummary(BaseModel):
    id: int
    name: str
    project: OdooRelationalValue
    stage: OdooRelationalValue
    priority: str | None = None
    deadline: str | None = None
    assignee_ids: list[int] = []
    tag_ids: list[int] = []
    odoo_url: str


class OdooTaskDetail(OdooTaskSummary):
    description_markdown: str | None = None
    attachments: list[OdooAttachmentSummary] | None = None
    chatter: list[OdooChatterMessage] | None = None


class CodingTaskPrompt(BaseModel):
    task_id: int
    prompt_text: str

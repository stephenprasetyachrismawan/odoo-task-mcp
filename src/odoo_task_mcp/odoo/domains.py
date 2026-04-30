from __future__ import annotations


def build_task_domain(
    *,
    uid: int | None = None,
    assigned_to_me: bool = True,
    project_id: int | None = None,
    allowed_project_ids: list[int] | None = None,
    priority: str | None = None,
    keyword: str | None = None,
    deadline_before: str | None = None,
    deadline_after: str | None = None,
) -> list:
    domain: list = []
    if assigned_to_me and uid is not None:
        domain.append(("user_ids", "in", [uid]))
    if project_id is not None:
        domain.append(("project_id", "=", project_id))
    if allowed_project_ids:
        domain.append(("project_id", "in", allowed_project_ids))
    if priority is not None:
        domain.append(("priority", "=", priority))
    if deadline_before:
        domain.append(("date_deadline", "<=", deadline_before))
    if deadline_after:
        domain.append(("date_deadline", ">=", deadline_after))
    if keyword:
        domain.extend(["|", ("name", "ilike", keyword), ("description", "ilike", keyword)])
    return domain

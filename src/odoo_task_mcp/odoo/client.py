from __future__ import annotations

import xmlrpc.client
from typing import Any

from odoo_task_mcp.exceptions import OdooAuthenticationError, OdooRpcError


class OdooXmlRpcClient:
    def __init__(self, *, base_url: str, db: str, username: str, api_key: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.db = db
        self.username = username
        self.api_key = api_key
        self.uid: int | None = None
        self._common = xmlrpc.client.ServerProxy(f"{self.base_url}/xmlrpc/2/common")
        self._object = xmlrpc.client.ServerProxy(f"{self.base_url}/xmlrpc/2/object")

    def get_uid(self) -> int:
        return self.authenticate() if self.uid is None else self.uid

    def authenticate(self) -> int:
        try:
            uid = self._common.authenticate(self.db, self.username, self.api_key, {})
        except Exception as exc:
            raise OdooAuthenticationError("Failed to authenticate to Odoo") from exc
        if not uid:
            raise OdooAuthenticationError("Failed to authenticate to Odoo")
        self.uid = int(uid)
        return self.uid

    def execute_kw(
        self,
        model: str,
        method: str,
        args: list[Any] | None = None,
        kwargs: dict[str, Any] | None = None,
    ) -> Any:
        uid = self.get_uid()
        try:
            return self._object.execute_kw(
                self.db, uid, self.api_key, model, method, args or [], kwargs or {}
            )
        except Exception as exc:
            raise OdooRpcError(f"Odoo RPC call failed: {model}.{method}") from exc

    def search(
        self, model: str, domain: list[Any], limit: int | None = None, order: str | None = None
    ) -> list[int]:
        kwargs: dict[str, Any] = {}
        if limit is not None:
            kwargs["limit"] = limit
        if order:
            kwargs["order"] = order
        return self.execute_kw(model, "search", [domain], kwargs)

    def search_read(
        self,
        model: str,
        domain: list[Any],
        fields: list[str],
        limit: int | None = None,
        order: str | None = None,
    ) -> list[dict[str, Any]]:
        kwargs: dict[str, Any] = {"fields": fields, "domain": domain}
        if limit is not None:
            kwargs["limit"] = limit
        if order:
            kwargs["order"] = order
        return self.execute_kw(model, "search_read", [], kwargs)

    def read(self, model: str, ids: list[int], fields: list[str]) -> list[dict[str, Any]]:
        return self.execute_kw(model, "read", [ids], {"fields": fields})

    def write(self, model: str, ids: list[int], values: dict[str, Any]) -> bool:
        return bool(self.execute_kw(model, "write", [ids, values]))

    def message_post(self, model: str, res_id: int, body: str) -> Any:
        return self.execute_kw(model, "message_post", [[res_id], {"body": body}])

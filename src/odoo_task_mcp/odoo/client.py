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

    def authenticate(self) -> int:
        try:
            uid = self._common.authenticate(self.db, self.username, self.api_key, {})
        except Exception as exc:  # noqa: BLE001
            raise OdooAuthenticationError("Failed to authenticate to Odoo") from exc
        if not uid:
            raise OdooAuthenticationError("Odoo authentication returned empty uid")
        self.uid = uid
        return uid

    def execute_kw(
        self,
        model: str,
        method: str,
        args: list[Any] | None = None,
        kwargs: dict[str, Any] | None = None,
    ) -> Any:
        if self.uid is None:
            self.authenticate()
        try:
            return self._object.execute_kw(
                self.db,
                self.uid,
                self.api_key,
                model,
                method,
                args or [],
                kwargs or {},
            )
        except Exception as exc:  # noqa: BLE001
            raise OdooRpcError(f"Odoo RPC call failed: {model}.{method}") from exc

    def search_read(
        self,
        model: str,
        domain: list[Any],
        fields: list[str],
        limit: int | None = None,
        order: str | None = None,
    ) -> list[dict[str, Any]]:
        kwargs: dict[str, Any] = {"domain": domain, "fields": fields}
        if limit is not None:
            kwargs["limit"] = limit
        if order is not None:
            kwargs["order"] = order
        return self.execute_kw(model, "search_read", [], kwargs)

    def read(self, model: str, ids: list[int], fields: list[str]) -> list[dict[str, Any]]:
        return self.execute_kw(model, "read", [ids], {"fields": fields})

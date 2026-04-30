class OdooTaskMcpError(Exception):
    """Base error type for this project."""


class OdooAuthenticationError(OdooTaskMcpError):
    """Raised when Odoo authentication fails."""


class OdooRpcError(OdooTaskMcpError):
    """Raised when XML-RPC call fails."""

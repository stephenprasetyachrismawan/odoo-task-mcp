class OdooTaskMcpError(Exception):
    """Base exception for Odoo Task MCP."""


class OdooAuthenticationError(OdooTaskMcpError):
    pass


class OdooRpcError(OdooTaskMcpError):
    pass


class OdooAccessPolicyError(OdooTaskMcpError):
    pass


class OdooTaskNotFoundError(OdooTaskMcpError):
    pass


class ReadOnlyModeError(OdooTaskMcpError):
    pass


class StageResolutionError(OdooTaskMcpError):
    pass


class InvalidInputError(OdooTaskMcpError):
    pass

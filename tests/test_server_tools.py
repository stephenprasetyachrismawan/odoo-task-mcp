def test_import_server_module():
    import odoo_task_mcp.server as server

    assert hasattr(server, "create_server")

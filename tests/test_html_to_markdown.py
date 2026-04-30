from odoo_task_mcp.transform.html_to_markdown import html_to_markdown


def test_html_to_markdown_basic():
    result = html_to_markdown("<p>Hello <b>World</b></p>")
    assert "Hello" in result
    assert "World" in result

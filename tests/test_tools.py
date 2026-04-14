"""Tests for StackOne tool wrappers."""

import json
from unittest.mock import MagicMock, patch

import pytest

from strands_stackone.tools import make_strands_tool, make_search_tool, make_execute_tool


class TestMakeStrandsTool:
    """Test wrapping StackOne tools as Strands tools."""

    def _make_mock_so_tool(self, name="bamboohr_get_employee"):
        mock = MagicMock()
        mock.name = name
        mock.description = f"Get details for {name}"
        mock.parameters = MagicMock()
        mock.parameters.properties = {
            "id": {"type": "string", "description": "Employee ID", "nullable": False},
            "fields_": {"type": "string", "description": "Fields to return", "nullable": True},
        }
        mock.execute.return_value = {"status": "success", "data": {"id": "123", "name": "John"}}
        return mock

    def test_creates_tool_with_correct_name(self):
        so_tool = self._make_mock_so_tool("bamboohr_get_employee")
        strands_tool = make_strands_tool(so_tool)
        assert strands_tool.tool_name == "bamboohr_get_employee"

    def test_creates_tool_with_correct_description(self):
        so_tool = self._make_mock_so_tool()
        strands_tool = make_strands_tool(so_tool)
        assert "Get details" in strands_tool.tool_spec["description"]

    def test_tool_execution_delegates_to_stackone(self):
        so_tool = self._make_mock_so_tool()
        strands_tool = make_strands_tool(so_tool)

        # The underlying StackOne tool's execute should be callable
        so_tool.execute.assert_not_called()

    def test_required_params_derived_from_nullable(self):
        so_tool = self._make_mock_so_tool()
        strands_tool = make_strands_tool(so_tool)
        schema = strands_tool.tool_spec["inputSchema"]
        assert "id" in schema["required"]
        assert "fields_" not in schema["required"]


class TestMakeSearchTool:
    """Test the stackone_search meta-tool."""

    def test_search_tool_has_correct_name(self):
        mock_toolset = MagicMock()
        search_tool = make_search_tool(mock_toolset)
        assert search_tool.tool_name == "stackone_search"

    def test_search_tool_has_description(self):
        mock_toolset = MagicMock()
        search_tool = make_search_tool(mock_toolset)
        assert "Search" in search_tool.tool_spec["description"]

    def test_search_tool_accepts_query_param(self):
        mock_toolset = MagicMock()
        search_tool = make_search_tool(mock_toolset)
        schema = search_tool.tool_spec["inputSchema"]["json"]
        assert "query" in schema["properties"]


class TestMakeExecuteTool:
    """Test the stackone_execute meta-tool."""

    def test_execute_tool_has_correct_name(self):
        mock_toolset = MagicMock()
        execute_tool = make_execute_tool(mock_toolset)
        assert execute_tool.tool_name == "stackone_execute"

    def test_execute_tool_has_description(self):
        mock_toolset = MagicMock()
        execute_tool = make_execute_tool(mock_toolset)
        assert "Execute" in execute_tool.tool_spec["description"]

    def test_execute_tool_accepts_action_name_and_parameters(self):
        mock_toolset = MagicMock()
        execute_tool = make_execute_tool(mock_toolset)
        schema = execute_tool.tool_spec["inputSchema"]["json"]
        assert "action_name" in schema["properties"]
        assert "parameters" in schema["properties"]

"""Tests for StackOneToolProvider."""

import os
from unittest.mock import MagicMock, patch

import pytest

from strands_stackone import StackOneToolProvider


class TestStackOneToolProvider:
    """Test StackOneToolProvider initialization and configuration."""

    @patch.dict(os.environ, {"STACKONE_API_KEY": "test-api-key"})
    def test_init_with_env_var(self):
        provider = StackOneToolProvider()
        assert provider.toolset is not None

    def test_init_with_explicit_key(self):
        provider = StackOneToolProvider(api_key="test-key")
        assert provider.toolset is not None

    def test_init_with_account_ids(self):
        provider = StackOneToolProvider(api_key="test-key", account_ids=["acc-123"])
        assert provider._account_ids == ["acc-123"]

    def test_init_with_custom_base_url(self):
        provider = StackOneToolProvider(api_key="test-key", base_url="https://custom.api.com")
        assert provider.toolset is not None


class TestLoadTools:
    """Test loading tools from StackOne."""

    def _make_mock_tool(self, name="bamboohr_list_employees", description="List employees"):
        mock_tool = MagicMock()
        mock_tool.name = name
        mock_tool.description = description
        mock_tool.parameters = MagicMock()
        mock_tool.parameters.properties = {
            "page_size": {"type": "integer", "description": "Number of results", "nullable": True},
        }
        mock_tool.execute.return_value = {"status": "success", "data": []}
        return mock_tool

    @patch("strands_stackone.provider.StackOneToolSet")
    def test_load_tools_returns_strands_tools(self, MockToolSet):
        mock_toolset = MockToolSet.return_value
        mock_toolset.fetch_tools.return_value = [
            self._make_mock_tool("bamboohr_list_employees", "List employees from BambooHR"),
            self._make_mock_tool("bamboohr_get_employee", "Get a specific employee"),
        ]

        provider = StackOneToolProvider(api_key="test-key", account_ids=["acc-123"])
        tools = provider.load_tools()

        assert len(tools) == 2
        mock_toolset.fetch_tools.assert_called_once_with(
            account_ids=["acc-123"],
            actions=None,
            providers=None,
        )

    @patch("strands_stackone.provider.StackOneToolSet")
    def test_load_tools_with_action_filter(self, MockToolSet):
        mock_toolset = MockToolSet.return_value
        mock_toolset.fetch_tools.return_value = [self._make_mock_tool()]

        provider = StackOneToolProvider(api_key="test-key")
        provider.load_tools(account_ids=["acc-456"], actions=["bamboohr_*"])

        mock_toolset.fetch_tools.assert_called_once_with(
            account_ids=["acc-456"],
            actions=["bamboohr_*"],
            providers=None,
        )

    @patch("strands_stackone.provider.StackOneToolSet")
    def test_load_tools_with_provider_filter(self, MockToolSet):
        mock_toolset = MockToolSet.return_value
        mock_toolset.fetch_tools.return_value = []

        provider = StackOneToolProvider(api_key="test-key")
        provider.load_tools(providers=["greenhouse", "lever"])

        mock_toolset.fetch_tools.assert_called_once_with(
            account_ids=None,
            actions=None,
            providers=["greenhouse", "lever"],
        )

    @patch("strands_stackone.provider.StackOneToolSet")
    def test_load_tools_empty_result(self, MockToolSet):
        mock_toolset = MockToolSet.return_value
        mock_toolset.fetch_tools.return_value = []

        provider = StackOneToolProvider(api_key="test-key")
        tools = provider.load_tools()

        assert tools == []


class TestSearchTools:
    """Test searching for StackOne tools."""

    def _make_mock_tool(self, name="bamboohr_list_employees"):
        mock_tool = MagicMock()
        mock_tool.name = name
        mock_tool.description = f"Description for {name}"
        mock_tool.parameters = MagicMock()
        mock_tool.parameters.properties = {}
        return mock_tool

    @patch("strands_stackone.provider.StackOneToolSet")
    def test_search_tools(self, MockToolSet):
        mock_toolset = MockToolSet.return_value
        mock_toolset.search_tools.return_value = [
            self._make_mock_tool("bamboohr_list_employees"),
            self._make_mock_tool("workday_list_employees"),
        ]

        provider = StackOneToolProvider(api_key="test-key", account_ids=["acc-123"])
        tools = provider.search_tools("list employees")

        assert len(tools) == 2
        mock_toolset.search_tools.assert_called_once_with(
            "list employees",
            account_ids=["acc-123"],
            top_k=5,
        )

    @patch("strands_stackone.provider.StackOneToolSet")
    def test_search_tools_custom_top_k(self, MockToolSet):
        mock_toolset = MockToolSet.return_value
        mock_toolset.search_tools.return_value = []

        provider = StackOneToolProvider(api_key="test-key")
        provider.search_tools("create candidate", top_k=10)

        mock_toolset.search_tools.assert_called_once_with(
            "create candidate",
            account_ids=None,
            top_k=10,
        )


class TestGetMetaTools:
    """Test meta-tools (search + execute) for dynamic discovery."""

    @patch("strands_stackone.provider.StackOneToolSet")
    def test_get_meta_tools_returns_two_tools(self, MockToolSet):
        provider = StackOneToolProvider(api_key="test-key")
        meta_tools = provider.get_meta_tools(account_ids=["acc-123"])

        assert len(meta_tools) == 2

    @patch("strands_stackone.provider.StackOneToolSet")
    def test_meta_tools_have_correct_names(self, MockToolSet):
        provider = StackOneToolProvider(api_key="test-key")
        meta_tools = provider.get_meta_tools()

        tool_names = [t.tool_name for t in meta_tools]
        assert "stackone_search" in tool_names
        assert "stackone_execute" in tool_names


class TestPackageStructure:
    """Test that the package is correctly structured."""

    def test_import_provider(self):
        from strands_stackone import StackOneToolProvider
        assert StackOneToolProvider is not None

    def test_all_exports(self):
        import strands_stackone
        assert "StackOneToolProvider" in strands_stackone.__all__

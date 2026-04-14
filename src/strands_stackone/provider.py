"""StackOne Tool Provider for Strands Agents.

Wraps the stackone-ai SDK to provide Strands-compatible tools that connect
AI agents to 200+ enterprise SaaS systems (HRIS, ATS, CRM, LMS, and more).
"""

import logging
from typing import Any

from stackone_ai import StackOneToolSet

from strands_stackone.tools import make_strands_tool, make_search_tool, make_execute_tool

logger = logging.getLogger(__name__)


class StackOneToolProvider:
    """Provides StackOne tools to Strands Agents.

    Wraps the stackone-ai SDK's StackOneToolSet to fetch, search, and execute
    StackOne actions as Strands-compatible tools.

    Args:
        api_key: StackOne API key. Falls back to STACKONE_API_KEY env var.
        account_ids: Default account IDs for multi-tenant scoping.
        base_url: StackOne API base URL. Defaults to https://api.stackone.com.
    """

    def __init__(
        self,
        api_key: str | None = None,
        account_ids: list[str] | None = None,
        base_url: str | None = None,
    ):
        self._toolset = StackOneToolSet(
            api_key=api_key,
            base_url=base_url,
            search={"method": "auto"},
        )
        self._account_ids = account_ids

    @property
    def toolset(self) -> StackOneToolSet:
        """Access the underlying StackOneToolSet for advanced usage."""
        return self._toolset

    def load_tools(
        self,
        *,
        account_ids: list[str] | None = None,
        actions: list[str] | None = None,
        providers: list[str] | None = None,
    ) -> list[Any]:
        """Fetch StackOne tools and return them as Strands-compatible tools.

        Connects to StackOne's MCP endpoint to discover available actions,
        then wraps each as a Strands @tool function.

        Args:
            account_ids: Account IDs to scope tools to. Overrides default.
            actions: Glob patterns to filter actions (e.g. ["bamboohr_*", "greenhouse_*"]).
            providers: Provider prefixes to filter (e.g. ["bamboohr", "greenhouse"]).

        Returns:
            List of Strands-compatible tool functions.
        """
        ids = account_ids or self._account_ids
        tools = self._toolset.fetch_tools(
            account_ids=ids,
            actions=actions,
            providers=providers,
        )

        strands_tools = []
        for so_tool in tools:
            strands_tools.append(make_strands_tool(so_tool))

        logger.info("Loaded %d StackOne tools for Strands agent", len(strands_tools))
        return strands_tools

    def search_tools(
        self,
        query: str,
        *,
        account_ids: list[str] | None = None,
        top_k: int = 5,
    ) -> list[Any]:
        """Search for StackOne tools by natural language query.

        Uses StackOne's semantic search to find relevant actions, then
        wraps them as Strands-compatible tools.

        Args:
            query: Natural language description of desired action.
            account_ids: Account IDs to scope search to.
            top_k: Maximum number of results to return.

        Returns:
            List of Strands-compatible tool functions matching the query.
        """
        ids = account_ids or self._account_ids
        tools = self._toolset.search_tools(
            query,
            account_ids=ids,
            top_k=top_k,
        )

        strands_tools = []
        for so_tool in tools:
            strands_tools.append(make_strands_tool(so_tool))

        logger.info("Found %d StackOne tools for query: %s", len(strands_tools), query)
        return strands_tools

    def get_meta_tools(
        self,
        *,
        account_ids: list[str] | None = None,
        top_k: int = 5,
    ) -> list[Any]:
        """Get search + execute meta-tools for dynamic tool discovery.

        Returns two tools that let the agent:
        1. stackone_search - Search for available actions by description
        2. stackone_execute - Execute a discovered action by name

        This pattern lets agents discover and use tools on-the-fly without
        needing all tools loaded upfront.

        Args:
            account_ids: Account IDs to scope operations to.
            top_k: Max results for search tool.

        Returns:
            List containing [stackone_search, stackone_execute] tools.
        """
        ids = account_ids or self._account_ids
        return [
            make_search_tool(self._toolset, account_ids=ids, top_k=top_k),
            make_execute_tool(self._toolset, account_ids=ids),
        ]

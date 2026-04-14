"""Tool factories for wrapping StackOne actions as Strands tools.

Converts StackOne SDK tool objects into Strands-compatible @tool functions
that can be passed directly to a Strands Agent.
"""

import json
import logging
from typing import Any

from strands import tool
from stackone_ai import StackOneToolSet
from stackone_ai.models import StackOneTool

logger = logging.getLogger(__name__)


def make_strands_tool(so_tool: StackOneTool) -> Any:
    """Wrap a StackOneTool as a Strands-compatible tool function.

    Creates a dynamically-named tool function that the Strands agent can call.
    The tool's name, description, and parameters are derived from the StackOne
    tool definition.

    Args:
        so_tool: A StackOneTool instance from the stackone-ai SDK.

    Returns:
        A Strands @tool-decorated function.
    """
    tool_name = so_tool.name
    tool_description = so_tool.description
    tool_params = so_tool.parameters

    # Build JSON Schema for the tool's input
    properties = tool_params.properties if tool_params else {}
    required = [k for k, v in properties.items() if not v.get("nullable", True)]

    input_schema = {
        "type": "object",
        "properties": {k: _clean_property(v) for k, v in properties.items()},
        "required": required,
    }

    @tool(name=tool_name, description=tool_description, inputSchema=input_schema)
    def _stackone_action(**kwargs: Any) -> dict[str, Any]:
        result = so_tool.execute(kwargs)
        return result

    return _stackone_action


def make_search_tool(
    toolset: StackOneToolSet,
    *,
    account_ids: list[str] | None = None,
    top_k: int = 5,
) -> Any:
    """Create a Strands tool that searches for available StackOne actions.

    The agent calls this tool with a natural language query to discover
    what actions are available (e.g. "list employees", "create candidate").

    Args:
        toolset: The StackOneToolSet instance.
        account_ids: Account IDs to scope search to.
        top_k: Maximum number of results.

    Returns:
        A Strands @tool function for searching StackOne actions.
    """

    @tool
    def stackone_search(query: str) -> dict[str, Any]:
        """Search for available StackOne actions by natural language description.

        Use this tool to discover what actions are available before executing them.
        For example, search for "list employees" or "create job posting" to find
        relevant actions across connected HRIS, ATS, CRM, LMS, and other systems.

        Args:
            query: Natural language description of the action you're looking for.

        Returns:
            A list of matching actions with their names, descriptions, and parameters.
        """
        tools = toolset.search_tools(query, account_ids=account_ids, top_k=top_k)

        results = []
        for t in tools:
            params = t.parameters
            param_info = {}
            if params and params.properties:
                for k, v in params.properties.items():
                    param_info[k] = {
                        "type": v.get("type", "string"),
                        "description": v.get("description", ""),
                        "required": not v.get("nullable", True),
                    }

            results.append({
                "action_name": t.name,
                "description": t.description,
                "parameters": param_info,
            })

        return {
            "status": "success",
            "query": query,
            "results_count": len(results),
            "actions": results,
        }

    return stackone_search


def make_execute_tool(
    toolset: StackOneToolSet,
    *,
    account_ids: list[str] | None = None,
) -> Any:
    """Create a Strands tool that executes a StackOne action by name.

    The agent calls this after using stackone_search to discover available
    actions. It takes an action name and parameters, and executes it.

    Args:
        toolset: The StackOneToolSet instance.
        account_ids: Account IDs to scope execution to.

    Returns:
        A Strands @tool function for executing StackOne actions.
    """
    # Cache fetched tools to avoid re-fetching on every execute call
    _tool_cache: dict[str, StackOneTool] = {}

    @tool
    def stackone_execute(action_name: str, parameters: str = "{}") -> dict[str, Any]:
        """Execute a StackOne action by name with the given parameters.

        Use this after stackone_search to run a discovered action. Pass the
        action_name exactly as returned by stackone_search, and provide the
        required parameters as a JSON string.

        Args:
            action_name: The exact action name from stackone_search results.
            parameters: JSON string of parameters for the action.

        Returns:
            The result of executing the action.
        """
        # Parse parameters
        if isinstance(parameters, str):
            try:
                params = json.loads(parameters)
            except json.JSONDecodeError:
                return {"status": "error", "message": f"Invalid JSON parameters: {parameters}"}
        else:
            params = parameters

        # Find the tool - check cache first, then fetch
        if action_name not in _tool_cache:
            connector = action_name.split("_")[0] if "_" in action_name else None
            try:
                tools = toolset.fetch_tools(
                    account_ids=account_ids,
                    providers=[connector] if connector else None,
                )
                for t in tools:
                    _tool_cache[t.name] = t
            except Exception as e:
                logger.warning("Failed to fetch tools for connector %s: %s", connector, e)

        so_tool = _tool_cache.get(action_name)
        if not so_tool:
            return {
                "status": "error",
                "message": f"Action '{action_name}' not found. Use stackone_search to discover available actions.",
            }

        try:
            result = so_tool.execute(params)
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}

    return stackone_execute


def _clean_property(prop: dict[str, Any]) -> dict[str, Any]:
    """Clean a JSON Schema property for Strands tool compatibility.

    Removes non-standard keys and normalizes the schema.
    """
    cleaned: dict[str, Any] = {}
    for key in ("type", "description", "enum", "items", "properties", "default"):
        if key in prop:
            cleaned[key] = prop[key]
    return cleaned

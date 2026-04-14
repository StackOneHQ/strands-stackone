"""StackOne integration for Strands Agents.

Connect your AI agents to 200+ enterprise SaaS systems via StackOne's
AI Agent Integration Gateway.

Usage:

    # Tool Provider pattern - fetch tools and pass to agent
    from strands import Agent
    from strands_stackone import StackOneToolProvider

    provider = StackOneToolProvider(account_ids=["acc-123"])
    agent = Agent(tools=provider.load_tools())

    # Search-driven pattern - agent discovers tools dynamically
    from strands_stackone import StackOneToolProvider

    provider = StackOneToolProvider()
    agent = Agent(tools=provider.get_meta_tools(account_ids=["acc-123"]))
    agent("Find all employees in the engineering department")
"""

from strands_stackone.provider import StackOneToolProvider

__all__ = [
    "StackOneToolProvider",
]

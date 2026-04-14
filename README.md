# strands-stackone

[StackOne](https://stackone.com) integration for [Strands Agents](https://strandsagents.com) -- connect your AI agents to 200+ enterprise SaaS systems.

[![PyPI](https://img.shields.io/pypi/v/strands-stackone)](https://pypi.org/project/strands-stackone/)
[![CI](https://github.com/StackOneHQ/strands-stackone/actions/workflows/ci.yml/badge.svg)](https://github.com/StackOneHQ/strands-stackone/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

## What is this?

This package lets your Strands agents take action across enterprise SaaS -- HRIS, ATS, CRM, LMS, IAM, documents, project management, and more -- through StackOne's AI Agent Integration Gateway.

Your agent thinks. StackOne takes action.

## Installation

```bash
pip install strands-stackone
```

## Quick start

### Option 1: Load specific tools

Fetch tools for specific connectors and pass them directly to your agent:

```python
import os
from strands import Agent
from strands_stackone import StackOneToolProvider

os.environ["STACKONE_API_KEY"] = "your-api-key"

provider = StackOneToolProvider(account_ids=["your-account-id"])
tools = provider.load_tools(providers=["bamboohr"])

agent = Agent(tools=tools)
agent("List all employees in the engineering department")
```

### Option 2: Search-driven discovery

Let the agent discover available tools dynamically using search + execute meta-tools:

```python
from strands import Agent
from strands_stackone import StackOneToolProvider

provider = StackOneToolProvider(account_ids=["your-account-id"])
agent = Agent(tools=provider.get_meta_tools())

agent("Find and list all open job postings, then get the details of the most recent one")
```

The agent will:
1. Call `stackone_search` to discover relevant actions
2. Call `stackone_execute` to run the discovered actions

### Option 3: Search then load

Search for tools by description, then pass the results to an agent:

```python
provider = StackOneToolProvider(account_ids=["your-account-id"])
hr_tools = provider.search_tools("employee management")

agent = Agent(tools=hr_tools)
agent("Get the headcount by department")
```

## Configuration

| Parameter | Environment Variable | Description |
|-----------|---------------------|-------------|
| `api_key` | `STACKONE_API_KEY` | Your StackOne API key |
| `account_ids` | -- | Connected account IDs for multi-tenant scoping |
| `base_url` | -- | API base URL (default: `https://api.stackone.com`) |

Get your API key at [app.stackone.com](https://app.stackone.com).

## Supported categories

StackOne provides 200+ connectors across:

- **HRIS**: Workday, BambooHR, HiBob, Personio, Gusto, and more
- **ATS**: Greenhouse, Ashby, Lever, Workable, SmartRecruiters
- **CRM**: Salesforce, HubSpot, Pipedrive
- **LMS**: Docebo, Udemy, Cornerstone
- **IAM**: Okta, OneLogin
- **Documents**: SharePoint, Google Drive, Notion, Confluence
- **Project Management**: Asana, Jira, Linear, ClickUp
- **Marketing**: Mailchimp, Klaviyo, Intercom
- **Finance**: QuickBooks, Xero, NetSuite
- **Collaboration**: Slack, Microsoft Teams

## Development

```bash
# Install dev dependencies
pip install hatch

# Run tests
hatch run test

# Lint and format
hatch run prepare
```

## License

Apache 2.0

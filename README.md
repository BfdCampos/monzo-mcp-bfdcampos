# 🏦 Monzo MCP Server

A Model Context Protocol (MCP) server that provides access to your Monzo banking data through a Claude tool.

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/BfdCampos/monzo-mcp-bfdcampos.git
cd monzo-mcp-bfdcampos/monzo-mcp-bfdcampos

# Install dependencies using uv (Python package manager)
uv install
```

## 🔑 API Setup

Create a `.env` file in the project directory with your Monzo credentials:

```
MONZO_ACCESS_TOKEN='your_access_token'
MONZO_USER_ID='your_user_id'
MONZO_ACCOUNT_ID='your_account_id'
```

> [!NOTE]
> To get your credentials, follow the instructions in the [official Monzo Dev API Docs](https://docs.monzo.com/)

## 🔧 Setup with Claude Desktop

### Method 1: Automatic Installation

Use the MCP CLI tool to install the server automatically:

```bash
uv run mcp install main.py
```

### Method 2: Manual Configuration

Add the server to your Claude Desktop configuration file located at `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "Monzo": {
      "command": "/Users/[Your Home Directory]/.local/bin/uv",
      "args": [
        "run",
        "--with",
        "mcp[cli],requests",
        "mcp",
        "run",
        "/path/to/your/monzo-mcp-bfdcampos/monzo-mcp-bfdcampos/main.py"
      ]
    }
  }
}
```

> **Note:** Replace `/path/to/your/` with your actual paths.
> **Important:** Make sure to include `requests` in the `--with` argument as shown above.

## 🤖 Using with Claude Desktop

1. Restart Claude Desktop after installation.
2. Open the app and start a new conversation.
3. You can now ask Claude about your Monzo account balance.

## 📊 Available Functions

### balance

Returns your current Monzo account balance and currency.

```python
response = {
    "balance": 91.55,  # Amount in decimal (e.g., £91.55)
    "currency": "GBP"
}
```

## ❓ FAQ

<details><summary>My Claude Desktop is not detecting the server</summary>

- Ensure you have the latest version of Claude Desktop.
- Restart Claude Desktop by force quitting the app and reopening it.
- Make sure your path is correct in the configuration file.
- Use the absolute path to your `uv` installation, e.g., `/Users/[Your Home Directory]/.local/bin/uv` in the command section of the configuration file.
- Verify that the `requests` library is included in the `--with` argument list in your configuration, as this is a common cause of connection issues.

</details>

<details><summary>I've asked Claude about my balance but it's not using the MCP server</summary>

- LLMs like Claude may not always use the MCP server for every request. Try rephrasing your question, specifically asking Claude to check your Monzo balance using the Monzo MCP tool.
- You can check if there were any errors by looking at the logs in `~/Library/Logs/Claude/mcp-server-Monzo.log`.

</details>

<details><summary>What is uv?</summary>

- `uv` is a Python package manager and installer that's designed to be much faster than pip.
- It maintains isolated environments for your projects and resolves dependencies efficiently.
- Learn more at [github.com/astral-sh/uv](https://github.com/astral-sh/uv).

</details>

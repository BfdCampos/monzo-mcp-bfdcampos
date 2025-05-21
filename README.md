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

> [!NOTE]
> To get your credentials, follow the instructions in the [official Monzo Dev API Docs](https://docs.monzo.com/)

```
MONZO_ACCESS_TOKEN='your_access_token'
MONZO_USER_ID='your_user_id'
MONZO_ACCOUNT_ID='your_default_account_id'

# Add specific account IDs for different account types
MONZO_UK_PREPAID_PERSONAL_ACCOUNT_ID='your_prepaid_account_id'
MONZO_UK_RETAIL_PERSONAL_ACCOUNT_ID='your_personal_account_id'
MONZO_UK_MONZO_FLEX_PERSONAL_ACCOUNT_ID='your_flex_account_id'
MONZO_UK_REWARDS_PERSONAL_ACCOUNT_ID='your_rewards_account_id'
MONZO_UK_RETAIL_JOINT_JOINT_ACCOUNT_ID='your_joint_account_id'
```

> [!NOTE]
> I recommend getting the account IDs and adding them to your dotenv file to have a smoother experience with the server and reduce the number of API calls. This can also be found in the [official Monzo Dev API Docs](https://docs.monzo.com/).

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
3. You can now ask Claude about your Monzo accounts:
   - "What's my current balance?"
   - "How much money do I have in my joint account?"
   - "Show me all my Monzo accounts"
   - "Move £50 from my personal account to my Savings pot"
   - "Show me my transactions from today"

## 📊 Available Functions

<details>
<summary>

### 💷 [balance](https://docs.monzo.com/#balance)

</summary>

Returns the balance, spending today, and currency for a specified account type.

Parameters:

- `account_type` (optional): Type of account to check balance for. Options: "default", "personal", "prepaid", "flex", "rewards", "joint"

Example requests:

```
What's my current balance?
How much money do I have in my joint account?
What's the balance of my flex account?
```

</details>

<details>
<summary>

### 🍯 [pots](https://docs.monzo.com/#pots)

</summary>

Returns the list of pots for a specified account type.

Parameters:

- `account_type` (optional): Type of account to check pots for. Options: "default", "personal", "prepaid", "flex", "rewards", "joint"

Example requests:

```
Show me my pots
How many pots do I have?
How much money do I have in my "Savings" pot?
```

</details>

<details>
<summary>

### 🪙 [pot_deposit](https://docs.monzo.com/#deposit-into-a-pot)

</summary>

Deposit money from an account into a pot.

Parameters:

- `pot_id` (required): The ID of the pot to deposit money into
- `amount` (required): The amount to deposit in pence (e.g., 1000 for £10.00)
- `account_type` (optional): The account to withdraw from. Default is "personal"
- `triggered_by` (optional): Source identifier for the transaction. Default is "mcp"

Example requests:

```
Add £25 to my Savings pot
Move £10 from my personal account to my Holiday pot
```

</details>

<details>
<summary>

### 🏧 [pot_withdraw](https://docs.monzo.com/#withdraw-from-a-pot)

</summary>

Withdraw money from a pot back to an account.

Parameters:

- `pot_id` (required): The ID of the pot to withdraw money from
- `amount` (required): The amount to withdraw in pence (e.g., 1000 for £10.00)
- `account_type` (optional): The account to deposit into. Default is "personal"
- `triggered_by` (optional): Source identifier for the transaction. Default is "mcp"

Example requests:

```
Take £25 from my Savings pot
Withdraw £10 from my Holiday pot to my personal account
```

</details>

<details>
<summary>

### 🧾 [list_transactions](https://docs.monzo.com/#list-transactions)

</summary>

Lists transactions for a specified account.

Parameters:

- `account_type` (optional): Type of account to list transactions for. Default is "personal"
- `since` (optional): Start date for transactions in ISO 8601 format (e.g., "2025-05-20T00:00:00Z")
- `before` (optional): End date for transactions in ISO 8601 format
- `limit` (optional): Maximum number of transactions to return. Default is 1000

Example requests:

```
Show me my recent transactions
What transactions do I have from today?
List all transactions from my joint account this month
```

</details>

<details>
<summary>

### 📖 [retrieve_transaction](https://docs.monzo.com/#retrieve-transaction)

</summary>

Retrieves details of a specific transaction.

Parameters:

- `transaction_id` (required): The ID of the transaction to retrieve
- `expand` (optional): Additional data to include in the response. Default is "merchant"

Example requests:

```
Show me the details of my last transaction
What was the last transaction I made?
```

</details>

<details>
<summary>

### 📝 [annotate_transaction](https://docs.monzo.com/#annotate-transaction)

</summary>

Edits the metadata of a transaction.

Parameters:

- `transaction_id` (required): The ID of the transaction to annotate
- `metadata_key` (required): The key of the metadata to edit. Default is 'notes'
- `metadata_value` (required): The new value for the metadata key. Empty values will remove the key
- `delete_note` (optional): If set to true, the note will be deleted. Default is false

Example requests:

```
Add a note to my last transaction saying "Dinner with friends"
Remove the note from my last transaction
```

</details>

## 📦 Missing Functions from the Monzo MCP present in the Monzo API

- [Create feed item](https://docs.monzo.com/#create-feed-item)
- [Upload Attachment](https://docs.monzo.com/#upload-attachment)
- [Register Attachment](https://docs.monzo.com/#register-attachment)
- [Deregister Attachement](https://docs.monzo.com/#deregister-attachment)
- [Create Receipt](https://docs.monzo.com/#create-receipt)
- [Retrieve Receipt](https://docs.monzo.com/#retrieve-receipt)
- [Delete Receipt](https://docs.monzo.com/#delete-receipt)
- [Registering a Webhook](https://docs.monzo.com/#registering-a-webhook)
- [List Webhooks](https://docs.monzo.com/#list-webhooks)
- [Deleting a Webhook](https://docs.monzo.com/#deleting-a-webhook)
- [Transaction Created](https://docs.monzo.com/#transaction-created)
- [General Payment Initiation for outside your own Monzo Account transfers](https://docs.monzo.com/#payment-initiation-services-api)

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

<details><summary>How do pot deposits and withdrawals work?</summary>

- When you deposit money into a pot or withdraw from a pot, the MCP creates a unique dedupe_id that includes the "triggered_by" parameter.
- This helps identify transactions and prevents accidental duplicate transactions.
- The default "triggered_by" value is "mcp", but you can customise this to track different sources of pot transfers.

</details>

<details><summary>What is uv?</summary>

- `uv` is a Python package manager and installer that's designed to be much faster than pip.
- It maintains isolated environments for your projects and resolves dependencies efficiently.
- Learn more at [github.com/astral-sh/uv](https://github.com/astral-sh/uv).

</details>

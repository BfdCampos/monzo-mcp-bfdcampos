from mcp.server.fastmcp import FastMCP
import requests
from dotenv import load_dotenv
import os
import uuid
import datetime

load_dotenv()

mcp = FastMCP("Monzo")

access_token = {}
access_token["b"] = os.getenv("B_MONZO_ACCESS_TOKEN")
access_token["m"] = os.getenv("M_MONZO_ACCESS_TOKEN")

user_id = {}
user_id["b"] = os.getenv("B_MONZO_USER_ID")
user_id["m"] = os.getenv("M_MONZO_USER_ID")

last_hour = (datetime.datetime.utcnow() - datetime.timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

account_types = {}
account_types["b"] = {
    "default": os.getenv("B_MONZO_UK_RETAIL_PERSONAL_ACCOUNT_ID"),
    "personal": os.getenv("B_MONZO_UK_RETAIL_PERSONAL_ACCOUNT_ID"),
    "prepaid": os.getenv("B_MONZO_UK_PREPAID_PERSONAL_ACCOUNT_ID"),
    "flex": os.getenv("B_MONZO_UK_MONZO_FLEX_PERSONAL_ACCOUNT_ID"),
    "rewards": os.getenv("B_MONZO_UK_REWARDS_PERSONAL_ACCOUNT_ID"),
    "joint": os.getenv("B_MONZO_UK_RETAIL_JOINT_JOINT_ACCOUNT_ID")
}
account_types["m"] = {
    "default": os.getenv("M_MONZO_UK_RETAIL_PERSONAL_ACCOUNT_ID"),
    "personal": os.getenv("M_MONZO_UK_RETAIL_PERSONAL_ACCOUNT_ID"),
    "prepaid": os.getenv("M_MONZO_UK_PREPAID_PERSONAL_ACCOUNT_ID"),
    "flex": os.getenv("M_MONZO_UK_MONZO_FLEX_PERSONAL_ACCOUNT_ID"),
    "rewards": None,  # Rewards account not available for Monzo UK
    "joint": os.getenv("M_MONZO_UK_RETAIL_JOINT_JOINT_ACCOUNT_ID")
}

url = "https://api.monzo.com/"
balance_url = f"{url}balance"
accounts_url = f"{url}accounts"
pots_url = f"{url}pots"
transactions_url = f"{url}transactions"

@mcp.tool("balance")
def get_balance(account_type: str = "personal", user: str = "b", total_balance: bool = False) -> dict:
    """
    Returns the information about an account including the balance in the lower denomination 
    of the specified Monzo account's currency. I.e. GBP, the balance is in pence. E.g. 9155 is £91.55.
    
    Parameters:
    account_type (str): Type of account to check balance for. 
                       Options: "personal", "prepaid", "flex", "rewards", "joint"
                       Defaults to "personal".
    user (str): Which user's account to access ("b" or "m"). Defaults to "b".
    total_balance (bool): If specifically asked for the total account balance, set this to True and it returns the total balance including flexible savings. Default is False.

    Returns:
    {
        "balance": int,
        "total_balance": int, # only if total_balance is True
        "balance_including_flexible_savings": int, # only if total_balance is True
        "currency": str,
        "spend_today": int,
        "local_currency": str,
        "local_exchange_rate": float,
        "local_spend": array,
    }
    """
    # Get token and account ID based on user and account_type
    selected_token = access_token[user]
    selected_account_id = account_types[user][account_type]
    
    if not selected_account_id:
        raise Exception(f"Account type '{account_type}' not available for user '{user}'")
        
    headers = {
        "Authorization": f"Bearer {selected_token}",
        "Content-Type": "application/json",
    }

    params = {
        "account_id": selected_account_id,
    }

    response = requests.get(balance_url, headers=headers, params=params)
    response_data = response.json()

    if response.status_code != 200:
        raise Exception(f"Error: {response_data.get('error', 'Unknown error')}")

    if total_balance:
        return response_data

    response_data.pop("total_balance", None)
    response_data.pop("balance_including_flexible_savings", None)

    return response_data

@mcp.tool("pots")
def get_pots_information(account_type: str = "personal", user: str = "b") -> dict:
    """
    Returns the pots information of the specified Monzo account including the balance
    in the lower denomination of the specified Monzo account's currency.
    I.e. GBP, the balance is in pence. E.g. 9155 is £91.55.
    
    Parameters:
    account_type (str): Type of account to check pots for. 
                       Options: "personal", "prepaid", "flex", "rewards", "joint"
                       Defaults to "personal".
    user (str): Which user's account to access ("b" or "m"). Defaults to "b".

    Returns:
    {
        "pots": [
            {
                "id": str,
                "name": str,
                "style": str,
                "balance": int,
                "currency": str,
                "type": str,
                "product_id": str,
                "current_account_id": str,
                "cover_image_url": str,
                "isa_wrapper": str,
                "round_up": bool,
                "round_up_multiplier": int,
                "is_tax_pot": bool,
                "created": str (UTC ISO 8601),
                "updated": str (UTC ISO 8601),
                "deleted": bool,
                "locked": bool,
                "available_for_bills": bool,
                "has_virtual_cards": bool,
            },
            ...
        ]
    }

    """
    # Get token and account ID based on user and account_type
    selected_token = access_token[user]
    selected_account_id = account_types[user][account_type]
    
    if not selected_account_id:
        raise Exception(f"Account type '{account_type}' not available for user '{user}'")
        
    headers = {
        "Authorization": f"Bearer {selected_token}",
        "Content-Type": "application/json",
    }
    
    params = {
        "current_account_id": selected_account_id,
    }

    response = requests.get(pots_url, headers=headers, params=params)
    response_data = response.json()

    if response.status_code != 200:
        raise Exception(f"Error: {response_data.get('error', 'Unknown error')}")

    pots = response_data.get("pots", [])

    return pots

@mcp.tool("pot_deposit")
def pot_deposit(
        pot_id: str,
        amount: int,
        account_type: str = "personal",
        user: str = "b"
) -> dict:

    """
    Deposit money into a pot.
    
    Parameters:
    pot_id (str): The ID of the pot to deposit money into.
    amount (int): The amount to deposit in the lower denomination of the specified Monzo account's currency.
                  I.e. GBP, the amount is in pence. E.g. 9155 is £91.55.
    account_type (str): Type of account to deposit into. 
                        Options: "personal", "prepaid", "flex", "rewards", "joint"
                        Defaults to "personal".
    user (str): Which user's account to access ("b" or "m"). Defaults to "b".
    
    Returns:
    {
        "id": str,
        "name": str,
        "style": str,
        "balance": int,
        "currency": str,
        "type": str,
        "product_id": str,
        "current_account_id": str,
        "cover_image_url": str,
        "isa_wrapper": str,
        "round_up": bool,
        "round_up_multiplier": int,
        "is_tax_pot": bool,
        "created": str (UTC ISO 8601),
        "updated": str (UTC ISO 8601),
        "deleted": bool,
        "locked": bool,
        "available_for_bills": bool,
        "has_virtual_cards": bool,
        "dedupe_id": str, # Unique ID for the deposit transaction generated by the tool, use this to identify the transaction
        "metadata": {
            "external_id": str, # The same as dedupe_id but in the format it appears when retrived either with the list_transactions or retrieve_transaction tools
        },
        "triggered_timestamp": str (UTC ISO 8601), # The timestamp of the deposit transaction useful to filter the list_transactions tool with `since: current_timestamp UTC minus an hour`
    }
    """
    # Get token and account ID based on user and account_type
    selected_token = access_token[user]
    selected_account_id = account_types[user][account_type]
    
    if not selected_account_id:
        raise Exception(f"Account type '{account_type}' not available for user '{user}'")

    url = f"{pots_url}/{pot_id}/deposit"

    triggered_by = "mcp"

    dedupe_id = f"{triggered_by}_{str(uuid.uuid4())}"
        
    headers = {
        "Authorization": f"Bearer {selected_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    
    data = {
        "source_account_id": selected_account_id,
        "amount": amount,
        "dedupe_id": dedupe_id,
    }

    response = requests.put(url, headers=headers, data=data)
    
    if response.status_code != 200:
        raise Exception(f"Error: {response.json().get('error', 'Unknown error')}")

    # Add dedupe_id and the current timestamp to the response
    response_data = response.json()

    response_data["dedupe_id"] = dedupe_id
    response_data["metadata"] = {
        "external_id": dedupe_id
    }
    response_data["triggered_timestamp"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    return response_data

@mcp.tool("pot_withdraw")
def pot_withdraw(
        pot_id: str,
        amount: int,
        account_type: str = "personal",
        user: str = "b"
) -> dict:
    """
    Withdraw money from a pot.
    
    Parameters:
    pot_id (str): The ID of the pot to withdraw money from.
    amount (int): The amount to withdraw in the lower denomination of the specified Monzo account's currency.
                  I.e. GBP, the amount is in pence. E.g. 9155 is £91.55.
    account_type (str): Type of account to withdraw from. 
                        Options: "personal", "prepaid", "flex", "rewards", "joint"
                        Defaults to "personal".
    user (str): Which user's account to access ("b" or "m"). Defaults to "b".
    
    Returns:
    {
        "id": str,
        "name": str,
        "style": str,
        "balance": int,
        "currency": str,
        "type": str,
        "product_id": str,
        "current_account_id": str,
        "cover_image_url": str,
        "isa_wrapper": str,
        "round_up": bool,
        "round_up_multiplier": int,
        "is_tax_pot": bool,
        "created": str (UTC ISO 8601),
        "updated": str (UTC ISO 8601),
        "deleted": bool,
        "locked": bool,
        "available_for_bills": bool,
        "has_virtual_cards": bool,
        "dedupe_id": str, # Unique ID for the withdrawal transaction generated by the tool, use this to identify the transaction
        "metadata": {
            "external_id": str, # The same as dedupe_id but in the format it appears when retrived either with the list_transactions or retrieve_transaction tools
        },
        "triggered_timestamp": str (UTC ISO 8601), # The timestamp of the withdrawal transaction useful to filter the list_transactions tool with `since: current_timestamp UTC minus an hour`
    }
    """
    # Get token and account ID based on user and account_type
    selected_token = access_token[user]
    selected_account_id = account_types[user][account_type]
    
    if not selected_account_id:
        raise Exception(f"Account type '{account_type}' not available for user '{user}'")

    url = f"{pots_url}/{pot_id}/withdraw"

    triggered_by = "mcp"

    dedupe_id = f"{triggered_by}_{str(uuid.uuid4())}"
        
    headers = {
        "Authorization": f"Bearer {selected_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    
    data = {
        "destination_account_id": selected_account_id,
        "amount": amount,
        "dedupe_id": dedupe_id,
    }

    response = requests.put(url, headers=headers, data=data)
    
    if response.status_code != 200:
        raise Exception(f"Error: {response.json().get('error', 'Unknown error')}")

    response_data = response.json()

    response_data["dedupe_id"] = dedupe_id
    response_data["metadata"] = {
        "external_id": dedupe_id
    }
    response_data["triggered_timestamp"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    return response_data

@mcp.tool("list_transactions")
def list_transactions(
        account_type: str = "personal",
        user: str = "b",
        since: str = last_hour,
        before: str = None,
        limit: int = 1000
    ) -> dict:
    """
    Returns a list of transactions for the specified Monzo account.
    
    Parameters:
    account_type (str): Type of account to list transactions for. 
                        Options: "personal", "prepaid", "flex", "rewards", "joint"
                        Defaults to "personal".
    user (str): Which user's account to access ("b" or "m"). Defaults to "b".
    since (str): The start date for the transactions in ISO 8601 format. Default is the last hour.
    before (str): The end date for the transactions in ISO 8601 format. Default is None.
    limit (int): The maximum number of transactions to return. Default is 1000.

    Returns:
    {
        "transactions": [
            {
                "id": str,
                "created": str (UTC ISO 8601),
                "description": str,
                "amount": int,
                "fees": {},
                "currency": str,
                "merchant": str,
                "merchant_feedback_uri": str,
                "notes": str,
                "metadata": {
                    "external_id": str,
                    "ledger_committed_timestamp_earliest": str (UTC ISO 8601),
                    "ledger_committed_timestamp_latest": str (UTC ISO 8601),
                    "ledger_insertion_id": str,
                    "pot_account_id": str,
                    "pot_id": str,
                    "pot_withdrawal_id": str,
                    "trigger": str,
                    "user_id": str,
                },
                "labels": [],
                "attachments": [],
                "international": str,
                "category": str,
                "categories": {
                    "transfers": int,
                },
                "is_load": bool,
                "settled": str (UTC ISO 8601),
                "local_amount": int,
                "local_currency": str,
                "updated": str (UTC ISO 8601),
                "account_id": str,
                "user_id": str,
                "counterparty": {},
                "scheme": str,
                "dedupe_id": str,
                "originator": bool,
                "include_in_spending": bool,
                "can_be_excluded_from_breakdown": bool,
                "can_be_made_subscription": bool,
                "can_split_the_bill": bool,
                "can_add_to_tab": bool,
                "can_match_transactions_in_categorization": bool,
                "amount_is_pending": bool,
                "atm_fees_detailed": {}
                "parent_account_id": str,
            },
            ...
        ]
    }
    """
    # Get token and account ID based on user and account_type
    selected_token = access_token[user]
    selected_account_id = account_types[user][account_type]
    
    if not selected_account_id:
        raise Exception(f"Account type '{account_type}' not available for user '{user}'")

    headers = {
        "Authorization": f"Bearer {selected_token}",
        "Content-Type": "application/json",
    }

    params = {
        "account_id": selected_account_id,
        "since": since,
        "before": before,
        "limit": limit,
        "expand[]": "merchant",
    }

    response = requests.get(transactions_url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(f"Error: {response.json().get('error', 'Unknown error')}")

    response_data = response.json()

    transactions = response_data.get("transactions", [])

    return transactions

@mcp.tool("retrieve_transaction")
def retrieve_transaction(
        transaction_id: str,
        user: str = "b",
        expand: str = "merchant"
    ) -> dict:
    """
    Returns the details of a specific transaction.
    
    Parameters:
    transaction_id (str): The ID of the transaction to retrieve.
    user (str): Which user's account to access ("b" or "m"). Defaults to "b".
    expand (str): Optional. The type of data to expand. Default is "merchant".

    Returns:
    {
        "transaction": {
            "id": str,
            "created": str (UTC ISO 8601),
            "description": str,
            "amount": int,
            "fees": {},
            "currency": str,
            "merchant": str,
            "merchant_feedback_uri": str,
            "notes": str,
            "metadata": {
                "external_id": str,
                "ledger_committed_timestamp_earliest": str (UTC ISO 8601),
                "ledger_committed_timestamp_latest": str (UTC ISO 8601),
                "ledger_insertion_id": str,
                "notes": str,
                "pot_account_id": str,
                "pot_deposit_id": str,
                "pot_id": str,
                "series_id": str,
                "series_iteration_count": str,
                "trigger": str,
                "user_id": str,
            },
            "labels": [],
            "attachments": [],
            "international": str,
            "category": str,
            "categories": {
                "transfers": int,
            },
            "is_load": bool,
            "settled": str (UTC ISO 8601),
            "local_amount": int,
            "local_currency": str,
            "updated": str (UTC ISO 8601),
            "account_id": str,
            "user_id": str,
            "counterparty": {},
            "scheme": str,
            "dedupe_id": str,
            "originator": bool,
            "include_in_spending": bool,
            "can_be_excluded_from_breakdown": bool,
            "can_be_made_subscription": bool,
            "can_split_the_bill": bool,
            "can_add_to_tab": bool,
            "can_match_transactions_in_categorization": bool,
            "amount_is_pending": bool,
            "atm_fees_detailed": {},
            "parent_account_id": str,
        }
    }
    """

    headers = {
        "Authorization": f"Bearer {access_token[user]}",
        "Content-Type": "application/json",
    }

    params = {
        "expand[]": expand,
    }

    response = requests.get(f"{transactions_url}/{transaction_id}", headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(f"Error: {response.json().get('error', 'Unknown error')}")

    response_data = response.json()

    return response_data

@mcp.tool("annotate_transaction")
def annotate_transaction(
        transaction_id: str,
        user: str = "b",
        metadata_key: str = "notes",
        metadata_value: str = "",
        delete_note: bool = False
    ) -> dict:
    """
    Annotate a transaction with a note or metadata key-value pair.

    To delete a note, set delete_note to True and use the default metadata_key "notes" and metadata_value "".
    To delete another key, set its value to an empty string.
    
    Parameters:
    transaction_id (str): The ID of the transaction to annotate.
    user (str): Which user's account to access ("b" or "m"). Defaults to "b".
    metadata_key (str): The key to annotate. Default is "notes".
    metadata_value (str): The value to annotate. Default is an empty string.
    delete_note (bool): Whether to delete the note. Default is False to prevent accidental deletion of note.

    Returns:
    {
        "transaction": {
            "id": str,
            "created": str (UTC ISO 8601),
            "description": str,
            "amount": int,
            "fees": {},
            "currency": str,
            "merchant": str,
            "merchant_feedback_uri": str,
            "notes": str,
            "metadata": {
                "external_id": str,
                "ledger_committed_timestamp_earliest": str (UTC ISO 8601),
                "ledger_committed_timestamp_latest": str (UTC ISO 8601),
                "ledger_insertion_id": str,
                "notes": str,
                "pot_account_id": str,
                "pot_deposit_id": str,
                "pot_id": str,
                "trigger": str,
                "user_id": str,
            },
            "labels": [],
            "attachments": [],
            "international": str,
            "category": str,
            "categories": {
                "transfers": int,
            },
            "is_load": bool,
            "settled": str (UTC ISO 8601),
            "local_amount": int,
            "local_currency": str,
            "updated": str (UTC ISO 8601),
            "account_id": str,
            "user_id": str,
            "counterparty": {},
            "scheme": str,
            "dedupe_id": str,
            "originator": bool,
            "include_in_spending": bool,
            "can_be_excluded_from_breakdown": bool,
            "can_be_made_subscription": bool,
            "can_split_the_bill": bool,
            "can_add_to_tab": bool,
            "can_match_transactions_in_categorization": bool,
            "amount_is_pending": bool,
            "atm_fees_detailed": {},
            "parent_account_id": str,
        }
    }
    """

    headers = {
        "Authorization": f"Bearer {access_token[user]}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {} 

    data[f"metadata[{metadata_key}]"] = metadata_value

    response = requests.patch(f"{transactions_url}/{transaction_id}", headers=headers, data=data)

    if response.status_code != 200:
        raise Exception(f"Error: {response.json().get('error', 'Unknown error')}")

    response_data = response.json()

    return response_data
























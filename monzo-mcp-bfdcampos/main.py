from mcp.server.fastmcp import FastMCP
import requests
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

mcp = FastMCP("Monzo")

access_token = os.getenv("MONZO_ACCESS_TOKEN")
user_id = os.getenv("MONZO_USER_ID")

# Get all account IDs from environment variables
uk_prepaid_personal_account_id = os.getenv("MONZO_UK_PREPAID_PERSONAL_ACCOUNT_ID")
uk_retail_personal_account_id = os.getenv("MONZO_UK_RETAIL_PERSONAL_ACCOUNT_ID")
uk_monzo_flex_personal_account_id = os.getenv("MONZO_UK_MONZO_FLEX_PERSONAL_ACCOUNT_ID")
uk_rewards_personal_account_id = os.getenv("MONZO_UK_REWARDS_PERSONAL_ACCOUNT_ID")
uk_retail_joint_joint_account_id = os.getenv("MONZO_UK_RETAIL_JOINT_JOINT_ACCOUNT_ID")

# Create a dictionary of account types for easier reference
account_types = {
    "default": uk_retail_personal_account_id,
    "personal": uk_retail_personal_account_id,
    "prepaid": uk_prepaid_personal_account_id,
    "flex": uk_monzo_flex_personal_account_id,
    "rewards": uk_rewards_personal_account_id,
    "joint": uk_retail_joint_joint_account_id
}

url = "https://api.monzo.com/"
balance_url = f"{url}balance"
accounts_url = f"{url}accounts"
pots_url = f"{url}pots"
transactions_url = f"{url}transactions"

@mcp.tool("balance")
def get_balance(account_type: str = "personal") -> dict:
    """
    Returns the information about an account including the balance in the lower denomination 
    of the specified Monzo account's currency. I.e. GBP, the balance is in pence. E.g. 9155 is £91.55.
    
    Parameters:
    account_type (str): Type of account to check balance for. 
                       Options:
                            - "default" (default)
                            - "personal"
                            - "prepaid"
                            - "flex"
                            - "rewards"
                            - "joint"
    """
    account_type = account_type.lower()
    
    selected_account_id = account_types.get(account_type)
    
    if not selected_account_id:
        selected_account_id = account_types["personal"]
        
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    params = {
        "account_id": selected_account_id,
    }

    response = requests.get(balance_url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(f"Error: {response_data.get('error', 'Unknown error')}")

    response_data = response.json()

    return response_data

@mcp.tool("pots")
def get_pots_information(account_type: str = "personal") -> dict:
    """
    Returns the pots information of the specified Monzo account including the balance
    in the lower denomination of the specified Monzo account's currency.
    I.e. GBP, the balance is in pence. E.g. 9155 is £91.55.
    
    Parameters:
    account_type (str): Type of account to check pots for. 
                       Options:
                            - "default" (default)
                            - "personal"
                            - "prepaid"
                            - "flex"
                            - "rewards"
                            - "joint"
    """
    account_type = account_type.lower()
    
    selected_account_id = account_types.get(account_type)
    
    if not selected_account_id:
        selected_account_id = account_types["personal"]
        
    headers = {
        "Authorization": f"Bearer {access_token}",
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
        triggered_by: str = "mcp"
) -> dict:

    """
    Deposit money into a pot.
    
    Parameters:
    pot_id (str): The ID of the pot to deposit money into.
    amount (int): The amount to deposit in the lower denomination of the specified Monzo account's currency.
                  I.e. GBP, the amount is in pence. E.g. 9155 is £91.55.
    account_type (str): Type of account to deposit into. 
                        Options:
                            - "default" (default)
                            - "personal"
                            - "prepaid"
                            - "flex"
                            - "rewards"
                            - "joint"
    triggered_by (str): The source of the deposit. Default is "mcp".
    
    Returns:
    dict: The response from the Monzo API.
    """
    url = f"{pots_url}/{pot_id}/deposit"

    dedupe_id = f"{triggered_by}_{str(uuid.uuid4())}"
        
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    
    data = {
        "source_account_id": account_types.get(account_type, account_types["personal"]),
        "amount": amount,
        "dedupe_id": dedupe_id,
    }

    response = requests.put(url, headers=headers, data=data)
    
    if response.status_code != 200:
        raise Exception(f"Error: {response.json().get('error', 'Unknown error')}")
    
    return response.json()

@mcp.tool("pot_withdraw")
def pot_withdraw(
        pot_id: str,
        amount: int,
        account_type: str = "personal",
        triggered_by: str = "mcp"
) -> dict:
    """
    Withdraw money from a pot.
    
    Parameters:
    pot_id (str): The ID of the pot to withdraw money from.
    amount (int): The amount to withdraw in the lower denomination of the specified Monzo account's currency.
                  I.e. GBP, the amount is in pence. E.g. 9155 is £91.55.
    account_type (str): Type of account to withdraw from. 
                        Options:
                            - "default" (default)
                            - "personal"
                            - "prepaid"
                            - "flex"
                            - "rewards"
                            - "joint"
    triggered_by (str): The source of the withdrawal. Default is "mcp".
    
    Returns:
    dict: The response from the Monzo API.
    """
    url = f"{pots_url}/{pot_id}/withdraw"

    dedupe_id = f"{triggered_by}_{str(uuid.uuid4())}"
        
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    
    data = {
        "destination_account_id": account_types.get(account_type, account_types["personal"]),
        "amount": amount,
        "dedupe_id": dedupe_id,
    }

    response = requests.put(url, headers=headers, data=data)
    
    if response.status_code != 200:
        raise Exception(f"Error: {response.json().get('error', 'Unknown error')}")
    
    return response.json()

@mcp.tool("list_transactions")
def list_transactions(
        account_type: str = "personal",
        since: str = None,
        before: str = None,
        limit: int = 1000
    ) -> dict:
    """
    Returns a list of transactions for the specified Monzo account.
    
    Parameters:
    account_type (str): Type of account to list transactions for. 
                        Options:
                            - "default" (default)
                            - "personal"
                            - "prepaid"
                            - "flex"
                            - "rewards"
                            - "joint"
    since (str): The start date for the transactions in ISO 8601 format. Default is None.
    before (str): The end date for the transactions in ISO 8601 format. Default is None.
    limit (int): The maximum number of transactions to return. Default is 1000.
    """

    account_type = account_type.lower()

    selected_account_id = account_types.get(account_type)

    headers = {
        "Authorization": f"Bearer {access_token}",
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
























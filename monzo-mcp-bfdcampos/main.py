from mcp.server.fastmcp import FastMCP
import requests
from dotenv import load_dotenv
import os

load_dotenv()

mcp = FastMCP("Monzo")

access_token = os.getenv("MONZO_ACCESS_TOKEN")
user_id = os.getenv("MONZO_USER_ID")
account_id = os.getenv("MONZO_ACCOUNT_ID")

url = "https://api.monzo.com/"
balance_url = f"{url}balance"

@mcp.tool("balance")
def get_balance():
    """
    Returns the balance of the given Monzo account and currency
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    params = {
        "account_id": account_id,
    }

    response = requests.get(balance_url, headers=headers, params=params)
    response_data = response.json()

    if response.status_code != 200:
        raise Exception(f"Error: {response_data.get('error', 'Unknown error')}")

    currency = response_data.get("currency", "GBP")
    balance = response_data.get("balance", 0) / 100
    
    return {
        "balance": balance,
        "currency": currency,
    }

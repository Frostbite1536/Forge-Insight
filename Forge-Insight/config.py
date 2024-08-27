import os
from typing import Dict, Any, List

# API Configuration
SUBGRAPH_URLS: Dict[str, str] = {
    "Forge": "https://subgraph.evmos.org/subgraphs/name/forge-subgraph",
    "Custom": ""  # Placeholder for user-defined URL
}

API_TIMEOUT = 30  # seconds

# Google Sheets Configuration
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
TOKEN_FILE = 'token.json'
CLIENT_SECRET_FILE = 'client_secret.json'

# Local Storage
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
CACHE_DIR = os.path.join(DATA_DIR, 'cache')
LOG_DIR = os.path.join(DATA_DIR, 'logs')

# Paths for user dictionaries and favorites storage
USER_DATA_DIR = os.path.join(DATA_DIR, 'user_data')
USER_DICTIONARIES_DIR = os.path.join(USER_DATA_DIR, 'dictionaries')
FAVORITES_FILE = os.path.join(USER_DATA_DIR, 'favorites.json')
EVMOS_DICTIONARY_PATH = os.path.join(os.path.dirname(__file__), 'evmos_dictionary.json')

# Logging Configuration
LOG_FILE = os.path.join(LOG_DIR, 'forge_data_app.log')
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# UI Configuration
WINDOW_TITLE = "Forge Insight"
WINDOW_SIZE = "900x800"
THEME = "default"

# Query Configuration
DEFAULT_QUERY_LIMIT = 100
MAX_QUERY_LIMIT = 1000

# Schema Definition
SCHEMA: Dict[str, Dict[str, Any]] = {
    "Factory": {
        "description": "Overall statistics for the entire DEX",
        "fields": {
            "id": "Factory address",
            "poolCount": "Total number of pools",
            "txCount": "Total number of transactions",
            "totalVolumeUSD": "Total volume in USD",
            "totalFeesUSD": "Total fees collected in USD",
            "totalValueLockedUSD": "Total value locked in USD"
        }
    },
    "Token": {
        "description": "Information about individual tokens",
        "fields": {
            "id": "Token address",
            "symbol": "Token symbol",
            "name": "Token name",
            "decimals": "Token decimals",
            "totalSupply": "Total supply of the token",
            "volume": "Trading volume in token units",
            "volumeUSD": "Trading volume in USD",
            "txCount": "Number of transactions involving this token"
        }
    },
    "Pool": {
        "description": "Information about liquidity pools",
        "fields": {
            "id": "Pool address",
            "token0": "Address of the first token in the pair",
            "token1": "Address of the second token in the pair",
            "feeTier": "Fee tier of the pool",
            "liquidity": "Current liquidity in the pool",
            "sqrtPrice": "Square root of the current price",
            "token0Price": "Price of token0 in terms of token1",
            "token1Price": "Price of token1 in terms of token0",
            "volumeUSD": "Total volume in USD",
            "txCount": "Total number of transactions"
        }
    },
    "Swap": {
        "description": "Individual swap transactions",
        "fields": {
            "id": "Unique identifier for the swap",
            "timestamp": "Timestamp of the swap",
            "pool": "Address of the pool where the swap occurred",
            "token0": "Address of the first token in the pair",
            "token1": "Address of the second token in the pair",
            "amount0": "Amount of token0 swapped",
            "amount1": "Amount of token1 swapped",
            "amountUSD": "USD value of the swap"
        }
    }
}

# Error messages
ERROR_MESSAGES = {
    'api_error': "An error occurred while querying the subgraph: {}",
    'auth_error': "Authentication failed: {}",
    'export_error': "Failed to export data: {}",
    'invalid_query': "Invalid query configuration: {}",
    'scheduling_error': "Error in scheduling query: {}",
    'invalid_subgraph_url': "Invalid subgraph URL: {}"
}

# Create necessary directories
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(USER_DATA_DIR, exist_ok=True)
os.makedirs(USER_DICTIONARIES_DIR, exist_ok=True)

def get_subgraph_urls() -> List[str]:
    return list(SUBGRAPH_URLS.keys())

def set_custom_subgraph_url(url: str) -> None:
    SUBGRAPH_URLS["Custom"] = url

def get_active_subgraph_url(selected: str) -> str:
    return SUBGRAPH_URLS.get(selected, "")
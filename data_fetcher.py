"""
OpenClaw Dashboard - Data Fetching Module
Fetches blockchain data from GeckoTerminal and Basescan APIs
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

# Token configuration for OpenClaw Infrastructure ecosystem
TOKENS = {
    "CLANKER": {
        "address": "0x1bc0c42215582d5a085795f4badbac3ff36d1bcb",
        "name": "Clanker",
        "project": "Clanker World",
        "category": "Infrastructure",
        "description": "Token launch infrastructure for AI agents",
        "summary": "AI-powered token deployment platform on Base. Users create ERC-20 tokens instantly by tagging @clanker on Farcaster - no coding required. Automatically handles smart contract deployment, creates Uniswap liquidity pools, and locks liquidity. Acquired by Farcaster in early 2025.",
        "founders": "Jack Dishman (Farcaster engineer) & @proxystudio.eth",
        "launched": "November 2024",
        "key_stats": "355K+ token launches, $50M+ in fees generated",
        "backers": "Farcaster (acquired)"
    },
    "BNKR": {
        "address": "0x22af33fe49fd1fa80c7149773dde5890d3c76f3b",
        "name": "Bankrbot",
        "project": "Bankrbot",
        "category": "Infrastructure",
        "description": "Wallet and DeFi infrastructure for agents",
        "summary": "AI-powered crypto trading assistant enabling buy/sell/swap via social media commands. Creates secure embedded wallets via Privy - no seed phrases needed. Supports Base, Ethereum, Polygon, Solana with advanced order types (limit, stop loss, TWAP, DCA).",
        "founders": "Deployer (Ham/TN100X community)",
        "launched": "February 2025",
        "key_stats": "First token launched by an AI agent on Base",
        "backers": "Coinbase Ventures (Base Ecosystem Fund)"
    },
    "MOLT": {
        "address": "0xb695559b26bb2c9703ef1935c37aeae9526bab07",
        "name": "Moltbook",
        "project": "Moltbook",
        "category": "Forums/Social",
        "description": "Reddit-like platform for AI agents",
        "summary": "Social networking platform exclusively for AI agents - 'the front page of the agent internet'. Only verified AI agents can post; humans observe. Features threaded conversations in topic-specific 'submolts'. Agents interact via APIs and downloadable skills.",
        "founders": "Matt Schlicht",
        "launched": "January 2026",
        "key_stats": "157K+ active agents, 1M+ human visitors in first week",
        "backers": "Mentioned by Elon Musk, followed by a16z co-founders"
    }
}

# Clanker deployer contracts for tracking ecosystem growth
DEPLOYER_CONTRACTS = {
    "v3.1": "0xd9acd656a5f1b519c9e76a2a6092265a74186e58",
    "v4.1": "0xe85a59c628f7d27878aceb4bf3b35733630083a9"
}

# Bankrbot main interaction address
BANKRBOT_MAIN = "0x7c3d3c9ea0f11b162a4261a849033030b4cd3064"

# API endpoints
GECKOTERMINAL_BASE = "https://api.geckoterminal.com/api/v2"
BASESCAN_API = "https://api.basescan.org/api"


class DataFetcher:
    """Fetches and processes blockchain data for the dashboard"""

    def __init__(self, basescan_api_key: Optional[str] = None):
        self.basescan_api_key = basescan_api_key or ""
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "OpenClaw-Dashboard/1.0"
        })

    def get_token_info(self, token_address: str) -> Dict:
        """Fetch token info from GeckoTerminal"""
        url = f"{GECKOTERMINAL_BASE}/networks/base/tokens/{token_address}"
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                attrs = data.get("data", {}).get("attributes", {})
                return {
                    "name": attrs.get("name", "Unknown"),
                    "symbol": attrs.get("symbol", "???"),
                    "price_usd": float(attrs.get("price_usd", 0) or 0),
                    "market_cap_usd": float(attrs.get("market_cap_usd", 0) or 0),
                    "fdv_usd": float(attrs.get("fdv_usd", 0) or 0),
                    "total_supply": attrs.get("total_supply", "0"),
                    "volume_24h": float(attrs.get("volume_usd", {}).get("h24", 0) or 0),
                    "price_change_24h": float(attrs.get("price_change_percentage", {}).get("h24", 0) or 0),
                    "address": token_address,
                    "success": True
                }
            return {"success": False, "error": f"Status {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_token_pools(self, token_address: str, limit: int = 5) -> List[Dict]:
        """Fetch liquidity pools for a token"""
        url = f"{GECKOTERMINAL_BASE}/networks/base/tokens/{token_address}/pools"
        try:
            response = self.session.get(url, params={"page": 1}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                pools = []
                for pool in data.get("data", [])[:limit]:
                    attrs = pool.get("attributes", {})
                    pools.append({
                        "name": attrs.get("name", "Unknown Pool"),
                        "address": attrs.get("address", ""),
                        "reserve_usd": float(attrs.get("reserve_in_usd", 0) or 0),
                        "volume_24h": float(attrs.get("volume_usd", {}).get("h24", 0) or 0),
                        "price_change_24h": float(attrs.get("price_change_percentage", {}).get("h24", 0) or 0)
                    })
                return pools
            return []
        except Exception as e:
            return []

    def get_token_ohlcv(self, pool_address: str, timeframe: str = "day", limit: int = 30) -> pd.DataFrame:
        """Fetch OHLCV data for price charts"""
        url = f"{GECKOTERMINAL_BASE}/networks/base/pools/{pool_address}/ohlcv/{timeframe}"
        try:
            response = self.session.get(url, params={"limit": limit}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                ohlcv = data.get("data", {}).get("attributes", {}).get("ohlcv_list", [])
                if ohlcv:
                    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
                    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
                    df = df.sort_values("timestamp")
                    return df
            return pd.DataFrame()
        except Exception as e:
            return pd.DataFrame()

    def get_holder_count(self, token_address: str) -> int:
        """Fetch holder count from Basescan (requires API key for accurate data)"""
        if not self.basescan_api_key:
            # Return placeholder - in production, use Basescan API
            return 0

        url = BASESCAN_API
        params = {
            "module": "token",
            "action": "tokenholdercount",
            "contractaddress": token_address,
            "apikey": self.basescan_api_key
        }
        try:
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "1":
                    return int(data.get("result", 0))
            return 0
        except:
            return 0

    def get_deployer_transactions(self, deployer_address: str, limit: int = 100) -> List[Dict]:
        """Fetch recent transactions from a deployer contract"""
        url = BASESCAN_API
        params = {
            "module": "account",
            "action": "txlist",
            "address": deployer_address,
            "startblock": 0,
            "endblock": 99999999,
            "page": 1,
            "offset": limit,
            "sort": "desc",
            "apikey": self.basescan_api_key or ""
        }
        try:
            response = self.session.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "1":
                    txs = []
                    for tx in data.get("result", []):
                        txs.append({
                            "hash": tx.get("hash", ""),
                            "timestamp": datetime.fromtimestamp(int(tx.get("timeStamp", 0))),
                            "from": tx.get("from", ""),
                            "to": tx.get("to", ""),
                            "value": int(tx.get("value", 0)) / 1e18,
                            "gas_used": int(tx.get("gasUsed", 0)),
                            "is_error": tx.get("isError", "0") == "1",
                            "method": tx.get("functionName", "").split("(")[0] if tx.get("functionName") else "transfer"
                        })
                    return txs
            return []
        except Exception as e:
            return []

    def get_contract_creation_count(self, deployer_address: str) -> Dict:
        """Estimate token deployments by counting contract creations"""
        url = BASESCAN_API
        params = {
            "module": "account",
            "action": "txlist",
            "address": deployer_address,
            "startblock": 0,
            "endblock": 99999999,
            "page": 1,
            "offset": 1000,
            "sort": "desc",
            "apikey": self.basescan_api_key or ""
        }
        try:
            response = self.session.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "1":
                    txs = data.get("result", [])
                    # Count transactions that created contracts (to address is empty or specific patterns)
                    creations = [tx for tx in txs if tx.get("to") == "" or tx.get("contractAddress")]

                    # Group by day
                    daily_counts = {}
                    for tx in txs:
                        ts = datetime.fromtimestamp(int(tx.get("timeStamp", 0)))
                        day = ts.strftime("%Y-%m-%d")
                        daily_counts[day] = daily_counts.get(day, 0) + 1

                    return {
                        "total_txs": len(txs),
                        "contract_creations": len(creations),
                        "daily_activity": daily_counts,
                        "success": True
                    }
            return {"success": False, "total_txs": 0}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_all_token_metrics(self) -> pd.DataFrame:
        """Fetch metrics for all tracked tokens"""
        records = []
        for symbol, config in TOKENS.items():
            info = self.get_token_info(config["address"])
            if info.get("success"):
                holders = self.get_holder_count(config["address"])
                pools = self.get_token_pools(config["address"], limit=1)
                top_pool_liquidity = pools[0]["reserve_usd"] if pools else 0

                records.append({
                    "symbol": symbol,
                    "name": config["name"],
                    "project": config["project"],
                    "category": config["category"],
                    "description": config["description"],
                    "address": config["address"],
                    "price_usd": info["price_usd"],
                    "market_cap_usd": info["market_cap_usd"],
                    "fdv_usd": info["fdv_usd"],
                    "volume_24h": info["volume_24h"],
                    "price_change_24h": info["price_change_24h"],
                    "holders": holders if holders > 0 else config.get("holders_estimate", 0),
                    "top_pool_liquidity": top_pool_liquidity
                })
            time.sleep(0.5)  # Rate limiting

        return pd.DataFrame(records)

    def get_ecosystem_activity(self) -> Dict:
        """Get aggregate ecosystem activity from all deployers"""
        total_activity = {
            "deployers": {},
            "total_txs_24h": 0,
            "total_contracts_created": 0
        }

        for version, address in DEPLOYER_CONTRACTS.items():
            data = self.get_contract_creation_count(address)
            if data.get("success"):
                total_activity["deployers"][version] = {
                    "address": address,
                    "total_txs": data["total_txs"],
                    "contract_creations": data["contract_creations"],
                    "daily_activity": data.get("daily_activity", {})
                }
                total_activity["total_contracts_created"] += data["contract_creations"]
            time.sleep(0.5)

        return total_activity


# Sample/fallback data for when APIs are unavailable
SAMPLE_DATA = {
    "CLANKER": {
        "price_usd": 42.90,
        "market_cap_usd": 42900000,
        "fdv_usd": 42900000,
        "volume_24h": 1250000,
        "price_change_24h": 33.2,
        "holders": 505908,
        "total_supply": 1000000
    },
    "BNKR": {
        "price_usd": 0.0005,
        "market_cap_usd": 54900000,
        "fdv_usd": 50000000,
        "volume_24h": 890000,
        "price_change_24h": 23.0,
        "holders": 220533,
        "total_supply": 100000000000
    },
    "MOLT": {
        "price_usd": 0.0006,
        "market_cap_usd": 58500000,
        "fdv_usd": 60000000,
        "volume_24h": 456000,
        "price_change_24h": -24.89,
        "holders": 13398,
        "total_supply": 100000000000
    }
}


def get_sample_metrics() -> pd.DataFrame:
    """Return sample data for demo/fallback purposes"""
    records = []
    for symbol, config in TOKENS.items():
        sample = SAMPLE_DATA.get(symbol, {})
        records.append({
            "symbol": symbol,
            "name": config["name"],
            "project": config["project"],
            "category": config["category"],
            "description": config["description"],
            "address": config["address"],
            "price_usd": sample.get("price_usd", 0),
            "market_cap_usd": sample.get("market_cap_usd", 0),
            "fdv_usd": sample.get("fdv_usd", 0),
            "volume_24h": sample.get("volume_24h", 0),
            "price_change_24h": sample.get("price_change_24h", 0),
            "holders": sample.get("holders", 0),
            "top_pool_liquidity": sample.get("volume_24h", 0) * 0.1
        })
    return pd.DataFrame(records)


def generate_sample_price_history(symbol: str, days: int = 30) -> pd.DataFrame:
    """Generate sample price history for demo purposes"""
    import random

    base_prices = {"CLANKER": 42.90, "BNKR": 0.0005, "MOLT": 0.0006}
    base_price = base_prices.get(symbol, 1.0)

    dates = pd.date_range(end=datetime.now(), periods=days, freq="D")
    prices = []
    current_price = base_price * 0.7  # Start lower

    for _ in range(days):
        change = random.uniform(-0.08, 0.12)  # Volatile memecoin behavior
        current_price *= (1 + change)
        current_price = max(current_price, base_price * 0.1)  # Floor
        prices.append(current_price)

    return pd.DataFrame({
        "timestamp": dates,
        "close": prices,
        "volume": [random.uniform(100000, 2000000) for _ in range(days)]
    })


def generate_sample_deployer_activity(days: int = 14) -> pd.DataFrame:
    """Generate sample deployer activity for demo purposes"""
    import random

    dates = pd.date_range(end=datetime.now(), periods=days, freq="D")

    return pd.DataFrame({
        "date": dates,
        "v3.1_deployments": [random.randint(50, 200) for _ in range(days)],
        "v4.1_deployments": [random.randint(100, 500) for _ in range(days)],
        "total_txs": [random.randint(500, 2000) for _ in range(days)]
    })

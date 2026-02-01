# OpenClaw AI Agent Ecosystem Dashboard

An interactive dashboard for tracking the OpenClaw AI agent ecosystem on Base blockchain. Built for both **investors** and **ecosystem builders**.

## Features

### 📊 Overview
- Total market cap, volume, and holder counts
- Token metric cards for CLANKER, BNKR, MOLT
- Risk indicators per token
- Price history comparison charts

### 💰 Investor View
- Token performance matrix
- Market cap distribution
- Volume vs Market Cap scatter plot
- Individual token deep dives with candlestick charts

### 🔧 Builder View
- Clanker deployer activity tracking (v3.1 and v4.1 contracts)
- Daily token deployment metrics
- Cumulative ecosystem growth charts
- Dune Analytics query templates
- Builder resource links

### ⚠️ Risk Analysis
- Risk assessment per token
- Holder concentration analysis
- Liquidity risk evaluation
- LpLocker verification tools

## Tracked Tokens

| Token | Address | Category |
|-------|---------|----------|
| CLANKER | `0x1bc0c42215582d5a085795f4badbac3ff36d1bcb` | Infrastructure |
| BNKR | `0x22af33fe49fd1fa80c7149773dde5890d3c76f3b` | Infrastructure |
| MOLT | `0xb695559b26bb2c9703ef1935c37aeae9526bab07` | Forums/Social |

## Deployer Contracts

| Version | Address |
|---------|---------|
| v3.1 | `0xd9acd656a5f1b519c9e76a2a6092265a74186e58` |
| v4.1 | `0xe85a59c628f7d27878aceb4bf3b35733630083a9` |

## Installation

```bash
# Clone or download the dashboard files
cd openclaw-dashboard

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip3 install -r requirements.txt

# Run the dashboard
streamlit run app.py
```

**Alternative: Using uv (faster)**
```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
streamlit run app.py
```

## Configuration

### Environment Variables (Optional)

For live data fetching, set up API keys:

```bash
export BASESCAN_API_KEY="your_basescan_api_key"
```

Get a free Basescan API key at: https://basescan.org/apis

### Live vs Sample Data

Toggle "Use Live Data" in the sidebar to switch between:
- **Sample Data**: Pre-populated metrics for demo/offline use
- **Live Data**: Real-time data from GeckoTerminal and Basescan APIs

## Data Sources

- **GeckoTerminal API**: Token prices, market caps, volumes (free, no key required)
- **Basescan API**: Holder counts, transaction history, deployer activity
- **Sample Data**: Fallback data based on research snapshot (~Jan 31, 2026)

## Architecture

```
openclaw-dashboard/
├── app.py              # Main Streamlit application
├── data_fetcher.py     # API clients and data processing
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Extending the Dashboard

### Add New Tokens

Edit `data_fetcher.py` and add to the `TOKENS` dictionary:

```python
TOKENS = {
    "NEW_TOKEN": {
        "address": "0x...",
        "name": "Token Name",
        "project": "Project Name",
        "category": "Category",
        "description": "Description"
    },
    # ...existing tokens
}
```

### Add New Deployers

Add to `DEPLOYER_CONTRACTS` in `data_fetcher.py`:

```python
DEPLOYER_CONTRACTS = {
    "v5.0": "0x...",
    # ...existing deployers
}
```

## Dune Analytics Integration

Use these queries to create your own Dune dashboards:

### Daily Deployments
```sql
SELECT
    date_trunc('day', block_time) AS day,
    COUNT(*) AS deployments
FROM base.transactions
WHERE "from" IN (
    '0xd9acd656a5f1b519c9e76a2a6092265a74186e58',
    '0xe85a59c628f7d27878aceb4bf3b35733630083a9'
)
GROUP BY day
ORDER BY day DESC
```

### Token Transfers
```sql
SELECT
    date_trunc('day', block_time) AS day,
    COUNT(*) AS transfers,
    SUM(value) AS volume
FROM erc20_base.evt_Transfer
WHERE contract_address = LOWER('0x1bc0c42215582d5a085795f4badbac3ff36d1bcb')
GROUP BY day
ORDER BY day DESC
```

## Risk Disclaimer

This dashboard is for informational purposes only. The OpenClaw ecosystem consists primarily of memecoins and experimental AI agent infrastructure. Prices are highly volatile and investments carry significant risk. Always DYOR (Do Your Own Research).

## License

MIT License - Feel free to modify and extend.

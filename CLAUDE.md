# CLAUDE.md - OpenClaw Dashboard Project

## Project Overview
This is an interactive Streamlit dashboard for tracking the OpenClaw AI agent ecosystem on Base blockchain. It serves both **investors** (token metrics, risk analysis) and **ecosystem builders** (deployer activity, growth metrics).

## Key Commands
```bash
# Setup (first time only)
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

# Or use uv (faster alternative)
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Run the dashboard
source venv/bin/activate  # or: source .venv/bin/activate (if using uv)
streamlit run app.py

# Test data fetcher
python -c "from data_fetcher import get_sample_metrics; print(get_sample_metrics())"
```

## Project Structure
```
openclaw-dashboard/
├── app.py              # Main Streamlit UI - 4 views (Overview, Investor, Builder, Risk)
├── data_fetcher.py     # API clients + data processing + sample data fallbacks
├── requirements.txt    # Dependencies: streamlit, pandas, plotly, requests, web3
├── README.md           # User documentation
└── CLAUDE.md           # This file - AI assistant instructions
```

## Architecture Decisions
- **Streamlit** chosen for rapid prototyping and interactive widgets
- **GeckoTerminal API** (free, no key) for token prices/volumes
- **Basescan API** (optional key) for holder counts and transaction history
- **Sample data fallback** ensures dashboard works offline/demo mode
- **Plotly** for interactive charts with dark theme

## Tracked Tokens (Infrastructure Focus)
| Symbol | Address | Category |
|--------|---------|----------|
| CLANKER | `0x1bc0c42215582d5a085795f4badbac3ff36d1bcb` | Token launch infra |
| BNKR | `0x22af33fe49fd1fa80c7149773dde5890d3c76f3b` | Wallet/DeFi infra |
| MOLT | `0xb695559b26bb2c9703ef1935c37aeae9526bab07` | Forums/Social |

## Deployer Contracts (Ecosystem Growth Tracking)
| Version | Address |
|---------|---------|
| v3.1 | `0xd9acd656a5f1b519c9e76a2a6092265a74186e58` |
| v4.1 | `0xe85a59c628f7d27878aceb4bf3b35733630083a9` |

## Key Contract Addresses
- **Bankrbot Main**: `0x7c3d3c9ea0f11b162a4261a849033030b4cd3064`
- **LpLocker**: `0x33e2Eda238edcF470309b8c6D228986A1204c8f9`

## Coding Conventions
- Use type hints for function parameters
- Include docstrings for all public functions
- Keep API calls in `data_fetcher.py`, UI logic in `app.py`
- Always provide sample data fallback for offline usage
- Use `format_number()` and `format_price()` helpers for display

## How to Extend

### Add a New Token
1. Edit `TOKENS` dict in `data_fetcher.py`:
```python
TOKENS["NEW"] = {
    "address": "0x...",
    "name": "Token Name",
    "project": "Project Name",
    "category": "Category",
    "description": "Description"
}
```
2. Add sample data in `SAMPLE_DATA` dict
3. Token will auto-appear in all dashboard views

### Add a New Deployer
1. Add to `DEPLOYER_CONTRACTS` in `data_fetcher.py`
2. Update `generate_sample_deployer_activity()` to include new column
3. Update Builder view charts in `app.py`

### Add a New Dashboard View
1. Add option to `view_mode` radio in sidebar
2. Create new `elif view_mode == "..."` block in `main()`
3. Follow existing pattern: metrics row → charts → details

## Data Sources & APIs
- **GeckoTerminal**: `https://api.geckoterminal.com/api/v2` (no auth)
- **Basescan**: `https://api.basescan.org/api` (optional API key via `BASESCAN_API_KEY` env var)
- **Rate limiting**: 0.5s delay between API calls in batch operations

## Environment Variables
```bash
BASESCAN_API_KEY=your_key_here  # Optional, for holder counts
```

## Testing
- Toggle "Use Live Data" OFF in sidebar for sample data (faster, offline)
- Toggle ON to test real API integration
- Check browser console for any Streamlit errors

## Known Limitations
- Holder counts require Basescan API key for accuracy
- OHLCV data requires finding the main liquidity pool address first
- Sample price history is randomly generated (not historical)

## Related Resources
- [Basescan](https://basescan.org)
- [GeckoTerminal Base](https://www.geckoterminal.com/base)
- [Dune Base Dashboard](https://dune.com/tk-research/base)
- [Streamlit Docs](https://docs.streamlit.io)

"""
OpenClaw AI Agent Ecosystem Dashboard
Track infrastructure tokens and ecosystem growth on Base

Built for both Investor and Ecosystem Builder stakeholders
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os

# Import our data fetching module
from data_fetcher import (
    DataFetcher,
    TOKENS,
    DEPLOYER_CONTRACTS,
    get_sample_metrics,
    generate_sample_price_history,
    generate_sample_deployer_activity,
    SAMPLE_DATA
)

# Page configuration
st.set_page_config(
    page_title="OpenClaw Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling - Cyberpunk Terminal Aesthetic
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&family=Inter:wght@300;400;600&display=swap');

    /* Global theme overrides */
    .stApp {
        background: #0a0e27;
        background-image:
            repeating-linear-gradient(0deg, rgba(0, 255, 136, 0.03) 0px, transparent 1px, transparent 2px, rgba(0, 255, 136, 0.03) 3px),
            radial-gradient(circle at 20% 50%, rgba(0, 255, 136, 0.05) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(255, 71, 87, 0.05) 0%, transparent 50%);
    }

    /* Fix Streamlit header/toolbar background */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    .stAppHeader, .stToolbar {
        background: transparent !important;
    }

    /* Hide the top decoration bar if present */
    .stDeployButton {
        color: #8892b0 !important;
    }

    /* Main block container */
    .block-container {
        padding-top: 2rem !important;
    }

    /* Main header with glitch effect */
    .main-header {
        font-family: 'JetBrains Mono', monospace;
        font-size: 3.5rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #00ff88;
        text-transform: uppercase;
        position: relative;
        display: inline-block;
        margin-bottom: 0.5rem;
        text-shadow:
            0 0 10px rgba(0, 255, 136, 0.5),
            0 0 20px rgba(0, 255, 136, 0.3),
            0 0 30px rgba(0, 255, 136, 0.2),
            2px 2px 0px rgba(255, 71, 87, 0.3);
    }

    .main-header::before {
        content: 'OPENCLAW';
        position: absolute;
        left: 2px;
        top: 0;
        color: rgba(255, 71, 87, 0.4);
        z-index: -1;
    }

    .subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        font-weight: 300;
        color: #8892b0;
        letter-spacing: 0.05em;
        margin-top: 0;
    }

    /* Metric cards with border animations */
    .stMetric {
        background: linear-gradient(135deg, rgba(10, 14, 39, 0.9) 0%, rgba(20, 25, 50, 0.9) 100%);
        border: 2px solid transparent;
        border-radius: 4px;
        padding: 1.5rem;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(10px);
    }

    .stMetric::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        border: 2px solid;
        border-image: linear-gradient(135deg, #00ff88, #00d9ff, #ff4757) 1;
        opacity: 0.3;
        pointer-events: none;
    }

    .stMetric:hover::before {
        opacity: 0.8;
        animation: borderPulse 1.5s infinite;
    }

    @keyframes borderPulse {
        0%, 100% { opacity: 0.8; }
        50% { opacity: 0.4; }
    }

    div[data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2rem;
        font-weight: 700;
        color: #00ff88;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
    }

    div[data-testid="stMetricLabel"] {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #8892b0;
        font-weight: 600;
    }

    div[data-testid="stMetricDelta"] {
        font-family: 'JetBrains Mono', monospace;
    }

    /* Positive/Negative indicators */
    .positive {
        color: #00ff88;
        text-shadow: 0 0 8px rgba(0, 255, 136, 0.5);
    }
    .negative {
        color: #ff4757;
        text-shadow: 0 0 8px rgba(255, 71, 87, 0.5);
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1224 0%, #0a0e27 100%);
        border-right: 1px solid rgba(0, 255, 136, 0.2);
    }

    section[data-testid="stSidebar"] .stRadio > label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        color: #00ff88;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Risk indicators with neon glow */
    .risk-indicator {
        padding: 8px 16px;
        border-radius: 2px;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        position: relative;
    }

    .risk-low {
        background-color: rgba(0, 255, 136, 0.2);
        color: #00ff88;
        border: 1px solid #00ff88;
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.3);
    }

    .risk-medium {
        background-color: rgba(255, 165, 2, 0.2);
        color: #ffa502;
        border: 1px solid #ffa502;
        box-shadow: 0 0 15px rgba(255, 165, 2, 0.3);
    }

    .risk-high {
        background-color: rgba(255, 71, 87, 0.2);
        color: #ff4757;
        border: 1px solid #ff4757;
        box-shadow: 0 0 15px rgba(255, 71, 87, 0.3);
    }

    /* Section headers */
    h1, h2, h3, h4 {
        font-family: 'JetBrains Mono', monospace !important;
        color: #ccd6f6 !important;
        font-weight: 700 !important;
    }

    h3 {
        font-size: 1.3rem !important;
        color: #00d9ff !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    h4 {
        font-size: 1.1rem !important;
        color: #00d9ff !important;
        letter-spacing: 0.03em;
    }

    /* Body text and paragraphs */
    p, li, span, div {
        color: #ccd6f6;
    }

    /* Markdown text styling */
    .stMarkdown p, .stMarkdown li {
        color: #a8b2d1 !important;
        font-family: 'Inter', sans-serif;
    }

    .stMarkdown strong {
        color: #ccd6f6 !important;
    }

    /* Code blocks with terminal styling */
    code {
        background: rgba(0, 0, 0, 0.5) !important;
        border: 1px solid rgba(0, 255, 136, 0.3) !important;
        border-radius: 2px !important;
        color: #00ff88 !important;
        font-family: 'JetBrains Mono', monospace !important;
        padding: 0.5rem 1rem !important;
        font-size: 0.85rem !important;
    }

    /* Dataframe styling */
    .stDataFrame {
        font-family: 'JetBrains Mono', monospace;
    }

    /* Horizontal rules */
    hr {
        border-color: rgba(0, 255, 136, 0.2) !important;
        margin: 2rem 0 !important;
    }

    /* Links */
    a {
        color: #00d9ff !important;
        text-decoration: none !important;
        font-weight: 600 !important;
        transition: all 0.3s ease;
    }

    a:hover {
        color: #00ff88 !important;
        text-shadow: 0 0 8px rgba(0, 255, 136, 0.5);
    }

    /* Buttons */
    .stButton > button {
        font-family: 'JetBrains Mono', monospace;
        background: linear-gradient(135deg, rgba(0, 217, 255, 0.1), rgba(0, 255, 136, 0.1));
        color: #00ff88;
        border: 1px solid #00ff88;
        border-radius: 2px;
        padding: 0.5rem 1.5rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background: rgba(0, 255, 136, 0.2);
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
        border-color: #00ff88;
    }

    /* Info/Warning boxes */
    .stAlert {
        font-family: 'Inter', sans-serif;
        border-radius: 2px;
        border-left: 4px solid;
    }

    /* Selectbox, multiselect */
    .stSelectbox, .stMultiSelect {
        font-family: 'Inter', sans-serif;
    }

    /* Captions */
    .stCaption {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #8892b0;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)

def apply_chart_theme(fig, title=None):
    """Apply cyberpunk theme to Plotly figure"""
    layout_updates = dict(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(10, 14, 39, 0.5)",
        font=dict(family="JetBrains Mono, monospace", color="#ccd6f6"),
        xaxis=dict(
            gridcolor="rgba(0, 255, 136, 0.1)",
            linecolor="rgba(0, 255, 136, 0.3)",
            tickfont=dict(color="#8892b0")
        ),
        yaxis=dict(
            gridcolor="rgba(0, 255, 136, 0.1)",
            linecolor="rgba(0, 255, 136, 0.3)",
            tickfont=dict(color="#8892b0")
        ),
        colorway=["#00ff88", "#00d9ff", "#ff4757", "#ffa502", "#b692f6", "#f093fb"]
    )
    # Set title - explicit empty string to clear any default
    if title:
        layout_updates["title"] = dict(text=title, font=dict(color="#00d9ff", size=18))
    else:
        layout_updates["title"] = dict(text="")

    fig.update_layout(**layout_updates)
    return fig


def format_number(num: float, decimals: int = 2) -> str:
    """Format large numbers with K, M, B suffixes"""
    if num >= 1_000_000_000:
        return f"${num/1_000_000_000:.{decimals}f}B"
    elif num >= 1_000_000:
        return f"${num/1_000_000:.{decimals}f}M"
    elif num >= 1_000:
        return f"${num/1_000:.{decimals}f}K"
    else:
        return f"${num:.{decimals}f}"


def format_price(price: float) -> str:
    """Format price with appropriate decimals"""
    if price >= 1:
        return f"${price:,.2f}"
    elif price >= 0.01:
        return f"${price:.4f}"
    else:
        return f"${price:.6f}"


def get_change_color(change: float) -> str:
    """Return color based on price change"""
    return "🟢" if change >= 0 else "🔴"


def calculate_risk_score(holders: int, liquidity: float, market_cap: float) -> tuple:
    """Calculate simple risk score based on holder concentration and liquidity"""
    # Higher holders and liquidity = lower risk
    holder_score = min(holders / 100000, 1) * 40  # Max 40 points
    liquidity_ratio = (liquidity / market_cap * 100) if market_cap > 0 else 0
    liquidity_score = min(liquidity_ratio / 5, 1) * 30  # Max 30 points for 5%+ liquidity
    mcap_score = min(market_cap / 50_000_000, 1) * 30  # Max 30 points

    total_score = holder_score + liquidity_score + mcap_score

    if total_score >= 70:
        return ("Low", "🟢", "#00ff88")
    elif total_score >= 40:
        return ("Medium", "🟡", "#ffa502")
    else:
        return ("High", "🔴", "#ff4757")


def get_price_history(fetcher: DataFetcher, symbol: str, address: str, use_live: bool, days: int = 30) -> pd.DataFrame:
    """Get price history - live data if available, otherwise sample data"""
    if use_live:
        try:
            # First get the main pool for this token
            pools = fetcher.get_token_pools(address, limit=1)
            if pools:
                pool_address = pools[0].get("id", "").split("_")[-1] if "_" in pools[0].get("id", "") else pools[0].get("attributes", {}).get("address", "")
                if pool_address:
                    df = fetcher.get_token_ohlcv(pool_address, timeframe="day", limit=days)
                    if not df.empty:
                        return df
        except Exception:
            pass
    # Fallback to sample data
    return generate_sample_price_history(symbol, days)


def get_deployer_activity(fetcher: DataFetcher, use_live: bool, days: int = 30) -> pd.DataFrame:
    """Get deployer activity - live data if available, otherwise sample data"""
    if use_live:
        try:
            activity_data = []
            dates = pd.date_range(end=datetime.now(), periods=days, freq="D")

            for version, addr in DEPLOYER_CONTRACTS.items():
                txs = fetcher.get_deployer_transactions(addr, limit=1000)
                if txs:
                    # Group transactions by day
                    for tx in txs:
                        tx_date = datetime.fromtimestamp(int(tx.get("timeStamp", 0))).date()
                        activity_data.append({"date": tx_date, "version": version})

            if activity_data:
                df = pd.DataFrame(activity_data)
                # Aggregate by date and version
                pivot = df.groupby(["date", "version"]).size().unstack(fill_value=0).reset_index()
                pivot.columns = ["date"] + [f"{v}_deployments" for v in pivot.columns[1:]]
                if "v3.1_deployments" not in pivot.columns:
                    pivot["v3.1_deployments"] = 0
                if "v4.1_deployments" not in pivot.columns:
                    pivot["v4.1_deployments"] = 0
                pivot["total_txs"] = pivot["v3.1_deployments"] + pivot["v4.1_deployments"]
                return pivot.tail(days)
        except Exception:
            pass
    # Fallback to sample data
    return generate_sample_deployer_activity(days)


def main():
    # Initialize data fetcher
    basescan_key = os.getenv("BASESCAN_API_KEY", "")
    fetcher = DataFetcher(basescan_api_key=basescan_key)

    # Sidebar configuration
    with st.sidebar:
        st.markdown("## 🤖 OpenClaw Dashboard")
        st.markdown("---")

        # View selector
        view_mode = st.radio(
            "Select View",
            ["📊 Overview", "💰 Investor", "🔧 Builder", "⚠️ Risk Analysis"],
            index=0
        )

        st.markdown("---")

        # Data source toggle
        use_live_data = st.toggle("Use Live Data", value=False, help="Fetch real-time data from APIs (requires internet)")

        if use_live_data:
            st.info("🔄 Fetching live data...")

        st.markdown("---")

        # Token filter
        st.markdown("### Token Selection")
        selected_tokens = st.multiselect(
            "Select tokens to display",
            options=list(TOKENS.keys()),
            default=list(TOKENS.keys())
        )

        st.markdown("---")
        st.markdown("### 📍 Tracked Addresses")
        st.markdown("**Deployer Contracts:**")
        for version, addr in DEPLOYER_CONTRACTS.items():
            st.code(f"{version}: {addr[:10]}...{addr[-6:]}", language=None)

        st.markdown("---")
        st.caption("Data sources: GeckoTerminal, Basescan")
        st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Main content
    st.markdown('<p class="main-header">OpenClaw</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">AI AGENT ECOSYSTEM // BASE NETWORK // REAL-TIME INTELLIGENCE</p>', unsafe_allow_html=True)

    # Fetch or use sample data
    if use_live_data:
        with st.spinner("Fetching live market data..."):
            df_tokens = fetcher.get_all_token_metrics()
            if df_tokens.empty:
                st.warning("Could not fetch live data. Using sample data.")
                df_tokens = get_sample_metrics()
    else:
        df_tokens = get_sample_metrics()

    # Filter by selected tokens
    df_tokens = df_tokens[df_tokens["symbol"].isin(selected_tokens)]

    # ========== OVERVIEW VIEW ==========
    if view_mode == "📊 Overview":
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)

        total_mcap = df_tokens["market_cap_usd"].sum()
        total_volume = df_tokens["volume_24h"].sum()
        total_holders = df_tokens["holders"].sum()
        avg_change = df_tokens["price_change_24h"].mean()

        with col1:
            st.metric(
                "Total Market Cap",
                format_number(total_mcap),
                delta=f"{avg_change:+.1f}% avg"
            )
        with col2:
            st.metric(
                "24h Volume",
                format_number(total_volume)
            )
        with col3:
            st.metric(
                "Total Holders",
                f"{total_holders:,}"
            )
        with col4:
            st.metric(
                "Tokens Tracked",
                len(df_tokens)
            )

        st.markdown("---")

        # About the Ecosystem - expandable info section
        with st.expander("ℹ️ **About the OpenClaw Ecosystem** - Click to learn more"):
            st.markdown("""
            The **OpenClaw ecosystem** represents the emerging AI agent economy on Base blockchain.
            These infrastructure tokens power autonomous AI agents that can launch tokens, trade crypto,
            and interact socially - all without human intervention.
            """)

            info_cols = st.columns(3)
            for idx, symbol in enumerate(["CLANKER", "BNKR", "MOLT"]):
                token_info = TOKENS.get(symbol, {})
                with info_cols[idx]:
                    st.markdown(f"**{symbol}** - {token_info.get('project', '')}")
                    st.markdown(f"_{token_info.get('summary', token_info.get('description', ''))}_")
                    st.markdown(f"""
                    - **Founders:** {token_info.get('founders', 'Unknown')}
                    - **Launched:** {token_info.get('launched', 'Unknown')}
                    - **Key Stats:** {token_info.get('key_stats', 'N/A')}
                    - **Backers:** {token_info.get('backers', 'N/A')}
                    """)

        st.markdown("---")

        # Token cards
        st.markdown("### 🪙 Infrastructure Token Metrics")

        cols = st.columns(len(df_tokens))
        for idx, (_, row) in enumerate(df_tokens.iterrows()):
            with cols[idx]:
                change_emoji = get_change_color(row["price_change_24h"])
                risk_label, risk_emoji, risk_color = calculate_risk_score(
                    row["holders"], row["top_pool_liquidity"], row["market_cap_usd"]
                )

                st.markdown(f"### {row['symbol']} {change_emoji}")
                st.caption(f"{row['project']} | {row['category']}")

                # Show token description
                token_info = TOKENS.get(row['symbol'], {})
                st.caption(f"_{token_info.get('description', '')}_")

                st.metric("Price", format_price(row["price_usd"]),
                          delta=f"{row['price_change_24h']:+.1f}%")

                st.markdown(f"""
                - **Market Cap:** {format_number(row['market_cap_usd'])}
                - **24h Volume:** {format_number(row['volume_24h'])}
                - **Holders:** {row['holders']:,}
                - **Risk:** {risk_emoji} {risk_label}
                """)

                st.code(row["address"][:20] + "...", language=None)

        # Price comparison chart
        st.markdown("---")
        st.markdown("### 📈 Price History Comparison")

        fig = make_subplots(
            rows=1, cols=len(df_tokens),
            subplot_titles=[row["symbol"] for _, row in df_tokens.iterrows()]
        )

        for idx, (_, row) in enumerate(df_tokens.iterrows()):
            price_df = get_price_history(fetcher, row["symbol"], row["address"], use_live_data, days=30)
            fig.add_trace(
                go.Scatter(
                    x=price_df["timestamp"],
                    y=price_df["close"],
                    mode="lines",
                    name=row["symbol"],
                    line=dict(width=2)
                ),
                row=1, col=idx + 1
            )

        fig.update_layout(height=300, showlegend=False)
        apply_chart_theme(fig)
        st.plotly_chart(fig, width="stretch")

    # ========== INVESTOR VIEW ==========
    elif view_mode == "💰 Investor":
        st.markdown("### 💰 Investor Dashboard")
        st.markdown("Focus on token performance, market dynamics, and investment metrics")

        # Performance table
        st.markdown("#### Token Performance Matrix")

        perf_df = df_tokens[["symbol", "project", "price_usd", "price_change_24h",
                             "market_cap_usd", "volume_24h", "holders"]].copy()
        perf_df["price_usd"] = perf_df["price_usd"].apply(format_price)
        perf_df["market_cap_usd"] = perf_df["market_cap_usd"].apply(lambda x: format_number(x))
        perf_df["volume_24h"] = perf_df["volume_24h"].apply(lambda x: format_number(x))
        perf_df["price_change_24h"] = perf_df["price_change_24h"].apply(lambda x: f"{x:+.2f}%")
        perf_df["holders"] = perf_df["holders"].apply(lambda x: f"{x:,}")

        perf_df.columns = ["Symbol", "Project", "Price", "24h Change", "Market Cap", "Volume", "Holders"]

        st.dataframe(perf_df, width="stretch", hide_index=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Market Cap Distribution")
            fig_mcap = px.pie(
                df_tokens,
                values="market_cap_usd",
                names="symbol",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_mcap.update_layout(height=350)
            apply_chart_theme(fig_mcap)
            st.plotly_chart(fig_mcap, width="stretch")

        with col2:
            st.markdown("#### Volume vs Market Cap")
            fig_scatter = px.scatter(
                df_tokens,
                x="market_cap_usd",
                y="volume_24h",
                size="holders",
                color="symbol",
                hover_name="project",
                log_x=True,
                log_y=True,
                size_max=60
            )
            fig_scatter.update_layout(
                height=350,
                xaxis_title="Market Cap (log)",
                yaxis_title="24h Volume (log)"
            )
            apply_chart_theme(fig_scatter)
            st.plotly_chart(fig_scatter, width="stretch")

        # Individual token deep dive
        st.markdown("---")
        st.markdown("#### 📊 Token Deep Dive")

        selected_token = st.selectbox("Select token for detailed analysis", df_tokens["symbol"].tolist())
        token_data = df_tokens[df_tokens["symbol"] == selected_token].iloc[0]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Price", format_price(token_data["price_usd"]),
                      delta=f"{token_data['price_change_24h']:+.1f}%")
        with col2:
            st.metric("Market Cap", format_number(token_data["market_cap_usd"]))
        with col3:
            st.metric("FDV", format_number(token_data["fdv_usd"]))

        # Price chart
        price_history = get_price_history(fetcher, selected_token, token_data["address"], use_live_data, days=60)

        fig_price = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                   row_heights=[0.7, 0.3],
                                   subplot_titles=("Price (USD)", "Volume"))

        fig_price.add_trace(
            go.Candlestick(
                x=price_history["timestamp"],
                open=price_history["close"] * 0.98,
                high=price_history["close"] * 1.02,
                low=price_history["close"] * 0.97,
                close=price_history["close"],
                name="Price"
            ),
            row=1, col=1
        )

        fig_price.add_trace(
            go.Bar(x=price_history["timestamp"], y=price_history["volume"],
                   name="Volume", marker_color="#667eea"),
            row=2, col=1
        )

        fig_price.update_layout(
            height=500,
            showlegend=False,
            xaxis_rangeslider_visible=False
        )
        apply_chart_theme(fig_price)
        st.plotly_chart(fig_price, width="stretch")

    # ========== BUILDER VIEW ==========
    elif view_mode == "🔧 Builder":
        st.markdown("### 🔧 Ecosystem Builder Dashboard")
        st.markdown("Track deployer activity, new token launches, and ecosystem growth metrics")

        # Deployer activity
        st.markdown("#### 🚀 Clanker Deployer Activity")
        st.markdown("Token deployment contracts powering the agent economy")

        deployer_df = get_deployer_activity(fetcher, use_live_data, days=30)

        # Key deployer metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            recent_deployments = deployer_df["v3.1_deployments"].tail(7).sum() + deployer_df["v4.1_deployments"].tail(7).sum()
            st.metric("7-Day Deployments", f"{recent_deployments:,}")
        with col2:
            daily_avg = (deployer_df["v3.1_deployments"].mean() + deployer_df["v4.1_deployments"].mean())
            st.metric("Daily Avg Deployments", f"{daily_avg:.0f}")
        with col3:
            total_txs = deployer_df["total_txs"].sum()
            st.metric("Total Transactions (30d)", f"{total_txs:,}")
        with col4:
            growth = ((deployer_df["total_txs"].tail(7).mean() /
                       deployer_df["total_txs"].head(7).mean()) - 1) * 100
            st.metric("Week-over-Week Growth", f"{growth:+.1f}%")

        # Deployment activity chart
        fig_deploy = go.Figure()

        fig_deploy.add_trace(go.Bar(
            x=deployer_df["date"],
            y=deployer_df["v3.1_deployments"],
            name="v3.1 Deployer",
            marker_color="#667eea"
        ))

        fig_deploy.add_trace(go.Bar(
            x=deployer_df["date"],
            y=deployer_df["v4.1_deployments"],
            name="v4.1 Deployer",
            marker_color="#764ba2"
        ))

        fig_deploy.update_layout(
            barmode="stack",
            height=400,
            xaxis_title="Date",
            yaxis_title="Deployments"
        )
        apply_chart_theme(fig_deploy, title="Daily Token Deployments by Deployer Version")
        st.plotly_chart(fig_deploy, width="stretch")

        # Deployer addresses
        st.markdown("#### 📍 Deployer Contract Addresses")

        for version, addr in DEPLOYER_CONTRACTS.items():
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                st.markdown(f"**{version}**")
            with col2:
                st.code(addr, language=None)
            with col3:
                st.link_button("View on Basescan", f"https://basescan.org/address/{addr}")

        # Ecosystem growth chart
        st.markdown("---")
        st.markdown("#### 📈 Ecosystem Growth Metrics")

        # Cumulative deployments
        deployer_df["cumulative"] = (deployer_df["v3.1_deployments"] +
                                      deployer_df["v4.1_deployments"]).cumsum()

        fig_growth = go.Figure()
        fig_growth.add_trace(go.Scatter(
            x=deployer_df["date"],
            y=deployer_df["cumulative"],
            mode="lines+markers",
            name="Cumulative Deployments",
            fill="tozeroy",
            line=dict(color="#00ff88", width=3)
        ))

        fig_growth.update_layout(height=350)
        apply_chart_theme(fig_growth, title="Cumulative Token Deployments (30 Days)")
        st.plotly_chart(fig_growth, width="stretch")

        # Builder resources
        st.markdown("---")
        st.markdown("#### 🛠️ Builder Resources")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **Dune Analytics Query Template:**
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
            """)

        with col2:
            st.markdown("""
            **Quick Links:**
            - [Basescan](https://basescan.org)
            - [Dune Base Dashboard](https://dune.com/tk-research/base)
            - [GeckoTerminal Base](https://www.geckoterminal.com/base)
            - [XMTP Protocol](https://xmtp.org)
            """)

    # ========== RISK ANALYSIS VIEW ==========
    elif view_mode == "⚠️ Risk Analysis":
        st.markdown("### ⚠️ Risk Analysis Dashboard")
        st.markdown("Assess investment risks across the OpenClaw ecosystem")

        # Risk overview
        st.markdown("#### Risk Assessment Summary")

        risk_data = []
        for _, row in df_tokens.iterrows():
            risk_label, risk_emoji, risk_color = calculate_risk_score(
                row["holders"], row["top_pool_liquidity"], row["market_cap_usd"]
            )

            # Additional risk factors
            holder_concentration = "High" if row["holders"] < 50000 else ("Medium" if row["holders"] < 200000 else "Low")
            liquidity_ratio = (row["top_pool_liquidity"] / row["market_cap_usd"] * 100) if row["market_cap_usd"] > 0 else 0
            liquidity_risk = "High" if liquidity_ratio < 1 else ("Medium" if liquidity_ratio < 3 else "Low")

            risk_data.append({
                "Token": row["symbol"],
                "Project": row["project"],
                "Overall Risk": f"{risk_emoji} {risk_label}",
                "Holder Concentration": holder_concentration,
                "Liquidity Risk": liquidity_risk,
                "Holders": f"{row['holders']:,}",
                "Liquidity Ratio": f"{liquidity_ratio:.2f}%"
            })

        risk_df = pd.DataFrame(risk_data)
        st.dataframe(risk_df, width="stretch", hide_index=True)

        # Risk indicators detail
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📊 Holder Distribution")

            fig_holders = px.bar(
                df_tokens,
                x="symbol",
                y="holders",
                color="holders",
                color_continuous_scale="Viridis",
                labels={"holders": "Holder Count", "symbol": "Token"}
            )
            fig_holders.update_layout(height=350)
            apply_chart_theme(fig_holders)
            st.plotly_chart(fig_holders, width="stretch")

            st.info("""
            **Holder Concentration Risk:**
            - More holders = lower risk of price manipulation
            - Watch for sudden holder decreases (whale exits)
            - CLANKER shows healthiest distribution
            """)

        with col2:
            st.markdown("#### 💧 Liquidity Analysis")

            fig_liq = go.Figure()
            fig_liq.add_trace(go.Bar(
                x=df_tokens["symbol"],
                y=df_tokens["top_pool_liquidity"],
                name="Pool Liquidity",
                marker_color="#667eea"
            ))
            fig_liq.update_layout(
                height=350,
                yaxis_title="Liquidity (USD)"
            )
            apply_chart_theme(fig_liq)
            st.plotly_chart(fig_liq, width="stretch")

            st.warning("""
            **Liquidity Risk Factors:**
            - Low liquidity = high slippage on trades
            - Monitor Uniswap pool reserves
            - Check for liquidity locks via LpLocker contracts
            """)

        # Risk alerts
        st.markdown("---")
        st.markdown("#### 🚨 Risk Alerts & Watchlist")

        st.markdown("""
        | Alert Type | Description | Tokens to Watch |
        |------------|-------------|-----------------|
        | 🔴 High Volatility | 24h price swings >20% | MOLT (memecoin dynamics) |
        | 🟡 Low Liquidity | Pool reserves <$50K | Monitor all tokens |
        | 🟢 Healthy Growth | Steady holder increase | CLANKER, BNKR |
        | ⚠️ Rug Indicators | Check liquidity locks | Verify via LpLocker |
        """)

        # LpLocker contract info
        st.markdown("---")
        st.markdown("#### 🔒 Liquidity Lock Verification")

        st.code("LpLocker Contract: 0x33e2Eda238edcF470309b8c6D228986A1204c8f9", language=None)
        st.link_button("Verify Locks on Basescan",
                       "https://basescan.org/address/0x33e2Eda238edcF470309b8c6D228986A1204c8f9")

        st.info("""
        **How to verify liquidity locks:**
        1. Check the LpLocker contract for locked LP tokens
        2. Verify lock duration extends beyond your investment horizon
        3. Cross-reference with pool addresses on GeckoTerminal
        """)


if __name__ == "__main__":
    main()

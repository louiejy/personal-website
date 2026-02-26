import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import time
from typing import Optional

st.set_page_config(
    page_title="Fractal Markets — Hurst Exponent",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;500&family=Lora:ital,wght@0,400;1,400&display=swap');

:root {
    --bg: #07090C;
    --bg-card: #0D1018;
    --bg-muted: #121620;
    --teal: #00D4AA;
    --teal-dim: rgba(0,212,170,0.12);
    --teal-border: rgba(0,212,170,0.2);
    --text: #D8E8E4;
    --text-muted: #4D6B64;
    --red: #E05C6A;
    --amber: #E8A030;
    --slate: #7A8FA8;
    --border: rgba(0,212,170,0.14);
}

html, body, [class*="css"] {
    font-family: 'JetBrains Mono', monospace;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}
.stApp { background-color: var(--bg) !important; }
#MainMenu, footer, header { visibility: hidden; }

/* ── Header ── */
.app-header {
    padding: 2.8rem 0 1.6rem 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2rem;
}
.app-title {
    font-family: 'Syne', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    color: var(--text);
    letter-spacing: -0.03em;
    line-height: 1;
    margin: 0;
}
.app-subtitle {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: var(--teal);
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-top: 0.55rem;
}

/* ── H Cards ── */
.h-card {
    background: var(--bg-card);
    border: 1px solid var(--teal-border);
    border-top: 2px solid var(--card-accent, var(--teal));
    border-radius: 4px;
    padding: 1.4rem 1.2rem;
    text-align: center;
}
.h-ticker {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.6rem;
}
.h-value {
    font-family: 'Syne', sans-serif;
    font-size: 3rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    line-height: 1;
    margin-bottom: 0.4rem;
}
.h-regime {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.h-desc {
    font-family: 'Lora', serif;
    font-style: italic;
    font-size: 0.75rem;
    color: var(--text-muted);
    line-height: 1.5;
}

/* ── Inputs ── */
.stTextInput > div > div > input {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 3px !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
    padding: 0.55rem 0.75rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--teal) !important;
    box-shadow: 0 0 0 2px var(--teal-dim) !important;
}
.stTextInput label, .stSelectbox label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.6rem !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
}
.stSelectbox > div > div {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 3px !important;
}
.stSelectbox > div > div > div {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
}

/* ── Button ── */
.stButton > button {
    background: var(--teal) !important;
    color: #07090C !important;
    border: none !important;
    border-radius: 3px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.7rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    padding: 0.6rem 2rem !important;
    transition: opacity 0.2s ease !important;
}
.stButton > button:hover { opacity: 0.8 !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
    background: transparent !important;
    border: none !important;
    padding: 0.55rem 1.1rem !important;
}
.stTabs [aria-selected="true"] {
    color: var(--teal) !important;
    border-bottom: 2px solid var(--teal) !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.2rem !important; }

/* ── Section labels ── */
.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--teal);
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.45rem;
    margin: 1.5rem 0 1rem 0;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--teal) !important; }
</style>
""", unsafe_allow_html=True)


# ── Plotly theme ──────────────────────────────────────────────────────────────
LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="JetBrains Mono", color="#D8E8E4", size=10),
    xaxis=dict(
        gridcolor="rgba(0,212,170,0.06)",
        linecolor="rgba(0,212,170,0.14)",
        tickfont=dict(size=9),
        zeroline=False,
    ),
    yaxis=dict(
        gridcolor="rgba(0,212,170,0.06)",
        linecolor="rgba(0,212,170,0.14)",
        tickfont=dict(size=9),
        zeroline=False,
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor="rgba(0,212,170,0.14)",
        borderwidth=1,
        font=dict(size=9),
    ),
    margin=dict(l=0, r=0, t=30, b=0),
    hovermode="x unified",
)

PALETTE = ["#00D4AA", "#E05C6A", "#E8A030", "#7B9FD4", "#C87FD4", "#6BCFB8"]


# ── Hurst R/S implementation ──────────────────────────────────────────────────
def _rs_core(prices: np.ndarray, min_chunk: int = 20):
    """
    Rescaled Range analysis on a price array.
    Returns (chunk_sizes, mean_rs_per_size).
    """
    log_ret = np.diff(np.log(np.maximum(prices, 1e-12)))
    n = len(log_ret)

    # Generate chunk sizes: n//2, n//3, ... down to min_chunk
    sizes = sorted(set(n // k for k in range(2, n + 1) if n // k >= min_chunk))
    if len(sizes) < 3:
        return [], []

    ns, rs_means = [], []
    for size in sizes:
        rs_list = []
        for start in range(0, n - size + 1, size):
            chunk = log_ret[start : start + size]
            dev = np.cumsum(chunk - chunk.mean())
            R = dev.max() - dev.min()
            S = chunk.std(ddof=1)
            if S > 0:
                rs_list.append(R / S)
        if rs_list:
            ns.append(size)
            rs_means.append(float(np.mean(rs_list)))

    return ns, rs_means


def hurst_rs(prices: np.ndarray) -> Optional[float]:
    ns, rs = _rs_core(prices)
    if len(ns) < 3:
        return None
    H = np.polyfit(np.log(ns), np.log(rs), 1)[0]
    return round(float(H), 4)


def rolling_hurst_series(prices: np.ndarray, window: int, step: int = 3):
    idxs, vals = [], []
    for i in range(window, len(prices), step):
        H = hurst_rs(prices[i - window : i + 1])
        if H is not None:
            idxs.append(i)
            vals.append(H)
    return idxs, vals


# ── Cached data layer ─────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_prices(ticker: str, period: str) -> pd.DataFrame:
    df = yf.Ticker(ticker).history(period=period)[["Close"]].dropna()
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def get_hurst_full(ticker: str, period: str) -> Optional[float]:
    df = fetch_prices(ticker, period)
    return hurst_rs(df["Close"].values)


@st.cache_data(ttl=3600, show_spinner=False)
def get_rolling_h(ticker: str, period: str, window: int):
    df = fetch_prices(ticker, period)
    prices = df["Close"].values
    dates = df.index
    idxs, vals = rolling_hurst_series(prices, window=window)
    return [str(dates[i].date()) for i in idxs], vals


@st.cache_data(ttl=3600, show_spinner=False)
def get_rs_data(ticker: str, period: str) -> dict:
    df = fetch_prices(ticker, period)
    ns, rs = _rs_core(df["Close"].values)
    if len(ns) < 3:
        return {}
    log_n = np.log(ns)
    log_rs = np.log(rs)
    coeffs = np.polyfit(log_n, log_rs, 1)
    H = round(float(coeffs[0]), 4)
    fitted = list(np.exp(np.polyval(coeffs, log_n)))
    # Random walk reference (slope = 0.5, same intercept mid-point)
    intercept_rw = np.mean(log_rs) - 0.5 * np.mean(log_n)
    rw_fitted = list(np.exp(0.5 * log_n + intercept_rw))
    return {"ns": ns, "rs": rs, "H": H, "fitted": fitted, "rw_ref": rw_fitted}


# ── Interpretation helpers ─────────────────────────────────────────────────────
def h_regime(H: float):
    if H < 0.45:
        return "Mean-Reverting", "#E05C6A", "Prices tend to reverse prior moves. Consistent with a range-bound market."
    if H < 0.55:
        return "Random Walk", "#7A8FA8", "No detectable memory. Consistent with the Efficient Market Hypothesis."
    return "Persistent / Trending", "#00D4AA", "Past trends tend to continue. The market exhibits long memory."


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <p class="app-title">Fractal Markets</p>
    <p class="app-subtitle">Hurst Exponent · Rescaled Range Analysis · After Mandelbrot</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="font-family:'Lora',serif;font-style:italic;font-size:0.82rem;
color:rgba(77,107,100,0.9);line-height:1.65;border-left:2px solid rgba(0,212,170,0.3);
padding-left:1rem;margin-bottom:2rem;max-width:780px;">
    "The key insight of fractal geometry is that roughness is the rule, not the exception — in nature,
    and in markets." — Benoît Mandelbrot. The Hurst exponent (H) measures long memory in a time series.
    H&nbsp;>&nbsp;0.5 means trends persist; H&nbsp;<&nbsp;0.5 means reversals dominate;
    H&nbsp;≈&nbsp;0.5 is the random walk assumed by classical finance.
</div>
""", unsafe_allow_html=True)

# ── Inputs ────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns([2, 1, 1.2, 0.9])
with c1:
    tickers_raw = st.text_input(
        "Tickers (comma-separated)",
        value="AAPL, SPY, BTC-USD",
        placeholder="e.g. AAPL, SPY, RY.TO, BTC-USD",
    )
with c2:
    period = st.selectbox("Data Period", ["2y", "5y", "10y", "max"], index=1)
with c3:
    win_label = st.selectbox(
        "Rolling Window",
        ["3 months  (63d)", "6 months (126d)", "1 year   (252d)", "2 years  (504d)"],
        index=2,
    )
    WIN_MAP = {"3 months  (63d)": 63, "6 months (126d)": 126, "1 year   (252d)": 252, "2 years  (504d)": 504}
    rolling_window = WIN_MAP[win_label]
with c4:
    st.markdown("<div style='height:1.85rem'></div>", unsafe_allow_html=True)
    run = st.button("Calculate H", type="primary", use_container_width=True)

st.markdown("""
<div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:rgba(77,107,100,0.55);
letter-spacing:0.08em;margin-top:0.3rem;margin-bottom:1.5rem;">
    Canadian stocks: add .TO suffix (e.g. RY.TO, TD.TO) · Crypto: BTC-USD, ETH-USD · FX: EURUSD=X
</div>
""", unsafe_allow_html=True)

# ── Analysis ──────────────────────────────────────────────────────────────────
if run:
    tickers = [t.strip().upper() for t in tickers_raw.split(",") if t.strip()][:5]

    loaded = {}
    errors = []
    prog = st.progress(0, text="Fetching price data...")
    for i, ticker in enumerate(tickers):
        prog.progress((i + 1) / len(tickers), text=f"Fetching {ticker}...")
        try:
            df = fetch_prices(ticker, period)
            if len(df) < 100:
                errors.append(f"{ticker}: insufficient history ({len(df)} days)")
                continue
            loaded[ticker] = df
        except Exception as e:
            errors.append(f"{ticker}: {str(e)[:60]}")
        time.sleep(0.08)
    prog.empty()

    for err in errors:
        st.warning(err)
    if not loaded:
        st.error("No data retrieved. Check your tickers.")
        st.stop()

    # ── H cards ───────────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Hurst Exponent — Full Period</div>', unsafe_allow_html=True)

    h_full = {}
    cols = st.columns(len(loaded))
    for i, (ticker, df) in enumerate(loaded.items()):
        H = hurst_rs(df["Close"].values)
        h_full[ticker] = H
        with cols[i]:
            if H is not None:
                regime, color, desc = h_regime(H)
                st.markdown(f"""
                <div class="h-card" style="--card-accent:{color};">
                    <div class="h-ticker">{ticker}</div>
                    <div class="h-value" style="color:{color};">{H:.3f}</div>
                    <div class="h-regime" style="color:{color};">{regime}</div>
                    <div class="h-desc">{desc}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="h-card" style="--card-accent:#4D6B64;">
                    <div class="h-ticker">{ticker}</div>
                    <div class="h-value" style="color:var(--text-muted);">—</div>
                    <div class="h-desc">Insufficient data for R/S analysis.</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["Rolling Hurst", "R/S Analysis", "Price History"])

    # ─ Tab 1: Rolling Hurst ───────────────────────────────────────────────────
    with tab1:
        st.markdown(
            f'<div class="section-label">Rolling H — {rolling_window}-Day Window (computed every 3 days)</div>',
            unsafe_allow_html=True,
        )

        fig = go.Figure()

        # Regime background bands
        fig.add_hrect(y0=0.0,  y1=0.45, fillcolor="rgba(224,92,106,0.05)", line_width=0,
                      annotation_text="Mean-reverting zone", annotation_position="top right",
                      annotation_font=dict(size=8, color="rgba(224,92,106,0.4)"))
        fig.add_hrect(y0=0.45, y1=0.55, fillcolor="rgba(122,143,168,0.05)", line_width=0,
                      annotation_text="Random walk zone", annotation_position="top right",
                      annotation_font=dict(size=8, color="rgba(122,143,168,0.4)"))
        fig.add_hrect(y0=0.55, y1=1.0,  fillcolor="rgba(0,212,170,0.04)",  line_width=0,
                      annotation_text="Trending zone", annotation_position="top right",
                      annotation_font=dict(size=8, color="rgba(0,212,170,0.4)"))

        # H = 0.5 reference
        fig.add_hline(y=0.5, line_dash="dot", line_color="rgba(255,255,255,0.15)", line_width=1)

        all_loaded = True
        for i, ticker in enumerate(loaded):
            with st.spinner(f"Computing rolling H for {ticker}…"):
                dates, H_vals = get_rolling_h(ticker, period, rolling_window)
            if not H_vals:
                st.warning(f"{ticker}: not enough data for rolling H with {rolling_window}-day window.")
                all_loaded = False
                continue
            fig.add_trace(go.Scatter(
                x=dates, y=H_vals,
                mode="lines", name=ticker,
                line=dict(color=PALETTE[i % len(PALETTE)], width=1.8),
            ))

        fig.update_layout(
            **LAYOUT, height=400,
            yaxis=dict(**LAYOUT["yaxis"], range=[0.15, 0.85], title="H"),
            xaxis=dict(**LAYOUT["xaxis"], title=None),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.58rem;
        color:rgba(77,107,100,0.5);letter-spacing:0.06em;margin-top:0.3rem;">
            Interpretation: sustained H &gt; 0.55 → trending regime · H &lt; 0.45 → mean-reverting regime ·
            Regime shifts can precede volatility changes.
        </div>
        """, unsafe_allow_html=True)

    # ─ Tab 2: R/S Analysis ────────────────────────────────────────────────────
    with tab2:
        st.markdown('<div class="section-label">R/S Log-Log Plot — Regression Slope = H</div>', unsafe_allow_html=True)

        fig2 = go.Figure()
        for i, ticker in enumerate(loaded):
            rs_data = get_rs_data(ticker, period)
            if not rs_data:
                continue
            color = PALETTE[i % len(PALETTE)]
            log_ns  = np.log(rs_data["ns"]).tolist()
            log_rs  = np.log(rs_data["rs"]).tolist()
            log_fit = np.log(rs_data["fitted"]).tolist()
            H = rs_data["H"]

            fig2.add_trace(go.Scatter(
                x=log_ns, y=log_rs,
                mode="markers", name=f"{ticker}  H={H}",
                marker=dict(color=color, size=8, symbol="circle"),
            ))
            fig2.add_trace(go.Scatter(
                x=log_ns, y=log_fit,
                mode="lines", name=f"{ticker} fit  (slope={H})",
                line=dict(color=color, width=1.5, dash="dash"),
                showlegend=False,
            ))

        # Random walk reference (slope=0.5)
        all_ns = []
        for ticker in loaded:
            rd = get_rs_data(ticker, period)
            if rd:
                all_ns.extend(rd["ns"])
        if all_ns:
            x_rng = np.linspace(np.log(min(all_ns)), np.log(max(all_ns)), 60)
            mid_y = np.mean([np.log(get_rs_data(t, period)["rs"]).mean()
                             for t in loaded if get_rs_data(t, period)])
            mid_x = np.mean(x_rng)
            y_rw  = mid_y + 0.5 * (x_rng - mid_x)
            fig2.add_trace(go.Scatter(
                x=x_rng.tolist(), y=y_rw.tolist(),
                mode="lines", name="Random walk (H=0.5)",
                line=dict(color="rgba(255,255,255,0.2)", width=1, dash="dot"),
            ))

        fig2.update_layout(
            **LAYOUT, height=420,
            hovermode="closest",
            xaxis=dict(**LAYOUT["xaxis"], title="log(chunk size n)"),
            yaxis=dict(**LAYOUT["yaxis"], title="log(R/S)"),
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("""
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.58rem;
        color:rgba(77,107,100,0.5);letter-spacing:0.06em;margin-top:0.3rem;">
            Each dot = average rescaled range at a given chunk size n.
            Slope of the fitted line = Hurst exponent.
            Dotted white line = pure random walk slope (H=0.5) for reference.
        </div>
        """, unsafe_allow_html=True)

    # ─ Tab 3: Price History ───────────────────────────────────────────────────
    with tab3:
        st.markdown('<div class="section-label">Price History (Normalized to 100 at Start)</div>', unsafe_allow_html=True)

        fig3 = go.Figure()
        for i, (ticker, df) in enumerate(loaded.items()):
            norm = (df["Close"] / df["Close"].iloc[0] * 100)
            fig3.add_trace(go.Scatter(
                x=[str(d.date()) for d in df.index],
                y=norm.tolist(),
                mode="lines", name=ticker,
                line=dict(color=PALETTE[i % len(PALETTE)], width=1.5),
            ))

        fig3.update_layout(
            **LAYOUT, height=380,
            yaxis=dict(**LAYOUT["yaxis"], title="Indexed (base = 100)"),
        )
        st.plotly_chart(fig3, use_container_width=True)

    # ── Summary table ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Summary</div>', unsafe_allow_html=True)
    rows = []
    for ticker, df in loaded.items():
        H = h_full.get(ticker)
        if H is not None:
            regime, _, _ = h_regime(H)
        else:
            regime = "—"
        rows.append({
            "Ticker":       ticker,
            "H (full period)": f"{H:.3f}" if H else "—",
            "Regime":       regime,
            "Data Points":  len(df),
            "Period Start": str(df.index[0].date()),
            "Period End":   str(df.index[-1].date()),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

else:
    st.markdown("""
    <div style="text-align:center;padding:5rem 2rem;color:rgba(77,107,100,0.35);">
        <div style="font-family:'Syne',sans-serif;font-size:5rem;font-weight:800;
        letter-spacing:-0.04em;opacity:0.25;margin-bottom:0.5rem;">0.72</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.68rem;
        letter-spacing:0.18em;text-transform:uppercase;color:rgba(0,212,170,0.3);">
            Enter tickers and click Calculate H
        </div>
        <div style="font-family:'Lora',serif;font-style:italic;font-size:0.8rem;
        margin-top:0.8rem;color:rgba(77,107,100,0.25);">
            Stocks · ETFs · Crypto · FX · Canadian (RY.TO) · All via Yahoo Finance
        </div>
    </div>
    """, unsafe_allow_html=True)

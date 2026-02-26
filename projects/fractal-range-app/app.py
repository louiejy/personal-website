import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from typing import Optional

st.set_page_config(
    page_title="Fractal Range — Trade · Trend · Tail",
    page_icon="▣",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Fira+Code:wght@300;400;500&family=Lora:ital@1&display=swap');

:root {
    --bg:        #080B0F;
    --bg-card:   #0D1219;
    --bg-muted:  #111820;
    --amber:     #F0A500;
    --amber-dim: rgba(240,165,0,0.1);
    --amber-bdr: rgba(240,165,0,0.2);
    --bull:      #00C896;
    --bear:      #E04560;
    --neutral:   #6B7A8F;
    --text:      #D6E0E8;
    --text-muted:#4A5A68;
    --border:    rgba(240,165,0,0.14);

    /* band colors */
    --trade-c:  #F0A500;
    --trend-c:  #5B9BD5;
    --tail-c:   #9B7FE8;
}

html, body, [class*="css"] {
    font-family: 'Fira Code', monospace;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}
.stApp { background-color: var(--bg) !important; }
#MainMenu, footer, header { visibility: hidden; }

/* ── App header ── */
.app-header {
    padding: 2.5rem 0 1.4rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2rem;
    display: flex;
    align-items: flex-end;
    gap: 1.5rem;
}
.app-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3.4rem;
    color: var(--text);
    letter-spacing: 0.05em;
    line-height: 1;
    margin: 0;
}
.app-tagline {
    font-family: 'Fira Code', monospace;
    font-size: 0.62rem;
    color: var(--amber);
    letter-spacing: 0.18em;
    text-transform: uppercase;
    padding-bottom: 0.3rem;
}

/* ── Signal cards ── */
.sig-card {
    background: var(--bg-card);
    border: 1px solid var(--card-bdr, var(--border));
    border-top: 3px solid var(--card-accent, var(--amber));
    border-radius: 3px;
    padding: 1.2rem 1rem 1rem;
}
.sig-horizon {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.1rem;
    letter-spacing: 0.1em;
    color: var(--card-accent, var(--amber));
    margin-bottom: 0.25rem;
}
.sig-window {
    font-family: 'Fira Code', monospace;
    font-size: 0.55rem;
    letter-spacing: 0.12em;
    color: var(--text-muted);
    text-transform: uppercase;
    margin-bottom: 0.8rem;
}
.sig-badge {
    display: inline-block;
    padding: 0.2rem 0.55rem;
    border-radius: 2px;
    font-family: 'Fira Code', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.08em;
    margin-bottom: 0.7rem;
}
.sig-levels {
    font-family: 'Fira Code', monospace;
    font-size: 0.65rem;
    color: var(--text-muted);
    line-height: 1.8;
}
.sig-levels span { color: var(--text); }

/* ── H card ── */
.h-strip {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-left: 3px solid var(--amber);
    border-radius: 3px;
    padding: 1rem 1.2rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
    height: 100%;
}
.h-strip-val {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.6rem;
    letter-spacing: 0.05em;
    line-height: 1;
    margin-bottom: 0.2rem;
}
.h-strip-label {
    font-family: 'Fira Code', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}
.h-strip-note {
    font-family: 'Lora', serif;
    font-style: italic;
    font-size: 0.72rem;
    color: var(--text-muted);
    line-height: 1.5;
}

/* ── Inputs ── */
.stTextInput > div > div > input {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 3px !important;
    color: var(--text) !important;
    font-family: 'Fira Code', monospace !important;
    font-size: 0.82rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--amber) !important;
    box-shadow: 0 0 0 2px var(--amber-dim) !important;
}
.stTextInput label, .stSelectbox label {
    font-family: 'Fira Code', monospace !important;
    font-size: 0.58rem !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
}
.stSelectbox > div > div {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 3px !important;
}
.stButton > button {
    background: var(--amber) !important;
    color: #080B0F !important;
    border: none !important;
    border-radius: 2px !important;
    font-family: 'Fira Code', monospace !important;
    font-size: 0.68rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    padding: 0.6rem 1.5rem !important;
    transition: opacity 0.15s ease !important;
}
.stButton > button:hover { opacity: 0.8 !important; }
.stToggle label {
    font-family: 'Fira Code', monospace !important;
    font-size: 0.62rem !important;
    letter-spacing: 0.1em !important;
    color: var(--text-muted) !important;
}
.section-label {
    font-family: 'Fira Code', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--amber);
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.4rem;
    margin: 1.8rem 0 1rem;
}
.stSpinner > div { border-top-color: var(--amber) !important; }
</style>
""", unsafe_allow_html=True)

# ── Plotly base theme ─────────────────────────────────────────────────────────
_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Fira Code", color="#D6E0E8", size=10),
    margin=dict(l=0, r=0, t=20, b=0),
)
_AXIS = dict(
    gridcolor="rgba(240,165,0,0.05)",
    linecolor="rgba(240,165,0,0.12)",
    tickfont=dict(size=9, family="Fira Code"),
    zeroline=False,
)


# ── Hurst R/S ────────────────────────────────────────────────────────────────
def _rs_core(prices: np.ndarray, min_chunk: int = 20):
    log_ret = np.diff(np.log(np.maximum(prices, 1e-12)))
    n = len(log_ret)
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
    return round(float(np.clip(H, 0.01, 0.99)), 4)


# ── Fractal range computation ─────────────────────────────────────────────────
TIMEFRAMES = {
    "trade": {"window": 21,  "label": "Trade",  "desc": "3 weeks",   "color": "#F0A500"},
    "trend": {"window": 63,  "label": "Trend",  "desc": "3 months",  "color": "#5B9BD5"},
    "tail":  {"window": 252, "label": "Tail",   "desc": "12 months", "color": "#9B7FE8"},
}


def compute_ranges(df: pd.DataFrame, H: float, use_hurst: bool = True) -> pd.DataFrame:
    """
    Compute fractal-adjusted Trade/Trend/Tail support & resistance.

    Band width = hvol(N) * close * (N/252)^exponent
    where exponent = H (fractal) or 0.5 (classical).
    """
    close = df["Close"]
    log_ret = np.log(close / close.shift(1))
    exponent = H if use_hurst else 0.5

    out = {}
    for name, cfg in TIMEFRAMES.items():
        N = cfg["window"]
        hvol = log_ret.rolling(N).std() * np.sqrt(252)
        ma   = close.rolling(N).mean()
        sigma = hvol * close * (N / 252) ** exponent

        out[f"{name}_upper"] = ma + sigma
        out[f"{name}_lower"] = ma - sigma
        out[f"{name}_ma"]    = ma

    return pd.DataFrame(out, index=df.index)


def get_signal(close_val: float, upper: float, lower: float, ma: float):
    """Returns (label, bg_color, text_color)."""
    if pd.isna(upper) or pd.isna(lower):
        return "NO DATA", "#1A1F2A", "#6B7A8F"
    if close_val >= upper:
        return "BULLISH BREAKOUT", "rgba(0,200,150,0.15)", "#00C896"
    if close_val > ma:
        return "BULLISH", "rgba(0,200,150,0.10)", "#00C896"
    if close_val > lower:
        return "BEARISH", "rgba(224,69,96,0.10)", "#E04560"
    return "BEARISH BREAKDOWN", "rgba(224,69,96,0.15)", "#E04560"


def h_regime(H: float):
    if H < 0.45:
        return "Mean-Reverting", "#E04560"
    if H < 0.55:
        return "Random Walk",    "#6B7A8F"
    return "Persistent",         "#00C896"


# ── Cached data ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_ohlcv(ticker: str, period: str) -> pd.DataFrame:
    df = yf.Ticker(ticker).history(period=period)
    return df[["Open", "High", "Low", "Close", "Volume"]].dropna()


@st.cache_data(ttl=3600, show_spinner=False)
def get_hurst(ticker: str, period: str) -> Optional[float]:
    df = fetch_ohlcv(ticker, period)
    return hurst_rs(df["Close"].values)


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div>
        <p class="app-title">FRACTAL RANGE</p>
    </div>
    <div style="padding-bottom:0.4rem;">
        <p class="app-tagline">Trade · Trend · Tail · Hurst-Adjusted Volatility Bands</p>
        <div style="font-family:'Lora',serif;font-style:italic;font-size:0.72rem;
        color:rgba(74,90,104,0.8);max-width:560px;line-height:1.5;margin-top:0.2rem;">
            Classical finance scales volatility as √T. Mandelbrot showed it scales as T^H.
            When H&nbsp;>&nbsp;0.5, tail risk is systematically wider than models assume.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Inputs ────────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns([1.2, 0.9, 0.9, 0.9, 0.9])
with c1:
    ticker = st.text_input("Ticker", value="SPY", placeholder="SPY, AAPL, BTC-USD, RY.TO").strip().upper()
with c2:
    period = st.selectbox("Calculation Period", ["2y", "5y", "10y", "max"], index=1)
with c3:
    display_days = st.selectbox("Chart Window", [60, 90, 180, 365], index=1,
                                format_func=lambda x: f"Last {x} days")
with c4:
    use_hurst = st.toggle("Fractal scaling (H)", value=True,
                          help="Use Hurst exponent to scale bands. Off = classical √T.")
with c5:
    st.markdown("<div style='height:1.85rem'></div>", unsafe_allow_html=True)
    run = st.button("Analyze", type="primary", use_container_width=True)

# ── Analysis ──────────────────────────────────────────────────────────────────
if run:
    with st.spinner(f"Fetching {ticker}…"):
        try:
            df = fetch_ohlcv(ticker, period)
        except Exception as e:
            st.error(f"Could not fetch data for {ticker}: {e}")
            st.stop()

    if len(df) < 300:
        st.warning(f"Only {len(df)} trading days available. Results may be less reliable.")

    # Hurst
    with st.spinner("Computing Hurst exponent…"):
        H = hurst_rs(df["Close"].values)

    if H is None:
        H = 0.5
        st.warning("Insufficient data for R/S analysis — defaulting to H=0.5 (classical).")

    effective_H = H if use_hurst else 0.5

    # Ranges
    ranges = compute_ranges(df, effective_H, use_hurst=True)
    combined = pd.concat([df, ranges], axis=1).dropna()

    last = combined.iloc[-1]
    close_now = last["Close"]

    # ── Signal cards + H card ─────────────────────────────────────────────────
    col_t, col_tr, col_ta, col_h = st.columns([1, 1, 1, 1])
    card_cols = {"trade": col_t, "trend": col_tr, "tail": col_ta}

    for name, cfg in TIMEFRAMES.items():
        upper = last[f"{name}_upper"]
        lower = last[f"{name}_lower"]
        ma    = last[f"{name}_ma"]
        sig_label, sig_bg, sig_fg = get_signal(close_now, upper, lower, ma)

        with card_cols[name]:
            st.markdown(f"""
            <div class="sig-card" style="--card-accent:{cfg['color']};--card-bdr:rgba({
                ','.join(str(int(cfg['color'].lstrip('#')[i:i+2], 16)) for i in (0,2,4))
            },0.25);">
                <div class="sig-horizon">{cfg['label'].upper()}</div>
                <div class="sig-window">{cfg['window']}-day · {cfg['desc']}</div>
                <div class="sig-badge" style="background:{sig_bg};color:{sig_fg};">{sig_label}</div>
                <div class="sig-levels">
                    resist&nbsp;<span>${upper:,.2f}</span><br>
                    price&nbsp;&nbsp;<span>${close_now:,.2f}</span><br>
                    support&nbsp;<span>${lower:,.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # H card
    regime_label, regime_color = h_regime(H)
    h_note = {
        "Mean-Reverting": "Bands are narrower than classical models. Price tends to revert.",
        "Random Walk":    "No detectable memory. Classical and fractal bands are near-identical.",
        "Persistent":     "Bands are wider than classical models. Tail risk is underestimated by √T.",
    }[regime_label]

    with col_h:
        st.markdown(f"""
        <div class="h-strip" style="border-left-color:{regime_color};">
            <div style="font-family:'Fira Code',monospace;font-size:0.55rem;letter-spacing:0.18em;
            text-transform:uppercase;color:var(--text-muted);margin-bottom:0.3rem;">
                Hurst Exponent{'  ·  fractal on' if use_hurst else '  ·  classical √T'}
            </div>
            <div class="h-strip-val" style="color:{regime_color};">{H:.3f}</div>
            <div class="h-strip-label" style="color:{regime_color};">{regime_label}</div>
            <div class="h-strip-note">{h_note}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # ── Chart ─────────────────────────────────────────────────────────────────
    st.markdown(f'<div class="section-label">{ticker} — {display_days}-Day Chart with Fractal Bands</div>',
                unsafe_allow_html=True)

    # Slice to display window
    chart_df = combined.tail(display_days)

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.78, 0.22],
        vertical_spacing=0.02,
    )

    # Band fills (draw widest first so Trade sits on top visually)
    for name, cfg in reversed(list(TIMEFRAMES.items())):
        color_rgb = tuple(int(cfg["color"].lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        opacity = {"tail": 0.07, "trend": 0.09, "trade": 0.11}[name]

        fig.add_trace(go.Scatter(
            x=list(chart_df.index) + list(chart_df.index[::-1]),
            y=list(chart_df[f"{name}_upper"]) + list(chart_df[f"{name}_lower"][::-1]),
            fill="toself",
            fillcolor=f"rgba({color_rgb[0]},{color_rgb[1]},{color_rgb[2]},{opacity})",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
        ), row=1, col=1)

        # Upper/lower band lines
        for bound in ["upper", "lower"]:
            fig.add_trace(go.Scatter(
                x=chart_df.index,
                y=chart_df[f"{name}_{bound}"],
                line=dict(color=f"rgba({color_rgb[0]},{color_rgb[1]},{color_rgb[2]},0.5)",
                          width=1, dash="dot"),
                name=f"{cfg['label']} {'R' if bound == 'upper' else 'S'}",
                showlegend=(bound == "upper"),
            ), row=1, col=1)

        # MA line
        fig.add_trace(go.Scatter(
            x=chart_df.index,
            y=chart_df[f"{name}_ma"],
            line=dict(color=f"rgba({color_rgb[0]},{color_rgb[1]},{color_rgb[2]},0.3)",
                      width=1),
            showlegend=False,
            hoverinfo="skip",
        ), row=1, col=1)

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=chart_df.index,
        open=chart_df["Open"],
        high=chart_df["High"],
        low=chart_df["Low"],
        close=chart_df["Close"],
        increasing_line_color="#00C896",
        decreasing_line_color="#E04560",
        increasing_fillcolor="#00C896",
        decreasing_fillcolor="#E04560",
        name=ticker,
        line=dict(width=1),
    ), row=1, col=1)

    # Volume
    colors = ["#00C896" if c >= o else "#E04560"
              for c, o in zip(chart_df["Close"], chart_df["Open"])]
    fig.add_trace(go.Bar(
        x=chart_df.index,
        y=chart_df["Volume"],
        marker_color=colors,
        marker_opacity=0.5,
        showlegend=False,
        name="Volume",
    ), row=2, col=1)

    # Layout
    fig.update_layout(
        **_LAYOUT,
        height=580,
        hovermode="x unified",
        xaxis_rangeslider_visible=False,
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(240,165,0,0.14)",
            borderwidth=1,
            font=dict(size=9, family="Fira Code"),
            orientation="h",
            yanchor="bottom", y=1.01,
            xanchor="left", x=0,
        ),
    )
    fig.update_xaxes(**_AXIS, row=1, col=1, showticklabels=False)
    fig.update_xaxes(**_AXIS, row=2, col=1)
    fig.update_yaxes(**_AXIS, title_text="Price", title_font=dict(size=9), row=1, col=1)
    fig.update_yaxes(**_AXIS, title_text="Vol",   title_font=dict(size=9), row=2, col=1,
                     tickformat=".2s")

    st.plotly_chart(fig, use_container_width=True)

    # ── Classical vs fractal comparison ───────────────────────────────────────
    if use_hurst and abs(H - 0.5) > 0.02:
        st.markdown('<div class="section-label">Fractal vs Classical — Tail Band Width Difference</div>',
                    unsafe_allow_html=True)

        ranges_classical = compute_ranges(df, 0.5, use_hurst=True)
        comb_cl = pd.concat([df, ranges_classical], axis=1).dropna().tail(display_days)

        fig2 = go.Figure()
        for name, cfg in TIMEFRAMES.items():
            color_rgb = tuple(int(cfg["color"].lstrip("#")[i:i+2], 16) for i in (0, 2, 4))

            frac_width = chart_df[f"{name}_upper"] - chart_df[f"{name}_lower"]
            clas_width = comb_cl[f"{name}_upper"]  - comb_cl[f"{name}_lower"]
            diff_pct   = ((frac_width.values - clas_width.values) / clas_width.values * 100)

            fig2.add_trace(go.Scatter(
                x=chart_df.index,
                y=diff_pct,
                mode="lines",
                name=f"{cfg['label']} (H={H:.2f} vs H=0.5)",
                line=dict(color=f"rgba({color_rgb[0]},{color_rgb[1]},{color_rgb[2]},0.85)",
                          width=1.5),
            ))

        fig2.add_hline(y=0, line_dash="dot",
                       line_color="rgba(255,255,255,0.15)", line_width=1)
        fig2.update_layout(
            **_LAYOUT,
            height=220,
            hovermode="x unified",
            yaxis=dict(**_AXIS, title_text="Band width difference (%)", title_font=dict(size=9)),
            xaxis=dict(**_AXIS),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=9)),
        )
        st.plotly_chart(fig2, use_container_width=True)

        direction = "wider" if H > 0.5 else "narrower"
        tail_n = TIMEFRAMES["tail"]["window"]
        scale_ratio = (tail_n / 252) ** H / (tail_n / 252) ** 0.5
        st.markdown(f"""
        <div style="font-family:'Fira Code',monospace;font-size:0.6rem;color:rgba(74,90,104,0.7);
        letter-spacing:0.06em;margin-top:0.3rem;">
            H={H:.3f} → Tail band is {direction} by ~{abs(scale_ratio - 1)*100:.1f}% vs classical model ·
            Positive = fractal model sees more risk than √T assumption
        </div>
        """, unsafe_allow_html=True)

    # ── Levels reference table ─────────────────────────────────────────────────
    st.markdown('<div class="section-label">Current Levels Reference</div>', unsafe_allow_html=True)

    table_rows = []
    for name, cfg in TIMEFRAMES.items():
        upper = last[f"{name}_upper"]
        lower = last[f"{name}_lower"]
        ma    = last[f"{name}_ma"]
        sig_label, _, sig_fg = get_signal(close_now, upper, lower, ma)
        dist_upper = (upper - close_now) / close_now * 100
        dist_lower = (close_now - lower) / close_now * 100
        table_rows.append({
            "Horizon":     f"{cfg['label']} ({cfg['window']}d)",
            "Support":     f"${lower:,.2f}",
            "Mid (MA)":    f"${ma:,.2f}",
            "Resistance":  f"${upper:,.2f}",
            "Signal":      sig_label,
            "To Resist.":  f"+{dist_upper:.2f}%",
            "To Support":  f"-{dist_lower:.2f}%",
        })

    st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

    st.markdown(f"""
    <div style="font-family:'Fira Code',monospace;font-size:0.56rem;color:rgba(74,90,104,0.45);
    text-align:right;margin-top:1.2rem;letter-spacing:0.06em;">
        {ticker} · H={H:.3f} · exponent={'H (fractal)' if use_hurst else '0.5 (classical)'} ·
        {len(df)} trading days · Not investment advice
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="text-align:center;padding:5rem 2rem;">
        <div style="font-family:'Bebas Neue',sans-serif;font-size:6rem;letter-spacing:0.05em;
        color:rgba(240,165,0,0.08);line-height:1;margin-bottom:0.5rem;">RANGE</div>
        <div style="font-family:'Fira Code',monospace;font-size:0.65rem;letter-spacing:0.2em;
        text-transform:uppercase;color:rgba(240,165,0,0.25);">
            Enter a ticker and click Analyze
        </div>
        <div style="font-family:'Lora',serif;font-style:italic;font-size:0.78rem;
        color:rgba(74,90,104,0.35);margin-top:0.8rem;">
            Stocks · ETFs · Crypto (BTC-USD) · Canadian stocks (RY.TO)
        </div>
    </div>
    """, unsafe_allow_html=True)

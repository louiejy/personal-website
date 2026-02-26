import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import time
import re
import xml.etree.ElementTree as ET
import urllib.parse
from datetime import datetime, timedelta

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EDGAR Peer Lens",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500&display=swap');

:root {
    --bg: #0E1117;
    --bg-card: #161B25;
    --bg-muted: #1C2333;
    --navy: #162447;
    --gold: #C9A84C;
    --gold-muted: rgba(201,168,76,0.15);
    --text: #E8E4DA;
    --text-muted: #8A8A8A;
    --border: rgba(201,168,76,0.2);
    --green: #4CAF82;
    --red: #CF6679;
}

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp { background-color: var(--bg) !important; }

/* Hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* App header */
.app-header {
    padding: 2.5rem 0 1.5rem 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2rem;
}
.app-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.8rem;
    font-weight: 600;
    color: var(--text);
    letter-spacing: -0.02em;
    line-height: 1;
    margin: 0;
}
.app-subtitle {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: var(--gold);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 0.5rem;
}

/* Input section */
.stTextInput > div > div > input {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    color: var(--text) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.85rem !important;
    padding: 0.6rem 0.8rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 2px var(--gold-muted) !important;
}
.stTextInput label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
}

/* Button */
.stButton > button {
    background: var(--gold) !important;
    color: #0E1117 !important;
    border: none !important;
    border-radius: 3px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    padding: 0.6rem 2rem !important;
    transition: opacity 0.2s ease !important;
}
.stButton > button:hover {
    opacity: 0.85 !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* Metric cards */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.75rem;
}
.metric-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.3rem;
}
.metric-value {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 1.6rem;
    font-weight: 500;
    color: var(--text);
    line-height: 1;
}
.metric-sub {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    color: var(--text-muted);
    margin-top: 0.3rem;
}

/* Section labels */
.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--gold);
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.5rem;
    margin: 2rem 0 1.2rem 0;
}

/* Company badge */
.company-badge {
    display: inline-block;
    background: var(--gold-muted);
    border: 1px solid var(--border);
    border-radius: 3px;
    padding: 0.2rem 0.6rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: var(--gold);
    letter-spacing: 0.05em;
    margin-right: 0.4rem;
    margin-bottom: 0.4rem;
}

/* Dataframe overrides */
.stDataFrame { border: 1px solid var(--border) !important; border-radius: 4px !important; }

/* Selectbox */
.stSelectbox > div > div {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
}
.stSelectbox label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
}

/* Info/warning */
.stAlert {
    background: var(--bg-muted) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
}

/* Spinner */
.stSpinner > div { border-top-color: var(--gold) !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
    background: transparent !important;
    border: none !important;
    padding: 0.6rem 1.2rem !important;
}
.stTabs [aria-selected="true"] {
    color: var(--gold) !important;
    border-bottom: 2px solid var(--gold) !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
HEADERS = {"User-Agent": "Justin Louie edgar-peer-lens@gmail.com"}
BASE_URL = "https://data.sec.gov"

METRICS = {
    "Revenue": [
        "Revenues",
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "SalesRevenueNet",
        "RevenueFromContractWithCustomerIncludingAssessedTax",
        "SalesRevenueGoodsNet",
    ],
    "Gross Profit": ["GrossProfit"],
    "Operating Income": ["OperatingIncomeLoss"],
    "Net Income": ["NetIncomeLoss", "ProfitLoss"],
    "Total Assets": ["Assets"],
    "Total Liabilities": ["Liabilities"],
    "Stockholders Equity": [
        "StockholdersEquity",
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
    ],
    "Cash & Equivalents": [
        "CashAndCashEquivalentsAtCarryingValue",
        "CashCashEquivalentsAndShortTermInvestments",
        "Cash",
    ],
    "Long-term Debt": ["LongTermDebt", "LongTermDebtNoncurrent"],
    "Operating Cash Flow": ["NetCashProvidedByUsedInOperatingActivities"],
    "R&D Expense": ["ResearchAndDevelopmentExpense"],
}

# ── SEC API helpers ───────────────────────────────────────────────────────────
@st.cache_data(ttl=86400, show_spinner=False)
def load_ticker_map():
    url = "https://www.sec.gov/files/company_tickers.json"
    r = requests.get(url, headers=HEADERS, timeout=15)
    data = r.json()
    return {
        v["ticker"]: {"cik": str(v["cik_str"]).zfill(10), "name": v["title"]}
        for v in data.values()
    }


@st.cache_data(ttl=3600, show_spinner=False)
def get_company_facts(cik: str):
    url = f"{BASE_URL}/api/xbrl/companyfacts/CIK{cik}.json"
    r = requests.get(url, headers=HEADERS, timeout=15)
    if r.status_code == 200:
        return r.json()
    return None


@st.cache_data(ttl=3600, show_spinner=False)
def get_company_info(cik: str):
    url = f"{BASE_URL}/submissions/CIK{cik}.json"
    r = requests.get(url, headers=HEADERS, timeout=15)
    if r.status_code == 200:
        return r.json()
    return None


def extract_annual_series(facts, concept):
    """Return list of (fiscal_year_end_date, value) for annual 10-K filings."""
    try:
        units = facts["facts"]["us-gaap"][concept]["units"]
        for unit_type in ["USD", "shares"]:
            if unit_type not in units:
                continue
            rows = [
                d for d in units[unit_type]
                if d.get("form") == "10-K" and d.get("fp") == "FY"
            ]
            if not rows:
                continue
            seen = {}
            for d in rows:
                year = d["end"][:4]
                seen[year] = (d["end"], d["val"])
            series = sorted(seen.values(), key=lambda x: x[0])
            return series
    except (KeyError, TypeError):
        pass
    return []


def get_latest_annual(facts, concepts):
    best_date, best_val = None, None
    for concept in concepts:
        series = extract_annual_series(facts, concept)
        if series:
            date, val = series[-1]
            if best_date is None or date > best_date:
                best_date, best_val = date, val
    return best_val, best_date


def get_historical(facts, concepts, n_years=5):
    best_series = []
    for concept in concepts:
        series = extract_annual_series(facts, concept)
        if series and (not best_series or series[-1][0] > best_series[-1][0]):
            best_series = series
    return best_series[-n_years:] if best_series else []


def fmt(val, unit="USD"):
    if val is None:
        return "—"
    if unit == "USD":
        if abs(val) >= 1e12:
            return f"${val/1e12:.2f}T"
        if abs(val) >= 1e9:
            return f"${val/1e9:.1f}B"
        if abs(val) >= 1e6:
            return f"${val/1e6:.0f}M"
        return f"${val:,.0f}"
    return f"{val:,.0f}"


def pct(numerator, denominator):
    if numerator is None or denominator is None or denominator == 0:
        return None
    return numerator / denominator * 100


# ── Plotly theme ──────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="IBM Plex Sans", color="#E8E4DA", size=12),
    xaxis=dict(
        gridcolor="rgba(201,168,76,0.08)",
        linecolor="rgba(201,168,76,0.2)",
        tickfont=dict(family="IBM Plex Mono", size=10),
    ),
    yaxis=dict(
        gridcolor="rgba(201,168,76,0.08)",
        linecolor="rgba(201,168,76,0.2)",
        tickfont=dict(family="IBM Plex Mono", size=10),
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor="rgba(201,168,76,0.2)",
        borderwidth=1,
        font=dict(family="IBM Plex Mono", size=10),
    ),
    margin=dict(l=0, r=0, t=30, b=0),
)

GOLD_PALETTE = [
    "#C9A84C", "#4CAF82", "#CF6679", "#7B9FD4", "#D4A5CF",
    "#F0C27F", "#6BCFB8", "#E88C8C",
]

@st.cache_data(ttl=1800, show_spinner=False)
def search_edgar(query: str, forms: str, days_back: int = 180) -> list:
    """Search EDGAR full-text search API. Returns list of hit _source dicts."""
    from datetime import datetime, timedelta
    end = datetime.today()
    start = end - timedelta(days=days_back)
    url = (
        f"https://efts.sec.gov/LATEST/search-index?"
        f"q={requests.utils.quote(query)}"
        f"&forms={requests.utils.quote(forms)}"
        f"&dateRange=custom"
        f"&startdt={start.strftime('%Y-%m-%d')}"
        f"&enddt={end.strftime('%Y-%m-%d')}"
    )
    r = requests.get(url, headers=HEADERS, timeout=15)
    if r.status_code == 200:
        return r.json().get("hits", {}).get("hits", [])
    return []


# ── Smart monitor (RSS-based, mirrors edgar_monitor.py logic) ─────────────────

HIGH_SIGNAL_FORMS = {
    "10-12B":    ("Spinoff Registration",          "New company being formally registered as a spinoff."),
    "10-12B/A":  ("Spinoff Registration Amendment","Amendment to an existing spinoff registration."),
    "DEFM14A":   ("Merger Proxy (Definitive)",     "Shareholders are voting on a merger — deal is late stage."),
    "PREM14A":   ("Merger Proxy (Preliminary)",    "Early-stage merger proxy — deal not yet definitive."),
    "SC 13E-3":  ("Going Private",                 "Company being taken private — classic Greenblatt stub situation."),
    "SC 13E-3/A":("Going Private Amendment",       "Amendment to a going-private filing."),
    "SC TO-T":   ("Tender Offer",                  "Third party launching a tender offer on a target's shares."),
    "SC TO-T/A": ("Tender Offer Amendment",        "Amendment to a tender offer — price or terms changed."),
    "SC 14D9":   ("Tender Offer Response",         "Target company's board response to a tender offer."),
}

RELEVANT_8K_ITEMS = {
    "1.01": ("Material Agreement",        "Entry into a material M&A or definitive agreement."),
    "1.02": ("Agreement Terminated",      "Termination of a material agreement — deal fell through."),
    "1.03": ("Bankruptcy / Receivership", "Company filing for or entering bankruptcy."),
    "2.01": ("Acquisition / Disposition", "Spinoff or asset sale completed — entity has changed hands."),
    "3.03": ("Rights Modification",       "Material modification to shareholder rights."),
}

ITEM_EMOJI = {
    "1.01": "📝", "1.02": "❌", "1.03": "⚠️", "2.01": "✅", "3.03": "🔒",
}


@st.cache_data(ttl=900, show_spinner=False)
def get_recent_filings_rss(form_type: str, count: int = 40) -> list:
    """Fetch recent filings from SEC EDGAR RSS/Atom feed."""
    params = {
        "action": "getcurrent", "type": form_type,
        "company": "", "dateb": "", "owner": "include",
        "count": str(count), "output": "atom",
    }
    url = f"https://www.sec.gov/cgi-bin/browse-edgar?{urllib.parse.urlencode(params)}"
    r = requests.get(url, headers=HEADERS, timeout=15)
    if r.status_code != 200:
        return []
    root = ET.fromstring(r.content)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    filings = []
    for entry in root.findall("atom:entry", ns):
        title_el = entry.find("atom:title", ns)
        link_el  = entry.find("atom:link", ns)
        upd_el   = entry.find("atom:updated", ns)
        title   = title_el.text or "" if title_el is not None else ""
        link    = link_el.get("href", "") if link_el is not None else ""
        updated = upd_el.text or "" if upd_el is not None else ""
        m = re.match(r"(.+?) - (.+?) \((\d+)\) \((.+?)\)", title)
        if m:
            filings.append({
                "form_type":        m.group(1).strip(),
                "company_name":     m.group(2).strip(),
                "cik":              m.group(3).strip(),
                "accession_number": m.group(4).strip(),
                "filing_url":       link,
                "filed_date":       updated[:10],
            })
    return filings


@st.cache_data(ttl=3600, show_spinner=False)
def get_8k_items_cached(filing_url: str) -> list:
    """Fetch an 8-K filing index and extract Item numbers from the document."""
    try:
        r = requests.get(filing_url, headers=HEADERS, timeout=12)
        # Find the primary .htm document
        doc_match = re.search(r'href="(/Archives/edgar/data/[^"]+\.htm)"', r.text)
        if doc_match:
            doc_url = "https://www.sec.gov" + doc_match.group(1)
            r2 = requests.get(doc_url, headers=HEADERS, timeout=12)
            matches = re.findall(r"Item\s+(\d+\.\d+)", r2.text, re.IGNORECASE)
            return sorted(set(matches))
    except Exception:
        pass
    return []


def run_smart_monitor(days_back: int, check_8ks: bool = True):
    """
    Run the smart monitor: RSS for high-signal forms + item-level 8-K filtering.
    Returns dict keyed by category with lists of filing dicts.
    """
    cutoff = (datetime.today() - timedelta(days=days_back)).date()
    results = {cat: [] for cat in ["spinoffs", "going_private", "mergers", "tender_offers", "bankruptcy_8k", "acquisition_8k", "agreement_8k"]}

    # ── High-signal forms via RSS ──────────────────────────────────────────────
    for form_type, (label, desc) in HIGH_SIGNAL_FORMS.items():
        raw = get_recent_filings_rss(form_type, count=40)
        for f in raw:
            if f["filed_date"] < str(cutoff):
                continue
            f["label"] = label
            f["description"] = desc
            f["form_type"] = form_type
            if "10-12B" in form_type:
                results["spinoffs"].append(f)
            elif "13E-3" in form_type:
                results["going_private"].append(f)
            elif "14A" in form_type:
                results["mergers"].append(f)
            elif "TO-T" in form_type or "TO-T/A" in form_type:
                results["tender_offers"].append(f)
            elif "14D9" in form_type:
                results["tender_offers"].append(f)
        time.sleep(0.15)

    # ── 8-Ks: fetch and read item numbers ─────────────────────────────────────
    if check_8ks:
        raw_8ks = get_recent_filings_rss("8-K", count=60)
        recent_8ks = [f for f in raw_8ks if f["filed_date"] >= str(cutoff)]
        for i, f in enumerate(recent_8ks):
            yield ("progress", i, len(recent_8ks), f["company_name"])
            items = get_8k_items_cached(f["filing_url"])
            relevant = [it for it in items if it in RELEVANT_8K_ITEMS]
            if not relevant:
                time.sleep(0.12)
                continue
            for item in relevant:
                name, desc = RELEVANT_8K_ITEMS[item]
                entry = {**f, "item": item, "label": f"{ITEM_EMOJI.get(item, '📄')} Item {item} — {name}", "description": desc}
                if item == "1.03":
                    results["bankruptcy_8k"].append(entry)
                elif item == "2.01":
                    results["acquisition_8k"].append(entry)
                elif item in ("1.01", "1.02", "3.03"):
                    results["agreement_8k"].append(entry)
            time.sleep(0.12)

    yield ("done", results)


def render_smart_table(filings: list, label: str, greenblatt_note: str):
    """Render a categorized results table."""
    st.markdown(f"""
    <div style="background:rgba(201,168,76,0.07);border:1px solid rgba(201,168,76,0.25);
    border-radius:4px;padding:0.8rem 1rem;margin-bottom:1rem;">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;letter-spacing:0.12em;
        text-transform:uppercase;color:#C9A84C;">{label}</div>
        <div style="font-family:'IBM Plex Sans',sans-serif;font-size:0.8rem;
        color:rgba(232,228,218,0.6);margin-top:0.25rem;">{greenblatt_note}</div>
    </div>
    """, unsafe_allow_html=True)

    if not filings:
        st.markdown('<div style="color:rgba(138,138,138,0.5);font-size:0.8rem;padding:0.4rem 0 1rem;">No filings in this window.</div>', unsafe_allow_html=True)
        return

    rows = []
    for f in filings[:20]:
        cik_str = f.get("cik", "").lstrip("0")
        accn = f.get("accession_number", "").replace("-", "")
        if cik_str and accn and len(accn) == 18 and accn.isdigit():
            url = f"https://www.sec.gov/Archives/edgar/data/{cik_str}/{accn}/"
        else:
            url = f.get("filing_url", "")
        rows.append({
            "Company":    f.get("company_name", "")[:45],
            "Form":       f.get("form_type", ""),
            "Signal":     f.get("label", ""),
            "Filed":      f.get("filed_date", ""),
            "Filing":     url,
        })

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
        column_config={"Filing": st.column_config.LinkColumn("Filing", display_text="View on EDGAR")},
    )


def filing_url(adsh: str) -> str:
    """Convert accession number to EDGAR filing index URL."""
    clean = adsh.replace("-", "")
    cik = clean[:10].lstrip("0")
    return f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=&dateb=&owner=include&count=40&search_text="


def build_filing_url(adsh: str, ciks: list) -> str:
    """Build direct EDGAR filing index URL from accession number and CIK list."""
    adsh_no_dashes = adsh.replace("-", "")
    cik = str(ciks[0]).lstrip("0") if ciks else adsh_no_dashes[:10].lstrip("0")
    return f"https://www.sec.gov/Archives/edgar/data/{cik}/{adsh_no_dashes}/"


def render_filing_cards(hits: list, event_type: str, description: str):
    """Render a list of EDGAR hits as a table with clickable filing links."""
    import re
    st.markdown(f"""
    <div style="
        background: rgba(201,168,76,0.07);
        border: 1px solid rgba(201,168,76,0.25);
        border-radius: 4px;
        padding: 0.8rem 1rem;
        margin-bottom: 1.2rem;
    ">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;letter-spacing:0.12em;text-transform:uppercase;color:#C9A84C;">{event_type}</div>
        <div style="font-family:'IBM Plex Sans',sans-serif;font-size:0.8rem;color:rgba(232,228,218,0.6);margin-top:0.2rem;">{description}</div>
    </div>
    """, unsafe_allow_html=True)

    if not hits:
        st.markdown('<div style="color:rgba(138,138,138,0.5);font-size:0.8rem;padding:0.5rem 0;">No recent filings found.</div>', unsafe_allow_html=True)
        return

    rows = []
    for h in hits[:15]:
        s = h.get("_source", {})
        names = s.get("display_names", [])
        company = names[0].split("(")[0].strip() if names else "Unknown"
        ticker_raw = names[0] if names else ""
        m = re.search(r'\(([A-Z]{1,5})\)', ticker_raw)
        ticker_display = m.group(1) if m else "—"
        adsh = s.get("adsh", "")
        ciks = s.get("ciks", [])
        rows.append({
            "Ticker": ticker_display,
            "Company": company[:45],
            "Form": s.get("form", s.get("root_forms", [""])[0] if s.get("root_forms") else ""),
            "Filed": s.get("file_date", "")[:10],
            "Filing": build_filing_url(adsh, ciks),
        })

    table_df = pd.DataFrame(rows)
    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Filing": st.column_config.LinkColumn("Filing", display_text="View on EDGAR"),
        },
    )


def hex_to_rgba(hex_color: str, alpha: float = 0.12) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <p class="app-title">EDGAR Peer Lens</p>
    <p class="app-subtitle">SEC Filing Competitor Intelligence · Powered by EDGAR Public API</p>
</div>
""", unsafe_allow_html=True)

# ── Top-level navigation ───────────────────────────────────────────────────────
main_tab2, main_tab1 = st.tabs(["Special Situations", "Peer Comparison"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Peer Comparison
# ══════════════════════════════════════════════════════════════════════════════
with main_tab1:

    # ── Input row ──────────────────────────────────────────────────────────────
    col_a, col_b, col_c = st.columns([1.2, 2.5, 0.8])

    with col_a:
        primary = st.text_input("Primary Ticker", value="AAPL", placeholder="e.g. AAPL").strip().upper()

    with col_b:
        peers_raw = st.text_input("Competitor Tickers", value="MSFT, GOOGL, AMZN, META", placeholder="e.g. MSFT, GOOGL, AMZN")

    with col_c:
        st.markdown("<div style='height:1.9rem'></div>", unsafe_allow_html=True)
        run = st.button("Run Analysis", type="primary", use_container_width=True)

    # ── Analysis ───────────────────────────────────────────────────────────────
    if run:
        all_tickers = [primary] + [t.strip().upper() for t in peers_raw.split(",")]
        all_tickers = list(dict.fromkeys([t for t in all_tickers if t]))

        with st.spinner("Loading SEC EDGAR data..."):
            ticker_map = load_ticker_map()

        company_data = {}
        not_found = []

        progress = st.progress(0, text="Fetching filings...")
        for i, ticker in enumerate(all_tickers):
            progress.progress((i + 1) / len(all_tickers), text=f"Fetching {ticker}...")
            if ticker not in ticker_map:
                not_found.append(ticker)
                continue
            meta = ticker_map[ticker]
            cik = meta["cik"]
            facts = get_company_facts(cik)
            info = get_company_info(cik)
            if facts:
                company_data[ticker] = {
                    "name": meta["name"],
                    "cik": cik,
                    "facts": facts,
                    "sic": info.get("sic", "—") if info else "—",
                    "sic_desc": info.get("sicDescription", "—") if info else "—",
                    "fiscal_year_end": info.get("fiscalYearEnd", "—") if info else "—",
                    "state": info.get("stateOfIncorporation", "—") if info else "—",
                }
            time.sleep(0.12)

        progress.empty()

        if not_found:
            st.warning(f"Not found in SEC database: {', '.join(not_found)}")

        if not company_data:
            st.error("No data retrieved. Check tickers and try again.")
            st.stop()

        # ── Company badges ──
        st.markdown('<div class="section-label">Companies</div>', unsafe_allow_html=True)
        badges = "".join(
            f'<span class="company-badge">{t} — {d["name"][:35]}</span>'
            for t, d in company_data.items()
        )
        st.markdown(badges, unsafe_allow_html=True)

        # ── Build summary dataframe ──
        rows = []
        for ticker, d in company_data.items():
            row = {"Ticker": ticker, "Company": d["name"][:40], "Industry": d["sic_desc"]}
            for metric, concepts in METRICS.items():
                val, date = get_latest_annual(d["facts"], concepts)
                row[metric] = val
                row[f"_date_{metric}"] = date
            rows.append(row)

        df = pd.DataFrame(rows)

        def safe_ratio(df, num_col, den_col):
            return df.apply(lambda r: pct(r.get(num_col), r.get(den_col)), axis=1)

        df["Gross Margin %"] = safe_ratio(df, "Gross Profit", "Revenue")
        df["Operating Margin %"] = safe_ratio(df, "Operating Income", "Revenue")
        df["Net Margin %"] = safe_ratio(df, "Net Income", "Revenue")
        df["Debt/Equity"] = df.apply(
            lambda r: round(r["Long-term Debt"] / r["Stockholders Equity"], 2)
            if r["Long-term Debt"] and r["Stockholders Equity"] and r["Stockholders Equity"] != 0
            else None, axis=1
        )

        # ── Sub-tabs ──
        tab1, tab2, tab3 = st.tabs(["Overview", "Detailed Metrics", "Historical Trends"])

        # ─ Overview ──────────────────────────────────────────────────────────
        with tab1:
            st.markdown('<div class="section-label">Revenue Comparison (Most Recent FY)</div>', unsafe_allow_html=True)

            rev_df = df[["Ticker", "Revenue"]].dropna(subset=["Revenue"]).copy()
            rev_df = rev_df.sort_values("Revenue", ascending=False)

            if not rev_df.empty:
                fig_rev = go.Figure(go.Bar(
                    x=rev_df["Ticker"],
                    y=rev_df["Revenue"] / 1e9,
                    marker_color=[GOLD_PALETTE[i % len(GOLD_PALETTE)] for i in range(len(rev_df))],
                    text=[fmt(v) for v in rev_df["Revenue"]],
                    textposition="outside",
                    textfont=dict(family="IBM Plex Mono", size=10, color="#E8E4DA"),
                ))
                fig_rev.update_layout(
                    **PLOTLY_LAYOUT,
                    yaxis_title="USD (Billions)",
                    height=320,
                    showlegend=False,
                )
                st.plotly_chart(fig_rev, use_container_width=True)

            st.markdown('<div class="section-label">Margin Profile</div>', unsafe_allow_html=True)

            margin_tickers = df["Ticker"].tolist()
            margin_fig = go.Figure()
            for col, label in [("Gross Margin %", "Gross"), ("Operating Margin %", "Operating"), ("Net Margin %", "Net")]:
                vals = df[col].tolist()
                margin_fig.add_trace(go.Bar(
                    name=label,
                    x=margin_tickers,
                    y=vals,
                    text=[f"{v:.1f}%" if v is not None else "—" for v in vals],
                    textposition="outside",
                    textfont=dict(family="IBM Plex Mono", size=9),
                ))
            margin_fig.update_layout(
                **PLOTLY_LAYOUT,
                barmode="group",
                yaxis_title="Margin (%)",
                height=320,
            )
            st.plotly_chart(margin_fig, use_container_width=True)

            primary_row = df[df["Ticker"] == primary]
            if not primary_row.empty:
                pr = primary_row.iloc[0]
                st.markdown(f'<div class="section-label">{primary} — Snapshot</div>', unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns(4)
                snapshot = [
                    ("Revenue", fmt(pr.get("Revenue")), pr.get("_date_Revenue", "")[:4] if pr.get("_date_Revenue") else ""),
                    ("Net Income", fmt(pr.get("Net Income")), pr.get("_date_Net Income", "")[:4] if pr.get("_date_Net Income") else ""),
                    ("Total Assets", fmt(pr.get("Total Assets")), ""),
                    ("Net Margin", f"{pr['Net Margin %']:.1f}%" if pr.get("Net Margin %") else "—", ""),
                ]
                for col_widget, (label, val, sub) in zip([c1, c2, c3, c4], snapshot):
                    with col_widget:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">{label}</div>
                            <div class="metric-value">{val}</div>
                            <div class="metric-sub">{sub}</div>
                        </div>
                        """, unsafe_allow_html=True)

        # ─ Detailed Metrics ───────────────────────────────────────────────────
        with tab2:
            st.markdown('<div class="section-label">Full Metrics Table (Most Recent Annual Filing)</div>', unsafe_allow_html=True)

            display_cols = ["Ticker", "Company"] + list(METRICS.keys()) + ["Gross Margin %", "Operating Margin %", "Net Margin %", "Debt/Equity"]
            display_df = df[[c for c in display_cols if c in df.columns]].copy()

            for metric in METRICS.keys():
                if metric in display_df.columns:
                    display_df[metric] = display_df[metric].apply(fmt)

            for pct_col in ["Gross Margin %", "Operating Margin %", "Net Margin %"]:
                if pct_col in display_df.columns:
                    display_df[pct_col] = display_df[pct_col].apply(
                        lambda x: f"{x:.1f}%" if x is not None else "—"
                    )

            if "Debt/Equity" in display_df.columns:
                display_df["Debt/Equity"] = display_df["Debt/Equity"].apply(
                    lambda x: f"{x:.2f}x" if x is not None else "—"
                )

            st.dataframe(
                display_df.set_index("Ticker"),
                use_container_width=True,
                height=min(60 + len(display_df) * 55, 500),
            )

            st.markdown('<div class="section-label">Relative Strength Radar</div>', unsafe_allow_html=True)

            radar_metrics = ["Revenue", "Gross Profit", "Operating Income", "Net Income", "Operating Cash Flow"]
            radar_df = df[["Ticker"] + radar_metrics].copy()

            for m in radar_metrics:
                max_val = radar_df[m].max()
                if max_val and max_val != 0:
                    radar_df[m] = radar_df[m] / max_val
                else:
                    radar_df[m] = 0

            fig_radar = go.Figure()
            for i, (_, row) in enumerate(radar_df.iterrows()):
                vals = [row[m] if row[m] is not None else 0 for m in radar_metrics]
                vals_closed = vals + [vals[0]]
                fig_radar.add_trace(go.Scatterpolar(
                    r=vals_closed,
                    theta=radar_metrics + [radar_metrics[0]],
                    fill="toself",
                    name=row["Ticker"],
                    line_color=GOLD_PALETTE[i % len(GOLD_PALETTE)],
                    fillcolor=hex_to_rgba(GOLD_PALETTE[i % len(GOLD_PALETTE)], 0.12),
                    opacity=0.85,
                ))

            fig_radar.update_layout(
                **PLOTLY_LAYOUT,
                polar=dict(
                    bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(visible=True, range=[0, 1], color="rgba(201,168,76,0.3)", tickfont=dict(size=8)),
                    angularaxis=dict(color="#E8E4DA", tickfont=dict(family="IBM Plex Mono", size=10)),
                ),
                height=420,
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        # ─ Historical Trends ──────────────────────────────────────────────────
        with tab3:
            st.markdown('<div class="section-label">Historical Trend (5-Year Annual)</div>', unsafe_allow_html=True)

            trend_metric = st.selectbox("Metric", list(METRICS.keys()), index=0)

            fig_trend = go.Figure()
            for i, (ticker, d) in enumerate(company_data.items()):
                series = get_historical(d["facts"], METRICS[trend_metric], n_years=6)
                if not series:
                    continue
                dates = [s[0][:4] for s in series]
                vals = [s[1] / 1e9 for s in series]
                fig_trend.add_trace(go.Scatter(
                    x=dates,
                    y=vals,
                    mode="lines+markers",
                    name=ticker,
                    line=dict(color=GOLD_PALETTE[i % len(GOLD_PALETTE)], width=2),
                    marker=dict(size=6, symbol="circle"),
                ))

            fig_trend.update_layout(
                **PLOTLY_LAYOUT,
                yaxis_title="USD (Billions)",
                height=380,
                hovermode="x unified",
            )
            st.plotly_chart(fig_trend, use_container_width=True)

            if primary in company_data:
                st.markdown(f'<div class="section-label">{primary} — Recent SEC Filings</div>', unsafe_allow_html=True)
                cik_raw = company_data[primary]["cik"].lstrip("0")
                info = get_company_info(company_data[primary]["cik"])
                if info and "filings" in info:
                    filings_data = info["filings"].get("recent", {})
                    if filings_data:
                        filing_df = pd.DataFrame({
                            "Form": filings_data.get("form", []),
                            "Filed": filings_data.get("filingDate", []),
                            "Description": filings_data.get("primaryDocument", []),
                        }).head(10)
                        filing_df = filing_df[filing_df["Form"].isin(["10-K", "10-Q", "8-K", "DEF 14A"])]
                        st.dataframe(filing_df, use_container_width=True, hide_index=True)

                st.markdown(
                    f"[View all {primary} filings on EDGAR →](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik_raw}&type=10-K&dateb=&owner=include&count=10)",
                )

    else:
        st.markdown("""
        <div style="
            text-align:center;
            padding: 5rem 2rem;
            color: rgba(138,138,138,0.6);
        ">
            <div style="font-family:'Cormorant Garamond',serif; font-size:3rem; color:rgba(201,168,76,0.3); margin-bottom:1rem;">⬡</div>
            <div style="font-family:'IBM Plex Mono',monospace; font-size:0.75rem; letter-spacing:0.15em; text-transform:uppercase;">
                Enter tickers and run analysis to begin
            </div>
            <div style="font-family:'IBM Plex Sans',sans-serif; font-size:0.85rem; color:rgba(138,138,138,0.5); margin-top:0.75rem;">
                Data sourced from SEC EDGAR · Free public API · No key required
            </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Special Situations
# ══════════════════════════════════════════════════════════════════════════════
with main_tab2:
    st.markdown("""
    <div style="font-family:'IBM Plex Sans',sans-serif;font-size:0.85rem;color:rgba(232,228,218,0.6);
    line-height:1.6;border-left:2px solid rgba(201,168,76,0.4);padding-left:1rem;margin-bottom:2rem;">
        Based on Joel Greenblatt's <em>You Can Be a Stock Market Genius</em>. Uses SEC RSS feeds for
        high-signal form types, then reads each 8-K's content to extract specific Item numbers —
        the same logic as a production filing monitor.
    </div>
    """, unsafe_allow_html=True)

    ss_col1, ss_col2, ss_col3 = st.columns([1, 1, 2])
    with ss_col1:
        days_filter = st.selectbox("Lookback window", [1, 5, 10, 15], index=0, format_func=lambda x: f"Past {x} day" if x == 1 else f"Past {x} days")
    with ss_col2:
        check_8ks = st.toggle("Read 8-K content", value=True, help="Fetches each 8-K to extract precise Item numbers. Slower but much more accurate.")
    with ss_col3:
        st.markdown("<div style='height:1.8rem'></div>", unsafe_allow_html=True)
        refresh_ss = st.button("Run Monitor", type="primary", use_container_width=True)

    if refresh_ss:
        results = {cat: [] for cat in ["spinoffs", "going_private", "mergers", "tender_offers", "bankruptcy_8k", "acquisition_8k", "agreement_8k"]}

        status_text = st.empty()
        progress_bar = st.progress(0)

        status_text.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.72rem;color:rgba(201,168,76,0.7);">Fetching high-signal forms via RSS...</div>', unsafe_allow_html=True)

        for event in run_smart_monitor(days_filter, check_8ks=check_8ks):
            if event[0] == "progress":
                _, idx, total, company = event
                pct = int((idx / total) * 100)
                progress_bar.progress(pct)
                status_text.markdown(f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.72rem;color:rgba(201,168,76,0.7);">Reading 8-K {idx}/{total} — {company[:40]}...</div>', unsafe_allow_html=True)
            elif event[0] == "done":
                results = event[1]

        progress_bar.empty()
        status_text.empty()

        # ── Results ───────────────────────────────────────────────────────────
        render_smart_table(
            results["spinoffs"],
            "Spinoffs (Form 10-12B / 10-12G)",
            "Greenblatt: Institutions are forced to sell spinoffs at separation — insiders own them. "
            "Historically among the most reliable sources of alpha."
        )
        render_smart_table(
            results["going_private"],
            "Going Private (SC 13E-3)",
            "Greenblatt: Management buying out public shareholders often signals deeply undervalued assets. "
            "Watch for stub equity opportunities."
        )
        render_smart_table(
            results["mergers"],
            "Merger Proxies (DEFM14A / PREM14A)",
            "Greenblatt: Merger arbitrage — definitive proxies signal late-stage deals with a measurable spread. "
            "Preliminary proxies are earlier and riskier."
        )
        render_smart_table(
            results["tender_offers"],
            "Tender Offers & Target Responses (SC TO-T / SC 14D9)",
            "Greenblatt: Buy the target at a spread to the offer price and collect when the deal closes. "
            "SC 14D9 shows whether the board is cooperating."
        )
        render_smart_table(
            results["bankruptcy_8k"],
            "Bankruptcy Filings (8-K Item 1.03)",
            "Greenblatt: Post-reorganization equity is systematically ignored by institutions. "
            "Emerging-from-bankruptcy companies can be deeply mispriced."
        )
        render_smart_table(
            results["acquisition_8k"],
            "Acquisitions & Dispositions Completed (8-K Item 2.01)",
            "Spinoff completions land here. The newly separated entity is often mispriced in its first weeks of trading."
        )
        render_smart_table(
            results["agreement_8k"],
            "Material Agreements & Terminations (8-K Items 1.01 / 1.02 / 3.03)",
            "Entry into or termination of material M&A agreements — early signal of deals forming or falling apart."
        )

        total_found = sum(len(v) for v in results.values())
        st.markdown(f"""
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.62rem;color:rgba(138,138,138,0.4);
        text-align:right;margin-top:1.5rem;letter-spacing:0.06em;">
            {total_found} filings found · SEC EDGAR RSS + Filing Content · Not investment advice
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <div style="text-align:center;padding:3rem 2rem;color:rgba(138,138,138,0.5);
        font-family:'IBM Plex Mono',monospace;font-size:0.72rem;letter-spacing:0.1em;text-transform:uppercase;">
            Select a lookback window and click "Run Monitor" to scan for corporate events
        </div>
        """, unsafe_allow_html=True)

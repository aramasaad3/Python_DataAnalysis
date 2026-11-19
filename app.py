"""
AI Landscape Dashboard
Python | Data Analysis and Visualization project

Data: Epoch AI (CC BY 4.0) - notable AI models, ML hardware, AI chip sales, GPU clusters,
data centers, benchmarks, capability index, AI company revenue and funding.
Run:  python -m streamlit run app.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="AI Landscape Dashboard", page_icon="📊", layout="wide",
                   initial_sidebar_state="expanded")
DATA = Path(__file__).parent / "data"

# ---------------------------------------------------------------- style
SURFACE, PAGE, INK, INK2, GRID, OTHER = "#ffffff", "#f5f5f2", "#0b0b0b", "#52514e", "#ebeae6", "#a3a29c"
# colour-blind-checked categorical order (blue, orange, aqua, yellow, magenta, green, violet, red)
S = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
DIVERGING = [[0, "#e34948"], [0.5, "#f0efec"], [1, "#2a78d6"]]
SEQUENTIAL = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]

st.markdown(
    f"""<style>
    .stApp {{background: {PAGE};}}
    .block-container {{padding-top: 3rem; padding-bottom: 3rem; max-width: 1320px;}}
    section[data-testid="stSidebar"] {{background: #ffffff; border-right: 1px solid {GRID};}}
    section[data-testid="stSidebar"] .block-container {{padding-top: 1.2rem;}}

    .brand {{display:flex; align-items:center; gap:12px; margin-bottom: 4px;}}
    .brand-mark {{width:40px; height:40px; border-radius:10px; display:grid; place-items:center;
                 background: linear-gradient(135deg, #2a78d6, #104281); color:#fff; font-weight:700;}}
    .brand-name {{font-weight:700; font-size:1.02rem; color:{INK}; line-height:1.2;}}
    .brand-sub {{font-size:.78rem; color:{INK2};}}
    .side-label {{font-size:.72rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase;
                 color:{INK2}; margin: 6px 0 2px;}}
    .badge {{display:inline-block; font-size:.72rem; font-weight:600; padding:2px 9px; border-radius:999px;
            background:#e7f0fb; color:#1c5cab; margin-left:6px; vertical-align:middle;}}
    .badge.off {{background:#f0efec; color:{INK2};}}
    .side-foot {{font-size:.75rem; color:{INK2}; line-height:1.5;}}

    .hero {{border-radius:18px; padding:26px 30px; color:#fff; margin-bottom:14px;
           background: radial-gradient(1200px 300px at 85% -40%, #2a78d6 0%, rgba(42,120,214,0) 60%),
                       linear-gradient(135deg, #0d1b2e 0%, #0f2a4a 100%);}}
    .hero .eyebrow {{font-size:.72rem; letter-spacing:.14em; text-transform:uppercase; color:#9ec5f4; font-weight:600;}}
    .hero h1 {{color:#fff; font-size:2.1rem; margin:.25rem 0 .35rem; padding:0; font-weight:700; letter-spacing:-.02em;}}
    .hero p {{color:#c9d6e6; margin:0 0 14px; font-size:.95rem;}}
    .chip {{display:inline-block; padding:5px 12px; margin:0 6px 6px 0; border-radius:999px; font-size:.8rem;
           background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.16); color:#e6eef8;}}

    .question {{background:#fff; border:1px solid {GRID}; border-left:4px solid #eda100; border-radius:12px;
               padding:14px 18px; margin-bottom:22px; display:flex; gap:16px; align-items:flex-start;}}
    .question .tag {{flex:none; font-size:.7rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase;
                    background:#fdf1d6; color:#8a5a00; padding:4px 10px; border-radius:6px; margin-top:2px;}}
    .question .text {{color:{INK}; font-size:1rem; line-height:1.5;}}

    .sec-head {{margin: 4px 0 14px;}}
    .sec-head .num {{font-size:.72rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:#2a78d6;}}
    .sec-head h2 {{margin:.15rem 0 .2rem; padding:0; font-size:1.55rem; font-weight:700; color:{INK};}}
    .sec-head p {{margin:0; color:{INK2};}}

    [data-testid="stMetric"] {{background:#fff; border:1px solid {GRID}; border-radius:12px; padding:14px 16px;}}
    [data-testid="stMetricLabel"] p {{font-size:.78rem; text-transform:uppercase; letter-spacing:.05em;
                                      font-weight:600; color:{INK2};}}
    [data-testid="stMetricValue"] {{font-size:1.6rem; font-weight:700;}}

    [class*="st-key-card"] {{background:#fff; border-radius:14px;}}
    .fig-tag {{display:inline-block; font-size:.68rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase;
              color:#1c5cab; background:#e7f0fb; padding:3px 9px; border-radius:6px; margin-bottom:8px;}}
    .fig-title {{font-size:1.12rem; font-weight:700; color:{INK}; line-height:1.3;}}
    .fig-sub {{font-size:.85rem; color:{INK2}; margin-top:2px;}}

    .drivers {{display:grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap:14px; margin-bottom:16px;}}
    .driver {{background:#fff; border:1px solid {GRID}; border-radius:14px; padding:18px 20px;}}
    .driver .k {{font-size:.72rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; color:{INK2};}}
    .driver .v {{font-size:clamp(1.5rem, 2.4vw, 2.2rem); font-weight:700; color:{INK}; margin:.2rem 0 .1rem;
                white-space:nowrap;}}
    .driver .v small {{font-size:.55em; font-weight:600; color:{INK2};}}
    .driver .d {{font-size:.88rem; color:{INK2}; line-height:1.45;}}
    .driver.win {{border:2px solid #2a78d6;}}
    .driver.win .k {{color:#1c5cab;}}
    .verdict {{background:#0f2a4a; color:#e6eef8; border-radius:14px; padding:20px 24px; margin-bottom:18px;
              font-size:1.02rem; line-height:1.6;}}
    .verdict b {{color:#fff;}}
    .verdict .tag {{font-size:.7rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:#9ec5f4;
                   display:block; margin-bottom:6px;}}
    @media (max-width: 900px) {{ .drivers {{grid-template-columns: 1fr;}} }}
    </style>""",
    unsafe_allow_html=True,
)


def style(fig, height=400, legend=True):
    fig.update_layout(
        template="plotly_white", height=height,
        paper_bgcolor=SURFACE, plot_bgcolor=SURFACE,
        font=dict(family="Segoe UI, Inter, system-ui, sans-serif", size=13, color=INK2),
        margin=dict(l=8, r=8, t=36, b=8),
        hoverlabel=dict(bgcolor="white", font_size=13, bordercolor=GRID),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0, title_text=""),
        showlegend=legend,
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False, linecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, zeroline=False, linecolor=GRID)
    return fig


def card(num):
    return st.container(border=True, key=f"card{num}")


def card_title(num, kind, title, subtitle):
    st.markdown(
        f'<div class="fig-tag">Figure {num:02d} · {kind}</div>'
        f'<div class="fig-title">{title}</div><div class="fig-sub">{subtitle}</div>',
        unsafe_allow_html=True)


def section_head(num, title, question):
    st.markdown(f'<div class="sec-head"><div class="num">Section {num} of 5</div>'
                f'<h2>{title}</h2><p>{question}</p></div>', unsafe_allow_html=True)


def show(fig, scroll_zoom=True):
    st.plotly_chart(fig, width="stretch", config={"displaylogo": False, "scrollZoom": scroll_zoom})


def nothing():
    st.info("No data matches these filters. Widen the filters in the sidebar.")


def sci(x):
    return "n/a" if pd.isna(x) else f"{x:.1e}".replace("e+", "e")


def money(x):
    if pd.isna(x):
        return "n/a"
    return f"${x / 1e12:.2f}T" if x >= 1e12 else f"${x / 1e9:,.0f}B" if x >= 1e9 else f"${x / 1e6:,.0f}M"


def log_ticks(lo, hi):
    vals = list(range(int(np.floor(lo)), int(np.ceil(hi)) + 1))
    step = max(1, int(np.ceil(len(vals) / 6)))
    vals = vals[::step]
    return vals, [f"1e{v}" for v in vals]


def decimal_year(d):
    d = pd.to_datetime(d, errors="coerce")
    return d.dt.year + (d.dt.dayofyear - 1) / 365.25


def to_date(t):
    return pd.to_datetime((np.asarray(t) - 1970) * 365.25 * 86400, unit="s")


def log_fit(t, y):
    """Slope/intercept of log10(y) against decimal year, or None if too few points."""
    t, y = np.asarray(t, float), np.asarray(y, float)
    ok = np.isfinite(t) & np.isfinite(y) & (y > 0)
    if ok.sum() < 5 or np.unique(t[ok]).size < 2:
        return None
    return np.polyfit(t[ok], np.log10(y[ok]), 1)


def doubling(slope):
    return 12 * np.log10(2) / slope if slope and slope > 0 else None


def trend_trace(fit, t, name="Trend"):
    xs = np.linspace(np.nanmin(t), np.nanmax(t), 50)
    return go.Scatter(x=to_date(xs), y=10 ** (fit[1] + fit[0] * xs), mode="lines", name=name,
                      line=dict(color=INK, width=2, dash="dash"), hoverinfo="skip")


def rgba(hex_color, a):
    c = hex_color.lstrip("#")
    return f"rgba({int(c[0:2], 16)},{int(c[2:4], 16)},{int(c[4:6], 16)},{a})"


def table_and_download(df, name):
    with st.expander("View and download the filtered data"):
        st.dataframe(df, width="stretch", hide_index=True)
        st.download_button("Download CSV", df.to_csv(index=False).encode(), f"{name}.csv", "text/csv",
                           key=f"dl_{name}")


# ---------------------------------------------------------------- data
@st.cache_data
def load_models():
    df = pd.read_csv(DATA / "notable_ai_models.csv", low_memory=False)
    df["date"] = pd.to_datetime(df["Publication date"], errors="coerce")
    df = df.dropna(subset=["date"]).copy()
    df["year"] = df["date"].dt.year.astype(int)
    df["domain"] = df["Domain"].fillna("Unknown").str.split(",").str[0].str.strip()
    country = df["Country (of organization)"].fillna("Unknown").str.split(",").str[0].str.strip()
    df["country"] = country.replace({"United States of America": "United States"})

    def org_type(s):
        if not isinstance(s, str):
            return "Unknown"
        parts = {p.strip() for p in s.split(",")}
        if {"Industry", "Academia"} <= parts:
            return "Industry + Academia"
        if "Industry" in parts:
            return "Industry"
        if "Academia" in parts:
            return "Academia"
        return "Government / collective"

    df["org_type"] = df["Organization categorization"].map(org_type)
    acc = df["Model accessibility"].fillna("Unknown").astype(str)
    df["access"] = np.select(
        [acc.str.startswith("Open weights"),
         acc.isin(["API access", "Hosted access (no API)", "Limited access"]),
         acc.eq("Unreleased")],
        ["Open weights", "API / hosted", "Unreleased"], "Unknown")
    df["params"] = pd.to_numeric(df["Parameters"], errors="coerce")
    df["compute"] = pd.to_numeric(df["Training compute (FLOP)"], errors="coerce")
    df["cost"] = pd.to_numeric(df["Training compute cost (2023 USD)"], errors="coerce")
    df["dyear"] = decimal_year(df["date"])
    df["Organization"] = df["Organization"].fillna("Unknown")
    return df


@st.cache_data
def load_hardware():
    h = pd.read_csv(DATA / "ml_hardware.csv")
    h["release"] = pd.to_datetime(h["Release date"], errors="coerce")
    h["year"] = h["release"].dt.year
    h["dyear"] = decimal_year(h["release"])
    h["Manufacturer"] = h["Manufacturer"].fillna("Unknown")
    h["Type"] = h["Type"].fillna("Unknown")
    return h


@st.cache_data
def load_sales():
    c = pd.read_csv(DATA / "timelines_by_chip.csv")
    c["quarter"] = pd.to_datetime(c["Start date"])
    c["qlabel"] = "Q" + c["quarter"].dt.quarter.astype(str) + " " + c["quarter"].dt.year.astype(str)
    c["Compute (H100-equivalents)"] = c["Compute estimate in H100e (median)"]
    c["Chips shipped"] = c["Number of Units"]
    c["Spend (billion USD)"] = c["Cost Estimate (USD)"] / 1e9
    c["Power draw (MW)"] = c["Total TDP (W)"] / 1e6
    return c


@st.cache_data
def load_clusters():
    g = pd.read_csv(DATA / "gpu_clusters.csv", low_memory=False)
    g["date"] = pd.to_datetime(g["First Operational Date"], format="%m/%d/%Y", errors="coerce")
    g["year"] = g["date"].dt.year
    g["anon"] = g["Name"].eq("Anonymized Chinese System")
    g["h100e"] = pd.to_numeric(g["H100 equivalents"], errors="coerce")
    g["power"] = pd.to_numeric(g["Power Capacity (MW)"], errors="coerce")
    g["Owner"] = g["Owner"].fillna("Undisclosed")
    g["Chip type (primary)"] = g["Chip type (primary)"].fillna("Undisclosed")
    return g


@st.cache_data
def load_datacenters():
    d = pd.read_csv(DATA / "data_centers.csv")
    d["Owner"] = (d["Owner"].fillna("Unknown").str.replace(r"\s*#\w+", "", regex=True).str.strip()
                  .replace({"Unknown": "Undisclosed owner", "": "Undisclosed owner"}))
    d["h100e"] = d["Current H100 equivalents"]
    d["power"] = d["Current power (MW)"]
    d["capex"] = d["Current total capital cost (2025 USD billions)"]
    return d[d["h100e"] > 0].copy()


@st.cache_data
def load_eci():
    e = pd.read_csv(DATA / "eci_scores.csv")
    e["date"] = pd.to_datetime(e["date"], errors="coerce")
    c = e["Country (of organization)"].fillna("Other")
    e["region"] = np.select([c.eq("United States of America"), c.eq("China")], ["United States", "China"], "Other")
    e["Organization"] = e["Organization"].fillna("Unknown")
    return e.dropna(subset=["date", "eci"])


@st.cache_data
def load_metr():
    m = pd.read_csv(DATA / "metr_time_horizons.csv")
    m["date"] = pd.to_datetime(m["Release date"], errors="coerce")
    m = m.dropna(subset=["date"])
    return m[m["Time horizon"] > 0].copy()


BENCHMARKS = {
    "MMLU (general knowledge)": ("bench_mmlu.csv", "EM"),
    "GPQA Diamond (PhD science)": ("bench_gpqa_diamond.csv", "mean_score"),
    "SWE-bench Verified (coding)": ("bench_swe_bench_verified.csv", "mean_score"),
    "Humanity's Last Exam": ("bench_hle.csv", "Accuracy"),
    "FrontierMath (research math)": ("bench_frontiermath.csv", "mean_score"),
    "ARC-AGI-2 (visual puzzles)": ("bench_arc_agi_2.csv", "Score"),
}


@st.cache_data
def load_benchmarks():
    rows = []
    for name, (file, col) in BENCHMARKS.items():
        b = pd.read_csv(DATA / file, low_memory=False)
        b = pd.DataFrame({"Benchmark": name, "Model": b["Model version"],
                          "date": pd.to_datetime(b["Release date"], errors="coerce"),
                          "score": pd.to_numeric(b[col], errors="coerce") * 100})
        rows.append(b.dropna(subset=["date", "score"]))
    return pd.concat(rows, ignore_index=True)


@st.cache_data
def load_revenue():
    r = pd.read_csv(DATA / "revenue_reports.csv")
    r["date"] = pd.to_datetime(r["Date"], errors="coerce")
    r = r[(r["Scope"] == "Full company") & (r["Annualized revenue (USD)"] > 0)].dropna(subset=["date"])
    return r.sort_values("date")


@st.cache_data
def load_funding():
    f = pd.read_csv(DATA / "funding_rounds.csv")
    f["date"] = pd.to_datetime(f["Close date"], errors="coerce")
    return f[f["Status"] == "Closed"]


models = load_models()
hw = load_hardware()
sales = load_sales()
clusters_all = load_clusters()
clusters = clusters_all.dropna(subset=["latitude", "longitude", "h100e"])
dcs = load_datacenters()
eci = load_eci()
metr = load_metr()
bench = load_benchmarks()
revenue = load_revenue()
funding = load_funding()

# fixed colour per entity (colour follows the entity, never its rank after filtering)
TOP_DOMAINS = list(models["domain"].value_counts().index[:4])
DOMAIN_COLORS = {d: S[i] for i, d in enumerate(TOP_DOMAINS)} | {"Other": OTHER}
TOP_COUNTRIES = list(models["country"].value_counts().drop("Unknown", errors="ignore").index[:5])
COUNTRY_COLORS = {c: S[i] for i, c in enumerate(TOP_COUNTRIES)} | {"Other": OTHER}
ACCESS_ORDER = ["Open weights", "API / hosted", "Unreleased", "Unknown"]
ACCESS_COLORS = {"Open weights": S[0], "API / hosted": S[1], "Unreleased": S[2], "Unknown": OTHER}
ORG_ORDER = ["Industry", "Academia", "Industry + Academia", "Government / collective"]
ORG_COLORS = {"Industry": S[0], "Academia": S[1], "Industry + Academia": S[2], "Government / collective": OTHER}
CHIP_MAKERS = ["NVIDIA", "Google", "AMD"]
CHIP_COLORS = {m: S[i] for i, m in enumerate(CHIP_MAKERS)} | {"Other": OTHER}
MAKERS = ["Nvidia", "Google", "AMD", "Huawei", "Amazon", "Cambricon"]
MAKER_COLORS = {m: S[i] for i, m in enumerate(MAKERS)}
SECTORS = ["Private", "Public", "Public/Private"]
SECTOR_COLORS = {s: S[i] for i, s in enumerate(SECTORS)}
REGIONS = ["United States", "China", "Other"]
REGION_COLORS = {"United States": S[0], "China": S[1], "Other": OTHER}
ECI_ACCESS = ["Closed weights", "Open weights", "Other"]
BENCH_NAMES = list(BENCHMARKS)
BENCH_COLORS = {b: S[i] for i, b in enumerate(BENCH_NAMES)}
COMPANIES = list(revenue["Company"].value_counts().index)
COMPANY_COLORS = {c: (S[i] if i < len(S) else OTHER) for i, c in enumerate(COMPANIES)}

# ---------------------------------------------------------------- filter state
MAX_YEAR = int(models["year"].max())
HW_MIN, HW_MAX = int(hw["year"].min()), int(hw["year"].max())
QUARTERS = list(sales.sort_values("quarter")["qlabel"].unique())
DEFAULT_Q = ("Q1 2024", "Q2 2026") if {"Q1 2024", "Q2 2026"} <= set(QUARTERS) else (QUARTERS[0], QUARTERS[-1])
CL_MIN, CL_MAX = int(clusters["year"].min()), int(clusters["year"].max())
DC_COUNTRIES = list(dcs["Country"].value_counts().index)

SECTIONS = {
    "models": ("1 · AI models", "Figures 1–5"),
    "hardware": ("2 · AI hardware", "Figures 6–7"),
    "infra": ("3 · Compute & infrastructure", "Figures 8–10"),
    "payoff": ("4 · Does it pay off?", "Figures 11–14"),
    "answer": ("5 · The answer", "Figure 15"),
}
DEFAULTS = {
    "models": {"m_year": (2012, MAX_YEAR), "m_domain": [], "m_country": [], "m_org": [],
               "m_access": ACCESS_ORDER},
    "hardware": {"h_maker": [], "h_type": [], "h_year": (2008, HW_MAX)},
    "infra": {"s_makers": MAKERS, "s_quarters": DEFAULT_Q, "c_sector": SECTORS, "c_supplier": [],
              "c_year": (2018, CL_MAX), "c_anon": False, "d_country": []},
    "payoff": {"p_access": ECI_ACCESS, "p_bench": BENCH_NAMES, "p_companies": ["OpenAI", "Anthropic"]},
    "answer": {},
}

# keep every filter's value when its section is hidden, and seed the defaults on first load
for group in DEFAULTS.values():
    for k, v in group.items():
        st.session_state[k] = st.session_state[k] if k in st.session_state else (
            list(v) if isinstance(v, list) else v)


def _same(a, b):
    if isinstance(b, list):  # an empty selection means "all", same as the default
        return set(a or b) == set(b)
    return tuple(a) == tuple(b) if isinstance(b, tuple) else a == b


def active_count(sec):
    return sum(not _same(st.session_state[k], v) for k, v in DEFAULTS[sec].items())


def reset(sec):
    for k, v in DEFAULTS[sec].items():
        st.session_state[k] = list(v) if isinstance(v, list) else v


# ---------------------------------------------------------------- growth rates (whole dataset)
@st.cache_data
def growth_rates():
    """Average growth per year (x) of each driver and result, from log-linear fits."""
    out = []

    def add(group, name, t, y, period):
        f = log_fit(t, y)
        if f is not None:
            out.append({"group": group, "name": name, "per_year": 10 ** f[0],
                        "doubling": doubling(f[0]), "period": period})

    x = models[(models["year"] >= 2012) & (models["compute"] > 0)]
    add("Bigger models", "Training compute of notable models", x["dyear"], x["compute"], "2012–2026")
    x = hw.dropna(subset=["Tensor-FP16/BF16 performance (FLOP/s)", "dyear"])
    add("Better chips", "Speed of a single AI chip (FP16)", x["dyear"],
        x["Tensor-FP16/BF16 performance (FLOP/s)"], "2017–2026")
    g = clusters_all.dropna(subset=["date", "h100e"]).sort_values("date")
    g = g[g["year"] >= 2016]
    add("More infrastructure", "Size of the largest GPU cluster", decimal_year(g["date"]),
        g["h100e"].cummax(), "2016–2026")
    q = (sales[(sales["qlabel"].isin(QUARTERS[QUARTERS.index("Q1 2024"):QUARTERS.index("Q2 2026") + 1]))]
         .groupby("quarter")["Compute (H100-equivalents)"].sum())
    add("More infrastructure", "AI chips shipped per quarter (H100e)", decimal_year(pd.Series(q.index)),
        q.values, "2024–2026")
    add("Results", "Length of tasks AI can finish alone", decimal_year(metr["date"]), metr["Time horizon"],
        "2019–2026")
    for c in ["OpenAI", "Anthropic"]:
        r = revenue[(revenue["Company"] == c) & (revenue["date"] >= "2023-01-01")]
        add("Results", f"{c} revenue", decimal_year(r["date"]), r["Annualized revenue (USD)"], "2023–2026")
    return pd.DataFrame(out)


# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-mark">AI</div><div>'
                '<div class="brand-name">AI Landscape</div>'
                '<div class="brand-sub">Data analysis dashboard</div></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="side-label">Sections</div>', unsafe_allow_html=True)
    sec = st.radio("Section", list(SECTIONS), key="section", label_visibility="collapsed",
                   format_func=lambda k: SECTIONS[k][0], captions=[v[1] for v in SECTIONS.values()])
    st.divider()

    if DEFAULTS[sec]:
        n_active = active_count(sec)
        h1, h2 = st.columns([3, 2], vertical_alignment="center")
        h1.markdown(f'<div class="side-label" style="margin:0">Filters'
                    f'<span class="badge {"" if n_active else "off"}">{n_active} active</span></div>',
                    unsafe_allow_html=True)
        h2.button("Reset", on_click=reset, args=(sec,), disabled=n_active == 0, icon=":material/restart_alt:",
                  width="stretch")

    if sec == "models":
        st.slider("Publication year", 1950, MAX_YEAR, key="m_year")
        st.multiselect("Domain", list(models["domain"].value_counts().index), key="m_domain",
                       placeholder="All domains")
        st.multiselect("Country", list(models["country"].value_counts().index), key="m_country",
                       placeholder="All countries")
        st.multiselect("Organization type", ORG_ORDER + ["Unknown"], key="m_org", placeholder="All types")
        st.pills("Model access", ACCESS_ORDER, selection_mode="multi", key="m_access")
    elif sec == "hardware":
        st.multiselect("Manufacturer", list(hw["Manufacturer"].value_counts().index), key="h_maker",
                       placeholder="All manufacturers")
        st.multiselect("Chip type", list(hw["Type"].value_counts().index), key="h_type", placeholder="All types")
        st.slider("Release year", HW_MIN, HW_MAX, key="h_year")
    elif sec == "infra":
        st.markdown("**Chip sales** · figure 8")
        st.pills("Chip designer", MAKERS, selection_mode="multi", key="s_makers")
        st.select_slider("Quarters", options=QUARTERS, key="s_quarters")
        st.markdown("**GPU clusters** · figure 9")
        st.pills("Sector", SECTORS, selection_mode="multi", key="c_sector")
        sup_opts = [s for s in clusters["GPU Supplier (primary)"].value_counts().index if s != "Anonymized"]
        st.multiselect("Chip supplier", sup_opts, key="c_supplier", placeholder="All suppliers")
        st.slider("First operational", CL_MIN, CL_MAX, key="c_year")
        st.toggle("Include anonymized Chinese systems", key="c_anon",
                  help="190 systems with no name or owner, placed at approximate locations in China.")
        st.markdown("**Data centers** · figure 10")
        st.multiselect("Country", DC_COUNTRIES, key="d_country", placeholder="All countries")
    elif sec == "payoff":
        st.markdown("**Capability index** · figure 11")
        st.pills("Model weights", ECI_ACCESS, selection_mode="multi", key="p_access")
        st.markdown("**Benchmarks** · figure 13")
        st.multiselect("Benchmarks", BENCH_NAMES, key="p_bench", placeholder="All benchmarks")
        st.markdown("**Revenue** · figure 14")
        st.pills("Companies", COMPANIES, selection_mode="multi", key="p_companies")
    else:
        st.caption("This section sums up the whole dataset, so it has no filters.")

    st.divider()
    st.markdown('<div class="side-foot">Source: Epoch AI, epoch.ai/data (CC BY 4.0), November 2026.<br>'
                'Built with pandas, NumPy, Plotly and Streamlit.</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------- header
st.markdown(
    f"""<div class="hero">
      <div class="eyebrow">Python · Data Analysis and Visualization</div>
      <h1>The AI Landscape in Data</h1>
      <p>Models, chips, data centers, capabilities and money, from Epoch AI's public datasets.</p>
      <span class="chip">{len(models):,} AI models</span><span class="chip">{len(hw):,} AI chips</span>
      <span class="chip">{clusters['Name'].nunique():,} GPU clusters</span>
      <span class="chip">{len(dcs):,} data centers</span><span class="chip">15 interactive charts</span>
    </div>
    <div class="question"><span class="tag">Research question</span>
      <span class="text">What is driving the AI boom: <b>bigger models</b>, <b>better chips</b>,
      or <b>more computing infrastructure</b>? And is it paying off? Sections 1–4 look at each part;
      section 5 gives the answer.</span></div>""",
    unsafe_allow_html=True,
)

ss = st.session_state

# ================================================================= SECTION 1: MODELS
if sec == "models":
    section_head(1, "AI models", "How fast are AI models growing, and who builds them?")
    m = models[models["year"].between(*ss.m_year)]
    if ss.m_domain:
        m = m[m["domain"].isin(ss.m_domain)]
    if ss.m_country:
        m = m[m["country"].isin(ss.m_country)]
    if ss.m_org:
        m = m[m["org_type"].isin(ss.m_org)]
    m = m[m["access"].isin(ss.m_access or ACCESS_ORDER)].copy()
    m["domain_g"] = np.where(m["domain"].isin(TOP_DOMAINS), m["domain"], "Other")
    m["country_g"] = np.where(m["country"].isin(TOP_COUNTRIES), m["country"], "Other")

    # trend fit used by KPI + figure 3
    fit = m[m["compute"] > 0]
    trend = log_fit(fit["dyear"], fit["compute"])

    k1, k2, k3, k4 = st.columns(4)
    known = m[m["access"] != "Unknown"]
    k1.metric("Models in view", f"{len(m):,}")
    k2.metric("Open weights",
              f"{(known['access'] == 'Open weights').mean():.0%}" if len(known) else "n/a")
    if fit.empty:
        k3.metric("Largest training run", "n/a")
    else:
        top = fit.loc[fit["compute"].idxmax()]
        k3.metric("Largest training run", f"{sci(top['compute'])} FLOP", top["Model"], delta_color="off")
    dm = doubling(trend[0]) if trend is not None else None
    k4.metric("Compute doubles every", f"{dm:.1f} months" if dm else "n/a",
              help="Log-linear fit of training compute against publication date, for the models in view.")

    if m.empty:
        nothing()
    else:
        # ---- 1. LINE
        a, b = st.columns(2)
        with a, card(1):
            card_title(1, "Line chart", "Language models took over from vision",
                       "Notable models published per year, by domain")
            years = range(int(m["year"].min()), int(m["year"].max()) + 1)
            order = [d for d in TOP_DOMAINS + ["Other"] if d in m["domain_g"].unique()]
            cnt = (m.groupby(["year", "domain_g"]).size().unstack(fill_value=0)
                   .reindex(index=years, columns=order, fill_value=0))
            long = cnt.reset_index().melt(id_vars="year", var_name="Domain", value_name="Models")
            fig = px.line(long, x="year", y="Models", color="Domain", markers=True,
                          color_discrete_map=DOMAIN_COLORS, category_orders={"Domain": order})
            fig.update_traces(line_width=2, marker_size=6)
            fig.update_xaxes(title=None)
            show(style(fig))

        # ---- 2. STACKED BAR
        with b, card(2):
            card_title(2, "Stacked bar chart", "Who gets to use the models?",
                       "Models per year, by how they were released")
            mode = st.segmented_control("Show as", ["Count", "Share of year"], default="Count",
                                        key="acc_mode", label_visibility="collapsed")
            acc = m.groupby(["year", "access"]).size().reset_index(name="Models")
            if mode == "Share of year":
                acc["Models"] = acc["Models"] / acc.groupby("year")["Models"].transform("sum") * 100
            fig = px.bar(acc, x="year", y="Models", color="access", color_discrete_map=ACCESS_COLORS,
                         category_orders={"access": ACCESS_ORDER},
                         labels={"Models": "Share of models (%)" if mode == "Share of year" else "Models",
                                 "access": "Access"})
            fig.update_traces(marker_line_color=SURFACE, marker_line_width=1.5)
            fig.update_layout(barmode="stack", bargap=0.15, barcornerradius=4)
            fig.update_xaxes(title=None)
            show(style(fig, height=360))

        # ---- 3. BUBBLE SCATTER + TREND LINE
        with card(3):
            t1, t2 = st.columns([3, 1], vertical_alignment="bottom")
            with t1:
                card_title(3, "Bubble scatter with trend line", "Training compute grows exponentially",
                           "Each bubble is a model; bubble size = number of parameters (log scale)")
            orgs = list(fit["Organization"].value_counts().index[:40])
            hl = t2.selectbox("Highlight an organization", ["None"] + orgs, key="hl_org")
            if fit.empty:
                nothing()
            else:
                pts = fit.copy()
                pts["size"] = np.log10(pts["params"].clip(lower=1)).fillna(3).clip(lower=3)
                pts["Parameters"] = pts["params"].map(sci)
                pts["Compute"] = pts["compute"].map(sci)
                fig = px.scatter(pts, x="date", y="compute", color="access", size="size", size_max=22,
                                 log_y=True, color_discrete_map=ACCESS_COLORS,
                                 category_orders={"access": ACCESS_ORDER}, hover_name="Model",
                                 hover_data={"Organization": True, "Compute": True, "Parameters": True,
                                             "date": "|%b %Y", "size": False, "compute": False,
                                             "access": True},
                                 labels={"compute": "Training compute (FLOP)", "date": "", "access": "Access"})
                fig.update_traces(marker=dict(opacity=0.8, line=dict(width=1, color=SURFACE)))
                if trend is not None:
                    fig.add_trace(trend_trace(trend, pts["dyear"]))
                if hl != "None":
                    h = pts[pts["Organization"] == hl]
                    fig.add_trace(go.Scatter(x=h["date"], y=h["compute"], mode="markers+text", name=hl,
                                             text=h["Model"], textposition="top center",
                                             textfont=dict(size=11, color=INK),
                                             marker=dict(size=14, color="rgba(0,0,0,0)",
                                                         line=dict(color=INK, width=2)),
                                             hoverinfo="skip"))
                show(style(fig, height=480))

        # ---- 4. DONUT  + 5. VIOLIN
        a, b = st.columns(2)
        with a, card(4):
            card_title(4, "Donut chart", "The US builds most notable models",
                       "Share of models by the developer's country (top 5 + other)")
            order = [c for c in TOP_COUNTRIES + ["Other"] if c in m["country_g"].unique()]
            share = m["country_g"].value_counts().reindex(order).reset_index()
            share.columns = ["Country", "Models"]
            fig = px.pie(share, names="Country", values="Models", hole=0.6, color="Country",
                         color_discrete_map=COUNTRY_COLORS, category_orders={"Country": order})
            fig.update_traces(sort=False, direction="clockwise", texttemplate="%{percent:.0%}",
                              textposition="inside", insidetextorientation="horizontal",
                              marker_line_color=SURFACE, marker_line_width=2,
                              hovertemplate="%{label}: %{value} models (%{percent})<extra></extra>")
            fig.add_annotation(text=f"<b>{len(m):,}</b><br>models", showarrow=False,
                               font=dict(size=18, color=INK))
            fig = style(fig, height=400)
            fig.update_layout(uniformtext_minsize=11, uniformtext_mode="hide",
                              legend=dict(orientation="v", x=1.0, y=0.5, yanchor="middle"))
            show(fig)

        with b, card(5):
            card_title(5, "Violin plot with box", "Industry trains the biggest models",
                       "Distribution by organization type (log scale)")
            metric = st.segmented_control(
                "Measure", ["Training compute (FLOP)", "Parameters", "Training cost (2023 USD)"],
                default="Training compute (FLOP)", key="violin_metric",
                label_visibility="collapsed") or "Training compute (FLOP)"
            col = {"Training compute (FLOP)": "compute", "Parameters": "params",
                   "Training cost (2023 USD)": "cost"}[metric]
            v = m[m[col] > 0].copy()
            if v.empty:
                nothing()
            else:
                v["log"] = np.log10(v[col])
                v["Value"] = v[col].map(sci)
                present = [o for o in ORG_ORDER + ["Unknown"] if o in v["org_type"].unique()]
                fig = px.violin(v, x="org_type", y="log", color="org_type", box=True, points="outliers",
                                color_discrete_map=ORG_COLORS | {"Unknown": OTHER},
                                category_orders={"org_type": present}, hover_name="Model",
                                hover_data={"Value": True, "log": False, "org_type": False},
                                labels={"org_type": "", "log": metric})
                tv, tt = log_ticks(v["log"].min(), v["log"].max())
                fig.update_yaxes(tickvals=tv, ticktext=tt, title=None)
                fig.update_xaxes(tickangle=0, tickvals=present,
                                 ticktext=[p.replace(" + ", " +<br>").replace(" / ", " /<br>") for p in present])
                fig.update_traces(meanline_visible=True, line_width=1.5)
                show(style(fig, height=352, legend=False))

        table_and_download(
            m[["Model", "Organization", "Publication date", "domain", "country", "org_type", "access",
               "Parameters", "Training compute (FLOP)", "Training compute cost (2023 USD)"]],
            "ai_models_filtered")

# ================================================================= SECTION 2: HARDWARE
elif sec == "hardware":
    section_head(2, "AI hardware", "How much better are the chips that train these models?")
    h = hw[hw["year"].between(*ss.h_year) | hw["year"].isna()]
    if ss.h_maker:
        h = h[h["Manufacturer"].isin(ss.h_maker)]
    if ss.h_type:
        h = h[h["Type"].isin(ss.h_type)]

    FP16, FP32 = "Tensor-FP16/BF16 performance (FLOP/s)", "FP32 (single precision) performance (FLOP/s)"
    chip_trend = log_fit(h["dyear"], h[FP16])
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Chips in view", f"{len(h):,}")
    perf = h.dropna(subset=[FP16])
    if perf.empty:
        k2.metric("Fastest chip (FP16)", "n/a")
    else:
        best = perf.loc[perf[FP16].idxmax()]
        k2.metric("Fastest chip (FP16)", f"{best[FP16] / 1e12:,.0f} TFLOP/s", best["Hardware name"],
                  delta_color="off")
    if chip_trend is not None and chip_trend[0] > 0:
        k3.metric("Chip speed grows", f"×{10 ** chip_trend[0]:.2f} per year",
                  help="Log-linear fit of FP16 performance against release date, for the chips in view.")
        k4.metric("Chip speed doubles every", f"{doubling(chip_trend[0]) / 12:.1f} years")
    else:
        k3.metric("Chip speed grows", "n/a")
        k4.metric("Chip speed doubles every", "n/a")

    # ---- 6. SCATTER + TREND
    with card(6):
        card_title(6, "Scatter with trend line", "Each chip is faster, but only slowly",
                   "Peak speed of every chip by release date (log scale)")
        which = st.segmented_control("Precision", ["FP16 (AI training)", "FP32 (classic)"],
                                     default="FP16 (AI training)", key="chip_metric",
                                     label_visibility="collapsed") or "FP16 (AI training)"
        col = FP16 if which.startswith("FP16") else FP32
        pts = h[(h[col] > 0) & h["release"].notna()].copy()
        if len(pts) < 3:
            nothing()
        else:
            pts["maker"] = np.where(pts["Manufacturer"].isin(CHIP_MAKERS), pts["Manufacturer"], "Other")
            pts["TFLOP/s"] = (pts[col] / 1e12).map("{:,.1f}".format)
            fig = px.scatter(pts, x="release", y=col, color="maker", log_y=True,
                             color_discrete_map=CHIP_COLORS, category_orders={"maker": CHIP_MAKERS + ["Other"]},
                             hover_name="Hardware name",
                             hover_data={"TFLOP/s": True, "maker": False, col: False, "release": "|%b %Y"},
                             labels={col: f"{which.split(' ')[0]} speed (FLOP/s)", "release": ""})
            fig.update_traces(marker=dict(size=9, opacity=0.85, line=dict(width=1, color=SURFACE)))
            f = log_fit(pts["dyear"], pts[col])
            if f is not None:
                fig.add_trace(trend_trace(f, pts["dyear"], name=f"Trend: ×{10 ** f[0]:.2f} per year"))
            fig.update_yaxes(dtick=1)
            show(style(fig, height=440))

    # ---- 7. HEATMAP
    with card(7):
        card_title(7, "Heatmap", "Which chip specs move together?",
                   "Correlation between hardware specs (log scale), for the chips in view")
        method = st.segmented_control("Correlation", ["Pearson", "Spearman"], default="Pearson",
                                      key="corr", label_visibility="collapsed") or "Pearson"
        cols = {
            "Release year": "year",
            "FP32 perf": FP32,
            "FP16 tensor perf": FP16,
            "Memory": "Memory (bytes)",
            "Bandwidth": "Memory bandwidth (byte/s)",
            "Power (TDP)": "TDP (W)",
            "Die size": "Die Size (mm^2)",
            "Process (nm)": "Process size (nm)",
            "Transistors": "Transistors (millions)",
            "Price": "Release price (USD)",
        }
        num = pd.DataFrame({k: pd.to_numeric(h[v], errors="coerce") for k, v in cols.items()})
        for k in num.columns:
            if k != "Release year":
                num[k] = np.log10(num[k].where(num[k] > 0))
        corr = num.corr(method=method.lower(), min_periods=8).dropna(how="all").dropna(axis=1, how="all")
        if corr.shape[0] < 2:
            nothing()
        else:
            fig = px.imshow(corr, text_auto=".2f", color_continuous_scale=DIVERGING, zmin=-1, zmax=1,
                            aspect="auto")
            fig.update_traces(hovertemplate="%{y} vs %{x}: %{z:.2f}<extra></extra>", textfont_size=11)
            fig.update_layout(coloraxis_colorbar=dict(title="r", thickness=12))
            show(style(fig, height=480))
            st.caption(f"Based on {len(h)} chips. Pairs with fewer than 8 chips reporting both specs are left blank.")

    table_and_download(
        h[["Hardware name", "Manufacturer", "Type", "Release date", FP16, FP32, "Memory (bytes)",
           "Memory bandwidth (byte/s)", "TDP (W)", "Release price (USD)"]],
        "ai_hardware_filtered")

# ================================================================= SECTION 3: INFRASTRUCTURE
elif sec == "infra":
    section_head(3, "Compute & infrastructure", "How much computing power is being built, and where?")

    g = clusters[clusters["Sector"].isin(ss.c_sector or SECTORS) & clusters["year"].between(*ss.c_year)]
    if ss.c_supplier:
        g = g[g["GPU Supplier (primary)"].isin(ss.c_supplier)]
    if not ss.c_anon:
        g = g[~g["anon"]]

    # ---- 8. STACKED AREA
    with card(8):
        card_title(8, "Stacked area chart", "The AI chip race, quarter by quarter",
                   "Estimated AI chips shipped by designer (median estimate)")
        t2, t3 = st.columns([5, 1], vertical_alignment="center")
        measure = t2.segmented_control(
            "Measure", ["Compute (H100-equivalents)", "Chips shipped", "Spend (billion USD)", "Power draw (MW)"],
            default="Compute (H100-equivalents)", key="sales_measure",
            label_visibility="collapsed") or "Compute (H100-equivalents)"
        cumulative = t3.toggle("Cumulative", value=False)

        q0, q1 = QUARTERS.index(ss.s_quarters[0]), QUARTERS.index(ss.s_quarters[1])
        keep = QUARTERS[q0:q1 + 1]
        sv = sales[sales["qlabel"].isin(keep) & sales["Chip manufacturer"].isin(ss.s_makers or MAKERS)]
        if sv.empty:
            nothing()
        else:
            order = [x for x in MAKERS if x in sv["Chip manufacturer"].unique()]
            pv = (sv.groupby(["qlabel", "Chip manufacturer"])[measure].sum().unstack(fill_value=0)
                  .reindex(index=keep, columns=order, fill_value=0))
            if cumulative:
                pv = pv.cumsum()
            long = pv.reset_index().melt(id_vars="qlabel", var_name="Designer", value_name=measure)
            fig = px.area(long, x="qlabel", y=measure, color="Designer", color_discrete_map=MAKER_COLORS,
                          category_orders={"Designer": order}, labels={"qlabel": ""})
            fig.update_traces(line_width=1.5, hovertemplate="%{fullData.name}: %{y:,.1f}<extra></extra>")
            fig.update_layout(hovermode="x unified")
            show(style(fig, height=420))
            if q0 < QUARTERS.index("Q1 2024"):
                st.caption("Before Q1 2024 the data covers only Nvidia (from 2022) and Google (from Q4 2022).")

    # ---- 9. MAP
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("GPU clusters", f"{len(g):,}")
    k2.metric("Total compute", f"{g['h100e'].sum() / 1e6:.2f}M H100e")
    k3.metric("Total power", f"{g['power'].sum() / 1000:.1f} GW")
    if len(g):
        big = g.loc[g["h100e"].idxmax()]
        k4.metric("Largest cluster", f"{big['h100e'] / 1000:,.0f}k H100e", big["Name"], delta_color="off")
    else:
        k4.metric("Largest cluster", "n/a")

    with card(9):
        card_title(9, "Bubble map", "Where the GPU clusters are",
                   "AI supercomputers worldwide; bubble size = computing power in H100-equivalents (log scale)")
        if g.empty:
            nothing()
        else:
            gm = g.copy()
            gm["size"] = np.log10(gm["h100e"].clip(lower=1)) + 1
            gm["Compute (H100e)"] = gm["h100e"].map("{:,.0f}".format)
            gm["Power (MW)"] = gm["power"].map(lambda x: "n/a" if pd.isna(x) else f"{x:,.0f}")
            gm["Since"] = gm["date"].dt.strftime("%b %Y")
            fig = px.scatter_geo(gm, lat="latitude", lon="longitude", color="Sector", size="size", size_max=18,
                                 color_discrete_map=SECTOR_COLORS, category_orders={"Sector": SECTORS},
                                 hover_name="Name",
                                 hover_data={"Owner": True, "Country": True, "Compute (H100e)": True,
                                             "Power (MW)": True, "Chip type (primary)": True, "Since": True,
                                             "size": False, "latitude": False, "longitude": False,
                                             "Sector": False},
                                 projection="natural earth")
            fig.update_traces(marker=dict(opacity=0.75, line=dict(width=1, color="white")))
            fig.update_geos(showland=True, landcolor="#f0efec", showcountries=True, countrycolor="#d9d8d3",
                            showocean=True, oceancolor=SURFACE, showlakes=False, showframe=False,
                            coastlinecolor="#d9d8d3", bgcolor=SURFACE)
            show(style(fig, height=540), scroll_zoom=False)

    # ---- 10. TREEMAP
    d = dcs[dcs["Country"].isin(ss.d_country)] if ss.d_country else dcs
    with card(10):
        card_title(10, "Treemap", "The mega data centers, and who owns them",
                   "Each box is a data center, grouped by owner; darker = more expensive per H100-equivalent")
        size_by = st.segmented_control("Box size", ["Computing power", "Power (MW)", "Cost (USD)"],
                                       default="Computing power", key="dc_size",
                                       label_visibility="collapsed") or "Computing power"
        scol = {"Computing power": "h100e", "Power (MW)": "power", "Cost (USD)": "capex"}[size_by]
        d = d[d[scol] > 0].copy()
        if d.empty:
            nothing()
        else:
            d["cost_per"] = d["capex"] * 1e9 / d["h100e"] / 1000
            d["Compute"] = d["h100e"].map(lambda x: f"{x / 1000:,.0f}k H100e")
            d["Power"] = d["power"].map(lambda x: f"{x:,.0f} MW")
            d["Cost"] = d["capex"].map(lambda x: f"${x:,.1f}B")
            fig = px.treemap(d, path=[px.Constant("All data centers"), "Owner", "Name"], values=scol,
                             color="cost_per", color_continuous_scale=SEQUENTIAL,
                             range_color=[d["cost_per"].quantile(0.05), d["cost_per"].quantile(0.95)],
                             hover_data={"Compute": True, "Power": True, "Cost": True, "Country": True},
                             labels={"cost_per": "$k per H100e"})
            fig.update_traces(marker=dict(line=dict(color=SURFACE, width=2)), root_color="#f0efec",
                              texttemplate="<b>%{label}</b>", tiling=dict(pad=2))
            fig.update_layout(coloraxis_colorbar=dict(title="$k per<br>H100e", thickness=12))
            show(style(fig, height=520))
            top3 = d.groupby("Owner")["h100e"].sum().sort_values(ascending=False)
            st.caption(f"{len(d)} data centers. The biggest owners by computing power: "
                       + ", ".join(f"{o} ({v / 1e6:.1f}M H100e)" for o, v in top3.head(3).items()) + ".")

    table_and_download(
        g[["Name", "Owner", "Country", "Sector", "GPU Supplier (primary)", "Chip type (primary)",
           "First Operational Date", "H100 equivalents", "Power Capacity (MW)"]],
        "gpu_clusters_filtered")

# ================================================================= SECTION 4: PAYOFF
elif sec == "payoff":
    section_head(4, "Does it pay off?", "Are the models getting more capable, and are AI companies earning from it?")

    e = eci[eci["Accessibility group"].isin(ss.p_access or ECI_ACCESS)].sort_values("date")
    us = e[e["region"] == "United States"].copy()
    cn = e[e["region"] == "China"].copy()
    gap = None
    if len(us) and len(cn):
        cn_best = cn["eci"].max()
        cn_date = cn.loc[cn["eci"].idxmax(), "date"]
        us["front"] = us["eci"].cummax()
        reached = us[us["front"] >= cn_best]
        if len(reached):
            gap = max(0.0, (cn_date - reached["date"].iloc[0]).days / 30.44)

    mt = log_fit(decimal_year(metr["date"]), metr["Time horizon"])
    k1, k2, k3, k4 = st.columns(4)
    if len(e):
        top = e.loc[e["eci"].idxmax()]
        k1.metric("Most capable model", f"{top['eci']:.0f} ECI", top["Display name"], delta_color="off")
    else:
        k1.metric("Most capable model", "n/a")
    k2.metric("China's gap to US", f"{gap:.0f} months" if gap is not None else "n/a",
              help="Time between the US first reaching China's best score and China reaching it.")
    k3.metric("Task length doubles", f"{doubling(mt[0]):.1f} months" if mt is not None else "n/a")
    val = funding.dropna(subset=["Valuation (post-money)"])
    vtop = val.loc[val["Valuation (post-money)"].idxmax()]
    k4.metric("Highest valuation", money(vtop["Valuation (post-money)"]), vtop["Company"], delta_color="off")

    a, b = st.columns(2)
    # ---- 11. CAPABILITY SCATTER + FRONTIER
    with a, card(11):
        card_title(11, "Scatter with frontier lines", "US vs China: the capability race",
                   "Epoch Capabilities Index of each model; lines show each country's best so far")
        if e.empty:
            nothing()
        else:
            fig = px.scatter(e, x="date", y="eci", color="region", color_discrete_map=REGION_COLORS,
                             category_orders={"region": REGIONS}, hover_name="Display name",
                             hover_data={"Organization": True, "Accessibility group": True, "region": False,
                                         "eci": ":.0f", "date": "|%b %Y"},
                             labels={"eci": "Capability index (ECI)", "date": "", "region": "Country"})
            fig.update_traces(marker=dict(size=8, opacity=0.55, line=dict(width=1, color=SURFACE)))
            for reg, part in [("United States", us), ("China", cn)]:
                if len(part):
                    fr = part.assign(front=part["eci"].cummax())
                    fr = fr[fr["front"].diff().fillna(1) > 0]
                    last = pd.DataFrame({"date": [e["date"].max()], "front": [fr["front"].iloc[-1]]})
                    fr = pd.concat([fr[["date", "front"]], last])
                    fig.add_trace(go.Scatter(x=fr["date"], y=fr["front"], mode="lines", line_shape="hv",
                                             name=f"{reg} best", line=dict(color=REGION_COLORS[reg], width=2.5),
                                             hoverinfo="skip"))
            show(style(fig, height=430))

    # ---- 12. TASK LENGTH
    with b, card(12):
        card_title(12, "Scatter with trend line (log scale)", "AI can do longer and longer tasks alone",
                   "How long a task (for a human expert) each model finishes half the time")
        mm = metr.copy()
        mm["Task length"] = mm["Time horizon"].map(
            lambda x: f"{x * 60:.0f} sec" if x < 1 else f"{x:.0f} min" if x < 60 else f"{x / 60:.1f} hours")
        fig = px.scatter(mm, x="date", y="Time horizon", log_y=True, hover_name="Model version",
                         hover_data={"Organization": True, "Task length": True, "Time horizon": False,
                                     "date": "|%b %Y"},
                         error_y=mm["CI_high"] - mm["Time horizon"],
                         error_y_minus=mm["Time horizon"] - mm["CI_low"],
                         labels={"date": "", "Time horizon": "Task length"})
        fig.update_traces(marker=dict(size=9, color=S[0], line=dict(width=1, color=SURFACE)),
                          error_y=dict(color=rgba(S[0], 0.25), thickness=1, width=0), name="Model",
                          showlegend=True)
        if mt is not None:
            fig.add_trace(trend_trace(mt, decimal_year(mm["date"]),
                                      name=f"Trend: doubles every {doubling(mt[0]):.0f} months"))
        ticks = [1 / 60, 10 / 60, 1, 10, 60, 600, 1440]
        fig.update_yaxes(tickvals=ticks, ticktext=["1 sec", "10 sec", "1 min", "10 min", "1 hour", "10 hours",
                                                   "1 day"])
        for name in mm.nlargest(1, "Time horizon")["Model version"]:
            r = mm[mm["Model version"] == name].iloc[0]
            fig.add_annotation(x=r["date"], y=np.log10(r["Time horizon"]), text=name.split("_")[0],
                               showarrow=False, xanchor="right", xshift=-8, font=dict(size=11, color=INK))
        show(style(fig, height=430))

    # ---- 13. BENCHMARK RACE
    with card(13):
        card_title(13, "Step line chart", "New tests get beaten faster and faster",
                   "Best score so far on each benchmark (record-setting models marked)")
        bsel = ss.p_bench or BENCH_NAMES
        bb = bench[bench["Benchmark"].isin(bsel)].sort_values("date")
        if bb.empty:
            nothing()
        else:
            fig = go.Figure()
            end = bb["date"].max()
            for name in [n for n in BENCH_NAMES if n in bsel]:
                part = bb[bb["Benchmark"] == name].copy()
                part["best"] = part["score"].cummax()
                rec = part[part["best"].diff().fillna(part["best"]) > 0]
                if rec.empty:
                    continue
                line =pd.concat([rec[["date", "best"]], pd.DataFrame({"date": [end], "best": [rec["best"].iloc[-1]]})])
                fig.add_trace(go.Scatter(x=line["date"], y=line["best"], mode="lines", line_shape="hv", name=name,
                                         line=dict(color=BENCH_COLORS[name], width=2), legendgroup=name,
                                         hoverinfo="skip"))
                fig.add_trace(go.Scatter(x=rec["date"], y=rec["best"], mode="markers", legendgroup=name,
                                         showlegend=False, customdata=rec[["Model"]],
                                         marker=dict(size=8, color=BENCH_COLORS[name], line=dict(width=1, color=SURFACE)),
                                         hovertemplate=f"<b>{name}</b><br>%{{customdata[0]}}<br>"
                                                       "%{y:.1f}% · %{x|%b %Y}<extra></extra>"))
            fig.update_yaxes(title="Best score (%)", range=[0, 102])
            show(style(fig, height=430))

    # ---- 14. REVENUE RACE
    with card(14):
        t1, t2 = st.columns([4, 1], vertical_alignment="bottom")
        with t1:
            card_title(14, "Line chart", "The money race: AI company revenue",
                       "Annualized revenue (yearly run rate) reported for each company")
        logy = t2.toggle("Log scale", value=False, key="rev_log")
        rv = revenue[revenue["Company"].isin(ss.p_companies or COMPANIES)].copy()
        if rv.empty:
            nothing()
        else:
            rv["Revenue"] = rv["Annualized revenue (USD)"].map(money)
            order = [c for c in COMPANIES if c in rv["Company"].unique()]
            fig = px.line(rv, x="date", y="Annualized revenue (USD)", color="Company", markers=True, log_y=logy,
                          color_discrete_map=COMPANY_COLORS, category_orders={"Company": order},
                          hover_data={"Revenue": True, "Annualized revenue (USD)": False, "Confidence": True,
                                      "date": "|%b %Y"},
                          labels={"date": "", "Annualized revenue (USD)": "Annualized revenue (USD)"})
            fig.update_traces(line_width=2, marker_size=7)
            fig.update_yaxes(tickprefix="$")
            show(style(fig, height=420))
            last = rv.groupby("Company").tail(1).sort_values("Annualized revenue (USD)", ascending=False)
            st.caption("Latest: " + ", ".join(
                f"{c} {money(v).replace('$', r'\$')} ({d:%b %Y})"
                for c, v, d in zip(last["Company"], last["Annualized revenue (USD)"], last["date"])) + ".")

    with st.expander("View and download the filtered data"):
        st.dataframe(e[["Display name", "Organization", "region", "Accessibility group", "date", "eci"]],
                     width="stretch", hide_index=True)
        st.download_button("Download CSV", e.to_csv(index=False).encode(), "capability_index.csv", "text/csv")

# ================================================================= SECTION 5: THE ANSWER
else:
    section_head(5, "The answer", "So what is driving the AI boom?")
    gr = growth_rates()

    def rate(name):
        row = gr[gr["name"] == name]
        return row["per_year"].iloc[0] if len(row) else float("nan")

    comp = rate("Training compute of notable models")
    chip = rate("Speed of a single AI chip (FP16)")
    clus = rate("Size of the largest GPU cluster")
    ship = rate("AI chips shipped per quarter (H100e)")
    task = rate("Length of tasks AI can finish alone")
    rev_o, rev_a = rate("OpenAI revenue"), rate("Anthropic revenue")
    other = comp / (chip * clus)

    st.markdown(
        f"""<div class="drivers">
          <div class="driver"><div class="k">Bigger models</div><div class="v">×{comp:.1f} <small>per year</small></div>
            <div class="d">Training compute of the notable models. This is the boom itself, and what we
            need to explain.</div></div>
          <div class="driver"><div class="k">Better chips</div><div class="v">×{chip:.2f} <small>per year</small></div>
            <div class="d">Each new AI chip is only about {(chip - 1) * 100:.0f}% faster than a year earlier.
            Explains only a small part.</div></div>
          <div class="driver win"><div class="k">More infrastructure · main driver</div>
            <div class="v">×{clus:.1f}–{ship:.1f} <small>per year</small></div>
            <div class="d">The largest GPU cluster grows ×{clus:.1f} a year and chip shipments ×{ship:.1f}.
            Building more is the biggest factor.</div></div>
        </div>
        <div class="verdict"><span class="tag">Our answer</span>
          Training compute grows <b>×{comp:.1f} a year</b>. Better chips give about <b>×{chip:.2f}</b> of that
          and bigger clusters about <b>×{clus:.1f}</b>; the remaining ×{other:.1f} comes from training runs
          that last longer and use a bigger share of each cluster. So the AI boom is driven mainly by
          <b>building more computing infrastructure</b>, not by better chips.
          And it is paying off so far: the length of tasks AI can do alone grows <b>×{task:.1f} a year</b>,
          and revenue at OpenAI and Anthropic grows <b>×{rev_o:.1f}</b> and <b>×{rev_a:.1f}</b> a year.
        </div>""",
        unsafe_allow_html=True,
    )

    # ---- 15. GROWTH COMPARISON
    with card(15):
        card_title(15, "Horizontal bar chart (log scale)", "Everything grows, but not at the same speed",
                   "Average growth per year, from a trend line fitted to each dataset")
        gplot = gr.copy()
        gplot["label"] = gplot["name"] + "  (" + gplot["period"] + ")"
        gplot["text"] = gplot["per_year"].map(lambda x: f"×{x:.2f}" if x < 2 else f"×{x:.1f}")
        group_colors = {"Bigger models": S[0], "Better chips": S[1], "More infrastructure": S[2], "Results": S[6]}
        gplot = gplot.iloc[::-1]
        fig = px.bar(gplot, x="per_year", y="label", color="group", orientation="h", text="text", log_x=True,
                     color_discrete_map=group_colors,
                     category_orders={"group": list(group_colors), "label": list(gplot["label"])},
                     hover_data={"per_year": ":.2f", "label": False, "text": False},
                     labels={"per_year": "Growth per year (×, log scale)", "label": "", "group": ""})
        fig.update_traces(textposition="outside", cliponaxis=False, marker_line_width=0)
        fig.update_layout(barcornerradius=4, bargap=0.3)
        fig.update_xaxes(range=[0, np.log10(gplot["per_year"].max()) + 0.25], tickvals=[1, 1.5, 2, 3, 5, 10],
                         ticktext=["×1", "×1.5", "×2", "×3", "×5", "×10"])
        fig.update_yaxes(categoryorder="array", categoryarray=list(gplot["label"]))
        show(style(fig, height=420))
        st.caption("Each number is 10 to the power of the slope of log(value) against time. The periods differ "
                   "between datasets, so compare them as rough sizes, not exact ratios.")

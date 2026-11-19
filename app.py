"""
AI Landscape Dashboard
Python | Data Analysis and Visualization project

Data: Epoch AI (CC BY 4.0) - notable AI models, ML hardware, AI chip sales, GPU clusters.
Run:  python -m streamlit run app.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="AI Landscape Dashboard", page_icon="📊", layout="wide")
DATA = Path(__file__).parent / "data"

# ---------------------------------------------------------------- style
SURFACE, INK, INK2, GRID, OTHER = "#fcfcfb", "#0b0b0b", "#52514e", "#e8e7e3", "#a3a29c"
# colour-blind-checked categorical order (blue, orange, aqua, yellow, magenta, green, violet, red)
S = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
DIVERGING = [[0, "#e34948"], [0.5, "#f0efec"], [1, "#2a78d6"]]

st.markdown(
    """<style>
    .block-container {padding-top: 2rem; max-width: 1400px;}
    [data-testid="stMetricValue"] {font-size: 1.7rem;}
    h1 {font-weight: 700; letter-spacing: -0.02em;}
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


def card_title(num, title, subtitle):
    st.markdown(f"#### {num}. {title}")
    st.caption(subtitle)


def show(fig):
    st.plotly_chart(fig, width="stretch", config={"displaylogo": False})


def nothing():
    st.info("No data matches these filters. Widen the filters above.")


def sci(x):
    return "n/a" if pd.isna(x) else f"{x:.1e}".replace("e+", "e")


def log_ticks(lo, hi):
    vals = list(range(int(np.floor(lo)), int(np.ceil(hi)) + 1))
    step = max(1, int(np.ceil(len(vals) / 6)))
    vals = vals[::step]
    return vals, [f"1e{v}" for v in vals]


def table_and_download(df, name):
    with st.expander("View and download the filtered data"):
        st.dataframe(df, width="stretch", hide_index=True)
        st.download_button("Download CSV", df.to_csv(index=False).encode(), f"{name}.csv", "text/csv")


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
    df["dyear"] = df["year"] + (df["date"].dt.dayofyear - 1) / 365.25
    df["Organization"] = df["Organization"].fillna("Unknown")
    return df


@st.cache_data
def load_hardware():
    h = pd.read_csv(DATA / "ml_hardware.csv")
    h["release"] = pd.to_datetime(h["Release date"], errors="coerce")
    h["year"] = h["release"].dt.year
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
    return g.dropna(subset=["latitude", "longitude", "h100e"])


models = load_models()
hw = load_hardware()
sales = load_sales()
clusters = load_clusters()

# fixed colour per entity (colour follows the entity, never its rank after filtering)
TOP_DOMAINS = list(models["domain"].value_counts().index[:4])
DOMAIN_COLORS = {d: S[i] for i, d in enumerate(TOP_DOMAINS)} | {"Other": OTHER}
TOP_COUNTRIES = list(models["country"].value_counts().drop("Unknown", errors="ignore").index[:5])
COUNTRY_COLORS = {c: S[i] for i, c in enumerate(TOP_COUNTRIES)} | {"Other": OTHER}
ACCESS_ORDER = ["Open weights", "API / hosted", "Unreleased", "Unknown"]
ACCESS_COLORS = {"Open weights": S[0], "API / hosted": S[1], "Unreleased": S[2], "Unknown": OTHER}
ORG_ORDER = ["Industry", "Academia", "Industry + Academia", "Government / collective"]
ORG_COLORS = {"Industry": S[0], "Academia": S[1], "Industry + Academia": S[2], "Government / collective": OTHER}
MAKERS = ["Nvidia", "Google", "AMD", "Huawei", "Amazon", "Cambricon"]
MAKER_COLORS = {m: S[i] for i, m in enumerate(MAKERS)}
SECTOR_COLORS = {"Private": S[0], "Public": S[1], "Public/Private": S[2]}

# ---------------------------------------------------------------- header
st.title("The AI Landscape in Data")
st.caption(
    "Models, chips, and the compute behind them. Every chart reacts to the filters in its tab. "
    "Source: Epoch AI (CC BY 4.0), epoch.ai/data, November 2026 snapshot."
)

tab_models, tab_hw, tab_infra = st.tabs(["AI models", "AI hardware", "Compute and infrastructure"])

# ================================================================= TAB 1: MODELS
with tab_models:
    max_year = int(models["year"].max())
    f1, f2, f3, f4 = st.columns([2, 3, 3, 3])
    yr = f1.slider("Publication year", 1950, max_year, (2012, max_year))
    dom_opts = list(models["domain"].value_counts().index)
    sel_dom = f2.multiselect("Domain", dom_opts, placeholder="All domains")
    cty_opts = list(models["country"].value_counts().index)
    sel_cty = f3.multiselect("Country", cty_opts, placeholder="All countries")
    sel_org = f4.multiselect("Organization type", ORG_ORDER + ["Unknown"], placeholder="All types")
    sel_acc = st.pills("Model access", ACCESS_ORDER, selection_mode="multi", default=ACCESS_ORDER)

    m = models[models["year"].between(*yr)]
    if sel_dom:
        m = m[m["domain"].isin(sel_dom)]
    if sel_cty:
        m = m[m["country"].isin(sel_cty)]
    if sel_org:
        m = m[m["org_type"].isin(sel_org)]
    m = m[m["access"].isin(sel_acc or ACCESS_ORDER)].copy()
    m["domain_g"] = np.where(m["domain"].isin(TOP_DOMAINS), m["domain"], "Other")
    m["country_g"] = np.where(m["country"].isin(TOP_COUNTRIES), m["country"], "Other")

    # trend fit used by KPI + chart 3
    fit = m.dropna(subset=["compute"])
    fit = fit[fit["compute"] > 0]
    slope = intercept = None
    if len(fit) >= 5 and fit["dyear"].nunique() > 1:
        slope, intercept = np.polyfit(fit["dyear"], np.log10(fit["compute"]), 1)

    k1, k2, k3, k4 = st.columns(4)
    known = m[m["access"] != "Unknown"]
    k1.metric("Models in view", f"{len(m):,}")
    k2.metric("Released with open weights",
              f"{(known['access'] == 'Open weights').mean():.0%}" if len(known) else "n/a")
    if fit.empty:
        k3.metric("Largest training run", "n/a")
    else:
        top = fit.loc[fit["compute"].idxmax()]
        k3.metric("Largest training run", f"{sci(top['compute'])} FLOP", top["Model"], delta_color="off")
    if slope and slope > 0:
        k4.metric("Training compute doubles every", f"{12 * np.log10(2) / slope:.1f} months",
                  help="Log-linear fit of training compute against publication date, for the models in view.")
    else:
        k4.metric("Training compute doubles every", "n/a")

    if m.empty:
        nothing()
    else:
        # ---- 1. LINE
        a, b = st.columns(2)
        with a, st.container(border=True):
            card_title(1, "Language models took over from vision",
                       "Line chart · notable models published per year, by domain")
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
        with b, st.container(border=True):
            card_title(2, "Who gets to use the models?",
                       "Stacked bar chart · models per year by how they were released")
            mode = st.segmented_control("Show as", ["Count", "Share of year"], default="Count",
                                        key="acc_mode")
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
            show(style(fig))

        # ---- 3. BUBBLE SCATTER + TREND LINE
        with st.container(border=True):
            card_title(3, "Training compute grows exponentially",
                       "Bubble scatter with trend line · each bubble is a model, size = number of parameters (log scale)")
            orgs = list(fit["Organization"].value_counts().index[:40])
            hl = st.selectbox("Highlight an organization", ["None"] + orgs, key="hl_org")
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
                if slope is not None:
                    xs = np.linspace(pts["dyear"].min(), pts["dyear"].max(), 50)
                    xd = pd.to_datetime((xs - 1970) * 365.25 * 86400, unit="s")
                    fig.add_trace(go.Scatter(x=xd, y=10 ** (intercept + slope * xs), mode="lines",
                                             name="Trend", line=dict(color=INK, width=2, dash="dash"),
                                             hoverinfo="skip"))
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
        with a, st.container(border=True):
            card_title(4, "Where the models come from",
                       "Donut chart · share of models by the developer's country (top 5 + other)")
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
            fig = style(fig, height=420)
            fig.update_layout(uniformtext_minsize=11, uniformtext_mode="hide",
                              legend=dict(orientation="v", x=1.0, y=0.5, yanchor="middle"))
            show(fig)

        with b, st.container(border=True):
            card_title(5, "Industry trains the biggest models",
                       "Violin plot with box · distribution by organization type (log scale)")
            metric = st.segmented_control(
                "Measure", ["Training compute (FLOP)", "Parameters", "Training cost (2023 USD)"],
                default="Training compute (FLOP)", key="violin_metric") or "Training compute (FLOP)"
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
                show(style(fig, height=380, legend=False))

        table_and_download(
            m[["Model", "Organization", "Publication date", "domain", "country", "org_type", "access",
               "Parameters", "Training compute (FLOP)", "Training compute cost (2023 USD)"]],
            "ai_models_filtered")

# ================================================================= TAB 2: HARDWARE
with tab_hw:
    f1, f2, f3 = st.columns([3, 3, 2])
    mk_opts = list(hw["Manufacturer"].value_counts().index)
    sel_mk = f1.multiselect("Manufacturer", mk_opts, placeholder="All manufacturers")
    ty_opts = list(hw["Type"].value_counts().index)
    sel_ty = f2.multiselect("Chip type", ty_opts, placeholder="All types")
    ymin, ymax = int(hw["year"].min()), int(hw["year"].max())
    hyr = f3.slider("Release year", ymin, ymax, (2016, ymax))

    h = hw[hw["year"].between(*hyr) | hw["year"].isna()]
    if sel_mk:
        h = h[h["Manufacturer"].isin(sel_mk)]
    if sel_ty:
        h = h[h["Type"].isin(sel_ty)]

    a, b = st.columns(2)
    # ---- 6. RADAR
    with a, st.container(border=True):
        card_title(6, "Head-to-head: AI accelerators",
                   "Radar chart · each spec scaled to the best of the selected chips (100 = best)")
        need = ["Tensor-FP16/BF16 performance (FLOP/s)", "Memory (bytes)",
                "Memory bandwidth (byte/s)", "TDP (W)"]
        cand = h.dropna(subset=need).sort_values("release", ascending=False)
        names = list(cand["Hardware name"])
        defaults = [n for n in ["NVIDIA H100 SXM5 80GB", "AMD Instinct MI300X", "Google TPU v6e Trillium"]
                    if n in names] or names[:3]
        pick = st.multiselect("Chips to compare (up to 3)", names, default=defaults, max_selections=3)
        if not pick:
            nothing()
        else:
            r = cand.set_index("Hardware name").loc[pick]
            specs = pd.DataFrame({
                "FP16 compute": r[need[0]] / 1e12,
                "Memory": r[need[1]] / 1e9,
                "Bandwidth": r[need[2]] / 1e12,
                "Efficiency": r[need[0]] / 1e12 / r[need[3]],
                "Power draw": r[need[3]],
            })
            units = ["TFLOP/s", "GB", "TB/s", "TFLOP/s per W", "W"]
            norm = specs / specs.max() * 100
            axes = list(specs.columns)
            fig = go.Figure()
            for i, chip in enumerate(pick):
                vals = list(norm.loc[chip]) + [norm.loc[chip].iloc[0]]
                raw = [f"{x:,.2f} {u}" for x, u in zip(specs.loc[chip], units)]
                raw += raw[:1]
                c = S[i].lstrip("#")
                fill = f"rgba({int(c[0:2], 16)},{int(c[2:4], 16)},{int(c[4:6], 16)},0.12)"
                fig.add_trace(go.Scatterpolar(
                    r=vals, theta=axes + [axes[0]], name=chip, fill="toself", customdata=raw,
                    line=dict(color=S[i], width=2), fillcolor=fill,
                    hovertemplate="<b>" + chip + "</b><br>%{theta}: %{customdata}<extra></extra>"))
            fig.update_layout(polar=dict(bgcolor=SURFACE,
                                         radialaxis=dict(range=[0, 100], gridcolor=GRID, showticklabels=False),
                                         angularaxis=dict(gridcolor=GRID)))
            fig = style(fig, height=440)
            fig.update_layout(margin=dict(l=70, r=70, t=70, b=30))
            show(fig)

    # ---- 7. HEATMAP
    with b, st.container(border=True):
        card_title(7, "Which chip specs move together?",
                   "Heatmap · correlation between hardware specs (log scale), for the chips in view")
        method = st.segmented_control("Correlation", ["Pearson", "Spearman"], default="Pearson",
                                      key="corr") or "Pearson"
        cols = {
            "Release year": "year",
            "FP32 perf": "FP32 (single precision) performance (FLOP/s)",
            "FP16 tensor perf": "Tensor-FP16/BF16 performance (FLOP/s)",
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
            show(style(fig, height=500))
            st.caption(f"Based on {len(h)} chips. Pairs with fewer than 8 chips reporting both specs are left blank.")

    table_and_download(
        h[["Hardware name", "Manufacturer", "Type", "Release date"] + need + ["Release price (USD)"]],
        "ai_hardware_filtered")

# ================================================================= TAB 3: INFRASTRUCTURE
with tab_infra:
    # ---- 8. STACKED AREA
    with st.container(border=True):
        card_title(8, "The AI chip race, quarter by quarter",
                   "Stacked area chart · estimated AI chips shipped by designer (median estimate)")
        f1, f2, f3 = st.columns([3, 4, 2])
        measure = f1.segmented_control(
            "Measure", ["Compute (H100-equivalents)", "Chips shipped", "Spend (billion USD)", "Power draw (MW)"],
            default="Compute (H100-equivalents)", key="sales_measure") or "Compute (H100-equivalents)"
        quarters = list(sales.sort_values("quarter")["qlabel"].unique())
        default_q = ("Q1 2024", "Q2 2026") if {"Q1 2024", "Q2 2026"} <= set(quarters) else (quarters[0], quarters[-1])
        qrange = f2.select_slider("Quarters", options=quarters, value=default_q)
        cumulative = f3.toggle("Cumulative", value=False)
        sel_makers = st.pills("Chip designer", MAKERS, selection_mode="multi", default=MAKERS)

        q0, q1 = quarters.index(qrange[0]), quarters.index(qrange[1])
        keep = quarters[q0:q1 + 1]
        sv = sales[sales["qlabel"].isin(keep) & sales["Chip manufacturer"].isin(sel_makers or MAKERS)]
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
            show(style(fig, height=430))
            if q0 < quarters.index("Q1 2024"):
                st.caption("Before Q1 2024 the data covers only Nvidia (from 2022) and Google (from Q4 2022).")

    # ---- 9. MAP
    with st.container(border=True):
        card_title(9, "Where the GPU clusters are",
                   "Bubble map · AI supercomputers worldwide, bubble size = computing power in H100-equivalents (log scale)")
        f1, f2, f3, f4 = st.columns([3, 3, 3, 2])
        sectors = f1.pills("Sector", list(SECTOR_COLORS), selection_mode="multi", default=list(SECTOR_COLORS))
        sup_opts = [s for s in clusters["GPU Supplier (primary)"].value_counts().index if s != "Anonymized"]
        sel_sup = f2.multiselect("Chip supplier", sup_opts, placeholder="All suppliers")
        cy0, cy1 = int(clusters["year"].min()), int(clusters["year"].max())
        cyr = f3.slider("First operational", cy0, cy1, (2018, cy1))
        anon = f4.toggle("Include anonymized Chinese systems", value=False,
                         help="190 systems with no name or owner, placed at approximate locations in China.")

        g = clusters[clusters["Sector"].isin(sectors or list(SECTOR_COLORS)) & clusters["year"].between(*cyr)]
        if sel_sup:
            g = g[g["GPU Supplier (primary)"].isin(sel_sup)]
        if not anon:
            g = g[~g["anon"]]

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Clusters", f"{len(g):,}")
        k2.metric("Total compute", f"{g['h100e'].sum() / 1e6:.2f}M H100e")
        k3.metric("Total power", f"{g['power'].sum() / 1000:.1f} GW")
        if len(g):
            big = g.loc[g["h100e"].idxmax()]
            k4.metric("Largest cluster", big["Name"], f"{big['h100e']:,.0f} H100e", delta_color="off")

        if g.empty:
            nothing()
        else:
            g = g.copy()
            g["size"] = np.log10(g["h100e"].clip(lower=1)) + 1
            g["Compute (H100e)"] = g["h100e"].map("{:,.0f}".format)
            g["Power (MW)"] = g["power"].map(lambda x: "n/a" if pd.isna(x) else f"{x:,.0f}")
            g["Since"] = g["date"].dt.strftime("%b %Y")
            fig = px.scatter_geo(g, lat="latitude", lon="longitude", color="Sector", size="size", size_max=18,
                                 color_discrete_map=SECTOR_COLORS, hover_name="Name",
                                 hover_data={"Owner": True, "Country": True, "Compute (H100e)": True,
                                             "Power (MW)": True, "Chip type (primary)": True, "Since": True,
                                             "size": False, "latitude": False, "longitude": False,
                                             "Sector": False},
                                 projection="natural earth")
            fig.update_traces(marker=dict(opacity=0.75, line=dict(width=1, color="white")))
            fig.update_geos(showland=True, landcolor="#f0efec", showcountries=True, countrycolor="#d9d8d3",
                            showocean=True, oceancolor=SURFACE, showlakes=False, showframe=False,
                            coastlinecolor="#d9d8d3", bgcolor=SURFACE)
            show(style(fig, height=540))

        table_and_download(
            g[["Name", "Owner", "Country", "Sector", "GPU Supplier (primary)", "Chip type (primary)",
               "First Operational Date", "H100 equivalents", "Power Capacity (MW)"]] if len(g) else g,
            "gpu_clusters_filtered")

st.divider()
st.caption("Built with Python: pandas, NumPy, Plotly and Streamlit. Data: Epoch AI, licensed CC BY 4.0.")

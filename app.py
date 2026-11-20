"""
STEP 4 - THE DASHBOARD  (run:  python -m streamlit run app.py)

Builds the web page: the sidebar filters, the sections, and the cards around each chart.
All numbers come from analysis.py and all charts from charts.py.
"""
import numpy as np
import streamlit as st

import analysis as A
import charts as C

st.set_page_config(page_title="Why Steam games fail", page_icon="🎮", layout="wide",
                   initial_sidebar_state="expanded")

# ---------------------------------------------------------------- page style
st.markdown("""<style>
.stApp {background: #0f1923;}
.block-container {padding-top: 2.6rem; padding-bottom: 3rem; max-width: 1340px;}
section[data-testid="stSidebar"] {background: #121c27; border-right: 1px solid #22313f;}
section[data-testid="stSidebar"] .block-container {padding-top: 1.2rem;}
h1, h2, h3, h4 {color: #e6edf3;}

.brand {display:flex; gap:12px; align-items:center; margin-bottom:6px;}
.brand .logo {width:42px; height:42px; border-radius:10px; display:grid; place-items:center; font-size:22px;
              background: linear-gradient(135deg, #66c0f4, #1b4d7a);}
.brand .name {font-weight:700; color:#e6edf3; font-size:1.05rem; line-height:1.2;}
.brand .sub {color:#93a7ba; font-size:.78rem;}
.label {font-size:.72rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:#93a7ba; margin:8px 0 2px;}
.badge {display:inline-block; margin-left:6px; padding:2px 9px; border-radius:99px; font-size:.72rem; font-weight:600;
        background:#1d3a55; color:#9fd7f7; letter-spacing:0; text-transform:none;}
.badge.off {background:#1b2733; color:#93a7ba;}
.foot {font-size:.75rem; color:#7f93a6; line-height:1.5;}

.hero {border-radius:18px; padding:28px 32px; margin-bottom:16px; border:1px solid #22384d;
       background: radial-gradient(900px 260px at 90% -30%, rgba(102,192,244,.35), rgba(102,192,244,0) 60%),
                   linear-gradient(135deg, #171a21 0%, #1b2838 55%, #2a475e 100%);}
.hero .eyebrow {font-size:.74rem; letter-spacing:.16em; text-transform:uppercase; color:#66c0f4; font-weight:700;}
.hero h1 {font-size:2.5rem; margin:.3rem 0 .4rem; padding:0; letter-spacing:-.02em;}
.hero p {color:#b8c7d6; margin:0 0 14px; font-size:1rem;}
.chip {display:inline-block; padding:5px 12px; margin:0 6px 6px 0; border-radius:99px; font-size:.8rem;
       background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.14); color:#dbe6f0;}

[data-testid="stMetric"] {background:#16222e; border:1px solid #22313f; border-radius:14px; padding:14px 16px;}
[data-testid="stMetricLabel"] p {font-size:.74rem; text-transform:uppercase; letter-spacing:.08em; color:#93a7ba;}
[data-testid="stMetricValue"] {font-size:1.65rem; font-weight:700; color:#e6edf3;}

.sec {margin: 18px 0 12px;}
.sec .num {font-size:.74rem; letter-spacing:.14em; text-transform:uppercase; color:#66c0f4; font-weight:700;}
.sec h2 {font-size:1.7rem; margin:.15rem 0 .2rem; padding:0;}
.sec p {color:#93a7ba; margin:0;}

[class*="st-key-card"] {background:#16222e; border:1px solid #22313f !important; border-radius:16px;}
.tag {display:inline-block; font-size:.68rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase;
      color:#9fd7f7; background:#1d3a55; padding:3px 9px; border-radius:6px; margin-bottom:8px;}
.ftitle {font-size:1.15rem; font-weight:700; color:#e6edf3;}
.how {font-size:.88rem; color:#93a7ba; margin-top:4px; line-height:1.45;}
.how b {color:#cfdbe6;}
.key {background:#1d3a55; border-radius:10px; padding:10px 14px; color:#e6edf3; font-size:.93rem; line-height:1.5;}
.key .k {font-size:.68rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:#9fd7f7; margin-right:8px;}
.why {font-size:.8rem; color:#7f93a6; margin-top:6px; font-style:italic;}

.panel {background:#16222e; border:1px solid #22313f; border-radius:16px; padding:18px 20px; height:100%;}
.panel .big {font-size:2.2rem; font-weight:800; color:#e6edf3; line-height:1.1;}
.panel .t {font-weight:700; color:#e6edf3; font-size:1.02rem; margin:.3rem 0 .2rem;}
.panel .d {color:#93a7ba; font-size:.9rem; line-height:1.45;}
.dot {display:inline-block; width:12px; height:12px; border-radius:50%; margin-right:8px; vertical-align:middle;}
.problem {background: linear-gradient(135deg, #3a1e26, #1b2838); border:1px solid #5a2c36; border-radius:16px;
          padding:22px 26px; margin-bottom:14px;}
.problem .big {font-size:3.2rem; font-weight:800; color:#ff8080; line-height:1;}
.problem .d {color:#e6edf3; font-size:1.05rem; margin-top:6px;}
</style>""", unsafe_allow_html=True)


@st.cache_data
def games():
    return A.load_games()


df_all = games()

# ---------------------------------------------------------------- filters (one panel for every chart)
DEFAULTS = {"f_years": (2006, 2024), "f_genres": [], "f_prices": list(A.PRICE_BANDS),
            "f_platform": "All", "f_publisher": "All"}
for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, list(v) if isinstance(v, list) else v)


def reset_filters():
    for k, v in DEFAULTS.items():
        st.session_state[k] = list(v) if isinstance(v, list) else v


def active_filters():
    ss = st.session_state
    return sum([ss.f_years != DEFAULTS["f_years"], bool(ss.f_genres),
                set(ss.f_prices or A.PRICE_BANDS) != set(A.PRICE_BANDS),
                ss.f_platform != "All", ss.f_publisher != "All"])


SECTIONS = {
    "overview": ("Overview", "The problem, the data, the brief"),
    "when": ("01 · When?", "Is Steam too crowded?"),
    "what": ("02 · What?", "Which games succeed?"),
    "who": ("03 · Who?", "Who wins on Steam?"),
    "why": ("04 · Why?", "The root cause"),
    "fix": ("05 · What to do", "Advice for the studio"),
}

with st.sidebar:
    st.markdown('<div class="brand"><div class="logo">🎮</div><div><div class="name">Steam Games</div>'
                '<div class="sub">Why do most games fail?</div></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="label">Sections</div>', unsafe_allow_html=True)
    sec = st.radio("Section", list(SECTIONS), key="section", label_visibility="collapsed",
                   format_func=lambda k: SECTIONS[k][0], captions=[v[1] for v in SECTIONS.values()])
    st.divider()
    n = active_filters()
    c1, c2 = st.columns([3, 2], vertical_alignment="center")
    c1.markdown(f'<div class="label" style="margin:0">Filters<span class="badge {"" if n else "off"}">{n} active</span></div>',
                unsafe_allow_html=True)
    c2.button("Reset", on_click=reset_filters, disabled=n == 0, icon=":material/restart_alt:", width="stretch")
    st.caption("Every filter changes every chart and number on every page.")
    st.slider("Release year", 2006, 2024, key="f_years")
    st.multiselect("Genre", A.GENRES, key="f_genres", placeholder="All genres")
    st.pills("Price", A.PRICE_BANDS, selection_mode="multi", key="f_prices")
    st.segmented_control("Platform", ["All", "Windows only", "Has a Mac version", "Has a Linux version"],
                         key="f_platform")
    st.segmented_control("Publisher", ["All", "Self-published", "Has a publisher"], key="f_publisher")
    st.divider()
    st.markdown('<div class="foot">Data: Steam Games Dataset (FronkonGames, Kaggle), collected from the Steam '
                'store and SteamSpy. Owner numbers are estimates.<br>Built with pandas, NumPy, Plotly and '
                'Streamlit.</div>', unsafe_allow_html=True)

ss = st.session_state
df = A.apply_filters(df_all, ss.f_years, ss.f_genres, ss.f_prices or A.PRICE_BANDS,
                     ss.f_platform or "All", ss.f_publisher or "All")


# ---------------------------------------------------------------- building blocks
def section(num, title, question):
    st.markdown(f'<div class="sec"><div class="num">{num}</div><h2>{title}</h2><p>{question}</p></div>',
                unsafe_allow_html=True)


def figure(num, fig, key_point, extra=None):
    """One chart card: tag, question, how to read, the chart, key point, why this chart."""
    kind, question, how, why = C.CHARTS[num]
    with st.container(border=True, key=f"card{num}"):
        st.markdown(f'<div class="tag">Fig. {num:02d} · {kind}</div><div class="ftitle">{question}</div>'
                    f'<div class="how"><b>How to read:</b> {how}</div>', unsafe_allow_html=True)
        if extra:
            extra()
        st.plotly_chart(fig, width="stretch", config={"displaylogo": False, "scrollZoom": False})
        st.markdown(f'<div class="key"><span class="k">Key point</span>{key_point.replace("$", "&#36;")}</div>'
                    f'<div class="why">Why this chart: {why}</div>', unsafe_allow_html=True)


def kpi_row(d):
    k = A.kpis(d)
    c = st.columns(5)
    c[0].metric("Games", f"{k['games']:,}")
    c[1].metric("Failed", "n/a" if np.isnan(k["failed"]) else A.pct(k["failed"]), help="Fewer than 10 reviews")
    c[2].metric("Hits", "n/a" if np.isnan(k["hit"]) else A.pct(k["hit"]), help="1,000 or more reviews")
    c[3].metric("Median reviews", "n/a" if np.isnan(k["median_reviews"]) else f"{k['median_reviews']:,.0f}",
                help="Half of the games have fewer reviews than this")
    c[4].metric("Top 1% share", "n/a" if np.isnan(k["top1_share"]) else f"{k['top1_share']:.0%}",
                help="Share of all reviews that go to the top 1% of games")


def panel(big, title, desc, color=None):
    dot = f'<span class="dot" style="background:{color}"></span>' if color else ""
    return (f'<div class="panel"><div class="big">{dot}{big}</div><div class="t">{title}</div>'
            f'<div class="d">{desc}</div></div>')


# ---------------------------------------------------------------- header
st.markdown(f"""<div class="hero">
  <div class="eyebrow">Steam games · 2006–2024 · Python data analysis</div>
  <h1>Why do most Steam games fail?</h1>
  <p>{len(df_all):,} real Steam games, analysed for a small game studio deciding what to make next.</p>
  <span class="chip">{len(df_all):,} games</span><span class="chip">12 genres</span>
  <span class="chip">{int(df_all['reviews'].sum() / 1e6):,} million reviews</span><span class="chip">15 charts</span>
  <span class="chip">5 filters for every chart</span>
</div>""", unsafe_allow_html=True)

if df.empty:
    st.warning("No games match these filters. Widen them in the sidebar or press Reset.")
    st.stop()

kpi_row(df)

# ================================================================= OVERVIEW
if sec == "overview":
    k = A.kpis(df)
    st.markdown(f'<div class="problem"><div class="big">{A.pct(k["failed"])}</div><div class="d">of these Steam games '
                f'<b>never reach 10 reviews</b>: almost nobody plays them. Only {A.pct(k["hit"])} become hits.</div></div>',
                unsafe_allow_html=True)
    section("The brief", "A small studio asks four questions", "Each section of this dashboard answers one.")
    q = st.columns(4)
    for col, (n_, t, d) in zip(q, [("01", "When?", "Is Steam getting too crowded?"),
                                   ("02", "What?", "Which genres and prices succeed?"),
                                   ("03", "Who?", "Who gets the players?"),
                                   ("04", "Why?", "What do failed games have in common?")]):
        col.markdown(panel(n_, t, d), unsafe_allow_html=True)
    section("Definitions", "How we measure success", "Steam does not publish sales, so we use reviews: "
            "every review is a player who bought and played the game.")
    d = st.columns(4)
    for col, o in zip(d, A.OUTCOMES):
        share = (df["outcome"] == o).mean()
        col.markdown(panel(A.pct(share), o, A.OUTCOME_HELP[o], C.OUTCOME_COLORS[o]), unsafe_allow_html=True)
    section("The data", "From 125,855 apps to a clean dataset", "Cleaned with pandas in prepare_data.py. "
            "This chart is about the whole file, so the filters do not change it.")
    steps, key = A.cleaning_funnel()
    figure(1, C.cleaning_funnel(steps), key)

# ================================================================= 01 WHEN
elif sec == "when":
    section("01 · When?", "Is Steam too crowded?", "How the number of games, and their chances, changed over time.")
    t, key = A.releases_per_year(df)
    figure(2, C.releases_per_year(t), key)
    t, key = A.failure_by_year(df)
    figure(3, C.failure_by_year(t), key)
    grid, key = A.failure_heatmap(df)
    figure(4, C.failure_heatmap(grid), key)

# ================================================================= 02 WHAT
elif sec == "what":
    section("02 · What?", "Which games succeed?", "Genres and prices: where the crowd is, and what players like.")
    a, b = st.columns(2)
    with a:
        t, key = A.genre_counts(df)
        figure(5, C.genre_counts(t), key)
    with b:
        g, order, key = A.genre_scores(df)
        figure(6, C.genre_scores(g, order), key)
    a, b = st.columns(2)
    with a:
        paid, key = A.price_distribution(df)
        figure(7, C.price_distribution(paid), key)
    with b:
        share, key = A.outcome_by_price(df)
        figure(8, C.outcome_by_price(share), key)
    t, key = A.genre_bubbles(df)
    figure(9, C.genre_bubbles(t), key)

# ================================================================= 03 WHO
elif sec == "who":
    section("03 · Who?", "Who wins on Steam?", "Publishers and platforms behind the games people play.")
    top, key = A.top_publishers(df)
    figure(10, C.top_publishers(top), key)
    t, key = A.platform_share(df)
    a, b = st.columns([3, 2])
    with a:
        figure(11, C.platform_share(t), key)
    with b:
        st.markdown(panel(A.pct((df["publisher"] == df["developer"]).mean()), "of games are self-published",
                          "The studio that made the game also sells it, without a publisher's marketing.")
                    + "<div style='height:12px'></div>"
                    + panel(f"{df['publisher'].nunique():,}", "different publishers",
                            "Yet a few big names collect most of the players."), unsafe_allow_html=True)

# ================================================================= 04 WHY
elif sec == "why":
    section("04 · Why?", "The root cause: too many games, too little attention",
            "Players go to a few games. Quality alone does not get you noticed; launch effort does.")
    a, b = st.columns(2)
    with a:
        t, key = A.winner_takes_all(df)
        figure(12, C.winner_takes_all(t), key)
    with b:
        pts, key = A.quality_vs_popularity(df)
        figure(13, C.quality_vs_popularity(pts), key)
    a, b = st.columns(2)
    with a:
        t, key = A.signal_effect(df)
        figure(14, C.signal_effect(t), key)
    with b:
        t, key = A.signal_dose(df)
        figure(15, C.signal_dose(t), key)
    st.caption("Note: these are links, not proof of cause. Bigger studios tend to do all four things, so part of "
               "the gap comes from bigger budgets.")

# ================================================================= 05 WHAT TO DO
else:
    section("05 · What to do", "Four pieces of advice for the studio",
            "Each one answers a finding, with the numbers for the games in your filter.")
    r = A.recommendations(df)
    fmt = lambda x: "n/a" if np.isnan(x) else A.pct(x)
    tips = [
        ("Translate the game", f"{fmt(r['lang_1'])} → {fmt(r['lang_4'])}",
         "Games in one language fail far more often than games in 4+ languages (Fig. 14)."),
        ("Add achievements", f"{fmt(r['ach_no'])} → {fmt(r['ach_yes'])}",
         "Achievements are cheap to add and go with a much lower failure rate (Fig. 14)."),
        ("Find a publisher, or market like one", f"{fmt(r['self'])} → {fmt(r['pub'])}",
         "Self-published games fail more; publishers bring visibility (Fig. 14)."),
        (f"Price it {r['best_band']}", f"{fmt(r['best_band_fail'])} failed",
         "The price range where the fewest games fail (Fig. 8). Avoid December launches: "
         f"{fmt(r['dec'])} failed vs {fmt(r['spring'])} in Jan–Apr."),
    ]
    cols = st.columns(2)
    for i, (t, big, d) in enumerate(tips):
        cols[i % 2].markdown(panel(big, f"{i + 1}. {t}", d) + "<div style='height:14px'></div>",
                             unsafe_allow_html=True)
    st.markdown('<div class="key" style="margin-top:6px"><span class="k">The answer</span>Most Steam games fail '
                'because the store is flooded and players go to a few games. The games that get noticed are the '
                'ones launched with more effort: translated, with achievements, on more platforms, and with a '
                'publisher behind them.</div>', unsafe_allow_html=True)

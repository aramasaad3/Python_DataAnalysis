"""
STEP 4 - THE DASHBOARD  (Dash + Plotly)      Run:  python app.py   then open http://127.0.0.1:8050

Blocks: 1 data, 2 building blocks, 3 page layout, 4 one function per tab, 5 callbacks, 6 start.
All numbers come from analysis.py, all charts from charts.py, the design from assets/style.css.

How the filters work: every filter is an Input of the same two callbacks (update_kpis and update_tab).
When any filter changes, Dash filters the games ONCE and redraws the key numbers and EVERY chart of
the open tab with that same selection.
"""
from dash import Dash, Input, Output, dcc, html

import analysis as A
import charts as C

# =============================================================================
# 1. THE DATA
# =============================================================================
df = A.load_games()
YEARS = [int(df["year"].min()), int(df["year"].max())]
PLATFORMS = ["All", "Windows only", "Has a Mac version", "Has a Linux version"]
PUBLISHERS = ["All", "Self-published", "Has a publisher"]


def selection(genre, price, years, platform, publisher):
    """The one place where the 5 filters are turned into the games every chart uses."""
    return A.apply_filters(df, years or YEARS, genre or [], price or [], platform or "All", publisher or "All")


# =============================================================================
# 2. BUILDING BLOCKS
# =============================================================================
def markdown(text):
    """analysis.py writes <b>bold</b>; Dash shows Markdown, so we turn it into **bold**."""
    return dcc.Markdown(text.replace("<b>", "**").replace("</b>", "**"), className="md")


def card(num, fig, key_point):
    """A white card: Fig. number + chart type, the question, how to read it, the chart, the key point,
    then 3 boxes: why we chose this chart, why not another, and another chart that would also fit."""
    kind, question, how, why, why_not, also = C.CHART_INFO[num]
    return html.Div([
        html.Div([html.Span(f"Fig. {num}", className="fig-num"), html.Span(kind, className="fig-kind")],
                 className="card-top"),
        html.H4(question, className="card-q"),
        html.P([html.B("How to read: "), how], className="how"),
        # a fixed height, otherwise the chart stretches to the height of the browser window
        dcc.Graph(figure=fig, config={"displaylogo": False, "scrollZoom": False},
                  style={"height": f"{fig.layout.height or 440}px"}),
        html.Div([html.Span("Key point", className="kp-label"), markdown(key_point)], className="keypoint"),
        html.Div([
            html.Div([html.H4("Why we chose this chart"), html.P(why)], className="answer chose"),
            html.Div([html.H4("Why we did not choose others"), html.P(why_not)], className="answer others"),
            html.Div([html.H4("Another chart that would also fit"), html.P(also)], className="answer also"),
        ], className="answers"),
    ], className="card")


def kpi(label, value, note, tone=""):
    return html.Div([html.Div(label, className="kpi-label"), html.Div(value, className="kpi-value " + tone),
                     html.Div(note, className="kpi-note")], className="kpi")


def heading(question, sub=""):
    return html.Div([html.H2(question, className="lede-q"), html.P(sub, className="lede-sub")], className="lede wide")


def section(text):
    return html.H3(text, className="section")


def tiles(items):
    """A row of small boxes: (big text, title, description)."""
    return html.Div([html.Div([html.Div(big, className="tile-big"), html.Div(title, className="tile-title"),
                               html.Div(desc, className="tile-desc")], className="tile") for big, title, desc in items],
                    className="tiles wide")


# =============================================================================
# 3. THE PAGE LAYOUT
# =============================================================================
header = html.Div(html.Div([
    html.Div("Steam games analysis / 2006–2024", className="kicker"),
    html.H1("Why do most Steam games fail?"),
    html.P(f"{len(df):,} real Steam games, analysed for a small game studio deciding what to make next.",
           className="standfirst"),
], className="header-inner"), className="header")

sidebar = html.Div([
    html.Div(html.Div("Filters", className="side-title"), className="side-head"),
    html.Div([html.Label("Genre"), dcc.Dropdown(id="genre", options=A.GENRES, multi=True, placeholder="All genres")],
             className="filter"),
    html.Div([html.Label("Price"), dcc.Dropdown(id="price", options=A.PRICE_BANDS, multi=True, placeholder="All prices")],
             className="filter"),
    html.Div([html.Label("Release years"),
              dcc.RangeSlider(id="years", min=YEARS[0], max=YEARS[1], step=1, value=YEARS,
                              marks={y: str(y) for y in range(YEARS[0], YEARS[1] + 1, 6)},
                              tooltip={"placement": "bottom"})], className="filter"),
    html.Div([html.Label("Platform"), dcc.RadioItems(id="platform", options=PLATFORMS, value="All",
                                                     className="radios")], className="filter"),
    html.Div([html.Label("Publisher"), dcc.RadioItems(id="publisher", options=PUBLISHERS, value="All",
                                                      className="radios")], className="filter"),
    html.Button("Reset filters", id="reset"),
    html.P("An empty dropdown means all. Every key number and every chart on every tab follows these filters.",
           className="small"),
], className="sidebar")

tabs = dcc.Tabs(id="tab", value="overview", className="tabs", children=[
    dcc.Tab(label=label, value=value, className="tab", selected_className="tab--selected")
    for label, value in [("01  Overview", "overview"), ("02  When?", "when"), ("03  What?", "what"),
                         ("04  Who?", "who"), ("05  Why?", "why"), ("06  What to do", "fix")]])

FONTS = ("https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600"
         "&family=IBM+Plex+Sans:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,500;8..60,600"
         "&display=swap")
app = Dash(__name__, title="Why Steam games fail", external_stylesheets=[FONTS])
server = app.server   # for hosting (e.g. Render: gunicorn app:server)

app.layout = html.Div([
    dcc.Location(id="url"),   # lets a link open a tab directly, e.g. http://127.0.0.1:8050/?tab=why
    header,
    html.Div([
        sidebar,
        html.Div([
            html.Div(id="kpis", className="kpis"),
            tabs,
            dcc.Loading(html.Div(id="content", className="grid"), color="#1b9e77"),
            html.Div("Source: Steam Games Dataset (FronkonGames, Kaggle), collected from the Steam store and "
                     "SteamSpy. Owner numbers are estimates. Failed = fewer than 10 reviews, Hit = 1,000+ reviews.",
                     className="footer"),
        ], className="main"),
    ], className="body"),
])


# =============================================================================
# 4. ONE FUNCTION PER TAB
# =============================================================================
def overview_tab(f):
    k = A.kpis(f)
    steps, key = A.cleaning_funnel()
    return [
        html.Div([html.Div(A.pct(k["failed"]), className="problem-big"),
                  html.Div([html.B("of these Steam games never reach 10 reviews"), ": almost nobody plays them. "
                            f"Only {A.pct(k['hit'])} become hits."], className="problem-text")],
                 className="problem wide"),
        section("The brief: four questions from a small game studio"),
        tiles([("01", "When?", "Is Steam getting too crowded?"), ("02", "What?", "Which genres and prices succeed?"),
               ("03", "Who?", "Who gets the players?"), ("04", "Why?", "What do failed games have in common?")]),
        section("How we measure success"),
        html.P("Steam does not publish sales, so we use reviews: every review is a player who bought and played "
               "the game.", className="lede-sub wide"),
        tiles([(A.pct((f["outcome"] == o).mean()), o, A.OUTCOME_HELP[o]) for o in A.OUTCOMES]),
        section("The data"),
        html.P("Cleaned with pandas in prepare_data.py. This chart describes the whole file, so the filters do not "
               "change it.", className="lede-sub wide"),
        card(1, C.cleaning_funnel(steps), key),
    ]


def when_tab(f):
    t, key2 = A.releases_per_year(f)
    y, key3 = A.failure_by_year(f)
    grid, key4 = A.failure_heatmap(f)
    return [heading("When? Is Steam getting too crowded?", "How the number of games, and their chances, changed."),
            card(2, C.releases_per_year(t), key2),
            card(3, C.failure_by_year(y), key3),
            card(4, C.failure_heatmap(grid), key4)]


def what_tab(f):
    t5, key5 = A.genre_counts(f)
    g6, order, key6 = A.genre_scores(f)
    p7, key7 = A.price_distribution(f)
    s8, key8 = A.outcome_by_price(f)
    b9, key9 = A.genre_bubbles(f)
    return [heading("What? Which games succeed?", "Genres and prices: where the crowd is, and what players like."),
            card(5, C.genre_counts(t5), key5), card(6, C.genre_scores(g6, order), key6),
            card(7, C.price_distribution(p7), key7), card(8, C.outcome_by_price(s8), key8),
            card(9, C.genre_bubbles(b9), key9)]


def who_tab(f):
    top, key10 = A.top_publishers(f)
    plat, key11 = A.platform_share(f)
    return [heading("Who? Who wins on Steam?", "Publishers and platforms behind the games people play."),
            tiles([(A.pct(f["self_published"].mean()), "self-published",
                    "The studio that made the game also sells it, without a publisher's marketing."),
                   (f"{f['publisher'].nunique():,}", "different publishers",
                    "Yet a few big names collect most of the players.")]),
            card(10, C.top_publishers(top), key10), card(11, C.platform_share(plat), key11)]


def why_tab(f):
    t12, key12 = A.winner_takes_all(f)
    p13, key13 = A.quality_vs_popularity(f)
    t14, key14 = A.signal_effect(f)
    t15, key15 = A.signal_dose(f)
    return [heading("Why? Too many games, too little attention",
                    "Players go to a few games. Quality alone does not get you noticed; launch effort does."),
            card(12, C.winner_takes_all(t12), key12), card(13, C.quality_vs_popularity(p13), key13),
            card(14, C.signal_effect(t14), key14), card(15, C.signal_dose(t15), key15),
            html.P("Note: these are links, not proof of cause. Bigger studios tend to do all four things, so part "
                   "of the gap comes from bigger budgets.", className="small wide")]


def fix_tab(f):
    r = A.recommendations(f)
    k = A.kpis(f)
    fmt = A.pct
    return [heading("What should the studio do?", "Each piece of advice answers a finding, with the numbers for "
                                                   "the games in your filter."),
            html.Div(html.P("Most Steam games fail because the store is flooded and players go to a few games. The "
                            "games that get noticed are the ones launched with more effort: translated, with "
                            "achievements, on more platforms, and with a publisher behind them.",
                            className="rootcause-text"), className="rootcause wide"),
            section("What we found"),
            html.Ol([html.Li(markdown(t)) for t in [
                A.failure_by_year(f)[1], A.winner_takes_all(f)[1], A.quality_vs_popularity(f)[1],
                A.signal_dose(f)[1], A.outcome_by_price(f)[1],
                f"Overall {fmt(k['failed'])} of these games failed and {fmt(k['hit'])} became hits."]],
                className="findings wide"),
            section("Recommendations for the studio"),
            html.Ol([
                html.Li(f"Translate the game into 4+ languages: failure drops from {fmt(r['lang_1'])} to "
                        f"{fmt(r['lang_4'])} (Fig. 14)."),
                html.Li(f"Add Steam achievements: {fmt(r['ach_no'])} → {fmt(r['ach_yes'])} failed (Fig. 14)."),
                html.Li(f"Find a publisher, or market like one: {fmt(r['self'])} of self-published games failed vs "
                        f"{fmt(r['pub'])} with a publisher (Fig. 14)."),
                html.Li(f"Price it {r['best_band']}, where the fewest games fail ({fmt(r['best_band_fail'])}, Fig. 8). "
                        f"Avoid December: {fmt(r['dec'])} failed vs {fmt(r['spring'])} in January–April."),
            ], className="recs wide")]


TABS = {"overview": overview_tab, "when": when_tab, "what": what_tab, "who": who_tab, "why": why_tab,
        "fix": fix_tab}


# =============================================================================
# 5. CALLBACKS - the same 5 filters feed the key numbers and every chart
# =============================================================================
FILTERS = [Input("genre", "value"), Input("price", "value"), Input("years", "value"),
           Input("platform", "value"), Input("publisher", "value")]


@app.callback(Output("kpis", "children"), *FILTERS)
def update_kpis(genre, price, years, platform, publisher):
    f = selection(genre, price, years, platform, publisher)
    k = A.kpis(f)
    if not len(f):
        return [kpi("Games", "0", "no games match")]
    return [
        kpi("Games", f"{k['games']:,}", "in the selection"),
        kpi("Failed", A.pct(k["failed"]), "under 10 reviews", "bad"),
        kpi("Hits", A.pct(k["hit"]), "1,000+ reviews", "good"),
        kpi("Median reviews", f"{k['median_reviews']:,.0f}", "half the games have fewer"),
        kpi("Top 1% share", f"{k['top1_share']:.0%}", "of all reviews", "warn"),
        kpi("Self-published", A.pct(f["self_published"].mean()), "no publisher"),
    ]


@app.callback(Output("content", "children"), Input("tab", "value"), *FILTERS)
def update_tab(tab, genre, price, years, platform, publisher):
    f = selection(genre, price, years, platform, publisher)
    if not len(f):
        return [html.H2("No games match these filters. Try a wider selection or press Reset.", className="lede wide")]
    return TABS[tab](f)


@app.callback(Output("tab", "value"), Input("url", "search"))
def open_tab_from_link(search):
    """?tab=why in the address opens that tab (handy during the presentation)."""
    wanted = (search or "").replace("?tab=", "")
    return wanted if wanted in TABS else "overview"


@app.callback(Output("genre", "value"), Output("price", "value"), Output("years", "value"),
              Output("platform", "value"), Output("publisher", "value"),
              Input("reset", "n_clicks"), prevent_initial_call=True)
def reset_filters(n_clicks):
    return [], [], YEARS, "All", "All"


# =============================================================================
# 6. START THE APP
# =============================================================================
if __name__ == "__main__":
    app.run(debug=False, port=8050)

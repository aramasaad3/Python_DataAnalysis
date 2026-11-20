"""
STEP 3 - VISUALISE  (Plotly, one function per chart)

Each function takes a table from analysis.py and returns a Plotly figure.
CHARTS below says, for every figure, which QUESTION it answers and WHY we chose that chart type -
the dashboard shows this text under each chart.
"""
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------------- colours (Steam-style dark theme)
CARD, GRID, TEXT, MUTED = "#16222e", "#26384a", "#e6edf3", "#93a7ba"
ACCENT = "#66c0f4"                      # Steam blue, used for single-series charts
RED, GREEN, GRAY = "#e66767", "#2fbf71", "#6b7f93"
# colour-blind-checked categorical palette (dark-mode steps)
PALETTE = ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#0ca30c", "#9085e9", "#e66767"]
OUTCOME_COLORS = {"Failed": RED, "Small": GRAY, "Solid": "#3987e5", "Hit": GREEN}
PLATFORM_COLORS = {"Windows only": GRAY, "Windows + Mac": "#3987e5", "Windows + Linux": "#c98500",
                   "Windows + Mac + Linux": "#199e70"}

# ---------------------------------------------------------------- what each chart is for
CHARTS = {
    1: ("Bar chart", "How did we clean the data?",
        "each bar is the number of games left after one cleaning step, from the raw file at the top.",
        "A bar per step makes it easy to see how many games each cleaning rule removed."),
    2: ("Line chart", "Is Steam getting crowded?",
        "each point is the number of games released that year. The dotted lines mark when Steam opened its "
        "store to everyone.",
        "A line chart is the best chart for a trend over time."),
    3: ("Bar chart", "Are new games noticed less than old ones?",
        "each bar is the share of that year's games that failed (fewer than 10 reviews). Older games had "
        "more years to collect reviews, so part of the rise is their age.",
        "Years are categories we want to compare side by side, which is what bars do."),
    4: ("Heatmap", "Is it one genre, or every genre?",
        "each square is one genre in one year; the redder it is, the more of those games failed. "
        "Empty squares had fewer than 30 games.",
        "A heatmap shows two things at once (genre AND year) with colour."),
    5: ("Horizontal bar chart", "Which genres are most crowded?",
        "each bar is the number of games in that genre. A game can belong to several genres.",
        "We rank categories, and horizontal bars leave room for long genre names."),
    6: ("Box plot", "Which genres do players like most?",
        "each box shows the review scores of a genre: the line is the typical (median) game, the box holds "
        "the middle half. Only games with 10+ reviews.",
        "A box plot compares the spread of a number across groups."),
    7: ("Histogram", "What do games cost?",
        "each bar counts the paid games in a $1 price range. Prices above $60 are grouped at the end.",
        "A histogram shows how one number (price) is spread out."),
    8: ("100% stacked bar chart", "Does the price change the outcome?",
        "each bar is one price range split into outcomes: red failed, gray small, blue solid, green hit.",
        "A 100% stacked bar shows the mix inside each group, so groups of different sizes can be compared."),
    9: ("Bubble chart", "Which genres are the best bet?",
        "each bubble is a genre. Further right = more hits, lower = fewer failures, so the bottom-right corner "
        "is the best bet. Bigger bubble = more games (more competition); brighter = better reviews.",
        "A bubble chart shows four numbers per genre at once: x, y, size and colour."),
    10: ("Treemap", "Who owns the most-played games?",
         "each box is a publisher; the bigger the box, the more reviews its games collected.",
         "A treemap shows parts of a whole when there are many groups."),
    11: ("Donut chart", "Do games bother with Mac and Linux?",
         "each slice is the share of games that run on that set of platforms.",
         "There are only 4 groups, so a donut shows their share of the whole clearly."),
    12: ("Cumulative line (Pareto)", "Do a few games take all the players?",
         "start from the most-reviewed game and move right: the line shows what share of ALL reviews the "
         "top games hold. The dashed line is what a fair split would look like.",
         "A cumulative line shows concentration: how much the top few hold."),
    13: ("Scatter plot", "Do good games get more players?",
         "each dot is one game (a random sample of 4,000). Right = more reviews (each step is 10× more), "
         "up = better score.",
         "A scatter plot shows the relationship between two numbers."),
    14: ("Grouped bar chart", "What do successful launches do differently?",
         "for each launch signal, the gray bar is the failure rate of games WITHOUT it and the blue bar of "
         "games WITH it.",
         "Grouped bars compare two groups side by side for several categories."),
    15: ("Grouped bar chart", "Does doing more of them help more?",
         "games are grouped by how many of the 4 signals they have (0 to 4). Red = % failed, green = % hits.",
         "Bars for each group show the trend clearly; both numbers are percentages so they share one axis."),
}


def style(fig, height=380, legend=True):
    fig.update_layout(
        template="plotly_dark", height=height, paper_bgcolor=CARD, plot_bgcolor=CARD,
        font=dict(family="Inter, Segoe UI, sans-serif", size=14, color=MUTED),
        margin=dict(l=8, r=12, t=30, b=8), showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0, title_text="", font=dict(color=TEXT)),
        hoverlabel=dict(bgcolor="#0f1923", bordercolor=GRID, font=dict(color=TEXT, size=13)),
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False, linecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, zeroline=False, linecolor=GRID)
    return fig


# ---------------------------------------------------------------- overview
def cleaning_funnel(steps):
    t = steps.iloc[::-1]
    fig = go.Figure(go.Bar(x=t["games"], y=t["step"], orientation="h", marker_color=ACCENT,
                           text=[f"{v:,}" for v in t["games"]], textposition="outside", cliponaxis=False,
                           hovertemplate="%{y}: %{x:,} games<extra></extra>"))
    fig.update_layout(bargap=0.35, barcornerradius=4)
    fig.update_xaxes(showticklabels=False, showgrid=False, range=[0, steps["games"].max() * 1.15])
    return style(fig, height=300, legend=False)


# ---------------------------------------------------------------- 01 WHEN
def releases_per_year(t):
    fig = go.Figure(go.Scatter(x=t["year"], y=t["games"], mode="lines+markers", line=dict(color=ACCENT, width=3),
                               marker=dict(size=7), fill="tozeroy", fillcolor="rgba(102,192,244,0.12)",
                               hovertemplate="%{x}: %{y:,} games<extra></extra>"))
    for year, label in [(2012, "Steam Greenlight<br>opens the store"), (2017, "Steam Direct:<br>anyone can publish")]:
        if len(t) and t["year"].min() <= year <= t["year"].max():
            fig.add_vline(x=year, line=dict(color=MUTED, dash="dot", width=1))
            fig.add_annotation(x=year, y=t["games"].max(), text=label, showarrow=False, xanchor="right",
                               xshift=-6, yanchor="top", align="right", font=dict(size=12, color=TEXT))
    fig.update_yaxes(title="Games released")
    return style(fig, legend=False)


def failure_by_year(t):
    fig = go.Figure(go.Bar(x=t["year"], y=t["failed"] * 100, marker_color=RED,
                           customdata=t["games"], hovertemplate="%{x}: %{y:.0f}% failed (of %{customdata:,} games)<extra></extra>"))
    fig.update_layout(bargap=0.2, barcornerradius=4)
    fig.update_yaxes(title="Games that failed (%)", ticksuffix="%", range=[0, 100])
    return style(fig, legend=False)


def failure_heatmap(grid):
    text = grid.apply(lambda c: c.map(lambda v: "" if np.isnan(v) else f"{v:.0%}"))
    fig = go.Figure(go.Heatmap(
        z=grid.values * 100, x=[str(c) for c in grid.columns], y=list(grid.index), text=text.values,
        texttemplate="%{text}", textfont=dict(size=11), zmin=0, zmax=100, xgap=2, ygap=2, hoverongaps=False,
        colorscale=[[0, "#1f3346"], [0.5, "#9b3f4a"], [1, "#ff6b6b"]],
        colorbar=dict(title="Failed", ticksuffix="%", thickness=12),
        hovertemplate="%{y}, %{x}: %{z:.0f}% failed<extra></extra>"))
    fig.update_yaxes(autorange="reversed", showgrid=False)
    fig.update_xaxes(showgrid=False)
    return style(fig, height=430, legend=False)


# ---------------------------------------------------------------- 02 WHAT
def genre_counts(t):
    fig = go.Figure(go.Bar(x=t["games"], y=t["genre"], orientation="h", marker_color=ACCENT,
                           text=[f"{v:,}" for v in t["games"]], textposition="outside", cliponaxis=False,
                           customdata=t["failed"] * 100,
                           hovertemplate="%{y}: %{x:,} games, %{customdata:.0f}% failed<extra></extra>"))
    fig.update_layout(bargap=0.3, barcornerradius=4)
    fig.update_xaxes(title="Games", range=[0, t["games"].max() * 1.18] if len(t) else None)
    return style(fig, height=430, legend=False)


def genre_scores(g, order):
    fig = px.box(g, x="genre", y="score", category_orders={"genre": order}, points=False,
                 color_discrete_sequence=[ACCENT])
    fig.update_traces(line_width=1.5, fillcolor="rgba(102,192,244,0.25)",
                      hovertemplate="%{x}<br>score %{y:.0f}%<extra></extra>")
    fig.update_xaxes(title=None, tickangle=-30)
    fig.update_yaxes(title="Positive reviews (%)", ticksuffix="%", range=[0, 101])
    return style(fig, height=430, legend=False)


def price_distribution(paid):
    fig = go.Figure(go.Histogram(x=paid["price"].clip(upper=60), xbins=dict(start=0, end=61, size=1),
                                 marker_color=ACCENT, hovertemplate="$%{x}: %{y:,} games<extra></extra>"))
    fig.update_layout(bargap=0.08)
    fig.update_xaxes(title="Price (USD)", tickprefix="$")
    fig.update_yaxes(title="Paid games")
    return style(fig, legend=False)


def outcome_by_price(share):
    fig = go.Figure()
    for o in share.columns:
        fig.add_trace(go.Bar(x=share.index, y=share[o], name=o, marker_color=OUTCOME_COLORS[o],
                             text=[f"{v:.0f}%" if v >= 6 else "" for v in share[o]], textposition="inside",
                             insidetextanchor="middle", textfont=dict(color="#ffffff"),
                             hovertemplate=f"%{{x}}: %{{y:.0f}}% {o.lower()}<extra></extra>"))
    fig.update_layout(barmode="stack", bargap=0.3)
    fig.update_traces(marker_line_color=CARD, marker_line_width=1.5)
    fig.update_yaxes(title="Share of games (%)", ticksuffix="%", range=[0, 100])
    return style(fig)


def genre_bubbles(t):
    d = t.assign(hit_pct=t["hit"] * 100, failed_pct=t["failed"] * 100)
    fig = px.scatter(d, x="hit_pct", y="failed_pct", size="games", color="score", hover_name="genre", size_max=38,
                     color_continuous_scale=[[0, "#1f4f7a"], [1, "#9fe0ff"]],
                     labels={"hit_pct": "Games that became hits (%)", "failed_pct": "Games that failed (%)",
                             "score": "Review score"},
                     hover_data={"games": ":,", "score": ":.0f"})
    fig.update_traces(marker=dict(line=dict(width=1, color=CARD), opacity=0.8))
    # genres sit close together, so each label gets its own offset and a thin leader line
    offsets = {"Indie": (-55, 28), "Casual": (-62, 24), "Early Access": (55, -16), "Action": (40, 26),
               "Adventure": (-20, -34), "Simulation": (-62, -26), "Strategy": (48, -16), "RPG": (40, 16),
               "Sports": (-55, -6), "Racing": (0, 32), "Free To Play": (60, 0), "Massively Multiplayer": (0, -22)}
    for _, r in d.iterrows():
        ax, ay = offsets.get(r["genre"], (30, -20))
        fig.add_annotation(x=r["hit_pct"], y=r["failed_pct"], text=r["genre"], ax=ax, ay=ay, showarrow=True,
                           arrowhead=0, arrowwidth=1, arrowcolor=MUTED, standoff=4, font=dict(color=TEXT, size=12))
    fig.update_layout(coloraxis_colorbar=dict(title="Score", ticksuffix="%", thickness=12))
    fig.update_xaxes(ticksuffix="%", range=[0, max(18, d["hit_pct"].max() * 1.25)])
    fig.update_yaxes(ticksuffix="%", autorange="reversed")
    fig.add_annotation(xref="paper", yref="paper", x=0.98, y=0.04, text="Best bet: more hits, fewer failures",
                       showarrow=False, xanchor="right", font=dict(color=GREEN, size=13))
    return style(fig, height=450, legend=False)


# ---------------------------------------------------------------- 03 WHO
def top_publishers(top):
    fig = px.treemap(top, path=[px.Constant("Top publishers"), "publisher"], values="reviews",
                     color="reviews", color_continuous_scale=[[0, "#1f4f7a"], [1, "#66c0f4"]],
                     custom_data=["games"])
    fig.update_traces(texttemplate="<b>%{label}</b><br>%{percentRoot:.0%} of their reviews",
                      hovertemplate="<b>%{label}</b><br>%{value:,} reviews<br>%{customdata[0]:,} games<extra></extra>",
                      marker=dict(line=dict(color=CARD, width=2)), root_color=CARD, tiling=dict(pad=2))
    fig.update_layout(coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0))
    return style(fig, height=460, legend=False)


def platform_share(t):
    fig = go.Figure(go.Pie(labels=t["platform"], values=t["games"], hole=0.6, sort=False, direction="clockwise",
                           marker=dict(colors=[PLATFORM_COLORS[p] for p in t["platform"]],
                                       line=dict(color=CARD, width=2)),
                           texttemplate="%{percent:.0%}", textposition="inside",
                           hovertemplate="%{label}: %{value:,} games (%{percent})<extra></extra>"))
    fig.add_annotation(text=f"<b>{t['games'].sum():,}</b><br>games", showarrow=False, font=dict(size=18, color=TEXT))
    fig.update_layout(uniformtext_minsize=11, uniformtext_mode="hide",
                      legend=dict(orientation="v", x=1.0, y=0.5, yanchor="middle"))
    return style(fig)


# ---------------------------------------------------------------- 04 WHY
def winner_takes_all(t):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, 100], y=[0, 100], mode="lines", name="Fair split",
                             line=dict(color=MUTED, dash="dash", width=1.5), hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=t["games"], y=t["reviews"], mode="lines", name="Real split", fill="tozeroy",
                             fillcolor="rgba(102,192,244,0.15)", line=dict(color=ACCENT, width=3),
                             hovertemplate="Top %{x:.1f}% of games hold %{y:.0f}% of reviews<extra></extra>"))
    if len(t):
        y1 = float(np.interp(1, t["games"], t["reviews"]))
        fig.add_annotation(x=1, y=y1, ax=60, ay=40, text=f"Top 1% of games<br><b>{y1:.0f}% of reviews</b>",
                           font=dict(color=TEXT, size=13), arrowcolor=TEXT, align="left")
    fig.update_xaxes(title="Share of games, most-reviewed first (%)", ticksuffix="%", range=[0, 100])
    fig.update_yaxes(title="Share of all reviews (%)", ticksuffix="%", range=[0, 102])
    return style(fig)


def quality_vs_popularity(pts):
    order = ["Small", "Solid", "Hit"]
    fig = px.scatter(pts, x="reviews", y="score", color="outcome", log_x=True, opacity=0.55,
                     color_discrete_map=OUTCOME_COLORS, category_orders={"outcome": order}, hover_name="name",
                     labels={"reviews": "Number of reviews (log scale)", "score": "Positive reviews (%)",
                             "outcome": "Outcome"})
    fig.update_traces(marker=dict(size=5))
    fig.add_hrect(y0=80, y1=101, x0=0, x1=0.25, xref="paper", fillcolor="rgba(230,103,103,0.10)", line_width=0)
    fig.add_annotation(xref="paper", x=0.01, y=97, text="Loved, but unseen", showarrow=False, xanchor="left",
                       font=dict(color=RED, size=13))
    fig.update_yaxes(ticksuffix="%", range=[0, 101])
    return style(fig, height=430)


def signal_effect(t):
    fig = go.Figure()
    fig.add_trace(go.Bar(y=t["signal"], x=t["Without"], name="Without it", orientation="h", marker_color=GRAY,
                         text=[f"{v:.0f}%" for v in t["Without"]], textposition="outside",
                         hovertemplate="%{y}<br>without: %{x:.0f}% failed<extra></extra>"))
    fig.add_trace(go.Bar(y=t["signal"], x=t["With"], name="With it", orientation="h", marker_color=ACCENT,
                         text=[f"{v:.0f}%" for v in t["With"]], textposition="outside",
                         hovertemplate="%{y}<br>with: %{x:.0f}% failed<extra></extra>"))
    fig.update_layout(barmode="group", bargap=0.3, bargroupgap=0.08, barcornerradius=4)
    fig.update_xaxes(title="Games that failed (%)", ticksuffix="%", range=[0, 75])
    fig.update_yaxes(autorange="reversed")
    return style(fig)


def signal_dose(t):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=t["signals"], y=t["failed"], name="% failed", marker_color=RED,
                         text=[f"{v:.0f}%" for v in t["failed"]], textposition="outside",
                         customdata=t["games"], hovertemplate="%{x} signals: %{y:.0f}% failed (%{customdata:,} games)<extra></extra>"))
    fig.add_trace(go.Bar(x=t["signals"], y=t["hit"], name="% hits", marker_color=GREEN,
                         text=[f"{v:.0f}%" for v in t["hit"]], textposition="outside",
                         customdata=t["games"], hovertemplate="%{x} signals: %{y:.0f}% hits (%{customdata:,} games)<extra></extra>"))
    fig.update_layout(barmode="group", bargap=0.25, bargroupgap=0.06, barcornerradius=4)
    fig.update_xaxes(title="Number of launch signals (0 = none, 4 = all)", dtick=1)
    fig.update_yaxes(title="Share of games (%)", ticksuffix="%", range=[0, 75])
    return style(fig)

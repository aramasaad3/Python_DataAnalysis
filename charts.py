"""
STEP 3 - VISUALISE  (Plotly, one function per chart)

Each chart function takes a table from analysis.py and returns a Plotly figure.
CHART_INFO says, for every chart: the question, how to read it, why we chose it,
why not another chart, and another chart that would also fit. The dashboard shows
these under every chart, and the presentation uses them as speaker notes.
"""
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

# ---------------------------------------------------------------- one look for every chart
# White background + Okabe-Ito colours (designed to be readable for colour-blind people)
BLUE, ORANGE, GREEN, PINK, SKY, VERMILLION, GRAY = (
    "#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00", "#999999")
INK, INK2, RULE = "#1d2433", "#5b6474", "#e4e2dc"
pio.templates["plotly_white"].layout.colorway = [BLUE, ORANGE, GREEN, PINK, SKY, VERMILLION, GRAY]
px.defaults.template = "plotly_white"

OUTCOME_COLORS = {"Failed": VERMILLION, "Small": GRAY, "Solid": SKY, "Hit": GREEN}
PLATFORM_COLORS = {"Windows only": GRAY, "Windows + Mac": BLUE, "Windows + Linux": ORANGE,
                   "Windows + Mac + Linux": GREEN}
BLUES = [[0, "#d9e8f3"], [1, BLUE]]
ORANGES = [[0, "#fdf1e8"], [0.5, "#f0a46c"], [1, VERMILLION]]

# ---------------------------------------------------------------- what each chart is for
# number: (chart type, question, how to read, why we chose it, why not another, another that would fit)
CHART_INFO = {
    1: ("Horizontal bar chart", "How did we clean the data?",
        "Each bar is the number of games left after one cleaning step, starting from the raw file at the top.",
        "We want to show how many games each cleaning rule removed. One bar per step makes the drop easy to see.",
        "A pie chart cannot show steps in order. A line chart would suggest a trend over time, but these are steps.",
        "A funnel chart: the same idea, drawn as a narrowing funnel."),
    2: ("Line chart", "Is Steam getting crowded?",
        "Each point is the number of games released that year. The dotted lines mark when Steam opened its store "
        "to everyone (Greenlight 2012, Direct 2017).",
        "We want to see how releases changed over time. A line chart is the chart for a trend over time.",
        "A pie chart cannot show change over time. A bar chart works, but with 19 bars the trend is harder to follow.",
        "An area chart: the same trend with the space under the line filled in."),
    3: ("Bar chart", "Are new games noticed less than old ones?",
        "Each bar is the share of that year's games that failed (fewer than 10 reviews). Older games had more years "
        "to collect reviews, so part of the rise is their age.",
        "We want to compare the failure rate of each year. Years are categories here, and bars compare categories.",
        "A pie cannot compare 17 years. A stacked bar would hide the one number we care about (the failure rate).",
        "A line chart, because the years have an order."),
    4: ("Heatmap", "Is it one genre, or every genre?",
        "Each square is one genre in one year; the darker the orange, the more of those games failed. Empty squares "
        "had fewer than 30 games.",
        "We want to look at two things at once: the genre AND the year. A heatmap shows a number for every pair "
        "with colour.",
        "12 line charts (one per genre) would be too crowded. A grouped bar with 12 × 11 bars is unreadable.",
        "Small multiples: one small bar chart per genre."),
    5: ("Horizontal bar chart", "Which genres are most crowded?",
        "Each bar is the number of games in that genre. A game can belong to several genres.",
        "We want to rank the genres by size. Bars compare categories, and horizontal bars leave room for the names.",
        "A pie with 12 slices is too many (lecture rule). A line chart would connect genres that have no order.",
        "A treemap: one box per genre, sized by the number of games."),
    6: ("Box plot", "Which genres do players like most?",
        "Each box shows the review scores of one genre: the line is the typical (median) game and the box holds the "
        "middle half of the games. Only games with 10+ reviews.",
        "We want to compare the spread of review scores across genres. A box plot shows the median, the middle half "
        "and the outliers for each group.",
        "A bar of averages hides the spread and is pulled by extreme values. A histogram per genre takes 12 charts.",
        "A violin plot: the same comparison, showing the full shape of each distribution."),
    7: ("Histogram", "What do games cost?",
        "Each bar counts the paid games in a $1 price range. Prices above $60 are grouped at the end.",
        "We want to see how one number (price) is spread out. A histogram shows that most games are cheap.",
        "A bar chart is for named groups, not for a continuous number like price. A box plot hides the shape.",
        "A density plot (KDE): the smooth version of the histogram."),
    8: ("100% stacked bar chart", "Does the price change the outcome?",
        "Each bar is one price range split into outcomes: orange failed, gray small, light blue solid, green hit.",
        "We want to compare the MIX of outcomes inside each price range. A 100% stacked bar makes every bar the "
        "same height, so groups of very different sizes can be compared.",
        "A normal stacked bar would be dominated by the cheap games (there are far more of them). Five pies are "
        "harder to compare side by side.",
        "A grouped bar chart: four bars (one per outcome) for each price range."),
    9: ("Bubble chart", "Which genres are the best bet?",
        "Each bubble is a genre. Further right = more hits, lower = fewer failures, so the bottom-right is the best "
        "bet. Bigger bubble = more games (more competition); darker = better reviews.",
        "We want to show four numbers per genre at once: hit rate (x), failure rate (y), number of games (size) and "
        "review score (colour). A bubble chart is a scatter plot that adds a third and fourth number.",
        "A bar chart can only show one number per genre. A table holds the numbers but hides the pattern.",
        "A scatter plot without sizes, with the number of games written as a label."),
    10: ("Treemap", "Who owns the most-played games?",
         "Each box is a publisher; the bigger the box, the more reviews its games collected.",
         "We want to show the share of each publisher in the whole, for 20 publishers. A treemap shows parts of a "
         "whole when there are many groups.",
         "A pie with 20 slices is unreadable (lecture rule: no pies with many slices).",
         "A sorted horizontal bar chart of the top 20 publishers."),
    11: ("Donut chart", "Do games bother with Mac and Linux?",
         "Each slice is the share of games that run on that set of platforms.",
         "There are only 4 groups and together they make 100% of the games, so a donut shows each share clearly.",
         "A line chart is for trends, not shares. A bar chart works but does not show 'part of the whole' as well.",
         "A 100% stacked bar with one bar."),
    12: ("Cumulative line (Pareto)", "Do a few games take all the players?",
         "Start from the most-reviewed game and move right: the line shows what share of ALL reviews the top games "
         "hold. The dashed line is what a fair split would look like.",
         "We want to show concentration: how much the top few games hold. A cumulative line shows it directly.",
         "A histogram of reviews is squashed against zero, because a few games have millions of reviews. A pie of "
         "87,000 games is impossible.",
         "A bar chart of the share held by the top 1%, 10% and 50% of games."),
    13: ("Scatter plot", "Do good games get more players?",
         "Each dot is one game (a random sample of 4,000). Right = more reviews (each step is 10× more), up = better "
         "score.",
         "We want to see the relationship between two numbers: quality (score) and popularity (reviews). A scatter "
         "plot is the chart for a relationship.",
         "A line chart would connect games that are not related. A bar chart cannot show 4,000 games.",
         "A hexbin / density heatmap, which handles many overlapping points."),
    14: ("Grouped bar chart", "What do successful launches do differently?",
         "For each launch signal, the gray bar is the failure rate of games WITHOUT it and the blue bar of games "
         "WITH it.",
         "We want to compare two groups (with / without) for four signals. Grouped bars put each pair side by side.",
         "A stacked bar would add the two rates together, which means nothing. Eight pies are hard to compare.",
         "A dot plot (dumbbell chart): two dots per signal joined by a line."),
    15: ("Grouped bar chart", "Does doing more of them help more?",
         "Games are grouped by how many of the 4 signals they have (0 to 4). Orange = % failed, green = % hits.",
         "We want to show how two percentages change as the number of signals goes up. Both are percentages, so "
         "they share one axis.",
         "Two separate y-axes (one per number) are confusing and easy to misread. A pie cannot show a trend.",
         "A line chart with two lines, because 0 to 4 has an order."),
}


def style(fig, height=440, legend=True):
    """The common look of every chart."""
    fig.update_layout(
        template="plotly_white", height=height, showlegend=legend,
        font=dict(family="IBM Plex Sans, Segoe UI, Arial, sans-serif", size=14, color=INK),
        margin=dict(l=10, r=16, t=36, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0, title_text=""),
        hoverlabel=dict(bgcolor="white", font=dict(size=13)),
    )
    fig.update_xaxes(gridcolor="#eeece6", zeroline=False, linecolor=RULE)
    fig.update_yaxes(gridcolor="#eeece6", zeroline=False, linecolor=RULE)
    return fig


# ---------------------------------------------------------------- 01 overview
def cleaning_funnel(steps):
    t = steps.iloc[::-1]
    fig = go.Figure(go.Bar(x=t["games"], y=t["step"], orientation="h", marker_color=BLUE,
                           text=[f"{v:,}" for v in t["games"]], textposition="outside", cliponaxis=False,
                           hovertemplate="%{y}: %{x:,} games<extra></extra>"))
    fig.update_layout(bargap=0.35)
    fig.update_xaxes(showticklabels=False, showgrid=False, range=[0, steps["games"].max() * 1.15])
    return style(fig, height=330, legend=False)


# ---------------------------------------------------------------- 02 when
def releases_per_year(t):
    fig = go.Figure(go.Scatter(x=t["year"], y=t["games"], mode="lines+markers", line=dict(color=BLUE, width=3),
                               marker=dict(size=7), hovertemplate="%{x}: %{y:,} games<extra></extra>"))
    for year, label in [(2012, "Steam Greenlight<br>opens the store"), (2017, "Steam Direct:<br>anyone can publish")]:
        if len(t) and t["year"].min() <= year <= t["year"].max():
            fig.add_vline(x=year, line=dict(color=INK2, dash="dot", width=1))
            fig.add_annotation(x=year, y=t["games"].max(), text=label, showarrow=False, xanchor="right", xshift=-6,
                               yanchor="top", align="right", font=dict(size=12, color=INK2))
    fig.update_yaxes(title="Games released")
    return style(fig, legend=False)


def failure_by_year(t):
    fig = go.Figure(go.Bar(x=t["year"], y=t["failed"] * 100, marker_color=VERMILLION, customdata=t["games"],
                           hovertemplate="%{x}: %{y:.0f}% failed (of %{customdata:,} games)<extra></extra>"))
    fig.update_layout(bargap=0.2)
    fig.update_yaxes(title="Games that failed (%)", ticksuffix="%", range=[0, 100])
    return style(fig, legend=False)


def failure_heatmap(grid):
    text = grid.apply(lambda c: c.map(lambda v: "" if np.isnan(v) else f"{v:.0%}"))
    fig = go.Figure(go.Heatmap(
        z=grid.values * 100, x=[str(c) for c in grid.columns], y=list(grid.index), text=text.values,
        texttemplate="%{text}", textfont=dict(size=11), zmin=0, zmax=100, xgap=2, ygap=2, hoverongaps=False,
        colorscale=ORANGES, colorbar=dict(title="Failed", ticksuffix="%", thickness=12),
        hovertemplate="%{y}, %{x}: %{z:.0f}% failed<extra></extra>"))
    fig.update_yaxes(autorange="reversed", showgrid=False)
    fig.update_xaxes(showgrid=False)
    return style(fig, height=470, legend=False)


# ---------------------------------------------------------------- 03 what
def genre_counts(t):
    fig = go.Figure(go.Bar(x=t["games"], y=t["genre"], orientation="h", marker_color=BLUE,
                           text=[f"{v:,}" for v in t["games"]], textposition="outside", cliponaxis=False,
                           customdata=t["failed"] * 100,
                           hovertemplate="%{y}: %{x:,} games, %{customdata:.0f}% failed<extra></extra>"))
    fig.update_layout(bargap=0.3)
    fig.update_xaxes(title="Games", range=[0, t["games"].max() * 1.18] if len(t) else None)
    return style(fig, height=470, legend=False)


def genre_scores(g, order):
    fig = px.box(g, x="genre", y="score", category_orders={"genre": order}, points=False,
                 color_discrete_sequence=[BLUE])
    fig.update_traces(line_width=1.5, hovertemplate="%{x}<br>score %{y:.0f}%<extra></extra>")
    fig.update_xaxes(title=None, tickangle=-30)
    fig.update_yaxes(title="Positive reviews (%)", ticksuffix="%", range=[0, 101])
    return style(fig, height=470, legend=False)


def price_distribution(paid):
    fig = go.Figure(go.Histogram(x=paid["price"].clip(upper=60), xbins=dict(start=0, end=61, size=1),
                                 marker_color=BLUE, hovertemplate="$%{x}: %{y:,} games<extra></extra>"))
    fig.update_layout(bargap=0.08)
    fig.update_xaxes(title="Price (USD)", tickprefix="$")
    fig.update_yaxes(title="Paid games")
    return style(fig, legend=False)


def outcome_by_price(share):
    fig = go.Figure()
    for o in share.columns:
        fig.add_trace(go.Bar(x=share.index, y=share[o], name=o, marker_color=OUTCOME_COLORS[o],
                             text=[f"{v:.0f}%" if v >= 6 else "" for v in share[o]], textposition="inside",
                             insidetextanchor="middle",
                             hovertemplate=f"%{{x}}: %{{y:.0f}}% {o.lower()}<extra></extra>"))
    fig.update_layout(barmode="stack", bargap=0.3)
    fig.update_traces(marker_line_color="white", marker_line_width=1.5)
    fig.update_yaxes(title="Share of games (%)", ticksuffix="%", range=[0, 100])
    return style(fig)


def genre_bubbles(t):
    d = t.assign(hit_pct=t["hit"] * 100, failed_pct=t["failed"] * 100)
    fig = px.scatter(d, x="hit_pct", y="failed_pct", size="games", color="score", hover_name="genre", size_max=38,
                     color_continuous_scale=[[0, "#9cc6e4"], [1, "#08467a"]],   # light end still visible on paper
                     labels={"hit_pct": "Games that became hits (%)", "failed_pct": "Games that failed (%)",
                             "score": "Review score"},
                     hover_data={"games": ":,", "score": ":.0f"})
    fig.update_traces(marker=dict(line=dict(width=1, color=INK2), opacity=0.9))
    # genres sit close together, so each label gets its own offset and a thin leader line
    offsets = {"Indie": (-55, 28), "Casual": (-62, 24), "Early Access": (55, -16), "Action": (40, 26),
               "Adventure": (-20, -34), "Simulation": (-62, -26), "Strategy": (48, -16), "RPG": (40, 16),
               "Sports": (-55, -6), "Racing": (0, 32), "Free To Play": (60, 0), "Massively Multiplayer": (0, -22)}
    for _, r in d.iterrows():
        ax, ay = offsets.get(r["genre"], (30, -20))
        fig.add_annotation(x=r["hit_pct"], y=r["failed_pct"], text=r["genre"], ax=ax, ay=ay, showarrow=True,
                           arrowhead=0, arrowwidth=1, arrowcolor=INK2, standoff=4, font=dict(color=INK, size=12))
    fig.update_layout(coloraxis_colorbar=dict(title="Score", ticksuffix="%", thickness=12))
    fig.update_xaxes(ticksuffix="%", range=[0, max(18, d["hit_pct"].max() * 1.25)])
    # reversed axis (fewer failures = higher up), with room so no bubble is cut off at the edge
    fig.update_yaxes(ticksuffix="%", range=[d["failed_pct"].max() + 4, d["failed_pct"].min() - 4])
    fig.add_annotation(xref="paper", yref="paper", x=0.98, y=0.04, text="Best bet: more hits, fewer failures",
                       showarrow=False, xanchor="right", font=dict(color=GREEN, size=13))
    return style(fig, height=480, legend=False)


# ---------------------------------------------------------------- 04 who
def top_publishers(top):
    fig = px.treemap(top, path=[px.Constant("Top publishers"), "publisher"], values="reviews",
                     color="reviews", color_continuous_scale=BLUES, custom_data=["games"])
    fig.update_traces(texttemplate="<b>%{label}</b><br>%{percentRoot:.0%} of their reviews",
                      hovertemplate="<b>%{label}</b><br>%{value:,} reviews<br>%{customdata[0]:,} games<extra></extra>",
                      marker=dict(line=dict(color="white", width=2)), root_color="#f6f5f1", tiling=dict(pad=2))
    fig.update_layout(coloraxis_showscale=False)
    fig = style(fig, height=480, legend=False)
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    return fig


def platform_share(t):
    fig = go.Figure(go.Pie(labels=t["platform"], values=t["games"], hole=0.6, sort=False, direction="clockwise",
                           marker=dict(colors=[PLATFORM_COLORS[p] for p in t["platform"]],
                                       line=dict(color="white", width=2)),
                           texttemplate="%{percent:.0%}", textposition="inside",
                           hovertemplate="%{label}: %{value:,} games (%{percent})<extra></extra>"))
    fig.add_annotation(text=f"<b>{t['games'].sum():,}</b><br>games", showarrow=False, font=dict(size=18, color=INK))
    fig = style(fig)
    fig.update_layout(uniformtext_minsize=11, uniformtext_mode="hide",
                      legend=dict(orientation="v", x=1.0, y=0.5, yanchor="middle"))
    return fig


# ---------------------------------------------------------------- 05 why
def winner_takes_all(t):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, 100], y=[0, 100], mode="lines", name="Fair split",
                             line=dict(color=INK2, dash="dash", width=1.5), hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=t["games"], y=t["reviews"], mode="lines", name="Real split", fill="tozeroy",
                             fillcolor="rgba(0,114,178,0.12)", line=dict(color=BLUE, width=3),
                             hovertemplate="Top %{x:.1f}% of games hold %{y:.0f}% of reviews<extra></extra>"))
    if len(t):
        y1 = float(np.interp(1, t["games"], t["reviews"]))
        fig.add_annotation(x=1, y=y1, ax=120, ay=70, text=f"Top 1% of games<br><b>{y1:.0f}% of reviews</b>",
                           font=dict(color=INK, size=13), arrowcolor=INK, align="left")
    fig.update_xaxes(title="Share of games, most-reviewed first (%)", ticksuffix="%", range=[0, 100])
    fig.update_yaxes(title="Share of all reviews (%)", ticksuffix="%", range=[0, 102])
    return style(fig)


def quality_vs_popularity(pts):
    order = ["Small", "Solid", "Hit"]
    fig = px.scatter(pts, x="reviews", y="score", color="outcome", log_x=True, opacity=0.5,
                     color_discrete_map=OUTCOME_COLORS, category_orders={"outcome": order}, hover_name="name",
                     labels={"reviews": "Number of reviews (log scale)", "score": "Positive reviews (%)",
                             "outcome": "Outcome"})
    fig.update_traces(marker=dict(size=5))
    fig.add_hrect(y0=80, y1=101, x0=0, x1=0.25, xref="paper", fillcolor="rgba(213,94,0,0.08)", line_width=0)
    fig.add_annotation(xref="paper", x=0.01, y=97, text="Loved, but unseen", showarrow=False, xanchor="left",
                       font=dict(color=VERMILLION, size=13))
    fig.update_yaxes(ticksuffix="%", range=[0, 101])
    return style(fig, height=470)


def signal_effect(t):
    fig = go.Figure()
    fig.add_trace(go.Bar(y=t["signal"], x=t["Without"], name="Without it", orientation="h", marker_color=GRAY,
                         text=[f"{v:.0f}%" for v in t["Without"]], textposition="outside",
                         hovertemplate="%{y}<br>without: %{x:.0f}% failed<extra></extra>"))
    fig.add_trace(go.Bar(y=t["signal"], x=t["With"], name="With it", orientation="h", marker_color=BLUE,
                         text=[f"{v:.0f}%" for v in t["With"]], textposition="outside",
                         hovertemplate="%{y}<br>with: %{x:.0f}% failed<extra></extra>"))
    fig.update_layout(barmode="group", bargap=0.3, bargroupgap=0.08)
    fig.update_xaxes(title="Games that failed (%)", ticksuffix="%", range=[0, 75])
    fig.update_yaxes(autorange="reversed")
    return style(fig)


def signal_dose(t):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=t["signals"], y=t["failed"], name="% failed", marker_color=VERMILLION,
                         text=[f"{v:.0f}%" for v in t["failed"]], textposition="outside", customdata=t["games"],
                         hovertemplate="%{x} signals: %{y:.0f}% failed (%{customdata:,} games)<extra></extra>"))
    fig.add_trace(go.Bar(x=t["signals"], y=t["hit"], name="% hits", marker_color=GREEN,
                         text=[f"{v:.0f}%" for v in t["hit"]], textposition="outside", customdata=t["games"],
                         hovertemplate="%{x} signals: %{y:.0f}% hits (%{customdata:,} games)<extra></extra>"))
    fig.update_layout(barmode="group", bargap=0.25, bargroupgap=0.06)
    fig.update_xaxes(title="Number of launch signals (0 = none, 4 = all)", dtick=1)
    fig.update_yaxes(title="Share of games (%)", ticksuffix="%", range=[0, 75])
    return style(fig)

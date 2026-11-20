"""
STEP 2 - ANALYSE THE DATA  (pandas only, no charts here)

Every function takes the FILTERED table of games and returns:
    (table for the chart, one-sentence key point)
so the same numbers are used by the dashboard and the presentation.

Definitions used everywhere:
    Failed = fewer than 10 reviews   (almost nobody played it)
    Hit    = 1,000 or more reviews   (a successful game)
    Score  = % of positive reviews   (only for games with 10+ reviews)
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).parent / "data"

GENRES = ["Indie", "Casual", "Action", "Adventure", "Simulation", "Strategy", "RPG",
          "Free To Play", "Early Access", "Sports", "Racing", "Massively Multiplayer"]
PRICE_BANDS = ["Free", "Under $5", "$5–15", "$15–30", "$30+"]
OUTCOMES = ["Failed", "Small", "Solid", "Hit"]
OUTCOME_HELP = {"Failed": "under 10 reviews", "Small": "10–99", "Solid": "100–999", "Hit": "1,000+"}
PLATFORMS = ["Windows only", "Windows + Mac", "Windows + Linux", "Windows + Mac + Linux"]
SIGNALS = {
    "sig_languages": "Translated into 4+ languages",
    "sig_achievements": "Has Steam achievements",
    "sig_mac": "Has a Mac version",
    "sig_publisher": "Has a publisher (not self-published)",
}


def pct(x):
    return f"{x:.0%}"


# ---------------------------------------------------------------- loading and filtering
def load_games():
    return pd.read_parquet(DATA / "games_clean.parquet")


def load_cleaning_report():
    return json.loads((DATA / "cleaning_report.json").read_text(encoding="utf-8"))


def apply_filters(df, years, genres, prices, platform, publisher_type):
    """One place where all filters are applied, so every chart sees the same games."""
    out = df[df["year"].between(*years)]
    if genres:
        out = out[out["genres"].str.contains("|".join(genres), regex=True)]
    if prices:
        out = out[out["price_band"].isin(prices)]
    if platform == "Has a Mac version":
        out = out[out["mac"]]
    elif platform == "Has a Linux version":
        out = out[out["linux"]]
    elif platform == "Windows only":
        out = out[out["platform"] == "Windows only"]
    if publisher_type == "Self-published":
        out = out[out["self_published"]]
    elif publisher_type == "Has a publisher":
        out = out[~out["self_published"]]
    return out


def explode_genres(df):
    """A game can have several genres: one row per (game, genre)."""
    g = df.assign(genre=df["genres"].str.split("|")).explode("genre")
    return g[g["genre"].isin(GENRES)]


def kpis(df):
    reviews = df["reviews"].sort_values(ascending=False)
    top = max(1, len(reviews) // 100)
    return {
        "games": len(df),
        "failed": df["failed"].mean() if len(df) else np.nan,
        "hit": df["hit"].mean() if len(df) else np.nan,
        "median_reviews": df["reviews"].median() if len(df) else np.nan,
        "top1_share": reviews.head(top).sum() / reviews.sum() if reviews.sum() else np.nan,
    }


# ---------------------------------------------------------------- overview
def cleaning_funnel():
    steps = pd.DataFrame(load_cleaning_report())
    kept = steps["games"].iloc[-1] / steps["games"].iloc[0]
    return steps, (f"We kept <b>{steps['games'].iloc[-1]:,}</b> of {steps['games'].iloc[0]:,} Steam apps "
                   f"({pct(kept)}): real games, released 2006–2024, with enough time to collect reviews.")


# ---------------------------------------------------------------- 01 WHEN
def releases_per_year(df):
    t = df.groupby("year").size().rename("games").reset_index()
    if len(t) < 2:
        return t, "Select more years to see the trend."
    first, last = t.iloc[0], t.iloc[-1]
    return t, (f"<b>{int(last.games):,}</b> games came out in {int(last.year)}, "
               f"{last.games / max(first.games, 1):,.0f}× more than in {int(first.year)}.")


def failure_by_year(df):
    t = df.groupby("year").agg(games=("failed", "size"), failed=("failed", "mean")).reset_index()
    t = t[t["games"] >= 100]   # years with very few games give unreliable rates
    if t.empty:
        return t, "Not enough games in this selection."
    first, last = t.iloc[0], t.iloc[-1]
    return t, (f"In {int(first.year)}, {pct(first.failed)} of new games failed; in {int(last.year)} it was "
               f"<b>{pct(last.failed)}</b>. More games compete for the same players.")


def failure_heatmap(df, start=2014):
    g = explode_genres(df[df["year"] >= start])
    t = g.groupby(["genre", "year"]).agg(n=("failed", "size"), rate=("failed", "mean")).reset_index()
    t.loc[t["n"] < 30, "rate"] = np.nan   # too few games to trust the rate
    grid = t.pivot(index="genre", columns="year", values="rate")
    grid = grid.reindex([x for x in GENRES if x in grid.index])
    if grid.empty or grid.shape[1] < 2:
        return grid, "Not enough games in this selection."
    full = [c for c in grid.columns if grid[c].notna().sum() >= min(8, len(grid))]
    if len(full) < 2:
        return grid, "Not enough games per genre to compare years."
    first, last = full[0], full[-1]
    both = grid[[first, last]].dropna()
    rising = (both[last] > both[first]).sum()
    return grid, (f"Failure went up in <b>{rising} of {len(both)}</b> genres between {first} and {last}: "
                  f"the problem is not one genre, it is the whole store.")


# ---------------------------------------------------------------- 02 WHAT
def genre_counts(df):
    g = explode_genres(df)
    t = g.groupby("genre").agg(games=("AppID", "size"), failed=("failed", "mean"), hit=("hit", "mean"))
    t = t.sort_values("games").reset_index()
    if t.empty:
        return t, "No genres in this selection."
    top = t.iloc[-1]
    return t, (f"<b>{top.genre}</b> is the most crowded genre with {int(top.games):,} games, "
               f"and {pct(top.failed)} of them failed.")


def genre_scores(df):
    g = explode_genres(df.dropna(subset=["score"]))
    order = (g.groupby("genre")["score"].median().sort_values(ascending=False).index.tolist())
    if not order:
        return g, order, "No reviewed games in this selection."
    med = g.groupby("genre")["score"].median()
    return g, order, (f"Players like <b>{order[0]}</b> games most (median {med[order[0]]:.0f}% positive) "
                      f"and <b>{order[-1]}</b> least ({med[order[-1]]:.0f}%).")


def price_distribution(df):
    paid = df[df["price"] > 0]
    free_share = (df["price"] == 0).mean() if len(df) else 0
    if paid.empty:
        return paid, "Only free games in this selection."
    return paid, (f"The typical paid game costs <b>${paid['price'].median():.2f}</b>; "
                  f"{pct((paid['price'] < 10).mean())} cost under $10 and {pct(free_share)} of all games are free.")


def outcome_by_price(df):
    t = (df.groupby(["price_band", "outcome"]).size().unstack(fill_value=0)
         .reindex(index=[p for p in PRICE_BANDS if p in df["price_band"].unique()], columns=OUTCOMES, fill_value=0))
    share = t.div(t.sum(axis=1), axis=0) * 100
    if share.empty:
        return share, "No games in this selection."
    if len(share) == 1:
        band = share.index[0]
        return share, f"{share.loc[band, 'Failed']:.0f}% of {band} games in this selection failed."
    best = share["Failed"].idxmin()
    worst = share["Failed"].idxmax()
    return share, (f"<b>{best}</b> games fail least ({share.loc[best, 'Failed']:.0f}%); "
                   f"<b>{worst}</b> games fail most ({share.loc[worst, 'Failed']:.0f}%).")


def genre_bubbles(df):
    g = explode_genres(df)
    t = g.groupby("genre").agg(games=("AppID", "size"), hit=("hit", "mean"), failed=("failed", "mean"),
                               score=("score", "median")).dropna().reset_index()
    t = t[t["games"] >= 20]   # a genre needs enough games for fair rates
    if t.empty or t["hit"].max() == 0:
        return t, "Not enough games (or no hits) in this selection to compare genres."
    best = t.loc[(t["hit"] - t["failed"]).idxmax()]
    worst = t.loc[(t["hit"] - t["failed"]).idxmin()]
    return t, (f"Best bet: <b>{best.genre}</b> ({pct(best.hit)} hits, {pct(best.failed)} failed). "
               f"Riskiest: <b>{worst.genre}</b> ({pct(worst.hit)} hits, {pct(worst.failed)} failed).")


# ---------------------------------------------------------------- 03 WHO
def top_publishers(df, n=20):
    t = (df[df["publisher"] != "Unknown"].groupby("publisher")
         .agg(reviews=("reviews", "sum"), games=("AppID", "size")).sort_values("reviews", ascending=False))
    total = df["reviews"].sum()
    top = t.head(n).reset_index()
    if top.empty or not total:
        return top, "No publishers in this selection."
    return top, (f"The top {len(top)} publishers ({top['games'].sum():,} games) collect "
                 f"<b>{pct(top['reviews'].sum() / total)}</b> of all reviews. <b>{top.iloc[0].publisher}</b> alone has "
                 f"{pct(top.iloc[0].reviews / total)}.")


def platform_share(df):
    t = df["platform"].value_counts().reindex(PLATFORMS).dropna().reset_index()
    t.columns = ["platform", "games"]
    fail = df.groupby("mac")["failed"].mean()
    if len(fail) < 2:
        return t, f"{pct(t['games'].iloc[0] / t['games'].sum())} of these games are {t['platform'].iloc[0]}."
    return t, (f"{pct((df['platform'] == 'Windows only').mean())} of games run on Windows only. "
               f"Games with a Mac version fail less: <b>{pct(fail[True])}</b> vs {pct(fail[False])}.")


# ---------------------------------------------------------------- 04 WHY
def winner_takes_all(df, points=300):
    r = df["reviews"].sort_values(ascending=False).to_numpy()
    if not r.sum():
        return pd.DataFrame(), "No reviews in this selection."
    share_games = np.arange(1, len(r) + 1) / len(r) * 100
    share_reviews = np.cumsum(r) / r.sum() * 100
    idx = np.unique(np.concatenate([np.linspace(0, len(r) - 1, points).astype(int),
                                    np.arange(min(len(r), 200))]))
    t = pd.DataFrame({"games": share_games[idx], "reviews": share_reviews[idx]})
    top1 = share_reviews[max(0, len(r) // 100 - 1)]
    return t, (f"The top <b>1%</b> of games get <b>{top1:.0f}%</b> of all reviews. "
               f"The other 99% share what is left.")


def quality_vs_popularity(df, sample=4000):
    s = df.dropna(subset=["score"])
    if s.empty:
        return s, "No reviewed games in this selection."
    r = np.corrcoef(s["score"], np.log10(s["reviews"]))[0, 1] if len(s) > 2 else np.nan
    hidden = ((s["score"] >= 80) & (s["reviews"] < 50)).sum()
    pts = s.sample(min(sample, len(s)), random_state=7)
    return pts, (f"Good reviews do not bring players: the link is weak (r = {r:.2f}). "
                 f"<b>{hidden:,}</b> games are rated 80%+ but have fewer than 50 reviews.")


def signal_effect(df):
    rows = []
    for col, label in SIGNALS.items():
        rate = df.groupby(col)["failed"].mean()
        rows.append({"signal": label, "Without": rate.get(False, np.nan) * 100, "With": rate.get(True, np.nan) * 100})
    t = pd.DataFrame(rows)
    gap = (t["Without"] - t["With"]).dropna()
    if gap.empty:
        return t, "Not enough games to compare."
    big = t.loc[gap.idxmax()]
    return t, (f"Every signal lowers the failure rate. The biggest gap: <b>{big.signal}</b> "
               f"({big.Without:.0f}% → {big.With:.0f}% failed).")


def signal_dose(df):
    t = df.groupby("signals").agg(games=("AppID", "size"), failed=("failed", "mean"), hit=("hit", "mean")).reset_index()
    t[["failed", "hit"]] *= 100
    if len(t) < 2:
        return t, "Not enough games to compare."
    lo, hi = t.iloc[0], t.iloc[-1]
    word = lambda n: "signal" if n == 1 else "signals"
    return t, (f"With {int(lo.signals)} {word(lo.signals)}, {lo.failed:.0f}% of games fail and {lo.hit:.0f}% become "
               f"hits. With {'all ' if hi.signals == 4 else ''}{int(hi.signals)}, only <b>{hi.failed:.0f}%</b> fail and <b>{hi.hit:.0f}%</b> become hits.")


# ---------------------------------------------------------------- 05 RECOMMENDATIONS
def recommendations(df):
    """Numbers behind the four recommendations, from the filtered games."""
    def rate(mask):
        sub = df[mask]
        return sub["failed"].mean() if len(sub) else np.nan
    bands = outcome_by_price(df)[0]
    return {
        "lang_1": rate(df["languages"] <= 1), "lang_4": rate(df["languages"] >= 4),
        "ach_no": rate(df["achievements"] == 0), "ach_yes": rate(df["achievements"] > 0),
        "self": rate(df["self_published"]), "pub": rate(~df["self_published"]),
        "best_band": bands["Failed"].idxmin() if not bands.empty else "n/a",
        "best_band_fail": bands["Failed"].min() / 100 if not bands.empty else np.nan,
        "dec": rate(df["month"] == 12), "spring": rate(df["month"].between(1, 4)),
    }

"""
STEP 1 - CLEAN THE DATA  (run once:  python prepare_data.py)

Reads the raw Kaggle file  data/raw/games.csv  (125,855 Steam apps, 400 MB)
and saves one small, clean file  data/games_clean.parquet  that the dashboard loads.

What we clean, in order (each step is printed with the number of games left):
  1. Fix the broken header  ("DiscountDLC count" is really two columns)
  2. Turn the release date text into real dates
  3. Keep games released 2006-2024  (Steam opened to other studios in 2006;
     2025-26 games have not had time to collect reviews yet)
  4. Remove playtests, apps with no genre, and software that is not a game
  5. Remove adult-only titles (sexual-content tags) - this is a classroom presentation
  6. Add the columns we analyse: reviews, score, outcome, price band, languages, ...
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

RAW = Path("data/raw/games.csv")
OUT = Path("data/games_clean.parquet")
REPORT = Path("data/cleaning_report.json")

# Genres that are real game genres (Steam also lists software types like "Utilities")
GAME_GENRES = ["Indie", "Casual", "Action", "Adventure", "Simulation", "Strategy", "RPG",
               "Free To Play", "Early Access", "Sports", "Racing", "Massively Multiplayer"]
SOFTWARE = {"Utilities", "Design & Illustration", "Animation & Modeling", "Software Training",
            "Video Production", "Audio Production", "Photo Editing", "Web Publishing", "Education",
            "Accounting", "Game Development"}

COLUMNS = ["AppID", "Name", "Release date", "Estimated owners", "Price", "Supported languages",
           "Windows", "Mac", "Linux", "Positive", "Negative", "Achievements", "DLC count",
           "Average playtime forever", "Developers", "Publishers", "Genres", "Tags"]

steps = []


def log(text, frame):
    steps.append({"step": text, "games": len(frame)})
    print(f"{len(frame):>8,}  {text}")


# ---------------------------------------------------------------- 1. load with a fixed header
header = RAW.open(encoding="utf-8").readline().strip().split(",")
names = []
for col in header:
    # The Kaggle header glues two columns together, so every column after "Price"
    # would be shifted by one. We split the name back into two.
    names += ["Discount", "DLC count"] if col == "DiscountDLC count" else [col]
df = pd.read_csv(RAW, header=0, names=names, usecols=COLUMNS, low_memory=False)
log("Raw Steam apps in the Kaggle file", df)

# ---------------------------------------------------------------- 2. dates
df["release_date"] = pd.to_datetime(df["Release date"], format="mixed", errors="coerce")
df = df.dropna(subset=["release_date"])
df["year"] = df["release_date"].dt.year
df["month"] = df["release_date"].dt.month

# ---------------------------------------------------------------- 3. years
df = df[df["year"].between(2006, 2024)]
log("Released 2006-2024", df)

# ---------------------------------------------------------------- 4. real games only
df = df[~df["Name"].fillna("").str.contains("playtest", case=False)]
log("Without playtests", df)
genre_lists = df["Genres"].fillna("").str.split(",").map(lambda g: [x.strip() for x in g if x.strip()])
is_software = genre_lists.map(lambda g: all(x in SOFTWARE for x in g))  # also true for "no genre"
df = df[~is_software]
log("Without software and apps with no genre", df)

# ---------------------------------------------------------------- 5. classroom-safe
adult = df["Tags"].fillna("").str.contains("Sexual Content|Nudity|NSFW|Hentai", case=False)
df = df[~adult].copy()
log("Without adult-only titles", df)

# ---------------------------------------------------------------- 6. new columns
df["reviews"] = df["Positive"] + df["Negative"]
# Review score only makes sense with enough reviews
df["score"] = np.where(df["reviews"] >= 10, df["Positive"] / df["reviews"].clip(lower=1) * 100, np.nan)
df["outcome"] = pd.cut(df["reviews"], [-1, 9, 99, 999, np.inf],
                       labels=["Failed", "Small", "Solid", "Hit"]).astype(str)
df["failed"] = df["reviews"] < 10        # fewer than 10 reviews = almost nobody played it
df["hit"] = df["reviews"] >= 1000        # 1,000+ reviews = a successful game

df["price_band"] = pd.cut(df["Price"], [-0.01, 0, 4.99, 14.99, 29.99, np.inf],
                          labels=["Free", "Under $5", "$5–15", "$15–30", "$30+"]).astype(str)
df["genres"] = df["Genres"].fillna("").str.split(",").map(
    lambda g: "|".join(x.strip() for x in g if x.strip() in GAME_GENRES))

langs = df["Supported languages"].fillna("[]").str.strip()
df["languages"] = np.where(langs.isin(["[]", ""]), 0, langs.str.count("', '") + 1)
df["mac"] = df["Mac"].astype(str).eq("True")
df["linux"] = df["Linux"].astype(str).eq("True")
df["platform"] = np.select([df["mac"] & df["linux"], df["mac"], df["linux"]],
                           ["Windows + Mac + Linux", "Windows + Mac", "Windows + Linux"], "Windows only")
df["publisher"] = df["Publishers"].fillna("").str.split(",").str[0].str.strip().replace("", "Unknown")
df["developer"] = df["Developers"].fillna("").str.split(",").str[0].str.strip().replace("", "Unknown")
df["self_published"] = df["Developers"].fillna("").eq(df["Publishers"].fillna(""))

# The four "launch effort" signals we test in the root-cause section
df["sig_languages"] = df["languages"] >= 4
df["sig_achievements"] = df["Achievements"] > 0
df["sig_mac"] = df["mac"]
df["sig_publisher"] = ~df["self_published"]
df["signals"] = df[["sig_languages", "sig_achievements", "sig_mac", "sig_publisher"]].sum(axis=1)

owners = df["Estimated owners"].fillna("0 - 0").str.split(" - ", expand=True).astype(float)
df["owners_mid"] = (owners[0] + owners[1]) / 2    # Steam only gives a range, so we use the middle

clean = df.rename(columns={"Name": "name", "Price": "price", "Positive": "positive",
                           "Negative": "negative", "Achievements": "achievements",
                           "Average playtime forever": "playtime"})[
    ["AppID", "name", "release_date", "year", "month", "price", "price_band", "genres", "platform", "mac",
     "linux", "languages", "achievements", "publisher", "developer", "self_published", "positive", "negative",
     "reviews", "score", "outcome", "failed", "hit", "owners_mid", "playtime",
     "sig_languages", "sig_achievements", "sig_mac", "sig_publisher", "signals"]]

clean.to_parquet(OUT, index=False)
REPORT.write_text(json.dumps(steps, indent=1), encoding="utf-8")
print(f"\nSaved {len(clean):,} games to {OUT}  ({OUT.stat().st_size / 1e6:.1f} MB)")

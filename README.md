# Why do most Steam games fail?

A Python data analysis and visualization project: 87,343 real Steam games (2006–2024), one
interactive dashboard with 15 charts and 5 filters that change every chart at once.

**Research question:** most Steam games are never noticed. Why, and what can a small studio do about it?

## How to run

```
pip install -r requirements.txt
python -m streamlit run app.py
```

On Windows you can also double-click `run_dashboard.bat`.

## The four Python files (in the order they run)

| File | Step | What it does |
|---|---|---|
| `prepare_data.py` | 1. Clean | Reads the raw Kaggle file, fixes its broken header, removes non-games, saves `data/games_clean.parquet`. Run once. |
| `analysis.py` | 2. Analyse | Applies the filters and calculates every number (pandas). Each function returns a table and a one-sentence key point. |
| `charts.py` | 3. Visualise | One Plotly function per chart, plus `CHARTS`: the question each chart answers and why we chose that chart type. |
| `app.py` | 4. Dashboard | The Streamlit web page: sidebar filters, sections, chart cards. |

## Data

- **Source:** Steam Games Dataset by FronkonGames (Kaggle), collected from the Steam store and SteamSpy.
- **Raw file:** `data/raw/games.csv` (125,855 apps, 400 MB). Not included in the repository because of its size.
- **Cleaning** (`prepare_data.py`):
  1. Fix the header: `DiscountDLC count` is really two columns, so every column after Price was shifted.
  2. Keep games released 2006–2024 (2025–26 games have not had time to collect reviews).
  3. Remove playtests, software (Utilities, Design…), apps with no genre, and adult-only titles.
- **Definitions:** Failed = fewer than 10 reviews · Hit = 1,000+ reviews · Score = % positive (10+ reviews only).
  Steam does not publish sales, so reviews are our measure of players. Owner numbers are estimates.

## Main findings

1. **Steam got crowded:** 17,559 games came out in 2024; failure rose from 5% (2008) to 63% (2024).
2. **Winner takes all:** the top 1% of games get 78% of all reviews.
3. **Quality is not enough:** score and popularity are barely linked (r = 0.14); 11,700+ well-rated games stay unseen.
4. **Root cause, launch effort:** games with none of 4 signals (4+ languages, achievements, Mac version, a
   publisher) fail 63% of the time; games with all 4 fail 15% and become hits 31% of the time.
   These are links, not proof of cause: bigger studios tend to do all four.

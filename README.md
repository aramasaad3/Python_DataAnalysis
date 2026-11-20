# Why do most Steam games fail?

A Python data analysis and visualization project on **87,343 real Steam games (2006–2024)**:
an interactive Dash dashboard (6 tabs, 15 figures, 5 filters that change every chart at once)
and an animated PowerPoint presentation built from the same code.

**Team:** Muhammad Abdulkhalq, Aram Asaad, Bashar Bahjat. Software Engineering, 4th stage, Salahaddin University - Erbil.
Course: Programming in Python, Data Analysis and Visualization.

## How to run

```
pip install -r requirements.txt
python app.py                  # dashboard -> open http://127.0.0.1:8050
python make_presentation.py    # builds presentation/Steam_Games_Presentation.pptx
```

`python prepare_data.py` rebuilds the clean data from the raw Kaggle file (only needed if you change the cleaning).
On Windows you can also double-click `run_dashboard.bat`. Open a tab directly with `?tab=why` (or overview, when,
what, who, fix) at the end of the address.

## Put it online (free)

Streamlit Cloud cannot run Dash apps. On [Render](https://render.com): New → Web Service → this GitHub repository,
Build command `pip install -r requirements.txt`, Start command `gunicorn app:server`.

## Files, in the order they run

| File | Step | What it does |
|---|---|---|
| `prepare_data.py` | 1. Clean | Reads the raw Kaggle file, fixes its broken header, keeps real games, saves `data/games_clean.parquet` |
| `analysis.py` | 2. Analyse | Applies the filters and calculates every number and key point (pandas) |
| `charts.py` | 3. Visualise | One Plotly function per chart + `CHART_INFO`: why we chose each chart, why not another, and an alternative |
| `app.py` | 4. Dashboard | The Dash web page; every filter is an Input of the same callbacks, so all charts update together |
| `make_presentation.py` | 5. Slides | Builds the PowerPoint from the same charts and numbers (with `icons.py` and `pptx_motion.py`) |
| `assets/style.css` | Design | Dashboard style (Dash loads it automatically) |

## Data

- **Source:** Steam Games Dataset by FronkonGames (Kaggle), collected from the Steam store and SteamSpy.
- **Raw file:** `data/raw/games.csv` (125,855 apps, 400 MB), not in the repository because of its size.
- **Cleaning:** split the broken `DiscountDLC count` header (every column after Price was shifted); keep 2006–2024;
  remove playtests, software, apps with no genre and adult-only titles.
- **Definitions:** Failed = fewer than 10 reviews · Hit = 1,000+ reviews · Score = % positive (10+ reviews only).
  Steam hides sales, so reviews measure players. Owner numbers are estimates.

## Main findings

1. Steam got crowded: 17,559 games in 2024; failure rose from 5% (2008) to 63% (2024), in every genre.
2. Winner takes all: the top 1% of games get 78% of all reviews.
3. Quality is not enough: score and popularity are barely linked (r = 0.14).
4. Root cause, launch effort: with none of 4 signals (4+ languages, achievements, Mac version, a publisher) 63% of
   games fail; with all 4, 15% fail and 31% become hits. These are links, not proof of cause.

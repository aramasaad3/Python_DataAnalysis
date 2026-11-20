"""
STEP 5 - THE PRESENTATION   Run:  python make_presentation.py   ->  presentation/Steam_Games_Presentation.pptx

* The headline of each slide IS the finding; big charts, big numbers, icons.
* Every chart comes from charts.py and every number from analysis.py, so slides and dashboard match.
* Morph transitions and entrance animations (pptx_motion.py), speaker notes on every slide.
  Play it in Slide Show mode to see the motion.
"""
import os
import time

import numpy as np
from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

import analysis as A
import charts as C
from icons import icon_png
from pptx_motion import animate, set_transition

STUDENTS = ["Muhammad Abdulkhalq", "Aram Asaad", "Bashar Bahjat"]
OUT = "presentation"
IMG = f"{OUT}/img"
os.makedirs(IMG, exist_ok=True)


def rgb(h):
    return RGBColor.from_string(h.lstrip("#"))


HEX = dict(ink="#1d2433", ink2="#5b6474", ink3="#8a919e", rule="#e4e2dc", paper="#f6f5f1", navy="#0b2540",
           accent="#1b9e77", amber="#f2b36b", good="#00704f", warn="#a86400", bad="#b0413e", mist="#c9d6e3")
INK, INK2, INK3, RULE, PAPER = (rgb(HEX[k]) for k in ("ink", "ink2", "ink3", "rule", "paper"))
NAVY, ACCENT, AMBER, GOOD, WARN, BAD, MIST = (rgb(HEX[k]) for k in
                                              ("navy", "accent", "amber", "good", "warn", "bad", "mist"))
WHITE, STEEL, TILE = rgb("ffffff"), rgb("9fb3c8"), rgb("ece9e1")
SERIF, SANS, MONO = "Georgia", "Calibri", "Consolas"
PX_PER_INCH = 100

# ---------------------------------------------------------------------------
# The numbers (all from analysis.py, for ALL games - no filters)
# ---------------------------------------------------------------------------
print("Loading data ...")
df = A.load_games()
k = A.kpis(df)
steps, _ = A.cleaning_funnel()
releases, _ = A.releases_per_year(df)
fail_year, _ = A.failure_by_year(df)
dose, _ = A.signal_dose(df)
effect, _ = A.signal_effect(df)
share_price, _ = A.outcome_by_price(df)
bubbles, _ = A.genre_bubbles(df)
publishers, _ = A.top_publishers(df)
rec = A.recommendations(df)

y_last, y_first = releases.iloc[-1], releases.iloc[0]
fy_first, fy_last = fail_year.iloc[0], fail_year.iloc[-1]
reviews_total = df["reviews"].sum()
scored = df.dropna(subset=["score"])
r_quality = np.corrcoef(scored["score"], np.log10(scored["reviews"]))[0, 1]
hidden_gems = int(((scored["score"] >= 80) & (scored["reviews"] < 50)).sum())
top20_share = publishers["reviews"].sum() / reviews_total
valve_share = publishers.iloc[0]["reviews"] / reviews_total
best_g = bubbles.loc[(bubbles["hit"] - bubbles["failed"]).idxmax()]
worst_g = bubbles.loc[(bubbles["hit"] - bubbles["failed"]).idxmin()]
mac_fail = df.groupby("mac")["failed"].mean()
win_only = (df["platform"] == "Windows only").mean()
d0, d4 = dose.iloc[0], dose.iloc[-1]


def pct(x):
    return f"{x:.0%}"


# ---------------------------------------------------------------------------
# Chart images (same functions as the dashboard)
# ---------------------------------------------------------------------------
def export(fig, name, w_in, h_in, font=16):
    """Save a chart as PNG sized for its place on the slide (transparent background)."""
    path = f"{IMG}/{name}.png"
    fig.update_layout(width=int(w_in * PX_PER_INCH), height=int(h_in * PX_PER_INCH), font_size=font,
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=30))
    for _ in range(5):
        try:
            fig.write_image(path, scale=2)
            return path
        except Exception:
            time.sleep(2)
    raise RuntimeError(f"could not export {name}")


print("Exporting charts ...")
W_FULL, H_FULL = 12.13, 4.95
W_MAIN, H_MAIN = 8.6, 4.95
W_HALF, H_HALF = 5.95, 4.95
g6, order6, _ = A.genre_scores(df)
img = {
    1: export(C.cleaning_funnel(steps), "fig01_cleaning", W_MAIN, H_MAIN, 15),
    2: export(C.releases_per_year(releases), "fig02_releases", W_MAIN, H_MAIN),
    3: export(C.failure_by_year(fail_year), "fig03_failure_year", W_MAIN, H_MAIN),
    4: export(C.failure_heatmap(A.failure_heatmap(df)[0]), "fig04_heatmap", W_FULL, H_FULL, 14),
    5: export(C.genre_counts(A.genre_counts(df)[0]), "fig05_genres", W_HALF, H_HALF, 14),
    6: export(C.genre_scores(g6, order6), "fig06_scores", W_HALF, H_HALF, 14),
    7: export(C.price_distribution(A.price_distribution(df)[0]), "fig07_prices", W_HALF, H_HALF, 14),
    8: export(C.outcome_by_price(share_price), "fig08_price_outcome", W_HALF, H_HALF, 14),
    9: export(C.genre_bubbles(bubbles), "fig09_bubbles", W_MAIN, H_MAIN, 14),
    10: export(C.top_publishers(publishers), "fig10_publishers", W_MAIN, H_MAIN, 14),
    11: export(C.platform_share(A.platform_share(df)[0]), "fig11_platforms", W_MAIN, H_MAIN, 15),
    12: export(C.winner_takes_all(A.winner_takes_all(df)[0]), "fig12_pareto", W_MAIN, H_MAIN),
    13: export(C.quality_vs_popularity(A.quality_vs_popularity(df)[0]), "fig13_quality", W_MAIN, H_MAIN),
    14: export(C.signal_effect(effect), "fig14_signals", W_MAIN, H_MAIN, 15),
    15: export(C.signal_dose(dose), "fig15_dose", W_MAIN, H_MAIN),
}

# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------
prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]
TOTAL_SLIDES = 28


def text(slide, x, y, w, h, lines, size=16, font=SANS, color=INK, bold=False, align=PP_ALIGN.LEFT,
         spacing=1.1, after=4, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, line in enumerate(lines if isinstance(lines, list) else [lines]):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment, p.line_spacing, p.space_after = align, spacing, Pt(after)
        r = p.add_run()
        r.text = line
        r.font.size, r.font.name, r.font.bold, r.font.color.rgb = Pt(size), font, bold, color
    return tb


def box(slide, x, y, w, h, fill, line=None, shape=MSO_SHAPE.RECTANGLE, alpha=None):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if alpha is not None:
        clr = s.fill._xPr.find(qn("a:solidFill"))[0]
        etree.SubElement(clr, qn("a:alpha")).set("val", str(int(alpha * 100000)))
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(0.75)
    s.shadow.inherit = False
    return s


def picture(slide, path, x, y, w=None, h=None, name=None):
    pic = slide.shapes.add_picture(path, Inches(x), Inches(y), Inches(w) if w else None, Inches(h) if h else None)
    if name:
        pic.name = name
    return pic


def icon(slide, name, x, y, size=0.5, color=HEX["ink"]):
    return picture(slide, icon_png(name, color), x, y, size, size)


def background(slide, color):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color


def notes(slide, txt):
    slide.notes_slide.notes_text_frame.text = txt


def page(kicker, headline, dark=False):
    """A slide with kicker + headline, footer and a progress line that grows slide by slide."""
    s = prs.slides.add_slide(BLANK)
    background(s, NAVY if dark else PAPER)
    n = len(prs.slides)
    text(s, 0.6, 0.42, 10, 0.3, kicker.upper(), 11, MONO, AMBER if dark else ACCENT)
    text(s, 0.6, 0.68, 12.1, 0.8, headline, 30, SERIF, WHITE if dark else INK)
    box(s, 0.6, 7.06, 12.13, 0.01, rgb("1d4570") if dark else RULE)
    bar = box(s, 0.6, 7.04, 12.13 * n / TOTAL_SLIDES, 0.035, ACCENT)
    bar.name = "!!progress"
    text(s, 0.6, 7.13, 8, 0.25, "WHY DO MOST STEAM GAMES FAIL?", 9, MONO, STEEL if dark else INK3)
    text(s, 11.73, 7.13, 1, 0.25, f"{n:02d}", 9, MONO, STEEL if dark else INK3, align=PP_ALIGN.RIGHT)
    set_transition(s, "morph")
    return s


def chart_notes(num):
    kind, question, how, why, why_not, also = C.CHART_INFO[num]
    return (f"FIG. {num} - {kind.upper()}: {question}\nHOW TO READ: {how}\nWHY THIS CHART: {why}\n"
            f"WHY NOT ANOTHER: {why_not}\nCOULD ALSO USE: {also}")


def tag(slide, num, x, y, w):
    """Small label under a chart: figure number, chart type and why it was chosen."""
    kind, why = C.CHART_INFO[num][0], C.CHART_INFO[num][3]
    if len(kind) + len(why) > w * 17:
        why = why.split(". ")[0].rstrip(".") + "."
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(0.3))
    tb.text_frame.word_wrap = True
    tb.text_frame.margin_left = tb.text_frame.margin_right = tb.text_frame.margin_top = 0
    p = tb.text_frame.paragraphs[0]
    r1 = p.add_run()
    r1.text = f"FIG. {num}  {kind.upper()}   "
    r1.font.size, r1.font.name, r1.font.bold, r1.font.color.rgb = Pt(9), MONO, True, ACCENT
    r2 = p.add_run()
    r2.text = why
    r2.font.size, r2.font.name, r2.font.color.rgb = Pt(10.5), SANS, INK2
    return tb


def callout(slide, x, y, w, value, label, color=INK, size=44):
    rule = box(slide, x, y, w, 0.02, INK)
    v = text(slide, x, y + 0.12, w, 1.0, value, size, MONO, color)
    lab = text(slide, x, y + 0.14 + size / 60, w, 0.9, label, 13.5, SANS, INK2, spacing=1.15)
    return [(rule, "wipe"), (v, "rise"), (lab, "fade")]


def chart_page(kicker, headline, num, note, callouts=()):
    """One big chart; with callouts the chart takes the left 70% and the numbers sit on the right."""
    s = page(kicker, headline)
    wide = not callouts
    pic = picture(s, img[num], 0.6, 1.55, W_FULL if wide else W_MAIN)
    seq = [(pic, "wipe"), (tag(s, num, 0.6, 6.62, W_FULL if wide else W_MAIN), "fade")]
    for i, (value, label, color) in enumerate(callouts):
        seq += callout(s, 9.6, 1.75 + i * 1.75, 3.13, value, label, color)
    animate(s, seq, step=200)
    notes(s, f"{note}\n\n{chart_notes(num)}")
    return s


def two_chart_page(kicker, headline, n1, n2, note):
    s = page(kicker, headline)
    seq = []
    for i, num in enumerate((n1, n2)):
        x = 0.6 + i * 6.18
        seq += [(picture(s, img[num], x, 1.55, W_HALF), "wipe"), (tag(s, num, x, 6.62, W_HALF), "fade")]
    animate(s, seq, step=220)
    notes(s, f"{note}\n\n" + "\n\n".join(chart_notes(num) for num in (n1, n2)))
    return s


def section_slide(number, title, sub, note):
    s = prs.slides.add_slide(BLANK)
    background(s, NAVY)
    num = text(s, 0.8, 1.7, 4, 1.3, number, 90, MONO, AMBER)
    ttl = text(s, 0.8, 3.1, 8.5, 1.6, title, 42, SERIF, WHITE, spacing=1.0)
    line = box(s, 0.8, 4.85, 1.4, 0.03, ACCENT)
    std = text(s, 0.8, 5.05, 7.5, 1.0, sub, 17, SANS, MIST, spacing=1.2)
    set_transition(s, "morph")
    animate(s, [(num, "zoom"), (ttl, "rise"), (line, "wipe"), (std, "fade")], step=230)
    notes(s, note)
    return s


def tiles(s, items, top=1.8, color=HEX["ink"], numcolor=ACCENT):
    """Four white tiles with an icon, a number, a title and a line of text."""
    seq = []
    for i, (ic, title, sub) in enumerate(items):
        x = 0.6 + i * 3.1
        seq += [(box(s, x, top, 2.9, 4.4, WHITE, RULE), "rise"),
                (box(s, x + 0.35, top + 0.4, 1.1, 1.1, TILE, shape=MSO_SHAPE.OVAL), "zoom"),
                (icon(s, ic, x + 0.6, top + 0.65, 0.6, color), "zoom"),
                (text(s, x + 0.35, top + 1.95, 2.3, 0.3, f"{i + 1:02d}", 12, MONO, numcolor), "fade"),
                (text(s, x + 0.35, top + 2.25, 2.4, 0.9, title, 26, SERIF, INK, spacing=1.0), "fade"),
                (text(s, x + 0.35, top + 3.1, 2.3, 1.2, sub, 14, SANS, INK2, spacing=1.15), "fade")]
    return seq


# ---------------------------------------------------------------------------
# Slides
# ---------------------------------------------------------------------------
print("Building slides ...")

# 1. Title
s = prs.slides.add_slide(BLANK)
background(s, NAVY)
kick = text(s, 0.8, 1.35, 8, 0.3, "STEAM GAMES ANALYSIS  /  2006-2024", 12, MONO, STEEL)
ttl = text(s, 0.8, 1.75, 10.5, 2.3, "Why do most Steam games fail?", 54, SERIF, WHITE, spacing=0.95)
line = box(s, 0.8, 4.25, 1.6, 0.04, ACCENT)
std = text(s, 0.8, 4.5, 9, 0.6, f"{k['games']:,} real games, one dashboard, one root cause.", 20, SANS, MIST)
who = text(s, 0.8, 5.6, 9, 1.0, ["  /  ".join(STUDENTS),
                                 "Software Engineering, 4th stage  /  Salahaddin University - Erbil"],
           12, MONO, STEEL, after=4)
set_transition(s, "fade", "slow")
animate(s, [(kick, "fade"), (ttl, "rise"), (line, "wipe"), (std, "fade"), (who, "fade")], start=400, step=300)
notes(s, f"We analysed {k['games']:,} real Steam games released between 2006 and 2024 to answer one question: "
         "why do most games on Steam fail, and what can a small studio do about it?")

# 2. The problem
s = prs.slides.add_slide(BLANK)
background(s, NAVY)
kick = text(s, 0.8, 1.3, 6, 0.3, "THE PROBLEM", 12, MONO, AMBER)
big = text(s, 0.8, 1.7, 7, 2.2, pct(k["failed"]), 150, MONO, WHITE)
sub = text(s, 0.8, 4.15, 7.5, 1.2, "of Steam games never reach 10 reviews", 28, SERIF, WHITE, spacing=1.05)
more = text(s, 0.8, 5.3, 7.5, 1.0, f"Almost nobody plays them. Only {pct(k['hit'])} become hits with 1,000+ reviews.",
            16, SANS, MIST, spacing=1.2)
set_transition(s, "morph")
animate(s, [(kick, "fade"), (big, "zoom"), (sub, "rise"), (more, "fade")], start=900, step=300)
notes(s, f"This is the problem. {pct(k['failed'])} of all the games in our data got fewer than 10 reviews: "
         "almost nobody bought or played them.")

# 3. The brief
s = page("The brief", "Four questions from a small game studio")
animate(s, tiles(s, [("calendar", "When?", "Is Steam getting too crowded?"),
                     ("tag", "What?", "Which genres and prices succeed?"),
                     ("users", "Who?", "Who gets the players?"),
                     ("search", "Why?", "What do failed games have in common?")]), step=90)
notes(s, "We imagine a small studio in Erbil asking us what game to make. Each part of the talk and each tab of "
         "the dashboard answers one of these four questions.")

# 4. The data
s = page("The data", f"{k['games']:,} real Steam games, 2006-2024")
seq = []
for i, (ic, value, label) in enumerate([("database", f"{steps['games'].iloc[0] // 1000}K", "apps in the raw file"),
                                        ("gamepad", f"{k['games'] // 1000}K", "games after cleaning"),
                                        ("tag", "12", "genres"),
                                        ("star", f"{reviews_total / 1e6:.0f}M", "player reviews")]):
    x = 0.6 + i * 3.1
    seq += [(icon(s, ic, x, 1.9, 0.55, HEX["accent"]), "zoom"),
            (text(s, x, 2.65, 2.9, 1.2, value, 60, MONO, INK), "rise"),
            (text(s, x, 3.75, 2.9, 0.4, label.upper(), 12, MONO, INK2), "fade")]
src = text(s, 0.6, 4.6, 6.6, 1.6, ["Source: Steam Games Dataset (FronkonGames, Kaggle), collected from the "
                                   "Steam store and SteamSpy. Owner numbers are estimates."], 15, SANS, INK2,
           spacing=1.25)
d_box = box(s, 7.6, 4.55, 5.13, 1.75, WHITE, RULE)
d1 = text(s, 7.9, 4.75, 4.6, 0.4, "FAILED = fewer than 10 reviews", 17, MONO, BAD)
d2 = text(s, 7.9, 5.25, 4.6, 0.4, "HIT = 1,000 or more reviews", 17, MONO, GOOD)
d3 = text(s, 7.9, 5.75, 4.6, 0.5, "Steam hides sales, so reviews measure players.", 13, SANS, INK2)
animate(s, seq + [(src, "fade"), (d_box, "rise"), (d1, "fade"), (d2, "fade"), (d3, "fade")], step=120)
notes(s, "Steam does not publish sales numbers, so we use reviews as our measure: every review is a player who "
         "bought and played the game. A game with fewer than 10 reviews has failed; 1,000+ reviews is a hit.")

# 5. Cleaning
s = page("Cleaning with pandas", "400 MB raw in, 5 MB clean out")
seq = []
for x, ic, value, label in [(0.6, "file", "400 MB", f"raw CSV, {steps['games'].iloc[0]:,} apps"),
                            (6.95, "database", "5.4 MB", f"clean Parquet, {k['games']:,} games")]:
    seq += [(box(s, x, 1.75, 5.78, 2.0, WHITE, RULE), "rise"), (icon(s, ic, x + 0.35, 2.15, 0.6), "zoom"),
            (text(s, x + 1.25, 1.98, 4.3, 1.0, value, 48, MONO, INK), "fade"),
            (text(s, x + 1.25, 2.95, 4.3, 0.4, label.upper(), 11, MONO, INK2), "fade")]
seq.insert(4, (icon(s, "arrow", 6.42, 2.5, 0.48, HEX["accent"]), "wipe"))
for i, (ic, head, body) in enumerate([
        ("wrench", "Broken header", "'DiscountDLC count' was two columns glued together: every column after "
                                    "Price was shifted. We split it."),
        ("check", "Real games only", "Removed playtests, software (Utilities, Design...), apps with no genre "
                                     "and adult-only titles."),
        ("calendar", "A fair comparison", "Kept 2006-2024: newer games have not had time to collect reviews.")]):
    x = 0.6 + i * 4.1
    seq += [(icon(s, ic, x, 4.3, 0.42, HEX["accent"]), "zoom"),
            (text(s, x + 0.6, 4.25, 3.4, 0.5, head, 22, SERIF, INK), "fade"),
            (text(s, x + 0.6, 4.85, 3.3, 1.5, body, 14, SANS, INK2, spacing=1.2), "fade")]
animate(s, seq, step=110)
notes(s, "prepare_data.py cleans the raw Kaggle file with pandas. The most important fix: the header was broken, "
         "so every column after Price was shifted by one. We also removed apps that are not games and kept "
         "2006-2024, so every game had time to collect reviews.")

# 6. Pipeline
s = page("Tools", "From raw data to advice in six steps")
seq = [(box(s, 1.3, 2.75, 10.8, 0.02, RULE), "wipe")]
for i, (ic, name_, tool) in enumerate([("file", "Load", "pandas"), ("wrench", "Clean", "prepare_data.py"),
                                       ("search", "Analyse", "analysis.py"), ("chart", "Visualise", "charts.py"),
                                       ("monitor", "Dashboard", "app.py (Dash)"), ("bulb", "Advise", "findings")]):
    cx = 1.3 + i * 2.16
    seq += [(box(s, cx - 0.55, 2.2, 1.1, 1.1, WHITE, INK, MSO_SHAPE.OVAL), "zoom"),
            (icon(s, ic, cx - 0.28, 2.47, 0.56), "zoom"),
            (text(s, cx - 1.0, 3.55, 2.0, 0.5, name_, 22, SERIF, INK, align=PP_ALIGN.CENTER), "fade"),
            (text(s, cx - 1.05, 4.1, 2.1, 0.6, tool, 12, MONO, INK2, align=PP_ALIGN.CENTER), "fade")]
foot = text(s, 0.6, 5.4, 12.1, 0.8, "One file of chart functions feeds both the dashboard and these slides, "
            "so every number matches.", 17, SERIF, INK)
animate(s, seq + [(foot, "fade")], step=90)
notes(s, "The data analysis workflow from the lecture: load, clean, analyse, visualise, communicate. Each step "
         "is one Python file.")

# 7. Dashboard
s = page("The dashboard", "6 tabs, 15 figures, 5 filters that change every chart")
shot = picture(s, f"{IMG}/dashboard.png", 0.6, 1.55, 7.6)
seq = [(shot, "wipe")]
for i, (value, label) in enumerate([("5 filters", "genre, price, years, platform, publisher"),
                                    ("6 tabs", "one question per tab"),
                                    ("15 figures", "each says why we chose that chart")]):
    seq += callout(s, 8.75, 1.75 + i * 1.65, 3.98, value, label, ACCENT if i == 0 else INK, 34)
animate(s, seq, step=200)
notes(s, "Every filter changes the key numbers and every chart on every tab at the same time. Under each chart "
         "the dashboard explains how to read it, the key point, and why we chose that chart type.")

# 8-11. WHEN
section_slide("01", "When? Is Steam too crowded?", "How the number of games, and their chances, changed.",
              "Part one: is Steam getting crowded?")
chart_page("When / releases", f"{int(y_last.games):,} games came out in {int(y_last.year)}", 2,
           f"Releases grew {y_last.games / y_first.games:,.0f} times since {int(y_first.year)}. The two dotted "
           "lines are when Steam opened its store: Greenlight in 2012 and Steam Direct in 2017.",
           callouts=[(f"{y_last.games / y_first.games:,.0f}x", f"more games than in {int(y_first.year)}", ACCENT),
                     (f"{int(y_last.games):,}", f"games released in {int(y_last.year)}", INK)])
chart_page("When / failure", f"Failure rose from {pct(fy_first.failed)} to {pct(fy_last.failed)}", 3,
           "More games compete for the same players. Older games had more years to collect reviews, so part of "
           "the rise is their age - but the jump after 2017 is far too big to be only that.",
           callouts=[(pct(fy_first.failed), f"of games failed in {int(fy_first.year)}", INK),
                     (pct(fy_last.failed), f"of games failed in {int(fy_last.year)}", BAD)])
chart_page("When / every genre", "It is not one genre: every genre got worse", 4,
           "Each row is a genre, each column a year. Every row gets darker to the right: failure went up in "
           "every genre.")

# 12-15. WHAT
section_slide("02", "What? Which games succeed?", "Genres and prices: where the crowd is, and what players like.",
              "Part two: which games succeed?")
two_chart_page("What / genres", "Indie is the most crowded genre", 5, 6,
               "On the left, how many games each genre has. On the right, how much players like each genre.")
two_chart_page("What / price", f"{share_price['Failed'].idxmin()} games fail least", 7, 8,
               f"Most games are cheap: the typical paid game costs ${df[df.price > 0].price.median():.2f}. But "
               f"{share_price['Failed'].idxmin()} games fail least ({share_price['Failed'].min():.0f}%) and "
               f"{share_price['Failed'].idxmax()} games fail most ({share_price['Failed'].max():.0f}%).")
chart_page("What / best bet", f"Best bet: {best_g.genre}. Riskiest: {worst_g.genre}", 9,
           "Further right means more hits, lower means fewer failures, so the bottom-right corner is the best bet.",
           callouts=[(pct(best_g.hit), f"of {best_g.genre} games become hits", GOOD),
                     (pct(worst_g.failed), f"of {worst_g.genre} games fail", BAD)])

# 16-18. WHO
section_slide("03", "Who? Who wins on Steam?", "Publishers and platforms behind the games people play.",
              "Part three: who gets the players?")
chart_page("Who / publishers", f"20 publishers hold {pct(top20_share)} of all reviews", 10,
           f"{publishers.iloc[0].publisher} alone has {pct(valve_share)} of every review on Steam.",
           callouts=[(pct(top20_share), "of reviews go to 20 publishers", ACCENT),
                     (pct(valve_share), f"go to {publishers.iloc[0].publisher} alone", INK)])
chart_page("Who / platforms", f"{pct(win_only)} of games are Windows only", 11,
           "Few studios make Mac or Linux versions, and those that do fail less.",
           callouts=[(pct(mac_fail[True]), "of games with a Mac version fail", GOOD),
                     (pct(mac_fail[False]), "of games without one fail", BAD)])

# 19-24. WHY
section_slide("04", "Why? The root cause", "Too many games, too little attention.",
              "Part four: why do games fail?")
chart_page("Why / attention", f"The top 1% of games get {k['top1_share']:.0%} of all reviews", 12,
           "Players go to a few games. The other 99% of games share what is left.",
           callouts=[(f"{k['top1_share']:.0%}", "of all reviews go to the top 1% of games", ACCENT),
                     (f"{k['median_reviews']:.0f}", "reviews for the typical (median) game", INK)])
chart_page("Why / quality", "Good games still fail: quality is not enough", 13,
           f"The link between review score and number of reviews is weak (r = {r_quality:.2f}). Many loved games "
           "are simply never seen.",
           callouts=[(f"r = {r_quality:.2f}", "score vs players: a weak link", INK),
                     (f"{hidden_gems:,}", "games rated 80%+ with fewer than 50 reviews", BAD)])
chart_page("Why / launch effort", "Successful launches do four things", 14,
           "Four launch signals: translated into 4+ languages, Steam achievements, a Mac version, and a "
           "publisher. Every one of them goes with a lower failure rate.",
           callouts=[(f"{effect.iloc[0].Without:.0f}% → {effect.iloc[0].With:.0f}%", "failed: 1 language vs 4+",
                      ACCENT),
                     (f"{effect.iloc[1].Without:.0f}% → {effect.iloc[1].With:.0f}%", "failed: no achievements vs some",
                      INK)])
chart_page("Why / the proof", "The more signals, the fewer failures", 15,
           f"With 0 signals, {d0.failed:.0f}% of games fail and {d0.hit:.0f}% become hits. With all 4, only "
           f"{d4.failed:.0f}% fail and {d4.hit:.0f}% become hits. These are links, not proof of cause: bigger "
           "studios tend to do all four things.",
           callouts=[(f"{d0.failed:.0f}%", "fail with 0 signals", BAD),
                     (f"{d4.failed:.0f}%", "fail with all 4 signals", GOOD)])

# root cause chain
s = page("Root cause", "Launch effort decides who gets noticed")
seq = [(text(s, 0.6, 1.75, 12.1, 0.5, "Share of games that FAIL, by number of launch signals:", 18, SANS, INK2),
        "fade")]
for i, row in dose.reset_index(drop=True).iterrows():
    x = 0.6 + i * 2.48
    color = BAD if row.failed > 40 else (WARN if row.failed > 25 else GOOD)
    seq += [(box(s, x, 2.5, 2.25, 2.4, WHITE, RULE), "rise"),
            (text(s, x + 0.25, 2.7, 1.9, 1.0, f"{row.failed:.0f}%", 44, MONO, color), "zoom"),
            (text(s, x + 0.25, 3.75, 1.9, 0.4, f"{int(row.signals)} SIGNAL{'S' if row.signals != 1 else ''}", 12,
                  MONO, INK2), "fade"),
            (text(s, x + 0.25, 4.15, 1.9, 0.5, f"{row.hit:.0f}% hits", 15, SANS, INK), "fade")]
take = text(s, 0.6, 5.35, 12.1, 0.9, "The store is flooded and players go to a few games. The games that get noticed "
            "are launched with more effort.", 22, SERIF, INK, spacing=1.15)
animate(s, seq + [(take, "fade")], step=110)
notes(s, "This is our root cause in one picture: as the launch effort goes up from 0 to 4 signals, the failure "
         "rate falls step by step, and the hit rate rises.")

# 25-26. WHAT TO DO
section_slide("05", "What should the studio do?", "Four pieces of advice, each answering a finding.",
              "Part five: our advice for the studio.")
s = page("Recommendations", "Launch with effort, not just a good game")
seq = []
for i, (ic, head, body) in enumerate([
        ("globe", "Translate it", f"4+ languages: failure drops from {pct(rec['lang_1'])} to {pct(rec['lang_4'])}."),
        ("star", "Add achievements", f"Cheap to add: {pct(rec['ach_no'])} → {pct(rec['ach_yes'])} failed."),
        ("users", "Find a publisher", f"Or market like one: {pct(rec['self'])} → {pct(rec['pub'])} failed."),
        ("dollar", f"Price {rec['best_band']}", f"Fewest failures ({pct(rec['best_band_fail'])}). Avoid December "
                                                f"({pct(rec['dec'])} vs {pct(rec['spring'])} in Jan-Apr).")]):
    x = 0.6 + i * 3.1
    seq += [(box(s, x, 1.8, 2.9, 4.4, WHITE, RULE), "rise"),
            (box(s, x + 0.35, 2.2, 1.0, 1.0, TILE, shape=MSO_SHAPE.OVAL), "zoom"),
            (icon(s, ic, x + 0.6, 2.45, 0.5, HEX["good"]), "zoom"),
            (text(s, x + 0.35, 3.55, 2.3, 0.3, f"{i + 1:02d}", 12, MONO, GOOD), "fade"),
            (text(s, x + 0.35, 3.85, 2.4, 0.9, head, 23, SERIF, INK, spacing=1.0), "fade"),
            (text(s, x + 0.35, 4.75, 2.3, 1.4, body, 14, SANS, INK2, spacing=1.2), "fade")]
animate(s, seq, step=80)
notes(s, "Each recommendation comes from one chart: languages, achievements and publisher from figure 14, "
         "price from figure 8.")

# 27. Method
s = page("Method", "Every chart type chosen for its question")
thumbs = [(2, "Trend", "Line"), (3, "Compare", "Bar"), (4, "Two categories", "Heatmap"), (6, "Spread", "Box plot"),
          (7, "Distribution", "Histogram"), (13, "Relationship", "Scatter"), (11, "Part of whole", "Donut"),
          (10, "Part of whole", "Treemap"), (9, "Four numbers", "Bubble chart"), (8, "Mix within groups", "100% stacked"),
          (12, "Concentration", "Pareto line"), (14, "Two groups", "Grouped bar")]
seq = []
for i, (num, goal, kind) in enumerate(thumbs):
    col, row = i % 6, i // 6
    x, y = 0.6 + col * 2.05, 1.65 + row * 2.55
    seq += [(box(s, x, y, 1.9, 1.6, WHITE, RULE), "rise"),
            (picture(s, img[num], x + 0.05, y + 0.05, 1.8, 1.5), "fade"),
            (text(s, x, y + 1.7, 1.9, 0.3, goal.upper(), 9, MONO, ACCENT), "fade"),
            (text(s, x, y + 1.95, 1.9, 0.4, kind, 15, SERIF, INK), "fade")]
foot = text(s, 0.6, 6.55, 12.1, 0.35, "Following the lecture's 'Choosing the Right Chart' table. The dashboard explains "
            "every choice under each chart.", 12, SANS, INK3)
animate(s, seq + [(foot, "fade")], step=55)
notes(s, "We matched every chart to its question, following the lecture's table: trend, compare, distribution, "
         "relationship, part of whole.")

# 28. Questions + demo
s = prs.slides.add_slide(BLANK)
background(s, NAVY)
ttl = text(s, 0.8, 1.9, 11, 1.4, "Questions?", 66, SERIF, WHITE)
team = text(s, 0.8, 3.2, 11, 0.4, "  /  ".join(STUDENTS), 14, MONO, WHITE)
line = box(s, 0.8, 3.75, 1.6, 0.04, ACCENT)
src = text(s, 0.8, 4.05, 11.5, 2.2, ["LIVE DEMO  python app.py  ->  http://127.0.0.1:8050",
                                     "DATA  Steam Games Dataset (FronkonGames, Kaggle), 2006-2024",
                                     "TOOLS  pandas, NumPy, Plotly, Dash, python-pptx",
                                     "NOTE  Links, not proof: bigger studios tend to do all four things."],
           12, MONO, MIST, spacing=1.3, after=8)
set_transition(s, "morph")
animate(s, [(ttl, "rise"), (team, "fade"), (line, "wipe"), (src, "fade")], start=900, step=300)
notes(s, "Thank you. For the live demo: open the dashboard, pick a genre, and show that every chart and number "
         "changes together; then press Reset.")

assert len(prs.slides) == TOTAL_SLIDES, f"set TOTAL_SLIDES to {len(prs.slides)}"
path = f"{OUT}/Steam_Games_Presentation.pptx"
prs.save(path)
print("Saved", path, "-", len(prs.slides), "slides")

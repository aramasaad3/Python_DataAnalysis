# The AI Landscape in Data

An interactive dashboard with 15 charts in 5 sections, built in Python with Streamlit and Plotly.

**Research question:** What is driving the AI boom: bigger models, better chips, or more computing infrastructure? And is it paying off?

1. AI models: models per year, open vs closed, training compute trend, countries, industry vs academia
2. AI hardware: chip speed over time, correlation between chip specs
3. Compute & infrastructure: AI chip sales, GPU cluster map, mega data centers
4. Does it pay off?: US vs China capability race, task length AI can do alone, benchmark records, company revenue
5. The answer: growth per year of every driver compared on one chart

## Run it on your computer
1. Install Python 3.11 or newer.
2. Open a terminal in this folder and run:
   pip install -r requirements.txt
   python -m streamlit run app.py
   (On Windows you can also double-click run_dashboard.bat after installing.)

Data: Epoch AI (epoch.ai/data), licensed CC BY 4.0.

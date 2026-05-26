# 📊 Marketing Analytics Dashboard

> A professional, dark-themed marketing analytics dashboard built with Streamlit and Plotly — giving teams instant visibility into channel performance, campaign ROI, and regional trends.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?style=flat-square&logo=streamlit)
![Plotly](https://img.shields.io/badge/Plotly-5.22-3F4F75?style=flat-square&logo=plotly)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## Overview

This dashboard transforms raw marketing CSV data into a fully interactive analytics suite. It is designed for marketing analysts, growth teams, and performance marketers who need quick, reliable insights without wrestling with complex BI tooling.

All charts are interactive (zoom, pan, hover). The sidebar filters cascade across every panel simultaneously — update a filter once and the entire dashboard refreshes.

---

## Features

| Feature | Details |
|---|---|
| **KPI Cards** | 8 headline metrics — Revenue, Spend, Conversions, ROAS, Impressions, Clicks, CTR, CPA |
| **Revenue & Spend Trend** | Grouped bar chart with overlaid profit line, monthly granularity |
| **Channel Performance** | Donut chart showing channel share for any selectable metric |
| **Campaign Analysis** | Horizontal bar chart comparing revenue vs spend per campaign |
| **Channel Heatmap** | Revenue intensity grid — channels × months |
| **ROAS Bar Chart** | Per-channel ROAS with a visual target line at 3× |
| **Regional Breakdown** | Bar chart + spend-vs-revenue bubble chart per region |
| **Conversion Funnel** | Impressions → Clicks → Conversions with drop-off rates |
| **Rate Trends** | CTR and conversion rate over time on a dual-line chart |
| **Data Table** | Raw or grouped view with sort, group-by, and CSV export |
| **Sidebar Filters** | Date range, channel, region, campaign, primary metric selector |

---

## Tech Stack

- **[Streamlit](https://streamlit.io/)** — App framework and UI layout
- **[Plotly](https://plotly.com/python/)** — Interactive charts (bar, line, pie, scatter, heatmap, funnel)
- **[Pandas](https://pandas.pydata.org/)** — Data wrangling and aggregations
- **[NumPy](https://numpy.org/)** — Numerical helpers
- **[python-dotenv](https://pypi.org/project/python-dotenv/)** — Environment variable management

---

## Project Structure

```
marketing-analytics-dashboard/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── .env.example            # Environment variable template
└── data/
    └── marketing_data.csv  # Sample dataset (6 months, 5 channels, 4 regions)
```

---

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- pip (comes with Python)

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/marketing-analytics-dashboard.git
cd marketing-analytics-dashboard
```

### 2. Create a virtual environment (recommended)

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables (optional)

```bash
cp .env.example .env
# Edit .env with your preferred settings
```

The `.env` file is optional — the app runs fine with its defaults.

---

## How to Run

```bash
streamlit run app.py
```

The dashboard opens automatically at `http://localhost:8501`.

To run on a custom port:

```bash
streamlit run app.py --server.port 8080
```

---

## Using Your Own Data

Replace `data/marketing_data.csv` with your own CSV file. The file must include these columns:

| Column | Type | Description |
|---|---|---|
| `date` | YYYY-MM-DD | Date of the record |
| `channel` | string | Marketing channel (e.g. Google Ads) |
| `campaign` | string | Campaign name |
| `region` | string | Geographic region |
| `impressions` | integer | Ad impressions |
| `clicks` | integer | Clicks |
| `conversions` | integer | Conversions |
| `revenue` | float | Revenue generated |
| `spend` | float | Ad spend |
| `ctr` | float | Click-through rate (%) |
| `conversion_rate` | float | Conversion rate (%) |

Or point to a different file via `.env`:

```
DATA_PATH=data/my_custom_data.csv
```

---

## Configuration

All settings live in `.env` (copy from `.env.example`):

```env
APP_TITLE=Marketing Analytics Dashboard
DATA_PATH=data/marketing_data.csv
CURRENCY_SYMBOL=$
```

---

## License

MIT — free to use, modify, and distribute.

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

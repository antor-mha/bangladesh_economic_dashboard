# Bangladesh Economic Indicators Dashboard

Interactive web application for visualizing Bangladesh's economic indicators with ML predictions, regional comparisons, and detailed analytics.

## Overview

7 interactive dashboards covering GDP, inflation, employment, trade, remittance, development indicators, regional comparisons, correlations, and machine learning forecasts to 2034.

## Features

- GDP & Growth — Historical trends (1995–2026), growth rates, time period filters
- Inflation & Jobs — Rate trends, forecasting, unemployment analysis
- Trade & Remittance — RMG exports, remittance patterns, trade balance
- Development Indicators — Foreign reserves, infrastructure, sectoral metrics
- Regional Comparison — Bangladesh vs India, Pakistan, Sri Lanka benchmarks
- Correlation Analysis — Indicator relationships and dependencies
- ML Predictions — Linear, Polynomial & Random Forest forecasts through 2034
- Modern UI — Responsive design, interactive charts, PNG export, real-time filters

## Data

Bangladesh Dataset (bangladesh_economy.csv)
- Year, GDP, GDP Growth Rate, Inflation Rate, Unemployment Rate
- Remittance, RMG Exports, Foreign Reserves (1995–2026)

Neighbors Dataset (neighbors_data.csv)
- Regional comparison data for India, Pakistan, Sri Lanka

## Installation

Python 3.8+ required.

```bash
pip install dash plotly pandas scikit-learn kaleido
```

Run the notebook in Jupyter or run via Dash app.

## Structure

```
bangladesh_economic_dashboard/
├── bangladesh_economic_dash.ipynb   # Main notebook
├── bangladesh_economy.csv            # Dataset (1995-2026)
├── neighbors_data.csv                # Regional data
└── README.md
```

## Technologies

Dash, Plotly, Pandas, Scikit-learn, NumPy

## Models

Three ML algorithms for forecasting to 2034:
- Linear Regression
- Polynomial Regression (Degree 2)
- Random Forest
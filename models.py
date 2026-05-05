"""
ML model training and prediction functions
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score

PREDICT_UNTIL = 2034

INDICATORS = {
    'GDP_Billion_USD':          'GDP (Billion USD)',
    'GDP_Growth_Rate':          'GDP Growth Rate (%)',
    'Inflation_Rate':           'Inflation Rate (%)',
    'Unemployment_Rate':        'Unemployment Rate (%)',
    'Remittance_Billion_USD':   'Remittance (Billion USD)',
    'RMG_Export_Billion_USD':   'RMG Exports (Billion USD)',
    'Foreign_Reserve_Billion_USD': 'Foreign Reserves (Billion USD)',
}


def train_all_models(dataframe, column, until_year):
    """Train Linear, Polynomial, and Random Forest models. Return predictions + R2 scores."""
    X = dataframe[['Year']].values
    y = dataframe[column].values
    future_years = np.arange(dataframe['Year'].max() + 1, until_year + 1).reshape(-1, 1)

    models = {
        'Linear':     LinearRegression(),
        'Polynomial': make_pipeline(PolynomialFeatures(degree=2), LinearRegression()),
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
    }

    results = {}
    for name, model in models.items():
        model.fit(X, y)
        train_preds = model.predict(X)
        r2 = r2_score(y, train_preds)
        future_preds = model.predict(future_years)
        
        # RF can't extrapolate well — nudge it slightly
        if name == 'Random Forest':
            trend = (y[-1] - y[-3]) / 2
            future_preds = future_preds + trend * np.arange(1, len(future_preds) + 1) * 0.3
        
        results[name] = {
            'future_years': future_years.flatten(),
            'predictions':  future_preds,
            'r2':           round(r2, 4),
        }
    return results


def train_ml_models(df):
    """Pre-train all models for all indicators"""
    ml_results = {
        col: train_all_models(df, col, PREDICT_UNTIL)
        for col in INDICATORS
    }
    return ml_results

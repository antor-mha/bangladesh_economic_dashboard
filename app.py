"""
Bangladesh Economic Indicators Dashboard
Main application file
"""

import pandas as pd
import dash
from dash import html, dcc
import warnings

from models import train_ml_models
from styles import C, NAV_TABS
from callbacks import register_callbacks

warnings.filterwarnings('ignore')

# Load data
df = pd.read_csv('bangladesh_economy.csv')
nb = pd.read_csv('neighbors_data.csv')

print(f'✅ Bangladesh data: {df.shape[0]} rows, {df.shape[1]} columns')
print(f'✅ Neighbors data:  {nb.shape[0]} rows')

# Train ML models
ml_results = train_ml_models(df)
print(f'✅ ML models trained: {list(ml_results.keys())}')

# Initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = 'Bangladesh Economy Dashboard'

# Build layout
app.layout = html.Div(
    style={
        'backgroundColor': C['bg'],
        'minHeight': '100vh',
        'fontFamily': 'Arial, sans-serif',
        'display': 'flex',
        'flexDirection': 'column'
    },
    children=[

        # ── Top Header Bar ──
        html.Div(style={
            'background': f'linear-gradient(135deg, {C["green"]} 0%, #14532d 100%)',
            'padding': '16px 28px',
            'borderBottom': f'3px solid {C["red"]}',
            'display': 'flex',
            'justifyContent': 'space-between',
            'alignItems': 'center',
            'flexShrink': '0',
        }, children=[
            html.Div([
                html.H1('Bangladesh Economic Indicators',
                        style={
                            'color': '#fff',
                            'fontSize': '22px',
                            'fontWeight': '800',
                            'margin': '0 0 2px'
                        }),
                html.P('Historical Data (1995–2026) · ML Forecasts (2027–2034) · South Asia Comparison',
                       style={
                           'color': 'rgba(255,255,255,0.75)',
                           'fontSize': '12px',
                           'margin': '0'
                       }),
            ]),
            html.Div(style={'display': 'flex', 'gap': '10px', 'alignItems': 'center'}, children=[
                html.Button('Export PNG', id='export-btn', n_clicks=0,
                            style={
                                'background': 'rgba(255,255,255,0.15)',
                                'color': '#fff',
                                'border': '1px solid rgba(255,255,255,0.4)',
                                'borderRadius': '8px',
                                'padding': '7px 16px',
                                'cursor': 'pointer',
                                'fontSize': '13px',
                                'fontWeight': '600'
                            }),
                dcc.Download(id='download-png'),
            ]),
        ]),

        # ── Stat Cards Row ──
        html.Div(style={
            'padding': '14px 28px',
            'borderBottom': f'1px solid {C["border"]}',
            'background': C['card']
        }, children=[
            html.Div(id='stat-cards',
                     style={'display': 'flex', 'gap': '10px', 'flexWrap': 'wrap'}),
        ]),

        # ── Body: Sidebar + Content ──
        html.Div(style={'display': 'flex', 'flex': '1', 'overflow': 'hidden'}, children=[

            # ── Sidebar ──
            html.Div(style={
                'width': '220px',
                'minWidth': '220px',
                'background': C['card'],
                'borderRight': f'1px solid {C["border"]}',
                'padding': '20px 12px',
                'display': 'flex',
                'flexDirection': 'column',
                'gap': '2px',
            }, children=[

                html.P('NAVIGATION', style={
                    'color': C['muted'],
                    'fontSize': '10px',
                    'fontWeight': '700',
                    'letterSpacing': '0.1em',
                    'margin': '0 0 10px 8px',
                }),

                # Nav items
                *[html.Div(
                    children=[
                        html.Span(icon, style={'fontSize': '16px', 'width': '22px'}),
                        html.Span(label, style={'fontSize': '13px', 'fontWeight': '500'}),
                    ],
                    id={'type': 'nav-btn', 'index': value},
                    n_clicks=0,
                    style={
                        'display': 'flex',
                        'alignItems': 'center',
                        'gap': '10px',
                        'padding': '10px 14px',
                        'borderRadius': '8px',
                        'cursor': 'pointer',
                        'marginBottom': '2px',
                        'color': C['text'],
                        'border': '1px solid transparent',
                    }
                ) for icon, label, value in NAV_TABS],

                html.Hr(style={
                    'border': 'none',
                    'borderTop': f'1px solid {C["border"]}',
                    'margin': '16px 0'
                }),

                # Year Range in sidebar
                html.P('YEAR RANGE', style={
                    'color': C['muted'],
                    'fontSize': '10px',
                    'fontWeight': '700',
                    'letterSpacing': '0.1em',
                    'margin': '0 0 8px 4px',
                }),
                dcc.Dropdown(
                    id='year-range',
                    options=[
                        {'label': 'All Years (1995–2026)', 'value': 'all'},
                        {'label': '2000s (2000–2009)',     'value': '2000s'},
                        {'label': '2010s (2010–2019)',     'value': '2010s'},
                        {'label': 'Recent (2020–2026)',    'value': 'recent'},
                    ],
                    value='all',
                    clearable=False,
                    style={'fontSize': '12px'},
                ),

                html.Hr(style={
                    'border': 'none',
                    'borderTop': f'1px solid {C["border"]}',
                    'margin': '16px 0'
                }),

                # What-if slider
                html.Div([
                    html.P('WHAT-IF GROWTH %', style={
                        'color': C['muted'],
                        'fontSize': '10px',
                        'fontWeight': '700',
                        'letterSpacing': '0.1em',
                        'margin': '0 0 8px 4px',
                    }),
                    dcc.Slider(
                        id='whatif-slider',
                        min=1,
                        max=10,
                        step=0.5,
                        value=5.0,
                        marks={i: f'{i}%' for i in [1, 3, 5, 7, 10]},
                        tooltip={'placement': 'bottom', 'always_visible': True}
                    ),
                ], id='whatif-controls', style={'display': 'none'}),

                # Hidden store
                dcc.Store(id='report-type', data='gdp'),

                html.Div(style={'flex': '1'}),

                html.P('Data: World Bank & IMF',
                       style={
                           'color': C['muted'],
                           'fontSize': '10px',
                           'textAlign': 'center',
                           'margin': '0'
                       }),
            ]),

            # ── Main Content ──
            html.Div(style={
                'flex': '1',
                'overflowY': 'auto',
                'padding': '24px 28px'
            }, children=[

                # Section title
                html.Div(id='section-title', style={'marginBottom': '16px'}, children=[
                    html.H2('GDP & Growth',
                            style={
                                'color': C['text'],
                                'fontSize': '20px',
                                'fontWeight': '700',
                                'margin': '0'
                            }),
                ]),

                # Charts output
                html.Div(id='charts-container'),
            ]),
        ]),
    ],
)

# Register all callbacks
register_callbacks(app, df, nb, ml_results)

if __name__ == '__main__':
    print('✅ Starting dashboard on http://127.0.0.1:8052/')
    app.run(debug=True, port=8052)

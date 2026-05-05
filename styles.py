"""
Design system, colors, and UI components
"""

from dash import html, dcc
import plotly.graph_objects as go

# Color Palette
C = {
    'bg':           '#f8fafc',
    'card':         '#ffffff',
    'border':       '#e2e8f0',
    'green':        '#16a34a',
    'green_light':  '#dcfce7',
    'red':          '#dc2626',
    'red_light':    '#fee2e2',
    'blue':         '#2563eb',
    'blue_light':   '#dbeafe',
    'amber':        '#d97706',
    'amber_light':  '#fef3c7',
    'purple':       '#7c3aed',
    'purple_light': '#ede9fe',
    'teal':         '#0d9488',
    'text':         '#0f172a',
    'muted':        '#64748b',
    'grid':         '#f1f5f9',
}

# Chart Layout Template
CHART = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color=C['text'], family='Arial', size=12),
    xaxis=dict(gridcolor=C['grid'], showgrid=True, linecolor=C['border']),
    yaxis=dict(gridcolor=C['grid'], showgrid=True, linecolor=C['border']),
    legend=dict(bgcolor='rgba(0,0,0,0)', borderwidth=0),
    margin=dict(l=10, r=10, t=44, b=10),
    title_font=dict(size=14, color=C['text']),
)

# Model Colors for Forecasts
MODEL_COLORS = {
    'Historical':   C['blue'],
    'Linear':       C['red'],
    'Polynomial':   C['green'],
    'Random Forest': C['purple'],
}

# Navigation Tabs
NAV_TABS = [
    ('📈', 'GDP & Growth',       'gdp'),
    ('💸', 'Inflation & Jobs',   'inflation'),
    ('🌍', 'Trade & Remittance', 'trade'),
    ('⚡', 'Development',        'dev'),
    ('🌏', 'vs Neighbors',       'neighbors'),
    ('🔗', 'Correlations',       'correlation'),
    ('🤖', 'ML Predictions',     'ml'),
]


def apply_theme(fig):
    """Apply theme to plotly figure"""
    fig.update_layout(**CHART)
    return fig


def card(children, extra=None):
    """Reusable card component"""
    s = {
        'background': C['card'],
        'border': f'1px solid {C["border"]}',
        'borderRadius': '12px',
        'padding': '20px'
    }
    if extra:
        s.update(extra)
    return html.Div(children, style=s)


def stat_card(label, value, color, bg):
    """Stat card with label and value"""
    return html.Div([
        html.P(label, style={
            'color': C['muted'], 'fontSize': '12px',
            'margin': '0 0 4px', 'fontWeight': '500'
        }),
        html.P(value, style={
            'color': color, 'fontSize': '20px',
            'fontWeight': '700', 'margin': '0'
        }),
    ], style={
        'background': bg,
        'borderRadius': '10px',
        'padding': '14px 18px',
        'flex': '1',
        'minWidth': '130px',
        'border': f'1px solid {C["border"]}'
    })


def insight_banner(text, color, bg):
    """Insight banner with colored background"""
    return html.Div(
        html.P(f'💡 {text}', style={
            'margin': '0',
            'fontSize': '13px',
            'color': color,
            'fontWeight': '500'
        }),
        style={
            'background': bg,
            'borderRadius': '8px',
            'padding': '10px 16px',
            'marginBottom': '16px',
            'border': f'1px solid {color}22'
        }
    )


def chart_card(fig, width='calc(50% - 8px)'):
    """Card wrapper for charts"""
    return html.Div(
        dcc.Graph(figure=fig, config={
            'displayModeBar': True,
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'bd_chart',
                'height': 500,
                'width': 900,
                'scale': 2
            },
        }),
        style={
            'width': width,
            'minWidth': '280px',
            'background': C['card'],
            'border': f'1px solid {C["border"]}',
            'borderRadius': '12px',
            'padding': '6px',
            'boxSizing': 'border-box'
        }
    )


def grid(charts):
    """Flex grid layout for charts"""
    return html.Div(charts, style={
        'display': 'flex',
        'flexWrap': 'wrap',
        'gap': '16px',
        'justifyContent': 'flex-start',
        'width': '100%',
        'boxSizing': 'border-box'
    })


def year_filter(dataframe, year_range):
    """Filter dataframe by year range"""
    ranges = {
        'all': (1995, 2026),
        '2000s': (2000, 2009),
        '2010s': (2010, 2019),
        'recent': (2020, 2026)
    }
    s, e = ranges.get(year_range, (1995, 2026))
    return dataframe[(dataframe['Year'] >= s) & (dataframe['Year'] <= e)]

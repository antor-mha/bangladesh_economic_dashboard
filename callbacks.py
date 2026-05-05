"""
Callbacks for Dash app interactivity
"""

import json
import dash
from dash import Input, Output
from dash.dependencies import ALL
from styles import C, year_filter, chart_card, grid, insight_banner, stat_card
import plotly.express as px
import plotly.graph_objects as go
from charts import (
    create_gdp_charts, create_inflation_charts,
    create_trade_charts, create_dev_charts
)
from models import INDICATORS, PREDICT_UNTIL
from dash import html, dcc


def register_callbacks(app, df, nb, ml_results):
    """Register all Dash callbacks"""

    # ── Callback: Handle sidebar nav clicks ──
    @app.callback(
        Output('report-type', 'data'),
        Input({'type': 'nav-btn', 'index': ALL}, 'n_clicks'),
        prevent_initial_call=True,
    )
    def update_active_tab(n_clicks_list):
        ctx = dash.callback_context
        if not ctx.triggered:
            return 'gdp'
        triggered_id = ctx.triggered[0]['prop_id']
        id_dict = json.loads(triggered_id.split('.')[0])
        return id_dict['index']

    # ── Callback: Highlight active nav item ──
    @app.callback(
        [Output({'type': 'nav-btn', 'index': val}, 'style') for _, _, val in [
            ('📈', 'GDP & Growth',       'gdp'),
            ('💸', 'Inflation & Jobs',   'inflation'),
            ('🌍', 'Trade & Remittance', 'trade'),
            ('⚡', 'Development',        'dev'),
            ('🌏', 'vs Neighbors',       'neighbors'),
            ('🔗', 'Correlations',       'correlation'),
            ('🤖', 'ML Predictions',     'ml'),
        ]],
        Input('report-type', 'data'),
    )
    def highlight_nav(active_tab):
        styles = []
        for _, _, val in [
            ('📈', 'GDP & Growth',       'gdp'),
            ('💸', 'Inflation & Jobs',   'inflation'),
            ('🌍', 'Trade & Remittance', 'trade'),
            ('⚡', 'Development',        'dev'),
            ('🌏', 'vs Neighbors',       'neighbors'),
            ('🔗', 'Correlations',       'correlation'),
            ('🤖', 'ML Predictions',     'ml'),
        ]:
            if val == active_tab:
                styles.append({
                    'display': 'flex', 'alignItems': 'center', 'gap': '10px',
                    'padding': '10px 14px', 'borderRadius': '8px', 'cursor': 'pointer',
                    'marginBottom': '2px', 'color': '#fff',
                    'background': '#16a34a',
                    'border': '1px solid #16a34a',
                    'fontWeight': '600',
                })
            else:
                styles.append({
                    'display': 'flex', 'alignItems': 'center', 'gap': '10px',
                    'padding': '10px 14px', 'borderRadius': '8px', 'cursor': 'pointer',
                    'marginBottom': '2px', 'color': '#0f172a',
                    'background': 'transparent',
                    'border': '1px solid transparent',
                })
        return styles

    # ── Callback: Update section title ──
    @app.callback(
        Output('section-title', 'children'),
        Input('report-type', 'data'),
    )
    def update_section_title(tab):
        labels = {
            'gdp':         '📈 GDP & Growth',
            'inflation':   '💸 Inflation & Jobs',
            'trade':       '🌍 Trade & Remittance',
            'dev':         '⚡ Development Indicators',
            'neighbors':   '🌏 Bangladesh vs Neighbors',
            'correlation': '🔗 Correlations',
            'ml':          '🤖 ML Predictions (2027–2034)',
        }
        return html.H2(labels.get(tab, ''),
                       style={'color': '#0f172a', 'fontSize': '20px',
                              'fontWeight': '700', 'margin': '0'})

    # ── Callback: Show what-if slider only on ML tab ──
    @app.callback(
        Output('whatif-controls', 'style'),
        Input('report-type', 'data'),
    )
    def toggle_whatif(tab):
        if tab == 'ml':
            return {'display': 'block'}
        return {'display': 'none'}

    # ── Callback: Dynamic stat cards ──
    @app.callback(
        Output('stat-cards', 'children'),
        Input('year-range', 'value'),
    )
    def update_stat_cards(year_range):
        fd = year_filter(df, year_range)
        latest = fd.iloc[-1]
        first = fd.iloc[0]
        gdp_growth_pct = ((latest['GDP_Billion_USD'] - first['GDP_Billion_USD'])
                          / first['GDP_Billion_USD'] * 100)
        return [
            stat_card(f'GDP {int(latest["Year"])}',
                      f'${latest["GDP_Billion_USD"]:.0f}B',       C['green'],  C['green_light']),
            stat_card(f'Growth {int(latest["Year"])}',
                      f'{latest["GDP_Growth_Rate"]}%',             C['blue'],   C['blue_light']),
            stat_card(f'Inflation {int(latest["Year"])}',
                      f'{latest["Inflation_Rate"]}%',              C['red'],    C['red_light']),
            stat_card(f'Unemployment',
                      f'{latest["Unemployment_Rate"]}%',           C['amber'],  C['amber_light']),
            stat_card(f'Remittance {int(latest["Year"])}',
                      f'${latest["Remittance_Billion_USD"]}B',     C['teal'],   '#ccfbf1'),
            stat_card(f'RMG Exports {int(latest["Year"])}',
                      f'${latest["RMG_Export_Billion_USD"]}B',     C['purple'], C['purple_light']),
            stat_card(f'Forex Reserves',
                      f'${latest["Foreign_Reserve_Billion_USD"]}B', C['blue'],  C['blue_light']),
            stat_card(f'Range GDP Growth',
                      f'{gdp_growth_pct:.1f}%',                    C['green'],  C['green_light']),
        ]

    # ── Main Callback: Render charts ──
    @app.callback(
        Output('charts-container', 'children'),
        [Input('report-type', 'data'),
         Input('year-range',  'value'),
         Input('whatif-slider', 'value')],
        prevent_initial_call=False,
    )
    def update_charts(tab, year_range, whatif_rate):
        whatif_rate = whatif_rate if whatif_rate is not None else 5.0
        fd = year_filter(df, year_range)
        
        if tab == 'gdp':
            return create_gdp_charts(df, year_range)
        elif tab == 'inflation':
            return create_inflation_charts(df, year_range)
        elif tab == 'trade':
            return create_trade_charts(df, year_range)
        elif tab == 'dev':
            return create_dev_charts(df, year_range)
        elif tab == 'neighbors':
            return create_neighbors_charts(df, nb, year_range)
        elif tab == 'correlation':
            return create_correlation_charts(df, year_range)
        elif tab == 'ml':
            return create_ml_charts(df, ml_results, year_range, whatif_rate)
        
        return html.Div()

    # ── Export PNG Callback ──
    @app.callback(
        Output('download-png', 'data'),
        Input('export-btn', 'n_clicks'),
        prevent_initial_call=True,
    )
    def export_png(n_clicks):
        import plotly.io as pio
        from plotly.subplots import make_subplots

        fig = make_subplots(
            rows=3, cols=3,
            subplot_titles=[
                'GDP (Billion USD)', 'GDP Growth Rate (%)', 'Inflation Rate (%)',
                'Unemployment Rate (%)', 'Remittance (Billion USD)', 'RMG Exports (Billion USD)',
                'Electricity Coverage (%)', 'Internet Users (M)', 'Poverty Rate (%)',
            ],
        )
        plots = [
            ('GDP_Billion_USD',         C['green'],  1,1),
            ('GDP_Growth_Rate',         C['blue'],   1,2),
            ('Inflation_Rate',          C['red'],    1,3),
            ('Unemployment_Rate',       C['amber'],  2,1),
            ('Remittance_Billion_USD',  C['purple'], 2,2),
            ('RMG_Export_Billion_USD',  C['teal'],   2,3),
            ('Electricity_Coverage',    C['amber'],  3,1),
            ('Internet_Users_Million',  C['blue'],   3,2),
            ('Poverty_Rate',            C['red'],    3,3),
        ]
        for col, color, row, c in plots:
            fig.add_trace(go.Scatter(
                x=df['Year'], y=df[col], mode='lines+markers',
                line=dict(color=color, width=2), marker=dict(size=4), showlegend=False),
                row=row, col=c)

        fig.update_layout(
            height=1000, width=1600,
            title_text='Bangladesh Economic Indicators — Full Summary (1995–2024)',
            title_font=dict(size=20, color=C['text']),
            paper_bgcolor='#f8fafc', plot_bgcolor='#ffffff',
            font=dict(color=C['text'], family='Arial'),
        )
        fig.update_xaxes(gridcolor=C['grid'])
        fig.update_yaxes(gridcolor=C['grid'])

        img_bytes = pio.to_image(fig, format='png', scale=2)
        return dcc.send_bytes(img_bytes, 'bangladesh_full_summary.png')


def create_neighbors_charts(df, nb, year_range):
    """Create Neighbors comparison charts"""
    from styles import apply_theme
    fd = year_filter(df, year_range)
    y_start = int(fd['Year'].iloc[0])
    y_end = int(fd['Year'].iloc[-1])
    
    COUNTRY_COLORS = {
        'Bangladesh': C['green'], 'India': C['amber'],
        'Pakistan': C['blue'], 'Sri Lanka': C['purple'],
        'Nepal': C['teal'], 'Myanmar': C['red'],
    }
    
    nb_fd = nb[(nb['Year'] >= y_start) & (nb['Year'] <= y_end)]
    if nb_fd.empty:
        nb_fd = nb

    f1 = apply_theme(px.line(nb_fd, x='Year', y='GDP_Per_Capita_USD', color='Country',
                              title=f'GDP Per Capita Comparison', markers=True,
                              color_discrete_map=COUNTRY_COLORS))
    
    f2 = apply_theme(px.bar(nb_fd, x='Country', y='GDP_Per_Capita_USD',
                             animation_frame='Year', title='GDP Per Capita Race',
                             color='Country', color_discrete_map=COUNTRY_COLORS))
    
    f3 = apply_theme(px.line(nb_fd, x='Year', y='GDP_Growth_Rate', color='Country',
                              title='GDP Growth Rate Comparison %', markers=True,
                              color_discrete_map=COUNTRY_COLORS))
    
    f4 = apply_theme(px.line(nb_fd, x='Year', y='Inflation_Rate', color='Country',
                              title='Inflation Rate Comparison %', markers=True,
                              color_discrete_map=COUNTRY_COLORS))

    latest_year = int(nb_fd['Year'].max())
    latest_nb = nb_fd[nb_fd['Year'] == latest_year].copy()
    
    f5 = go.Figure()
    cats = ['GDP_Per_Capita_USD', 'GDP_Growth_Rate', 'Inflation_Rate', 'Unemployment_Rate']
    cat_labels = ['GDP/Capita', 'GDP Growth', 'Inflation', 'Unemployment']
    
    for _, row in latest_nb.iterrows():
        vals = [row[c] for c in cats]
        denom = [(nb[c].max() - nb[c].min()) for c in cats]
        vals_norm = [(v - nb[c].min()) / d * 100 if d > 0 else 0
                     for v, c, d in zip(vals, cats, denom)]
        f5.add_trace(go.Scatterpolar(
            r=vals_norm + [vals_norm[0]],
            theta=cat_labels + [cat_labels[0]],
            name=row['Country'],
            line=dict(color=COUNTRY_COLORS.get(row['Country'], '#888'))
        ))
    
    f5.update_layout(title=f'{latest_year} Comparison (Normalized)',
                     polar=dict(bgcolor='rgba(0,0,0,0)'),
                     paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                     font=dict(color=C['text'], family='Arial', size=12))

    rank_df = nb_fd.copy()
    rank_df['Rank'] = rank_df.groupby('Year')['GDP_Per_Capita_USD'].rank(ascending=False)
    bd_rank = rank_df[rank_df['Country'] == 'Bangladesh'].copy()
    
    f6 = apply_theme(px.line(bd_rank, x='Year', y='Rank',
                              title='Bangladesh Rank (lower = better)', markers=True,
                              color_discrete_sequence=[C['green']]))
    f6.update_yaxes(autorange='reversed', tickvals=[1,2,3,4,5,6])

    bd_latest = nb_fd[(nb_fd['Country']=='Bangladesh') & (nb_fd['Year']==latest_year)]
    bd_gdp = bd_latest['GDP_Per_Capita_USD'].values[0]
    bd_rank_val = int(rank_df[(rank_df['Country']=='Bangladesh') &
                              (rank_df['Year']==latest_year)]['Rank'].values[0])
    
    ins = insight_banner(
        f"Bangladesh GDP per capita: ${bd_gdp:,.0f} — ranked #{bd_rank_val} in South Asia",
        C['green'], C['green_light'])
    
    return html.Div([ins, grid([chart_card(f1), chart_card(f2),
                                chart_card(f3), chart_card(f4),
                                chart_card(f5), chart_card(f6)])])


def create_correlation_charts(df, year_range):
    """Create Correlation analysis charts"""
    from styles import apply_theme
    fd = year_filter(df, year_range)
    y_start = int(fd['Year'].iloc[0])
    y_end = int(fd['Year'].iloc[-1])
    
    num_cols = ['GDP_Billion_USD','GDP_Growth_Rate','Inflation_Rate',
                'Unemployment_Rate','Remittance_Billion_USD',
                'Export_Billion_USD','Import_Billion_USD','Poverty_Rate',
                'Electricity_Coverage','Internet_Users_Million','CO2_Emissions_MT']
    
    corr = fd[num_cols].corr().round(2)
    short = ['GDP','GDP Gr.','Inflation','Unemploy.','Remittance',
             'Export','Import','Poverty','Electricity','Internet','CO₂']
    
    f1 = go.Figure(go.Heatmap(
        z=corr.values, x=short, y=short,
        colorscale=[[0,C['red']],[0.5,'#f8fafc'],[1,C['green']]],
        zmid=0, text=corr.values.round(2),
        texttemplate='%{text}', textfont=dict(size=10),
        hoverongaps=False,
    ))
    f1.update_layout(title=f'Correlation Heatmap', paper_bgcolor='rgba(0,0,0,0)',
                     plot_bgcolor='rgba(0,0,0,0)', font=dict(color=C['text']))

    f2 = apply_theme(px.scatter(fd, x='GDP_Per_Capita_USD', y='Poverty_Rate',
                                 color='Year', size='Population_Million',
                                 title='GDP Per Capita vs Poverty',
                                 trendline='ols',
                                 color_continuous_scale='Blues'))
    
    f3 = apply_theme(px.scatter(fd, x='GDP_Billion_USD', y='CO2_Emissions_MT',
                                 color='Year', size='Population_Million',
                                 title='GDP vs CO₂ Emissions',
                                 trendline='ols',
                                 color_continuous_scale='Reds'))
    
    f4 = apply_theme(px.scatter(fd, x='Remittance_Billion_USD', y='GDP_Billion_USD',
                                 color='Year', size='Import_Billion_USD',
                                 title='Remittance vs GDP',
                                 trendline='ols',
                                 color_continuous_scale='Greens'))
    
    corr_val = fd['GDP_Per_Capita_USD'].corr(fd['Poverty_Rate'])
    ins = insight_banner(
        f"Strong correlation (r = {corr_val:.2f}) between GDP per capita and poverty reduction",
        C['purple'], C['purple_light'])
    
    return html.Div([ins, grid([chart_card(f1, width='98%'),
                                chart_card(f2), chart_card(f3), chart_card(f4)])])


def create_ml_charts(df, ml_results, year_range, whatif_rate):
    """Create ML Predictions charts"""
    from styles import apply_theme
    
    last_gdp = df['GDP_Billion_USD'].iloc[-1]
    last_year = int(df['Year'].iloc[-1])
    wi_years = list(range(last_year + 1, last_year + 11))
    wi_gdp = [last_gdp * ((1 + whatif_rate/100)**i) for i in range(1, 11)]
    
    wi_fig = go.Figure()
    wi_fig.add_trace(go.Scatter(
        x=df['Year'], y=df['GDP_Billion_USD'],
        mode='lines+markers', name='Historical',
        line=dict(color=C['blue'], width=2.5)))
    wi_fig.add_trace(go.Scatter(
        x=wi_years, y=wi_gdp,
        mode='lines+markers', name=f'What-if @ {whatif_rate}%',
        line=dict(color=C['green'], width=2.5, dash='dash'),
        marker=dict(symbol='diamond', size=7)))
    wi_fig.add_vline(x=last_year + 0.5, line_dash='dot', line_color=C['muted'])
    wi_fig.update_layout(title=f'What-if: GDP @ {whatif_rate}% growth',
                         paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                         font=dict(color=C['text']))
    
    charts = [chart_card(apply_theme(wi_fig), width='98%')]
    r2_cards = []
    
    for col, label in list(INDICATORS.items())[:3]:
        scores = ml_results[col]
        r2_cards.append(html.Div([
            html.P(label, style={'fontWeight': '700', 'color': C['text'],
                                 'fontSize': '13px', 'margin': '0 0 8px'}),
            html.Div(style={'display': 'flex', 'gap': '8px'}, children=[
                html.Span(f'Linear: {scores["Linear"]["r2"]}',
                          style={'background': C['red_light'], 'color': C['red'],
                                 'borderRadius': '6px', 'padding': '3px 8px',
                                 'fontSize': '12px', 'fontWeight': '600'}),
                html.Span(f'Poly: {scores["Polynomial"]["r2"]}',
                          style={'background': C['green_light'], 'color': C['green'],
                                 'borderRadius': '6px', 'padding': '3px 8px',
                                 'fontSize': '12px', 'fontWeight': '600'}),
                html.Span(f'RF: {scores["Random Forest"]["r2"]}',
                          style={'background': C['purple_light'], 'color': C['purple'],
                                 'borderRadius': '6px', 'padding': '3px 8px',
                                 'fontSize': '12px', 'fontWeight': '600'}),
            ]),
        ], style={'background': C['card'], 'border': f'1px solid {C["border"]}',
                  'borderRadius': '10px', 'padding': '14px', 'flex': '1', 'minWidth': '280px'}))
    
    r2_row = html.Div([
        html.P('Model Accuracy (R² Score)',
               style={'fontWeight': '700', 'color': C['text'],
                      'fontSize': '14px', 'margin': '0 0 12px'}),
        html.Div(r2_cards, style={'display': 'flex', 'gap': '12px', 'flexWrap': 'wrap'}),
    ], style={'background': C['bg'], 'border': f'1px solid {C["border"]}',
              'borderRadius': '12px', 'padding': '16px', 'marginBottom': '16px'})
    
    for col, label in INDICATORS.items():
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['Year'], y=df[col],
            mode='lines+markers', name='Historical',
            line=dict(color=MODEL_COLORS['Historical'], width=2.5)))
        
        for model_name in ['Linear', 'Polynomial', 'Random Forest']:
            res = ml_results[col][model_name]
            fig.add_trace(go.Scatter(
                x=res['future_years'], y=res['predictions'],
                mode='lines+markers', name=f'{model_name} (R²={res["r2"]})',
                line=dict(color=MODEL_COLORS[model_name], width=2, dash='dash'),
                marker=dict(size=5, symbol='diamond')))
        
        fig.add_vline(x=last_year + 0.5, line_dash='dot', line_color=C['muted'])
        fig.update_layout(title=label, paper_bgcolor='rgba(0,0,0,0)',
                         plot_bgcolor='rgba(0,0,0,0)', font=dict(color=C['text']))
        charts.append(chart_card(apply_theme(fig)))
    
    ins = insight_banner(
        f"At {whatif_rate}% growth: GDP could reach ${wi_gdp[-1]:.0f}B by {wi_years[-1]}",
        C['purple'], C['purple_light'])
    
    return html.Div([ins, r2_row, grid(charts)])

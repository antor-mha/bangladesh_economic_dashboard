"""
Chart generation functions for each dashboard tab
"""

import plotly.express as px
import plotly.graph_objects as go
from dash import html
from styles import (
    apply_theme, chart_card, grid, insight_banner,
    C, MODEL_COLORS, year_filter
)


def create_gdp_charts(df, year_range):
    """Create GDP & Growth dashboard charts"""
    fd = year_filter(df, year_range)
    y_start = int(fd['Year'].iloc[0])
    y_end = int(fd['Year'].iloc[-1])

    f1 = apply_theme(px.area(fd, x='Year', y='GDP_Billion_USD',
                              title='GDP Over Time (Billion USD)',
                              color_discrete_sequence=[C['green']]))
    
    f2 = apply_theme(px.bar(fd, x='Year', y='GDP_Growth_Rate',
                             title='Annual GDP Growth Rate (%)',
                             color='GDP_Growth_Rate',
                             color_continuous_scale=[[0,'#ef4444'],[0.4,'#fbbf24'],[1,'#22c55e']]))
    
    f3 = apply_theme(px.line(fd, x='Year', y='GDP_Per_Capita_USD',
                              title='GDP Per Capita (USD)', markers=True,
                              color_discrete_sequence=[C['blue']]))
    
    f4 = apply_theme(px.scatter(fd, x='GDP_Growth_Rate', y='GDP_Per_Capita_USD',
                                 size='GDP_Billion_USD', color='Year',
                                 title='Growth Rate vs Per Capita (bubble = GDP size)',
                                 color_continuous_scale='Blues'))
    
    ddf = fd.copy()
    ddf['Decade'] = (ddf['Year'] // 10 * 10).astype(str) + 's'
    decade_avg = ddf.groupby('Decade')[['GDP_Growth_Rate','Inflation_Rate','Unemployment_Rate']].mean().reset_index()
    
    f5 = apply_theme(px.bar(decade_avg, x='Decade',
                             y=['GDP_Growth_Rate','Inflation_Rate','Unemployment_Rate'],
                             title='Decade Averages: Growth vs Inflation vs Unemployment',
                             barmode='group',
                             color_discrete_sequence=[C['green'], C['red'], C['amber']]))
    
    f6 = go.Figure()
    f6.add_trace(go.Scatter(x=fd['Year'], y=fd['GDP_Billion_USD'],
                             mode='lines', fill='tozeroy',
                             fillcolor='rgba(22,163,74,0.1)',
                             line=dict(color=C['green'], width=2.5)))
    
    for yr_val, label in [(2006,'$61B: Garments boom'),(2015,'$195B: Digital BD'),(2021,'$355B: Post-COVID')]:
        row = fd[fd['Year']==yr_val]
        if not row.empty:
            f6.add_annotation(x=yr_val, y=row['GDP_Billion_USD'].values[0], text=label,
                              showarrow=True, arrowhead=2, arrowcolor=C['muted'],
                              font=dict(size=10, color=C['muted']),
                              bgcolor='white', bordercolor=C['border'])
    
    f6.update_layout(title='GDP Journey with Key Milestones', **{'paper_bgcolor':'rgba(0,0,0,0)', 'plot_bgcolor':'rgba(0,0,0,0)', 'font':dict(color=C['text'], family='Arial', size=12), 'xaxis':dict(gridcolor=C['grid'], showgrid=True, linecolor=C['border']), 'yaxis':dict(gridcolor=C['grid'], showgrid=True, linecolor=C['border']), 'legend':dict(bgcolor='rgba(0,0,0,0)', borderwidth=0), 'margin':dict(l=10, r=10, t=44, b=10), 'title_font':dict(size=14, color=C['text'])})
    
    ins = insight_banner(
        f"Bangladesh's GDP grew {fd['GDP_Billion_USD'].iloc[-1]/fd['GDP_Billion_USD'].iloc[0]:.1f}x "
        f"from {y_start} to {y_end} — average growth of {fd['GDP_Growth_Rate'].mean():.1f}% per year.",
        C['green'], C['green_light'])
    
    return html.Div([ins, grid([chart_card(f1), chart_card(f2),
                                chart_card(f3), chart_card(f4),
                                chart_card(f5), chart_card(f6)])])


def create_inflation_charts(df, year_range):
    """Create Inflation & Jobs dashboard charts"""
    fd = year_filter(df, year_range)
    y_start = int(fd['Year'].iloc[0])
    y_end = int(fd['Year'].iloc[-1])

    f1 = apply_theme(px.line(fd, x='Year', y='Inflation_Rate',
                              title='Inflation Rate (%)', markers=True,
                              color_discrete_sequence=[C['red']]))
    f1.add_hline(y=5, line_dash='dash', line_color=C['muted'],
                 annotation_text='5% target', annotation_font_color=C['muted'])
    
    f2 = apply_theme(px.bar(fd, x='Year', y='Unemployment_Rate',
                             title='Unemployment Rate (%)',
                             color='Unemployment_Rate',
                             color_continuous_scale=[[0, C['green']], [1, C['red']]]))
    
    f3 = apply_theme(px.scatter(fd, x='Inflation_Rate', y='Unemployment_Rate',
                                 text='Year', color='Year',
                                 title='Phillips Curve: Inflation vs Unemployment',
                                 color_continuous_scale='RdYlGn_r'))
    
    f4 = apply_theme(px.line(fd, x='Year', y=['Inflation_Rate','Unemployment_Rate'],
                              title='Inflation vs Unemployment Trend', markers=True,
                              color_discrete_sequence=[C['red'], C['amber']]))
    
    f5 = apply_theme(px.area(fd, x='Year', y='Poverty_Rate',
                              title='Poverty Rate Over Time (%)',
                              color_discrete_sequence=[C['amber']]))
    
    f6 = apply_theme(px.scatter(fd, x='Inflation_Rate', y='Poverty_Rate',
                                 color='Year', size='Unemployment_Rate',
                                 title='Inflation vs Poverty Rate',
                                 color_continuous_scale='YlOrRd'))
    
    poverty_drop = fd['Poverty_Rate'].iloc[0] - fd['Poverty_Rate'].iloc[-1]
    ins = insight_banner(
        f"Poverty dropped from {fd['Poverty_Rate'].iloc[0]}% in {y_start} to "
        f"{fd['Poverty_Rate'].iloc[-1]}% in {y_end} — a {poverty_drop:.1f}pp reduction "
        f"despite average inflation of {fd['Inflation_Rate'].mean():.1f}%.",
        C['amber'], C['amber_light'])
    
    return html.Div([ins, grid([chart_card(f1), chart_card(f2),
                                chart_card(f3), chart_card(f4),
                                chart_card(f5), chart_card(f6)])])


def create_trade_charts(df, year_range):
    """Create Trade & Remittance dashboard charts"""
    fd = year_filter(df, year_range)
    y_start = int(fd['Year'].iloc[0])
    y_end = int(fd['Year'].iloc[-1])

    f1 = apply_theme(px.line(fd, x='Year', y=['Export_Billion_USD','Import_Billion_USD'],
                              title='Exports vs Imports (Billion USD)', markers=True,
                              color_discrete_sequence=[C['green'], C['red']]))
    
    fd2 = fd.copy()
    fd2['Trade_Balance'] = fd2['Export_Billion_USD'] - fd2['Import_Billion_USD']
    f2 = apply_theme(px.bar(fd2, x='Year', y='Trade_Balance',
                             title='Trade Balance (Exports − Imports)',
                             color='Trade_Balance',
                             color_continuous_scale=[[0,C['red']],[0.5,C['amber']],[1,C['green']]]))
    
    f3 = apply_theme(px.area(fd, x='Year', y='Remittance_Billion_USD',
                              title='Remittance Inflow (Billion USD)',
                              color_discrete_sequence=[C['purple']]))
    
    f4 = apply_theme(px.area(fd, x='Year', y='RMG_Export_Billion_USD',
                              title='Ready-Made Garments (RMG) Export (Billion USD)',
                              color_discrete_sequence=[C['teal']]))
    
    f5 = apply_theme(px.bar(fd, x='Year',
                             y=['Export_Billion_USD','Import_Billion_USD','Remittance_Billion_USD'],
                             title='Export vs Import vs Remittance Comparison',
                             barmode='group',
                             color_discrete_sequence=[C['green'], C['red'], C['purple']]))
    
    fd3 = fd.copy()
    fd3['RMG_Share'] = (fd3['RMG_Export_Billion_USD'] / fd3['Export_Billion_USD'] * 100).round(1)
    f6 = apply_theme(px.line(fd3, x='Year', y='RMG_Share',
                              title='RMG Share of Total Exports (%)', markers=True,
                              color_discrete_sequence=[C['teal']]))
    f6.add_hline(y=80, line_dash='dash', line_color=C['muted'],
                 annotation_text='80% mark', annotation_font_color=C['muted'])
    
    remit_growth = fd['Remittance_Billion_USD'].iloc[-1] / fd['Remittance_Billion_USD'].iloc[0]
    ins = insight_banner(
        f"RMG exports reached ${fd['RMG_Export_Billion_USD'].iloc[-1]}B in {y_end}, "
        f"making up over 80% of total exports. Remittances grew "
        f"{remit_growth:.0f}x from {y_start} to {y_end}.",
        C['teal'], '#ccfbf1')
    
    return html.Div([ins, grid([chart_card(f1), chart_card(f2),
                                chart_card(f3), chart_card(f4),
                                chart_card(f5), chart_card(f6)])])


def create_dev_charts(df, year_range):
    """Create Development Indicators dashboard charts"""
    fd = year_filter(df, year_range)
    y_start = int(fd['Year'].iloc[0])
    y_end = int(fd['Year'].iloc[-1])

    f1 = apply_theme(px.line(fd, x='Year', y='Electricity_Coverage',
                              title='Electricity Coverage (%)', markers=True,
                              color_discrete_sequence=[C['amber']]))
    f1.add_hline(y=100, line_dash='dash', line_color=C['green'],
                 annotation_text='100% achieved 2022')
    
    f2 = apply_theme(px.area(fd, x='Year', y='Internet_Users_Million',
                              title='Internet Users (Millions)',
                              color_discrete_sequence=[C['blue']]))
    
    f3 = apply_theme(px.line(fd, x='Year', y='Foreign_Reserve_Billion_USD',
                              title='Foreign Exchange Reserves (Billion USD)', markers=True,
                              color_discrete_sequence=[C['green']]))
    
    f4 = apply_theme(px.bar(fd, x='Year', y='CO2_Emissions_MT',
                             title='CO₂ Emissions (Million Tonnes)',
                             color='CO2_Emissions_MT',
                             color_continuous_scale=[[0, C['green_light']], [1, C['red']]]))
    
    f5 = apply_theme(px.line(fd, x='Year', y='Rice_Production_MT',
                              title='Rice Production (Million Tonnes)', markers=True,
                              color_discrete_sequence=[C['amber']]))
    
    f6 = apply_theme(px.line(fd, x='Year', y=['Electricity_Coverage','Internet_Users_Million'],
                              title='Electricity Coverage vs Internet Users', markers=True,
                              color_discrete_sequence=[C['amber'], C['blue']]))
    
    ins = insight_banner(
        f"Bangladesh achieved 100% electricity coverage in 2022 and grew internet "
        f"users from {fd['Internet_Users_Million'].iloc[0]}M in {y_start} to "
        f"{fd['Internet_Users_Million'].iloc[-1]}M in {y_end}.",
        C['blue'], C['blue_light'])
    
    return html.Div([ins, grid([chart_card(f1), chart_card(f2),
                                chart_card(f3), chart_card(f4),
                                chart_card(f5), chart_card(f6)])])

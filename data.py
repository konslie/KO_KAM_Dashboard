import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import plotly

TIER_ORDER = ['Tier 1', 'Tier 2', 'Tier 3', '핵심', 'W.seg', '일반']

def load_data(filepath="synthetic_b2b_dashboard_20k.csv"):
    df = pd.read_csv(filepath)
    
    # Raw tier names from the CSV: 'Tier 1', 'Tier 2', 'Tier 3', '핵심', 'W.seg', '일반'
    
    # 1. TIER 그룹핑 (KA vs GA)
    ka_tiers = ['Tier 1', 'Tier 2', 'Tier 3']
    ga_tiers = ['W.seg', '핵심', '일반']
    
    def classify_account(tier):
        if tier in ka_tiers:
            return 'KA'
        elif tier in ga_tiers:
            return 'GA'
        else:
            return 'Other'
            
    df['ACCOUNT_TYPE'] = df['TIER'].apply(classify_account)
    
    # Cast SLIN_TOTAL to float to prevent Plotly JSON i4 binary encoding overflow
    df['SLIN_TOTAL'] = df['SLIN_TOTAL'].astype(float)
    
    return df

def get_filter_options(df):
    months = sorted(df['YYYYMM'].dropna().unique().tolist(), reverse=True)
    divisions = sorted(df['RVRT_DIV_NM'].dropna().unique().tolist())
    account_types = ['KA', 'GA']
    tiers = TIER_ORDER
    teams = sorted(df['RVRT_TEAM_NM'].dropna().unique().tolist())
    return months, divisions, account_types, tiers, teams

def filter_data(df, selected_month=None, selected_div=None, selected_account=None, selected_tier=None, selected_team=None):
    if selected_month:
        df = df[df['YYYYMM'] == int(selected_month)]
    if selected_div and selected_div != 'All':
        df = df[df['RVRT_DIV_NM'] == selected_div]
    if selected_account and selected_account != 'All':
        df = df[df['ACCOUNT_TYPE'] == selected_account]
    if selected_tier and selected_tier != 'All':
        df = df[df['TIER'] == selected_tier]
    if selected_team and selected_team != 'All':
        df = df[df['RVRT_TEAM_NM'] == selected_team]
    return df
# Helper to format sales in 억
def fmt_eok(val):
    eok = val / 100_000_000
    if eok >= 1:
        return f"{eok:,.1f}억"
    else:
        return f"{val:,.0f}"

# Helper to standardise layout
def get_base_layout(title=""):
    return dict(
        title=dict(text=title, font=dict(color='#111827', family='Pretendard', size=16)),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#6b7280', family='Pretendard'),
        margin=dict(t=40, b=20, l=20, r=20),
    )

def get_hero_kpi(df):
    total_sales = df['SLIN_TOTAL'].sum()
    ka_sales = df[df['ACCOUNT_TYPE'] == 'KA']['SLIN_TOTAL'].sum()
    ga_sales = df[df['ACCOUNT_TYPE'] == 'GA']['SLIN_TOTAL'].sum()
    
    return {
        'total_sales': fmt_eok(total_sales),
        'ka_sales': fmt_eok(ka_sales),
        'ga_sales': fmt_eok(ga_sales)
    }

def get_ka_ga_ratio_chart(df):
    summary = df.groupby('ACCOUNT_TYPE')['SLIN_TOTAL'].sum().reset_index()
    if summary.empty:
        return "{}"
    summary['SLIN_EOK'] = summary['SLIN_TOTAL'] / 1e8
    summary['TEXT'] = summary['SLIN_EOK'].apply(lambda x: f"{x:,.1f} 억")
    fig = px.pie(summary, values='SLIN_TOTAL', names='ACCOUNT_TYPE', hole=0.7,
                 color='ACCOUNT_TYPE', color_discrete_map={'KA': '#ec4899', 'GA': '#475569'},
                 category_orders={'ACCOUNT_TYPE': ['KA', 'GA']})
    layout = get_base_layout()
    layout['showlegend'] = False
    fig.update_layout(**layout)
    fig.update_traces(textposition='inside', textinfo='percent+label+text', text=summary['TEXT'].tolist(), insidetextorientation='horizontal')
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def get_tier_distribution_chart(df):
    summary = df.groupby(['ACCOUNT_TYPE', 'TIER'])['SLIN_TOTAL'].sum().reset_index()
    if summary.empty:
        return "{}"
    
    summary['TIER'] = pd.Categorical(summary['TIER'], categories=TIER_ORDER, ordered=True)
    summary = summary.sort_values(['ACCOUNT_TYPE', 'TIER'], ascending=[False, True]) # KA before GA
    summary['SLIN_EOK'] = summary['SLIN_TOTAL'] / 1e8

    fig = go.Figure()
    for acct, color in [('KA', '#ec4899'), ('GA', '#475569')]:
        sub = summary[summary['ACCOUNT_TYPE'] == acct]
        if not sub.empty:
            fig.add_trace(go.Bar(
                x=[sub['ACCOUNT_TYPE'].tolist(), sub['TIER'].tolist()],
                y=sub['SLIN_EOK'].tolist(),
                name=acct,
                marker_color=color,
                text=[f"{v:,.1f} 억" for v in sub['SLIN_EOK'].tolist()],
                textposition='auto',
                textangle=0
            ))

    layout = get_base_layout()
    layout['xaxis_title'] = ''
    layout['yaxis_title'] = '매출 (억)'
    layout['showlegend'] = False
    fig.update_layout(**layout)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def get_tier_customer_count_chart(df):
    summary = df.groupby(['ACCOUNT_TYPE', 'TIER'])['EPM_CUST_ID'].nunique().reset_index()
    if summary.empty:
        return "{}"
    
    summary['TIER'] = pd.Categorical(summary['TIER'], categories=TIER_ORDER, ordered=True)
    summary = summary.sort_values(['ACCOUNT_TYPE', 'TIER'], ascending=[False, True]) # KA before GA

    fig = go.Figure()
    for acct, color in [('KA', '#ec4899'), ('GA', '#475569')]:
        sub = summary[summary['ACCOUNT_TYPE'] == acct]
        if not sub.empty:
            fig.add_trace(go.Bar(
                x=[sub['ACCOUNT_TYPE'].tolist(), sub['TIER'].tolist()],
                y=sub['EPM_CUST_ID'].tolist(),
                name=acct,
                marker_color=color,
                text=[f"{v:,.0f}" for v in sub['EPM_CUST_ID'].tolist()],
                textposition='auto',
                textangle=0
            ))

    layout = get_base_layout()
    layout['xaxis_title'] = ''
    layout['yaxis_title'] = '고객 수 (명)'
    layout['showlegend'] = False
    fig.update_layout(**layout)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def get_org_kaga_ratio_chart(df, org_col='RVRT_DIV_NM'):
    summary = df.groupby([org_col, 'ACCOUNT_TYPE'])['SLIN_TOTAL'].sum().reset_index()
    if summary.empty:
        return "{}"
    summary['SLIN_EOK'] = summary['SLIN_TOTAL'] / 1e8
    summary['TEXT'] = summary['SLIN_EOK'].apply(lambda x: f"{x:,.1f} 억" if x > 0 else "")
    fig = px.bar(summary, x=org_col, y='SLIN_EOK', color='ACCOUNT_TYPE', barmode='stack',
                 color_discrete_map={'KA': '#ec4899', 'GA': '#475569'},
                 category_orders={'ACCOUNT_TYPE': ['KA', 'GA']},
                 text='TEXT')
    fig.update_traces(textposition='auto', textangle=0)
    layout = get_base_layout()
    if org_col == 'RVRT_DIV_NM':
        axis_label = '담당'
    elif org_col == 'RVRT_TEAM_NM':
        axis_label = '팀'
    else:
        axis_label = '사원'
    layout['xaxis_title'] = axis_label
    layout['yaxis_title'] = '매출 (억)'
    layout['legend_title'] = ''
    fig.update_layout(**layout)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def get_org_tier_cross_chart(df, org_col='RVRT_DIV_NM'):
    summary = df.groupby([org_col, 'TIER'])['SLIN_TOTAL'].sum().reset_index()
    if summary.empty:
        return "{}"
    summary['SLIN_EOK'] = summary['SLIN_TOTAL'] / 1e8
    summary['TEXT'] = summary['SLIN_EOK'].apply(lambda x: f"{x:,.1f} 억" if x > 0 else "")
    fig = px.bar(summary, x=org_col, y='SLIN_EOK', color='TIER', barmode='group',
                 color_discrete_map={
                     'Tier 1': '#be185d', 'Tier 2': '#ec4899', 'Tier 3': '#fbcfe8',
                     '핵심': '#475569', 'W.seg': '#94a3b8', '일반': '#e2e8f0'
                 },
                 category_orders={'TIER': TIER_ORDER},
                 text='TEXT')
    fig.update_traces(textposition='auto', textangle=0)
    layout = get_base_layout()
    if org_col == 'RVRT_DIV_NM':
        axis_label = '담당'
    elif org_col == 'RVRT_TEAM_NM':
        axis_label = '팀'
    else:
        axis_label = '사원'
    layout['xaxis_title'] = axis_label
    layout['yaxis_title'] = '매출 (억)'
    layout['legend_title'] = 'Tier'
    fig.update_layout(**layout)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def get_tier_org_cross_chart(df, org_col='RVRT_DIV_NM'):
    """Tier별 담당별 매출 크로스 분석 (x축=Tier, 색상=담당)"""
    summary = df.groupby(['ACCOUNT_TYPE', 'TIER', org_col])['SLIN_TOTAL'].sum().reset_index()
    if summary.empty:
        return "{}"

    summary['TIER'] = pd.Categorical(summary['TIER'], categories=TIER_ORDER, ordered=True)
    summary = summary.sort_values('TIER')

    # 담당별 색상 파레트
    org_colors = ['#003d5c', '#31497e', '#674f95', '#a14e9a', '#d44c8d', '#f9596f', '#ff7a47', '#ffa600']
    orgs = sorted(summary[org_col].unique().tolist())
    color_map = {org: org_colors[i % len(org_colors)] for i, org in enumerate(orgs)}

    summary['SLIN_EOK'] = summary['SLIN_TOTAL'] / 1e8
    summary['TEXT'] = summary['SLIN_EOK'].apply(lambda x: f"{x:,.1f} 억" if x > 0 else "")

    fig = px.bar(summary, x='TIER', y='SLIN_EOK', color=org_col, barmode='group',
                 color_discrete_map=color_map,
                 category_orders={'TIER': TIER_ORDER},
                 text='TEXT')
    fig.update_traces(textposition='auto', textangle=0)
    layout = get_base_layout()
    if org_col == 'RVRT_DIV_NM':
        legend_label = '담당'
    elif org_col == 'RVRT_TEAM_NM':
        legend_label = '팀'
    else:
        legend_label = '사원'
    layout['xaxis_title'] = 'Tier'
    layout['yaxis_title'] = '매출 (억)'
    layout['legend_title'] = legend_label
    fig.update_layout(**layout)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def get_org_product_mix_chart(df, org_col='RVRT_DIV_NM'):
    summary = df.groupby([org_col, 'PFLS_NM'])['SLIN_TOTAL'].sum().reset_index()
    if summary.empty:
        return "{}"
    pivot_df = summary.pivot(index=org_col, columns='PFLS_NM', values='SLIN_TOTAL').fillna(0)
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_df.values.tolist(),
        x=pivot_df.columns.tolist(),
        y=pivot_df.index.tolist(),
        colorscale=[
            [0.0, '#5463a8'],
            [0.1, '#807bb8'],
            [0.2, '#a596c8'],
            [0.3, '#c7b3d8'],
            [0.4, '#e4d1eb'],
            [0.5, '#fff2ff'],
            [0.6, '#f8d4f0'],
            [0.7, '#f4b5dc'],
            [0.8, '#f195c4'],
            [0.9, '#ed72a7'],
            [1.0, '#e74b86']
        ],
        xgap=2,
        ygap=2,
        colorbar=dict(title='매출액(원)')
    ))
    layout = get_base_layout()
    layout['margin'] = dict(t=20, b=40, l=80, r=20)
    if org_col == 'RVRT_DIV_NM':
        axis_label = '담당'
    elif org_col == 'RVRT_TEAM_NM':
        axis_label = '팀'
    else:
        axis_label = '사원'
    layout['yaxis_title'] = axis_label
    layout['xaxis_title'] = '상품'
    fig.update_layout(**layout)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def get_tier_product_mix_chart(df):
    summary = df.groupby(['ACCOUNT_TYPE', 'TIER', 'PFLS_NM'])['SLIN_TOTAL'].sum().reset_index()
    if summary.empty:
        return "{}"
    
    # Calculate percentage for product mix (0-100) per tier
    # Grouping by ['ACCOUNT_TYPE', 'TIER'] is equivalent to grouping by 'TIER' because each TIER belongs to one ACCOUNT_TYPE
    tier_totals = summary.groupby(['ACCOUNT_TYPE', 'TIER'])['SLIN_TOTAL'].transform('sum')
    summary['PERCENTAGE'] = summary['SLIN_TOTAL'] / tier_totals * 100

    # Pivot to get multi-index
    pivot_df = summary.pivot(index=['ACCOUNT_TYPE', 'TIER'], columns='PFLS_NM', values='PERCENTAGE').fillna(0)
    
    # Reindex to enforce the desired order
    ordered_index = pd.MultiIndex.from_tuples(
        [('KA', 'Tier 1'), ('KA', 'Tier 2'), ('KA', 'Tier 3'), 
         ('GA', '핵심'), ('GA', 'W.seg'), ('GA', '일반')],
        names=['ACCOUNT_TYPE', 'TIER']
    )
    # Only keep indices that exist in the data to avoid NaNs
    valid_ordered_index = [idx for idx in ordered_index if idx in pivot_df.index]
    if valid_ordered_index:
        pivot_df = pivot_df.reindex(valid_ordered_index)
    
    # Explicitly convert to lists so plotly handles strings correctly
    z_values = pivot_df.values.tolist()
    x_values = pivot_df.columns.tolist()
    y_values = [pivot_df.index.get_level_values(0).tolist(), pivot_df.index.get_level_values(1).tolist()]

    fig = go.Figure(data=go.Heatmap(
        z=z_values,
        x=x_values,
        y=y_values,
        colorscale=[
            [0.0, '#5463a8'],
            [0.1, '#807bb8'],
            [0.2, '#a596c8'],
            [0.3, '#c7b3d8'],
            [0.4, '#e4d1eb'],
            [0.5, '#fff2ff'],
            [0.6, '#f8d4f0'],
            [0.7, '#f4b5dc'],
            [0.8, '#f195c4'],
            [0.9, '#ed72a7'],
            [1.0, '#e74b86']
        ],
        xgap=2,
        ygap=2,
        colorbar=dict(title='비중(%)'),
        hovertemplate='Account: %{y[0]}<br>Tier: %{y[1]}<br>Product: %{x}<br>Mix: %{z:.1f}%<extra></extra>'
    ))
    
    layout = get_base_layout()
    layout['margin'] = dict(t=20, b=40, l=100, r=20)
    layout['yaxis_title'] = 'Tier'
    layout['xaxis_title'] = '상품'
    
    # Ensure yaxis is created if not present
    if 'yaxis' not in layout:
        layout['yaxis'] = dict()
    layout['yaxis']['autorange'] = 'reversed'
    
    fig.update_layout(**layout)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def get_rep_efficiency_chart(df, org_col='RVRT_DIV_NM'):
    # We want to show individual reps. The color should be org_col to show division or team breakdown.
    # Group by both DIV, TEAM, and EMP to not lose detail, but color by org_col
    summary = df.groupby(['RVRT_DIV_NM', 'RVRT_TEAM_NM', 'RVRT_EMP_NM']).agg(
        total_sales=('SLIN_TOTAL', 'sum'),
        customer_count=('EPM_CUST_ID', 'nunique')
    ).reset_index()
    if summary.empty:
        return "{}"
    summary['total_sales_eok'] = summary['total_sales'] / 1e8
    fig = px.scatter(summary, x='customer_count', y='total_sales_eok', color=org_col, hover_data=['RVRT_TEAM_NM', 'RVRT_EMP_NM'],
                     color_discrete_sequence=['#003d5c', '#31497e', '#674f95', '#a14e9a', '#d44c8d', '#f9596f', '#ff7a47', '#ffa600'])
    fig.update_traces(marker=dict(size=10))
    layout = get_base_layout()
    layout['xaxis_title'] = '담당 고객 수'
    layout['yaxis_title'] = '발생 매출액 (억)'
    if org_col == 'RVRT_DIV_NM':
        legend_label = '담당'
    elif org_col == 'RVRT_TEAM_NM':
        legend_label = '팀'
    else:
        legend_label = '사원'
    layout['legend_title'] = legend_label
    layout['xaxis'] = dict(title='담당 고객 수', showgrid=True, gridcolor='#e5e7eb', gridwidth=1)
    layout['yaxis'] = dict(title='발생 매출액 (억)', showgrid=True, gridcolor='#e5e7eb', gridwidth=1)
    fig.update_layout(**layout)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def get_tier_radar_chart(df):
    """Tier별 상품군 강점 프로파일 레이더 차트"""
    # KA/GA 각각 Tier별로 상품 매출 비중(%) 계산
    summary = df.groupby(['ACCOUNT_TYPE', 'TIER', 'PFLS_NM'])['SLIN_TOTAL'].sum().reset_index()
    if summary.empty:
        return "{}"

    # Tier 내 총매출 대비 상품별 비중
    tier_totals = summary.groupby(['ACCOUNT_TYPE', 'TIER'])['SLIN_TOTAL'].transform('sum')
    summary['PCT'] = summary['SLIN_TOTAL'] / tier_totals * 100

    # 색상 매핑 (KA: 핑크 계열, GA: 그레이 계열)
    color_map = {
        'Tier 1': dict(line='#be185d', fill='rgba(190,24,93,0.15)'),
        'Tier 2': dict(line='#ec4899', fill='rgba(236,72,153,0.15)'),
        'Tier 3': dict(line='#fbcfe8', fill='rgba(251,207,232,0.15)'),
        '핵심':   dict(line='#475569', fill='rgba(71,85,105,0.15)'),
        'W.seg':  dict(line='#94a3b8', fill='rgba(148,163,184,0.15)'),
        '일반':   dict(line='#cbd5e1', fill='rgba(203,213,225,0.15)'),
    }

    products = sorted(summary['PFLS_NM'].unique().tolist())

    fig = go.Figure()

    for tier in TIER_ORDER:
        sub = summary[summary['TIER'] == tier]
        if sub.empty:
            continue
        # 상품별 비중을 products 순서에 맞춰 정렬
        pct_map = dict(zip(sub['PFLS_NM'], sub['PCT']))
        values = [pct_map.get(p, 0) for p in products]
        # 레이더 차트는 닫힌 형태로 보여주기 위해 첫 값을 끝에 추가
        values_closed = values + [values[0]]
        products_closed = products + [products[0]]

        colors = color_map.get(tier, dict(line='#6b7280', fill='rgba(107,114,128,0.15)'))
        acct = 'KA' if tier in ['Tier 1', 'Tier 2', 'Tier 3'] else 'GA'

        fig.add_trace(go.Scatterpolar(
            r=values_closed,
            theta=products_closed,
            name=f'{acct} - {tier}',
            line=dict(color=colors['line'], width=2),
            fill='toself',
            fillcolor=colors['fill'],
            marker=dict(size=5, color=colors['line']),
        ))

    layout = get_base_layout()
    layout['polar'] = dict(
        radialaxis=dict(visible=True, showline=False, gridcolor='#e5e7eb', tickfont=dict(size=10, color='#6b7280')),
        angularaxis=dict(gridcolor='#e5e7eb', tickfont=dict(size=11, color='#111827', family='Pretendard')),
        bgcolor='rgba(0,0,0,0)',
    )
    layout['legend'] = dict(orientation='h', yanchor='bottom', y=-0.15, xanchor='center', x=0.5)
    layout['margin'] = dict(t=30, b=60, l=60, r=60)
    fig.update_layout(**layout)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def get_customer_product_count_chart(df, org_col='RVRT_DIV_NM'):
    """Tier별/담당별 고객당 평균 사용 상품수"""
    # 고객별 상품수 계산
    cust_products = df.groupby(['ACCOUNT_TYPE', 'TIER', org_col, 'EPM_CUST_ID'])['PFLS_NM'].nunique().reset_index()
    cust_products.columns = ['ACCOUNT_TYPE', 'TIER', org_col, 'EPM_CUST_ID', 'PRODUCT_COUNT']

    # Tier별 평균
    tier_avg = cust_products.groupby(['ACCOUNT_TYPE', 'TIER'])['PRODUCT_COUNT'].mean().reset_index()
    tier_avg.columns = ['ACCOUNT_TYPE', 'TIER', 'AVG_PRODUCTS']

    if tier_avg.empty:
        return "{}", "{}"

    # Tier 순서 적용
    tier_avg['TIER'] = pd.Categorical(tier_avg['TIER'], categories=TIER_ORDER, ordered=True)
    tier_avg = tier_avg.sort_values('TIER')

    color_map = {
        'Tier 1': '#be185d', 'Tier 2': '#ec4899', 'Tier 3': '#fbcfe8',
        '핵심': '#475569', 'W.seg': '#94a3b8', '일반': '#e2e8f0'
    }

    fig_tier = go.Figure()
    for _, row in tier_avg.iterrows():
        fig_tier.add_trace(go.Bar(
            x=[row['TIER']],
            y=[round(row['AVG_PRODUCTS'], 1)],
            name=row['TIER'],
            marker_color=color_map.get(row['TIER'], '#6b7280'),
            text=[f"{row['AVG_PRODUCTS']:.1f}"],
            textposition='outside',
            showlegend=False,
        ))
    layout_tier = get_base_layout()
    layout_tier['yaxis_title'] = '평균 상품수'
    layout_tier['xaxis_title'] = 'Tier'
    fig_tier.update_layout(**layout_tier)

    # 담당별 평균
    org_avg = cust_products.groupby([org_col])['PRODUCT_COUNT'].mean().reset_index()
    org_avg.columns = [org_col, 'AVG_PRODUCTS']
    org_avg = org_avg.sort_values('AVG_PRODUCTS', ascending=False)

    fig_org = go.Figure()
    fig_org.add_trace(go.Bar(
        x=org_avg[org_col].tolist(),
        y=[round(v, 1) for v in org_avg['AVG_PRODUCTS'].tolist()],
        marker_color='#ec4899',
        text=[f"{v:.1f}" for v in org_avg['AVG_PRODUCTS'].tolist()],
        textposition='outside',
        showlegend=False,
    ))
    if org_col == 'RVRT_DIV_NM':
        axis_label = '담당'
    elif org_col == 'RVRT_TEAM_NM':
        axis_label = '팀'
    else:
        axis_label = '사원'
    layout_org = get_base_layout()
    layout_org['yaxis_title'] = '평균 상품수'
    layout_org['xaxis_title'] = axis_label
    fig_org.update_layout(**layout_org)

    return (
        json.dumps(fig_tier, cls=plotly.utils.PlotlyJSONEncoder),
        json.dumps(fig_org, cls=plotly.utils.PlotlyJSONEncoder)
    )

def get_arpu_chart(df, org_col='RVRT_DIV_NM'):
    """Tier별/담당별 ARPU (고객당 평균 매출)"""
    # 고객별 매출 합산
    cust_rev = df.groupby(['ACCOUNT_TYPE', 'TIER', org_col, 'EPM_CUST_ID'])['SLIN_TOTAL'].sum().reset_index()

    # Tier별 ARPU
    tier_arpu = cust_rev.groupby(['ACCOUNT_TYPE', 'TIER'])['SLIN_TOTAL'].mean().reset_index()
    tier_arpu.columns = ['ACCOUNT_TYPE', 'TIER', 'ARPU']

    if tier_arpu.empty:
        return "{}", "{}"

    tier_arpu['TIER'] = pd.Categorical(tier_arpu['TIER'], categories=TIER_ORDER, ordered=True)
    tier_arpu = tier_arpu.sort_values('TIER')

    color_map = {
        'Tier 1': '#be185d', 'Tier 2': '#ec4899', 'Tier 3': '#fbcfe8',
        '핵심': '#475569', 'W.seg': '#94a3b8', '일반': '#e2e8f0'
    }

    fig_tier = go.Figure()
    for _, row in tier_arpu.iterrows():
        arpu_eok = row['ARPU'] / 1e8
        fig_tier.add_trace(go.Bar(
            x=[row['TIER']],
            y=[arpu_eok],
            name=row['TIER'],
            marker_color=color_map.get(row['TIER'], '#6b7280'),
            text=[f"{arpu_eok:.1f}억"],
            textposition='outside',
            showlegend=False,
        ))
    layout_tier = get_base_layout()
    layout_tier['yaxis_title'] = 'ARPU (억)'
    layout_tier['xaxis_title'] = 'Tier'
    fig_tier.update_layout(**layout_tier)

    # 담당별 ARPU
    org_arpu = cust_rev.groupby([org_col])['SLIN_TOTAL'].mean().reset_index()
    org_arpu.columns = [org_col, 'ARPU']
    org_arpu = org_arpu.sort_values('ARPU', ascending=False)

    fig_org = go.Figure()
    org_arpu_eok = [v / 1e8 for v in org_arpu['ARPU'].tolist()]
    fig_org.add_trace(go.Bar(
        x=org_arpu[org_col].tolist(),
        y=org_arpu_eok,
        marker_color='#1e293b',
        text=[f"{v:.1f}억" for v in org_arpu_eok],
        textposition='outside',
        showlegend=False,
    ))
    if org_col == 'RVRT_DIV_NM':
        axis_label = '담당'
    elif org_col == 'RVRT_TEAM_NM':
        axis_label = '팀'
    else:
        axis_label = '사원'
    layout_org = get_base_layout()
    layout_org['yaxis_title'] = 'ARPU (억)'
    layout_org['xaxis_title'] = axis_label
    fig_org.update_layout(**layout_org)

    return (
        json.dumps(fig_tier, cls=plotly.utils.PlotlyJSONEncoder),
        json.dumps(fig_org, cls=plotly.utils.PlotlyJSONEncoder)
    )

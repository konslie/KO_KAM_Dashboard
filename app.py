from flask import Flask, render_template, request
import data

app = Flask(__name__)

# Load full dataset once when the app starts
df_all = data.load_data()
months, divisions, account_types, tiers, teams = data.get_filter_options(df_all)

@app.route('/')
def index():
    # Get filter parameters from request args
    selected_month = request.args.get('month')
    selected_div = request.args.get('division', 'All')
    selected_account = request.args.get('account_type', 'All')
    selected_tier = request.args.get('tier', 'All')
    selected_team = request.args.get('team', 'All')
    
    # Defaults to the latest month if no month selected
    if not selected_month and months:
        selected_month = str(months[0])
        
    # Filter data
    df_filtered = data.filter_data(
        df_all, 
        selected_month=selected_month, 
        selected_div=selected_div,
        selected_account=selected_account,
        selected_tier=selected_tier,
        selected_team=selected_team
    )
    
    # Dynamic org dimension logic
    # Drill-down hierarchy: Division -> Team -> Employee
    if selected_team and selected_team != 'All':
        org_col = 'RVRT_EMP_NM'
        org_label = '사원'
    elif selected_div and selected_div != 'All':
        org_col = 'RVRT_TEAM_NM'
        org_label = '팀'
    else:
        org_col = 'RVRT_DIV_NM'
        org_label = '담당'
    
    # Calculate KPIs
    kpi = data.get_hero_kpi(df_filtered)
    
    # Generate Charts JSON
    ka_ga_ratio_json = data.get_ka_ga_ratio_chart(df_filtered)
    tier_dist_json = data.get_tier_distribution_chart(df_filtered)
    tier_cust_json = data.get_tier_customer_count_chart(df_filtered)
    div_kaga_ratio_json = data.get_org_kaga_ratio_chart(df_filtered, org_col)
    div_tier_cross_json = data.get_org_tier_cross_chart(df_filtered, org_col)
    tier_org_cross_json = data.get_tier_org_cross_chart(df_filtered, org_col)
    
    product_mix_json = data.get_org_product_mix_chart(df_filtered, org_col)
    tier_product_mix_json = data.get_tier_product_mix_chart(df_filtered)
    rep_efficiency_json = data.get_rep_efficiency_chart(df_filtered, org_col)
    tier_radar_json = data.get_tier_radar_chart(df_filtered)
    
    prod_count_tier_json, prod_count_org_json = data.get_customer_product_count_chart(df_filtered, org_col)
    arpu_tier_json, arpu_org_json = data.get_arpu_chart(df_filtered, org_col)
    
    return render_template('index.html', 
                           kpi=kpi,
                           months=months,
                           divisions=divisions,
                           account_types=account_types,
                           tiers=tiers,
                           teams=teams,
                           selected_month=selected_month,
                           selected_div=selected_div,
                           selected_account=selected_account,
                           selected_tier=selected_tier,
                           selected_team=selected_team,
                           org_label=org_label,
                           ka_ga_ratio_json=ka_ga_ratio_json,
                           tier_dist_json=tier_dist_json,
                           tier_cust_json=tier_cust_json,
                           div_kaga_ratio_json=div_kaga_ratio_json,
                           div_tier_cross_json=div_tier_cross_json,
                           tier_org_cross_json=tier_org_cross_json,
                           product_mix_json=product_mix_json,
                           tier_product_mix_json=tier_product_mix_json,
                           rep_efficiency_json=rep_efficiency_json,
                           tier_radar_json=tier_radar_json,
                           prod_count_tier_json=prod_count_tier_json,
                           prod_count_org_json=prod_count_org_json,
                           arpu_tier_json=arpu_tier_json,
                           arpu_org_json=arpu_org_json)

if __name__ == '__main__':
    app.run(debug=True, port=5001)

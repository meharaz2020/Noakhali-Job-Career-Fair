import dash
from dash import html, dcc, dash_table
import dash_daq as daq
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import create_engine

# =============================================
#    DATABASE & CONFIG
# =============================================
DB_URL = "postgresql://bumeharaz:WrQhUZZjf2WqsJHiSOFuAszRrSUVQqAA@dpg-d5mj5abe5dus73eiju70-a.oregon-postgres.render.com/dbname_ou61"
engine = create_engine(DB_URL)

FAIR_LOGO = 'https://bdjobs.com/jobfair/new_reg/images/bdjobs-chakri-mela-noakhali-jan-2026.svg'
FAIR_NAME = "BDJOBS CHAKRI MELA - NOAKHALI 2026"

def get_db_data():
    try:
        query = "SELECT * FROM dashboard_stats ORDER BY 1 DESC LIMIT 1"
        df = pd.read_sql(query, engine)
        if not df.empty:
            return df.iloc[0].to_dict()
    except Exception as e:
        print(f"Database Sync Error: {e}")
    
    return {
        "total_registered": 0, "visitors": 0, "applied_to_job": 0,
        "application": 0, "unique_applicant": 0, "total_companies": 0,
        "direct_payment": 0, "paid_by_applicants": 0, "pro_users_today": 0,
        "amount_pro_users": 0, "total_revenue": 0, "pro_seeker_total": 0
    }

app = dash.Dash(
    __name__, 
    title=FAIR_NAME,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)

app.index_string = f'''
<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>{{%title%}}</title>
        <link rel="icon" type="image/svg+xml" href="{FAIR_LOGO}">
        {{%css%}}
    </head>
    <body>
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
    </body>
</html>
'''
server = app.server 

# =============================================
#    LAYOUT
# =============================================
app.layout = html.Div(id='main-container', children=[
    dcc.Store(id='theme-store', storage_type='local'), 
    dcc.Store(id='timer-trigger', data=1),
    dcc.Interval(id='live-refresh', interval=100000, n_intervals=0),

    html.Div(id='quantum-loader', children=[
        html.Div([
            html.Img(src=FAIR_LOGO, className='loader-logo'),
            html.Div(className='scan-line'),
            html.P("Welcome To Noakhali Job & Career Fair...", className='loader-text')
        ], className='loader-content')
    ]),

    html.Header([
        html.Div([html.Img(src=FAIR_LOGO, className='header-logo')], className='h-left'),
        html.Div([html.H1("Noakhali Job & Career Fair", className='header-title')], className='h-center'),
        html.Div([daq.BooleanSwitch(id='theme-toggle', color="#00d2ff", on=False)], className='h-right')
    ], id='main-header', className='glass-header'),

    html.Main([
        html.Section([
            html.Div(id='kicker-container', children=[
                html.Span(id='live-dot-red', className='pulse-dot red'),
                html.Span(id='live-dot-green', className='pulse-dot green'),
                html.Span(id='status-kicker', className='kicker'),
            ], className='status-wrapper'),
            
            html.Div(id='timer-grid', children=[
                html.Div([html.H2(id='d-val'), html.P('Days')], className='time-mini-cube hover-glow'),
                html.Div([html.H2(id='h-val'), html.P('Hours')], className='time-mini-cube hover-glow'),
                html.Div([html.H2(id='m-val'), html.P('Mins')], className='time-mini-cube hover-glow'),
                html.Div([html.H2(id='s-val'), html.P('Secs')], className='time-mini-cube hover-glow'),
            ], className='timer-flex'),

            html.Div(id='live-dashboard') 
        ]),
    ]),
    html.Footer(html.P(f"© 2026 Meharaz Hossain - meharazbdjobs@gmail.com"), className='footer-mini')
])

# =============================================
#    THEME PERSISTENCE
# =============================================
@app.callback(
    Output('theme-toggle', 'on'),
    [Input('theme-store', 'modified_timestamp')],
    [State('theme-store', 'data')]
)
def load_theme(ts, data):
    if ts is None or data is None: return False 
    return data

@app.callback(
    [Output('main-container', 'className'), Output('theme-store', 'data')],
    [Input('theme-toggle', 'on')]
)
def save_theme(on):
    return ('dark-theme' if on else 'light-theme'), on

# =============================================
#    CORE DASHBOARD CALLBACK
# =============================================
@app.callback(
    Output('live-dashboard', 'children'),
    [Input('live-refresh', 'n_intervals'), Input('theme-toggle', 'on')]
)
def update_dashboard(n, dark_mode):
    raw_data = get_db_data()
    data = {k: int(float(v)) if v is not None else 0 for k, v in raw_data.items()}
    
    table_labels = {
        "total_registered": "TOTAL REGISTERED",
        "visitors": "VISITORS",
        "applied_to_job": "APPLIED TO JOB",
        "application": "TOTAL APPLICATIONS",
        "unique_applicant": "UNIQUE APPLICANTS",
        "total_companies": "TOTAL COMPANIES",
        "direct_payment": "DIRECT PAYMENT",
        "paid_by_applicants": "PAID BY APPLICANTS",
        "pro_users_today": "PRO USERS TODAY",
        "amount_pro_users": "AMOUNT PRO USERS",
        "pro_seeker_total": "PRO SEEKER TOTAL (APPLIED)",
        "total_revenue": "TOTAL REVENUE"
    }

    order = ["total_registered", "visitors", "applied_to_job", "application", "unique_applicant", "total_companies", 
             "direct_payment", "paid_by_applicants", "pro_users_today", "amount_pro_users", "pro_seeker_total", "total_revenue"]
    
    items = []
    for key in order:
        if key in data:
            label = table_labels.get(key, key.replace("_", " ").upper())
            val = f"৳{data[key]:,}" if key == "total_revenue" else f"{data[key]:,}"
            items.append({"M": label, "V": val})

    accent = "#00d2ff" if dark_mode else "#003366"
    text_color = "#f8fafc" if dark_mode else "#0f172a"
    grid_c = "rgba(0,210,255,0.1)" if dark_mode else "rgba(0,0,0,0.05)"
    d_style = {'backgroundColor': 'transparent', 'color': text_color}

    # FIX: Lock graph height and ensure responsive width
    def apply_style(fig):
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=text_color, family='Rajdhani'),
            margin=dict(l=20, r=20, t=10, b=20), 
            height=160, # Locked Height
            autosize=True, # Responsive Width
            showlegend=False
        )
        fig.update_yaxes(gridcolor=grid_c, zerolinecolor=grid_c)
        fig.update_xaxes(gridcolor=grid_c, zerolinecolor=grid_c)
        return fig

    df1 = pd.DataFrame(items[:6])
    df2 = pd.DataFrame(items[6:])

    # Graphs
    f1 = apply_style(go.Figure(go.Bar(x=['Reg', 'Vis', 'Apps'], y=[data['total_registered'], data['visitors'], data['applied_to_job']], marker_color=accent)))
    f2 = apply_style(go.Figure(go.Pie(labels=['Direct', 'Pro'], values=[data['direct_payment'], data['amount_pro_users']], hole=.6)))
    eng_val = (data['application'] / data['total_companies']) if data['total_companies'] > 0 else 0
    f3 = apply_style(go.Figure(go.Indicator(mode="gauge+number", value=int(eng_val), gauge={'bar':{'color':accent}, 'axis':{'range':[0,500]}})))
    f4 = apply_style(go.Figure(go.Bar(x=['Uni', 'Tot'], y=[data['unique_applicant'], data['application']], marker_color=accent)))
    f5 = apply_style(go.Figure(go.Pie(labels=['Dir', 'Fee'], values=[data['direct_payment'], data['paid_by_applicants']], hole=.6)))
    f6 = apply_style(go.Figure(go.Indicator(mode="number+delta", value=data['pro_users_today'], delta={'reference': 100})))
    f7 = apply_style(go.Figure(go.Scatter(x=['D-2', 'D-1', 'Live'], y=[0, 0, data['total_companies']], fill='tozeroy', line_color=accent)))
    f8 = apply_style(go.Figure(go.Indicator(mode="gauge+number", value=data['total_revenue'], gauge={'shape':"bullet", 'bar':{'color':accent}, 'axis':{'range':[0, 100000]}})))
    f9 = apply_style(go.Figure(go.Funnel(y=["Visitors", "Applicants"], x=[data['visitors'], data['unique_applicant']], marker_color=accent)))

    return [
        html.Div([
            html.Div([html.P("FAIR REACH"), html.H4(f"{data['total_registered']:,}")], className='mini-intel hover-glow'),
            html.Div([html.P("TOTAL APPS"), html.H4(f"{data['application']:,}")], className='mini-intel hover-glow'),
            html.Div([html.P("NET REVENUE"), html.H4(f"৳{data['total_revenue']:,}")], className='mini-intel hover-glow'),
        ], className='mini-stats-grid'),

        html.Div([
            html.Div([dash_table.DataTable(data=df1.to_dict('records'), columns=[{"name": i, "id": i} for i in df1.columns], style_header={'display': 'none'}, style_cell={'padding': '12px', 'fontSize': '12px', 'textAlign': 'left', 'fontFamily': 'Inter', 'border': 'none'}, style_data=d_style, style_as_list_view=True)], className='table-col no-hover-table'),
            html.Div([dash_table.DataTable(data=df2.to_dict('records'), columns=[{"name": i, "id": i} for i in df2.columns], style_header={'display': 'none'}, style_cell={'padding': '12px', 'fontSize': '12px', 'textAlign': 'left', 'fontFamily': 'Inter', 'border': 'none'}, style_data=d_style, style_as_list_view=True)], className='table-col no-hover-table'),
        ], className='dual-table-container'),

        html.Div([
            html.Div([html.H5("USER FLOW"), dcc.Graph(figure=f1, config={'responsive': True, 'displayModeBar': False})], className='graph-box-m hover-glow'),
            html.Div([html.H5("REVENUE SHARE"), dcc.Graph(figure=f2, config={'responsive': True, 'displayModeBar': False})], className='graph-box-m hover-glow'),
            html.Div([html.H5("ENGAGEMENT"), dcc.Graph(figure=f3, config={'responsive': True, 'displayModeBar': False})], className='graph-box-m hover-glow'),
            html.Div([html.H5("UNIQUE REACH"), dcc.Graph(figure=f4, config={'responsive': True, 'displayModeBar': False})], className='graph-box-m hover-glow'),
            html.Div([html.H5("FEE RATIO"), dcc.Graph(figure=f5, config={'responsive': True, 'displayModeBar': False})], className='graph-box-m hover-glow'),
            html.Div([html.H5("PRO GROWTH"), dcc.Graph(figure=f6, config={'responsive': True, 'displayModeBar': False})], className='graph-box-m hover-glow'),
            html.Div([html.H5("TRACTION"), dcc.Graph(figure=f7, config={'responsive': True, 'displayModeBar': False})], className='graph-box-m hover-glow'),
            html.Div([html.H5("GOAL TRACK"), dcc.Graph(figure=f8, config={'responsive': True, 'displayModeBar': False})], className='graph-box-m hover-glow'),
            html.Div([html.H5("CONVERSION"), dcc.Graph(figure=f9, config={'responsive': True, 'displayModeBar': False})], className='graph-box-m hover-glow'),
        ], className='nine-graph-matrix'),
    ]

# --- CLIENTSIDE SCRIPTS ---
app.clientside_callback(
    f"""
    function(trigger) {{
        const runUpdate = () => {{
            const start = new Date(2026, 0, 20, 10, 0, 0);
            const end = new Date(2026, 0, 20, 16, 0, 0);
            const now = new Date();
            let diff, statusText, showRed, showGreen;
            if (now < start) {{ diff = start - now; statusText = "WAITING FOR LAUNCH"; showRed = false; showGreen = true; }}
            else if (now >= start && now <= end) {{ diff = end - now; statusText = "LIVE FEED ACTIVE"; showRed = true; showGreen = false; }}
            else {{ diff = 0; statusText = "FAIR CONCLUDED"; showRed = false; showGreen = true; }}
            document.getElementById("d-val").innerText = Math.floor(diff/86400000).toString().padStart(2, '0');
            document.getElementById("h-val").innerText = Math.floor((diff%86400000)/3600000).toString().padStart(2, '0');
            document.getElementById("m-val").innerText = Math.floor((diff%3600000)/60000).toString().padStart(2, '0');
            document.getElementById("s-val").innerText = Math.floor((diff%60000)/1000).toString().padStart(2, '0');
            document.getElementById("status-kicker").innerText = statusText;
            document.getElementById("live-dot-red").style.display = showRed ? "inline-block" : "none";
            document.getElementById("live-dot-green").style.display = showGreen ? "inline-block" : "none";
        }};
        runUpdate(); setInterval(runUpdate, 1000);
        setTimeout(() => {{
            const ldr = document.getElementById('quantum-loader');
            if(ldr) {{ ldr.style.opacity = '0'; setTimeout(() => ldr.style.display = 'none', 500); }}
        }}, 1500);
        return window.dash_clientside.no_update;
    }}
    """,
    Output("main-container", "title"), Input("timer-trigger", "data")
)

app.clientside_callback(
    """
    function(n) {
        if (!document.getElementById('master-style')) {
            const style = document.createElement('style');
            style.id = 'master-style';
            style.textContent = `
                body { margin: 0; font-family: 'Inter', sans-serif; overflow-x: hidden; }
                #main-container { transition: background-color 0.4s ease, color 0.4s ease; min-height: 100vh; }
                .dark-theme { background: #020617 !important; color: #f8fafc !important; }
                .light-theme { background: #f8fafc !important; color: #0f172a !important; }
                #quantum-loader { position: fixed; inset: 0; background: #020617; z-index: 9999; display: flex; justify-content: center; align-items: center; transition: 0.6s; }
                .scan-line { width: 180px; height: 2px; background: #00d2ff; margin: 15px auto; animation: scan 2s infinite; box-shadow: 0 0 15px #00d2ff; }
                @keyframes scan { 0%, 100% { transform: scaleX(0.2); } 50% { transform: scaleX(1.4); } }
                .loader-text { font-family: 'Rajdhani'; color: #00d2ff; letter-spacing: 4px; font-size: 0.7rem; }
                .glass-header { display: flex; justify-content: space-between; align-items: center; padding: 0 5%; height: 55px; background: #003366; color: white; border-bottom: 2px solid #00d2ff; }
                .dark-theme .glass-header { background: rgba(15, 23, 42, 0.95); }
                .header-logo { height: 35px; }
                .header-title { font-family: 'Rajdhani'; color: #00d2ff; font-size: 1.2rem; margin: 0; }
                .dual-table-container { display: flex; gap: 20px; justify-content: center; padding: 0 5% 20px; }
                .table-col { flex: 1; background: rgba(0,210,255,0.02); border-radius: 12px; overflow: hidden; }
                .no-hover-table * { pointer-events: none !important; background-color: transparent !important; }
                .hover-glow { transition: 0.3s ease; border: 1px solid transparent; }
                .hover-glow:hover { transform: translateY(-4px); border-color: #00d2ff !important; box-shadow: 0 8px 15px rgba(0,210,255,0.1); }
                .mini-stats-grid { display: flex; justify-content: center; gap: 15px; margin-bottom: 25px; margin-top: 20px;}
                .mini-intel { padding: 15px; border-radius: 10px; border-left: 4px solid #00d2ff; background: rgba(0,210,255,0.03); min-width: 180px; }
                .mini-intel h4 { font-size: 1.5rem; color: #00d2ff; margin: 5px 0 0; font-family: 'Rajdhani'; }
                
                /* GRID FIX: Ensure items don't stretch vertically */
                .nine-graph-matrix { 
                    display: grid; 
                    grid-template-columns: repeat(3, 1fr); 
                    gap: 15px; 
                    padding: 0 5% 50px; 
                    align-items: start; 
                }
                .graph-box-m { 
                    background: rgba(0,210,255,0.03); 
                    border-radius: 12px; 
                    padding: 8px; 
                    border: 1px solid rgba(0,210,255,0.08); 
                    height: 200px; /* Locked box height */
                    overflow: hidden;
                }
                .graph-box-m h5 { font-family: 'Rajdhani'; color: #00d2ff; text-align: center; margin: 2px 0; font-size: 0.75rem; }
                
                .timer-flex { display: flex; justify-content: center; gap: 10px; margin: 20px 0; }
                .time-mini-cube { padding: 10px; background: rgba(0,210,255,0.06); border-radius: 8px; min-width: 70px; text-align: center; }
                .time-mini-cube h2 { color: #00d2ff; margin: 0; font-family: 'Rajdhani'; font-size: 2rem; }
                .status-wrapper { display: flex; align-items: center; justify-content: center; gap: 10px; margin-top: 25px; }
                .pulse-dot { width: 12px; height: 12px; border-radius: 50%; display: inline-block; }
                .red { background: #ff4d4d; animation: p 1.5s infinite; box-shadow: 0 0 10px #ff4d4d; }
                .green { background: #22c55e; animation: p 1.5s infinite; box-shadow: 0 0 10px #22c55e; }
                @keyframes p { 0% { transform: scale(1); opacity: 1; } 100% { transform: scale(2.2); opacity: 0; } }
                .kicker { font-family: 'Rajdhani'; letter-spacing: 2px; font-weight: 600; font-size: 1rem; }
                .footer-mini { text-align: center; padding: 30px; opacity: 0.4; font-size: 0.7rem; border-top: 1px solid rgba(0,210,255,0.05); }
            `;
            document.head.appendChild(style);
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('main-container', 'id'), Input('main-container', 'id')
)

if __name__ == '__main__':
    app.run(debug=True)




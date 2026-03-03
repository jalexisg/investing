import streamlit as st

def inject_premium_css():
    """Injects high-end financial dashboard styling and hides default elements."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
        
        :root {
            --bg-primary: #09090b;
            --bg-secondary: #0f172a;
            --bg-glass: rgba(30, 41, 59, 0.7);
            --border-color: #334155;
            --accent-blue: #38bdf8;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --uptrend: #22c55e;
            --downtrend: #ef4444;
        }

        .stApp {
            background-color: var(--bg-primary);
            color: var(--text-primary);
            font-family: 'Outfit', sans-serif;
        }

        /* Hide Streamlit Default UI elements */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display:none;}
        [data-testid="stHeader"] {background: rgba(0,0,0,0); border: none;}

        /* Card Styling with Glassmorphism */
        .metric-card {
            background: var(--bg-glass);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--border-color);
            padding: 1.5rem;
            border-radius: 16px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .metric-card:hover {
            transform: translateY(-4px);
            border-color: var(--accent-blue);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
        }

        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: var(--bg-primary);
        }
        ::-webkit-scrollbar-thumb {
            background: var(--border-color);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #475569;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #020617;
            border-right: 1px solid var(--border-color);
        }
        
        /* Ticker Tape Animation */
        .ticker-wrap {
            width: 100%;
            overflow: hidden;
            background: #020617;
            border-bottom: 2px solid #0ea5e9;
            padding: 10px 0;
            white-space: nowrap;
            position: sticky;
            top: 0;
            z-index: 999;
        }
        .ticker {
            display: inline-block;
            animation: ticker 40s linear infinite;
        }
        .ticker-item {
            display: inline-block;
            padding: 0 40px;
            font-size: 0.95rem;
            font-weight: 500;
        }
        .price-up { color: var(--uptrend); }
        .price-down { color: var(--downtrend); }

        @keyframes ticker {
            0% { transform: translateX(100%); }
            100% { transform: translateX(-100%); }
        }

        /* Tabs and Dataframes */
        button[data-baseweb="tab"] {
            background-color: transparent !important;
            border: none !important;
            color: var(--text-secondary) !important;
            font-weight: 600 !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: var(--accent-blue) !important;
            border-bottom: 2px solid var(--accent-blue) !important;
        }
    </style>
    """, unsafe_allow_html=True)

def render_custom_header():
    """Renders a professional top header to replace the hidden Streamlit bar."""
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0 20px 0; border-bottom: 1px solid var(--border-color); margin-bottom: 30px;">
        <div style="display: flex; align-items: center; gap: 15px;">
            <div style="background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%); width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 20px;">🛡️</div>
            <div>
                <h1 style="margin: 0; font-size: 24px; font-weight: 700; color: var(--text-primary);">Terminal de Inversión Pro</h1>
                <p style="margin: 0; font-size: 13px; color: var(--text-secondary);">Análisis de Mercado en Tiempo Real</p>
            </div>
        </div>
        <div style="display: flex; gap: 20px; align-items: center;">
            <span style="font-size: 13px; color: #10b981;">● MERCADOS ABIERTOS</span>
            <div style="padding: 6px 14px; background: #1e293b; border-radius: 8px; font-size: 12px; border: 1px solid var(--border-color);">CUENTA PREMIUM</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_ticker_tape(data):
    """Renders a scrolling ticker tape at the top."""
    items_html = ""
    for item in data:
        change_class = "price-up" if item['change'] >= 0 else "price-down"
        arrow = "▲" if item['change'] >= 0 else "▼"
        items_html += f'''<div class="ticker-item"><span style="color: var(--text-secondary);">{item['symbol']}</span><span>{item['price']}</span><span class="{change_class}">{arrow} {abs(item['change_pct'])}%</span></div>'''
    
    st.markdown(f'''<div class="ticker-wrap"><div class="ticker">{items_html}</div></div>''', unsafe_allow_html=True)

def render_metric_card(title, value, change=None, suffix=""):
    """Renders a premium metric card."""
    change_html = ""
    if change is not None:
        color = "var(--uptrend)" if change >= 0 else "var(--downtrend)"
        arrow = "▲" if change >= 0 else "▼"
        change_html = f'<div style="color: {color}; font-size: 0.85rem; margin-top: 4px;">{arrow} {abs(change)}%</div>'
    
    st.markdown(f'''
<div class="metric-card">
    <div style="color: var(--text-secondary); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;">{title}</div>
    <div style="font-size: 1.5rem; font-weight: 700;">{value}{suffix}</div>
    {change_html}
</div>
    ''', unsafe_allow_html=True)

def format_large_number(num):
    if num is None:
        return "-"
    if num >= 1e12:
        return f"{num/1e12:.1f} T"
    if num >= 1e9:
        return f"{num/1e9:.1f} B"
    if num >= 1e6:
        return f"{num/1e6:.1f} M"
    return f"{num:.2f}"

def render_dataframe(dataframe):
    # (Existing logic, but will be integrated with premium styles automatically via inject_premium_css)
    column_config = {
        "Ticker": st.column_config.TextColumn("Símbolo", width="small"),
        "Nombre": st.column_config.TextColumn("Nombre", width="medium"),
        "Precio Actual": st.column_config.NumberColumn("Precio", format="$%.2f"),
        "Valor Justo": st.column_config.NumberColumn("Valor Razonable", format="$%.2f", help="Promedio de: Analyst Target, Graham Formula (Growth), Historical PE"),
        "Potencial": st.column_config.ProgressColumn("Potencial", format="%.2f%%", min_value=-1, max_value=1),
        "Estado": st.column_config.TextColumn("Etiqueta", width="small"),
        "Market Cap": st.column_config.NumberColumn("Cap. Mercado", format="$%.2e"),
        "Div Yield": st.column_config.NumberColumn("Div Yield", format="%.2f%%"),
        "P/E": st.column_config.NumberColumn("PER", format="%.1fx"),
        "P/B": st.column_config.NumberColumn("P/Valor Libro", format="%.1fx"),
        "P/S (TTM)": st.column_config.NumberColumn("P/Ventas", format="%.1fx"),
        "EV": st.column_config.NumberColumn("Valor Empresa", format="$%.2e"),
        "Deuda/Eq": st.column_config.NumberColumn("Deuda/Cap", format="%.1f%%"),
        "Técnico": st.column_config.TextColumn("Análisis Técnico", width="medium"),
        "Modelos": st.column_config.TextColumn("Detalles Modelos", width="medium"),
    }

    def style_status(val):
        if val == 'Infravalorada' or 'Compra' in str(val):
            color = '#10b981' # Green
        elif val == 'Sobrevalorada' or 'Venta' in str(val):
            color = '#ef4444' # Red
        else: 
            color = '#f59e0b' # Amber
        return f'color: {color}; font-weight: bold;'

    styled_df = dataframe.style.map(style_status, subset=['Estado', 'Técnico'])

    st.dataframe(
        styled_df,
        column_config=column_config,
        use_container_width=True,
        hide_index=True,
        height=600
    )

def render_etf_dataframe(dataframe):
    st.dataframe(
        dataframe,
        column_config={
            "Ticker": st.column_config.TextColumn("Símbolo", width="small"),
            "Nombre": st.column_config.TextColumn("Nombre", width="large"),
            "Precio": st.column_config.NumberColumn("Precio", format="$%.2f"),
            "Potencial": st.column_config.ProgressColumn(
                "Potencial 52W",
                help="Potencial de recuperación hasta el máximo de 52 semanas",
                format="%.2f%%",
                min_value=-0.5,
                max_value=0.5,
            ),
            "Estado": st.column_config.TextColumn("Estado", width="medium"),
            "Yield": st.column_config.NumberColumn("Yield", format="%.2f%%", help="Yield de dividendos (si aplica)"),
            "Expense Ratio": st.column_config.NumberColumn("Exp. Ratio", format="%.4f", help="Ratio de gastos anual"),
            "Retorno YTD": st.column_config.NumberColumn("Retorno YTD", format="%.2f%%"),
            "Categoría": st.column_config.TextColumn("Categoría"),
            "Activos": st.column_config.NumberColumn("Activos", format="$%.2e"),
        },
        use_container_width=True,
        hide_index=True
    )

def render_crypto_dataframe(dataframe):
    def highlight_crypto_status(val):
        color = ''
        if 'Alcista' in str(val) or 'En Máximos' in str(val):
            color = 'background-color: #10b98120; color: #10b981'
        elif 'Bajista' in str(val):
             color = 'background-color: #ef444420; color: #ef4444'
        elif 'Oportunidad' in str(val):
             color = 'background-color: #3b82f620; color: #3b82f6'
        return color

    def highlight_trend(val):
        color = ''
        if 'Alcista' in str(val):
            color = 'color: #10b981; font-weight: bold'
        elif 'Bajista' in str(val):
            color = 'color: #ef4444; font-weight: bold'
        return color

    st.dataframe(
        dataframe.style.map(highlight_crypto_status, subset=['Estado']).map(highlight_trend, subset=['Tendencia']),
        column_config={
            "Ticker": st.column_config.TextColumn("Símbolo", width="small"),
            "Nombre": st.column_config.TextColumn("Nombre", width="medium"),
            "Precio": st.column_config.NumberColumn("Precio", format="$%.2f"),
            "Potencial": st.column_config.ProgressColumn(
                "Potencial 52W",
                help="Distancia al máximo de 52 semanas",
                format="%.2f%%",
                min_value=-0.5,
                max_value=1.5,
            ),
            "Estado": st.column_config.TextColumn("Estado (Oportunidad)"),
            "Tendencia": st.column_config.TextColumn("Tendencia (MA)"),
            "Market Cap": st.column_config.NumberColumn("Market Cap", format="$%.2e"),
            "Volumen 24h": st.column_config.NumberColumn("Volumen 24h", format="$%.2e"),
            "MA 50d": st.column_config.NumberColumn("MA 50d", format="$%.2f"),
            "MA 200d": st.column_config.NumberColumn("MA 200d", format="$%.2f"),
        },
        use_container_width=True,
        hide_index=True
    )

import streamlit as st

def inject_premium_css():
    """Injects high-end financial dashboard styling and hides default elements."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
        
        :root {
            --bg-primary: #020617;
            --bg-secondary: #0f172a;
            --bg-glass: rgba(15, 23, 42, 0.6);
            --bg-glass-hover: rgba(30, 41, 59, 0.8);
            --border-color: rgba(51, 65, 85, 0.5);
            --accent-blue: #38bdf8;
            --accent-glow: rgba(56, 189, 248, 0.15);
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

        /* Sidebar Styling - Premium Redesign */
        [data-testid="stSidebar"] {
            background-color: #020617;
            border-right: 1px solid var(--border-color);
            padding-top: 2rem;
        }

        [data-testid="stSidebar"] section {
            background-color: transparent !important;
        }

        /* Force Sidebar Text Visibility & Padding */
        [data-testid="stSidebarNav"] label p,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] section[data-testid="stSidebarNav"] p,
        [data-testid="stSidebar"] .stMarkdown p,
        [data-testid="stSidebar"] .stMarkdown span,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stCaption,
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
            color: #ffffff !important;
            font-size: 0.95rem !important;
            font-weight: 500 !important;
        }

        /* Sidebar Nav Item Spacing & Hover */
        [data-testid="stSidebarNav"] ul {
            padding-top: 1rem !important;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label {
            padding: 10px 16px !important;
            border-radius: 12px !important;
            margin-bottom: 6px !important;
            transition: all 0.2s ease !important;
            border: 1px solid transparent !important;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:hover {
            background-color: var(--bg-glass-hover) !important;
            border-color: var(--border-color) !important;
            transform: translateX(4px);
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] [data-testid="stMarkdownContainer"] p {
            font-weight: 600 !important;
            letter-spacing: 0.02em;
        }

        [data-testid="stSidebar"] hr {
            margin: 1.5rem 0 !important;
            border-top: 1px solid var(--border-color) !important;
            opacity: 0.3;
        }

        /* Card Styling with Enhanced Glassmorphism */
        .metric-card {
            background: var(--bg-glass);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--border-color);
            padding: 1.75rem;
            border-radius: 20px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        .metric-card::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--accent-blue), transparent);
            opacity: 0;
            transition: opacity 0.4s ease;
        }
        .metric-card:hover {
            transform: translateY(-6px);
            border-color: rgba(56, 189, 248, 0.4);
            box-shadow: 0 10px 40px -10px var(--accent-glow);
            background: var(--bg-glass-hover);
        }
        .metric-card:hover::before {
            opacity: 1;
        }

        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: var(--bg-primary);
        }
        ::-webkit-scrollbar-thumb {
            background: #334155;
            border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: var(--accent-blue);
        }

        /* Ticker Tape Animation - Refined */
        .ticker-wrap {
            width: 100%;
            overflow: hidden;
            background: #020617;
            border-bottom: 1px solid var(--border-color);
            padding: 0;
            white-space: nowrap;
            position: sticky;
            top: 0;
            z-index: 999;
            height: 32px;
            display: flex;
            align-items: center;
        }
        .ticker {
            display: inline-block;
            animation: ticker 60s linear infinite;
        }
        .ticker-item {
            display: inline-block;
            padding: 0 30px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            font-weight: 500;
            letter-spacing: -0.01em;
        }
        .price-up { color: var(--uptrend) !important; }
        .price-down { color: var(--downtrend) !important; }

        @keyframes ticker {
            0% { transform: translateX(100%); }
            100% { transform: translateX(-100%); }
        }

        /* Tabs Refinement */
        button[data-baseweb="tab"] {
            background-color: transparent !important;
            border: none !important;
            color: var(--text-secondary) !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            padding-bottom: 8px !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: var(--accent-blue) !important;
            border-bottom: 2px solid var(--accent-blue) !important;
        }

        /* Layout Gap Reduction - Aggressive */
        [data-testid="stVerticalBlock"] {
            gap: 0.25rem !important;
        }
        .stMain {
            padding-top: 0.5rem !important;
        }
        [data-testid="stHeader"] {
            display: none;
        }
        div.block-container {
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
        }

        /* Fix Button Contrast (White text on dark background) */
        button[kind="secondary"], button[kind="primary"] {
            background-color: #1e293b !important;
            color: #ffffff !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
            transition: all 0.2s ease !important;
        }
        button[kind="secondary"]:hover, button[kind="primary"]:hover {
            background-color: var(--accent-blue) !important;
            border-color: var(--accent-blue) !important;
            color: #000000 !important;
        }

        /* Sidebar Spacing Refinement */
        [data-testid="stSidebarNav"] ul {
            padding-top: 0.5rem !important;
        }
        [data-testid="stSidebar"] hr {
            margin: 1rem 0 !important;
        }

    </style>
    """, unsafe_allow_html=True)

def render_custom_header():
    """Renders a professional top header with premium aesthetic."""
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 0 16px 0; border-bottom: 1px solid var(--border-color); margin-bottom: 20px; position: relative;">
        <div style="display: flex; align-items: center; gap: 16px;">
            <div style="background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%); width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; box-shadow: 0 8px 16px -4px rgba(14, 165, 233, 0.5); font-size: 20px;">🛡️</div>
            <div>
                <h1 style="margin: 0; font-size: 22px; font-weight: 800; color: var(--text-primary); letter-spacing: -0.02em; line-height: 1.1;">INVESTING PRO <span style="color: var(--accent-blue); font-weight: 400; font-size: 14px; margin-left: 4px; vertical-align: middle;">TERMINAL</span></h1>
                <p style="margin: 0; font-size: 12px; color: var(--text-secondary); font-weight: 500; letter-spacing: 0.05em; text-transform: uppercase;">Intelligence & Asset Tracking</p>
            </div>
        </div>
        <div style="display: flex; gap: 24px; align-items: center;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="display: inline-block; width: 8px; height: 8px; background: #10b981; border-radius: 50%; box-shadow: 0 0 12px #10b981;"></span>
                <span style="font-size: 12px; color: #10b981; font-weight: 700; letter-spacing: 0.05em;">LIVE MARKETS</span>
            </div>
            <div style="padding: 8px 16px; background: linear-gradient(180deg, rgba(30, 41, 59, 0.4) 0%, rgba(15, 23, 42, 0.4) 100%); border-radius: 10px; font-size: 11px; font-weight: 700; border: 1px solid var(--border-color); color: var(--text-primary); letter-spacing: 0.05em;">PREMIUM ACCESS</div>
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

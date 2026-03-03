import streamlit as st
import yfinance as yf
import pandas as pd
import json
import os

from data_provider import get_stock_data, get_etf_data, get_crypto_data, fetch_concurrently
from ui_helpers import (
    render_dataframe, render_etf_dataframe, render_crypto_dataframe, 
    inject_premium_css, render_ticker_tape, render_metric_card,
    render_custom_header
)
from economics_provider import get_market_summary, get_economic_calendar
from tools_helper import render_compound_interest_tool, render_mortgage_tool
import consts

# --- Page Configuration ---
st.set_page_config(
    page_title="Investing Pro Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Inject Premium Styles ---
inject_premium_css()

# --- Load Data ---
TICKERS_FILE = "tickers.json"
DEFAULT_TICKERS = {
    "stocks": ["AAPL", "TSLA", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "NFLX", "AMD", "INTC"],
    "etfs": [],
    "crypto": []
}

def load_tickers():
    if os.path.exists(TICKERS_FILE):
        try:
            with open(TICKERS_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return {"stocks": data, "etfs": [], "crypto": []}
                if isinstance(data, dict):
                    for key in ["stocks", "etfs", "crypto"]:
                        if key not in data:
                            data[key] = []
                    return data
        except Exception:
            pass
    return DEFAULT_TICKERS.copy()

def save_tickers(tickers):
    try:
        with open(TICKERS_FILE, "w") as f:
            json.dump(tickers, f)
    except Exception as e:
        print(f"Error saving tickers: {e}")

# Initialize session state
if 'tickers' not in st.session_state:
    st.session_state.tickers = load_tickers()

def main():
    # --- Top Bar Segment (Ticker Tape) ---
    market_summary = get_market_summary()
    render_ticker_tape(market_summary)
    render_custom_header()

    # --- Sidebar Navigation ---
    with st.sidebar:
        st.title("🛡️ Investing Pro")
        st.markdown("---")
        nav_selection = st.radio(
            "Navegación",
            ["Dashboard Principal", "Análisis de Mercado", "Calendario Económico", "Herramientas"],
            index=0
        )
        st.markdown("---")
        st.caption("Configuración de Cartera")
        # Reuse existing management UI but condensed for sidebar
        with st.expander("Gestionar Tickers"):
            all_stocks = st.session_state.tickers["stocks"]
            to_remove = st.multiselect("Eliminar:", options=all_stocks)
            if st.button("Eliminar Seleccionados"):
                for t in to_remove:
                    st.session_state.tickers["stocks"].remove(t)
                save_tickers(st.session_state.tickers)
                st.rerun()

    if nav_selection == "Dashboard Principal":
        st.title("Panel de Control")
        
        # --- Top Indices Summary Cards ---
        if market_summary:
            num_cards = min(len(market_summary), 4)
            cols = st.columns(num_cards)
            for i in range(num_cards):
                with cols[i]:
                    render_metric_card(
                        market_summary[i]['symbol'], 
                        f"${market_summary[i]['price']}", 
                        market_summary[i]['change_pct']
                    )

        st.markdown("### Mis Activos")
        tab_stocks, tab_etfs, tab_crypto = st.tabs([
            "🏢 Acciones", "📊 ETFs", "🪙 Cripto"
        ])

        with tab_stocks:
            # Search / Add UI
            c1, c2 = st.columns([4, 1])
            with c1:
                search = st.selectbox("Añadir Acción:", [""] + consts.COMMON_TICKERS, key="dash_search", label_visibility="collapsed")
            with c2:
                if st.button("➕ Añadir"):
                    if search:
                        t = consts.get_ticker_from_string(search)
                        if t not in st.session_state.tickers["stocks"]:
                            st.session_state.tickers["stocks"].append(t)
                            save_tickers(st.session_state.tickers)
                            st.success(f"Añadido {t}")
                            st.rerun()
            
            if st.session_state.tickers["stocks"]:
                with st.spinner("Cargando cotizaciones..."):
                    data = fetch_concurrently(st.session_state.tickers["stocks"], get_stock_data)
                if data:
                    df = pd.DataFrame(data)
                    render_dataframe(df)
            else:
                st.info("Añade acciones para comenzar.")

        with tab_etfs:
            if st.session_state.tickers["etfs"]:
                with st.spinner("Cargando ETFs..."):
                    data = fetch_concurrently(st.session_state.tickers["etfs"], get_etf_data)
                if data:
                    render_etf_dataframe(pd.DataFrame(data))
            else:
                st.info("Añade ETFs en la sección de herramientas.")

        with tab_crypto:
             if st.session_state.tickers["crypto"]:
                with st.spinner("Cargando Cripto..."):
                    data = fetch_concurrently(st.session_state.tickers["crypto"], get_crypto_data)
                if data:
                    render_crypto_dataframe(pd.DataFrame(data))
             else:
                st.info("Añade Cripto en la sección de herramientas.")

    elif nav_selection == "Análisis de Mercado":
        st.title("Análisis Financerio")
        st.markdown("### 💎 Oportunidades (Value Investing)")
        if st.session_state.tickers["stocks"]:
            data = fetch_concurrently(st.session_state.tickers["stocks"], get_stock_data)
            df = pd.DataFrame(data)
            undervalued = df[df['Estado'] == 'Infravalorada']
            if not undervalued.empty:
                render_dataframe(undervalued)
                st.balloons()
            else:
                st.info("No hay acciones infravaloradas en tu lista actual.")
        
        st.markdown("---")
        st.markdown("### 📊 Comparativa de Rendimiento (Sparklines Próximamente)")
        st.info("Métricas técnicas detalladas se añadirán en la próxima actualización.")

    elif nav_selection == "Calendario Económico":
        st.title("Calendario Económico")
        st.markdown("Eventos clave que mueven el mercado hoy.")
        cal_df = get_economic_calendar()
        
        # Display as a clean table with highlighting
        def style_importance(val):
            if val == 'High': return 'color: #ef4444; font-weight: bold;'
            if val == 'Medium': return 'color: #f59e0b;'
            return ''
            
        st.dataframe(
            cal_df.style.map(style_importance, subset=['Importance']),
            use_container_width=True,
            hide_index=True
        )

    elif nav_selection == "Herramientas":
        st.title("🛡️ Herramientas Financieras")
        
        tool_type = st.segmented_control(
            "Seleccionar Herramienta",
            ["Calculadora Interés Compuesto", "Calculadora Hipoteca"],
            default="Calculadora Interés Compuesto",
            label_visibility="collapsed"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if tool_type == "Calculadora Interés Compuesto":
            render_compound_interest_tool()
        elif tool_type == "Calculadora Hipoteca":
            render_mortgage_tool()

if __name__ == "__main__":
    main()

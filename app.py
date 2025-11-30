import streamlit as st
import yfinance as yf
import pandas as pd

import json
import os

# Configuración de la página
st.set_page_config(
    page_title="Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS personalizados para imitar el look dark/pro
st.markdown("""
<style>
    .stApp {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    .stDataFrame {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* Ajustes para botones y inputs */
    .stButton button {
        background-color: #007bff;
        color: white;
        border: none;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

TICKERS_FILE = "tickers.json"

def load_tickers():
    if os.path.exists(TICKERS_FILE):
        try:
            with open(TICKERS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return ["AAPL", "TSLA", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "NFLX", "AMD", "INTC"]

def save_tickers(tickers):
    try:
        with open(TICKERS_FILE, "w") as f:
            json.dump(tickers, f)
    except Exception as e:
        print(f"Error saving tickers: {e}")

# Inicializar estado de tickers
if 'tickers' not in st.session_state:
    st.session_state.tickers = load_tickers()

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

@st.cache_data(ttl=3600) # Cache por 1 hora para evitar rate limits
def get_historical_pe(ticker_symbol):
    """
    Calcula el P/E promedio de los últimos 5 años usando datos históricos.
    Retorna (avg_pe, method_used)
    """
    try:
        t = yf.Ticker(ticker_symbol)
        
        # 1. Intentar obtener EPS históricos
        fin = t.financials
        if 'Basic EPS' not in fin.index:
            # Intentar con 'Diluted EPS' si Basic no está
            if 'Diluted EPS' in fin.index:
                eps_series = fin.loc['Diluted EPS']
            else:
                return None, "No historical EPS"
        else:
            eps_series = fin.loc['Basic EPS']
            
        # 2. Obtener precios históricos para las fechas de los reportes
        # Necesitamos precios cercanos a las fechas de los reportes anuales
        pe_values = []
        history = t.history(period="5y")
        
        if history.empty:
            return None, "No price history"

        for date, eps in eps_series.items():
            # Buscar el precio de cierre más cercano a la fecha del reporte
            # Usamos un rango de +/- 5 días por si es fin de semana
            try:
                # Convertir fecha de reporte a timestamp si es necesario
                ts = pd.Timestamp(date)
                # Buscar en history
                # nearest_idx = history.index.get_indexer([ts], method='nearest')[0]
                # price = history.iloc[nearest_idx]['Close']
                
                # Método más robusto: reindexar o buscar
                # Simplemente tomamos el precio del día o el anterior disponible
                mask = (history.index <= ts)
                if mask.any():
                    price = history.loc[mask].iloc[-1]['Close']
                    if eps > 0: # Evitar división por cero o P/E negativos raros para promedio
                        pe = price / eps
                        # Filtrar outliers extremos (ej: P/E > 500 o < 0)
                        if 0 < pe < 200:
                            pe_values.append(pe)
            except Exception:
                continue
                
        if pe_values:
            return sum(pe_values) / len(pe_values), "5y Historical Avg"
        
        return None, "Insufficient data"
        
    except Exception as e:
        print(f"Error calculating historical PE for {ticker_symbol}: {e}")
        return None, "Error"

@st.cache_data(ttl=900) # Cache de 15 min para datos actuales
def get_stock_data(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        current_price = info.get('currentPrice') or info.get('regularMarketPrice')
        if not current_price:
            return None

        eps = info.get('trailingEps')
        pe_ratio = info.get('trailingPE')
        forward_pe = info.get('forwardPE')
        peg_ratio = info.get('pegRatio')
        book_value = info.get('bookValue')
        target_price = info.get('targetMeanPrice')
        
        # --- Advanced Valuation Models ---
        models = {}
        
        # 1. Analyst Target Price (Consenso)
        if target_price:
            models['Analyst Target'] = target_price
            
        # 2. Graham Formula (Modified): V = EPS * (8.5 + 2g)
        # Derivamos 'g' (Crecimiento esperado) del PEG: PEG = PE / g  =>  g = PE / PEG
        if eps and eps > 0 and pe_ratio and peg_ratio and peg_ratio > 0:
            try:
                expected_growth = pe_ratio / peg_ratio
                # Cap growth rate to realistic levels (e.g., max 25% for conservative estimate)
                g = min(expected_growth, 25) 
                graham_value = eps * (8.5 + 2 * g)
                models['Graham Formula'] = graham_value
            except Exception:
                pass

        # 3. Graham Number: REMOVED (Not suitable for Tech/Software with low Book Value)
        # if eps and eps > 0 and book_value and book_value > 0:
        #     try:
        #         graham_number = (22.5 * eps * book_value) ** 0.5
        #         models['Graham Number'] = graham_number
        #     except Exception:
        #         pass
                
        # 4. Historical PE (Fallback / Supplementary)
        hist_pe, _ = get_historical_pe(ticker_symbol)
        if hist_pe and eps:
            models['Historical PE'] = eps * hist_pe

        # --- Composite Fair Value ---
        # Promedio de los modelos disponibles
        if models:
            valid_values = [v for v in models.values() if v is not None and v > 0]
            if valid_values:
                fair_value = sum(valid_values) / len(valid_values)
                
                # Debug string for tooltip
                model_details = "\n".join([f"{k}: ${v:.2f}" for k, v in models.items()])
            else:
                fair_value = None
                model_details = "No valid models"
        else:
            # Fallback extremo: Trailing PE * EPS (si no hay nada más)
            if eps and pe_ratio:
                fair_value = eps * pe_ratio
                model_details = "Fallback: Trailing PE"
            else:
                fair_value = None
                model_details = "Insufficient Data"

        # Status & Potential
        if fair_value:
            potential = ((fair_value - current_price) / current_price)
            
            # Logic based on user observation: +/- 20% range is "Fair Value"
            if potential > 0.20:
                status = "Infravalorada"
            elif potential < -0.20:
                status = "Sobrevalorada"
            else:
                status = "Precio Justo"
        else:
            status = "N/A"
            potential = None

        return {
            "Ticker": ticker_symbol,
            "Nombre": info.get('shortName', ticker_symbol),
            "Precio Actual": current_price,
            "Valor Justo": fair_value,
            "Potencial": potential,
            "Estado": status,
            "Market Cap": info.get('marketCap'),
            "Div Yield": info.get('dividendYield'),
            "P/E": pe_ratio,
            "P/B": info.get('priceToBook'),
            "P/S (TTM)": info.get('priceToSalesTrailing12Months'),
            "EV": info.get('enterpriseValue'),
            "Deuda/Eq": info.get('debtToEquity'),
            "Modelos": model_details # Para mostrar detalles si se desea
        }
    except Exception as e:
        print(f"Error fetching data for {ticker_symbol}: {e}")
        return None

# --- UI Principal ---

# Tabs principales
tab_market, tab_opportunities, tab_risk, tab_health = st.tabs([
    "Visión de mercado", 
    "💎 Oportunidades", 
    "Riesgo", 
    "Salud Financiera"
])

# --- Lógica de visualización común ---
def render_dataframe(dataframe):
    # Configuración de columnas para st.dataframe
    column_config = {
        "Ticker": st.column_config.TextColumn("Símbolo", width="small"),
        "Nombre": st.column_config.TextColumn("Nombre", width="medium"),
        "Precio Actual": st.column_config.NumberColumn(
            "Precio", format="$%.2f"
        ),
        "Valor Justo": st.column_config.NumberColumn(
            "Valor Razonable", 
            format="$%.2f",
            help="Promedio de: Analyst Target, Graham Formula (Growth), Historical PE"
        ),
        "Potencial": st.column_config.ProgressColumn(
            "Potencial",
            format="%.2f%%",
            min_value=-1,
            max_value=1,
        ),
        "Estado": st.column_config.TextColumn(
            "Etiqueta",
            width="small"
        ),
        "Market Cap": st.column_config.NumberColumn(
            "Cap. Mercado",
            format="$%.2e"
        ),
        "Div Yield": st.column_config.NumberColumn(
            "Div Yield",
            format="%.2f%%"
        ),
        "P/E": st.column_config.NumberColumn("PER", format="%.1fx"),
        "P/B": st.column_config.NumberColumn("P/Valor Libro", format="%.1fx"),
        "P/S (TTM)": st.column_config.NumberColumn("P/Ventas", format="%.1fx"),
        "EV": st.column_config.NumberColumn("Valor Empresa", format="$%.2e"),
        "Deuda/Eq": st.column_config.NumberColumn("Deuda/Cap", format="%.1f%%"),
        "Modelos": st.column_config.TextColumn("Detalles Modelos", width="medium"),
    }

    def style_status(val):
        if val == 'Infravalorada':
            color = '#28a745' # Green
        elif val == 'Sobrevalorada':
            color = '#dc3545' # Red
        else: # Precio Justo or N/A
            color = '#ffc107' # Yellow/Orange for Fair Value/Neutral
        return f'color: {color}; font-weight: bold;'

    styled_df = dataframe.style.map(style_status, subset=['Estado'])

    st.dataframe(
        styled_df,
        column_config=column_config,
        use_container_width=True,
        hide_index=True,
        height=600
    )



import consts

# --- Tab 1: Visión de Mercado ---
with tab_market:
    # Área de búsqueda y acciones
    col1, col2 = st.columns([3, 1])
    with col1:
        # Buscador inteligente con autocompletado
        search_selection = st.selectbox(
            "Buscar valores", 
            options=[""] + consts.COMMON_TICKERS, # Opción vacía por defecto
            index=0,
            label_visibility="collapsed", 
            key="search_market",
            placeholder="Escribe para buscar (ej: Apple, TSM...)"
        )
    with col2:
        add_btn = st.button("➕ Añadir", key="add_btn_market")

    # Lógica de añadido
    if add_btn and search_selection:
        # Extraer ticker limpio
        t = consts.get_ticker_from_string(search_selection)
        
        if t in st.session_state.tickers:
            st.warning(f"El ticker {t} ya está en la lista.")
        else:
            # VALIDACIÓN: Verificar si existe en Yahoo Finance
            with st.spinner(f"Validando {t}..."):
                try:
                    # Usamos fast_info para ser más rápidos, o info si es necesario
                    # fast_info a veces no tiene todo, info es más seguro para validar existencia real
                    ticker_obj = yf.Ticker(t)
                    # Intentamos obtener un dato clave
                    price = ticker_obj.info.get('currentPrice') or ticker_obj.info.get('regularMarketPrice')
                    
                    if price:
                        st.session_state.tickers.append(t)
                        save_tickers(st.session_state.tickers)
                        st.success(f"Añadido correctamente: {t}")
                        st.rerun()
                    else:
                        st.error(f"No se encontraron datos para '{t}'. Verifica el ticker.")
                except Exception as e:
                    st.error(f"Error validando '{t}': {e}")
    
    # Opción para añadir manual si no está en la lista
    with st.expander("¿No encuentras tu acción? Añade manualmente"):
        manual_ticker = st.text_input("Ticker manual (ej: BTC-USD)", key="manual_ticker")
        if st.button("Añadir Manual"):
            t_man = manual_ticker.strip().upper()
            if t_man:
                if t_man in st.session_state.tickers:
                    st.warning("Ya está en la lista.")
                else:
                    with st.spinner(f"Validando {t_man}..."):
                        try:
                            ticker_obj = yf.Ticker(t_man)
                            price = ticker_obj.info.get('currentPrice') or ticker_obj.info.get('regularMarketPrice')
                            if price:
                                st.session_state.tickers.append(t_man)
                                save_tickers(st.session_state.tickers)
                                st.success(f"Añadido: {t_man}")
                                st.rerun()
                            else:
                                st.error(f"Ticker inválido o sin datos: {t_man}")
                        except:
                            st.error("Error al validar.")

    # Gestión de Tickers (Eliminar)
    with st.expander("Gestionar / Eliminar Acciones"):
        tickers_to_remove = st.multiselect(
            "Selecciona acciones para eliminar:",
            options=st.session_state.tickers,
            default=[]
        )
        if st.button("Eliminar Seleccionados"):
            if tickers_to_remove:
                for t in tickers_to_remove:
                    if t in st.session_state.tickers:
                        st.session_state.tickers.remove(t)
                save_tickers(st.session_state.tickers) # SAVE
                st.success("Acciones eliminadas.")
                st.rerun()

    # Procesamiento de datos
    data = []
    # Barra de progreso
    progress_bar = st.progress(0)
    total_tickers = len(st.session_state.tickers)

    for i, t in enumerate(st.session_state.tickers):
        res = get_stock_data(t)
        if res:
            data.append(res)
        progress_bar.progress((i + 1) / total_tickers)

    progress_bar.empty()

    if data:
        df = pd.DataFrame(data)
        render_dataframe(df)
    else:
        st.info("No hay datos para mostrar. Añade tickers para comenzar.")

# --- Tab 2: Oportunidades ---
with tab_opportunities:
    st.markdown("### 💎 Acciones Infravaloradas")
    st.markdown("Filtrando solo acciones donde el **Precio Actual < Valor Justo**.")
    
    if data:
        df_opp = pd.DataFrame(data)
        undervalued_df = df_opp[df_opp['Estado'] == "Infravalorada"]
        
        if not undervalued_df.empty:
            render_dataframe(undervalued_df)
            st.balloons()
        else:
            st.info("No se encontraron oportunidades infravaloradas en tu lista actual.")
    else:
        st.info("Carga datos en la pestaña 'Visión de mercado' primero.")

# --- Placeholders para otras tabs ---
with tab_risk:
    st.info("Próximamente: Análisis de Volatilidad y Beta.")

with tab_health:
    st.info("Próximamente: Altman Z-Score y Ratios de Liquidez.")

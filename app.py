import streamlit as st
import yfinance as yf
import pandas as pd

import json
import os

DEFAULT_TICKERS = {
    "stocks": ["AAPL", "TSLA", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "NFLX", "AMD", "INTC"],
    "etfs": [],
    "crypto": []
}

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
    /* Mejora de visibilidad de Tabs */
    button[data-baseweb="tab"] {
        color: #a0a0a0; /* Gris claro para no seleccionados */
        font-weight: 500;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #ffffff; /* Blanco para seleccionados */
        background-color: #2b2b2b;
        border-top: 2px solid #007bff;
    }
</style>
""", unsafe_allow_html=True)

TICKERS_FILE = "tickers.json"

def load_tickers():
    if os.path.exists(TICKERS_FILE):
        try:
            with open(TICKERS_FILE, "r") as f:
                data = json.load(f)
                # Migration: If it's a list (old format), convert to dict
                if isinstance(data, list):
                    return {
                        "stocks": data,
                        "etfs": [],
                        "crypto": []
                    }
                # Validation: Ensure all keys exist
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

@st.cache_data(ttl=900)
def get_etf_data(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('navPrice')
        # Prices
        current_price = info.get('currentPrice') or info.get('navPrice') or info.get('regularMarketPrice')
        if not current_price:
            return None

        # Helper to safely get value or None
        def safe_get(key):
            v = info.get(key)
            return v if v is not None else None

        # Potential & Status based on 52-Week High
        high_52w = safe_get('fiftyTwoWeekHigh')
        potential = None
        status = "N/A"
        
        if current_price and high_52w and high_52w > 0:
            potential = (high_52w - current_price) / current_price
            
            if potential > 0.20:
                status = "Oportunidad de Rebote"
            elif potential > 0.05:
                status = "Recuperando"
            elif potential >= 0:
                status = "Cerca de Máximos"
            else:
                status = "En Máximos"

        return {
            "Ticker": ticker_symbol,
            "Nombre": info.get('shortName', ticker_symbol),
            "Precio": current_price,
            "Potencial": potential,
            "Estado": status,
            "Yield": safe_get('yield'),
            "Expense Ratio": safe_get('annualReportExpenseRatio'),
            "Retorno YTD": safe_get('ytdReturn'),
            "Categoría": safe_get('category'),
            "Activos": safe_get('totalAssets')
        }
    except Exception as e:
        print(f"Error fetching ETF data for {ticker_symbol}: {e}")
        return None

@st.cache_data(ttl=300)
def get_crypto_data(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        current_price = info.get('currentPrice') or info.get('regularMarketPrice')
        if not current_price:
            return None
            
        market_cap = info.get('marketCap')
        volume_24h = info.get('volume24Hr') or info.get('volume')
        circulating_supply = info.get('circulatingSupply')
        
        # Trend Logic (Calculated independently)
        ma50 = info.get('fiftyDayAverage')
        ma200 = info.get('twoHundredDayAverage')
        trend = "Neutro"
        if ma50 and ma200:
            if current_price > ma50 and current_price > ma200:
                trend = "Alcista (Bullish)"
            elif current_price < ma50 and current_price < ma200:
                trend = "Bajista (Bearish)"
        else:
             trend = "N/A"

        # Status logic (Opportunity from 52W High)
        high_52w = info.get('fiftyTwoWeekHigh')
        potential = None
        status = "Neutro" # Default fallback
        
        if current_price and high_52w and high_52w > 0:
            potential = (high_52w - current_price) / current_price
            
            if potential > 0.20:
                status = "Oportunidad de Rebote"
            elif potential > 0.05:
                status = "Recuperando"
            elif potential >= 0:
                status = "Cerca de Máximos"
            else:
                status = "En Máximos"

        return {
            "Ticker": ticker_symbol,
            "Nombre": info.get('shortName', ticker_symbol),
            "Precio": current_price,
            "Potencial": potential,
            "Estado": status,
            "Tendencia": trend,
            "Market Cap": info.get('marketCap'),
            "Volumen 24h": info.get('volume24Hr'),
            "Circulating Supply": info.get('circulatingSupply'),
            "MA 50d": info.get('fiftyDayAverage'),
            "MA 200d": info.get('twoHundredDayAverage')
        }
    except Exception as e:
        print(f"Error fetching Crypto data for {ticker_symbol}: {e}")
        return None

# --- Helper Functions ---
def render_dataframe(dataframe):
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
        "Modelos": st.column_config.TextColumn("Detalles Modelos", width="medium"),
    }

    def style_status(val):
        if val == 'Infravalorada':
            color = '#28a745'
        elif val == 'Sobrevalorada':
            color = '#dc3545'
        else: 
            color = '#ffc107'
        return f'color: {color}; font-weight: bold;'

    styled_df = dataframe.style.map(style_status, subset=['Estado'])

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
    # Style logic based on Status
    def highlight_crypto_status(val):
        color = ''
        if 'Alcista' in str(val) or 'En Máximos' in str(val):
            color = 'background-color: #2ca02c; color: white'
        elif 'Bajista' in str(val):
             color = 'background-color: #d62728; color: white'
        elif 'Oportunidad' in str(val):
             color = 'background-color: #1f77b4; color: white'
        return color

    def highlight_trend(val):
        color = ''
        if 'Alcista' in str(val):
            color = 'color: #2ca02c; font-weight: bold'
        elif 'Bajista' in str(val):
            color = 'color: #d62728; font-weight: bold'
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

# --- UI Principal ---
def main():
    import consts
    
    # Tabs principales
    tab_stocks, tab_etfs, tab_crypto, tab_opportunities, tab_risk, tab_health = st.tabs([
        "🏢 Acciones",
        "📊 ETFs",
        "🪙 Criptomonedas", 
        "💎 Oportunidades", 
        "Riesgo", 
        "Salud Financiera"
    ])

    # --- Tab 1: Acciones ---
    with tab_stocks:
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
            
            if t in st.session_state.tickers["stocks"]:
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
                            st.session_state.tickers["stocks"].append(t)
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
                    if t_man in st.session_state.tickers["stocks"]:
                        st.warning("Ya está en la lista.")
                    else:
                        with st.spinner(f"Validando {t_man}..."):
                            try:
                                ticker_obj = yf.Ticker(t_man)
                                price = ticker_obj.info.get('currentPrice') or ticker_obj.info.get('regularMarketPrice')
                                if price:
                                    st.session_state.tickers["stocks"].append(t_man)
                                    save_tickers(st.session_state.tickers)
                                    st.success(f"Añadido: {t_man}")
                                    st.rerun()
                                else:
                                    st.error(f"Ticker inválido o sin datos: {t_man}")
                            except Exception:
                                st.error("Error al validar.")

        # Gestión de Tickers (Eliminar)
        with st.expander("Gestionar / Eliminar Acciones"):
            tickers_to_remove = st.multiselect(
                "Selecciona acciones para eliminar:",
                options=st.session_state.tickers["stocks"],
                default=[]
            )
            if st.button("Eliminar Seleccionados"):
                if tickers_to_remove:
                    for t in tickers_to_remove:
                        if t in st.session_state.tickers["stocks"]:
                            st.session_state.tickers["stocks"].remove(t)
                    save_tickers(st.session_state.tickers) # SAVE
                    st.success("Acciones eliminadas.")
                    st.rerun()

        # Procesamiento de datos
        data = []
        # Barra de progreso
        progress_bar = st.progress(0)
        total_tickers = len(st.session_state.tickers["stocks"])

        for i, t in enumerate(st.session_state.tickers["stocks"]):
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


    # --- Tab 2: ETFs ---
    with tab_etfs:
        col1, col2 = st.columns([3, 1])
        with col1:
            etf_search = st.selectbox(
                "Añadir ETF", 
                options=[""] + consts.COMMON_ETFS,
                index=0,
                label_visibility="collapsed",
                placeholder="Buscar ETF (ej: VOO, QQQ...)",
                key="etf_search"
            )
        with col2:
            add_etf_btn = st.button("➕ Añadir ETF")

        if add_etf_btn and etf_search:
            t = consts.get_ticker_from_string(etf_search)
            if t in st.session_state.tickers["etfs"]:
                st.warning("Ya está en la lista.")
            else:
                with st.spinner(f"Validando {t}..."):
                    try:
                        ticker = yf.Ticker(t)
                        # Simple validation: checks if it has a price or nav
                        info = ticker.info
                        if info.get('currentPrice') or info.get('navPrice') or info.get('regularMarketPrice'):
                            st.session_state.tickers["etfs"].append(t)
                            save_tickers(st.session_state.tickers)
                            st.success(f"Añadido: {t}")
                            st.rerun()
                        else:
                            st.error("No se encontraron datos.")
                    except Exception:
                        st.error("Ticker inválido.")

        # Manual Add
        with st.expander("¿No encuentras tu ETF? Añade manualmente"):
            manual_etf = st.text_input("Ticker manual (ej: VUAG.L)", key="manual_etf")
            if st.button("Añadir Manual", key="btn_manual_etf"):
                t_man = manual_etf.strip().upper()
                if t_man:
                    if t_man in st.session_state.tickers["etfs"]:
                        st.warning("Ya está en la lista.")
                    else:
                        with st.spinner(f"Validando {t_man}..."):
                            try:
                                ticker = yf.Ticker(t_man)
                                info = ticker.info
                                if info.get('currentPrice') or info.get('navPrice') or info.get('regularMarketPrice'):
                                    st.session_state.tickers["etfs"].append(t_man)
                                    save_tickers(st.session_state.tickers)
                                    st.success(f"Añadido: {t_man}")
                                    st.rerun()
                                else:
                                    st.error("No se encontraron datos.")
                            except Exception:
                                st.error("Error al validar.")

        # Remove ETFs
        with st.expander("Gestionar ETFs"):
            etfs_to_remove = st.multiselect("Eliminar ETFs", options=st.session_state.tickers["etfs"], key="remove_etfs")
            if st.button("Eliminar Seleccionados", key="btn_remove_etfs"):
                for t in etfs_to_remove:
                    if t in st.session_state.tickers["etfs"]:
                        st.session_state.tickers["etfs"].remove(t)
                save_tickers(st.session_state.tickers)
                st.rerun()

        # Data
        etf_data = []
        if st.session_state.tickers["etfs"]:
            progress_etf = st.progress(0)
            total_etfs = len(st.session_state.tickers["etfs"])
            for i, t in enumerate(st.session_state.tickers["etfs"]):
                d = get_etf_data(t)
                if d: etf_data.append(d)
                progress_etf.progress((i+1)/total_etfs)
            progress_etf.empty()

        if etf_data:
            render_etf_dataframe(pd.DataFrame(etf_data))
        else:
            st.info("Añade ETFs para ver información.")
            
        with st.expander("ℹ️ Ayuda: ¿Qué significan estos datos?"):
            st.markdown("""
            **Potencial 52w**: Porcentaje que le falta subir para recuperar su Máximo Anual (52-Week High).
            * Cálculo: `(Máximo 52 Semanas - Precio Actual) / Precio Actual`
            * **Oportunidad de Rebote**: El activo ha caído >20% desde sus máximos.
            * **Recuperando**: Ha caído entre 5% y 20%.
            * **Cerca de Máximos**: Está a menos de un 5% de su máximo.
            """)

    # --- Tab 3: Criptomonedas ---
    with tab_crypto:
        col1, col2 = st.columns([3, 1])
        with col1:
            crypto_search = st.selectbox(
                "Añadir Cripto",
                options=[""] + consts.COMMON_CRYPTO,
                index=0,
                label_visibility="collapsed",
                placeholder="Buscar Cripto (ej: BTC-USD...)",
                key="crypto_search"
            )
        with col2:
            add_crypto_btn = st.button("➕ Añadir Cripto")

        if add_crypto_btn and crypto_search:
            t = consts.get_ticker_from_string(crypto_search)
            if t in st.session_state.tickers["crypto"]:
                st.warning("Ya está en la lista.")
            else:
                with st.spinner(f"Validando {t}..."):
                    try:
                        ticker = yf.Ticker(t)
                        if ticker.info.get('currentPrice') or ticker.info.get('regularMarketPrice'):
                            st.session_state.tickers["crypto"].append(t)
                            save_tickers(st.session_state.tickers)
                            st.success(f"Añadido: {t}")
                            st.rerun()
                        else:
                            st.error("No se encontraron datos.")
                    except Exception:
                        st.error("Ticker inválido (asegúrate de usar XXX-USD).")

        # Manual Add
        with st.expander("¿No encuentras tu Cripto? Añade manualmente"):
            manual_crypto = st.text_input("Ticker manual (ej: DOGE-USD)", key="manual_crypto")
            if st.button("Añadir Manual", key="btn_manual_crypto"):
                t_man = manual_crypto.strip().upper()
                if t_man:
                    if t_man in st.session_state.tickers["crypto"]:
                        st.warning("Ya está en la lista.")
                    else:
                        with st.spinner(f"Validando {t_man}..."):
                            try:
                                ticker = yf.Ticker(t_man)
                                if ticker.info.get('currentPrice') or ticker.info.get('regularMarketPrice'):
                                    st.session_state.tickers["crypto"].append(t_man)
                                    save_tickers(st.session_state.tickers)
                                    st.success(f"Añadido: {t_man}")
                                    st.rerun()
                                else:
                                    st.error("No se encontraron datos.")
                            except Exception:
                                st.error("Error al validar.")

        # Remove Crypto
        with st.expander("Gestionar Criptomonedas"):
            crypto_to_remove = st.multiselect("Eliminar Criptos", options=st.session_state.tickers["crypto"], key="remove_crypto")
            if st.button("Eliminar Seleccionados", key="btn_remove_crypto"):
                for t in crypto_to_remove:
                    if t in st.session_state.tickers["crypto"]:
                        st.session_state.tickers["crypto"].remove(t)
                save_tickers(st.session_state.tickers)
                st.rerun()

        # Data
        crypto_data = []
        if st.session_state.tickers["crypto"]:
            progress_crypto = st.progress(0)
            total_crypto = len(st.session_state.tickers["crypto"])
            for i, t in enumerate(st.session_state.tickers["crypto"]):
                d = get_crypto_data(t)
                if d: crypto_data.append(d)
                progress_crypto.progress((i+1)/total_crypto)
            progress_crypto.empty()

        if crypto_data:
            render_crypto_dataframe(pd.DataFrame(crypto_data))
        else:
            st.info("Añade Criptomonedas (ej: BTC-USD) para comenzar.")
            
        with st.expander("ℹ️ Ayuda: ¿Qué significan estos datos?"):
            st.markdown("""
            **Potencial 52w**: Distancia hasta el máximo precio del último año.
            * **Oportunidad de Rebote**: Caída >20% desde máximos. Puede indicar un buen punto de entrada si la tendencia de fondo es alcista.
            * **Alcista / En Máximos**: El activo está rompiendo récords o muy fuerte.
            """)

    # --- Tab 4: Oportunidades ---
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

if __name__ == "__main__":
    main()

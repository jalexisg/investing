# 📈 Stock Analysis Dashboard

Una aplicación web profesional de análisis financiero construida con **Python** y **Streamlit**, diseñada para replicar y mejorar funcionalidades clave de **Investing.com**.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue)
![Agents](https://img.shields.io/badge/AGENTS.md-Implemented-purple)

> **For AI Agents**: Please refer to [AGENTS.md](AGENTS.md) for context and instructions.


## 🚀 Características

- **Monitor de Mercado en Tiempo Real**: Visualización de precios, cambios y métricas clave.
- **Estilo "Investing.com"**: Interfaz oscura profesional con tablas detalladas.
- **Valoración Avanzada (Fair Value)**: Cálculo de "Valor Justo" compuesto utilizando múltiples modelos:
    - **Precio Objetivo de Analistas**: Consenso del mercado.
    - **Fórmula de Graham (Modificada)**: Basada en el crecimiento esperado ($V = EPS \times (8.5 + 2g)$).
    - **P/E Histórico**: Basado en el promedio de valoración de los últimos 5 años.
- **Detección de Oportunidades**: Identificación automática de acciones "Infravaloradas" vs "Sobrevaloradas".
- **Gestión de Tickers**: Barra de búsqueda integrada para añadir cualquier acción (e.g., AAPL, MSFT, IBM).
- **Dockerizado**: Listo para desplegar en cualquier entorno con Docker.

## 🛠️ Stack Tecnológico

- **Frontend**: Streamlit (Python)
- **Datos**: `yfinance` (Yahoo Finance API)
- **Contenedorización**: Docker & Docker Compose
- **Análisis**: Pandas & NumPy

## 📦 Instalación y Uso

### Opción 1: Docker (Recomendada)

1.  Clona el repositorio:
    ```bash
    git clone <tu-repo>
    cd investing
    ```

2.  Construye y corre el contenedor:
    ```bash
    docker-compose up --build
    ```

3.  Abre tu navegador en:
    [http://localhost:8501](http://localhost:8501)

### Opción 2: Local (Python)

1.  Crea un entorno virtual:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```

2.  Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

3.  Ejecuta la aplicación:
    ```bash
    streamlit run app.py
    ```

## 📊 Modelos de Valoración

El "Valor Justo" se calcula como el promedio de los siguientes modelos (cuando hay datos disponibles):

1.  **Analyst Target Price**: El precio objetivo promedio estimado por analistas profesionales.
2.  **Graham Formula**: Una adaptación de la fórmula clásica de Benjamin Graham, ajustada por el crecimiento derivado del ratio PEG.
3.  **Historical PE Valuation**: Valoración basada en multiplicar el EPS actual por el P/E promedio histórico (5 años) de la acción.

> **Nota**: El "Número de Graham" (basado en activos) fue excluido intencionalmente para evitar infravalorar empresas tecnológicas con pocos activos tangibles (como Microsoft o Apple).

## 📝 Licencia

Este proyecto es de uso libre para fines educativos y personales.

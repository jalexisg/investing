# AGENTS.md

> **Purpose**: This file provides context and instructions for AI agents working on the Investing project.

## Project Overview
This project is a professional financial analysis web application built with **Python** and **Streamlit**, designed to replicate and enhance key functionalities of **Investing.com**.

### Key Features
- **Real-time Market Monitor**: Prices, changes, and metrics.
- **Fair Value Calculation**: Uses multiple models (Analyst Targets, Graham Formula, Historical PE).
- **Opportunity Detection**: Undervalued vs Overvalued identification.
- **Dockerized**: Fully containerized for easy deployment.

## Tech Stack
- **Frontend**: Streamlit
- **Data Source**: `yfinance`
- **Analysis**: Pandas, NumPy
- **Containerization**: Docker, Docker Compose

## Development Environment
- **Run locally**: `streamlit run app.py`
- **Run with Docker**: `docker-compose up --build`
- **Python Version**: 3.9+

## Directory Structure
- `/`: Root application files (`app.py`, `consts.py`, `tickers.json`).
- `skills/`: Directory containing AI agent skills and helper scripts.
- `tests/`: Automated tests.

## Agent Skills
This project uses the `skills/` directory to organize specialized capabilities.
- **Debug Utils** (`skills/debug_utils`): Scripts for debugging individual tickers and valuation models.

Always refer to `SKILL.md` within each skill folder for specific instructions.

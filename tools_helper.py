import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

def render_compound_interest_tool():
    """Renders a professional compound interest calculator."""
    st.subheader("📈 Calculadora de Interés Compuesto")
    st.markdown("Proyecta el crecimiento de tu patrimonio a largo plazo.")

    col1, col2 = st.columns([1, 2])

    with col1:
        initial_investment = st.number_input("Inversión Inicial ($)", min_value=0, value=10000, step=1000)
        monthly_contribution = st.number_input("Contribución Mensual ($)", min_value=0, value=500, step=100)
        annual_rate = st.slider("Tasa de Interés Anual (%)", min_value=1.0, max_value=20.0, value=8.0, step=0.5)
        years = st.slider("Años de Inversión", min_value=1, max_value=50, value=20)

    # Calculation logic
    months = years * 12
    monthly_rate = (1 + annual_rate / 100) ** (1 / 12) - 1
    
    data = []
    balance = initial_investment
    total_contributions = initial_investment
    
    data.append({
        "Mes": 0,
        "Año": 0,
        "Saldo": balance,
        "Contribuciones": total_contributions,
        "Intereses": 0
    })

    for month in range(1, months + 1):
        interest = balance * monthly_rate
        balance += interest + monthly_contribution
        total_contributions += monthly_contribution
        
        if month % 12 == 0:
            data.append({
                "Mes": month,
                "Año": month // 12,
                "Saldo": round(balance, 2),
                "Contribuciones": round(total_contributions, 2),
                "Intereses": round(balance - total_contributions, 2)
            })

    df = pd.DataFrame(data)

    with col2:
        # Summary metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Saldo Final", f"${balance:,.2f}")
        m2.metric("Total Invertido", f"${total_contributions:,.2f}")
        m3.metric("Intereses Totales", f"${(balance - total_contributions):,.2f}")

        # Plotting
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['Año'], y=df['Saldo'], name='Saldo Total', fill='tozeroy', line=dict(color='#38bdf8')))
        fig.add_trace(go.Scatter(x=df['Año'], y=df['Contribuciones'], name='Capital Invertido', fill='tozeroy', line=dict(color='#94a3b8')))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f8fafc'),
            margin=dict(l=0, r=0, t=30, b=0),
            height=300,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(gridcolor='#334155', title="Años"),
            yaxis=dict(gridcolor='#334155', title="Valor ($)")
        )
        st.plotly_chart(fig, use_container_width=True)

def render_mortgage_tool():
    """Renders a professional mortgage calculator."""
    st.subheader("🏠 Calculadora de Hipoteca")
    st.markdown("Calcula cuotas mensuales y el coste total de tu vivienda.")

    col1, col2 = st.columns([1, 2])

    with col1:
        loan_amount = st.number_input("Importe del Préstamo ($)", min_value=0, value=200000, step=10000)
        interest_rate = st.number_input("Interés Anual (%)", min_value=0.1, value=3.5, step=0.1)
        loan_term = st.slider("Plazo (Años)", min_value=1, max_value=40, value=30)
        
    # Calculation
    monthly_rate = interest_rate / 100 / 12
    num_payments = loan_term * 12
    
    if monthly_rate > 0:
        monthly_payment = (loan_amount * monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)
    else:
        monthly_payment = loan_amount / num_payments
        
    total_paid = monthly_payment * num_payments
    total_interest = total_paid - loan_amount

    with col2:
        st.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.5); padding: 25px; border-radius: 15px; border: 1px solid #334155;">
            <div style="text-align: center; margin-bottom: 20px;">
                <p style="color: #94a3b8; font-size: 14px; margin-bottom: 5px;">CUOTA MENSUAL ESTIMADA</p>
                <h2 style="color: #38bdf8; font-size: 42px; margin: 0;">${monthly_payment:,.2f}</h2>
            </div>
            <hr style="border-color: #334155;">
            <div style="display: flex; justify-content: space-between; margin-top: 20px;">
                <div>
                    <p style="color: #94a3b8; font-size: 12px; margin: 0;">TOTAL A PAGAR</p>
                    <p style="font-size: 18px; font-weight: bold;">${total_paid:,.2f}</p>
                </div>
                <div style="text-align: right;">
                    <p style="color: #94a3b8; font-size: 12px; margin: 0;">TOTAL INTERESES</p>
                    <p style="font-size: 18px; font-weight: bold; color: #ef4444;">${total_interest:,.2f}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Donut Chart for Breakdown
        labels = ['Capital', 'Intereses']
        values = [loan_amount, total_interest]
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.6, marker=dict(colors=['#38bdf8', '#ef4444']))])
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f8fafc'),
            margin=dict(l=0, r=0, t=0, b=0),
            height=200,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

import streamlit as st
import pandas as pd
from calculator import calculator

st.title("KiwiSaver + Life Cover Offset Projection")

st.write("Enter your details below to run the projection:")

# --- User Inputs ---
L = st.number_input("Base Life Cover (NZD)", value=500000.0, step=10000.0)
P0 = st.number_input("Baseline Premium (NZD)", value=1800.0, step=50.0)
K0 = st.number_input("KiwiSaver Start Balance (NZD)", value=0.0, step=1000.0)
S0 = st.number_input("Annual Salary Contribution (NZD)", value=0.0, step=100.0)

# --- Run Calculator ---
if st.button("Run Projection"):
    df = calculator(max_t=30,  # fixed at 2 for now
                    L=L,
                    P0=P0,
                    g=0.03,
                    r_avg=0.05011,
                    K0=K0,
                    S0=S0,
                    alpha=1.0)
    
    st.subheader("Projection Results")
    st.dataframe(df.style.format({
        "KiwiSaver Start Balance": "{:,.2f}",
        "Baseline Premium": "{:,.2f}",
        "Offset": "{:,.2f}",
        "Effective Cover": "{:,.2f}",
        "Premium w/ Offset": "{:,.2f}",
        "Premium Saving": "{:,.2f}",
        "Voluntary Contribution": "{:,.2f}",
        "Annual Salary Contribution": "{:,.2f}",
        "Annual Investment Return": "{:,.2f}",
        "KiwiSaver End Balance": "{:,.2f}"
    }))

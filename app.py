import streamlit as st
import pandas as pd
from calculator import calculator

st.title("KiwiSaver + Life Cover Offset Projection")

st.write("Enter your details below to run the projection:")

# --- User Inputs ---
L = st.number_input("Base Life Cover (NZD)", value=500000.0, step=10000.0)
P0 = st.number_input("Baseline Premium (NZD)", value=1800.0, step=50.0)
g = st.number_input("Annual Premium Escalation Rate (%)", value=3.0, step=0.1) / 100
r_avg = st.number_input("Annual Rate on Investment (%)", value=5.011, step=0.01) / 100
K0 = st.number_input("KiwiSaver Start Balance (NZD)", value=100000.0, step=1000.0)
Salary = st.number_input("Annual Salary (NZD)", value=80000.0, step=1000.0)
si = st.number_input("Annual Salary Increase (%)", value=3.0, step=0.5)/100
percetnage = st.number_input("Annual KiwiSaver Contribution (%)", value=3.0, step=0.5)/100
current_age = st.number_input("Age of client", value=21, step=1)
stop_age = st.number_input("Calculator stopping age", value=65, step=1)

# --- Run Calculator ---
if st.button("Run Projection"):
    df, full_cover_t = calculator(max_t=stop_age-current_age,  # fixed at 2 for now
                    L=L,
                    P0=P0,
                    g=g,
                    r_avg=r_avg,
                    K0=K0,
                    si=si,
                    S0=Salary * percetnage,
                    alpha=1.0)
    
    # --- Show message when KiwiSaver fully offsets Life Cover ---
    # last_year = df["years"].iloc[-1]
    st.success(f"Based on your inputs, the client will no longer need life cover at age {full_cover_t + current_age}.")
    
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
    }),
    hide_index=True
    )
    

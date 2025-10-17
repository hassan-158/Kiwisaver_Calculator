import streamlit as st
import pandas as pd
from calculator import calculator
import plotly.graph_objects as go
from PIL import Image

BRAND = {
    "yellow": "#FFD200",
    "dark": "#222222",
}

col1, col2 = st.columns([0.2, 1])
with col1:
    logo = Image.open("assets/logo.png")
    st.image(logo, use_container_width=True)

st.title("Wealthhq Life Cover Offset Calculator")

st.set_page_config(page_title="KiwiSaver Offset Projection", layout="wide")
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
    df_offset, full_cover_t = calculator(
        max_t=stop_age-current_age,
        L=L,
        P0=P0,
        g=g,
        r_avg=r_avg,
        K0=K0,
        si=si,
        S0=Salary * percetnage,
        alpha=1.0
    )
    
    # --- Without Offset (new scenario) ---
    df_no_offset, _ = calculator(
        max_t=stop_age-current_age,
        L=L,
        P0=P0,
        g=g,
        r_avg=r_avg,
        K0=K0,
        si=si,
        S0=Salary * percetnage,
        alpha=0.0   # 👈 disables offset effect
    )
    
    # --- Show message when KiwiSaver fully offsets Life Cover ---
    st.success(f"Based on your inputs, the client will no longer need life cover at age {full_cover_t + current_age}.")
    
    st.subheader("Projection Results")
    st.dataframe(df_offset.style.format({
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
    
    st.title("Offset vs No Offset Benchmark")
    st.subheader("Summary Statistics")

    total_premium_with_offset = df_offset["Premium w/ Offset"].sum()
    total_premium_without_offset = df_no_offset["Baseline Premium"].sum()

    ks_end_with_offset = df_offset["KiwiSaver End Balance"].iloc[-1]
    ks_end_without_offset = df_no_offset["KiwiSaver End Balance"].iloc[-1]

    total_true_cost = ks_end_with_offset - ks_end_without_offset
    per_year_true_cost = total_true_cost / (stop_age - current_age)

    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
    col1.metric("Total Cost of Insurance Premiums (With Offset)", f"${total_premium_with_offset:,.0f}")
    col2.metric("Total Cost of Insurance Premiums (Without Offset)", f"${total_premium_without_offset:,.0f}")
    col3.metric("Total True Cost", f"${total_true_cost:,.0f}")
    col4.metric("True Cost / Year", f"${per_year_true_cost:,.0f}")

    st.write("---")

    st.markdown("### Scenario Comparison Charts")

    # --- Top Row ---
    col_a, spacer, col_c = st.columns([1, 0.2, 1])

    # --- Plot 1: KiwiSaver End Balance ---
    with col_a:
        fig_ks = go.Figure()
        fig_ks.add_trace(go.Scatter(
            x=df_offset["year"] + current_age,
            y=df_offset["KiwiSaver End Balance"],
            mode="lines+markers",
            name="KiwiSaver (With Offset)",
            line=dict(color=BRAND["yellow"], width=3)
        ))
        fig_ks.add_trace(go.Scatter(
            x=df_no_offset["year"] + current_age,
            y=df_no_offset["KiwiSaver End Balance"],
            mode="lines+markers",
            name="KiwiSaver (Without Offset)",
            line=dict(color=BRAND["dark"], width=3)
        ))
        fig_ks.update_layout(
            title="KiwiSaver Balance",
            xaxis_title="Client Age (years)",
            yaxis_title="Value (NZD)",
            legend_title="Scenario",
            hovermode="x unified"
        )
        st.plotly_chart(fig_ks, use_container_width=True)

    # --- Plot 2: Premiums ---
    with col_c:
        fig_prem = go.Figure()
        fig_prem.add_trace(go.Scatter(
            x=df_offset["year"] + current_age,
            y=df_offset["Premium w/ Offset"],
            mode="lines+markers",
            name="Premium (With Offset)",
            line=dict(color=BRAND["yellow"], width=3)
        ))
        fig_prem.add_trace(go.Scatter(
            x=df_no_offset["year"] + current_age,
            y=df_no_offset["Baseline Premium"],
            mode="lines+markers",
            name="Premium (Without Offset)",
            line=dict(color=BRAND["dark"], width=3)
        ))
        fig_prem.update_layout(
            title="Insurance Premiums",
            xaxis_title="Client Age (years)",
            yaxis_title="Annual Premium (NZD)",
            legend_title="Scenario",
            hovermode="x unified"
        )
        st.plotly_chart(fig_prem, use_container_width=True)

    # --- Bottom Row ---
    col_b, spacer_bottom, col_d = st.columns([1, 0.2, 1])

    # --- Plot 3: Life Cover ---
    with col_b:
        fig_cover = go.Figure()
        fig_cover.add_trace(go.Scatter(
            x=df_offset["year"] + current_age,
            y=df_offset["Effective Cover"],
            mode="lines+markers",
            name="Life Cover (With Offset)",
            line=dict(color=BRAND["yellow"], width=3)
        ))
        fig_cover.add_trace(go.Scatter(
            x=df_no_offset["year"] + current_age,
            y=[L] * len(df_no_offset),
            mode="lines+markers",
            name="Life Cover (Without Offset)",
            line=dict(color=BRAND["dark"], width=3)
        ))
        fig_cover.update_layout(
            title="Life Cover Level",
            xaxis_title="Client Age (years)",
            yaxis_title="Cover (NZD)",
            legend_title="Scenario",
            hovermode="x unified"
        )
        st.plotly_chart(fig_cover, use_container_width=True)

    # --- Plot 4: Annual KiwiSaver Investment Return ---
    with col_d:
        fig_return = go.Figure()
        fig_return.add_trace(go.Scatter(
            x=df_offset["year"] + current_age,
            y=df_offset["Annual Investment Return"],
            mode="lines+markers",
            name="Investment Return (With Offset)",
            line=dict(color=BRAND["yellow"], width=3)
        ))
        fig_return.add_trace(go.Scatter(
            x=df_no_offset["year"] + current_age,
            y=df_no_offset["Annual Investment Return"],
            mode="lines+markers",
            name="Investment Return (Without Offset)",
            line=dict(color=BRAND["dark"], width=3)
        ))
        fig_return.update_layout(
            title="Annual KiwiSaver Investment Return",
            xaxis_title="Client Age (years)",
            yaxis_title="Return (NZD)",
            legend_title="Scenario",
            hovermode="x unified"
        )
        st.plotly_chart(fig_return, use_container_width=True)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from PIL import Image

from calculator import *


# Branding colours
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



L = st.number_input("Base Life Cover (NZD)", value=500_000.0, step=10_000.0, format="%f")
P0 = st.number_input("Baseline Premium (Phase-Out) (NZD)", value=1_800.0, step=50.0, format="%f")
g = st.number_input("Annual Premium Escalation Rate (%)", value=3.0, step=0.1) / 100.0

r_avg = st.number_input("Annual Rate on Investment (%)", value=5.011, step=0.01) / 100.0
K0 = st.number_input("KiwiSaver Start Balance (NZD)", value=100_000.0, step=1_000.0, format="%f")

Salary = st.number_input("Annual Salary (NZD)", value=80_000.0, step=1_000.0, format="%f")
si = st.number_input("Annual Salary Increase (%)", value=3.0, step=0.5) / 100.0
percentage = st.number_input("Annual KiwiSaver Contribution (%)", value=3.0, step=0.5) / 100.0

current_age = st.number_input("Age of client", value=21, step=1)
stop_age = st.number_input("Calculator stopping age", value=65, step=1)

st.markdown("**Total Wealth inputs**")
enable_total_wealth = st.checkbox("Enable Total-Wealth approach", value=True)

# Break out asset inputs (KiwiSaver is already supplied as K0)
property_value = st.number_input("Property Value (NZD)", value=200_000.0, step=1_000.0, format="%f")
cash = st.number_input("Cash (NZD)", value=50_000.0, step=1_000.0, format="%f")
managed_funds = st.number_input("Managed Funds (NZD)", value=100_000.0, step=1_000.0, format="%f")
other_assets = st.number_input("Other Assets (NZD)", value=20_000.0, step=1_000.0, format="%f")

liabilities = st.number_input("Total Liabilities (NZD)", value=600_000.0, step=1_000.0, format="%f")

asset_growth_rate = st.number_input("Annual Asset Growth Rate (%)", value=5.01, step=0.1) / 100.0
debt_shrink_rate = st.number_input("Annual Debt Shrink Rate (%)", value=5.01, step=0.1) / 100.0

num_kids = st.number_input("Number of children", min_value=0, max_value=20, value=0, step=1)

# Child ages entry (render below to keep layout tidy)
child_ages = []
if num_kids > 0:
    st.markdown("Children ages")
    for i in range(int(num_kids)):
        age = st.number_input(f"Age of child #{i+1}", min_value=0, max_value=30, value=5, key=f"child_age_{i}")
        child_ages.append(int(age))

S0 = Salary * percentage

# ---------- Run button ----------
if st.button("Run Projection"):
    max_t = int(stop_age - current_age)

    # Phase-Out (with offset) and no-offset baseline for comparison (phase-out P0)
    df_phase, full_cover_t_phase = calculator_phaseout(
        max_t=max_t,
        L=L,
        P0=P0,
        g=g,
        r_avg=r_avg,
        K0=K0,
        si=si,
        S0=S0,
        alpha=1.0
    )

    df_no_offset, _ = calculator_phaseout(
        max_t=max_t,
        L=L,
        P0=P0,
        g=g,
        r_avg=r_avg,
        K0=K0,
        si=si,
        S0=S0,
        alpha=0.0
    )

    # ---------- Compute initial total wealth gap ----------
    # Sum all assets
    total_assets_start = float(property_value) + float(cash) + float(managed_funds) + float(other_assets)

    # Compute total remaining responsibilities for all children (sum over remaining years until 18)
    responsibilities_start = sum([responsibility_for_age(age) for age in child_ages])

    # Total wealth gap (negative if liabilities + responsibilities exceed assets)
    total_wealth_gap = float(K0) + total_assets_start - liabilities - responsibilities_start

    # L for the model is just the gap (funeral/buffer handled inside the calculator)
    L_total_wealth = max(0, -total_wealth_gap)  # only if gap is negative, else 0

    # ---------- Total-Wealth model ----------
    df_total, full_cover_t_total = calculator_total_wealth(
        max_t=int(stop_age - current_age),
        L=L_total_wealth,          # <-- gap only, funeral/buffer handled inside
        P0=P0,
        g=g,
        r_avg=r_avg,
        K0=K0,
        si=si,
        S0=S0,
        property_value=property_value,
        cash=cash,
        managed_funds=managed_funds,
        other_assets=other_assets,
        liabilities=liabilities,
        child_ages=child_ages,
        asset_growth_rate=asset_growth_rate,
        debt_shrink_rate=debt_shrink_rate
    )

    # ---------- Success message restored ----------
    phase_age_msg = None
    total_age_msg = None
    if full_cover_t_phase is not None:
        phase_age_msg = int(current_age + full_cover_t_phase)
    if full_cover_t_total is not None:
        total_age_msg = int(current_age + full_cover_t_total)

    if enable_total_wealth:
        phase_text = f"{phase_age_msg}" if phase_age_msg is not None else "not within projection horizon"
        total_text = f"{total_age_msg}" if total_age_msg is not None else "not within projection horizon"
        st.success(f"Based on your inputs, the client will no longer need life cover at age {phase_text} (Phase-Out) and age {total_text} (Total-Wealth).")
    else:
        phase_text = f"{phase_age_msg}" if phase_age_msg is not None else "not within projection horizon"
        st.success(f"Based on your inputs, the client will no longer need life cover at age {phase_text}.")


    # ---------- Tabs logic ----------
    if enable_total_wealth:
        tab_phase, tab_total = st.tabs(["Phase Out", "Total Wealth"])
    else:
        tab_phase = st.tabs(["Phase Out"])[0]
        tab_total = None

    # ---- Phase Out tab content ----
    with tab_phase:
        st.header("Phase-Out Strategy")
            # ---------- Summary Statistics ----------
        st.subheader("Summary Statistics")

        total_premium_with_offset = df_phase["Premium w/ Offset"].sum()
        total_premium_without_offset = df_no_offset["Baseline Premium"].sum()

        ks_end_with_offset = df_phase["KiwiSaver End Balance"].iloc[-1]
        ks_end_without_offset = df_no_offset["KiwiSaver End Balance"].iloc[-1]

        total_true_cost = ks_end_with_offset - ks_end_without_offset
        per_year_true_cost = total_true_cost / max(1, stop_age - current_age)

        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
        col1.metric("Total Cost of Insurance Premiums (With Offset)", f"${total_premium_with_offset:,.0f}")
        col2.metric("Total Cost of Insurance Premiums (Without Offset)", f"${total_premium_without_offset:,.0f}")
        col3.metric("Total True Cost", f"${total_true_cost:,.0f}")
        col4.metric("True Cost / Year", f"${per_year_true_cost:,.0f}")

        st.dataframe(
            df_phase.style.format({
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

        # Charts compare Phase-Out vs No-offset baseline
        col_a, spacer, col_c = st.columns([1, 0.2, 1])
        with col_a:
            fig_ks = go.Figure()
            fig_ks.add_trace(go.Scatter(
                x=df_phase["year"] + current_age,
                y=df_phase["KiwiSaver End Balance"],
                mode="lines+markers",
                name="KiwiSaver (Phase-Out)",
                line=dict(color=BRAND["yellow"], width=3)
            ))
            fig_ks.add_trace(go.Scatter(
                x=df_no_offset["year"] + current_age,
                y=df_no_offset["KiwiSaver End Balance"],
                mode="lines+markers",
                name="KiwiSaver (No Offset Baseline)",
                line=dict(color=BRAND["dark"], width=3)
            ))
            fig_ks.update_layout(title="KiwiSaver Balance", xaxis_title="Client Age (years)", yaxis_title="Value (NZD)", hovermode="x unified")
            st.plotly_chart(fig_ks, use_container_width=True)

        with col_c:
            fig_prem = go.Figure()
            fig_prem.add_trace(go.Scatter(
                x=df_phase["year"] + current_age,
                y=df_phase["Premium w/ Offset"],
                mode="lines+markers",
                name="Premium (Phase-Out)",
                line=dict(color=BRAND["yellow"], width=3)
            ))
            fig_prem.add_trace(go.Scatter(
                x=df_no_offset["year"] + current_age,
                y=df_no_offset["Baseline Premium"],
                mode="lines+markers",
                name="Premium (No Offset Baseline)",
                line=dict(color=BRAND["dark"], width=3)
            ))
            fig_prem.update_layout(title="Insurance Premiums", xaxis_title="Client Age (years)", yaxis_title="Annual Premium (NZD)", hovermode="x unified")
            st.plotly_chart(fig_prem, use_container_width=True)

        # bottom row
        col_b, spacer_b, col_d = st.columns([1, 0.2, 1])
        with col_b:
            fig_cover = go.Figure()
            fig_cover.add_trace(go.Scatter(
                x=df_phase["year"] + current_age,
                y=df_phase["Effective Cover"],
                mode="lines+markers",
                name="Required Cover (Phase-Out)",
                line=dict(color=BRAND["yellow"], width=3)
            ))
            fig_cover.add_trace(go.Scatter(
                x=df_no_offset["year"] + current_age,
                y=[L] * len(df_no_offset),
                mode="lines+markers",
                name="Required Cover (No Offset Baseline)",
                line=dict(color=BRAND["dark"], width=3)
            ))
            fig_cover.update_layout(title="Required Life Cover Over Time", xaxis_title="Client Age (years)", yaxis_title="Cover (NZD)", hovermode="x unified")
            st.plotly_chart(fig_cover, use_container_width=True)

        with col_d:
            fig_return = go.Figure()
            fig_return.add_trace(go.Scatter(
                x=df_phase["year"] + current_age,
                y=df_phase["Annual Investment Return"],
                mode="lines+markers",
                name="Investment Return (Phase-Out)",
                line=dict(color=BRAND["yellow"], width=3)
            ))
            fig_return.add_trace(go.Scatter(
                x=df_no_offset["year"] + current_age,
                y=df_no_offset["Annual Investment Return"],
                mode="lines+markers",
                name="Investment Return (No Offset Baseline)",
                line=dict(color=BRAND["dark"], width=3)
            ))
            fig_return.update_layout(title="Annual KiwiSaver Investment Return", xaxis_title="Client Age (years)", yaxis_title="Return (NZD)", hovermode="x unified")
            st.plotly_chart(fig_return, use_container_width=True)

    # ---- Total Wealth tab content (only table, no plots) ----
    if tab_total is not None:
        with tab_total:
            st.header("Total-Wealth Strategy")
            st.subheader("Summary")
            starting_cover = df_total.iloc[0]["Required Cover"]

            col1, col2 = st.columns([2, 2])
            col1.metric("Starting Required Life Cover", f"${starting_cover:,.0f}")
            col2.metric("Phase Out Length (Years)", f"{full_cover_t_total:.0f}")
            st.dataframe(
                df_total.style.format({
                    "KiwiSaver Start Balance": "{:,.2f}",
                    "Total Assets Start": "{:,.2f}",
                    "Total Liabilities Start": "{:,.2f}",
                    "Responsibilities Start": "{:,.2f}",
                    "Baseline Premium": "{:,.2f}",
                    "Required Cover": "{:,.2f}",
                    "Premium w/ Offset": "{:,.2f}",
                    "Premium Saving": "{:,.2f}",
                    "Voluntary Contribution": "{:,.2f}",
                    "Annual Salary Contribution": "{:,.2f}",
                    "Annual Investment Return": "{:,.2f}",
                    "KiwiSaver End Balance": "{:,.2f}",
                    "Total Assets": "{:,.2f}",
                    "Total Liabilities": "{:,.2f}",
                    "Responsibilities": "{:,.2f}"
                }),
                hide_index=True
            )



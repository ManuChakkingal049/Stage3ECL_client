# streamlit_app.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.title("ECL Calculator")

# User Inputs
with st.sidebar:
    st.header("Loan & Collateral Info")
    total_os = st.slider("Total Outstanding (TOTAL OS)", 0.0, 10000000.0, 100000.0, step=1000.0)
    collateral_hc = st.slider("Collateral after H.C", 0.0, 10000000.0, 50000.0, step=1000.0)
    ecf_dcf_cover = st.slider("Unsecured Portion Covered by ECF/DCF", 0.0, 10000000.0, 10000.0, step=1000.0)

    st.header("Dates")
    classification_date_str = st.date_input("Classification Date", datetime.today() - timedelta(days=1500)).strftime("%d-%b-%Y")
    crms_issue_date_str = st.date_input("CRMS Issue Date", datetime.today() - timedelta(days=2000)).strftime("%d-%b-%Y")
    run_date_str = st.date_input("Run Date", datetime.today()).strftime("%d-%b-%Y")

# Utility Functions
def convert_to_date(date_string):
    return datetime.strptime(date_string, "%d-%b-%Y")

def calculate_years_since_npl(classification_date, run_date):
    return (run_date - classification_date).days / 365

# Computations
run_date = convert_to_date(run_date_str)
classification_date = convert_to_date(classification_date_str)
crms_issue_date = convert_to_date(crms_issue_date_str)

years_since_npl = calculate_years_since_npl(classification_date, run_date)
unsecured_whole = max(total_os - collateral_hc, 0)
net_secured = min(collateral_hc, total_os)
net_unsecured = max(unsecured_whole - ecf_dcf_cover, 0)

# Provisions
min_nusp_a = net_unsecured
four_years_after_crms = crms_issue_date + timedelta(days=4 * 365)
min_nusp_b = unsecured_whole * (1 if run_date >= four_years_after_crms else 0.25)
provision_unsecured = max(min_nusp_a, min_nusp_b)
min_prov_secured = net_secured * 0.25 if years_since_npl > 4 else 0
final_required_provision = provision_unsecured + min_prov_secured

# Output
st.header("📊 Results")
st.write(f"Years Since NPL: `{years_since_npl:.2f}`")
st.write(f"Unsecured Portion (whole): `{unsecured_whole:,.2f}`")
st.write(f"NET Secured Portion: `{net_secured:,.2f}`")
st.write(f"NET Unsecured Portion (NUSP): `{net_unsecured:,.2f}`")
st.write(f"Min Provision on NUSP (A): `{min_nusp_a:,.2f}`")
st.write(f"Min Provision on NUSP (B): `{min_nusp_b:,.2f}`")
st.write(f"Provision - Unsecured: `{provision_unsecured:,.2f}`")
st.write(f"Provision - Secured: `{min_prov_secured:,.2f}`")

st.success(f"✅ FINAL Required Provision / ECL (CRMS): `{final_required_provision:,.2f}`")

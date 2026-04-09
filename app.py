import streamlit as st
import pandas as pd
import time
import random
import plotly.express as px

# --- 1. THE RECOVERY OPS "BRAIN" ---
# This simulates the reputation check by looking for 'Risk Keywords'
# In a real tool, this would be the text pulled from a search
def get_simulated_reputation(name):
    # This list allows you to 'rig' the demo for specific results
    high_risk_firms = ["Frederick J. Hanna", "Forster & Garbus", "Weltman Weinberg"]
    caution_firms = ["Blitt and Gaines", "Aldridge Pite Haan"]
    
    # Simulate a small delay for 'processing'
    time.sleep(random.uniform(0.5, 1.5))
    
    if any(firm in name for firm in high_risk_firms):
        return "🔴 HIGH RISK", -0.75, "Consumer complaints regarding aggressive tactics found."
    elif any(firm in name for firm in caution_firms):
        return "🟡 CAUTION", 0.0, "Mixed professional reviews; monitoring recommended."
    else:
        return "🟢 LOW RISK", 0.82, "Maintains high professional standards and compliance."

# --- 2. UI DESIGN ---
st.set_page_config(page_title="Recovery Ops Auditor", layout="wide")
st.title("Recovery Operations: Law Firm Reputation Auditor 🛡️")
st.markdown("Automated panel monitoring for Reputational Risk and Compliance.")

st.sidebar.header("Data Management")
uploaded_file = st.sidebar.file_uploader("Upload Vendor CSV", type=["csv"])

if not uploaded_file:
    df = pd.DataFrame({
        "vendor_name": ["Weltman Weinberg & Reis", "Pressler Felt & Warshaw", "Zwicker & Associates", "Blitt and Gaines", "Frederick J. Hanna & Associates", "Aldridge Pite Haan", "Forster & Garbus"],
        "city": ["Cleveland", "Parsippany", "Andover", "Vernon Hills", "Marietta", "Atlanta", "Commack"],
        "state": ["OH", "NJ", "MA", "IL", "GA", "GA", "NY"]
    })
else:
    df = pd.read_csv(uploaded_file)

# --- 3. AUDIT EXECUTION ---
if st.button("Run Professional Audit"):
    results = []
    progress_bar = st.progress(0)
    
    for index, row in df.iterrows():
        name = row['vendor_name']
        location = f"{row['city']}, {row['state']}"
        st.write(f"Auditing: **{name}**...")
        
        status, score, findings = get_simulated_reputation(name)
        
        results.append({
            "Vendor": name, 
            "Location": location,
            "Status": status, 
            "Risk Score": score,
            "Findings": findings
        })
        progress_bar.progress((index + 1) / len(df))
    
    # --- 4. EXECUTIVE DASHBOARD ---
    st.success("Panel Audit Complete!")
    res_df = pd.DataFrame(results)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Risk Distribution")
        fig = px.pie(res_df, names='Status', color='Status',
                     color_discrete_map={
                         '🔴 HIGH RISK': '#ff4b4b', 
                         '🟢 LOW RISK': '#00cc96', 
                         '🟡 CAUTION': '#ffff00'
                     })
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Detailed Audit Log")
        st.dataframe(res_df, use_container_width=True, hide_index=True)

    st.download_button("Download Compliance Report", res_df.to_csv(index=False), "reputation_report.csv")

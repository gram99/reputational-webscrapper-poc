import streamlit as st
import pandas as pd
import time
import random
import requests
from bs4 import BeautifulSoup # Ensure 'beautifulsoup4' is in requirements.txt
import plotly.express as px
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# --- 1. ANALYSIS ENGINE ---
analyzer = SentimentIntensityAnalyzer()

def get_recovery_metrics(text):
    """Calculates risk based on sentiment and industry-specific red flags."""
    score = analyzer.polarity_scores(text)['compound']
    
    # Custom 'Red Flag' detection for debt collection
    red_flags = ["harassment", "aggressive", "unethical", "lawsuit", "illegal", "fined", "violations"]
    if any(word in text.lower() for word in red_flags):
        score -= 0.2 # Heavily penalize industry red flags

    if score <= -0.1:
        return "🔴 HIGH RISK", round(score, 2), "Terminate/Audit"
    elif score >= 0.1:
        return "🟢 LOW RISK", round(score, 2), "Expand/Onboard"
    else:
        return "🟡 CAUTION", round(score, 2), "Monitor/Restructure"

def get_search_data(name, city, state):
    """Fetches real text snippets from the web for accurate analysis."""
    query = f"{name} {city} {state} debt collection complaints reviews news"
    # Using DuckDuckGo HTML for high reliability on cloud servers
    url = f"https://duckduckgo.com{query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"}
    
    try:
        response = requests.get(url, headers=headers, timeout=12)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract the actual text descriptions from the search results
            snippets =]
            if snippets:
                return " ".join(snippets)
            return f"General search for {name} returned no specific negative or positive narratives."
        return "Connection successful but access to snippets was limited."
    except Exception as e:
        return f"Audit interrupted by connection timeout."

# --- 2. EXECUTIVE UI ---
st.set_page_config(page_title="Recovery Ops Auditor", layout="wide")
st.title("Recovery Operations: Law Firm Reputation Auditor 🛡️")
st.markdown("Automated panel monitoring for Reputational Risk and Compliance.")

st.sidebar.header("Upload Vendor List")
uploaded_file = st.sidebar.file_uploader("Upload CSV (vendor_name, city, state)", type=["csv"])

if not uploaded_file:
    # Industry standard sample for testing
    df = pd.DataFrame({
        "vendor_name": ["Weltman Weinberg & Reis", "Frederick J. Hanna & Assoc", "Zwicker & Associates"],
        "city": ["Cleveland", "Marietta", "Andover"],
        "state": ["OH", "GA", "MA"]
    })
else:
    df = pd.read_csv(uploaded_file)

# --- 3. AUDIT EXECUTION ---
if st.button("Launch Professional Panel Audit") and not df.empty:
    results = []
    
    with st.spinner("Executing live reputation scan..."):
        for index, row in df.iterrows():
            name, city, state = row['vendor_name'], row['city'], row['state']
            
            # 1. Fetch live snippets
            findings = get_search_data(name, city, state)
            
            # 2. Analyze sentiment + red flags
            risk_label, score, rec = get_recovery_metrics(findings)
            
            results.append({
                "Firm Name": name,
                "Location": f"{city}, {state}",
                "Reputation Status": risk_label,
                "Risk Score": score,
                "Ops Recommendation": rec,
                "Audit Snippet": findings[:150] + "..." # Display a preview in the table
            })
            time.sleep(random.uniform(1.5, 3)) # Human-like pacing
    
    # --- 4. EXECUTIVE DASHBOARD ---
    res_df = pd.DataFrame(results)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Firms Audited", len(res_df))
    c2.metric("Terminate/Audit (Risk)", len(res_df[res_df['Ops Recommendation'] == "Terminate/Audit"]))
    c3.metric("Expand/Onboard (Growth)", len(res_df[res_df['Ops Recommendation'] == "Expand/Onboard"]))

    st.divider()

    col_chart, col_table = st.columns([1, 2])
    with col_chart:
        st.subheader("Contractual Risk Mix")
        fig = px.pie(res_df, names='Reputation Status', color='Reputation Status',
                     color_discrete_map={'🔴 HIGH RISK': '#ff4b4b', '🟢 LOW RISK': '#00cc96', '🟡 CAUTION': '#636efa'})
        st.plotly_chart(fig, use_container_width=True)

    with col_table:
        st.subheader("Actionable Audit Log")
        st.dataframe(res_df, use_container_width=True, hide_index=True)

    st.download_button("📩 Download Professional Audit Report", res_df.to_csv(index=False), "recovery_audit_report.csv")

import streamlit as st
import pandas as pd
import time
import random
import plotly.express as px
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# --- 1. SETUP & ANALYSIS ---
analyzer = SentimentIntensityAnalyzer()

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    try:
        service = Service("/usr/bin/chromedriver")
        return webdriver.Chrome(service=service, options=chrome_options)
    except Exception:
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def get_recovery_metrics(text):
    score = analyzer.polarity_scores(text)['compound']
    if score <= -0.05:
        return "🔴 HIGH RISK", score, "Terminate/Audit"
    elif score >= 0.05:
        return "🟢 LOW RISK", score, "Expand/Onboard"
    else:
        return "🟡 CAUTION", score, "Monitor/Restructure"

# --- 2. UI ---
st.set_page_config(page_title="Recovery Ops - Reputation Audit", layout="wide")
st.title("Recovery Operations: Law Firm Reputation Auditor 🛡️")
st.markdown("Automated risk assessment for evaluating current vendor panels and identifying potential replacements.")

st.sidebar.header("Upload Vendor List")
uploaded_file = st.sidebar.file_uploader("Upload CSV (Required columns: vendor_name, city, state)", type=["csv"])

if not uploaded_file:
    # Creating a dummy template for first-time use
    df = pd.DataFrame({
        "vendor_name": ["Weltman Weinberg & Reis", "Frederick J. Hanna & Assoc", "Zwicker & Associates"],
        "city": ["Cleveland", "Marietta", "Andover"],
        "state": ["OH", "GA", "MA"]
    })
    st.sidebar.info("Using sample data. Upload a custom CSV for full panel audit.")
else:
    df = pd.read_csv(uploaded_file)

# --- 3. AUDIT ENGINE ---
if st.button("Start Vendor Panel Audit") and not df.empty:
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    driver = get_driver()
    
    for index, row in df.iterrows():
        name, city, state = row['vendor_name'], row['city'], row['state']
        status_text.text(f"Auditing: {name} ({city}, {state})")
        
        # Specific search string for Recovery Managers
        search_query = f"{name} {city} {state} collection complaints"
        
        try:
            driver.get(f"https://google.com{search_query.replace(' ', '+')}")
            time.sleep(random.uniform(4, 7))
            
            page_title = driver.title
            risk_label, score, rec = get_recovery_metrics(page_title)
            
            results.append({
                "Firm Name": name,
                "Location": f"{city}, {state}",
                "Reputation Status": risk_label,
                "Risk Score": score,
                "Ops Recommendation": rec,
                "Findings": f"Public Sentiment: {page_title}"
            })
        except:
            results.append({
                "Firm Name": name, "Location": f"{city}, {state}",
                "Reputation Status": "⚪ ERROR", "Risk Score": 0,
                "Ops Recommendation": "Retry Connection", "Findings": "Timeout"
            })
        
        progress_bar.progress((index + 1) / len(df))
    
    driver.quit()
    
    # --- 4. EXECUTIVE DASHBOARD ---
    st.success("Panel Audit Complete!")
    res_df = pd.DataFrame(results)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Firms Checked", len(res_df))
    c2.metric("High Reputation Risks", len(res_df[res_df['Ops Recommendation'] == "Terminate/Audit"]))
    c3.metric("Onboarding Candidates", len(res_df[res_df['Ops Recommendation'] == "Expand/Onboard"]))

    st.divider()

    col_chart, col_table = st.columns([1, 2])
    
    with col_chart:
        st.subheader("Contractual Risk Mix")
        fig = px.pie(res_df, names='Reputation Status', color='Reputation Status',
                     color_discrete_map={'🔴 HIGH RISK': '#ff4b4b', '🟢 LOW RISK': '#00cc96', '🟡 CAUTION': '#636efa'})
        st.plotly_chart(fig, use_container_width=True)

    with col_table:
        st.subheader("Actionable Vendor Insights")
        st.dataframe(res_df, use_container_width=True, hide_index=True)

    st.download_button("Download Compliance Audit Report", res_df.to_csv(index=False), "recovery_audit_report.csv")

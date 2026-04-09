import streamlit as st
import pandas as pd
import time
import random
import plotly.express as px
from urllib.parse import urlparse # Built-in, no requirement change needed
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
        # Standard path for Streamlit Cloud
        service = Service("/usr/bin/chromedriver")
        return webdriver.Chrome(service=service, options=chrome_options)
    except:
        # Local computer fallback
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def analyze_reputation(text):
    score = analyzer.polarity_scores(text)['compound']
    # Professional 3-way risk logic
    if score <= -0.05: 
        return "🔴 HIGH RISK", score
    elif score >= 0.05: 
        return "🟢 LOW RISK", score
    else: 
        return "🟡 CAUTION", score

# --- 2. UI DESIGN ---
st.set_page_config(page_title="Recovery Ops Auditor", layout="wide")
st.title("Recovery Operations: Law Firm Reputation Auditor 🛡️")

st.sidebar.header("Data Management")
uploaded_file = st.sidebar.file_uploader("Upload Vendor CSV (vendor_name, city, state)", type=["csv"])

if not uploaded_file:
    try:
        df = pd.read_csv("vendors.csv")
    except:
        df = pd.DataFrame(columns=["vendor_name", "city", "state"])
else:
    df = pd.read_csv(uploaded_file)

# --- 3. AUDIT EXECUTION ---
if st.button("Run Scraper Audit") and not df.empty:
    results = []
    progress_bar = st.progress(0)
    
    driver = get_driver()
    
    for index, row in df.iterrows():
        name = f"{row['vendor_name']} {row['city']} {row['state']}"
        st.write(f"Auditing: **{name}**...")
        
        # Using a direct search URL
        search_url = f"https://google.com{name.replace(' ', '+')}+complaints"
        
        try:
            driver.get(search_url)
            time.sleep(random.uniform(4, 6)) # Human-like pacing for VPN/Firewall stability
            
            page_title = driver.title
            risk_label, score = analyze_reputation(page_title)
            
            # Identify the site name (Source) from the URL
            source_site = urlparse(driver.current_url).netloc
            
            results.append({
                "Vendor": row['vendor_name'], 
                "Location": f"{row['city']}, {row['state']}",
                "Status": risk_label, 
                "Source Site": source_site if source_site else "google.com",
                "Findings": page_title
            })
        except:
            # Fallback if connection is blocked
            results.append({
                "Vendor": row['vendor_name'], 
                "Location": f"{row['city']}, {row['state']}",
                "Status": "⚪ ERROR", 
                "Source Site": "Connection Blocked",
                "Findings": "Unable to reach search provider"
            })
        
        progress_bar.progress((index + 1) / len(df))
    
    driver.quit()
    
    # --- 4. EXECUTIVE DASHBOARD ---
    st.success("Audit Complete!")
    res_df = pd.DataFrame(results)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Risk Distribution")
        fig = px.pie(res_df, names='Status', color='Status',
                     color_discrete_map={
                         '🔴 HIGH RISK': '#ff4b4b', 
                         '🟢 LOW RISK': '#00cc96', 
                         '🟡 CAUTION': '#ffff00', # Bright Yellow
                         '⚪ ERROR': '#808080'
                     })
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Detailed Audit Log")
        # hide_index removes the far-left numbering
        st.dataframe(res_df, use_container_width=True, hide_index=True)

    csv_data = res_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Compliance Report", csv_data, "reputation_report.csv", "text/csv")

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

# --- 1. SETUP ---
analyzer = SentimentIntensityAnalyzer()

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    try:
        service = Service("/usr/bin/chromedriver")
        return webdriver.Chrome(service=service, options=chrome_options)
    except:
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def analyze_reputation(text):
    score = analyzer.polarity_scores(text)['compound']
    # FIXED LOGIC: Three-way split for High, Low, and Caution
    if score <= -0.05: 
        return "🔴 HIGH RISK", score
    elif score >= 0.05: 
        return "🟢 LOW RISK", score
    else: 
        return "🟡 CAUTION", score

# --- 2. UI ---
st.set_page_config(page_title="Reputation Guard POC", layout="wide")
st.title("Recovery Operations: Law Firm Reputation Auditor 🛡️")

st.sidebar.header("Data Management")
uploaded_file = st.sidebar.file_uploader("Upload Vendor CSV", type=["csv"])

if not uploaded_file:
    try:
        df = pd.read_csv("vendors.csv")
    except:
        df = pd.DataFrame(columns=["vendor_name", "city", "state"])
else:
    df = pd.read_csv(uploaded_file)

# --- 3. THE ACTION ---
if st.button("Run Scraper") and not df.empty:
    results = []
    progress_bar = st.progress(0)
    
    driver = get_driver()
    
    for index, row in df.iterrows():
        name = f"{row['vendor_name']} {row['city']} {row['state']}"
        st.write(f"Checking: **{name}**...")
        
        # Simple Google Search URL
        url = f"https://google.com{name.replace(' ', '+')}+complaints"
        
        try:
            driver.get(url)
            time.sleep(random.uniform(3, 5))
            
            data = driver.title
            risk_label, score = analyze_reputation(data)
            
            results.append({
                "Vendor": row['vendor_name'], 
                "Location": f"{row['city']}, {row['state']}",
                "Status": risk_label, 
                "Findings": data
            })
        except:
            results.append({
                "Vendor": row['vendor_name'], 
                "Location": f"{row['city']}, {row['state']}",
                "Status": "⚪ ERROR", 
                "Findings": "Connection Fail"
            })
        
        progress_bar.progress((index + 1) / len(df))
    
    driver.quit()
    
    # --- 4. RESULTS DISPLAY ---
    st.success("Complete!")
    res_df = pd.DataFrame(results)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Risk Distribution")
        # Color map updated for Yellow/Caution
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
        st.dataframe(res_df, use_container_width=True, hide_index=True)

    csv = res_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Report", csv, "report.csv", "text/csv")

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

# --- 1. SETUP & ANALYSIS LOGIC ---
analyzer = SentimentIntensityAnalyzer()

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    ]
    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
    
    try:
        service = Service("/usr/bin/chromedriver")
        return webdriver.Chrome(service=service, options=chrome_options)
    except Exception:
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def analyze_text(text):
    score = analyzer.polarity_scores(text)['compound']
    status = "🔴 HIGH" if score <= -0.05 else "🟢 LOW" if score >= 0.05 else "🟡 NEUTRAL"
    return status, score

# --- 2. USER INTERFACE ---
st.set_page_config(page_title="Reputational Risk Auditor", layout="wide")
st.title("Bulk Reputational Risk Auditor 📋")

st.sidebar.header("Data Management")
uploaded_file = st.sidebar.file_uploader("Upload Vendor CSV", type=["csv"])

if not uploaded_file:
    try:
        df = pd.read_csv("vendors.csv")
    except:
        df = pd.DataFrame(columns=["vendor_name"])
else:
    df = pd.read_csv(uploaded_file)

# --- 3. EXECUTION ---
if st.button("Start Bulk Audit") and not df.empty:
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    driver = get_driver()
    
    for index, row in df.iterrows():
        name = row['vendor_name']
        wait_time = random.uniform(3, 5)
        status_text.text(f"Auditing: {name} ({index+1}/{len(df)})")
        time.sleep(wait_time)
        
        # Note: Replace this with driver.get() for live scraping later
        simulated_text = f"Public report for {name}: Recurring consumer feedback mentions lack of clarity and aggressive tactics."
        
        risk_label, score = analyze_text(simulated_text)
        results.append({
            "Vendor": name, 
            "Risk Level": risk_label, 
            "Sentiment Score": score, 
            "Snippet Found": simulated_text
        })
        
        progress_bar.progress((index + 1) / len(df))
    
    driver.quit()
    
    # --- 4. RESULTS DISPLAY ---
    st.success("Audit Complete!")
    results_df = pd.DataFrame(results)
    
    # Dashboard Layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Risk Distribution")
        # Color-coded Pie Chart
        fig = px.pie(
            results_df, 
            names='Risk Level', 
            color='Risk Level',
            color_discrete_map={
                '🔴 HIGH': '#ff4b4b', 
                '🟢 LOW': '#00cc96', 
                '🟡 NEUTRAL': '#636efa'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Detailed Audit Log")
        # FIX: hide_index=True removes the far-left numbering
        st.dataframe(results_df, use_container_width=True, hide_index=True)
    
    csv_report = results_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Full Risk Report", csv_report, "reputation_report.csv", "text/csv")

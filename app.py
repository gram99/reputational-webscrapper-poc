import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# --- 1. CORE LOGIC ---
analyzer = SentimentIntensityAnalyzer()

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Try cloud driver first, then local manager
    try:
        return webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=options)
    except:
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def get_risk(text):
    score = analyzer.polarity_scores(text)['compound']
    if score <= -0.05: return "🔴 HIGH", score
    return "🟢 LOW", score

# --- 2. UI ---
st.set_page_config(layout="wide")
st.title("Reputational Risk Scraper POC 🛡️")

# Load CSV from your repo
try:
    df = pd.read_csv("vendors.csv")
    st.write("Using default `vendors.csv` from repository.")
except:
    st.error("Missing vendors.csv file.")
    df = pd.DataFrame()

if st.button("Run Scraper") and not df.empty:
    results = []
    driver = get_driver()
    
    for name in df['vendor_name']:
        st.write(f"Checking: {name}...")
        
        # Simple search URL
        url = f"https://google.com{name}+reviews"
        
        try:
            driver.get(url)
            time.sleep(3) # Simple wait
            
            # Just grab the title of the search results page
            data = driver.title
            
            risk_label, score = get_risk(data)
            results.append({"Vendor": name, "Risk": risk_label, "Score": score, "Findings": data})
        except:
            results.append({"Vendor": name, "Risk": "⚪ ERROR", "Score": 0, "Findings": "Connection Fail"})

    driver.quit()
    
    # --- 3. DISPLAY ---
    st.success("Complete!")
    res_df = pd.DataFrame(results)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Detailed Audit Log")
        st.dataframe(res_df)
    with col2:
        st.subheader("Download Report")
        csv = res_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "report.csv")

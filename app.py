import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# --- SETUP ---
analyzer = SentimentIntensityAnalyzer()

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def analyze_text(text):
    score = analyzer.polarity_scores(text)['compound']
    status = "🔴 HIGH" if score <= -0.05 else "🟢 LOW" if score >= 0.05 else "🟡 NEUTRAL"
    return status, score

# --- UI ---
st.set_page_config(page_title="Bulk Vendor Auditor", layout="wide")
st.title("Bulk Reputational Risk Auditor 📋")

# 1. Upload or Load CSV
uploaded_file = st.sidebar.file_uploader("Upload Vendor CSV", type=["csv"])
if not uploaded_file:
    st.info("Upload a CSV with a 'vendor_name' column to begin, or use the default 'vendors.csv' in the repo.")
    # Fallback to a local file if it exists
    try:
        df = pd.read_csv("vendors.csv")
    except:
        df = pd.DataFrame(columns=["vendor_name"])
else:
    df = pd.read_csv(uploaded_file)

# 2. Run Bulk Analysis
if st.button("Start Bulk Audit") and not df.empty:
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    driver = get_driver()
    
    for index, row in df.iterrows():
        name = row['vendor_name']
        status_text.text(f"Auditing: {name} ({index+1}/{len(df)})")
        
        # --- SIMULATED SCRAPE (Replace with real URL logic) ---
        # In a real scenario: driver.get(f"https://google.com{name}+reviews")
        # For this POC, we'll simulate a finding
        simulated_text = f"Review for {name}: They were very aggressive and didn't follow FDCPA guidelines."
        
        risk_label, score = analyze_text(simulated_text)
        results.append({"Vendor": name, "Risk Level": risk_label, "Score": score, "Snippet": simulated_text})
        
        # Update progress
        progress_bar.progress((index + 1) / len(df))
        time.sleep(1) # Gentle on servers
    
    driver.quit()
    
    # 3. Display Results
    results_df = pd.DataFrame(results)
    st.success("Audit Complete!")
    st.dataframe(results_df, use_container_width=True)
    
    # 4. Download Results
    csv_output = results_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Risk Report", data=csv_output, file_name="reputation_report.csv", mime="text/csv")

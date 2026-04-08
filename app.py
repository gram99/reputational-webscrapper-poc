import streamlit as st
import pandas as pd
import time
import random
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
    
    # Rotate User-Agents to look like different browsers
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    ]
    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
    
    # FIX: Point to the system-installed driver on Streamlit Cloud
    try:
        # Standard path for chromium-driver in the Streamlit Linux environment
        service = Service("/usr/bin/chromedriver")
        return webdriver.Chrome(service=service, options=chrome_options)
    except Exception:
        # Fallback for local testing on your personal computer
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def analyze_text(text):
    score = analyzer.polarity_scores(text)['compound']
    status = "🔴 HIGH" if score <= -0.05 else "🟢 LOW" if score >= 0.05 else "🟡 NEUTRAL"
    return status, score

# --- 2. USER INTERFACE ---
st.set_page_config(page_title="Reputational Risk Auditor", layout="wide")
st.title("Bulk Reputational Risk Auditor 📋")

# Sidebar for CSV Handling
st.sidebar.header("Data Management")
uploaded_file = st.sidebar.file_uploader("Upload Vendor CSV", type=["csv"])

if not uploaded_file:
    st.info("Using default 'vendors.csv' from repository. Upload a new one in the sidebar to change lists.")
    try:
        df = pd.read_csv("vendors.csv")
    except:
        st.error("Could not find 'vendors.csv'. Please create it in your repo.")
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
        
        # RANDOM DELAY: Wait between 3 to 6 seconds per vendor
        wait_time = random.uniform(3, 6)
        status_text.text(f"Waiting {round(wait_time, 1)}s... Next: {name} ({index+1}/{len(df)})")
        time.sleep(wait_time)
        
        # --- SCRAPE LOGIC ---
        # Note: Replace this simulation with driver.get() for live scraping
        simulated_text = f"Review for {name}: Consumer complaints regarding lack of transparency and aggressive calls."
        
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
    
    # Display table
    st.dataframe(results_df, use_container_width=True)
    
    # Provide download option
    csv_report = results_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Full Risk Report",
        data=csv_report,
        file_name="reputation_risk_audit.csv",
        mime="text/csv"
    )

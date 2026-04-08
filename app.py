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

# --- 1. THE BRAINS ---
analyzer = SentimentIntensityAnalyzer()

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    # Try the cloud path first, then local fallback
    try:
        service = Service("/usr/bin/chromedriver")
        return webdriver.Chrome(service=service, options=chrome_options)
    except:
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def analyze_reputation(text):
    score = analyzer.polarity_scores(text)['compound']
    if score <= -0.05: return "🔴 HIGH", score
    elif score >= 0.05: return "🟢 LOW", score
    else: return "🟡 NEUTRAL", score

# --- 2. THE UI ---
st.set_page_config(page_title="Reputation Guard POC", layout="wide")
st.title("Reputational Risk Scraper POC 🛡️")

# CSV Management
st.sidebar.header("Data Upload")
uploaded_file = st.sidebar.file_uploader("Upload your Vendor CSV", type=["csv"])

if not uploaded_file:
    st.info("Using default 'vendors.csv' from your repository.")
    try:
        df = pd.read_csv("vendors.csv")
    except:
        df = pd.DataFrame(columns=["vendor_name"])
else:
    df = pd.read_csv(uploaded_file)

# --- 3. THE ACTION ---
if st.button("Run Scraper") and not df.empty:
    results = []
    progress_bar = st.progress(0)
    
    driver = get_driver()
    
    for index, row in df.iterrows():
        name = row['vendor_name']
        st.write(f"🔍 Checking: **{name}**...")
        
        # We search Google but don't need an API key 
        # because the 'driver' acts like a real person browsing.
        search_url = f"https://google.com{name}+complaints+reviews"
        
        try:
            driver.get(search_url)
            time.sleep(random.uniform(3, 5)) # Be human-like
            
            # Grab the title and some page text for the analysis
            findings = f"Public records check for {name}: " + driver.title
            
            risk_label, score = analyze_reputation(findings)
            results.append({"Vendor": name, "Risk Level": risk_label, "Sentiment Score": score, "Findings": findings})
        except Exception as e:
            results.append({"Vendor": name, "Risk Level": "⚪ ERROR", "Sentiment Score": 0, "Findings": "Could not reach site."})
        
        progress_bar.progress((index + 1) / len(df))
    
    driver.quit()
    
    # --- 4. THE RESULTS ---
    st.success("Scrape Complete!")
    res_df = pd.DataFrame(results)

    # Visuals
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Risk Mix")
        fig = px.pie(res_df, names='Risk Level', color='Risk Level',
                     color_discrete_map={'🔴 HIGH':'#ff4b4b', '🟢 LOW':'#00cc96', '🟡 NEUTRAL':'#636efa', '⚪ ERROR':'#808080'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Detailed Audit Log")
        st.dataframe(res_df, use_container_width=True)

    # Download button
    csv = res_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Report", csv, "reputation_report.csv", "text/csv")

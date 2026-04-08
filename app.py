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
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    
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

# --- 2. UI ---
st.set_page_config(page_title="Reputation Guard POC", layout="wide")
st.title("Reputational Risk Scraper POC 🛡️")

st.sidebar.header("Data Upload")
uploaded_file = st.sidebar.file_uploader("Upload your Vendor CSV", type=["csv"])

# Logic to load the CSV
if not uploaded_file:
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
        st.write(f"🔍 Auditing: **{name}**...")
        
        # We use a direct DuckDuckGo search which is easier for cloud servers
        search_url = f"https://duckduckgo.com{name.replace(' ', '+')}+complaints"
        
        try:
            driver.get(search_url)
            time.sleep(random.uniform(3, 5)) 
            
            # Get the page title
            page_info = driver.title
            
            risk_label, score = analyze_reputation(page_info)
            results.append({
                "Vendor": name, 
                "Risk Level": risk_label, 
                "Score": score, 
                "Findings": f"Public Record: {page_info}"
            })
        except Exception as e:
            results.append({
                "Vendor": name, 
                "Risk Level": "⚪ ERROR", 
                "Score": 0, 
                "Findings": "Connection Reset by Server"
            })
        
        progress_bar.progress((index + 1) / len(df))
    
    driver.quit()
    
    # --- 4. RESULTS (FIXED COLUMNS) ---
    st.success("Scrape Complete!")
    res_df = pd.DataFrame(results)

    # Specify '2' in st.columns to fix the TypeError
    col1, col2 = st.columns(2) 
    
    with col1:
        st.subheader("Risk Mix")
        fig = px.pie(res_df, names='Risk Level', color='Risk Level',
                     color_discrete_map={'🔴 HIGH':'#ff4b4b', '🟢 LOW':'#00cc96', '🟡 NEUTRAL':'#636efa', '⚪ ERROR':'#808080'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Detailed Audit Log")
        st.dataframe(res_df, use_container_width=True)

    csv = res_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Report", csv, "reputation_report.csv")

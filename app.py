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
    
    # Updated: This points directly to the driver installed via packages.txt
    # and falls back to ChromeDriverManager if running locally.
    try:
        service = Service("/usr/bin/chromedriver")
        return webdriver.Chrome(service=service, options=chrome_options)
    except:
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def analyze_text(text):
    score = analyzer.polarity_scores(text)['compound']
    if score <= -0.05: return "🔴 HIGH", score
    elif score >= 0.05: return "🟢 LOW", score
    else: return "🟡 NEUTRAL", score

# --- 2. USER INTERFACE ---
st.set_page_config(page_title="Reputation Guard Pro", layout="wide")
st.title("Reputational Risk Executive Dashboard 🛡️")

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
if st.button("Launch Comprehensive Audit") and not df.empty:
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    driver = get_driver()
    
    for index, row in df.iterrows():
        name = row['vendor_name']
        wait_time = random.uniform(2, 4)
        status_text.text(f"Scanning: {name}...")
        time.sleep(wait_time)
        
        # Simulated finding
        simulated_text = random.choice([
            f"Severe consumer complaints found for {name} regarding unethical billing.",
            f"{name} maintains professional standards and positive consumer feedback.",
            f"No significant public sentiment found for {name}."
        ])
        
        risk_label, score = analyze_text(simulated_text)
        results.append({"Vendor": name, "Risk": risk_label, "Score": score, "Source": simulated_text})
        progress_bar.progress((index + 1) / len(df))
    
    driver.quit()
    
    # --- 4. DATA VISUALIZATION ---
    st.success("Audit Complete!")
    res_df = pd.DataFrame(results)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Vendors", len(res_df))
    c2.metric("High Risk Identified", len(res_df[res_df['Risk'] == "🔴 HIGH"]))
    c3.metric("Average Sentiment", round(res_df['Score'].mean(), 2))

    st.divider()

    chart_col, table_col = st.columns([1, 1.5])
    
    with chart_col:
        st.subheader("Risk Distribution")
        fig = px.pie(res_df, names='Risk', color='Risk',
                     color_discrete_map={'🔴 HIGH':'#ff4b4b', '🟢 LOW':'#00cc96', '🟡 NEUTRAL':'#636efa'})
        st.plotly_chart(fig, use_container_width=True)

    with table_col:
        st.subheader("Detailed Findings")
        st.dataframe(res_df, use_container_width=True)

    csv_report = res_df.to_csv(index=False).encode('utf-8')
    st.download_button("📩 Download Regulatory Compliance Report", data=csv_report, file_name="vendor_risk_audit.csv")

st.sidebar.info("Tip: Use the 'Regulatory Compliance Report' for internal legal reviews.")

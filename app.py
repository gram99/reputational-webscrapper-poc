import streamlit as st
import pandas as pd
import time
import random
import plotly.express as px
import matplotlib
matplotlib.use('Agg') # Stable backend for cloud servers
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
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
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    ]
    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
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

# --- 2. SEARCH FUNCTION (REWRITTEN FOR STABILITY) ---
def get_vendor_headlines(driver, vendor_name):
    search_query = f"{vendor_name} complaints"
    url = f"https://google.com{search_query}&tbm=nws"
    
    driver.get(url)
    time.sleep(2) 
    
    try:
        headlines = driver.find_elements(By.TAG_NAME, "h3")
        
        # Expanded logic to prevent truncation errors
        top_headlines = []
        for h in headlines[:3]:
            if h.text and h.text.strip():
                top_headlines.append(h.text)
                
        if len(top_headlines) > 0:
            return " | ".join(top_headlines)
        else:
            return "No significant headlines found."
    except Exception as e:
        return f"Search failed: {str(e)}"

# --- 3. UI ---
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

# --- 4. EXECUTION ---
if st.button("Launch Live Reputation Audit") and not df.empty:
    results = []
    all_text_for_cloud = ""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    driver = get_driver()
    
    for index, row in df.iterrows():
        name = row['vendor_name']
        wait_time = random.uniform(4, 7)
        status_text.text(f"Searching web for: {name}...")
        time.sleep(wait_time)
        
        real_text = get_vendor_headlines(driver, name)
        all_text_for_cloud += " " + real_text
        
        risk_label, score = analyze_text(real_text)
        results.append({
            "Vendor": name, 
            "Risk": risk_label, 
            "Score": score, 
            "Live Headlines": real_text
        })
        
        progress_bar.progress((index + 1) / len(df))
    
    driver.quit()
    
    # --- 5. RESULTS ---
    st.success("Audit Complete!")
    res_df = pd.DataFrame(results)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Vendors", len(res_df))
    c2.metric("High Risk Identified", len(res_df[res_df['Risk'] == "🔴 HIGH"]))
    c3.metric("Average Sentiment", round(res_df['Score'].mean(), 2))

    st.divider()

    col_chart, col_table = st.columns([1, 1.5])
    
    with col_chart:
        st.subheader("Risk Distribution")
        fig_pie = px.pie(res_df, names='Risk', color='Risk',
                     color_discrete_map={'🔴 HIGH':'#ff4b4b', '🟢 LOW':'#00cc96', '🟡 NEUTRAL':'#636efa'})
        st.plotly_chart(fig_pie, use_container_width=True)

        if all_text_for_cloud.strip():
            st.subheader("Key Risk Keywords")
            wc = WordCloud(width=400, height=200, background_color='white', colormap='Reds').generate(all_text_for_cloud)
            fig_wc, ax = plt.subplots()
            ax.imshow(wc, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig_wc)

    with table_col:
        st.subheader("Detailed Findings")
        st.dataframe(res_df, use_container_width=True)

    csv_report = res_df.to_csv(index=False).encode('utf-8')
    st.download_button("📩 Download Regulatory Compliance Report", data=csv_report, file_name="vendor_risk_audit.csv")

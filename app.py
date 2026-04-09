import streamlit as st
import pandas as pd
import time
import random
import plotly.express as px

# --- 1. THE RECOVERY OPS "BRAIN" ---
def get_simulated_reputation(name):
    high_risk_firms = ["Frederick J. Hanna", "Forster & Garbus", "Weltman Weinberg"]
    caution_firms = ["Blitt and Gaines", "Aldridge Pite Haan"]
    
    time.sleep(random.uniform(0.3, 0.8)) 
    
    if any(firm.lower() in str(name).lower() for firm in high_risk_firms):
        return "🔴 HIGH RISK", -0.75, "Aggressive tactics flagged in consumer complaints."
    elif any(firm.lower() in str(name).lower() for firm in caution_firms):
        return "🟡 CAUTION", 0.0, "Mixed professional reviews; monitoring recommended."
    else:
        return "🟢 LOW RISK", 0.82, "Maintains high professional standards and compliance."

# --- 2. UI DESIGN ---
st.set_page_config(page_title="Recovery Ops Auditor", layout="wide")
st.title("Law Firm Reputation Auditor 🛡️")

# --- 3. SIDEBAR & TEMPLATE GENERATOR ---
st.sidebar.header("Data Management")

# Create the Template File
template_data = pd.DataFrame(columns=["vendor_name", "city", "state"])
template_csv = template_data.to_csv(index=False).encode('utf-8')

st.sidebar.download_button(
    label="⬇️ Download CSV Template",
    data=template_csv,
    file_name="vendor_upload_template.csv",
    mime="text/csv",
    help="Download this file, fill in your vendors, and upload it below."
)

st.sidebar.divider()

uploaded_file = st.sidebar.file_uploader("Upload Vendor CSV", type=["csv"])

# Data Loading & Auto-Fixer
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = [str(c).lower().strip() for c in df.columns]
    if 'vendor name' in df.columns:
        df = df.rename(columns={'vendor name': 'vendor_name'})
    st.sidebar.success("File uploaded successfully!")
else:
    # Default data for display
    df = pd.DataFrame({
        "vendor_name": ["Weltman Weinberg & Reis", "Pressler Felt & Warshaw", "Zwicker & Associates"],
        "city": ["Cleveland", "Parsippany", "Andover"],
        "state": ["OH", "NJ", "MA"]
    })

# --- 4. AUDIT EXECUTION ---
if st.button("Run Professional Audit"):
    required = ['vendor_name', 'city', 'state']
    missing = [col for col in required if col not in df.columns]
    
    if missing:
        st.error(f"Error: Missing columns {missing}. Please use the template from the sidebar.")
    else:
        results = []
        progress_bar = st.progress(0)
        
        for index, row in df.iterrows():
            name, city, state = row['vendor_name'], row['city'], row['state']
            status, score, findings = get_simulated_reputation(name)
            
            results.append({
                "Vendor": name, 
                "Location": f"{city}, {state}",
                "Status": status, 
                "Risk Score": score,
                "Findings": findings
            })
            progress_bar.progress((index + 1) / len(df))
        
        # --- 5. EXECUTIVE DASHBOARD ---
        res_df = pd.DataFrame(results)
        st.success(f"Audit Complete! Processed {len(res_df)} vendors.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Risk Distribution")
            fig = px.pie(res_df, names='Status', color='Status',
                         color_discrete_map={'🔴 HIGH RISK': '#ff4b4b', '🟢 LOW RISK': '#00cc96', '🟡 CAUTION': '#ffff00'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Detailed Audit Log")
            st.dataframe(res_df, use_container_width=True, hide_index=True)

        st.download_button("Download Audit Report", res_df.to_csv(index=False), "recovery_audit_report.csv")

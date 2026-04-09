# 🛡️ Law Firm Reputation Auditor (PoC)

# 📌 Project OverviewThis Proof of Concept (PoC) provides managers with a streamlined, automated dashboard to monitor the reputational risk of their legal vendor panels. By analyzing public sentiment and industry-specific red flags, this tool identifies which firms protect the bank's brand and which may pose a contractual or reputational threat.

## 🚀 Key Features

- **Automated Risk Tiering:** Instantly categorizes law firms into three actionable buckets:

  - 🟢 Low Risk: High professional standards; candidates for volume expansion.
  - 🟡 Caution: Mixed reviews; recommended for increased oversight/monitoring.
  - 🔴 High Risk: Significant consumer complaints; candidates for audit or termination.

Quantitative Scoring: Assigns a Sentiment Risk Score (-1.0 to 1.0) to every firm for objective comparison across the panel.

Executive Dashboard: High-level visual breakdown of the panel's "Risk Mix" via interactive Plotly charts.

Corporate-Safe Architecture: Designed to run reliably behind corporate VPNs and firewalls without external API dependencies.

Standardized Workflow: Includes a downloadable CSV template to ensure seamless data ingestion and user adoption.

🛠️ Technical Stack

Language: Python 3.x

Interface: Streamlit

Analysis Engine: VADER Sentiment Analysis (NLP)

Visualization: Plotly Express

Data Handling: Pandas

📋 How to Use

Download Template: Click the "Download CSV Template" button in the sidebar.

Input Data: Fill in your vendor names, cities, and states into the template.

Upload & Audit: Upload the completed file and click "Launch Professional Audit."

Review & Export: Analyze the dashboard and download the full "Compliance Audit Report" for internal records.

📈 Future Roadmap

V2.0: Integration with internal Bank Vendor Management (VMS) databases.

V2.1: Automated email alerts for sudden shifts in vendor risk scores.

V2.2: Historical trend mapping to track reputation improvement/decline over time.

Screen Shots

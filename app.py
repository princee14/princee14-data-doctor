import os

# ✅ Turn off telemetry and config writing
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
os.environ["STREAMLIT_DISABLE_CONFIG_FILE"] = "true"

# ✅ Redirect config to writable /tmp dir
os.environ["STREAMLIT_CONFIG_DIR"] = "/tmp/.streamlit"
os.makedirs("/tmp/.streamlit", exist_ok=True)




import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from data_cleaner import clean_data
from eda_generator import generate_eda_report
from datetime import datetime

st.set_page_config(page_title="🩺 Data Doctor", layout="wide")

st.title("🩺📊 Data Doctor")
st.markdown("""
Welcome to **Data Doctor** – your tool to clean and analyze your data effortlessly.
Upload your CSV, review missing data, clean it, and generate an automated EDA report.
""")

# File upload
uploaded_file = st.file_uploader("📂 Upload your CSV file", type=["csv"])

if uploaded_file:
    uploaded_df = pd.read_csv(uploaded_file)

    st.subheader("✅ Preview of Uploaded Data")
    st.dataframe(uploaded_df.head())

    # 🔍 Explore Missing Data
    st.subheader("🔍 Explore Missing Data in Your File")
    st.markdown("""
This heatmap shows **where your dataset has missing values**.
Each vertical line represents a column; brighter areas indicate missing entries in that column or row.
""")

    # 🔹 FORMAL SIZE heatmap: smaller & clearer
    fig, ax = plt.subplots(figsize=(10, 3))  # smaller, horizontal format
    sns.heatmap(uploaded_df.isnull(), cbar=False, cmap='YlOrRd', yticklabels=False, ax=ax)
    st.pyplot(fig)

    # 🔍 Summary of Missing Values
    st.subheader("📈 Summary of Missing Values by Column")
    missing_table = uploaded_df.isnull().sum().reset_index()
    missing_table.columns = ['Column', 'Missing Count']
    missing_table['Missing %'] = (missing_table['Missing Count'] / len(uploaded_df)) * 100
    st.dataframe(missing_table)

    # ⚙️ Cleaning Options
    st.subheader("⚙️ Data Cleaning Options")
    remove_outliers = st.checkbox("📉 Remove Outliers (recommended)", value=True)

    # ❌ Removed target column selectbox
    # st.subheader("🎯 Optional: Select Target Column for EDA")
    # target_col = st.selectbox("Select Target Column (or leave None)", ["None"] + list(uploaded_df.columns))
    # if target_col == "None":
    #     target_col = None
    target_col = None  # Just pass None silently

    # 🚀 Clean Button
    if st.button("🚀 Clean Data & Generate Report"):
        with st.spinner("Cleaning your data..."):
            cleaned_df, cleaning_summary = clean_data(uploaded_df, remove_outliers=remove_outliers)
            st.success("✅ Data cleaned successfully!")

        st.subheader("🔄 Comparison: Raw vs Cleaned Data")
        col1, col2 = st.columns(2)
        with col1:
            st.caption("📂 Raw Data")
            st.dataframe(uploaded_df.head())
        with col2:
            st.caption("🧼 Cleaned Data")
            st.dataframe(cleaned_df.head())

        # Summary of actions
        st.subheader("📝 What We Fixed in Your Data")
        for action in cleaning_summary:
            st.success(f"✅ {action}")

        # Download CSV
        st.subheader("📥 Download Your Cleaned Data")
        csv = cleaned_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", data=csv, file_name="cleaned_data.csv", mime='text/csv')

        # Generate and display EDA
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        report_path = f"output/eda_report_{timestamp}.html"
        with st.spinner("Generating EDA Report..."):
            os.makedirs("output", exist_ok=True)
            generate_eda_report(cleaned_df, report_path, target=target_col)
        st.success("✅ EDA Report Generated!")

        with open(report_path, 'r', encoding='utf-8') as f:
            html_data = f.read()
        st.subheader("📊 Interactive EDA Report")
        st.components.v1.html(html_data, height=800, scrolling=True)

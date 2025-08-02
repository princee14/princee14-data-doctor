import os

# ✅ Turn off telemetry and config writing
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
os.environ["STREAMLIT_DISABLE_CONFIG_FILE"] = "true"

# ✅ Redirect config to writable /tmp dir
os.environ["STREAMLIT_CONFIG_DIR"] = "/tmp/.streamlit"
os.makedirs("/tmp/.streamlit", exist_ok=True)

# ✅ Handle optional dependency for profiling
try:
    from ydata_profiling import ProfileReport
except ImportError:
    ProfileReport = None

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from data_cleaner import clean_data
from eda_generator import generate_eda_report
from datetime import datetime

# ✅ Gemini for AI Assistant
import google.generativeai as genai
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

st.set_page_config(page_title="🩺 Data Doctor", layout="wide")

st.title("🩺📊 Data Doctor")
st.markdown("""
Welcome to **Data Doctor** – your tool to clean and analyze your data effortlessly.
Upload your CSV, review missing data, clean it, and generate an automated EDA report.
""")

# ---------- 📌 Insight Generator Function (to be used after cleaning) ----------
def generate_basic_insights(df):
    insights = []
    insights.append(f"The dataset has **{df.shape[1]} columns** and **{df.shape[0]} rows**.")

    numeric_cols = df.select_dtypes(include='number').columns
    if not numeric_cols.empty:
        highest_mean_col = df[numeric_cols].mean().idxmax()
        highest_mean_val = df[numeric_cols].mean().max()
        insights.append(f"Column `{highest_mean_col}` has the highest mean: **{highest_mean_val:.2f}**")

    cat_cols = df.select_dtypes(include='object').columns
    for col in cat_cols:
        top_val = df[col].mode().iloc[0]
        insights.append(f"The most common value in `{col}` is **\"{top_val}\"**")
        break

    missing_summary = df.isnull().mean().sort_values(ascending=False)
    for col, ratio in missing_summary.items():
        if ratio > 0:
            insights.append(f"Column `{col}` has missing values in **{ratio*100:.1f}%** of rows.")
            break

    return insights

# ---------- 📂 File Upload ----------
uploaded_file = st.file_uploader("📂 Upload your CSV file", type=["csv"])

if uploaded_file:
    uploaded_df = pd.read_csv(uploaded_file)

    st.subheader("✅ Preview of Uploaded Data")
    st.dataframe(uploaded_df.head())

    # 🤖 AI Assistant (based on raw uploaded data)
    st.subheader("🤖 Ask AI About Your Data")
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    for role, message in st.session_state.chat_history:
        st.chat_message(role).write(message)

    user_question = st.chat_input("Ask a question about your dataset...")

    if user_question:
        system_instruction = f"""
You are a helpful data analyst assistant. The user uploaded a pandas DataFrame named `df`.
Use only the dataset provided to answer the user's question.
Respond clearly using data facts, not code.

Here is the DataFrame sample (first 3 rows):
{uploaded_df.head(3).to_string(index=False)}

DataFrame Info:
{uploaded_df.info(buf=None)}

User's Question: {user_question}
"""

        with st.spinner("Thinking..."):
            response = model.generate_content(system_instruction)

        st.chat_message("user").write(user_question)
        st.chat_message("assistant").write(response.text)

        st.session_state.chat_history.append(("user", user_question))
        st.session_state.chat_history.append(("assistant", response.text))

    if st.button("🧹 Clear Chat"):
        st.session_state.chat_history = []

    # 🔍 Explore Missing Data
    st.subheader("🔍 Explore Missing Data in Your File")
    st.markdown("""
This heatmap shows **where your dataset has missing values**.
Each vertical line represents a column; brighter areas indicate missing entries in that column or row.
""")

    fig, ax = plt.subplots(figsize=(10, 3))
    sns.heatmap(uploaded_df.isnull(), cbar=False, cmap='YlOrRd', yticklabels=False, ax=ax)
    st.pyplot(fig)

    # 📈 Summary of Missing Values
    st.subheader("📈 Summary of Missing Values by Column")
    missing_table = uploaded_df.isnull().sum().reset_index()
    missing_table.columns = ['Column', 'Missing Count']
    missing_table['Missing %'] = (missing_table['Missing Count'] / len(uploaded_df)) * 100
    st.dataframe(missing_table)

    # ⚙️ Cleaning Options
    st.subheader("⚙️ Data Cleaning Options")
    remove_outliers = st.checkbox("📉 Remove Outliers (recommended)", value=True)

    target_col = None  # Not used yet

    if st.button("🚀 Clean Data & Generate Report"):
        with st.spinner("Cleaning your data..."):
            cleaned_df, cleaning_summary = clean_data(uploaded_df, remove_outliers=remove_outliers)
            st.success("✅ Data cleaned successfully!")

        # 📌 Quick Dataset Insights (after cleaning)
        st.subheader("📌 Quick Dataset Insights (After Cleaning)")
        for insight in generate_basic_insights(cleaned_df):
            st.info(insight)

        # 🔄 Comparison
        st.subheader("🔄 Comparison: Raw vs Cleaned Data")
        col1, col2 = st.columns(2)
        with col1:
            st.caption("📂 Raw Data")
            st.dataframe(uploaded_df.head())
        with col2:
            st.caption("🧼 Cleaned Data")
            st.dataframe(cleaned_df.head())

        # 📝 Cleaning Summary
        st.subheader("📝 What We Fixed in Your Data")
        for action in cleaning_summary:
            st.success(f"✅ {action}")

        # 📥 Download Cleaned CSV
        st.subheader("📥 Download Your Cleaned Data")
        csv = cleaned_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", data=csv, file_name="cleaned_data.csv", mime='text/csv')

        # 📊 Generate EDA
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
